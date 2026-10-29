#define _QNX_SOURCE 1
#include "bench.h"
#include "observer.h"
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
extern uint32_t registration(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(OBS_SYMBOL);
extern unsigned smoke_native_calls(void);
int main(int argc,char **argv) {
 int fd;unsigned i;
 if(argc!=3 || strcmp(argv[0],"path_child") || strcmp(argv[1],"-t") || !setup_paths(argv[2]))return 12;
 fd=open(TX_REPORT,O_RDWR);
 struct tx_report *r;
 const struct obs_file *(*view)(void)=0;
 void *symbol=dlsym(RTLD_DEFAULT,"delphi_observer_view");
 if(fd<0)return 10;
 r=mmap(0,sizeof(*r),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(r==MAP_FAILED)return 11;
 if(r->magic!=PATH_MAGIC || r->version!=1 || r->bytes!=sizeof(*r) || r->app_runs>=6 || !regular_file(TX_COPY))return 12;
 if(sizeof(view)!=sizeof(symbol))return 13;
 memcpy(&view,&symbol,sizeof(view));
 for(i=0;i<9;++i) {
  uintptr_t a=0x1000+i,b=0x2000+i;uint32_t value;
  errno=ERANGE;
  value=registration(a,b,0x12345678u,0x87654321u,0x55aa55aau,0xaa55aa55u);
  if(value!=((uint32_t)(a^b)^0x80000001u) || errno!=EDOM)return 14;
 }
 if(smoke_native_calls()!=9)return 15;
 if(view) {
  const struct obs_header *h=&view()->header;
  if(h->status!=OBS_READY || !h->count || h->count+h->dropped!=9)return 16;
  r->observed_runs++;
 }
 {
  struct path_run *row=&r->runs[r->app_runs];
  row->sequence=r->app_runs+1;row->pid=getpid();row->ppid=getppid();
  row->observed=view!=0;row->records=view?view()->header.count:0;row->args_ok=1;
 }
 r->app_runs++;r->arguments_ok=1;r->last_pid=getpid();r->last_ppid=getppid();
 printf("PATH_APP observed=%u pid=%u ppid=%u argv=preserved\n",view!=0,r->last_pid,r->last_ppid);
 return 0;
}
