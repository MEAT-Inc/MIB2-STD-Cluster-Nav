#define _QNX_SOURCE 1
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
int main(void){pid_t p;void *h;void (*get)(void*),(*deinit)(void);int (*init)(void*),(*id)(void);uint32_t config[5]={0};struct timespec wait={2,0};
 if(setenv("XSAL_INSTANCE_NAME","delphi_graceful_fixture",1))return 1;
 p=fork();if(!p){execl("/proc/boot/procman","procman","-f","/proc/boot/manager.cfg","-c","0","-t",(char*)0);_exit(99);}if(p<0)return 2;
 nanosleep(&wait,0);h=dlopen("/proc/boot/libXSAL.so",RTLD_NOW);if(!h){printf("SAL_LIBRARY_REFUSED %s\n",dlerror());return 3;}
 get=dlsym(h,"SAL_Get_Config");init=dlsym(h,"SAL_Init");deinit=dlsym(h,"SAL_Deinit");id=dlsym(h,"SAL_Get_App_Id");if(!get||!init||!deinit||!id)return 4;
 get(config);if(config[0]||config[1]||config[2]!=64||config[3]!=32||config[4]!=0xffffffffu)return 5;
 ((unsigned char*)config)[0]=2;config[1]=1;printf("SAL_CLIENT_INIT_BEGIN app=2 threads=1\n");fflush(stdout);
 if(init(config)!=1){puts("SAL_CLIENT_INIT_FAILED");return 6;}if(id()!=2)return 7;puts("SAL_CLIENT_INIT_PASS app=2");fflush(stdout);
 deinit();puts("SAL_CLIENT_DEINIT_PASS");fflush(stdout);return 0;}
