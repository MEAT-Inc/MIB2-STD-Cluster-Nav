/* Synthetic processes only. Never loads or launches vehicle software. */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

/* mode: 0 baseline, 1 observer absolute path, 2 provider, 3 observer basename,
 * 4 explicitly linked observer. Environment changes are confined to children. */
static int run_case(int mode) {
    int status;
    pid_t child;
    fflush(NULL);
    child = fork();
    if (child < 0) return 10;
    if (!child) {
        if (setenv("LD_LIBRARY_PATH", "/proc/boot", 1)) _exit(11);
        if (unsetenv("LD_PRELOAD") || unsetenv("DL_DEBUG")) _exit(12);
        if (mode == 1 || mode == 2 || mode == 3) {
            const char *library = mode == 2 ? "/proc/boot/libprobe_provider.so" :
                mode == 3 ? "libprobe_observer.so" : "/proc/boot/libprobe_observer.so";
            if (setenv("LD_PRELOAD", library, 1)) _exit(13);
        }
        if (mode == 4)
            execl("/proc/boot/probe_linked", "probe_linked", "--linked", (char *)0);
        else if (mode == 1 || mode == 3)
            execl("/proc/boot/probe_main", "probe_main", "--preloaded", (char *)0);
        else
            execl("/proc/boot/probe_main", "probe_main", (char *)0);
        fprintf(stderr, "DELPHI_EXEC_FAIL mode=%d errno=%d\n", mode, errno);
        _exit(14);
    }
    if (waitpid(child, &status, 0) != child) return 15;
    return WIFEXITED(status) ? WEXITSTATUS(status) : 16;
}
int main(void) {
    static const int modes[] = {0, 0, 1, 1, 2, 3, 4, 0};
    static const char *names[] = {"baseline", "baseline_repeat", "preload",
        "preload_repeat", "provider", "basename", "linked", "restore_baseline"};
    unsigned i;
    int failed = 0;
    printf("DELPHI_QNX_PATHS interp=%d libc=%d observer=%d\n",
        access("/usr/lib/ldqnx.so.2", R_OK), access("/proc/boot/libc.so.3", R_OK),
        access("/proc/boot/libprobe_observer.so", R_OK));
    for (i = 0; i < sizeof(modes)/sizeof(modes[0]); ++i) {
        int result = run_case(modes[i]);
        printf("DELPHI_QNX_CASE name=%s exit=%d executable_present=%d\n",
            names[i], result, access("/proc/boot/probe_main", R_OK) == 0);
        if (result) failed = 1;
    }
    if (failed) return 1;
    puts("DELPHI_QNX_SUITE_PASS");
    return 0;
}
