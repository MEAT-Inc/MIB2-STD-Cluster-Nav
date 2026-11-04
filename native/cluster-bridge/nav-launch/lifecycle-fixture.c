/* QNX controller-composition fixture only; unit SAL/crash guard is tested separately. */
#define _QNX_SOURCE 1
#include "launch.h"
#include "proc_guard.h"
#include <sys/wait.h>
#include <fcntl.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
static const struct timespec tick={0,100000000};
int main(int argc,char **argv){
 pg_identity old,manager,newnav;int f,m,n,i;unsigned long pid,mp;unsigned long long start,ms;char *end;
 if(argc!=6||strcmp(argv[1],"cycle")){return 2;}
 pid=strtoul(argv[2],&end,10);if(*end||!pid||pid>0x7fffffff){return 2;}
 start=strtoull(argv[3],&end,10);if(*end||!start){return 2;}
 mp=strtoul(argv[4],&end,10);if(*end||!mp||mp>0x7fffffff){return 2;}
 ms=strtoull(argv[5],&end,10);if(*end||!ms){return 2;}
 f=pg_open(pid,0,&old);m=pg_open(mp,0,&manager);
 if(f<0||m<0||old.start_time!=start||old.parent!=(pid_t)mp||manager.start_time!=ms||
    strcmp(old.executable,NAV_TARGET)||strcmp(manager.executable,MANAGER_TARGET)||pg_matches(f,&old)||pg_matches(m,&manager)){return 3;}
 {struct launch_state s;int a=open(LAUNCH_ACTIVE,O_RDONLY);
  if(a>=0){ssize_t got=read(a,&s,sizeof(s));close(a);
   if(got==sizeof(s)&&s.phase==2&&!s.observed_pid&&s.root[strlen(LAUNCH_PREFIX)]=='0'){
    for(i=0;i<160;i++){nanosleep(&tick,0);}
    puts("NAV_LIFECYCLE_DELAYED_START_PASS");
   }
  }
 }
 if(pg_matches(f,&old)||pg_matches(m,&manager)||kill(old.pid,SIGINT)){return 3;}
 close(f);
 for(i=0;i<100;i++){
  n=pg_find(NAV_TARGET,manager.pid,&newnav);
  if(n>=0){
   if(newnav.pid!=old.pid&&newnav.start_time!=old.start_time&&!pg_matches(n,&newnav)){close(n);close(m);puts("NAV_LIFECYCLE_FIXTURE_RESTART_PASS");return 0;}
   close(n);
  }
  nanosleep(&tick,0);
 }
 close(m);return 3;
}
