#define _QNX_SOURCE 1
#include "bench.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/pathmgr.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
static struct tx_report *report;
static const struct timespec poll_delay={0,100000000};
static int own_link(void) {
 char path[256];ssize_t n=readlink(TX_TARGET,path,sizeof(path)-1);
 if(n<0)return 0;
 path[n]=0;
 return !strcmp(path,TX_WRAPPER);
}
static uint32_t hash_file(const char *path) {
 unsigned char bytes[512];uint32_t hash=2166136261u;ssize_t n;int fd=open(path,O_RDONLY);
 if(fd<0)return 0;
 while((n=read(fd,bytes,sizeof(bytes)))>0) {
  ssize_t i;for(i=0;i<n;++i)hash=(hash^bytes[i])*16777619u;
 }
 close(fd);return n<0?0:hash;
}
static int owned_wait(pid_t child) {
 unsigned tick;int status=0;pid_t p;
 for(tick=0;tick<60;++tick) {
  p=waitpid(child,&status,WNOHANG);
  if(p==child)return WIFEXITED(status)?WEXITSTATUS(status):123;
  if(p<0 && errno!=EINTR)return 124;
  nanosleep(&poll_delay,0);
 }
 p=waitpid(child,&status,WNOHANG);
 if(!p) { kill(child,SIGKILL); do{p=waitpid(child,&status,0);}while(p<0&&errno==EINTR); }
 return 124;
}
static int launch(pid_t *pid) {
 *pid=fork();
 if(!*pid) { execl(TX_TARGET,"path_child","-t",test_root,(char*)0);_exit(122); }
 if(*pid<0)return 121;
 return owned_wait(*pid);
}
static pid_t arm_guard(void) {
 unsigned i;pid_t p;
 report->armed=report->done=report->watchdog_finished=report->watchdog_removed=0;
 p=fork();
 if(!p) {
  report->armed=1;
  for(i=0;i<30 && !report->done;++i)nanosleep(&poll_delay,0);
  if(own_link()) { if(pathmgr_unlink(TX_TARGET))_exit(1);report->watchdog_removed=1; }
  report->watchdog_finished=1;_exit(0);
 }
 if(p<0)return -1;
 for(i=0;i<15 && !report->armed;++i)nanosleep(&poll_delay,0);
 if(report->armed)return p;
 report->done=1;owned_wait(p);return -1;
}
static int finish_guard(pid_t guard) {
 report->done=1;
 return owned_wait(guard);
}
static int wrap(int argc,char **argv) {
 /* Only a freshly created, strictly named private RAM test path is accepted. */
 if(argc!=3 || strcmp(argv[1],"-t") || !own_link())return 126;
 if(getenv("DLO_TX_FAIL_BEFORE_DETACH"))return 130;
 if(pathmgr_unlink(TX_TARGET) || own_link())return 127;
 if(getenv("DLO_TX_FAIL_AFTER_DETACH"))return 125;
 if(setenv("LD_PRELOAD",tx_library,1) || setenv("DELPHI_OBSERVER_LOG",tx_log,1))return 128;
 execv(TX_COPY,argv);return 129;
}
#define CHECK(value) do { if(!(value)) { fprintf(stderr,"PATH_CHECK_FAILED line=%d errno=%d\n",__LINE__,errno);goto fail; } } while(0)
int main(int argc,char **argv) {
 int fd,result;pid_t child,guard=-1,installer;unsigned i;uint32_t original;
 struct sigaction action;
 if(argc!=3)return 2;
 if(!setup_paths(!strcmp(argv[0],"path_child")?argv[2]:argv[1]))return 2;
 if(!strcmp(argv[0],"path_child"))return wrap(argc,argv);
 if(strcmp(argv[2],"suite"))return 2;
 if(!regular_file(TX_TARGET) || !regular_file(TX_COPY) || !regular_file(TX_WRAPPER) || !regular_file(tx_library))return 2;
 if(unsetenv("LD_PRELOAD") || unsetenv("DL_DEBUG") || setenv("LD_LIBRARY_PATH",tx_search,1))return 2;
 if(sizeof(*report)!=208)return 2;
 memset(&action,0,sizeof(action));action.sa_handler=SIG_DFL;sigemptyset(&action.sa_mask);
 if(sigaction(SIGCHLD,&action,0))return 3;
 original=hash_file(TX_TARGET);
 printf("PATH_HASH original=%08x copy=%08x errno=%d\n",original,hash_file(TX_COPY),errno);
 if(!original || original!=hash_file(TX_COPY))return 4;
 fd=open(TX_REPORT,O_CREAT|O_EXCL|O_RDWR,0600);
 if(fd<0)return 5;
 if(ftruncate(fd,sizeof(*report)))return 6;
 report=mmap(0,sizeof(*report),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(report==MAP_FAILED)return 7;
 memset(report,0,sizeof(*report));
 report->magic=PATH_MAGIC;report->version=1;report->bytes=sizeof(*report);
 CHECK(!launch(&child));
 CHECK(report->app_runs==1 && report->observed_runs==0 && report->last_pid==(unsigned)child && report->last_ppid==(unsigned)getpid());
 puts("PATH_BASELINE_PASS");
 guard=arm_guard();CHECK(guard>0);
 CHECK(!pathmgr_symlink(TX_WRAPPER,TX_TARGET));CHECK(own_link());
 CHECK(!launch(&child));
 CHECK(report->app_runs==2 && report->observed_runs==1 && report->last_pid==(unsigned)child && report->last_ppid==(unsigned)getpid());
 CHECK(!own_link() && hash_file(TX_TARGET)==original && report->arguments_ok);
 CHECK(!finish_guard(guard));guard=-1;
 CHECK(!launch(&child));CHECK(report->app_runs==3 && report->observed_runs==1);
 puts("PATH_ONE_SHOT_RESTORE_PASS");
 guard=arm_guard();CHECK(guard>0);
 CHECK(!pathmgr_symlink(TX_WRAPPER,TX_TARGET));
 CHECK(!setenv("DLO_TX_FAIL_AFTER_DETACH","1",1));
 result=launch(&child);CHECK(result==125);
 CHECK(!unsetenv("DLO_TX_FAIL_AFTER_DETACH"));
 CHECK(!own_link() && hash_file(TX_TARGET)==original);
 /* Model the captured manager's restart-after-error behavior. */
 CHECK(!launch(&child));CHECK(report->app_runs==4 && report->observed_runs==1);
 CHECK(!finish_guard(guard));guard=-1;
 puts("PATH_AFTER_DETACH_FAILURE_PASS");
 CHECK(getenv("LD_PRELOAD")==0); /* Child environment must not leak into manager. */
 guard=arm_guard();CHECK(guard>0);
 CHECK(!pathmgr_symlink(TX_WRAPPER,TX_TARGET));
 CHECK(!setenv("DLO_TX_FAIL_BEFORE_DETACH","1",1));
 CHECK(launch(&child)==130);CHECK(own_link());
 CHECK(!unsetenv("DLO_TX_FAIL_BEFORE_DETACH"));
 CHECK(!owned_wait(guard));guard=-1;
 CHECK(report->watchdog_removed && !own_link());
 CHECK(hash_file(TX_TARGET)==original && !launch(&child));
 CHECK(report->app_runs==5 && report->observed_runs==1);
 puts("PATH_BEFORE_DETACH_FAILURE_PASS");
 installer=fork();CHECK(installer>=0);
 if(!installer) {
  pid_t watchdog=arm_guard();
  if(watchdog<0 || pathmgr_symlink(TX_WRAPPER,TX_TARGET))_exit(1);
  _exit(0); /* Watchdog must clean up even after the installer exits. */
 }
 CHECK(!owned_wait(installer));
 for(i=0;i<45 && !report->watchdog_finished;++i)nanosleep(&poll_delay,0);
 CHECK(report->watchdog_finished && report->watchdog_removed && !own_link());
 CHECK(hash_file(TX_TARGET)==original && !launch(&child));
 CHECK(report->app_runs==6 && report->observed_runs==1);
 puts("PATH_ORPHAN_WATCHDOG_PASS");
 puts("PATH_SUITE_PASS");return 0;
fail:
 if(own_link())pathmgr_unlink(TX_TARGET);
 if(guard>0)finish_guard(guard);
 return 1;
}
