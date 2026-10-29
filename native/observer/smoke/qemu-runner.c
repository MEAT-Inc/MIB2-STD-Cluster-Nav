#include <stdio.h>
#include <sys/wait.h>
#include <unistd.h>
int main(void) {
    const char *modes[]={"baseline","observed","timeout-control"};
    unsigned i;
    for(i=0;i<3;++i) {
        int status;
        pid_t p=fork();
        if (!p) { execl("/proc/boot/observer_smoke_guard","observer_smoke_guard",
            "/ramdisk/delphi-observer-smoke_00000000000000000000000000000000",modes[i],(char*)0); _exit(99); }
        if (p<0 || waitpid(p,&status,0)!=p || !WIFEXITED(status) || WEXITSTATUS(status)!=(i==2?124:0)) return 1;
    }
    puts("DELPHI_SMOKE_QNX_SUITE_PASS");
    return 0;
}
