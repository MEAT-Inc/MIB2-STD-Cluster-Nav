#ifndef SAL_FIXTURE_API_H
#define SAL_FIXTURE_API_H
#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct thread_attr {const char *name;int32_t id,priority;uint32_t stack;};
struct api {void *handle;void (*get)(void*),(*deinit)(void),(*thread_attr)(void*);int (*init)(void*),(*send)(unsigned,int,unsigned,const void*,unsigned),(*create)(void(*)(void*),void*,const void*),(*queue)(unsigned,unsigned,void*,void*),(*subscribe)(unsigned,int),(*wait_destroyed)(const unsigned*,unsigned);const uint32_t *(*receive)(void);};
static int resolve(struct api *a){memset(a,0,sizeof(*a));a->handle=dlopen("/proc/boot/libXSAL.so",RTLD_NOW);if(!a->handle)return -1;
#define GET(field,name) a->field=dlsym(a->handle,name);if(!a->field){fprintf(stderr,"SAL_FIXTURE_MISSING %s\n",name);return -1;}
 GET(get,"SAL_Get_Config");GET(init,"SAL_Init");GET(deinit,"SAL_Deinit");GET(send,"SAL_Send");GET(thread_attr,"SAL_Init_Thread_Attr");GET(create,"SAL_Create_Thread");GET(queue,"SAL_Create_Queue");GET(subscribe,"SAL_Subscribe");GET(receive,"SAL_Receive");GET(wait_destroyed,"SAL_Wait_Destroyed");
#undef GET
 return 0;}
static int initialize(struct api *a,unsigned id){uint32_t c[5]={0};a->get(c);if(c[0]||c[1]||c[2]!=64||c[3]!=32||c[4]!=0xffffffffu)return -1;((unsigned char*)c)[0]=(unsigned char)id;c[1]=1;return a->init(c)==1?0:-1;}
#endif
