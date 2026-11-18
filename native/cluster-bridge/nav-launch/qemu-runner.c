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
#include <sys/stat.h>
static const char *roots[]={LAUNCH_PREFIX "00000000000000000000000000000000",LAUNCH_PREFIX "11111111111111111111111111111111"};
static const struct timespec tick={0,100000000};
static int read_state(const char *path,struct launch_state *s){int fd=open(path,O_RDONLY);ssize_t n;if(fd<0)return -1;n=read(fd,s,sizeof(*s));close(fd);return n==(ssize_t)sizeof(*s)?0:-1;}
static pid_t start(const char *root,pid_t pid,int phone){pid_t p;char exe[192],n[32];snprintf(exe,sizeof(exe),"%s/nav_launch",root);snprintf(n,sizeof(n),"%u",(unsigned)pid);fflush(0);p=fork();if(!p){if(setsid()<0)_exit(98);(void)phone;execl(exe,"nav_launch","start-disconnected",root,n,(char*)0);_exit(99);}return p;}
static int cleanup(const char *root){pid_t p;int status;char exe[192];snprintf(exe,sizeof(exe),"%s/nav_launch",root);fflush(0);p=fork();if(!p){execl(exe,"nav_launch","cleanup-disconnected",root,(char*)0);_exit(99);}if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status))return 99;return WEXITSTATUS(status);}
static int finalize(const char *root){pid_t p;int status;char exe[192];snprintf(exe,sizeof(exe),"%s/nav_launch",root);fflush(0);p=fork();if(!p){execl(exe,"nav_launch","finalize-recovery",root,(char*)0);_exit(99);}if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status))return 99;return WEXITSTATUS(status);}
static int arm(const char *root){pid_t p;int status;char exe[192];snprintf(exe,sizeof(exe),"%s/nav_launch",root);fflush(0);p=fork();if(!p){execl(exe,"nav_launch","arm-replay",root,(char*)0);_exit(99);}if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status))return 99;return WEXITSTATUS(status);}
static int same_observed(struct launch_state *s,pid_t manager){int fd;pg_identity p;fd=pg_open(s->observed_pid,0,&p);if(fd<0)return -1;if(p.parent!=manager||p.start_time!=s->observed_start||strcmp(p.executable,NAV_TARGET)||pg_matches(fd,&p)){close(fd);return -1;}close(fd);return 0;}
static void dump(const char *label,struct launch_state *s){unsigned i;printf("%s ",label);for(i=0;i<sizeof(*s);++i)printf("%02x",((unsigned char*)s)[i]);puts("");}
int main(void){pid_t manager,p;pg_identity stock;struct launch_state s,final;int fd,status;unsigned i,k;char path[192],lockpath[192];
 if(chdir("/extbin/apps/bin")||sizeof(s)!=512||setenv("XSAL_INSTANCE_NAME","delphi_disconnect_emulator",1))return 1;
 manager=fork();if(!manager){execl(MANAGER_TARGET,"procman","-f","/proc/boot/launch-manager.cfg","-c","0","-t",(char*)0);_exit(99);}if(manager<0)return 2;
 for(i=0;i<50;++i){fd=pg_find(NAV_TARGET,manager,&stock);if(fd>=0)break;nanosleep(&tick,0);}if(fd<0)return 3;close(fd);
 {const char *names[]={"/proc/boot/libc.so.3","/proc/boot/libXSAL.so",LAUNCH_PREFIX "00000000000000000000000000000000/libc.so.3.reference",LAUNCH_PREFIX "00000000000000000000000000000000/libXSAL.so.reference"};unsigned j;
  for(j=0;j<4;j++){struct stat st;unsigned char b[16]={0};int q=open(names[j],O_RDONLY);ssize_t n=q<0?-1:read(q,b,sizeof(b));if(q>=0)close(q);if(!lstat(names[j],&st))printf("FIXTURE_REF path=%s mode=%o bytes=%llu read=%d first=%02x%02x%02x%02x\n",names[j],(unsigned)st.st_mode,(unsigned long long)st.st_size,(int)n,b[0],b[1],b[2],b[3]);}
 }
 for(k=0;k<2;++k){
  p=start(roots[k],stock.pid,k!=0);if(p<0)return 4;
  if(k){
   for(i=0;i<80;++i){if(!read_state(LAUNCH_ACTIVE,&s)&&s.observed_start)break;nanosleep(&tick,0);}if(i==80)return 5;
   if(kill(-p,SIGHUP)||waitpid(p,&status,0)!=p||!WIFSIGNALED(status)||WTERMSIG(status)!=SIGHUP)return 6;
  }else if(waitpid(p,&status,0)!=p||!WIFEXITED(status)||WEXITSTATUS(status)!=2)return 7;
  snprintf(path,sizeof(path),"/dev/shmem/delphi-nav-launch-report-%s.bin",roots[k]+strlen(LAUNCH_PREFIX));
  for(i=0;i<750;++i){if(!read_state(path,&s)&&s.guard_done)break;nanosleep(&tick,0);}if(i==750)return 8;
  if(s.version!=1||s.phase!=4||s.error||!s.capture_done||!s.guard_done||s.cleanup_authorized||s.cleanup_started||s.restoration_verified||s.restored_pid||strcmp(s.inherited_cwd,"/extbin/apps/bin")||!s.obs_count||s.obs_count!=9||s.obs_dropped)return 9;
  {char logfile[192],text[256]={0};int lf;
   snprintf(logfile,sizeof(logfile),"/dev/shmem/delphi-nav-lifecycle-%s-start-cycle.txt",roots[k]+strlen(LAUNCH_PREFIX));lf=open(logfile,O_RDONLY);
   if(lf<0||read(lf,text,sizeof(text)-1)<=0){return 31;}close(lf);
   if(!strstr(text,"NAV_LIFECYCLE_FIXTURE_RESTART_PASS")){return 32;}
   if(!k){if(!strstr(text,"NAV_LIFECYCLE_DELAYED_START_PASS")){return 33;}puts("NAV_LIFECYCLE_DELAYED_START_PASS");}
   puts("NAV_LIFECYCLE_INTEGRATION_PASS");
  }
  if(k){if(!((uint64_t)s.reserved[0]|((uint64_t)s.reserved[1]<<32))||((uint64_t)s.reserved[0]|((uint64_t)s.reserved[1]<<32))==s.observed_start)return 29;puts("NAV_POST_EXEC_IDENTITY_PASS");}
  else {if(s.reserved[0]||s.reserved[1])return 30;puts("NAV_PRODUCTION_LIFECYCLE_PASS");}
  for(i=0;i<10;++i)nanosleep(&tick,0);
  if(same_observed(&s,manager)||read_state(LAUNCH_ACTIVE,&final)||final.observed_pid!=s.observed_pid)return 10;
  dump(k?"NAV_DISCONNECT_ORPHAN_PENDING_HEX":"NAV_DISCONNECT_PENDING_HEX",&s);
  puts(k?"NAV_DISCONNECT_ORPHAN_PENDING_PASS":"NAV_DISCONNECT_PENDING_NO_SIGNAL_PASS");
  if(!k){
   struct launch_state *shared;uint64_t correct;
   fd=open(LAUNCH_ACTIVE,O_RDWR);if(fd<0)return 11;shared=mmap(0,sizeof(*shared),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(shared==MAP_FAILED)return 12;
   correct=shared->observed_start;shared->observed_start=correct+1;
   if(arm(roots[k])!=3||cleanup(roots[k])!=3||same_observed(&s,manager))return 13;
   shared->observed_start=correct;
   correct=shared->manager_start;shared->manager_start=correct+1;
   if(arm(roots[k])!=3||cleanup(roots[k])!=3||same_observed(&s,manager))return 14;
   shared->manager_start=correct;
   puts("NAV_DISCONNECT_STATE_MISMATCH_REFUSED");
   snprintf(lockpath,sizeof(lockpath),"/dev/shmem/delphi-nav-launch-cleanup-%s.lock",roots[k]+strlen(LAUNCH_PREFIX));fd=open(lockpath,O_CREAT|O_EXCL|O_WRONLY,0600);if(fd<0)return 15;close(fd);
   if(cleanup(roots[k])!=3||same_observed(&s,manager))return 16;
   if(unlink(lockpath))return 17;
   puts("NAV_DISCONNECT_LOCK_REFUSED");munmap(shared,sizeof(*shared));
  }
  {uint32_t report[128];int rf;snprintf(path,sizeof(path),"/dev/shmem/delphi-nav-report-%s.bin",roots[k]+strlen(LAUNCH_PREFIX));
   if(arm(roots[k])||arm(roots[k]))return 24;
   rf=open(path,O_RDONLY);if(rf<0||read(rf,report,sizeof(report))!=(ssize_t)sizeof(report)||report[21]!=1)return 25;close(rf);puts("NAV_REPLAY_ARM_PASS");}
  if(k){struct launch_state *q;fd=open(LAUNCH_ACTIVE,O_RDWR);if(fd<0)return 40;q=mmap(0,sizeof(*q),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(q==MAP_FAILED)return 41;q->error=1005;q->observed_signal_error=3;q->cleanup_authorized=q->cleanup_started=1;
   if(finalize(roots[k])!=3||same_observed(&s,manager))return 42;
   q->error=q->observed_signal_error=q->cleanup_authorized=q->cleanup_started=0;munmap(q,sizeof(*q));puts("NAV_FINALIZE_ALIVE_REFUSAL_PASS");}
  if(cleanup(roots[k]))return 18;
  snprintf(path,sizeof(path),"/dev/shmem/delphi-nav-launch-final-%s.bin",roots[k]+strlen(LAUNCH_PREFIX));
  if(read_state(path,&final)||final.error||final.phase!=6||!final.capture_done||!final.cleanup_authorized||!final.cleanup_started||!final.restoration_verified||final.observed_pid==final.restored_pid)return 19;
  fd=pg_find(NAV_TARGET,manager,&stock);if(fd<0||stock.pid!=(pid_t)final.restored_pid)return 20;close(fd);
  if(k){struct launch_state failed=s;uint64_t correct;struct launch_state *q;pid_t restored=stock.pid;failed.error=1005;failed.observed_signal_error=3;failed.cleanup_authorized=failed.cleanup_started=1;
   if(cleanup(roots[k]))return 49;
   fd=open(path,O_WRONLY|O_TRUNC);if(fd<0||write(fd,&failed,sizeof(failed))!=sizeof(failed))return 50;close(fd);
   fd=open(LAUNCH_ACTIVE,O_CREAT|O_EXCL|O_RDWR,0600);if(fd<0||write(fd,&failed,sizeof(failed))!=sizeof(failed))return 43;q=mmap(0,sizeof(*q),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(q==MAP_FAILED)return 44;
   correct=q->manager_start;q->manager_start++;if(finalize(roots[k])!=3)return 45;q->manager_start=correct;munmap(q,sizeof(*q));puts("NAV_FINALIZE_STALE_REFUSAL_PASS");
   if(finalize(roots[k])||finalize(roots[k])){return 46;}fd=pg_find(NAV_TARGET,manager,&stock);if(fd<0||stock.pid!=restored)return 47;close(fd);snprintf(path,sizeof(path),"/dev/shmem/delphi-nav-launch-recovered-%s.bin",roots[k]+strlen(LAUNCH_PREFIX));if(read_state(path,&final)||final.error||!final.restoration_verified||final.phase!=6)return 48;puts("NAV_FINALIZE_RECOVERED_PASS");}
  if(!k&&cleanup(roots[k]))return 21;
  fd=pg_find(NAV_TARGET,manager,&stock);if(fd<0||stock.pid!=(pid_t)final.restored_pid)return 22;close(fd);
  dump(k?"NAV_DISCONNECT_ORPHAN_FINAL_HEX":"NAV_DISCONNECT_FINAL_HEX",&final);
  puts(k?"NAV_DISCONNECT_ORPHAN_CLEANUP_PASS":"NAV_DISCONNECT_LATE_CLEANUP_PASS");puts("NAV_DISCONNECT_IDEMPOTENT_PASS");
 }
 fd=pg_find(NAV_TARGET,manager,&stock);if(fd<0||pg_interrupt(fd,&stock))return 23;close(fd);kill(manager,SIGTERM);waitpid(manager,&status,0);puts("NAV_DISCONNECT_QNX_SUITE_PASS");return 0;
}
