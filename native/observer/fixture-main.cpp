#define _GNU_SOURCE 1
#include "fixture.h"
#include <errno.h>
#include <dlfcn.h>
#include <pthread.h>
#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
static void verify(bool ok, int line) { if (!ok) { fprintf(stderr, "OBSERVER_CHECK_FAILED line=%d errno=%d\n", line, errno); abort(); } }
#define check(ok) verify((ok), __LINE__)
static uint32_t call(uintptr_t a, uintptr_t b) {
    errno = ERANGE;
    uint32_t value = registration(a, b, ARG2, ARG3, ARG4, ARG5);
    check(errno == EDOM);
    return value;
}
static void *worker(void *id) {
    uintptr_t i, base = (uintptr_t)id * 1000;
    for (i = 0; i < 250; ++i)
        check(call(base + i, 0x12340000) == ((uint32_t)((base+i)^0x12340000) ^ UINT32_C(0x80000001)));
    return 0;
}
int main(int argc, char **argv) {
    bool disabled = argc == 2 && !strcmp(argv[1], "--disabled");
    bool baseline = argc == 2 && !strcmp(argv[1], "--baseline");
    typedef const obs_file *(*view_fn)(void);
    view_fn view = (view_fn)dlsym(RTLD_DEFAULT, "delphi_observer_view");
    check(baseline ? !view : view != 0);
    unsigned before = fixture_calls();
    for (unsigned i = 0; i < 20; ++i) check(call(i + 1, 0x12340000) == ((i + 1)^UINT32_C(0x12340000)^UINT32_C(0x80000001)));
    check(fixture_calls() == before + 20);
    try { errno = ERANGE; registration(UINT32_C(0xeeee0001), 0, ARG2, ARG3, ARG4, ARG5); check(false); }
    catch (const fixture_exception &e) { check(e.value == 99); }
    check(fixture_calls() == before + 21);
    sigjmp_buf context;
    int jump = sigsetjmp(context, 1);
    if (!jump) { errno = ERANGE; registration(UINT32_C(0xeeee0002), (uintptr_t)&context, ARG2, ARG3, ARG4, ARG5); check(false); }
    check(jump == 7 && fixture_calls() == before + 22);
    check(call(UINT32_C(0xeeee0003), 0) == (UINT32_C(0x1234)^UINT32_C(0x5678)^UINT32_C(0x80000001)));
    check(fixture_calls() == before + 24);
    uint32_t count_before_fork = view ? view()->header.count : 0;
    uint32_t drops_before_fork = view ? view()->header.dropped : 0;
    fflush(NULL);
    pid_t child = fork();
    check(child >= 0);
    if (!child) {
        check(call(0x1234, 0x5678) == (UINT32_C(0x1234)^UINT32_C(0x5678)^UINT32_C(0x80000001)));
        _exit(0);
    }
    int child_status;
    check(waitpid(child, &child_status, 0) == child && WIFEXITED(child_status) && WEXITSTATUS(child_status) == 0);
    check(fixture_calls() == before + 24);
    if (view) check(view()->header.count == count_before_fork && view()->header.dropped == drops_before_fork);
    pthread_t threads[8];
    for (uintptr_t i = 0; i < 8; ++i) check(!pthread_create(&threads[i], 0, worker, (void *)(i+1)));
    for (unsigned i = 0; i < 8; ++i) check(!pthread_join(threads[i], 0));
    check(fixture_calls() == before + 2024);
    if (view) {
        const obs_file *file = view();
        const obs_header &h = file->header;
        check(h.magic == OBS_MAGIC && h.version == OBS_VERSION && h.header_bytes == 128);
        check(h.status == (disabled ? OBS_READY | OBS_LOG_DISABLED : OBS_READY));
        if (disabled) check(h.count == 0 && h.dropped == 0);
        else {
            check(h.count <= OBS_CAPACITY && h.count >= 24 && h.dropped > 0 && h.lock == 0);
            check(h.count + h.dropped <= 2024);
            if (!h.drop_flags) check(h.count + h.dropped == 2024);
            for (unsigned i = 0; i < h.count; ++i) {
                const obs_record &r = file->records[i];
                check(r.sequence == i + 1 && r.committed == i + 1 && r.thread && r.caller);
                if (i < 20) check(r.receiver == i+1 && r.endpoint == 0x12340000 && r.thread_sequence == i+1);
                for (unsigned j = 0; j < i; ++j)
                    if (file->records[j].thread == r.thread) check(file->records[j].thread_sequence < r.thread_sequence);
            }
        }
        printf("OBSERVER_RECORDS count=%u dropped=%u lower_bound=%u\n", h.count, h.dropped, h.drop_flags);
    }
    printf("OBSERVER_FIXTURE_PASS mode=%s calls=%u exception=pass longjmp=pass recursion=pass threads=8 fork=pass\n",
        baseline ? "baseline" : disabled ? "disabled" : "observed", fixture_calls());
    return 0;
}
