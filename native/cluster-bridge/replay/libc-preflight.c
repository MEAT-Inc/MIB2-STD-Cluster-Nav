#define _GNU_SOURCE 1
#define _QNX_SOURCE 1
#include "libc-profile.h"
#ifdef REPLAY_LOADER_TEST
#include "sdk-libc-profile.h"
#else
#include "unit-libc-profile.h"
#endif
#include <dlfcn.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
static int input;
static int rd(void *p,uint32_t a,void *b,unsigned n){unsigned done=0,tries=0;(void)p;if(n&&a>UINT32_MAX-(n-1))return -1;while(done<n&&tries++<128){unsigned want=n-done;ssize_t got;
#ifdef REPLAY_FORCE_PARTIAL_READ
 if(want>2)want=2;
#endif
 got=pread64(input,(unsigned char*)b+done,want,(off64_t)a+done);if(got<0&&errno==EINTR)continue;if(got<=0||(unsigned)got>want)return -1;done+=(unsigned)got;}return done==n?0:-1;}
int main(void){uint32_t f[3],base=0;char path[64],name[128]={0};unsigned i;int matched,known;Dl_info di;unsigned char code[32];const char *symbol[3]={"open","write","close"};void *libc_handle=dlopen("libc.so.3",RTLD_NOW);
 for(i=0;i<3;i++)f[i]=libc_handle?(uintptr_t)dlsym(libc_handle,symbol[i]):0;
 snprintf(path,sizeof(path),"/proc/%u/as",(unsigned)getpid());input=open(path,O_RDONLY);matched=input>=0&&!replay_libc_validate(&replay_expected_libc,f,rd,0,&base);known=dladdr((void*)(uintptr_t)f[1],&di);
 if(known&&di.dli_fname)for(i=0;i<sizeof(name)-1&&di.dli_fname[i];i++){unsigned char c=di.dli_fname[i];name[i]=c>=32&&c<127&&c!='"'&&c!='\\'?c:'_';}
 printf("{\"version\":1,\"profile_matches\":%s,\"base\":%u,\"functions\":[%u,%u,%u],\"dladdr_known\":%s,\"dladdr_name\":\"%s\",\"entry_code\":[",matched?"true":"false",base,f[0],f[1],f[2],known?"true":"false",name);
 for(i=0;i<3;i++){unsigned j;printf("%s\"",i?",":"");if(input>=0&&!rd(0,f[i],code,32))for(j=0;j<32;j++)printf("%02x",code[j]);printf("\"");}puts("]}");if(input>=0)close(input);return matched?0:1;}
