#define main factory_fixture_original_main
#include "../endpoint-factory/fixture.c"
#undef main
#include "runtime.h"
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
static unsigned char stock[]={0,6,10,8,8,1,26,4,8,3,32,0,10,4,8,2,34,0,10,6,8,5,26,2,8,1};
static unsigned char video[]={10,8,8,9,26,4,8,3,32,0},input[]={10,4,8,10,34,0};
struct response {unsigned char data[256];unsigned n;};
struct outbuffer {unsigned char *data;unsigned capacity,start,end;};
static unsigned char sent[16384];static unsigned sent_n;static struct response response;
static int native_pop_fixture(void *router,void *p){struct response *r=p;(void)router;if(errno!=ERANGE)++bad;memcpy(r->data,stock,sizeof(stock));r->n=sizeof(stock);errno=EDOM;return 0x123456;}
static int native_queue_fixture(void *router,unsigned char channel,void *p,unsigned n){(void)router;if(channel||n>sizeof(sent)||errno!=ERANGE)++bad;memcpy(sent,p,n);sent_n=n;errno=EDOM;return 0x234567;}
static int marshal_fixture(void *router,unsigned short id,const void *p,void *out){const struct response *r=p;struct outbuffer *b=out;(void)router;if(id!=6)++bad;b->data=malloc(r->n);memcpy(b->data,r->data,r->n);b->capacity=b->end=r->n;b->start=0;return 7;}
static void video_discovery(void *v,void *p){struct response *r=p;(void)v;memcpy(r->data+r->n,video,sizeof(video));r->n+=sizeof(video);}
static void input_discovery(void *v,void *p){struct response *r=p;(void)v;memcpy(r->data+r->n,input,sizeof(input));r->n+=sizeof(input);}
static int reg_fixture(void *router,void *endpoint){unsigned id=get(endpoint,12);uint32_t *p=(uint32_t*)((char*)router+0x100+id*4);if(*p)return 0;*p=(uintptr_t)endpoint;return 1;}
static void fake_focus(void *v,int m,unsigned char u){(void)v;(void)m;(void)u;}
static void fake_ack(void *v,int session,unsigned n){(void)v;(void)session;(void)n;}
int factory_profile_api(struct factory_api *a,uintptr_t *r,uintptr_t *p,uintptr_t *b){(void)a;(void)r;(void)p;(void)b;return 0;}
int pop_export(void*,void*) __asm__("_ZN13MessageRouter32populateServiceDiscoveryResponseEP24ServiceDiscoveryResponse");
int queue_export(void*,unsigned char,void*,unsigned) __asm__("_ZN13MessageRouter13queueOutgoingEhPvj");
int main(void){
 struct secondary_test_hooks hooks={native_pop_fixture,native_queue_fixture,marshal_fixture,video_discovery,input_discovery};
 struct stream_native api={{allocate,deallocate,video_ctor,input_ctor,wrap,attach,release,video_delete,input_delete,add_config,count,media_start,media_stop,codec,data,focus,input_key,0x80001000,0x80002000},reg_fixture,fake_focus,fake_ack};
 unsigned char router[0x500],good[16384],original[256];struct stream_report r;unsigned k,scenario,good_n;int fd;
 for(scenario=0;scenario<2;++scenario){
  memset(router,0,sizeof(router));bad=mode=fail_at=attempt=0;
  fd=open("/dev/shmem/secondary-transaction-fixture.bin",O_CREAT|O_EXCL|O_WRONLY,0600);if(fd<0)return 1;
  secondary_test_bind(&hooks,&api,router,&r,fd);errno=ERANGE;
  if(pop_export(router,&response)!=0x123456||errno!=EDOM||r.w[SREGISTERED]!=2||!get(router,0x100+9*4)||!get(router,0x100+10*4))return 2;
  memcpy(original,response.data,response.n);errno=ERANGE;
  if(scenario==0){
   if(queue_export(router,0,response.data,response.n)!=0x234567||errno!=EDOM||r.w[SREWRITES]!=1||sent_n<=response.n||memcmp(original,response.data,response.n)||bad)return 3;
   good_n=sent_n;memcpy(good,sent,good_n);
   response.data[2]=0;errno=ERANGE;
   if(queue_export(router,0,response.data,response.n)!=0x234567||errno!=EDOM||r.w[SFALLBACK]!=1||sent_n!=good_n||memcmp(sent,good,good_n)||r.w[SREGISTERED]!=2)return 4;
  }else{
   response.data[2]=0;errno=ERANGE;
   if(queue_export(router,0,response.data,response.n)!=0x234567||errno!=EDOM||r.w[SFALLBACK]!=1||sent_n!=sizeof(stock)||memcmp(sent,stock,sizeof(stock))||r.w[SREGISTERED]||get(router,0x100+9*4)||get(router,0x100+10*4))return 5;
  }
  if(bad)return 6;
  close(fd);unlink("/dev/shmem/secondary-transaction-fixture.bin");
  for(k=0;k<32;++k)if(allocations[k]){free(allocations[k]);allocations[k]=0;}
 }
 puts("SECONDARY_DISCOVERY_TRANSACTION_QNX_PASS success=metadata_only fallback=stock_or_last_good original_bytes=preserved");return 0;
}
