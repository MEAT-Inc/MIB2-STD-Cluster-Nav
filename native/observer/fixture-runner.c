#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
static int run_case(int kind) {
    char path[128];
    int status, fd;
    const char sentinel[] = "existing-log-must-remain";
    snprintf(path, sizeof(path), "/dev/shmem/delphi-observer-test-%u-%d.bin", (unsigned)getpid(), kind);
    if (kind == 4) {
        fd = open(path, O_CREAT | O_EXCL | O_RDWR, 0600);
        if (fd < 0 || write(fd, sentinel, sizeof(sentinel)) != sizeof(sentinel)) return 30;
        close(fd);
    }
    fflush(NULL);
    pid_t child = fork();
    if (child < 0) return 10;
    if (!child) {
        if (setenv("LD_LIBRARY_PATH", "/proc/boot", 1) || unsetenv("LD_PRELOAD")) _exit(11);
        if (kind) {
            if (setenv("LD_PRELOAD", "/proc/boot/libdelphi_observer.so", 1) ||
                setenv("DELPHI_OBSERVER_LOG", kind == 2 ? "/invalid/disabled" : path, 1)) _exit(12);
        }
        if (kind == 7) execl("/proc/boot/observer_abi", "observer_abi", (char *)0);
        else if (kind == 5) execl("/proc/boot/observer_empty", "observer_empty", (char *)0);
        else if (kind == 6) execl("/proc/boot/observer_wrong", "observer_wrong", (char *)0);
        else if (kind == 2 || kind == 4) execl("/proc/boot/observer_fixture", "observer_fixture", "--disabled", (char *)0);
        else if (!kind) execl("/proc/boot/observer_fixture", "observer_fixture", "--baseline", (char *)0);
        else execl("/proc/boot/observer_fixture", "observer_fixture", (char *)0);
        fprintf(stderr, "OBSERVER_EXEC_FAIL errno=%d\n", errno);
        _exit(14);
    }
    if (waitpid(child, &status, 0) != child || !WIFEXITED(status)) return 15;
    if (kind == 4) {
        char actual[sizeof(sentinel)];
        fd = open(path, O_RDONLY);
        if (fd < 0 || read(fd, actual, sizeof(actual)) != sizeof(actual) || memcmp(actual, sentinel, sizeof(actual))) return 31;
        close(fd);
    }
    return WEXITSTATUS(status);
}
int main(void) {
    static const char *names[] = {"baseline", "observed", "disabled", "repeated", "existing", "missing", "wrong_module", "arm_abi"};
    unsigned i;
    int failed = 0;
    for (i = 0; i < sizeof(names)/sizeof(names[0]); ++i) {
        int actual = run_case(i), expected = (i == 5 || i == 6) ? 125 : 0;
        printf("OBSERVER_CASE name=%s exit=%d expected=%d\n", names[i], actual, expected);
        if (actual != expected) failed = 1;
    }
    if (failed) return 1;
    puts("OBSERVER_QNX_SUITE_PASS");
    return 0;
}
