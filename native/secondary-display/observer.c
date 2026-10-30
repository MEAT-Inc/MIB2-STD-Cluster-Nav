#define _GNU_SOURCE 1
#define _QNX_SOURCE 1
#include "runtime.h"
#include "../endpoint-factory/probe.h"
#include "../observer/observer.h"
#include "wire.h"
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdio.h>
#define POP_SYMBOL "_ZN13MessageRouter32populateServiceDiscoveryResponseEP24ServiceDiscoveryResponse"
#define QUEUE_SYMBOL "_ZN13MessageRouter13queueOutgoingEhPvj"
struct buffer {unsigned char *data;unsigned capacity,start,end;};
static int (*native_pop)(void*,void*),(*native_queue)(void*,unsigned char,void*,unsigned);
static int (*native_marshall)(void*,unsigned short,const void*,struct buffer*);
static void (*native_video_discovery)(void*,void*),(*native_input_discovery)(void*,void*);
static struct stream_context context;static struct stream_report fallback_report;
static pthread_mutex_t discovery_mutex=PTHREAD_MUTEX_INITIALIZER;
static int enabled;static unsigned char *stock_storage,*stock_wire,*last_good;static unsigned stock_bytes,last_good_bytes;
static uintptr_t libbase;
struct discovery_capture {uint32_t magic,pid,original_bytes,sent_bytes,flags,committed;unsigned char original[8192],sent[16384];};
static struct discovery_capture *discovery_capture;
_Static_assert(sizeof(struct discovery_capture)==24600,"discovery capture ABI");
static int basename_is_library(const char *p){const char *n=strrchr(p,'/');n=n?n+1:p;return !strcmp(n,"libautoreceiver.so")||!strcmp(n,"libautoreceiver.so.1");}
__attribute__((constructor)) static void secondary_init(void){
 const char *p=getenv("DELPHI_OBSERVER_LOG"),*prefix="/dev/shmem/delphi-observer-aa-";char path[160];unsigned j,n=strlen(prefix);struct stream_report *r=&fallback_report;int fd=-1,raw=-1,df=-1,saved=errno;Dl_info pi,qi;
 native_pop=dlsym(RTLD_NEXT,POP_SYMBOL);native_queue=dlsym(RTLD_NEXT,QUEUE_SYMBOL);
 if(!p||strncmp(p,prefix,n)||strlen(p)!=n+36||strcmp(p+n+32,".bin"))goto initialized;
 for(j=0;j<32;++j)if(!((p[n+j]>='0'&&p[n+j]<='9')||(p[n+j]>='a'&&p[n+j]<='f')))goto initialized;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-secondary-report-%.*s.bin",32,p+n);fd=open(path,O_CREAT|O_EXCL|O_RDWR,0600);
 if(fd<0||ftruncate(fd,sizeof(*r)))goto initialized;
 {void *m=mmap(0,sizeof(*r),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);if(m==MAP_FAILED)goto initialized;r=m;}
 snprintf(path,sizeof(path),"/dev/shmem/delphi-secondary-video-%.*s.h264",32,p+n);raw=open(path,O_CREAT|O_EXCL|O_WRONLY,0600);
 snprintf(path,sizeof(path),"/dev/shmem/delphi-secondary-discovery-%.*s.bin",32,p+n);df=open(path,O_CREAT|O_EXCL|O_RDWR,0600);
 if(df>=0&&!ftruncate(df,sizeof(*discovery_capture))){void *m=mmap(0,sizeof(*discovery_capture),PROT_READ|PROT_WRITE,MAP_SHARED,df,0);if(m!=MAP_FAILED){discovery_capture=m;memset(m,0,sizeof(*discovery_capture));discovery_capture->magic=0x32534344;discovery_capture->pid=getpid();}}
 if(!native_pop||!native_queue||!dladdr((void*)native_pop,&pi)||!dladdr((void*)native_queue,&qi)||pi.dli_fbase!=qi.dli_fbase||!pi.dli_fname||!basename_is_library(pi.dli_fname))goto initialized;
 libbase=(uintptr_t)pi.dli_fbase;
 if((uintptr_t)native_pop-libbase!=0x7f57c||(uintptr_t)native_queue-libbase!=0x7f5d8)goto initialized;
 native_marshall=(int(*)(void*,unsigned short,const void*,struct buffer*))(libbase+0x7f600);
 native_video_discovery=(void(*)(void*,void*))(libbase+0x8dc90);native_input_discovery=(void(*)(void*,void*))(libbase+0x79040);
 enabled=raw>=0&&discovery_capture;
 initialized:if(fd>=0)close(fd);if(df>=0)close(df);stream_init(&context,r,raw);
 if(enabled){int tf;snprintf(path,sizeof(path),"/dev/shmem/delphi-secondary-timing-%.*s.bin",32,p+n);tf=open(path,O_CREAT|O_EXCL|O_RDWR,0600);if(tf>=0){if(!ftruncate(tf,sizeof(struct stream_timing))){void *m=mmap(0,sizeof(struct stream_timing),PROT_READ|PROT_WRITE,MAP_SHARED,tf,0);if(m!=MAP_FAILED){context.timing=m;memset(m,0,sizeof(struct stream_timing));context.timing->magic=0x314d4954;context.timing->version=1;context.timing->pid=getpid();context.timing->record_bytes=40;context.timing->capacity=TIMING_CAPACITY;}}close(tf);}}
 if(!enabled&&r!=&fallback_report)r->w[SERROR]=30;errno=saved;
}
/* Stock discovery bytes are backed by the same native marshaller heap. They
 * remain untouched and available if construction/rewrite cannot commit. */
