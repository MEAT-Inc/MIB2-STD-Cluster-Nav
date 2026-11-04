#define _QNX_SOURCE 1
#include "launch.h"
#include "proc_guard.h"
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
static char root[128],original[192],wrapper[192],lifecycle[192],xsref[192],cref[192],library[192],nav_config[192],manager_ref[192],config_ref[192],logpath[192],reportpath[192],finalpath[192],lockpath[192];
static const struct timespec tick={0,100000000};
static int regular(const char *path) {struct stat s;return !lstat(path,&s)&&S_ISREG(s.st_mode);}
static int paths(const char *path) {
 unsigned i,n=(unsigned)strlen(LAUNCH_PREFIX);struct stat st;
 if(strlen(path)!=n+32 || strncmp(path,LAUNCH_PREFIX,n))return 0;
 for(i=0;i<32;++i)if(!((path[n+i]>='0'&&path[n+i]<='9')||(path[n+i]>='a'&&path[n+i]<='f')))return 0;
 if(lstat(path,&st)||!S_ISDIR(st.st_mode))return 0;
 strcpy(root,path);
 snprintf(original,sizeof(original),"%s/NavigationServer.original",root);
 snprintf(wrapper,sizeof(wrapper),"%s/nav_launch",root);
 snprintf(lifecycle,sizeof(lifecycle),"%s/nav_cycle",root);
 snprintf(xsref,sizeof(xsref),"%s/libXSAL.so.reference",root);
 snprintf(cref,sizeof(cref),"%s/libc.so.3.reference",root);
 snprintf(library,sizeof(library),"%s/libdelphi_cluster.so",root);
 snprintf(nav_config,sizeof(nav_config),"%s/NavServer.cfg.reference",root);
 snprintf(manager_ref,sizeof(manager_ref),"%s/procman.reference",root);
 snprintf(config_ref,sizeof(config_ref),"%s/procman-core.cfg",root);
 snprintf(logpath,sizeof(logpath),"/dev/shmem/delphi-nav-report-%s.bin",root+n);
 snprintf(reportpath,sizeof(reportpath),"/dev/shmem/delphi-nav-launch-report-%s.bin",root+n);
 snprintf(finalpath,sizeof(finalpath),"/dev/shmem/delphi-nav-launch-final-%s.bin",root+n);
 snprintf(lockpath,sizeof(lockpath),"/dev/shmem/delphi-nav-launch-cleanup-%s.lock",root+n);
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
static int references(void) {int ok=regular(lifecycle)&&identical("/proc/boot/libXSAL.so",xsref)&&identical("/proc/boot/libc.so.3",cref)&&identical(NAV_TARGET,original)&&identical(NAV_CONFIG,nav_config)&&identical(MANAGER_TARGET,manager_ref)&&identical("/etc/procman_core.cfg",config_ref);if(!ok)fprintf(stderr,"NAV_REFERENCES_REFUSED helper=%d xsal=%d libc=%d nav=%d cfg=%d manager=%d core=%d\n",regular(lifecycle),identical("/proc/boot/libXSAL.so",xsref),identical("/proc/boot/libc.so.3",cref),identical(NAV_TARGET,original),identical(NAV_CONFIG,nav_config),identical(MANAGER_TARGET,manager_ref),identical("/etc/procman_core.cfg",config_ref));return ok;}
static int own_alias(void) {char b[192];ssize_t n=readlink(NAV_TARGET,b,sizeof(b)-1);if(n<0)return 0;b[n]=0;return !strcmp(b,wrapper);}
static void record_error(unsigned code) {if(!state->error)state->error=code;}
static int remove_alias(void) {
 if(own_alias() && pathmgr_unlink(NAV_TARGET))return -1;
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
/* Nonce-specific report can only be published by the post-exec preload. */
static int sample_trace(void) {
 uint32_t w[128];struct stat st;int fd;ssize_t n;
 if(!regular(logpath))return 0;
 fd=open(logpath,O_RDONLY);if(fd<0)return 0;
 if(fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size!=512){close(fd);return 0;}
 n=read(fd,w,sizeof(w));close(fd);
 if(n!=(ssize_t)sizeof(w)||w[0]!=0x31504c52u||w[1]!=1||w[2]!=512||w[3]!=state->observed_pid||w[4]<1||w[4]>4)return 0;
 state->obs_status=(w[4]<=3&&!w[5])?1:0;state->obs_count=w[10];state->obs_dropped=w[5];return 1;
}
static int wrapper_main(int argc,char **argv) {
 int fd,mfd;pg_identity parent;const char *preload;unsigned i;
 if(argc<3||argc>4||strcmp(argv[1],"-fcfg")||strcmp(argv[2],NAV_CONFIG_REL))return 120;
 if(argc==4){if(strncmp(argv[3],"-X",2)||!argv[3][2]||strlen(argv[3])>22)return 120;for(i=2;argv[3][i];++i)if(argv[3][i]<'0'||argv[3][i]>'9')return 120;}
 fd=open(LAUNCH_ACTIVE,O_RDWR);if(fd<0)return 121;
 state=mmap(0,sizeof(*state),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(state==MAP_FAILED)return 122;
 if(state->magic!=LAUNCH_MAGIC||state->version!=1||state->bytes!=sizeof(*state)||!memchr(state->root,0,sizeof(state->root))||!paths(state->root)||!state->guard_armed||state->guard_done||!own_alias())return 123;
 mfd=pg_open(getppid(),0,&parent);if(mfd<0)return 124;
 close(mfd);
 if(parent.pid!=(pid_t)state->manager_pid||parent.start_time!=state->manager_start||strcmp(parent.executable,MANAGER_TARGET))return 124;
 /* Restore the factory namespace before any potentially failing exec/setup. */
 if(remove_alias())return 125;
 if(!references()||!getcwd(state->inherited_cwd,sizeof(state->inherited_cwd))||!identical(NAV_CONFIG_REL,nav_config))return 126;
 preload=getenv("LD_PRELOAD");if(preload&&*preload)return 127;
 if(setenv("LD_PRELOAD",library,1)||setenv("DELPHI_NAV_REPORT",logpath,1))return 128;
 __sync_synchronize();state->observed_pid=(unsigned)getpid();
 #ifdef NAV_LAUNCH_RACE_FIXTURE
 {pg_identity pre;int f=pg_open(getpid(),0,&pre);struct timespec delay={1,0};
  if(f<0||strcmp(pre.executable,NAV_TARGET)||pre.parent!=(pid_t)state->manager_pid)return 131;
  close(f);state->reserved[0]=(uint32_t)pre.start_time;state->reserved[1]=(uint32_t)(pre.start_time>>32);
  puts("NAV_PREEXEC_CANONICAL_RACE_PROVEN");fflush(stdout);nanosleep(&delay,0);}
#endif
 execv(NAV_TARGET,argv);return 129;
}
static int stock_now(pg_identity manager) {
 int f,m;pg_identity stock,check;
 f=pg_find(NAV_TARGET,manager.pid,&stock);if(f<0)return -1;
 if(stock.pid==(pid_t)state->observed_pid&&(!state->observed_start||stock.start_time==state->observed_start)){close(f);errno=ESTALE;return -1;}
 m=pg_open(manager.pid,0,&check);
 if(m<0||pg_matches(m,&manager)||own_alias()||!references()||pg_matches(f,&stock)){if(m>=0)close(m);close(f);return -1;}
 close(m);close(f);state->restored_pid=stock.pid;state->restored_start=stock.start_time;state->restoration_verified=1;state->phase=6;return 0;
}
/* Same car-validated SAL shutdown + exact-crash recovery helper for both edges.
 * The controller never substitutes a generic signal when helper checks fail. */
static int lifecycle_child(const char *mode,const char *edge,pg_identity nav,pg_identity manager){
 char pid[24],start[32],mp[24],ms[32],log[192];pid_t child;int status,fd;struct sigaction sa;
 if(!regular(lifecycle)){return 126;}
 snprintf(pid,sizeof(pid),"%u",(unsigned)nav.pid);snprintf(start,sizeof(start),"%llu",(unsigned long long)nav.start_time);
 snprintf(mp,sizeof(mp),"%u",(unsigned)manager.pid);snprintf(ms,sizeof(ms),"%llu",(unsigned long long)manager.start_time);
 snprintf(log,sizeof(log),"/dev/shmem/delphi-nav-lifecycle-%s-%s-%s.txt",root+strlen(LAUNCH_PREFIX),edge,mode);
 memset(&sa,0,sizeof(sa));sa.sa_handler=SIG_DFL;sigemptyset(&sa.sa_mask);if(sigaction(SIGCHLD,&sa,0)){return 126;}
 fflush(0);child=fork();if(!child){
  fd=open(log,O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0||dup2(fd,STDOUT_FILENO)<0||dup2(fd,STDERR_FILENO)<0){_exit(126);}close(fd);
  execl(lifecycle,"nav_cycle",mode,pid,start,mp,ms,(char*)0);_exit(127);
 }
 if(child<0){return 126;}
 while(waitpid(child,&status,0)<0){if(errno!=EINTR){return 126;}}
 return WIFEXITED(status)?WEXITSTATUS(status):124;
}
static int lifecycle_cycle(const char *edge,int navfd,pg_identity nav,int managerfd,pg_identity manager){
 int rc;
 if(pg_matches(navfd,&nav)||pg_matches(managerfd,&manager)){return 3;}
 rc=lifecycle_child("cycle",edge,nav,manager);
 printf("NAV_LIFECYCLE edge=%s mode=cycle exit=%d\n",edge,rc);fflush(stdout);
 if(rc==3){
  if(pg_matches(navfd,&nav)||pg_matches(managerfd,&manager)){return 3;}
  rc=lifecycle_child("recover",edge,nav,manager);
  printf("NAV_LIFECYCLE edge=%s mode=recover exit=%d\n",edge,rc);fflush(stdout);
 }
 return rc;
}
/* Capture expiry and controller loss NEVER authorize a post-capture signal. */
static int watchdog(pg_identity manager) {
 unsigned i;int ready=0,ofd=-1;pg_identity observed;
 state->guard_armed=1;
 for(i=0;i<1000&&!state->guard_done;++i){
  if(state->observed_pid&&sample_trace()){ofd=pg_open(state->observed_pid,0,&observed);if(ofd>=0){if(observed.parent==manager.pid&&!strcmp(observed.executable,NAV_TARGET)&&!pg_matches(ofd,&observed))break;close(ofd);ofd=-1;}}
  nanosleep(&tick,0);
 }
 if(ofd>=0){state->observed_start=observed.start_time;state->phase=3;
  printf("LAUNCH_OBSERVED pid=%u parent=%u base=%llx start=%llu exec=%s\n",(unsigned)observed.pid,(unsigned)observed.parent,(unsigned long long)observed.base_address,(unsigned long long)observed.start_time,observed.executable);
  for(i=0;i<state->capture_seconds*10&&!state->guard_done;++i){sample_trace();if(!ready&&state->obs_status==1){printf("LAUNCH_READY capture_seconds=%u\n",state->capture_seconds);fflush(stdout);ready=1;}if(pg_matches(ofd,&observed)){record_error(1100);break;}nanosleep(&tick,0);}
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
static int valid_state(const struct launch_state *s) {return s->magic==LAUNCH_MAGIC&&s->version==1&&s->bytes==sizeof(*s)&&memchr(s->root,0,sizeof(s->root))&&!strcmp(s->root,root)&&s->guard_done==1&&s->capture_done==1&&s->capture_seconds==20&&s->controller_pid>0&&s->controller_pid<=INT_MAX&&s->manager_pid>0&&s->manager_pid<=INT_MAX&&s->manager_start;}
/* An explicit disconnected-only entry point; no timer or failure path calls it.
 * Lock creation is exclusive. Ambiguous/abandoned cleanup locks fail closed. */
static int cleanup_disconnected(const char *path) {
 struct launch_state copy;struct stat st;pg_identity manager,observed,check;int fd,m=-1,o=-1,lock=-1,status=3;unsigned i;
 if(!paths(path))return 2;
 fd=open(LAUNCH_ACTIVE,O_RDWR);
 if(fd<0){
  if(load_state(finalpath,&copy)||!valid_state(&copy)||!copy.restoration_verified||copy.phase!=6)return 3;
  state=&copy;m=pg_open(copy.manager_pid,0,&manager);o=pg_open(copy.restored_pid,0,&observed);
  if(m>=0&&o>=0&&manager.start_time==copy.manager_start&&!strcmp(manager.executable,MANAGER_TARGET)&&observed.parent==manager.pid&&observed.start_time==copy.restored_start&&!strcmp(observed.executable,NAV_TARGET)&&!pg_matches(m,&manager)&&!pg_matches(o,&observed)&&!own_alias()&&references()){puts("LAUNCH_ALREADY_RESTORED");status=0;}
  goto done;
 }
 if(fstat(fd,&st)||st.st_size!=sizeof(*state)){close(fd);return 3;}
 state=mmap(0,sizeof(*state),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(state==MAP_FAILED)return 3;
 if(!valid_state(state)||state->phase!=4||state->restoration_verified||state->cleanup_started)return 3;
 m=pg_open(state->manager_pid,0,&manager);
 if(m<0||manager.start_time!=state->manager_start||strcmp(manager.executable,MANAGER_TARGET)||!references())goto done;
 o=pg_open(state->observed_pid,0,&observed);
 if(o>=0){
  if(observed.start_time!=state->observed_start||observed.parent!=manager.pid||(strcmp(observed.executable,NAV_TARGET)&&strcmp(observed.executable,wrapper))||pg_matches(o,&observed))goto done;
  fd=pg_find(NAV_TARGET,manager.pid,&check);
  if(fd>=0){int exact=check.pid==observed.pid&&check.start_time==observed.start_time&&check.parent==observed.parent&&!strcmp(check.executable,observed.executable)&&!pg_matches(fd,&check);close(fd);if(!exact)goto done;}
  else if(errno!=ESRCH)goto done;
 }else if(errno!=ENOENT&&errno!=ESRCH)goto done;
 lock=open(lockpath,O_WRONLY|O_CREAT|O_EXCL,0600);if(lock<0)goto done;close(lock);lock=-1;
 if(pg_matches(m,&manager)||!references()||(o>=0&&pg_matches(o,&observed))||remove_alias())goto done;
 state->cleanup_authorized=1;state->cleanup_started=1;
 if(o>=0){int rc=lifecycle_cycle("cleanup",o,observed,m,manager);if(rc){state->observed_signal_error=(unsigned)rc;record_error(1005);}}
 if(o>=0){close(o);o=-1;}
 for(i=0;i<100;++i){if(!stock_now(manager))break;nanosleep(&tick,0);}
 if(!state->restoration_verified)record_error(1006);else sample_trace();
 if(write_state(finalpath,state)){record_error(1007);goto done;}
 if(state->restoration_verified&&active_owned())unlink(LAUNCH_ACTIVE);
 if(state->restoration_verified)puts("LAUNCH_RESTORED");
 if(!state->error&&state->restoration_verified){puts("LAUNCH_COMPLETE");status=0;}else status=1;
 done:if(m>=0)close(m);if(o>=0)close(o);if(status)printf("LAUNCH_CLEANUP_REFUSED_OR_INCOMPLETE status=%d\n",status);fflush(stdout);return status;
}
/* Explicit operator arm; identity/report validation only, no transport or signal. */
static int arm_replay(const char *path) {
 struct launch_state copy={0};pg_identity manager={0},observed={0};struct stat st;uint32_t *w;const char *stage="active-open";unsigned report_status=0,report_error=0,report_stage=0;int a=-1,m=-1,o=-1,r=-1,rc=3;ssize_t n;
 if(!paths(path))return 2;
 a=open(LAUNCH_ACTIVE,O_RDONLY);if(a<0)goto done;
 stage="active-state";if(fstat(a,&st)||!S_ISREG(st.st_mode)||st.st_size!=sizeof(copy))goto done;
 n=read(a,&copy,sizeof(copy));if(n!=(ssize_t)sizeof(copy)||copy.magic!=LAUNCH_MAGIC||copy.version!=1||copy.bytes!=sizeof(copy)||!memchr(copy.root,0,sizeof(copy.root))||strcmp(copy.root,root)||!copy.observed_pid||!copy.observed_start||!copy.manager_pid||!copy.manager_start||copy.cleanup_started||copy.restoration_verified)goto done;
 stage="process-identity";m=pg_open(copy.manager_pid,0,&manager);o=pg_open(copy.observed_pid,0,&observed);
 if(m<0||o<0||manager.start_time!=copy.manager_start||strcmp(manager.executable,MANAGER_TARGET)||observed.start_time!=copy.observed_start||observed.parent!=manager.pid||strcmp(observed.executable,NAV_TARGET)||own_alias()||!references())goto done;
 stage="report-file";if(!regular(logpath))goto done;
 r=open(logpath,O_RDWR);if(r<0||fstat(r,&st)||!S_ISREG(st.st_mode)||st.st_size!=512)goto done;
 w=mmap(0,512,PROT_READ|PROT_WRITE,MAP_SHARED,r,0);if(w==MAP_FAILED)goto done;
 stage="report-ready-or-recheck";report_status=w[4];report_error=w[5];report_stage=w[22];
 if(w[0]==0x31504c52u&&w[1]==1&&w[2]==512&&w[3]==copy.observed_pid&&w[4]==1&&!w[5]&&w[21]<=1&&!pg_matches(m,&manager)&&!pg_matches(o,&observed)&&!own_alias()&&references()){
  if(__sync_bool_compare_and_swap(&w[21],0,1)||w[21]==1){puts("NAV_REPLAY_ARMED");rc=0;}
 }
 munmap(w,512);
 done:if(a>=0)close(a);if(m>=0)close(m);if(o>=0)close(o);if(r>=0)close(r);if(rc)printf("NAV_REPLAY_ARM_REFUSED stage=%s errno=%d expected_pid=%u expected_start=%llu expected_parent=%u current_pid=%u current_start=%llu current_parent=%u manager_expected_start=%llu manager_current_start=%llu report_status=%u report_error=%u report_stage=%u\n",stage,errno,copy.observed_pid,(unsigned long long)copy.observed_start,copy.manager_pid,(unsigned)observed.pid,(unsigned long long)observed.start_time,(unsigned)observed.parent,(unsigned long long)copy.manager_start,(unsigned long long)manager.start_time,report_status,report_error,report_stage);return rc;
}
int main(int argc,char **argv) {
 int fd,afd=-1,mfd=-1,status=0;pid_t guard;pg_identity baseline,manager;char *end;long pid;unsigned i;
 struct sigaction action;
 if(sizeof(struct launch_state)!=512)return 2;
 if(!strcmp(argv[0],"NavigationServer")||!strcmp(argv[0],NAV_TARGET))return wrapper_main(argc,argv);
 if(argc==3&&!strcmp(argv[1],"arm-replay"))return arm_replay(argv[2]);
 if(argc==3&&!strcmp(argv[1],"cleanup-disconnected"))return cleanup_disconnected(argv[2]);
 if(argc<2||strcmp(argv[1],"start-disconnected"))return 2;
 argc--;argv++;
 if(argc!=3||!paths(argv[1]))return 2;
 errno=0;pid=strtol(argv[2],&end,10);if(errno||*end||pid<=0||pid>INT_MAX)return 2;
 if(!regular(wrapper)||!regular(library)||!references())return 3;
 afd=pg_open((pid_t)pid,0,&baseline);if(afd<0)goto refused;
 printf("LAUNCH_CANDIDATE pid=%u parent=%u exec=%s\n",(unsigned)baseline.pid,(unsigned)baseline.parent,baseline.executable);
 if(strcmp(baseline.executable,NAV_TARGET))goto refused;
 mfd=pg_open(baseline.parent,0,&manager);if(mfd<0||strcmp(manager.executable,MANAGER_TARGET)||pg_matches(afd,&baseline))goto refused;
 printf("LAUNCH_BASELINE pid=%u parent=%u start=%llu exec=%s\n",(unsigned)baseline.pid,(unsigned)baseline.parent,(unsigned long long)baseline.start_time,baseline.executable);
 printf("LAUNCH_MANAGER pid=%u start=%llu exec=%s\n",(unsigned)manager.pid,(unsigned long long)manager.start_time,manager.executable);
 fd=open(LAUNCH_ACTIVE,O_RDWR|O_CREAT|O_EXCL,0600);if(fd<0)goto refused;
 if(ftruncate(fd,sizeof(*state))){close(fd);unlink(LAUNCH_ACTIVE);goto refused;}
 state=mmap(0,sizeof(*state),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(state==MAP_FAILED){unlink(LAUNCH_ACTIVE);goto refused;}
 memset(state,0,sizeof(*state));state->magic=LAUNCH_MAGIC;state->version=1;state->bytes=sizeof(*state);
 state->controller_pid=getpid();state->manager_pid=manager.pid;state->baseline_pid=baseline.pid;
 state->capture_seconds=20;
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
 else if(pathmgr_symlink(wrapper,NAV_TARGET)||!own_alias()){record_error(1012);state->guard_done=1;}
 else {
  state->phase=2;
  {int rc=lifecycle_cycle("start",afd,baseline,mfd,manager);if(rc){state->initial_signal_error=(unsigned)rc;record_error(1013);state->guard_done=1;}}
 }
 close(afd);close(mfd);
 while(waitpid(guard,&status,0)<0){if(errno!=EINTR){puts("LAUNCH_FAILED wait");return 1;}}
 if(!state->guard_armed && state->phase<2 && active_owned())unlink(LAUNCH_ACTIVE);
 if(WIFEXITED(status)&&WEXITSTATUS(status)==0&&!state->error&&state->observed_pid&&state->restoration_verified){return 0;}
 if(state->guard_done&&state->phase==4&&state->capture_done){puts("LAUNCH_PENDING_DISCONNECTED_CLEANUP");return 2;}
 printf("LAUNCH_FAILED phase=%u error=%u restored=%u\n",state->phase,state->error,state->restoration_verified);return 1;
 refused:if(afd>=0)close(afd);if(mfd>=0)close(mfd);printf("LAUNCH_REFUSED errno=%d\n",errno);return 3;
}
