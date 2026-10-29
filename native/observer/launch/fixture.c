#define _QNX_SOURCE 1
#include "observer.h"
#include <errno.h>
#include <dlfcn.h>
#include <stdint.h>
#include <sys/mman.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
extern uint32_t registration(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(OBS_SYMBOL);
extern unsigned smoke_native_calls(void);

int main(int argc,char **argv){
 unsigned i;struct timespec tick={0,100000000};
 for(i=0;i<9;++i){errno=ERANGE;if(registration(0x1000+i,0x2000+i,0x12345678,0x87654321,0x55aa55aa,0xaa55aa55)!=0x80003001u||errno!=EDOM)return 9;}
 if(smoke_native_calls()!=9)return 10;
 printf("LAUNCH_FIXTURE pid=%u parent=%u argc=%d argv0=%s\n",(unsigned)getpid(),(unsigned)getppid(),argc,argv[0]);fflush(stdout);
 for(i=0;i<700;++i)nanosleep(&tick,0);
 return 8;
}
