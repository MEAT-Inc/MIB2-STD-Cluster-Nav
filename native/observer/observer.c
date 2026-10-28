#define _GNU_SOURCE 1
#define _QNX_SOURCE 1
#include "observer.h"
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

_Static_assert(sizeof(struct obs_header) == 128, "fixed header ABI");
_Static_assert(sizeof(struct obs_record) == 32, "fixed record ABI");
_Static_assert(__atomic_always_lock_free(4, 0), "requires inline atomic32");
static struct obs_file fallback;
static struct obs_file *logfile = &fallback;
static uintptr_t native_target;
static uint32_t owner_pid;
static int logging_enabled;
static struct { uint32_t thread, sequence; } threads[OBS_THREAD_SLOTS];

/* Unrecoverable ORIGINAL-symbol resolution fails before normal application main.
 * Logging failures below always disable observation and retain forwarding. */
__attribute__((noreturn)) static void resolution_failure(void) {
    static const char text[] = "delphi-observer: original registration symbol unavailable or wrong module; startup refused\n";
    (void)write(STDERR_FILENO, text, sizeof(text)-1);
    _exit(125);
}
static const char *basename_of(const char *s) {
    const char *p = strrchr(s, '/');
    return p ? p + 1 : s;
}
static int valid_log_path(const char *p) {
#ifdef __QNXNTO__
    const char *prefix = "/dev/shmem/delphi-observer-";
#else
    const char *prefix = "/tmp/delphi-observer-";
#endif
    size_t n = strlen(prefix);
    if (strncmp(p, prefix, n) || !p[n]) return 0;
    for (p += n; *p; ++p)
        if (!((*p >= 'a' && *p <= 'z') || (*p >= 'A' && *p <= 'Z') ||
              (*p >= '0' && *p <= '9') || *p == '-' || *p == '_' || *p == '.')) return 0;
    return 1;
}
__attribute__((constructor)) static void initialize(void) {
    int saved_errno = errno, fd, flags = O_CREAT | O_EXCL | O_RDWR;
    void *symbol = dlsym(RTLD_NEXT, OBS_SYMBOL);
    Dl_info info, self;
    char default_path[128];
    const char *path = getenv("DELPHI_OBSERVER_LOG");
    if (!symbol || !dladdr(symbol, &info) || !info.dli_fname ||
        !dladdr((void *)initialize, &self) || info.dli_fbase == self.dli_fbase ||
        (strcmp(basename_of(info.dli_fname), "libautoreceiver.so") &&
         strcmp(basename_of(info.dli_fname), "libautoreceiver.so.1"))) resolution_failure();
    native_target = (uintptr_t)symbol;
    owner_pid = (uint32_t)getpid();
    fallback.header.magic = OBS_MAGIC;
    fallback.header.version = OBS_VERSION;
    fallback.header.header_bytes = sizeof(struct obs_header);
    fallback.header.record_bytes = sizeof(struct obs_record);
    fallback.header.capacity = OBS_CAPACITY;
    fallback.header.pointer_bytes = sizeof(void *);
    fallback.header.pid = owner_pid;
    fallback.header.native_address = (uint32_t)native_target;
    fallback.header.module_base = (uint32_t)(uintptr_t)info.dli_fbase;
    fallback.header.status = OBS_READY | OBS_LOG_DISABLED;
    if (!path) {
#ifdef __QNXNTO__
        snprintf(default_path, sizeof(default_path), "/dev/shmem/delphi-observer-%u.bin", owner_pid);
#else
        snprintf(default_path, sizeof(default_path), "/tmp/delphi-observer-%u.bin", owner_pid);
#endif
        path = default_path;
    }
#ifdef O_NOFOLLOW
    flags |= O_NOFOLLOW;
#endif
    if (valid_log_path(path) && (fd = open(path, flags, 0600)) != -1) {
        if (!ftruncate(fd, sizeof(struct obs_file))) {
            void *mapped = mmap(NULL, sizeof(struct obs_file), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
            if (mapped != MAP_FAILED) {
                logfile = mapped;
                /* Constructor only: initialize/prefault the whole fixed mapping. */
                memset(logfile, 0, sizeof(*logfile));
                logfile->header = fallback.header;
                logfile->header.status = OBS_READY;
                logging_enabled = 1;
            }
        }
        close(fd);
    }
    /* No destructor: mapping lifetime is the process lifetime, avoiding races
     * with other threads at exit. The OS releases it, and retains the log object. */
    errno = saved_errno;
}
static void dropped(struct obs_header *h) {
    unsigned i;
    for (i = 0; i < 4; ++i) {
        uint32_t previous = __atomic_load_n(&h->dropped, __ATOMIC_RELAXED);
        if (previous == UINT32_MAX || __atomic_compare_exchange_n(&h->dropped,
            &previous, previous + 1, 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) return;
    }
    /* Bounded accounting effort: mark that the saturated count is a lower bound. */
    __atomic_store_n(&h->drop_flags, OBS_DROP_INEXACT, __ATOMIC_RELAXED);
}
/* Hidden C helper called before the assembly wrapper restores its saved inputs.
 * One try-lock attempt, fixed-size scan, no allocation/file I/O/loader calls.
 * The lock is also the recursion guard for the logger; it is released before
 * native execution, so recursive native calls remain observable and unmodified. */
__attribute__((visibility("hidden"))) uintptr_t delphi_observer_enter(
        uintptr_t receiver, uintptr_t endpoint, uintptr_t caller) {
    uintptr_t target = native_target;
    int saved_errno = errno;
    uint32_t unlocked = 0, thread, thread_sequence = 0, flags = 0;
    unsigned i;
    struct obs_header *h;
    if (!target) resolution_failure();
    if (!logging_enabled || (uint32_t)getpid() != owner_pid) goto done;
    h = &logfile->header;
    if (!__atomic_compare_exchange_n(&h->lock, &unlocked, 1, 1,
                                    __ATOMIC_ACQUIRE, __ATOMIC_RELAXED)) {
        dropped(h); goto done;
    }
    if (h->count >= OBS_CAPACITY) {
        dropped(h); goto unlock;
    }
    thread = (uint32_t)(uintptr_t)pthread_self();
    for (i = 0; i < OBS_THREAD_SLOTS; ++i) {
        if (!threads[i].thread || threads[i].thread == thread) {
            threads[i].thread = thread;
            thread_sequence = ++threads[i].sequence;
            break;
        }
    }
    if (!thread_sequence) flags |= OBS_THREAD_UNTRACKED;
    {
        uint32_t index = h->count;
        struct obs_record *r = &logfile->records[index];
        r->sequence = index + 1;
        r->thread = thread;
        r->thread_sequence = thread_sequence;
        r->receiver = (uint32_t)receiver;
        r->endpoint = (uint32_t)endpoint;
        r->caller = (uint32_t)caller;
        r->flags = flags;
        __atomic_store_n(&r->committed, index + 1, __ATOMIC_RELEASE);
        __atomic_store_n(&h->count, index + 1, __ATOMIC_RELEASE);
    }
unlock:
    __atomic_store_n(&h->lock, 0, __ATOMIC_RELEASE);
done:
    errno = saved_errno;
    return target;
}
__attribute__((visibility("default"))) const struct obs_file *delphi_observer_view(void) {
    return logfile;
}
