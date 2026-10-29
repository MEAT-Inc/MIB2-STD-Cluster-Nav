#define _QNX_SOURCE 1
#include "bench.h"
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/pathmgr.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
int main(void) {
 struct report *r;pid_t manager,guard;int fd,status,ok=0;unsigned i;
 struct timespec tick={0,100000000};
 fd=open(REPORT,O_CREAT|O_EXCL|O_RDWR,0600);
 if(fd<0 || ftruncate(fd,sizeof(*r)))return 2;
 r=mmap(0,sizeof(*r),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(r==MAP_FAILED)return 3;
 memset(r,0,sizeof(*r));
 if(setenv("XSAL_INSTANCE_NAME","delphi_emulator_managed_bench",1))return 4;
 manager=fork();
 if(!manager) { execl("/proc/boot/procman.captured","procman","-f","/proc/boot/manager.cfg","-c","0","-t",(char*)0);perror("exec procman");_exit(98); }
 if(manager<0)return 5;
 for(i=0;i<100 && r->count<2;++i) {
  if(waitpid(manager,&status,WNOHANG)==manager) { printf("MANAGED_MANAGER_EARLY_EXIT status=%d\n",status);return 6; }
  nanosleep(&tick,0);
 }
 printf("MANAGED_SNAPSHOT count=%u manager=%u child=%u ppid=%u extra_code=%d\n",r->count,(unsigned)manager,r->pid,r->ppid,r->extra_code);
 if(r->count==2 && r->ppid==(unsigned)manager && r->extra_code==(7<<8)) {
  printf("MANAGED_EXIT_STATUS_ENCODING_PASS encoded=%d\n",r->extra_code);
  guard=fork();
  if(!guard) {
   r->guard_armed=1;
   for(i=0;i<60 && !r->guard_done;++i)nanosleep(&tick,0);
   if(owned_redirect()) { if(pathmgr_unlink(TARGET))_exit(88);r->guard_removed=1; }
   _exit(0);
  }
  if(guard<0)return 8;
  for(i=0;i<20 && !r->guard_armed;++i)nanosleep(&tick,0);
  if(!r->guard_armed || pathmgr_symlink(WRAPPER,TARGET) || !owned_redirect())return 9;
  if(kill((pid_t)r->pid,SIGINT))return 7;
  for(i=0;i<60 && r->count<3;++i)nanosleep(&tick,0);
  printf("MANAGED_SIGNAL_RESTART count=%u code=%d expected=%d\n",r->count,r->extra_code,SIGINT);
  if(r->count==3 && r->extra_code==SIGINT && r->ppid==(unsigned)manager &&
     r->last_observed && r->observed==1 && r->records>0 && !owned_redirect()) {
   puts("MANAGED_REAL_OBSERVER_CAPTURE_PASS");
   r->guard_done=1;
   if(waitpid(guard,&status,0)!=guard || !WIFEXITED(status) || WEXITSTATUS(status))return 10;
   if(kill((pid_t)r->pid,SIGINT))return 11;
   for(i=0;i<60 && r->count<4;++i)nanosleep(&tick,0);
   if(r->count==4 && r->extra_code==SIGINT && r->ppid==(unsigned)manager &&
      !r->last_observed && r->observed==1 && !owned_redirect()) {
    for(i=0;i<15;++i)nanosleep(&tick,0);
    if(r->count==4) { ok=1;puts("MANAGED_REAL_STOCK_RESTORE_PASS"); }
   }
  }
 }
 /* This owns the emulated manager child, not any vehicle process. */
 kill(manager,SIGTERM);while(waitpid(manager,&status,0)<0 && errno==EINTR){}
 if(ok)puts("MANAGED_REAL_PROCMAN_RESTART_AND_CLEAN_EXIT_PASS");
 else puts("MANAGED_SUITE_FAIL");
 return ok?0:1;
}
