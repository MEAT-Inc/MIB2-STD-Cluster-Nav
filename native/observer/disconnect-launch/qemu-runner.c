#define _QNX_SOURCE 1
#include "launch.h"
#include "proc_guard.h"
#include <sys/mman.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
static const char *roots[]={LAUNCH_PREFIX "00000000000000000000000000000000",LAUNCH_PREFIX "11111111111111111111111111111111"};
static const struct timespec tick={0,100000000};
static int read_state(const char *path,struct launch_state *s){int fd=open(path,O_RDONLY);ssize_t n;if(fd<0)return -1;n=read(fd,s,sizeof(*s));close(fd);return n==(ssize_t)sizeof(*s)?0:-1;}
static pid_t start(const char *root,pid_t pid,int phone){pid_t p;char exe[192],n[32];snprintf(exe,sizeof(exe),"%s/observer_launch",root);snprintf(n,sizeof(n),"%u",(unsigned)pid);fflush(0);p=fork();if(!p){if(setsid()<0)_exit(98);if(phone)execl(exe,"observer_launch","start-disconnected",root,n,"phone",(char*)0);else execl(exe,"observer_launch","start-disconnected",root,n,(char*)0);_exit(99);}return p;}
static int cleanup(const char *root){pid_t p;int status;char exe[192];snprintf(exe,sizeof(exe),"%s/observer_launch",root);fflush(0);p=fork();if(!p){execl(exe,"observer_launch","cleanup-disconnected",root,(char*)0);_exit(99);}if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status))return 99;return WEXITSTATUS(status);}
static int same_observed(struct launch_state *s,pid_t manager){int fd;pg_identity p;fd=pg_open(s->observed_pid,0,&p);if(fd<0)return -1;if(p.parent!=manager||p.start_time!=s->observed_start||strstr(p.executable,"/AndroidAuto.original")==0||pg_matches(fd,&p)){close(fd);return -1;}close(fd);return 0;}
static void dump(const char *label,struct launch_state *s){unsigned i;printf("%s ",label);for(i=0;i<sizeof(*s);++i)printf("%02x",((unsigned char*)s)[i]);puts("");}
int main(void){pid_t manager,p;pg_identity stock;struct launch_state s,final;int fd,status;unsigned i,k;char path[192],lockpath[192];
 if(sizeof(s)!=512||setenv("XSAL_INSTANCE_NAME","delphi_disconnect_emulator",1))return 1;
 manager=fork();if(!manager){execl(MANAGER_TARGET,"procman","-f","/proc/boot/launch-manager.cfg","-c","0","-t",(char*)0);_exit(99);}if(manager<0)return 2;
 for(i=0;i<50;++i){fd=pg_find(AA_TARGET,manager,&stock);if(fd>=0)break;nanosleep(&tick,0);}if(fd<0)return 3;close(fd);
 for(k=0;k<2;++k){
  p=start(roots[k],stock.pid,k!=0);if(p<0)return 4;
  if(k){
   for(i=0;i<80;++i){if(!read_state(LAUNCH_ACTIVE,&s)&&s.observed_start)break;nanosleep(&tick,0);}if(i==80)return 5;
   if(kill(-p,SIGHUP)||waitpid(p,&status,0)!=p||!WIFSIGNALED(status)||WTERMSIG(status)!=SIGHUP)return 6;
  }else if(waitpid(p,&status,0)!=p||!WIFEXITED(status)||WEXITSTATUS(status)!=2)return 7;
  snprintf(path,sizeof(path),"/dev/shmem/delphi-aa-report-%s.bin",roots[k]+strlen(LAUNCH_PREFIX));
  for(i=0;i<750;++i){if(!read_state(path,&s)&&s.guard_done)break;nanosleep(&tick,0);}if(i==750)return 8;
  if(s.version!=3||s.phase!=4||s.error||!s.capture_done||!s.guard_done||s.cleanup_authorized||s.cleanup_started||s.restoration_verified||s.restored_pid||!s.obs_count||s.obs_count+s.obs_dropped!=9)return 9;
  for(i=0;i<10;++i)nanosleep(&tick,0);
  if(same_observed(&s,manager)||read_state(LAUNCH_ACTIVE,&final)||final.observed_pid!=s.observed_pid)return 10;
  dump(k?"DISCONNECT_ORPHAN_PENDING_HEX":"DISCONNECT_PENDING_HEX",&s);
  puts(k?"DISCONNECT_ORPHAN_PENDING_PASS":"DISCONNECT_PENDING_NO_SIGNAL_PASS");
  if(!k){
   struct launch_state *shared;uint64_t correct;
   fd=open(LAUNCH_ACTIVE,O_RDWR);if(fd<0)return 11;shared=mmap(0,sizeof(*shared),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(shared==MAP_FAILED)return 12;
   correct=shared->observed_start;shared->observed_start=correct+1;
   if(cleanup(roots[k])!=3||same_observed(&s,manager))return 13;
   shared->observed_start=correct;
   correct=shared->manager_start;shared->manager_start=correct+1;
   if(cleanup(roots[k])!=3||same_observed(&s,manager))return 14;
   shared->manager_start=correct;
   puts("DISCONNECT_STATE_MISMATCH_REFUSED");
   snprintf(lockpath,sizeof(lockpath),"/dev/shmem/delphi-aa-cleanup-%s.lock",roots[k]+strlen(LAUNCH_PREFIX));fd=open(lockpath,O_CREAT|O_EXCL|O_WRONLY,0600);if(fd<0)return 15;close(fd);
   if(cleanup(roots[k])!=3||same_observed(&s,manager))return 16;
   if(unlink(lockpath))return 17;
   puts("DISCONNECT_LOCK_REFUSED");munmap(shared,sizeof(*shared));
  }
  if(cleanup(roots[k]))return 18;
  snprintf(path,sizeof(path),"/dev/shmem/delphi-aa-final-%s.bin",roots[k]+strlen(LAUNCH_PREFIX));
  if(read_state(path,&final)||final.error||final.phase!=6||!final.capture_done||!final.cleanup_authorized||!final.cleanup_started||!final.restoration_verified||final.observed_pid==final.restored_pid)return 19;
  fd=pg_find(AA_TARGET,manager,&stock);if(fd<0||stock.pid!=(pid_t)final.restored_pid)return 20;close(fd);
  if(cleanup(roots[k]))return 21;
  fd=pg_find(AA_TARGET,manager,&stock);if(fd<0||stock.pid!=(pid_t)final.restored_pid)return 22;close(fd);
  dump(k?"DISCONNECT_ORPHAN_FINAL_HEX":"DISCONNECT_FINAL_HEX",&final);
  puts(k?"DISCONNECT_ORPHAN_CLEANUP_PASS":"DISCONNECT_LATE_CLEANUP_PASS");puts("DISCONNECT_IDEMPOTENT_PASS");
 }
 fd=pg_find(AA_TARGET,manager,&stock);if(fd<0||pg_interrupt(fd,&stock))return 23;close(fd);kill(manager,SIGTERM);waitpid(manager,&status,0);puts("DISCONNECT_QNX_SUITE_PASS");return 0;
}
