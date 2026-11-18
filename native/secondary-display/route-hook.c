#define _GNU_SOURCE 1
#define _QNX_SOURCE 1
#include "../cluster-bridge/live/queue.h"
#include "route-policy.h"
#include "../observer/launch/proc_guard.h"
#include "route-profile.h"
#include <dlfcn.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <pthread.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
static route_send stock;
static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
static struct route_policy policy;
static const volatile uint32_t *nav;
static const struct live_shared *queue;
static uint32_t fallback[128],*report=fallback,nonce[4];
static int enabled,navfd=-1;static pg_identity identity;
static uint64_t nowms(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (uint64_t)t.tv_sec*1000+t.tv_nsec/1000000;}
static const void *map(const char *name,size_t n,int create){struct stat st;void *p;int fd=open(name,create?O_RDWR|O_CREAT|O_EXCL:O_RDONLY,0600);if(fd<0)return 0;if((create&&ftruncate(fd,n))||fstat(fd,&st)||(uint64_t)st.st_size!=n){close(fd);return 0;}p=mmap(0,n,create?PROT_READ|PROT_WRITE:PROT_READ,MAP_SHARED,fd,0);close(fd);return p==MAP_FAILED?0:p;}
static void counts(void){report[7]=policy.held;report[8]=policy.released;report[9]=policy.cancelled;report[11]=policy.errors;report[14]=(uint32_t)policy.deadline;report[15]=policy.deadline>>32;}
static int healthy(void){unsigned i;uint32_t status;if(!enabled||policy.disabled||pg_matches(navfd,&identity))return 0;if(__atomic_load_n(&queue->magic,__ATOMIC_ACQUIRE)!=LIVE_MAGIC||queue->version!=1||queue->bytes!=sizeof(*queue)||queue->capacity!=LIVE_CAPACITY||queue->producer_pid!=(uint32_t)getpid()||queue->consumer_pid!=(uint32_t)identity.pid||queue->dropped||queue->closed)return 0;for(i=0;i<4;i++)if(queue->nonce[i]!=nonce[i])return 0;status=__atomic_load_n(&nav[4],__ATOMIC_ACQUIRE);return nav[0]==0x31504c52&&nav[1]==1&&nav[2]==512&&nav[3]==(uint32_t)identity.pid&&(status==1||status==2)&&!nav[5]&&nav[21]==1&&!nav[20]&&(nav[67]==2||nav[67]==3)&&nav[71]==(uint32_t)getpid()&&nav[72]==1&&!nav[73];}
static int poll_policy(uint64_t ms,uint64_t start){int stop=0;pthread_mutex_lock(&lock);report[12]++;report[17]=healthy();if(!ms||ms-start>215000||(policy.deadline&&(!healthy()||ms>=policy.deadline))){report[13]=!ms?4:ms-start>215000?3:ms>=policy.deadline?2:1;route_release(&policy,stock);counts();report[4]=3;stop=1;}pthread_mutex_unlock(&lock);return stop;}
static void *watch(void *arg){uint64_t start=nowms();(void)arg;for(;;){struct timespec t={0,100000000};nanosleep(&t,0);if(poll_policy(nowms(),start))break;}return 0;}
#ifdef ROUTE_HOOK_TEST
extern void *route_test_object(void);
extern void route_test_ack(void*);
static void *phone_instance(void){return route_test_object();}
static void phone_ack(void *p){route_test_ack(p);}
#else
static void *phone_instance(void){return ((void*(*)(void))0x1189e0)();}
static void phone_ack(void *p){((void(*)(void*,int))0x119840)(p,0);}
#endif
__attribute__((constructor)) static void route_init(void){const char *p=getenv("DELPHI_OBSERVER_LOG"),*prefix="/dev/shmem/delphi-observer-aa-";char token[33],path[160],hex[9];unsigned i,n=strlen(prefix);pthread_t worker;Dl_info info;stock=(route_send)dlsym(RTLD_NEXT,"SAL_Send");if(!p||strncmp(p,prefix,n)||strlen(p)!=n+36||strcmp(p+n+32,".bin")||strspn(p+n,"0123456789abcdef")!=32)return;memcpy(token,p+n,32);token[32]=0;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-nav-report-%s.bin",token);nav=map(path,512,0);if(!nav)return;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-route-policy-%s.bin",token);{void *m=(void*)map(path,512,1);if(!m)return;report=m;}report[0]=0x31545052;report[1]=2;report[2]=512;report[3]=getpid();report[4]=4;
 if(!stock||!dladdr((void*)stock,&info)||!info.dli_fbase||(uintptr_t)stock-(uintptr_t)info.dli_fbase!=0xc6e8||memcmp((void*)stock,route_sal_code,16)){report[5]=1;return;}for(i=0;i<sizeof(route_profile)/sizeof(route_profile[0]);i++)if(memcmp((void*)(uintptr_t)route_profile[i].address,route_profile[i].bytes,route_profile[i].size)){report[5]=2;return;}
 if(nav[0]!=0x31504c52||nav[1]!=1||nav[2]!=512||(nav[67]!=2&&nav[67]!=3)||!nav[3]){report[5]=3;return;}navfd=pg_open(nav[3],0,&identity);if(navfd<0||strcmp(identity.executable,"/extbin/apps/bin/NavigationServer")||identity.base_address!=0x100000){report[5]=4;return;}report[6]=identity.pid;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-live-%s.bin",token);queue=map(path,sizeof(*queue),0);if(!queue){report[5]=5;return;}for(i=0;i<4;i++){memcpy(hex,token+8*i,8);hex[8]=0;nonce[i]=strtoul(hex,0,16);}enabled=1;report[4]=1;if(pthread_create(&worker,0,watch,0)){enabled=0;report[4]=4;report[5]=6;}else pthread_detach(worker);}
