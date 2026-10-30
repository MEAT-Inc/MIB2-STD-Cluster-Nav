#define _QNX_SOURCE 1
#include "runtime.h"
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <unistd.h>
_Static_assert(sizeof(void*)==4,"ARM32 endpoint ABI");
_Static_assert(sizeof(struct stream_report)==512,"stream report ABI");
struct adapter { const void *vtable;struct stream_context *owner; };
static uint32_t word(void *p,unsigned o){uint32_t v;memcpy(&v,(char*)p+o,4);return v;}
static void put(void *p,unsigned o,uint32_t v){memcpy((char*)p+o,&v,4);}
static void add(struct stream_context *c,unsigned index,unsigned value){uint32_t *p=&c->report->w[index];*p=UINT_MAX-*p<value?UINT_MAX:*p+value;}
static void stage(struct stream_context *c,unsigned s){uint32_t old=__atomic_load_n(&c->report->w[SSTAGE],__ATOMIC_RELAXED);while(old<s&&!__atomic_compare_exchange_n(&c->report->w[SSTAGE],&old,s,0,__ATOMIC_RELAXED,__ATOMIC_RELAXED)){} }
static void error(struct stream_context *c,unsigned e){if(!c->report->w[SERROR])c->report->w[SERROR]=e;}
static void complete(void *p){(void)p;}
static void deleting(void *p){struct adapter *a=p;struct stream_context *c=a->owner;stream_retire(c);c->api.object.deallocate(p);}
static int unused(void *p,...){struct stream_context *c=((struct adapter*)p)->owner;pthread_mutex_lock(&c->mutex);error(c,20);pthread_mutex_unlock(&c->mutex);return -1;}
static unsigned save(struct stream_context *c,const void *p,unsigned n){unsigned done=0,tries=0;ssize_t written;
 if(c->fd<0||c->report->w[SSAVED]>STREAM_LIMIT||n>STREAM_LIMIT-c->report->w[SSAVED])return 0;
 while(done<n&&tries++<8){written=write(c->fd,(const char*)p+done,n-done);if(written<0&&errno==EINTR)continue;if(written<=0){c->report->w[SIOERROR]=errno?errno:EIO;break;}done+=(unsigned)written;add(c,SSAVED,(unsigned)written);}
 return done;
}
static int setup(void *p,int codec){struct stream_context *c=((struct adapter*)p)->owner;pthread_mutex_lock(&c->mutex);add(c,SSETUP,1);c->active=0;c->configured=0;c->session=-1;stage(c,4);if(codec!=3)error(c,21);pthread_mutex_unlock(&c->mutex);return codec==3?0:-1;}
static int configuration(void *p,int index){struct stream_context *c=((struct adapter*)p)->owner;pthread_mutex_lock(&c->mutex);add(c,SCONFIG,1);c->configured=index==0;if(index!=0)error(c,22);pthread_mutex_unlock(&c->mutex);return index==0?0:-1;}
static int start(void *p,int session){struct stream_context *c=((struct adapter*)p)->owner;pthread_mutex_lock(&c->mutex);add(c,SSTART,1);c->session=session;c->report->w[SSESSION]=(uint32_t)session;c->active=c->configured&&session>=0;pthread_mutex_unlock(&c->mutex);return 0;}
static int stop(void *p,int session){struct stream_context *c=((struct adapter*)p)->owner;(void)session;pthread_mutex_lock(&c->mutex);add(c,SSTOP,1);c->active=0;pthread_mutex_unlock(&c->mutex);return 0;}
static int codec(void *p,void *bytes,unsigned n){struct stream_context *c=((struct adapter*)p)->owner;unsigned saved;pthread_mutex_lock(&c->mutex);add(c,SCODEC,1);if(bytes&&n&&n<=65536){saved=save(c,bytes,n);add(c,SCODECBYTES,saved);if(saved!=n)add(c,SDROPPED,1);}else error(c,23);pthread_mutex_unlock(&c->mutex);return 0;}
static int data(void *p,int session,uint64_t timestamp,const struct factory_shared *borrowed,const void *bytes,unsigned n){struct stream_context *c=((struct adapter*)p)->owner;int ack=0;unsigned saved=0;(void)borrowed;
 pthread_mutex_lock(&c->mutex);
 c->report->w[STSLOW]=(uint32_t)timestamp;c->report->w[STSHIGH]=(uint32_t)(timestamp>>32);
 c->report->w[SCHANNEL]=((unsigned char*)c->video)[5];
 if(c->active&&session==c->session&&bytes&&n&&n<=1024*1024){add(c,SFRAMES,1);add(c,SFRAMEBYTES,n);saved=save(c,bytes,n);stage(c,5);}
 if(!n||saved!=n)add(c,SDROPPED,1);
 ack=session>=0&&session==c->session&&((unsigned char*)c->video)[4]&&((unsigned char*)c->video)[5];
 if(ack)add(c,SACKS,1);
 pthread_mutex_unlock(&c->mutex);
 /* ACK only this endpoint/session after synchronous consumption or drop. */
 if(ack)c->api.ack(c->video,session,1);
 return 0;
}
static int focus(void *p,int mode,unsigned char unsolicited){struct stream_context *c=((struct adapter*)p)->owner;int valid=mode>=0&&mode<=2;pthread_mutex_lock(&c->mutex);add(c,SFOCUS,1);if(!valid)error(c,24);pthread_mutex_unlock(&c->mutex);if(valid)c->api.focus(c->video,mode,unsolicited);return 0;}
static const void *vtable[]={complete,deleting,unused,data,codec,setup,start,stop,configuration,focus};
void stream_init(struct stream_context *c,struct stream_report *r,int fd){memset(c,0,sizeof(*c));memset(r,0,sizeof(*r));pthread_mutex_init(&c->mutex,0);c->report=r;c->fd=fd;c->session=-1;r->w[SMAGIC]=STREAM_MAGIC;r->w[SVERSION]=1;r->w[SBYTES]=sizeof(*r);r->w[SPID]=getpid();r->w[SLIMIT]=STREAM_LIMIT;}
void stream_arm(struct stream_context *c,const struct stream_native *a,void *router){if(c->armed||c->attempted)return;c->api=*a;c->router=router;c->armed=1;c->report->w[SFACTORY]=1;c->report->w[SROUTER]=(uintptr_t)router;stage(c,1);}
void stream_retire(struct stream_context *c){pthread_mutex_lock(&c->mutex);c->active=0;c->armed=0;c->installed=0;c->report->w[SINSTALLED]=0;pthread_mutex_unlock(&c->mutex);}
void stream_rollback(struct stream_context *c){uint32_t *s9=(uint32_t*)((char*)c->router+0x100+9*4),*s10=(uint32_t*)((char*)c->router+0x100+10*4);
 if(c->video)__sync_bool_compare_and_swap(s9,(uintptr_t)c->video,0);
 if(c->input)__sync_bool_compare_and_swap(s10,(uintptr_t)c->input,0);
 c->installed=0;c->report->w[SREGISTERED]=0;c->report->w[SINSTALLED]=0;c->report->w[SQUARANTINE]=1;
 /* Do not destroy anything potentially referenced by a discovery protobuf.
  * This diagnostic's quarantined/private objects live until process exit. */
}
int stream_install(struct stream_context *c){struct adapter *a;struct factory_shared temp={0,0};struct factory_api *f=&c->api.object;uint32_t before9,before10,inserted[2];int keys[2]={23,65536};unsigned k;
 if(!c->armed||c->attempted)return c->installed;
 c->attempted=1;add(c,SATTEMPTS,1);before9=word(c->router,0x100+9*4);before10=word(c->router,0x100+10*4);c->report->w[SBEFORE9]=before9;c->report->w[SBEFORE10]=before10;
 if(before9||before10){error(c,1);return 0;}
 c->video=f->allocate(0x50);c->input=f->allocate(0x64);if(!c->video||!c->input){error(c,2);goto fail;}
 f->video_ctor(c->video,9,c->router,1);f->input_ctor(c->input,10,c->router);
 if(word(c->video,0)!=f->video_vptr||word(c->input,0)!=f->input_vptr||word(c->video,8)!=(uintptr_t)c->router||word(c->input,8)!=(uintptr_t)c->router||word(c->video,12)!=9||word(c->input,12)!=10){error(c,3);goto fail;}
 for(k=0;k<2;++k){memset(inserted,0,sizeof(inserted));f->input_key(inserted,(char*)c->input+0x38,&keys[k]);if(!inserted[0]||((unsigned char*)inserted)[4]!=1){error(c,11);goto fail;}add(c,SKEYS,1);}
 put(c->video,0x1c,4);a=f->allocate(sizeof(*a));if(!a){error(c,4);goto fail;}a->vtable=vtable;a->owner=c;f->wrap(&temp,a);
 if(!temp.count||*temp.count!=1||temp.object!=a){error(c,5);goto fail;}
 f->attach(c->video,&temp);if(word(c->video,0x34)!=(uintptr_t)temp.count||word(c->video,0x38)!=(uintptr_t)a||*temp.count!=2){error(c,6);goto fail;}f->release(&temp);if(*temp.count!=1){error(c,7);goto fail;}
 if(f->add_config(c->video,1,2,0,0,160,0,10000)!=0||f->config_count(c->video)!=1){error(c,8);goto fail;}
 c->report->w[SVIDEO]=(uintptr_t)c->video;c->report->w[SINPUT]=(uintptr_t)c->input;c->report->w[SCALLBACK]=(uintptr_t)a;c->report->w[SVID]=9;c->report->w[SINID]=10;
 if(!c->api.reg(c->router,c->video)||word(c->router,0x100+9*4)!=(uintptr_t)c->video){error(c,9);goto fail;}
 if(!c->api.reg(c->router,c->input)||word(c->router,0x100+10*4)!=(uintptr_t)c->input){error(c,10);goto fail;}
 c->installed=1;c->report->w[SREGISTERED]=2;c->report->w[SINSTALLED]=1;stage(c,2);return 1;
 fail:stream_rollback(c);return 0;
}
