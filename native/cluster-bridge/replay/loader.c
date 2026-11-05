#define _GNU_SOURCE 1
#define _QNX_SOURCE 1
#include "replay.h"
#include "imports.h"
#include "libc-profile.h"
#ifdef REPLAY_LOADER_TEST
#include "sdk-libc-profile.h"
#else
#include "unit-libc-profile.h"
#endif
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
extern int delphi_replay_open(const char*,int,unsigned,uintptr_t);
extern ssize_t delphi_replay_write(int,const void*,size_t,uintptr_t);
extern int delphi_replay_close(int,uintptr_t);
static volatile uint32_t *arm_report;static int memfd=-1;static uint32_t fallback[128],diagnostic_slots[3];
static int exact(uint32_t a,void *p,unsigned n){unsigned done=0,tries=0;if(n&&a>UINT32_MAX-(n-1))return 0;while(done<n&&tries++<128){unsigned want=n-done;ssize_t got;
 got=pread64(memfd,(unsigned char*)p+done,want,(off64_t)a+done);if(got<0&&errno==EINTR)continue;if(got<=0||(unsigned)got>want)return 0;done+=(unsigned)got;}return done==n;}
static int profile_read(void *unused,uint32_t a,void *p,unsigned n){(void)unused;
#ifdef REPLAY_FORCE_PARTIAL_READ
 {unsigned done=0;while(done<n){unsigned take=n-done;if(take>2)take=2;if(!exact(a+done,(unsigned char*)p+done,take))return -1;done+=take;}return 0;}
#else
 return exact(a,p,n)?0:-1;
#endif
}
static int hooks_retained(void){uint32_t v;unsigned i;const uintptr_t wanted[3]={(uintptr_t)delphi_replay_open,(uintptr_t)delphi_replay_write,(uintptr_t)delphi_replay_close};for(i=0;i<3;i++)if(!diagnostic_slots[i]||!exact(diagnostic_slots[i],&v,4)||v!=wanted[i])return 0;return 1;}
static void inspect(void *unused,volatile uint32_t *r){uint32_t v,p=0,p2,b[19],sample[12]={0};unsigned i;(void)unused;if(!r)return;sample[4]=0xffffffffu;
 for(i=0;i<3;i++){if(!diagnostic_slots[i]||!exact(diagnostic_slots[i],&v,4)){sample[11]=1;continue;}sample[i]=v;}
#ifndef REPLAY_LOADER_TEST
 if(!exact(0x5aeab0,&p,4))sample[11]=2;
 else if(p){if((p&3)||p>0x7ffffed0u||!exact(p+0xe0,b,sizeof(b))||!exact(0x5aeab0,&p2,4)||p!=p2)sample[11]=3;
 else{sample[3]=p;sample[4]=b[18];for(i=0;i<5;i++)sample[5+i]=b[6+i];}}
#else
 (void)p;(void)p2;(void)b;
#endif
 for(i=0;i<10;i++){__atomic_store_n(&r[40+i],sample[i],__ATOMIC_RELAXED);}
 __atomic_store_n(&r[51],sample[11],__ATOMIC_RELEASE);
}
static int geometry(void *unused,int fd){uint32_t p,p2,b[19];(void)unused;if(!arm_report||__atomic_load_n(&arm_report[21],__ATOMIC_ACQUIRE)!=1||!hooks_retained())return 0;if(!exact(0x5aeab0,&p,4)||!p||(p&3)||p>0x7ffffed0u||!exact(p+0xe0,b,sizeof(b))||!exact(0x5aeab0,&p2,4)||p!=p2)return 0;return b[6]==800&&b[7]==480&&b[8]==800&&b[9]==480&&b[10]==0&&(int)b[18]==fd;}
static int slots(uint32_t out[3]){unsigned char h[52];uint32_t ph[8],tag[2],rel[2],sym[4],dynamic=0,dynsize=0,strings=0,symbols=0,jmp=0,bytes=0,rwlo=0,rwhi=0;unsigned i,j,found=0;uint16_t pe,pn;uint32_t po;char name[16];const char *wanted[3]={"open","write","close"};
 if(!exact(0x100000,h,sizeof(h))||memcmp(h,"\177ELF\1\1\1",7)||h[16]!=2||h[17]||h[18]!=40||h[19])return 0;
 memcpy(&po,h+28,4);memcpy(&pe,h+42,2);memcpy(&pn,h+44,2);if(pe!=32||pn>32||po>65536)return 0;
 for(i=0;i<pn;i++){if(!exact(0x100000+po+i*pe,ph,32))return 0;if(ph[0]==2){dynamic=ph[2];dynsize=ph[4];}if(ph[0]==1&&ph[6]==6){rwlo=ph[2];rwhi=ph[2]+ph[5];}}
 if(!dynamic||dynsize>4096||!rwlo||rwhi<=rwlo)return 0;
 for(i=0;i+8<=dynsize;i+=8){if(!exact(dynamic+i,tag,8))return 0;if(!tag[0])break;if(tag[0]==5)strings=tag[1];if(tag[0]==6)symbols=tag[1];if(tag[0]==23)jmp=tag[1];if(tag[0]==2)bytes=tag[1];}
 if(!strings||!symbols||!jmp||!bytes||bytes>65536||bytes%8)return 0;
 for(i=0;i<bytes;i+=8){if(!exact(jmp+i,rel,8)||rel[1]>>8>=65536)return 0;if((rel[1]&255)!=22)continue;if(!exact(symbols+(rel[1]>>8)*16,sym,16)||!exact(strings+sym[0],name,16))return 0;name[15]=0;for(j=0;j<3;j++)if(!strcmp(name,wanted[j])){if(found&(1u<<j)||rel[0]<rwlo||rel[0]>rwhi-4||(rel[0]&3))return 0;out[j]=rel[0];found|=1u<<j;}}
 return found==7;
}
#ifdef REPLAY_LOADER_TEST
static int (*test_geometry)(void*,int);
static int armed_test_geometry(void *p,int fd){return arm_report&&arm_report[21]==1&&test_geometry&&test_geometry(p,fd);}
#endif
__attribute__((constructor)) static void load(void){
 struct replay_config c;struct replay_import hooks[3];const char *report=getenv("DELPHI_NAV_REPORT"),*prefix="/dev/shmem/delphi-nav-report-";char path[192];unsigned i,n=strlen(prefix);int fd=-1,raw=-1,logfd=-1,capturefd=-1,saved=errno,error=1001,started=0;struct stat st;unsigned char code[4],*bytes=0;size_t at=0;uint32_t *out=fallback,slot[3],v;ssize_t got;uint32_t functions[3],libc_base;void *libc_handle;
 memset(&c,0,sizeof(c));memset(hooks,0,sizeof(hooks));libc_handle=dlopen("libc.so.3",RTLD_NOW);c.native_open=libc_handle?dlsym(libc_handle,"open"):0;c.native_write=libc_handle?dlsym(libc_handle,"write"):0;c.native_close=libc_handle?dlsym(libc_handle,"close"):0;
 if(!c.native_open||!c.native_write||!c.native_close){return;}
 replay_bind_callbacks(c.native_open,c.native_write,c.native_close);
 if(!report||strncmp(report,prefix,n)||strlen(report)!=n+36||strcmp(report+n+32,".bin"))goto end;
 for(i=0;i<32;i++)if(!((report[n+i]>='0'&&report[n+i]<='9')||(report[n+i]>='a'&&report[n+i]<='f')))goto end;
 snprintf(path,sizeof(path),"/ramdisk/delphi-nav-bridge_%.*s/nav-startup.txt",32,report+n);logfd=c.native_open(path,O_CREAT|O_EXCL|O_WRONLY,0600);
 fd=c.native_open(report,O_CREAT|O_EXCL|O_RDWR,0600);if(fd<0||ftruncate(fd,512))goto end;
 {void *m=mmap(0,512,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);if(m==MAP_FAILED)goto end;out=m;arm_report=out;memset(out,0,512);}
 out[RP_MAGIC]=RPL_REPORT_MAGIC;out[RP_VERSION]=1;out[RP_SIZE]=512;out[RP_PID]=getpid();out[22]=1;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-nav-source-%.*s.bin",32,report+n);capturefd=c.native_open(path,O_CREAT|O_EXCL|O_RDWR,0600);if(capturefd>=0&&!ftruncate(capturefd,1024*1024)){void *m=mmap(0,1024*1024,PROT_READ|PROT_WRITE,MAP_SHARED,capturefd,0);if(m!=MAP_FAILED){c.capture=m;c.capture_capacity=1024*1024;}}
 functions[0]=(uintptr_t)c.native_open;functions[1]=(uintptr_t)c.native_write;functions[2]=(uintptr_t)c.native_close;for(i=0;i<3;i++)out[26+i]=functions[i];
 snprintf(path,sizeof(path),"/proc/%u/as",(unsigned)getpid());memfd=c.native_open(path,O_RDONLY);error=1002;
 if(memfd<0||replay_libc_validate(&replay_expected_libc,functions,profile_read,0,&libc_base))goto end;
 out[36]=libc_base;out[22]=2;error=1003;if(!slots(slot))goto end;
#ifndef REPLAY_LOADER_TEST
 {const uint32_t a[]={0x1ee75c,0x22cdb4,0x1ee308},expected[]={REPLAY_IMPORT_OPEN_SLOT,REPLAY_IMPORT_WRITE_SLOT,REPLAY_IMPORT_CLOSE_SLOT};const unsigned char code_expected[3][4]={{0x39,0xd4,0xfc,0xeb},{0xb4,0xd8,0xfb,0xeb},{0xe1,0xd5,0xfc,0xeb}};for(i=0;i<3;i++)if(slot[i]!=expected[i]||slot[i]<REPLAY_IMPORT_RW_BEGIN||slot[i]+4>REPLAY_IMPORT_RW_END||!exact(a[i],code,4)||memcmp(code,code_expected[i],4))goto end;}
 c.geometry=geometry;c.open_lr=0x1ee760;c.write_lr=0x22cdb8;c.close_lr=0x1ee30c;
#else
 (void)code;(void)geometry;test_geometry=dlsym(RTLD_DEFAULT,"test_geometry");c.geometry=armed_test_geometry;c.open_lr=(uintptr_t)dlsym(RTLD_DEFAULT,"test_open_return");c.write_lr=(uintptr_t)dlsym(RTLD_DEFAULT,"test_write_return");c.close_lr=(uintptr_t)dlsym(RTLD_DEFAULT,"test_close_return");
#endif
 for(i=0;i<3;i++){diagnostic_slots[i]=slot[i];}
 c.inspect=inspect;
 out[22]=3;snprintf(path,sizeof(path),"/ramdisk/delphi-nav-bridge_%.*s/replay.bin",32,report+n);error=1004;
 if(lstat(path,&st)||!S_ISREG(st.st_mode)||st.st_size<32||st.st_size>8*1024*1024)goto end;
 raw=c.native_open(path,O_RDONLY);if(raw<0||fstat(raw,&st))goto end;bytes=malloc(st.st_size);if(!bytes)goto end;
 while(at<(size_t)st.st_size){got=read(raw,bytes+at,st.st_size-at);if(got<0&&errno==EINTR)continue;if(got<=0)goto end;at+=got;}
 #ifndef REPLAY_LOADER_TEST
 c.timeline_required=1;
#endif
 out[22]=4;c.file_bytes=bytes;c.file_size=at;c.report=out;c.defer_ready=1;
 if(replay_init(&c)){error=1005;goto end;}started=1;out[22]=5;
 hooks[0].native=(uintptr_t)c.native_open;hooks[1].native=(uintptr_t)c.native_write;hooks[2].native=(uintptr_t)c.native_close;hooks[0].replacement=(uintptr_t)delphi_replay_open;hooks[1].replacement=(uintptr_t)delphi_replay_write;hooks[2].replacement=(uintptr_t)delphi_replay_close;
 for(i=0;i<3;i++){hooks[i].slot=(volatile uint32_t*)(uintptr_t)slot[i];out[26+i]=hooks[i].native;out[29+i]=hooks[i].replacement;out[32+i]=slot[i];if(!exact(slot[i],&v,4)){error=1006;goto end;}
#ifndef REPLAY_LOADER_TEST
 out[23+i]=v;hooks[i].lazy=REPLAY_IMPORT_LAZY;
#else
 out[23+i]=v;if(v==hooks[i].native)hooks[i].lazy=v;else{uint32_t instruction;if(v<0x100000||v>=slot[i]||!exact(v,&instruction,4)||instruction!=0xe52de004u){error=1006;goto end;}hooks[i].lazy=v;}
#endif
 }
 {int result=replay_imports_install(hooks,3);out[35]=(uint32_t)result;if(result){error=1007;goto end;}}out[22]=6;
 for(i=0;i<3;i++)if(*hooks[i].slot!=hooks[i].replacement){(void)replay_imports_restore(hooks,3);error=1008;goto end;}
 out[22]=7;if(replay_publish_ready()){(void)replay_imports_restore(hooks,3);error=1009;goto end;}error=0;
 end:if(capturefd>=0)c.native_close(capturefd);if(fd>=0)c.native_close(fd);if(raw>=0)c.native_close(raw);if(error){if(started)replay_stop();out[RP_MAGIC]=RPL_REPORT_MAGIC;out[RP_VERSION]=1;out[RP_SIZE]=512;out[RP_PID]=getpid();out[RP_STATUS]=RPL_ERROR;out[RP_ERROR]=error;}if(logfd>=0){int len=snprintf(path,sizeof(path),"REPLAY_INIT stage=%u error=%d app_imports=%u\n",out[22],error,error?0:3);if(len>0&&(unsigned)len<sizeof(path)){size_t done=0;unsigned tries=0;while(done<(size_t)len&&tries++<32){ssize_t w=c.native_write(logfd,path+done,len-done);if(w<0&&errno==EINTR)continue;if(w<=0)break;done+=w;}}c.native_close(logfd);}errno=saved;
}
