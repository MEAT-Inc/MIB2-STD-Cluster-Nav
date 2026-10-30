#include "factory.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void *allocations[32];static unsigned attempt,fail_at,bad,mode;
static void put(void *p,unsigned o,uint32_t v){memcpy((char*)p+o,&v,4);}
static uint32_t get(void *p,unsigned o){uint32_t v;memcpy(&v,(char*)p+o,4);return v;}
static void *allocate(unsigned n){unsigned k;void *p;if(++attempt==fail_at)return 0;p=calloc(1,n);for(k=0;k<32;++k)if(!allocations[k]){allocations[k]=p;return p;}abort();}
static void deallocate(void *p){unsigned k;for(k=0;k<32;++k)if(allocations[k]==p){allocations[k]=0;free(p);return;}++bad;}
static void video_ctor(void *v,unsigned char id,void *router,unsigned char autofocus){memset(v,0,0x50);put(v,0,mode==1?1:0x80001000);put(v,8,(uintptr_t)router);put(v,12,id);((unsigned char*)v)[0x30]=autofocus;}
static void input_ctor(void *v,unsigned char id,void *router){memset(v,0,0x64);put(v,0,0x80002000);put(v,8,(uintptr_t)router);put(v,12,id);}
static void wrap(struct factory_shared *p,void *o){p->object=o;p->count=allocate(4);if(p->count)*p->count=1;}
static void attach(void *v,const struct factory_shared *p){put(v,0x34,(uintptr_t)p->count);put(v,0x38,(uintptr_t)p->object);if(mode!=2)++*p->count;}
static void release(struct factory_shared *p){if(!p->count)return;if(--*p->count==0){if(p->object){void (**vt)(void*)=*(void(***)(void*))p->object;vt[1](p->object);}deallocate(p->count);}}
static void video_delete(void *v){struct factory_shared p={(void*)get(v,0x34),(void*)get(v,0x38)};release(&p);if(get(v,0x40))deallocate((void*)get(v,0x40));deallocate(v);}
static void input_delete(void *v){deallocate(v);}
static int add_config(void *v,int a,int b,int c,int d,int e,int f,int g){if(a!=1||b!=2||c||d||e!=160||f||g!=10000){++bad;return -1;}put(v,0x40,(uintptr_t)allocate(4));if(!get(v,0x40))return -1;put(v,0x4c,1);return 1;}
static unsigned count(void *v){return get(v,0x4c);}
static unsigned outstanding(void){unsigned n=0,k;for(k=0;k<32;++k)n+=allocations[k]!=0;return n;}
int main(void){
 struct factory_api a={allocate,deallocate,video_ctor,input_ctor,wrap,attach,release,video_delete,input_delete,add_config,count,0x80001000,0x80002000};
 struct factory_result r;unsigned char router[0x500],before[sizeof(router)];unsigned test,k;int result;
 memset(router,0x55,sizeof(router));memcpy(before,router,sizeof(router));
 for(test=0;test<8;++test){attempt=0;mode=0;fail_at=0;if(test>=2&&test<=5)fail_at=test-1;if(test==6)mode=1;if(test==7)mode=2;
  result=factory_run(&a,router,&r);
  if(memcmp(router,before,sizeof(router))||bad)return 1;
  if(test<2){if(result||r.error||r.callback_destroyed!=1||r.unexpected_callback||r.quarantined||!r.input_destroyed||!r.video_destroyed||!r.temp_released||r.configurations!=1||outstanding())return 2;}
  else {if(result!=-1||!r.error)return 3;if(test<=4&&outstanding())return 4;if(test>=5&&!r.quarantined)return 5;}
  /* Test-owned quarantine allocations only; production intentionally does not
   * guess at destructors after a bad native ABI/refcount observation. */
  for(k=0;k<32;++k)if(allocations[k]){free(allocations[k]);allocations[k]=0;}
 }
 if(factory_run(0,router,&r)!=-1||r.error!=1)return 6;
 puts("ENDPOINT_FACTORY_QNX_OWNERSHIP_FAILURE_PASS cases=9");return 0;
}
