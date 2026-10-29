#define _QNX_SOURCE 1
#include <stdio.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>
int main(void){
 const char *modes[]={"baseline","observed","disabled","full","missing"};unsigned i;int status;pid_t p;char log[160];
 for(i=0;i<5;++i){fflush(0);p=fork();if(!p){
  snprintf(log,sizeof(log),"/dev/shmem/delphi-observer-aa-%032x.bin",i);
  setenv("LD_LIBRARY_PATH",i==4?"/missing:/proc/boot":"/proc/boot",1);
  if(i)setenv("LD_PRELOAD","/proc/boot/libdelphi_observer.so",1);else unsetenv("LD_PRELOAD");
  setenv("DELPHI_OBSERVER_LOG",i==2?"/bad":log,1);
  execl("/proc/boot/display_fixture","display_fixture",modes[i],(char*)0);_exit(99);}
  if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status)||WEXITSTATUS(status)!=(i==4?125:0)){printf("DISPLAY_CASE_FAILED mode=%s status=%d\n",modes[i],status);return 1;}
 }
 puts("DISPLAY_QNX_SUITE_PASS");return 0;
}
