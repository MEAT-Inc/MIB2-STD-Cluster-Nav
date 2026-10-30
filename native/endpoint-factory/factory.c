#include "factory.h"
#include <stddef.h>
#include <string.h>
_Static_assert(sizeof(void*)==4,"Delphi ARM32 ABI");
_Static_assert(sizeof(struct factory_shared)==8,"count pointer then object pointer");
struct callback_owner { const struct factory_api *api; struct factory_result *result; };
struct callback { const void *vtable; struct callback_owner *owner; };
_Static_assert(sizeof(struct callback)==8,"independent callback adapter");
static uintptr_t word(const void *p,unsigned offset){uint32_t v;memcpy(&v,(const char*)p+offset,4);return v;}
static void complete(void *p){struct callback *c=p;++c->owner->result->callback_destroyed;}
static void deleting(void *p){struct callback *c=p;const struct factory_api *a=c->owner->api;complete(p);a->deallocate(p);}
static int unexpected(void *p,...){struct callback *c=p;++c->owner->result->unexpected_callback;return -1;}
/* Only destructors are reachable while this endpoint remains unpublished. */
static const void *callback_vtable[]={complete,deleting,unexpected,unexpected,unexpected,unexpected,unexpected,unexpected,unexpected,unexpected};
static int valid_object(void *p,uintptr_t vptr,unsigned id,void *router){return word(p,0)==vptr&&word(p,8)==(uintptr_t)router&&word(p,12)==id&&!((unsigned char*)p)[4]&&!((unsigned char*)p)[5];}
int factory_run(const struct factory_api *a,void *router,struct factory_result *r){
 void *v=0,*i=0;struct callback *c=0;struct factory_shared temp={0,0};struct callback_owner owner={a,r};
 memset(r,0,sizeof(*r));
 if(!a||!router||!a->allocate||!a->deallocate||!a->video_ctor||!a->input_ctor||!a->wrap||!a->attach||!a->release||!a->video_delete||!a->input_delete||!a->add_config||!a->config_count||!a->video_vptr||!a->input_vptr){r->error=1;return -1;}
 v=a->allocate(0x50);if(!v){r->error=2;return -1;}
 a->video_ctor(v,9,router,0);r->video_constructed=1;
 if(!valid_object(v,a->video_vptr,9,router)||word(v,0x34)||word(v,0x38)||((unsigned char*)v)[0x30]){r->error=3;goto quarantine;}
 i=a->allocate(0x64);if(!i){r->error=4;goto cleanup;}
 a->input_ctor(i,10,router);r->input_constructed=1;
 if(!valid_object(i,a->input_vptr,10,router)||word(i,0x5c)||word(i,0x60)){r->error=5;goto quarantine;}
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
 if(a->add_config(v,1,2,0,0,160,0,10000)!=1||a->config_count(v)!=1){r->error=11;goto cleanup;}
 r->configurations=1;
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
