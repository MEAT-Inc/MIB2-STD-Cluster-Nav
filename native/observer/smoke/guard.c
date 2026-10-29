#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/wait.h>
#include <unistd.h>
static int valid_directory(const char *path) {
    const char *prefix="/ramdisk/delphi-observer-smoke_";
    unsigned i,n=(unsigned)strlen(prefix);
    if (strlen(path)!=n+32 || strncmp(path,prefix,n)) return 0;
    for(i=0;i<32;++i) if (!((path[n+i]>='0'&&path[n+i]<='9')||(path[n+i]>='a'&&path[n+i]<='f'))) return 0;
    return 1;
}
int main(int argc,char **argv) {
    char childpath[160],library[160],search[180],logpath[160];
    const char *suffix;
    struct sigaction action;
    pid_t child,waited;
    int status=0,is_timeout;
    unsigned tick,limit;
    const struct timespec pause_time={0,100000000};
    if (argc!=3 || !valid_directory(argv[1])) return 2;
    is_timeout=!strcmp(argv[2],"timeout-control");
    if (strcmp(argv[2],"baseline") && strcmp(argv[2],"observed") && !is_timeout) return 2;
    suffix=argv[1]+strlen("/ramdisk/delphi-observer-smoke_");
    snprintf(childpath,sizeof(childpath),"%s/observer_smoke",argv[1]);
    snprintf(library,sizeof(library),"%s/libdelphi_observer.so",argv[1]);
    snprintf(search,sizeof(search),"%s:/proc/boot",argv[1]);
    snprintf(logpath,sizeof(logpath),"/dev/shmem/delphi-observer-smoke-%s.bin",suffix);
    memset(&action,0,sizeof(action));
    action.sa_handler=SIG_DFL;
    sigemptyset(&action.sa_mask);
    if (sigaction(SIGCHLD,&action,0)) return 3;
    fflush(NULL);
    child=fork();
    if (child<0) return 4;
    if (!child) {
        if (unsetenv("LD_PRELOAD") || unsetenv("DL_DEBUG") ||
            setenv("LD_LIBRARY_PATH",search,1)) _exit(120);
        if (!strcmp(argv[2],"observed") && (setenv("LD_PRELOAD",library,1) ||
            setenv("DELPHI_OBSERVER_LOG",logpath,1))) _exit(121);
        execl(childpath,"observer_smoke",argv[2],(char *)0);
        _exit(122);
    }
    limit=is_timeout?20:100;
    for (tick=0;tick<limit;++tick) {
        waited=waitpid(child,&status,WNOHANG);
        if (waited==child) break;
        if (waited<0 && errno!=EINTR) return 7;
        nanosleep(&pause_time,0);
    }
    if (tick==limit) {
        /* Recheck before killing: only this unreaped child can be targeted. */
        waited=waitpid(child,&status,WNOHANG);
        if (!waited) {
            if (kill(child,SIGKILL) && errno!=ESRCH) return 5;
            do { waited=waitpid(child,&status,0); } while(waited<0 && errno==EINTR);
        }
        if (waited!=child) return 6;
        puts("DELPHI_SMOKE_TIMEOUT child_reaped=1");
        return 124;
    }
    if (!WIFEXITED(status)) return 123;
    printf("DELPHI_SMOKE_GUARD mode=%s exit=%d\n",argv[2],WEXITSTATUS(status));
    return WEXITSTATUS(status);
}