static int backup_stock(void *router,void *response){struct buffer b={0,0,0,0};
 if(stock_storage)return 1;
 (void)native_marshall(router,6,response,&b);
 if(!b.data||b.start>b.end||b.end>b.capacity||b.end-b.start<2||b.end-b.start>8192||b.data[b.start]||b.data[b.start+1]!=6){free(b.data);return 0;}
 stock_storage=b.data;stock_wire=b.data+b.start;stock_bytes=b.end-b.start;context.report->w[SBACKUP]=stock_bytes;return 1;
}
__attribute__((visibility("default"))) int secondary_populate(void *router,void *response) __asm__(POP_SYMBOL);
int secondary_populate(void *router,void *response){int result,saved,entry_errno=errno;struct factory_api api;uintptr_t profile_router,primary,base;struct stream_native a;
 if(!native_pop)_exit(125);
 if(!enabled)return native_pop(router,response);
 pthread_mutex_lock(&discovery_mutex);
 if(context.installed&&context.router==router){uint32_t s9,s10;memcpy(&s9,(char*)router+0x100+9*4,4);memcpy(&s10,(char*)router+0x100+10*4,4);if(s9!=(uintptr_t)context.video||s10!=(uintptr_t)context.input){stream_retire(&context);context.report->w[SERROR]=32;}}
 errno=entry_errno;result=native_pop(router,response);saved=errno;context.report->w[SPOPULATE]++;
 if(!context.armed&&factory_profile_api(&api,&profile_router,&primary,&base)&&profile_router==(uintptr_t)router&&base==libbase){
  memset(&a,0,sizeof(a));a.object=api;a.reg=(int(*)(void*,void*))(base+0x7f54c);a.focus=(void(*)(void*,int,unsigned char))(base+0x8db50);a.ack=(void(*)(void*,int,unsigned))(base+0x7e650);stream_arm(&context,&a,router);
 }
 if(context.armed&&context.router==router&&!context.attempted){
  if(backup_stock(router,response)&&stream_install(&context)){
   native_video_discovery(context.video,response);native_input_discovery(context.input,response);
  }else if(!stock_storage&&!context.report->w[SERROR])context.report->w[SERROR]=31;
 }
 pthread_mutex_unlock(&discovery_mutex);errno=saved;return result;
}
__attribute__((visibility("default"))) int secondary_queue(void *router,unsigned char channel,void *bytes,unsigned n) __asm__(QUEUE_SYMBOL);
int secondary_queue(void *router,unsigned char channel,void *bytes,unsigned n){unsigned char *temp=0,*send=bytes;unsigned length=n,out=0;int result,saved=errno;
 if(!native_queue)_exit(125);
 if(!enabled||channel||!bytes||n<2||((unsigned char*)bytes)[0]||((unsigned char*)bytes)[1]!=6)return native_queue(router,channel,bytes,n);
 pthread_mutex_lock(&discovery_mutex);
 if(context.installed&&context.router==router){
  if(discovery_capture){__atomic_store_n(&discovery_capture->committed,0,__ATOMIC_RELEASE);discovery_capture->original_bytes=n>8192?8192:n;discovery_capture->sent_bytes=0;discovery_capture->flags=n>8192?1:0;memcpy(discovery_capture->original,bytes,discovery_capture->original_bytes);}
  temp=malloc(16384);
  if(temp&&cluster_wire_rewrite(bytes,n,temp,16384,&out)){
   send=temp;length=out;context.report->w[SREWRITES]++;if(__atomic_load_n(&context.report->w[SSTAGE],__ATOMIC_RELAXED)<3)__atomic_store_n(&context.report->w[SSTAGE],3,__ATOMIC_RELAXED);
  }else {
   if(discovery_capture){discovery_capture->flags|=2;}
   context.report->w[SWIREERROR]=1;context.report->w[SFALLBACK]++;
   if(last_good){send=last_good;length=last_good_bytes;}
   else if(stock_wire){send=stock_wire;length=stock_bytes;stream_rollback(&context);}
   else {_exit(125);} /* No unknown pair descriptor may escape without metadata. */
  }
 }
 if(discovery_capture&&context.router==router&&discovery_capture->original_bytes){discovery_capture->sent_bytes=length>16384?16384:length;memcpy(discovery_capture->sent,send,discovery_capture->sent_bytes);__atomic_store_n(&discovery_capture->committed,1,__ATOMIC_RELEASE);}
 errno=saved;result=native_queue(router,channel,send,length);saved=errno;
 if(temp&&send==temp){free(last_good);last_good=temp;last_good_bytes=length;temp=0;}
 free(temp);pthread_mutex_unlock(&discovery_mutex);errno=saved;return result;
}

#ifdef SECONDARY_TESTING
void secondary_test_bind(const struct secondary_test_hooks *h,const struct stream_native *a,void *router,struct stream_report *r,int fd){
 free(stock_storage);free(last_good);stock_storage=stock_wire=last_good=0;stock_bytes=last_good_bytes=0;
 pthread_mutex_destroy(&context.mutex);stream_init(&context,r,fd);stream_arm(&context,a,router);
 native_pop=h->populate;native_queue=h->queue;native_marshall=(int(*)(void*,unsigned short,const void*,struct buffer*))h->marshal;
 native_video_discovery=h->video_discovery;native_input_discovery=h->input_discovery;enabled=1;
}
#endif