__attribute__((visibility("default"))) int SAL_Send(unsigned app,unsigned thread,unsigned event,const void *bytes,unsigned n){int held=0,rc,saved=errno,good;uint32_t focus=0xffffffffu,decision=3;uint64_t ms;unsigned at;
 if(!stock){stock=(route_send)dlsym(RTLD_NEXT,"SAL_Send");if(!stock)_exit(125);}if(!enabled||event!=ROUTE_EVENT){errno=saved;return stock(app,thread,event,bytes,n);}if(n==12&&bytes)memcpy(&focus,(const char*)bytes+8,4);
 pthread_mutex_lock(&lock);report[16]++;ms=nowms();good=healthy();report[18]=focus;report[19]=app;report[20]=thread;report[22]=0xffffffffu;report[23]=(uint32_t)ms;report[24]=ms>>32;report[25]=nav[4];report[26]=nav[5];report[27]=queue->closed;report[28]=queue->dropped;report[29]=nav[72];report[30]=n;
 if(policy.deadline&&(!good||!ms||ms>=policy.deadline)){route_release(&policy,stock);report[4]=3;good=0;}
 if(n==12&&bytes&&focus==ROUTE_PROJECTED){decision=4;if(good&&ms){void *object=phone_instance();report[22]=object?*((unsigned char*)object+0xdc):0;decision=5;if(object&&report[22]){held=route_apply(&policy,1,ms,app,thread,event,bytes,n);decision=held?1:6;if(held){/* Same stock acknowledgement as DSI phone focus2. */phone_ack(object);report[10]++;report[4]=2;}}}}
 else if(n==12&&bytes&&focus==ROUTE_NATIVE){decision=2;route_apply(&policy,0,ms,app,thread,event,bytes,n);}
 /* Never forward a new projected request ahead of older deferred listeners. */
 if(focus==ROUTE_PROJECTED&&!held&&policy.held&&!policy.disabled){route_release(&policy,stock);report[4]=3;}
 if(policy.disabled&&focus==ROUTE_PROJECTED&&!held&&policy.deadline&&ms>=policy.deadline)decision=7;
 report[21]=decision;at=report[31];if(at<16){unsigned off=32+6*at;report[off]=(uint32_t)ms;report[off+1]=ms>>32;report[off+2]=focus;report[off+3]=app;report[off+4]=thread;report[off+5]=decision;report[31]=at+1;}
 counts();pthread_mutex_unlock(&lock);errno=saved;if(held)return 1;rc=stock(app,thread,event,bytes,n);return rc;}
