#define _QNX_SOURCE 1
#include "sal-fixture-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
#include <sys/procfs.h>
#include <devctl.h>
#include <sys/wait.h>
#include "proc_guard.h"
#include "stall-guard.h"
static void pause_ms(unsigned ms){struct timespec t={ms/1000,(ms%1000)*1000000};nanosleep(&t,0);}
static uint32_t target(void){uint32_t p=0;int f=open("/dev/shmem/sal-target-ready.bin",O_RDONLY);if(f>=0){if(read(f,&p,4)!=4)p=0;close(f);}return p;}
static uint32_t wait_target(void){unsigned i;uint32_t p;for(i=0;i<3000;i++){p=target();if(p)return p;pause_ms(1);}return 0;}
static int wait_gone(uint32_t p){unsigned i;char path[64];snprintf(path,sizeof(path),"/proc/%u/as",p);for(i=0;i<3000;i++){int f=open(path,O_RDONLY);if(f<0&&errno==ENOENT&&!target()) { return 0; }
if(f>=0){close(f);}pause_ms(1);}return -1;}
static void registry(pid_t pid){char path[64],name[100];uint32_t count=0,ptr=0,w[16];unsigned i;int f;snprintf(path,sizeof(path),"/proc/%u/as",(unsigned)pid);f=open(path,O_RDONLY);if(f<0)return;if(pread(f,&count,4,0x12ff7c)!=4){close(f);return;}printf("REGISTRY count=%u\n",count);if(count>108){close(f);return;}for(i=0;i<count;i++){if(pread(f,&ptr,4,0x12ff80+4*i)!=4||!ptr||pread(f,w,sizeof(w),ptr)!=sizeof(w))break;memset(name,0,sizeof(name));if(w[0])pread(f,name,sizeof(name)-1,w[0]);printf("REGISTRY id=%u pid=%u status=%u state=%u mask=%x name=%s\n",((unsigned char*)w)[16],w[8],w[13],w[14],w[1],name);{char child[64];int c;unsigned tid;snprintf(child,sizeof(child),"/proc/%u/as",w[8]);c=open(child,O_RDONLY);if(c>=0){for(tid=1;tid<=8;tid++){procfs_status z;memset(&z,0,sizeof(z));z.tid=tid;if(!devctl(c,DCMD_PROC_TIDSTATUS,&z,sizeof(z),0))printf("TARGET_TID %u state=%u ip=%llx sp=%llx peer=%u\n",tid,z.state,(unsigned long long)z.ip,(unsigned long long)z.sp,(unsigned)z.blocked.connect.pid);}close(c);}}}close(f);fflush(stdout);}
static int cycle_helper(pg_identity n,pg_identity pm,int bad){char p[24],start[32],m[24],ms[32];pid_t c;int status;snprintf(p,sizeof(p),"%u",(unsigned)n.pid);snprintf(start,sizeof(start),"%llu",(unsigned long long)n.start_time+bad);snprintf(m,sizeof(m),"%u",(unsigned)pm.pid);snprintf(ms,sizeof(ms),"%llu",(unsigned long long)pm.start_time);fflush(0);c=fork();if(!c){execl("/proc/boot/nav_cycle_test","nav_cycle_test","cycle",p,start,m,ms,(char*)0);_exit(99);}if(c<0||waitpid(c,&status,0)!=c||!WIFEXITED(status)) { return 99; }
return WEXITSTATUS(status);}
static int page_helper(pg_identity n,pg_identity pm,unsigned address,int bad){
 char pid[24],start[32],manager[24],ms[32],va[24];pid_t c;int status;
 snprintf(pid,sizeof(pid),"%u",(unsigned)n.pid);snprintf(start,sizeof(start),"%llu",(unsigned long long)n.start_time+bad);
 snprintf(manager,sizeof(manager),"%u",(unsigned)pm.pid);snprintf(ms,sizeof(ms),"%llu",(unsigned long long)pm.start_time);snprintf(va,sizeof(va),"%u",address);
 fflush(0);c=fork();
 if(!c){int f=open("/dev/shmem/nav-page-test.bin",O_WRONLY|O_CREAT|O_TRUNC,0600);if(f<0||dup2(f,STDOUT_FILENO)<0){_exit(98);}close(f);
  execl("/proc/boot/nav_cycle_test","nav_cycle_test","page",pid,start,manager,ms,va,(char*)0);_exit(99);}
 if(c<0||waitpid(c,&status,0)!=c||!WIFEXITED(status)){return 99;}
 return WEXITSTATUS(status);
}
static int page_tests(pg_identity n,pg_identity pm){
 unsigned char b[4097];ssize_t got;int f;unsigned i;const unsigned badaddr[2]={0x100004,0x40000000};
 if(page_helper(n,pm,0x100000,0)){return -1;}
 f=open("/dev/shmem/nav-page-test.bin",O_RDONLY);if(f<0){return -1;}got=read(f,b,sizeof(b));close(f);
 if(got!=4096||memcmp(b,"\177ELF\1\1\1",7)){return -1;}
 puts("NAV_PAGE_READ_QNX_PASS");
 if(page_helper(n,pm,0x100000,1)!=3){return -1;}
 f=open("/dev/shmem/nav-page-test.bin",O_RDONLY);if(f<0){return -1;}got=read(f,b,sizeof(b));close(f);if(got){return -1;}
 puts("NAV_PAGE_STALE_IDENTITY_REFUSAL_PASS");
 for(i=0;i<2;i++){
  if(page_helper(n,pm,badaddr[i],0)!=3){return -1;}
  f=open("/dev/shmem/nav-page-test.bin",O_RDONLY);if(f<0){return -1;}got=read(f,b,sizeof(b));close(f);if(got){return -1;}
 }
 puts("NAV_PAGE_BAD_ADDRESS_REFUSAL_PASS");return 0;
}
static int stall_capture_test(void){
 uint32_t words[STALL_WORDS],m[2],saved;int f;ssize_t n;
 f=open("/proc/boot/stall.stack",O_RDONLY);if(f<0){return -1;}n=read(f,words,sizeof(words));close(f);if(n!=sizeof(words)){return -1;}
 f=open("/proc/boot/stall.mutex",O_RDONLY);if(f<0){return -1;}n=read(f,m,sizeof(m));close(f);if(n!=sizeof(m)){return -1;}
 if(!stall_blob(words,m,0x7eaa4,704597)){return -1;}
 saved=words[55];words[55]=6;if(stall_blob(words,m,0x7eaa4,704597)){return -1;}words[55]=saved;
 saved=words[192];words[192]+=4;if(stall_blob(words,m,0x7eaa4,704597)){return -1;}words[192]=saved;
 saved=m[1];m[1]=0;if(stall_blob(words,m,0x7eaa4,704597)){return -1;}m[1]=saved;
 if(stall_blob(words,m,0x7eaa4,704598)){return -1;}
 {uint32_t ext[STALL_EXT_WORDS];unsigned i;const unsigned required[]={0,10,28,46,56,57,58,59,60,71,72,73,74,75,76,107,110,116,117,118,208};
 f=open("/proc/boot/stall.replay.stack",O_RDONLY);if(f<0)return -1;n=read(f,ext,sizeof(ext));close(f);if(n!=sizeof(ext))return -1;
 f=open("/proc/boot/stall.replay.mutex",O_RDONLY);if(f<0)return -1;n=read(f,m,sizeof(m));close(f);if(n!=sizeof(m))return -1;
 if(!stall_blob_tid(ext,m,0x5da64,1376328,3)||stall_blob_tid(ext,m,0x5da64,1376328,2)||stall_blob_tid(ext,m,0x5da64,1376328,4)||stall_blob_tid(ext,m,0x5da64,1376329,3))return -1;
 for(i=0;i<sizeof(required)/sizeof(required[0]);i++){unsigned k=required[i];saved=ext[k];ext[k]^=4;if(stall_blob_tid(ext,m,0x5da64,1376328,3))return -1;ext[k]=saved;}
 saved=m[1];m[1]^=0x10000;if(stall_blob_tid(ext,m,0x5da64,1376328,3))return -1;m[1]=saved;
 puts("NAV_REPLAY_STALL_CAPTURE_GUARD_PASS");
 }
 {uint32_t ext[STALL_EXT_WORDS];unsigned i;const unsigned required[]={0,10,28,46,56,57,58,59,60,71,72,73,74,75,76,103,104,105,106,107,108,109,110,112,115,116,117,118,208};
 f=open("/proc/boot/stall.live.stack",O_RDONLY);if(f<0)return -1;n=read(f,ext,sizeof(ext));close(f);if(n!=sizeof(ext))return -1;
 f=open("/proc/boot/stall.live.mutex",O_RDONLY);if(f<0)return -1;n=read(f,m,sizeof(m));close(f);if(n!=sizeof(m))return -1;
 if(!stall_blob_tid(ext,m,0x5da64,1560661,3)||stall_blob_tid(ext,m,0x5da64,1560661,2)||stall_blob_tid(ext,m,0x5da64,1560661,4)||stall_blob_tid(ext,m,0x5da68,1560661,3)||stall_blob_tid(ext,m,0x5da64,1560662,3))return -1;
 for(i=0;i<sizeof(required)/sizeof(required[0]);i++){unsigned k=required[i];saved=ext[k];ext[k]^=4;if(stall_blob_tid(ext,m,0x5da64,1560661,3))return -1;ext[k]=saved;}
 saved=m[0];m[0]=0;if(stall_blob_tid(ext,m,0x5da64,1560661,3))return -1;m[0]=saved;
 saved=m[1];m[1]^=0x10000;if(stall_blob_tid(ext,m,0x5da64,1560661,3))return -1;m[1]=saved;
 puts("NAV_LIVE_STALL_CAPTURE_GUARD_PASS");
 }
 puts("NAV_STALL_CAPTURE_GUARD_PASS");return 0;
}
static int recover_helper(pg_identity n,pg_identity pm,const char *mode,int bad){
 char pid[24],start[32],manager[24],ms[32];pid_t c;int status;
 snprintf(pid,sizeof(pid),"%u",(unsigned)n.pid);snprintf(start,sizeof(start),"%llu",(unsigned long long)n.start_time+bad);
 snprintf(manager,sizeof(manager),"%u",(unsigned)pm.pid);snprintf(ms,sizeof(ms),"%llu",(unsigned long long)pm.start_time);
 fflush(0);c=fork();if(!c){execl("/proc/boot/nav_cycle_test","nav_cycle_test",mode,pid,start,manager,ms,(char*)0);_exit(99);}
 if(c<0||waitpid(c,&status,0)!=c||!WIFEXITED(status)){return 99;}return WEXITSTATUS(status);
}
int main(void){pid_t p;struct api a;uint32_t first,second,id=29;if(setenv("XSAL_INSTANCE_NAME","delphi_graceful_fixture",1)) { return 1; }
if(stall_capture_test()){return 40;}p=fork();if(!p){execl("/proc/boot/procman","procman","-f","/proc/boot/manager.cfg","-c","0","-t","-v","7",(char*)0);_exit(99);}if(p<0) { return 2; }
pause_ms(2000);{char b[256]={0};int f=open("/proc/boot/manager.cfg",O_RDONLY);if(f>=0){ssize_t n=read(f,b,sizeof(b)-1);if(n>0)printf("FIXTURE_CONFIG bytes=%d text=[%s]\n",(int)n,b);close(f);}}
 if(resolve(&a)||initialize(&a,2)){puts("SAL_CLIENT_INIT_FAILED");return 3;}puts("SAL_CLIENT_INIT_PASS app=2");fflush(stdout);first=wait_target();if(!first){registry(p);printf("SAL_INITIAL_TARGET_ABSENT explicit_start_rc=%d\n",a.send(1,0,0x161,&id,4));fflush(stdout);first=wait_target();if(!first){registry(p);return 4;}}
 if(a.send(29,0,0x163,0,0)!=1||wait_gone(first)){return 5;}
 pause_ms(1200);if(target()) { return 6; }
puts("SAL_CLEAN_EXIT_NO_AUTORESTART_PASS");
 if(a.send(1,0,0x161,&id,4)!=1){return 7;}
 second=wait_target();if(!second||first==second) { return 8; }
puts("SAL_EXPLICIT_START_PASS");
 if(a.send(29,0,0x163,0,0)!=1||wait_gone(second)){return 9;}
 if(a.send(1,0,0x161,&id,4)!=1) { return 30; }
first=wait_target();if(!first) { return 31; }
{pg_identity n,pm;int f=pg_open(first,0,&n),m=pg_open(p,0,&pm);if(f<0||m<0) { return 32; }
close(f);close(m);if(page_tests(n,pm)){return 37;}if(cycle_helper(n,pm,1)!=3||target()!=first) { return 33; }
puts("NAV_CONTROL_IDENTITY_REFUSAL_PASS");if(cycle_helper(n,pm,0)!=0) { return 34; }
second=wait_target();if(!second||second==first) { return 35; }
puts("NAV_CONTROL_GUARDED_CYCLE_PASS");
 {pg_identity q,manager;int x=pg_open(second,0,&q),y=pg_open(p,0,&manager);if(x<0||y<0){return 41;}close(x);close(y);
  if(recover_helper(q,manager,"recover",0)!=3||target()!=second){return 42;}
  puts("NAV_RECOVER_HEALTHY_REFUSAL_PASS");
  if(recover_helper(q,manager,"recover-fixture",1)!=3||target()!=second){return 43;}
  puts("NAV_RECOVER_STALE_REFUSAL_PASS");
  unlink("/dev/shmem/sal-target-ready.bin");
  if(recover_helper(q,manager,"recover-fixture",0)){return 44;}
  first=wait_target();if(!first||first==second){return 45;}second=first;
  puts("NAV_RECOVER_FACTORY_AUTORESTART_PASS");
 }
 if(a.send(29,0,0x163,0,0)!=1||wait_gone(second)) { return 36; }
}a.deinit();puts("SAL_CLIENT_DEINIT_PASS");puts("SAL_GRACEFUL_CONTROL_QNX_PASS");fflush(stdout);return 0;}
