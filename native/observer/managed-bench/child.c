#define _QNX_SOURCE 1
#include "bench.h"
#include "observer.h"
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
extern uint32_t registration(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(OBS_SYMBOL);
extern unsigned smoke_native_calls(void);
int main(int argc,char **argv) {
 int fd=open(REPORT,O_RDWR);struct report *r;unsigned count;
 if(fd<0)return 80;
 r=mmap(0,sizeof(*r),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);
 if(r==MAP_FAILED)return 81;
 count=r->count+1;r->pid=getpid();r->ppid=getppid();r->extra_code=argc>2?atoi(argv[2]+2):-1;
 {
  unsigned i;const struct obs_file *(*view)(void)=0;
  void *symbol=dlsym(RTLD_DEFAULT,"delphi_observer_view");
  if(sizeof(view)!=sizeof(symbol))return 84;
  memcpy(&view,&symbol,sizeof(view));
  for(i=0;i<9;++i) {
   uint32_t result;errno=ERANGE;
   result=registration(0x1000u+i,0x2000u+i,0x12345678u,0x87654321u,0x55aa55aau,0xaa55aa55u);
   if(result!=0x80003001u || errno!=EDOM)return 85;
  }
  if(smoke_native_calls()!=9)return 86;
  r->last_observed=view!=0;r->records=0;
  if(view) {
   const struct obs_header *h=&view()->header;
   if(h->status!=OBS_READY || h->count==0 || h->count+h->dropped!=9 || h->pid!=(unsigned)getpid())return 87;
   r->observed++;r->records=h->count;
  }
 }
 printf("MANAGED_OBSERVER observed=%u records=%u\n",r->last_observed,r->records);
 printf("MANAGED_CHILD count=%u pid=%u ppid=%u argc=%d arg0=%s arg1=%s extra=%s\n",count,r->pid,r->ppid,argc,argv[0],argc>1?argv[1]:"",argc>2?argv[2]:"");
 fflush(stdout);r->count=count;
 if(argc<2 || argv[1][0]!='-' || argv[1][1]!='t')return 82;
 if(count==2 || count==3) { unsigned i;struct timespec tick={0,100000000};
  for(i=0;i<100;++i)nanosleep(&tick,0);
  return 83; /* Runner must interrupt this owned synthetic app before timeout. */
 }
 return count==1?7:0;
}
