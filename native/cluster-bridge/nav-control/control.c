/* Orderly Nav cycle only. No signal, namespace alias, preload, or video writer. */
#define _QNX_SOURCE 1
#define _LARGEFILE64_SOURCE 1
#define _FILE_OFFSET_BITS 64
#include "proc_guard.h"
#include <sys/stat.h>
#include <fcntl.h>
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>
#include "sal-profile.h"
#include "stall-guard.h"
#include <sys/procfs.h>
#include <sys/states.h>
#include <devctl.h>
#ifdef NAV_CONTROL_TEST
#define NAV_PATH "/proc/boot/idle_fixture"
#else
#define NAV_PATH "/extbin/apps/bin/NavigationServer"
#endif
#define PM_PATH "/proc/boot/procman"
struct record {uint32_t address,pid,status,state;};
struct api {void *handle;void (*get)(void*),(*deinit)(void);int (*init)(void*),(*send)(unsigned,int,unsigned,const void*,unsigned),(*resolve)(unsigned,unsigned,uint32_t*);};
static int read_at(int f,uint32_t a,void *p,size_t n){unsigned i=0;size_t at=0;if(n>512||(n&&a>UINT32_MAX-(n-1))) { return -1; }
while(at<n&&i++<64){ssize_t got=pread64(f,(char*)p+at,n-at,(off64_t)a+at);if(got<0&&errno==EINTR)continue;if(got<=0) { return -1; }
at+=got;}return at==n?0:-1;}
static int elf(int f){unsigned char b[20];return !read_at(f,0x100000,b,20)&&!memcmp(b,"\177ELF\1\1\1",7)&&b[16]==2&&!b[17]&&b[18]==40&&!b[19];}
static int nav_profile(int f){
#ifndef NAV_CONTROL_TEST
 const uint32_t a[3]={0x1ee75c,0x22cdb4,0x1ee308};const unsigned char expected[3][4]={{0x39,0xd4,0xfc,0xeb},{0xb4,0xd8,0xfb,0xeb},{0xe1,0xd5,0xfc,0xeb}};unsigned i;unsigned char b[4];for(i=0;i<3;i++)if(read_at(f,a[i],b,4)||memcmp(b,expected[i],4)) { return 0; }

#endif
 return elf(f);}
