#define _QNX_SOURCE 1
#include "launch.h"
#include "proc_guard.h"
#include "observer.h"
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/pathmgr.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
static struct launch_state *state;
static char root[128],original[192],wrapper[192],library[192],receiver[192],manager_ref[192],config_ref[192],logpath[192],reportpath[192],finalpath[192],lockpath[192];
static const struct timespec tick={0,100000000};
static int regular(const char *path) {struct stat s;return !lstat(path,&s)&&S_ISREG(s.st_mode);}
static int paths(const char *path) {
 unsigned i,n=(unsigned)strlen(LAUNCH_PREFIX);struct stat st;
 if(strlen(path)!=n+32 || strncmp(path,LAUNCH_PREFIX,n))return 0;
 for(i=0;i<32;++i)if(!((path[n+i]>='0'&&path[n+i]<='9')||(path[n+i]>='a'&&path[n+i]<='f')))return 0;
 if(lstat(path,&st)||!S_ISDIR(st.st_mode))return 0;
 strcpy(root,path);
 snprintf(original,sizeof(original),"%s/AndroidAuto.original",root);
 snprintf(wrapper,sizeof(wrapper),"%s/observer_launch",root);
 snprintf(library,sizeof(library),"%s/libdelphi_observer.so",root);
 snprintf(receiver,sizeof(receiver),"%s/receiver.reference",root);
 snprintf(manager_ref,sizeof(manager_ref),"%s/procman.reference",root);
 snprintf(config_ref,sizeof(config_ref),"%s/procman-core.cfg",root);
 snprintf(logpath,sizeof(logpath),"/dev/shmem/delphi-observer-aa-%s.bin",root+n);
 snprintf(reportpath,sizeof(reportpath),"/dev/shmem/delphi-aa-report-%s.bin",root+n);
 snprintf(finalpath,sizeof(finalpath),"/dev/shmem/delphi-aa-final-%s.bin",root+n);
 snprintf(lockpath,sizeof(lockpath),"/dev/shmem/delphi-aa-cleanup-%s.lock",root+n);
 return 1;
}
static int identical(const char *a,const char *b) {
 unsigned char x[4096],y[4096];ssize_t n,m;int f=-1,g=-1,result=0;
 /* Stock library version names may be symlinks; compare their resolved bytes.
  * Private staged references must remain regular non-symlink files. */
 {struct stat st;if(stat(a,&st)||!S_ISREG(st.st_mode)||!regular(b))return 0;}
 f=open(a,O_RDONLY);g=open(b,O_RDONLY);if(f<0||g<0)goto done;
 for(;;){n=read(f,x,sizeof(x));m=read(g,y,sizeof(y));if(n<0||m<0||n!=m)break;if(!n){result=1;break;}if(memcmp(x,y,(size_t)n))break;}
 done:if(f>=0)close(f);if(g>=0)close(g);return result;
}
static int references(void) {return identical(AA_TARGET,original)&&identical(RECEIVER_TARGET,receiver)&&identical(MANAGER_TARGET,manager_ref)&&identical("/etc/procman_core.cfg",config_ref);}
static int own_alias(void) {char b[192];ssize_t n=readlink(AA_TARGET,b,sizeof(b)-1);if(n<0)return 0;b[n]=0;return !strcmp(b,wrapper);}
static void record_error(unsigned code) {if(!state->error)state->error=code;}
static int remove_alias(void) {
 if(own_alias() && pathmgr_unlink(AA_TARGET))return -1;
 if(own_alias())return -1;
 state->alias_removed=1;return 0;
}
static int write_state(const char *path,const struct launch_state *value) {
 int fd=open(path,O_WRONLY|O_CREAT|O_EXCL,0600);size_t off=0;ssize_t n;
 if(fd<0)return -1;
 while(off<sizeof(*value)){n=write(fd,(const char*)value+off,sizeof(*value)-off);if(n<=0){close(fd);return -1;}off+=(size_t)n;}
 return close(fd);
}
static int write_report(void) {struct launch_state copy=*state;copy.guard_done=1;return write_state(reportpath,&copy);}
static int active_owned(void) {
 struct launch_state copy;int fd=open(LAUNCH_ACTIVE,O_RDONLY);ssize_t n;
 if(fd<0)return 0;
 n=read(fd,&copy,sizeof(copy));close(fd);
 return n==(ssize_t)sizeof(copy)&&copy.magic==LAUNCH_MAGIC&&copy.controller_pid==state->controller_pid&&!memcmp(copy.root,state->root,sizeof(copy.root));
}
static void sample_trace(void) {
 struct obs_header h;int fd=open(logpath,O_RDONLY);ssize_t n;
 if(fd<0)return;
 n=read(fd,&h,sizeof(h));close(fd);
 if(n!=(ssize_t)sizeof(h)||h.magic!=OBS_MAGIC||h.version!=1||h.pid!=state->observed_pid)return;
 state->obs_status=h.status;state->obs_count=h.count;state->obs_dropped=h.dropped;
}
static int wrapper_main(int argc,char **argv) {
 int fd,mfd;pg_identity parent;const char *preload;unsigned i;
 if(argc<2||argc>3||strcmp(argv[1],"-t"))return 120;
 if(argc==3){if(strncmp(argv[2],"-X",2)||!argv[2][2]||strlen(argv[2])>24)return 120;for(i=2;argv[2][i];++i)if(argv[2][i]<'0'||argv[2][i]>'9')return 120;}
 fd=open(LAUNCH_ACTIVE,O_RDWR);if(fd<0)return 121;
 state=mmap(0,sizeof(*state),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(state==MAP_FAILED)return 122;
 if(state->magic!=LAUNCH_MAGIC||state->version!=3||state->bytes!=sizeof(*state)||!memchr(state->root,0,sizeof(state->root))||!paths(state->root)||!state->guard_armed||state->guard_done||!own_alias())return 123;
 mfd=pg_open(getppid(),0,&parent);if(mfd<0)return 124;
 close(mfd);
 if(parent.pid!=(pid_t)state->manager_pid||parent.start_time!=state->manager_start||strcmp(parent.executable,MANAGER_TARGET))return 124;
 /* Restore the factory namespace before any potentially failing exec/setup. */
 if(remove_alias())return 125;
 if(!references())return 126;
 preload=getenv("LD_PRELOAD");if(preload&&*preload)return 127;
 if(setenv("LD_PRELOAD",library,1)||setenv("DELPHI_OBSERVER_LOG",logpath,1))return 128;
 __sync_synchronize();state->observed_pid=(unsigned)getpid();
 execv(original,argv);return 129;
}
static int stock_now(pg_identity manager) {
 int f,m;pg_identity stock,check;
 f=pg_find(AA_TARGET,manager.pid,&stock);if(f<0)return -1;
 m=pg_open(manager.pid,0,&check);
 if(m<0||pg_matches(m,&manager)||own_alias()||!references()||pg_matches(f,&stock)){if(m>=0)close(m);close(f);return -1;}
 close(m);close(f);state->restored_pid=stock.pid;state->restored_start=stock.start_time;state->restoration_verified=1;state->phase=6;return 0;
}
/* Capture expiry and controller loss NEVER authorize a post-capture signal. */
static int watchdog(pg_identity manager) {
 unsigned i;int ready=0,ofd=-1;pg_identity observed;
 state->guard_armed=1;
 for(i=0;i<150&&!state->guard_done;++i){
  if(state->observed_pid){ofd=pg_open(state->observed_pid,0,&observed);if(ofd>=0){if(observed.parent==manager.pid&&!strcmp(observed.executable,original))break;close(ofd);ofd=-1;}}
  nanosleep(&tick,0);
 }
 if(ofd>=0){state->observed_start=observed.start_time;state->phase=3;
  printf("LAUNCH_OBSERVED pid=%u parent=%u base=%llx start=%llu exec=%s\n",(unsigned)observed.pid,(unsigned)observed.parent,(unsigned long long)observed.base_address,(unsigned long long)observed.start_time,observed.executable);
  for(i=0;i<state->capture_seconds*10&&!state->guard_done;++i){sample_trace();if(!ready&&state->obs_status==OBS_READY){printf("LAUNCH_READY capture_seconds=%u\n",state->capture_seconds);fflush(stdout);ready=1;}if(pg_matches(ofd,&observed)){record_error(1100);break;}nanosleep(&tick,0);}
  close(ofd);
 }else if(!state->guard_done){record_error(1001);ofd=pg_find(wrapper,manager.pid,&observed);if(ofd>=0){state->observed_pid=observed.pid;state->observed_start=observed.start_time;close(ofd);}}
 if(remove_alias())record_error(1002);
 state->guard_done=0;state->capture_done=1;state->phase=4;sample_trace();
 /* If the observed child already exited, verify existing stock without a signal. */
 if(!state->observed_pid||!state->observed_start){if(stock_now(manager))record_error(1006);}
 else {ofd=pg_open(state->observed_pid,0,&observed);if(ofd<0&&(errno==ENOENT||errno==ESRCH))(void)stock_now(manager);if(ofd>=0)close(ofd);}
 if(write_report())record_error(1007);
 __sync_synchronize();state->guard_done=1;
 if(state->restoration_verified&&active_owned())unlink(LAUNCH_ACTIVE);
 puts("LAUNCH_CAPTURE_DONE");
 if(state->restoration_verified)puts("LAUNCH_RESTORED_NO_SIGNAL");else puts("LAUNCH_AWAITING_DISCONNECTED_CLEANUP");
 fflush(stdout);return state->restoration_verified?(state->error?1:0):2;
}
static int load_state(const char *path,struct launch_state *copy) {int fd=open(path,O_RDONLY);ssize_t n;if(fd<0)return -1;n=read(fd,copy,sizeof(*copy));close(fd);return n==(ssize_t)sizeof(*copy)?0:-1;}
static int valid_state(const struct launch_state *s) {return s->magic==LAUNCH_MAGIC&&s->version==3&&s->bytes==sizeof(*s)&&memchr(s->root,0,sizeof(s->root))&&!strcmp(s->root,root)&&s->guard_done==1&&s->capture_done==1&&(s->capture_seconds==20||s->capture_seconds==60)&&s->controller_pid>0&&s->controller_pid<=INT_MAX&&s->manager_pid>0&&s->manager_pid<=INT_MAX&&s->manager_start;}
/* An explicit disconnected-only entry point; no timer or failure path calls it.
 * Lock creation is exclusive. Ambiguous/abandoned cleanup locks fail closed. */
static int cleanup_disconnected(const char *path) {
 struct launch_state copy;struct stat st;pg_identity manager,observed,check;int fd,m=-1,o=-1,lock=-1,status=3;unsigned i;
 if(!paths(path))return 2;
 fd=open(LAUNCH_ACTIVE,O_RDWR);
 if(fd<0){
  if(load_state(finalpath,&copy)||!valid_state(&copy)||!copy.restoration_verified||copy.phase!=6)return 3;
  state=&copy;m=pg_open(copy.manager_pid,0,&manager);o=pg_open(copy.restored_pid,0,&observed);
  if(m>=0&&o>=0&&manager.start_time==copy.manager_start&&!strcmp(manager.executable,MANAGER_TARGET)&&observed.parent==manager.pid&&observed.start_time==copy.restored_start&&!strcmp(observed.executable,AA_TARGET)&&!pg_matches(m,&manager)&&!pg_matches(o,&observed)&&!own_alias()&&references()){puts("LAUNCH_ALREADY_RESTORED");status=0;}
  goto done;
 }
 if(fstat(fd,&st)||st.st_size!=sizeof(*state)){close(fd);return 3;}
 state=mmap(0,sizeof(*state),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(state==MAP_FAILED)return 3;
 if(!valid_state(state)||state->phase!=4||state->restoration_verified||state->cleanup_started)return 3;
 m=pg_open(state->manager_pid,0,&manager);
 if(m<0||manager.start_time!=state->manager_start||strcmp(manager.executable,MANAGER_TARGET)||!references())goto done;
 o=pg_open(state->observed_pid,0,&observed);
 if(o>=0){
  if(observed.start_time!=state->observed_start||observed.parent!=manager.pid||(strcmp(observed.executable,original)&&strcmp(observed.executable,wrapper))||pg_matches(o,&observed))goto done;
  fd=pg_find(AA_TARGET,manager.pid,&check);if(fd>=0){close(fd);goto done;}if(errno!=ESRCH)goto done;
 }else if(errno!=ENOENT&&errno!=ESRCH)goto done;
 lock=open(lockpath,O_WRONLY|O_CREAT|O_EXCL,0600);if(lock<0)goto done;close(lock);lock=-1;
 if(pg_matches(m,&manager)||!references()||(o>=0&&pg_matches(o,&observed))||remove_alias())goto done;
 state->cleanup_authorized=1;state->cleanup_started=1;
 if(o>=0&&pg_interrupt(o,&observed)){state->observed_signal_error=errno;record_error(1005);}
 if(o>=0){close(o);o=-1;}
 for(i=0;i<100;++i){if(!stock_now(manager))break;nanosleep(&tick,0);}
 if(!state->restoration_verified)record_error(1006);else sample_trace();
 if(write_state(finalpath,state)){record_error(1007);goto done;}
 if(state->restoration_verified&&active_owned())unlink(LAUNCH_ACTIVE);
 if(state->restoration_verified)puts("LAUNCH_RESTORED");
 if(!state->error&&state->restoration_verified){puts("LAUNCH_COMPLETE");status=0;}else status=1;
 done:if(m>=0)close(m);if(o>=0)close(o);if(status)printf("LAUNCH_CLEANUP_REFUSED_OR_INCOMPLETE status=%d\n",status);fflush(stdout);return status;
}
int main(int argc,char **argv) {
 int fd,afd=-1,mfd=-1,status=0;pid_t guard;pg_identity baseline,manager;char *end;long pid;unsigned i;
 struct sigaction action;
 if(sizeof(struct launch_state)!=512)return 2;
 if(!strcmp(argv[0],"AndroidAuto")||!strcmp(argv[0],AA_TARGET))return wrapper_main(argc,argv);
 if(argc==3&&!strcmp(argv[1],"cleanup-disconnected"))return cleanup_disconnected(argv[2]);
 if(argc<2||strcmp(argv[1],"start-disconnected"))return 2;
 argc--;argv++;
 if((argc!=3&&argc!=4)||!paths(argv[1])||(argc==4&&strcmp(argv[3],"phone")))return 2;
 errno=0;pid=strtol(argv[2],&end,10);if(errno||*end||pid<=0||pid>INT_MAX)return 2;
 if(!regular(wrapper)||!regular(library)||!references())return 3;
 afd=pg_open((pid_t)pid,0,&baseline);if(afd<0)goto refused;
 printf("LAUNCH_CANDIDATE pid=%u parent=%u exec=%s\n",(unsigned)baseline.pid,(unsigned)baseline.parent,baseline.executable);
 if(strcmp(baseline.executable,AA_TARGET))goto refused;
 mfd=pg_open(baseline.parent,0,&manager);if(mfd<0||strcmp(manager.executable,MANAGER_TARGET)||pg_matches(afd,&baseline))goto refused;
 printf("LAUNCH_BASELINE pid=%u parent=%u start=%llu exec=%s\n",(unsigned)baseline.pid,(unsigned)baseline.parent,(unsigned long long)baseline.start_time,baseline.executable);
 printf("LAUNCH_MANAGER pid=%u start=%llu exec=%s\n",(unsigned)manager.pid,(unsigned long long)manager.start_time,manager.executable);
 fd=open(LAUNCH_ACTIVE,O_RDWR|O_CREAT|O_EXCL,0600);if(fd<0)goto refused;
 if(ftruncate(fd,sizeof(*state))){close(fd);unlink(LAUNCH_ACTIVE);goto refused;}
 state=mmap(0,sizeof(*state),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(state==MAP_FAILED){unlink(LAUNCH_ACTIVE);goto refused;}
 memset(state,0,sizeof(*state));state->magic=LAUNCH_MAGIC;state->version=3;state->bytes=sizeof(*state);
 state->controller_pid=getpid();state->manager_pid=manager.pid;state->baseline_pid=baseline.pid;
 state->capture_seconds=argc==4?60:20;
 state->baseline_start=baseline.start_time;state->manager_start=manager.start_time;strcpy(state->root,root);
 memset(&action,0,sizeof(action));action.sa_handler=SIG_DFL;sigemptyset(&action.sa_mask);
 if(sigaction(SIGCHLD,&action,0)){unlink(LAUNCH_ACTIVE);goto refused;}
 fflush(0);guard=fork();
 if(!guard){
  close(afd);close(mfd);
  action.sa_handler=SIG_IGN;
  if(sigaction(SIGHUP,&action,0)||setsid()<0){record_error(1014);state->guard_done=1;write_report();_exit(1);}
  _exit(watchdog(manager));
 }
 if(guard<0){unlink(LAUNCH_ACTIVE);goto refused;}
 for(i=0;i<20&&!state->guard_armed;++i)nanosleep(&tick,0);
 if(!state->guard_armed){record_error(1010);state->guard_done=1;}
 else if(pg_matches(mfd,&manager)||pg_matches(afd,&baseline)||!references()){record_error(1011);state->guard_done=1;}
 else if(pathmgr_symlink(wrapper,AA_TARGET)||!own_alias()){record_error(1012);state->guard_done=1;}
 else {
  state->phase=2;
  if(pg_interrupt(afd,&baseline)){state->initial_signal_error=(unsigned)errno;record_error(1013);state->guard_done=1;}
 }
 close(afd);close(mfd);
 while(waitpid(guard,&status,0)<0){if(errno!=EINTR){puts("LAUNCH_FAILED wait");return 1;}}
 if(!state->guard_armed && state->phase<2 && active_owned())unlink(LAUNCH_ACTIVE);
 if(WIFEXITED(status)&&WEXITSTATUS(status)==0&&!state->error&&state->observed_pid&&state->restoration_verified){return 0;}
 if(state->guard_done&&state->phase==4&&state->capture_done){puts("LAUNCH_PENDING_DISCONNECTED_CLEANUP");return 2;}
 printf("LAUNCH_FAILED phase=%u error=%u restored=%u\n",state->phase,state->error,state->restoration_verified);return 1;
 refused:if(afd>=0)close(afd);if(mfd>=0)close(mfd);printf("LAUNCH_REFUSED errno=%d\n",errno);return 3;
}
