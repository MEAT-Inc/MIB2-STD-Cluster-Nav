#define _QNX_SOURCE 1
#include "launch.h"
#include "proc_guard.h"
#include <errno.h>
#include <dirent.h>
#include <devctl.h>
#include <sys/procfs.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
static const char *root0=LAUNCH_PREFIX "00000000000000000000000000000000";
static const char *root1=LAUNCH_PREFIX "11111111111111111111111111111111";
static const struct timespec tick={0,100000000};
static int load_report(const char *path,struct launch_state *s){int fd=open(path,O_RDONLY);ssize_t n;if(fd<0)return -1;n=read(fd,s,sizeof(*s));close(fd);return n==(ssize_t)sizeof(*s)?0:-1;}
static int dump(const char *path,const char *label){
 unsigned char buf[512];ssize_t n,i;unsigned off=0;int fd=open(path,O_RDONLY),bad=0;
 unsigned limit=!strcmp(label,"LAUNCH_TRACE_HEX")?416:512;
 if(fd<0)return -1;
 printf("%s ",label);
 while((n=read(fd,buf,sizeof(buf)))>0){for(i=0;i<n;++i){if(off<limit)printf("%02x",buf[i]);else if(buf[i])bad=1;off++;}}
 puts("");close(fd);
 if(n<0||bad)return -1;
 if(limit==416)puts("LAUNCH_TRACE_ZERO_TAIL_OK");
 return 0;
}
static pid_t run(const char *root,pid_t pid){char exe[192],number[32];pid_t child;snprintf(exe,sizeof(exe),"%s/observer_launch",root);snprintf(number,sizeof(number),"%u",(unsigned)pid);fflush(0);child=fork();if(!child){if(setsid()<0)_exit(98);if(!strcmp(root,root1))execl(exe,"observer_launch",root,number,"phone",(char*)0);else execl(exe,"observer_launch",root,number,(char*)0);_exit(99);}return child;}
int main(void){
 pid_t manager,child;pg_identity stock,wrong;int fd=-1,status;unsigned i;struct launch_state s;char report[192],log[192];
 if(setenv("XSAL_INSTANCE_NAME","delphi_observer_launch_emulator",1))return 2;
 manager=fork();if(!manager){execl(MANAGER_TARGET,"procman","-f","/proc/boot/launch-manager.cfg","-c","0","-t",(char*)0);_exit(99);}if(manager<0)return 3;
 for(i=0;i<50;++i){fd=pg_find(AA_TARGET,manager,&stock);if(fd>=0)break;nanosleep(&tick,0);}
 if(fd<0){
  DIR *dir=opendir("/proc");struct dirent *entry;pg_identity probe;
  if(dir){while((entry=readdir(dir))){pid_t pp=(pid_t)atoi(entry->d_name);int test;
   if(pp<=0)continue;
   test=pg_open(pp,0,&probe);
   if(test>=0){printf("PG_PROBE pid=%u parent=%u exec=%s start=%llu\n",(unsigned)probe.pid,(unsigned)probe.parent,probe.executable,(unsigned long long)probe.start_time);close(test);}
   else {char path[64];procfs_info info;char raw[2048];int f,a=-1,b=-1;snprintf(path,sizeof(path),"/proc/%u/as",(unsigned)pp);f=open(path,O_RDONLY);if(f>=0){a=devctl(f,DCMD_PROC_INFO,&info,sizeof(info),0);memset(raw,0,sizeof(raw));b=devctl(f,DCMD_PROC_MAPDEBUG_BASE,raw,sizeof(raw),0);printf("PG_RAW pid=%u info=%d parent=%u debug=%d path=%s\n",(unsigned)pp,a,(unsigned)info.parent,b,raw+8);close(f);}else printf("PG_OPEN pid=%u errno=%d\n",(unsigned)pp,errno);}
  }closedir(dir);}perror("pg_find stock");return 4;}
 wrong=stock;wrong.start_time++;
 if(pg_interrupt(fd,&wrong)!=-1||errno!=ESTALE||pg_matches(fd,&stock))return 5;
 close(fd);puts("LAUNCH_IDENTITY_MISMATCH_REJECTED");
 child=run(root0,stock.pid);if(child<0||waitpid(child,&status,0)!=child||!WIFEXITED(status)||WEXITSTATUS(status))return 6;
 snprintf(report,sizeof(report),"/dev/shmem/delphi-aa-report-%s.bin",root0+strlen(LAUNCH_PREFIX));
 snprintf(log,sizeof(log),"/dev/shmem/delphi-observer-aa-%s.bin",root0+strlen(LAUNCH_PREFIX));
 if(load_report(report,&s)||s.error||s.phase!=6||!s.restoration_verified||(!s.obs_count||s.obs_count+s.obs_dropped!=9)||s.observed_pid==s.restored_pid||!s.guard_done){printf("LAUNCH_BENCH_REPORT error=%u phase=%u restored=%u count=%u dropped=%u got=%u value=%08x expected=%08x base=%08x\n",s.error,s.phase,s.restoration_verified,s.obs_count,s.obs_dropped,s.got_valid,s.binding_value,s.expected_binding,s.observer_base);return 7;}
 if(dump(report,"LAUNCH_REPORT_HEX")||dump(log,"LAUNCH_TRACE_HEX"))return 15;
 puts("LAUNCH_MANAGED_CAPTURE_RESTORE_PASS");
 fd=pg_find(AA_TARGET,manager,&stock);if(fd<0)return 8;close(fd);
 child=run(root1,stock.pid);if(child<0)return 9;
 for(i=0;i<80;++i){if(!load_report(LAUNCH_ACTIVE,&s)&&s.observed_start)break;nanosleep(&tick,0);}
 if(!s.observed_start)return 10;
 if(kill(-child,SIGHUP)||waitpid(child,&status,0)!=child||!WIFSIGNALED(status)||WTERMSIG(status)!=SIGHUP)return 11;
 snprintf(report,sizeof(report),"/dev/shmem/delphi-aa-report-%s.bin",root1+strlen(LAUNCH_PREFIX));
 for(i=0;i<750;++i){if(!load_report(report,&s)&&s.guard_done)break;nanosleep(&tick,0);}
 if(i==750||s.error||!s.restoration_verified||s.phase!=6||(!s.obs_count||s.obs_count+s.obs_dropped!=9))return 12;
 if(dump(report,"LAUNCH_ORPHAN_REPORT_HEX"))return 16;
 fd=pg_find(AA_TARGET,manager,&stock);if(fd<0||stock.pid!=(pid_t)s.restored_pid)return 13;
 if(pg_interrupt(fd,&stock))return 14;
 close(fd);
 kill(manager,SIGTERM);waitpid(manager,&status,0);
 puts("LAUNCH_ORPHAN_RESTORE_PASS");puts("LAUNCH_HANGUP_GROUP_RESTORE_PASS");puts("LAUNCH_PHONE_WINDOW_PASS");puts("LAUNCH_QNX_SUITE_PASS");return 0;
}