static int pm_profile(int f){unsigned i;unsigned char b[16];if(!elf(f)) { return 0; }
for(i=0;i<3;i++)if(read_at(f,pm_addresses[i],b,16)||memcmp(b,pm_code[i],16)) { return 0; }
return 1;}
static int record(int f,struct record *r){uint32_t n,a,w[16];unsigned i,found=0;char name[sizeof("navigationserver")];if(read_at(f,0x12ff7c,&n,4)||n>108) { return -1; }
for(i=0;i<n;i++){if(read_at(f,0x12ff80+4*i,&a,4)||!a||(a&3)||read_at(f,a,w,sizeof(w))) { return -1; }
if(w[4]!=29){continue;}if(++found!=1||read_at(f,w[0],name,sizeof(name))||memcmp(name,"navigationserver",sizeof(name))) { return -1; }
r->address=a;r->pid=w[8];r->status=w[13];r->state=w[14];}return found==1?0:-1;}
static int bind_api(struct api *a){unsigned i;int f;uint32_t base;uintptr_t fn[5];unsigned char code[16],h[20];char self[64];memset(a,0,sizeof(*a));if(getenv("LD_PRELOAD")&&*getenv("LD_PRELOAD")) { return -1; }
a->handle=dlopen("/proc/boot/libXSAL.so",RTLD_NOW);if(!a->handle) { return -1; }
a->get=dlsym(a->handle,"SAL_Get_Config");a->init=dlsym(a->handle,"SAL_Init");a->deinit=dlsym(a->handle,"SAL_Deinit");a->send=dlsym(a->handle,"SAL_Send");a->resolve=dlsym(a->handle,"SAL_NS_Resolve_Channel");fn[0]=(uintptr_t)a->get;fn[1]=(uintptr_t)a->init;fn[2]=(uintptr_t)a->deinit;fn[3]=(uintptr_t)a->send;fn[4]=(uintptr_t)a->resolve;if(!fn[1]||fn[1]<sal_offsets[1]) { return -1; }
base=fn[1]-sal_offsets[1];if(base&4095) { return -1; }
snprintf(self,sizeof(self),"/proc/%u/as",(unsigned)getpid());f=open(self,O_RDONLY);if(f<0) { return -1; }
if(read_at(f,base,h,20)||memcmp(h,"\177ELF\1\1\1",7)||h[16]!=3||h[17]||h[18]!=40||h[19]){close(f);return -1;}for(i=0;i<5;i++)if(fn[i]!=base+sal_offsets[i]||read_at(f,fn[i],code,16)||memcmp(code,sal_code[i],16)){close(f);return -1;}close(f);return 0;}
static int start_api(struct api *a){uint32_t c[5]={0};if(bind_api(a)) { return -1; }
a->get(c);if(c[0]||c[1]||c[2]!=64||c[3]!=32||c[4]!=0xffffffffu) { return -1; }
((unsigned char*)c)[0]=2;c[1]=1;return a->init(c)==1?0:-1;}
static int route(struct api *a,unsigned app,pid_t pid){uint32_t v[2]={0};int ok=a->resolve(app,0,v)==1&&v[0]==(uint32_t)pid&&v[1]>0&&v[1]<0x10000;if(!ok)fprintf(stderr,"NAV_ROUTE_MISMATCH app=%u expected=%u observed=%u,%u\n",app,(unsigned)pid,v[0],v[1]);return ok;}
static void pause_ms(void){struct timespec t={0,10000000};nanosleep(&t,0);}
static uint64_t now(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t)) { return 0; }
return (uint64_t)t.tv_sec*1000+t.tv_nsec/1000000;}
static int gone(pid_t p){char b[64];int f;snprintf(b,sizeof(b),"/proc/%u/as",(unsigned)p);f=open(b,O_RDONLY);if(f>=0){close(f);return 0;}return errno==ENOENT||errno==ESRCH;}
static uint64_t number(const char *s){char *e;unsigned long long v;if(!s||!*s||strspn(s,"0123456789")!=strlen(s)) { return 0; }
errno=0;v=strtoull(s,&e,10);return errno||*e?0:v;}
static int crash_guard(int f,pid_t pid){
 procfs_status z;uint32_t words[STALL_EXT_WORDS],mutex[2],confirm[2],tid;size_t at=0;
 if(read_at(f,0x1076ee8,mutex,sizeof(mutex))){return 0;}
 tid=mutex[1]&0xffffu;
 if((tid!=2&&tid!=3)||mutex[0]!=0x80000000u||(mutex[1]&0x7fff0000u)!=(((uint32_t)pid&0x7fffu)<<16)){fprintf(stderr,"NAV_RECOVER_OWNER_REFUSED owner=%x\n",mutex[1]);return 0;}
 memset(&z,0,sizeof(z));z.tid=tid;
 if(devctl(f,DCMD_PROC_TIDSTATUS,&z,sizeof(z),0)||(uint32_t)z.tid!=tid||z.state!=STATE_MUTEX||
    (z.ip!=0x1038714u&&z.ip!=0x1038710u)||z.sp>0xbffff000u||z.blocked.sync.sync!=0x1076ee8u){fprintf(stderr,"NAV_RECOVER_WAIT_REFUSED state=%u ip=%llx sp=%llx mutex=%lx\n",z.state,(unsigned long long)z.ip,(unsigned long long)z.sp,(unsigned long)z.blocked.sync.sync);return 0;}
 while(at<sizeof(words)){
  size_t n=sizeof(words)-at;if(n>512){n=512;}
  if(read_at(f,(uint32_t)z.sp+at,(char*)words+at,n)){return 0;}at+=n;
 }
 if(read_at(f,0x1076ee8,confirm,sizeof(confirm))||memcmp(mutex,confirm,sizeof(mutex))){return 0;}
 {int match=stall_blob_tid(words,mutex,(uint32_t)z.sp,(uint32_t)pid,tid);fprintf(stderr,"NAV_RECOVER_CRASH_SIGNATURE match=%d tid=%u state=%u ip=%llx sp=%llx owner=%x signal=%u fault_pc=%x map_delete_return=%x\n",match,tid,z.state,(unsigned long long)z.ip,(unsigned long long)z.sp,mutex[1],words[tid==3?71:55],words[tid==3?75:59],words[tid==3?208:192]);return match;}
}
/* Read-only snapshot of the captured unit's MOST video state. */
static int most_status(const char *arg){
 uint64_t requested=number(arg);pg_identity most,pm;int f=-1,mf=-1,rc=3;
 uint32_t allowed,txstate,tid,tid_after;unsigned char config,bytes[16];procfs_status z;
 const uint32_t addresses[3]={0x1bcd60,0x1a72f8,0x1bdeb4};
 const unsigned char expected[3][16]={
  {0xb4,0x39,0x0e,0xe3,0x24,0x30,0x40,0xe3,0x00,0x30,0x93,0xe5,0x00,0x00,0x53,0xe3},
  {0x14,0x39,0x0e,0xe3,0x24,0x30,0x40,0xe3,0x00,0x30,0xd3,0xe5,0x00,0x00,0x53,0xe3},
  {0xc0,0x39,0x0e,0xe3,0x24,0x30,0x40,0xe3,0x00,0x30,0x93,0xe5,0x03,0x00,0xa0,0xe1}};
 unsigned i;
 if(!requested||requested>0x7fffffff) return 2;
 f=pg_open(requested,0,&most);
 if(f<0||strcmp(most.executable,"/extbin/apps/bin/Most")||most.base_address!=0x100000||!elf(f)) goto out;
 mf=pg_open(most.parent,0,&pm);
 if(mf<0||strcmp(pm.executable,PM_PATH)||!pm_profile(mf)) goto out;
 for(i=0;i<3;i++) if(read_at(f,addresses[i],bytes,16)||memcmp(bytes,expected[i],16)) goto out;
 if(read_at(f,0x24e9b4,&allowed,4)||read_at(f,0x24e914,&config,1)||
    read_at(f,0x24e9c0,&txstate,4)||read_at(f,0x247ea4,&tid,4)||!tid||tid>0x7fffffff) goto out;
 memset(&z,0,sizeof(z));z.tid=tid;
 if(devctl(f,DCMD_PROC_TIDSTATUS,&z,sizeof(z),0)||(uint32_t)z.tid!=tid||
    read_at(f,0x247ea4,&tid_after,4)||tid_after!=tid||pg_matches(f,&most)||pg_matches(mf,&pm)) goto out;
 printf("{\"version\":1,\"readonly\":true,\"pid\":%u,\"start_time\":%llu,\"manager_pid\":%u,\"manager_start\":%llu,\"tx_allowed\":%u,\"config_ok\":%u,\"tx_state\":%u,\"video_tid\":%u,\"thread_state\":%u,\"thread_ip\":%llu,\"thread_sp\":%llu}\n",(unsigned)most.pid,(unsigned long long)most.start_time,(unsigned)pm.pid,(unsigned long long)pm.start_time,allowed,(unsigned)config,txstate,tid,(unsigned)z.state,(unsigned long long)z.ip,(unsigned long long)z.sp);
 rc=0;
 out:if(f>=0)close(f);if(mf>=0)close(mf);if(rc)fprintf(stderr,"MOST_STATUS_REFUSED errno=%d\n",errno);return rc;
}
int main(int argc,char **argv){uint64_t requested,ns,ms,end;pg_identity nav,pm,newnav;struct record before={0},after={0};struct api a;uint32_t app=29;int nf=-1,mf=-1,nf2=-1,active=0,code=3,recovery=0,fixture_recovery=0,sent_signal=0;const char *stage="identity";sigset_t unblocked;struct sigaction sa;memset(&a,0,sizeof(a));memset(&newnav,0,sizeof(newnav));
 if(argc==3&&!strcmp(argv[1],"most-status")) return most_status(argv[2]);
 recovery=argc==6&&!strcmp(argv[1],"recover");
#ifdef NAV_CONTROL_TEST
 fixture_recovery=argc==6&&!strcmp(argv[1],"recover-fixture");recovery|=fixture_recovery;
#endif
 if(argc==1){puts("Plan only: inspect <NavPID>; cycle <NavPID> <NavStart> <ManagerPID> <ManagerStart>");return 0;}
 if((argc!=3||strcmp(argv[1],"inspect"))&&(argc!=6||(strcmp(argv[1],"cycle")&&!recovery))&&(argc!=7||strcmp(argv[1],"page"))) { return 2; }

 requested=number(argv[2]);if(!requested||requested>0x7fffffff) { return 2; }
nf=pg_open(requested,0,&nav);if(nf<0||strcmp(nav.executable,NAV_PATH)||nav.base_address!=0x100000||!nav_profile(nf)) { goto done; }
mf=pg_open(nav.parent,0,&pm);if(mf<0||strcmp(pm.executable,PM_PATH)||!pm_profile(mf)||record(mf,&before)||before.pid!=(uint32_t)nav.pid||before.state!=3||pg_matches(nf,&nav)||pg_matches(mf,&pm)) { goto done; }

 if(argc==3){printf("{\"version\":1,\"readonly\":true,\"pid\":%u,\"start_time\":%llu,\"manager_pid\":%u,\"manager_start\":%llu,\"app_id\":29,\"state\":%u}\n",(unsigned)nav.pid,(unsigned long long)nav.start_time,(unsigned)pm.pid,(unsigned long long)pm.start_time,before.state);code=0;goto done;}
 ns=number(argv[3]);ms=number(argv[5]);if(!ns||!ms||nav.start_time!=ns||pm.start_time!=ms||number(argv[4])!=(uint64_t)pm.pid) { goto done; }

 if(argc==7){
  unsigned char page[4096];uint64_t address=number(argv[6]);size_t at=0;
  stage="read_page";
  if(address<4096||address>0xbffff000u||(address&4095)){goto done;}
  while(at<sizeof(page)){
   if(read_at(nf,(uint32_t)address+at,page+at,512)){goto done;}
   at+=512;
  }
  if(pg_matches(nf,&nav)||pg_matches(mf,&pm)){goto done;}
  at=0;
  while(at<sizeof(page)){
   ssize_t n=write(STDOUT_FILENO,page+at,sizeof(page)-at);
   if(n<0&&errno==EINTR){continue;}
   if(n<=0){goto done;}
   at+=(size_t)n;
  }
  code=0;goto done;
 }
 memset(&sa,0,sizeof(sa));sa.sa_handler=SIG_DFL;sigemptyset(&sa.sa_mask);if(sigaction(SIGALRM,&sa,0)) { goto done; }
sigemptyset(&unblocked);sigaddset(&unblocked,SIGALRM);if(sigprocmask(SIG_UNBLOCK,&unblocked,0)) { goto done; }
alarm(60);
 if(recovery){
  uint32_t restart=0;
  stage="recover_guard";
  if(read_at(mf,before.address+0x2c,&restart,4)||restart!=1||
     (!fixture_recovery&&!crash_guard(nf,nav.pid))){goto done;}
  pause_ms();
  if(pg_matches(nf,&nav)||pg_matches(mf,&pm)||record(mf,&after)||
     after.address!=before.address||after.pid!=(uint32_t)nav.pid||after.state!=3||
     (!fixture_recovery&&!crash_guard(nf,nav.pid))){goto done;}
  /* Checked PID/start/parent and exact repeated crash signature. Recheck+kill
   * are separate calls, not an atomic procfs signal. Never retry another PID. */
  stage="recover_terminate";
  if(kill(nav.pid,SIGKILL)){goto done;}sent_signal=1;close(nf);nf=-1;
  stage="recover_restart";end=now()+25000;
  while(now()<end){
   if(pg_matches(mf,&pm)||record(mf,&after)||after.address!=before.address){goto done;}
   if(after.pid&&after.pid!=(uint32_t)nav.pid&&after.state==3){
    nf2=pg_open(after.pid,0,&newnav);
    if(nf2>=0){
     if(newnav.parent==pm.pid&&newnav.start_time!=nav.start_time&&
        !strcmp(newnav.executable,NAV_PATH)&&nav_profile(nf2)&&!pg_matches(nf2,&newnav)&&after.status==SIGKILL){code=0;break;}
     close(nf2);nf2=-1;
    }
   }
   pause_ms();
  }
  goto done;
 }
 stage="sal_profile";if(start_api(&a)) { goto done; }
active=1;stage="namespace";if(!route(&a,1,pm.pid)||!route(&a,29,nav.pid)||pg_matches(nf,&nav)||pg_matches(mf,&pm)) { goto done; }

 stage="stop_request";fprintf(stderr,"NAV_GRACEFUL_STOP_REQUEST pid=%u\n",(unsigned)nav.pid);if(a.send(29,0,0x163,0,0)!=1) { goto done; }
close(nf);nf=-1;
 stage="clean_exit";end=now()+25000;while(now()<end){if(pg_matches(mf,&pm)||record(mf,&after)||after.address!=before.address) { goto done; }
if(gone(nav.pid)&&after.state==0){if(after.status) { goto done; }
break;}pause_ms();}if(!gone(nav.pid)||after.state!=0||after.status) { goto done; }
fprintf(stderr,"NAV_GRACEFUL_CLEAN_EXIT pid=%u status=0\n",(unsigned)nav.pid);
 stage="start_request";if(pg_matches(mf,&pm)||record(mf,&after)||after.address!=before.address||after.state!=0||after.status||!route(&a,1,pm.pid)) { goto done; }
if(a.send(1,0,0x161,&app,4)!=1) { goto done; }
fprintf(stderr,"NAV_GRACEFUL_START_REQUEST app=29\n");
 stage="new_process";end=now()+25000;while(now()<end){if(pg_matches(mf,&pm)||record(mf,&after)||after.address!=before.address) { goto done; }
if(after.pid&&after.pid!=(uint32_t)nav.pid&&after.state==3){nf2=pg_open(after.pid,0,&newnav);if(nf2>=0){if(newnav.parent==pm.pid&&newnav.start_time!=nav.start_time&&!strcmp(newnav.executable,NAV_PATH)&&nav_profile(nf2)&&route(&a,29,newnav.pid)&&!pg_matches(nf2,&newnav)){code=0;break;}close(nf2);nf2=-1;}}pause_ms();}
 done:if(active){a.deinit();}alarm(0);if(argc==6)printf("{\"version\":1,\"process_cycle_verified\":%s,\"functional_maps_verified\":false,\"stage\":\"%s\",\"old_pid\":%u,\"new_pid\":%u,\"new_start\":%llu,\"last_exit_raw\":%u,\"signals_to_nav\":%s,\"termination_signal\":%d}\n",code?"false":"true",stage,(unsigned)requested,(unsigned)newnav.pid,(unsigned long long)newnav.start_time,after.status,sent_signal?"true":"false",sent_signal?SIGKILL:0);if(code)fprintf(stderr,"NAV_GRACEFUL_REFUSED_OR_PARTIAL stage=%s errno=%d\n",stage,errno);if(nf>=0){close(nf);}if(nf2>=0){close(nf2);}if(mf>=0){close(mf);}return code;}
