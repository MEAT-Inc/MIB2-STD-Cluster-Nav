#define _QNX_SOURCE 1
#include "sal-fixture-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <errno.h>
static void pause_ms(unsigned ms){struct timespec t={ms/1000,(ms%1000)*1000000};nanosleep(&t,0);}
static uint32_t target(void){uint32_t p=0;int f=open("/dev/shmem/sal-target-ready.bin",O_RDONLY);if(f>=0){if(read(f,&p,4)!=4)p=0;close(f);}return p;}
static uint32_t wait_target(void){unsigned i;uint32_t p;for(i=0;i<3000;i++){p=target();if(p)return p;pause_ms(1);}return 0;}
static int wait_gone(uint32_t p){unsigned i;char path[64];snprintf(path,sizeof(path),"/proc/%u/as",p);for(i=0;i<3000;i++){int f=open(path,O_RDONLY);if(f<0&&errno==ENOENT&&!target())return 0;if(f>=0)close(f);pause_ms(1);}return -1;}
int main(void){pid_t p;struct api a;uint32_t first,second,id=30;if(setenv("XSAL_INSTANCE_NAME","delphi_graceful_fixture",1))return 1;p=fork();if(!p){execl("/proc/boot/procman","procman","-f","/proc/boot/manager.cfg","-c","1","-t",(char*)0);_exit(99);}if(p<0)return 2;pause_ms(2000);
 if(resolve(&a)||initialize(&a,2)){puts("SAL_CLIENT_INIT_FAILED");return 3;}puts("SAL_CLIENT_INIT_PASS app=2");fflush(stdout);first=wait_target();if(!first)return 4;
 if(a.send(30,0,0x163,0,0)!=1||wait_gone(first)){return 5;}
 pause_ms(1200);if(target())return 6;puts("SAL_CLEAN_EXIT_NO_AUTORESTART_PASS");
 if(a.send(1,0,0x161,&id,4)!=1){return 7;}
 second=wait_target();if(!second||first==second)return 8;puts("SAL_EXPLICIT_START_PASS");
 if(a.send(30,0,0x163,0,0)!=1||wait_gone(second)){return 9;}
 a.deinit();puts("SAL_CLIENT_DEINIT_PASS");puts("SAL_GRACEFUL_CONTROL_QNX_PASS");fflush(stdout);return 0;}
