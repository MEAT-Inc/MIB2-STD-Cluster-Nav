#include "factory.h"
#include <stddef.h>
#include <string.h>
_Static_assert(sizeof(void*)==4,"Delphi ARM32 ABI");
_Static_assert(sizeof(struct factory_shared)==8,"count pointer then object pointer");
struct callback_owner { const struct factory_api *api; struct factory_result *result; const unsigned char *payload; const struct factory_shared *buffer; };
struct callback { const void *vtable; struct callback_owner *owner; };
_Static_assert(sizeof(struct callback)==8,"independent callback adapter");
static uintptr_t word(const void *p,unsigned offset){uint32_t v;memcpy(&v,(const char*)p+offset,4);return v;}
static void complete(void *p){struct callback *c=p;++c->owner->result->callback_destroyed;}
static void deleting(void *p){struct callback *c=p;const struct factory_api *a=c->owner->api;complete(p);a->deallocate(p);}
static int unexpected(void *p,...){struct callback *c=p;++c->owner->result->unexpected_callback;return -1;}
/* Synchronous diagnostic callbacks: borrowed data is never retained. */
static int data_callback(void *p,int session,uint64_t ts,const struct factory_shared *buffer,const void *data,unsigned bytes){struct callback_owner *o=((struct callback*)p)->owner;++o->result->data_calls;o->result->data_bytes+=bytes;if(session!=37||ts!=0x123456789abcdef0ULL||buffer!=o->buffer||data!=o->payload+5||bytes!=10||memcmp(data,o->payload+5,10))++o->result->unexpected_callback;return 0;}
static int codec_callback(void *p,void *data,unsigned bytes){struct callback_owner *o=((struct callback*)p)->owner;++o->result->codec_calls;if(data!=o->payload||bytes!=8||memcmp(data,o->payload,8))++o->result->unexpected_callback;return 0;}
static int start_callback(void *p,int session){struct callback_owner *o=((struct callback*)p)->owner;++o->result->start_calls;if(session!=37)++o->result->unexpected_callback;return 0;}
static int stop_callback(void *p,int session){struct callback_owner *o=((struct callback*)p)->owner;++o->result->stop_calls;if(session!=37)++o->result->unexpected_callback;return 0;}
static int config_callback(void *p,int index){struct callback_owner *o=((struct callback*)p)->owner;++o->result->media_config_calls;if(index)++o->result->unexpected_callback;return 0;}
static int focus_callback(void *p,int mode,unsigned char unsolicited){struct callback_owner *o=((struct callback*)p)->owner;++o->result->focus_calls;if(mode!=1||unsolicited!=1)++o->result->unexpected_callback;return 0;}
static const void *callback_vtable[]={complete,deleting,unexpected,data_callback,codec_callback,unexpected,start_callback,stop_callback,config_callback,focus_callback};
int factory_trigger(unsigned enabled,uintptr_t caller,volatile uint32_t *once){uint32_t zero=0;if(!enabled||caller!=0x124e54u)return 0;return __atomic_compare_exchange_n(once,&zero,1,0,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED);}
static int valid_object(void *p,uintptr_t vptr,unsigned id,void *router){return word(p,0)==vptr&&word(p,8)==(uintptr_t)router&&word(p,12)==id&&!((unsigned char*)p)[4]&&!((unsigned char*)p)[5];}
int factory_run(const struct factory_api *a,void *router,struct factory_result *r){
 void *v=0,*i=0;struct callback *c=0;struct factory_shared temp={0,0};struct callback_owner owner={a,r,0,0};
 unsigned char payload[16];uint32_t buffer_words[4],start_words[3]={0,37,0},stop_words[1]={0},focus_words[6]={0,0,1,1,0,4};
 struct factory_shared buffer={0,buffer_words};unsigned k;int keys[2]={23,65536};uint32_t inserted[2];
 memset(r,0,sizeof(*r));
 if(!a||!router||!a->allocate||!a->deallocate||!a->video_ctor||!a->input_ctor||!a->wrap||!a->attach||!a->release||!a->video_delete||!a->input_delete||!a->add_config||!a->config_count||!a->media_start||!a->media_stop||!a->codec||!a->data||!a->focus_request||!a->input_key||!a->video_vptr||!a->input_vptr){r->error=1;return -1;}
 v=a->allocate(0x50);if(!v){r->error=2;return -1;}
 a->video_ctor(v,9,router,0);r->video_constructed=1;
 if(!valid_object(v,a->video_vptr,9,router)||word(v,0x34)||word(v,0x38)||((unsigned char*)v)[0x30]){r->error=3;goto quarantine;}
 i=a->allocate(0x64);if(!i){r->error=4;goto cleanup;}
 a->input_ctor(i,10,router);r->input_constructed=1;
 if(!valid_object(i,a->input_vptr,10,router)||word(i,0x5c)||word(i,0x60)){r->error=5;goto quarantine;}
 /* Reuse the exact stock set<int>::insert sret helper on the private set. */
 for(k=0;k<2;++k){memset(inserted,0,sizeof(inserted));a->input_key(inserted,(char*)i+0x38,&keys[k]);if(!inserted[0]||((unsigned char*)inserted)[4]!=1){r->error=16;goto quarantine;}}
 c=a->allocate(sizeof(*c));if(!c){r->error=6;goto cleanup;}
 c->vtable=callback_vtable;c->owner=&owner;
 a->wrap(&temp,c);
 if(!temp.count||temp.object!=c||*temp.count!=1){r->error=7;goto quarantine;}
 r->callback_wrapped=1;a->attach(v,&temp);
 if(word(v,0x34)!=(uintptr_t)temp.count||word(v,0x38)!=(uintptr_t)c||*temp.count!=2){r->error=8;goto quarantine;}
 r->callback_attached=1;a->release(&temp);r->temp_released=1;
 /* A released temporary may retain stale words; never release it twice. */
 if(*(uint32_t*)word(v,0x34)!=1){r->error=9;goto quarantine;}
 temp.count=0;temp.object=0;c=0;
 if(a->config_count(v)!=0){r->error=10;goto cleanup;}
 /* addSupportedConfiguration returns index, not count (native8e170). */
 if(a->add_config(v,1,2,0,0,160,0,10000)!=0||a->config_count(v)!=1){r->error=11;goto cleanup;}
 r->configurations=1;
 /* Profiled native methods read Start fields4/8, no Stop fields and Focus
  * fields8/c/14. These local argument views are neither serialized nor
  * retained, and no virtual protobuf method is called on them. */
 for(k=0;k<sizeof(payload);++k)payload[k]=(unsigned char)(k+0x40);
 buffer_words[0]=(uintptr_t)payload;buffer_words[1]=sizeof(payload);buffer_words[2]=2;buffer_words[3]=15;
 owner.payload=payload;owner.buffer=&buffer;
 if(a->media_start(v,start_words)||a->codec(v,payload,8)||a->data(v,0x123456789abcdef0ULL,&buffer,3)||a->focus_request(v,focus_words)!=1||a->media_stop(v,stop_words)){r->error=14;goto cleanup;}
 if(r->codec_calls!=1||r->start_calls!=1||r->stop_calls!=1||r->media_config_calls!=1||r->focus_calls!=1||r->data_calls!=1||r->data_bytes!=10){r->error=15;goto cleanup;}

 cleanup:
 if(i){a->input_delete(i);r->input_destroyed=1;}
 if(v){a->video_delete(v);r->video_destroyed=1;}
 if(r->callback_attached&&r->callback_destroyed!=1)r->error=12;
 if(r->unexpected_callback)r->error=13;
 return r->error?-1:0;
 quarantine:
 /* Unknown native layout/refcounts: do not guess at a destructor or publish.
  * Kernel reclaims these private, unregistered allocations at process exit. */
 r->quarantined=1;return -1;
}
