#include "proc_guard.h"
#include <sys/procfs.h>
#include <devctl.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/stat.h>

static int fail(int error) { errno = error; return -1; }
static int command(int fd, int cmd, void *data, size_t size)
{
    int error = devctl(fd, cmd, data, size, NULL);
    return error ? fail(error) : 0;
}
/* The QNX IFS returns image-root-relative debug names (observed in QEMU).
 * Normalize only known root namespaces; never resolve against caller cwd. */
static int copy_path(char *out,size_t capacity,const char *source) {
    size_t n=strlen(source);int relative=source[0]!='/';
    if(!n || strstr(source,"/../") || strstr(source,"/./") ||
       !strcmp(source,"..") || !strncmp(source,"../",3))return fail(EINVAL);
    if(relative && strncmp(source,"proc/boot/",10) &&
       strncmp(source,"extbin/apps/",12) &&
       strncmp(source,"ramdisk/delphi-aa-observer_",sizeof("ramdisk/delphi-aa-observer_")-1))return fail(EINVAL);
    if(n+(size_t)relative>=capacity)return fail(ENAMETOOLONG);
    if(relative){out[0]='/';memcpy(out+1,source,n+1);}else memcpy(out,source,n+1);
    return 0;
}
int pg_read_identity(int fd, pg_identity *out)
{
    procfs_info before, after;
    pg_identity result;
    /* Heap storage supplies alignment for procfs_debuginfo's uint64_t. Fill
     * with nonzero bytes so an absent/truncated terminator cannot pass. */
    size_t offset = offsetof(procfs_debuginfo, path);
    size_t size = offset + sizeof result.executable;
    procfs_debuginfo *debug;
    int saved;
    if (!out) return fail(EINVAL);
    if (command(fd, DCMD_PROC_INFO, &before, sizeof before)) return -1;
    debug = malloc(size);
    if (!debug) return -1;
    memset(debug, 0xff, size);
    if (command(fd, DCMD_PROC_MAPDEBUG_BASE, debug, size)) goto error;
    if (!memchr(debug->path, '\0', sizeof result.executable)) {
        errno = ENAMETOOLONG; goto error;
    }
    memset(&result, 0, sizeof result);
    if (copy_path(result.executable,sizeof(result.executable),debug->path)) goto error;
    free(debug);
    if (command(fd, DCMD_PROC_INFO, &after, sizeof after)) return -1;
    if (before.pid != after.pid || before.parent != after.parent ||
        before.start_time != after.start_time ||
        before.base_address != after.base_address) return fail(ESTALE);
    result.pid = after.pid;
    result.parent = after.parent;
    result.start_time = after.start_time;
    result.base_address = after.base_address;
    *out = result;
    return 0;
error:
    saved = errno; free(debug); return fail(saved);
}
int pg_open(pid_t pid, int writable, pg_identity *out)
{
    char path[64];
    int fd, saved, count, status;
    if (pid <= 0 || !out) return fail(EINVAL);
    count = snprintf(path, sizeof path, "/proc/%ld/as", (long)pid);
    if (count < 0 || (size_t)count >= sizeof path) return fail(EOVERFLOW);
    fd = open(path, writable ? O_RDWR : O_RDONLY);
    if (fd < 0) return -1;
    status = pg_read_identity(fd, out);
    if (!status && out->pid == pid) return fd;
    saved = errno;
    if (!status && out->pid != pid) saved = ESTALE;
    close(fd);
    return fail(saved);
}
int pg_matches(int fd, const pg_identity *expected)
{
    pg_identity current;
    if (!expected || !memchr(expected->executable, '\0',
                            sizeof expected->executable)) return fail(EINVAL);
    if (pg_read_identity(fd, &current)) return -1;
    if (current.pid != expected->pid || current.parent != expected->parent ||
        current.start_time != expected->start_time ||
        strcmp(current.executable, expected->executable)) return fail(ESTALE);
    return 0;
}
int pg_interrupt(int fd, const pg_identity *expected)
{
    if (pg_matches(fd, expected)) return -1;
    /* Match the captured manager's kill(SIGINT) behavior. The procfs debugger
     * signal command did not preserve restart status in the emulated runtime.
     * This recheck and kill are separate operations, NOT atomic compare/signal.
     * There is one chosen delivery path, with no retry/fallback to another PID. */
    return kill(expected->pid, SIGINT);
}
static int numeric_pid(const char *name, pid_t *out)
{
    unsigned long value = 0;
    const unsigned char *p = (const unsigned char *)name;
    if (!*p) return 0;
    for (; *p; ++p) {
        unsigned digit;
        if (*p < '0' || *p > '9') return 0;
        digit = *p - '0';
        if (value > ((unsigned long)INT_MAX - digit) / 10) return 0;
        value = value * 10 + digit;
    }
    if (!value) return 0;
    *out = (pid_t)value;
    return 1;
}
int pg_find(const char *exactpath, pid_t parent, pg_identity *out)
{
    DIR *dir;
    struct dirent *entry;
    pg_identity candidate, found;
    int held = -1, fd, saved = 0;
    pid_t pid;
    if (!exactpath || exactpath[0] != '/' || !out || parent <= 0 ||
        strlen(exactpath) >= sizeof out->executable) return fail(EINVAL);
    dir = opendir("/proc");
    if (!dir) return -1;
    for (;;) {
        errno = 0;
        entry = readdir(dir);
        if (!entry) { saved = errno; break; }
        if (!numeric_pid(entry->d_name, &pid)) continue;
        fd = pg_open(pid, 0, &candidate);
        if (fd < 0) continue; /* Other /proc entries may be inaccessible/gone. */
        close(fd);
        if (candidate.parent != parent || strcmp(candidate.executable, exactpath)) continue;
        if (held >= 0) { saved = EEXIST; break; }
        held = pg_open(pid, 0, &found);
        if (held < 0) { saved = errno; break; }
        if (pg_matches(held, &candidate)) { saved = errno; break; }
    }
    closedir(dir);
    if (saved) { if (held >= 0) close(held); return fail(saved); }
    if (held < 0) return fail(ESRCH);
    if (pg_matches(held, &found)) { saved = errno; close(held); return fail(saved); }
    *out = found;
    return held;
}

