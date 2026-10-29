/* Extend the tested registration observer without changing that source/release. */
#include "../observer.c"
#include "display.h"
_Static_assert(sizeof(struct display_record)==4160,"display record ABI");
static struct display_file display_fallback;
static struct display_file *display_log=&display_fallback;
static uintptr_t display_targets[3];
static uint32_t display_owner;
static int display_enabled;
static uintptr_t resolve_display(const char *name,uintptr_t *base){
 void *target=dlsym(RTLD_NEXT,name);Dl_info info,self;
 if(!target||!dladdr(target,&info)||!info.dli_fname||!dladdr((void*)resolve_display,&self)||info.dli_fbase==self.dli_fbase||
    (strcmp(basename_of(info.dli_fname),"libautoreceiver.so")&&strcmp(basename_of(info.dli_fname),"libautoreceiver.so.1")))resolution_failure();
 if(*base && *base!=(uintptr_t)info.dli_fbase)resolution_failure();
 *base=(uintptr_t)info.dli_fbase;return (uintptr_t)target;
}
__attribute__((constructor)) static void display_initialize(void){
 const char *mainpath=getenv("DELPHI_OBSERVER_LOG");const char *prefix="/dev/shmem/delphi-observer-aa-";
 char path[160];uintptr_t base=0;int fd,saved=errno;unsigned i,n=(unsigned)strlen(prefix);
 display_targets[0]=resolve_display(CONFIG_SYMBOL,&base);display_targets[1]=resolve_display(FOCUS_SYMBOL,&base);display_targets[2]=resolve_display(QUEUE_SYMBOL,&base);
 display_owner=(uint32_t)getpid();
 display_fallback.header.magic=DISPLAY_MAGIC;display_fallback.header.version=1;
 display_fallback.header.header_bytes=128;display_fallback.header.record_bytes=4160;
 display_fallback.header.capacity=DISPLAY_CAPACITY;display_fallback.header.pointer_bytes=4;display_fallback.header.pid=display_owner;
 display_fallback.header.native_address=display_targets[0];display_fallback.header.module_base=base;
 display_fallback.header.reserved[0]=display_targets[1];display_fallback.header.reserved[1]=display_targets[2];
 display_fallback.header.status=OBS_READY|OBS_LOG_DISABLED;
 if(!mainpath||strncmp(mainpath,prefix,n)||strlen(mainpath)!=n+36||strcmp(mainpath+n+32,".bin"))goto done;
 for(i=0;i<32;++i)if(!((mainpath[n+i]>='0'&&mainpath[n+i]<='9')||(mainpath[n+i]>='a'&&mainpath[n+i]<='f')))goto done;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-display-%.*s.bin",32,mainpath+n);
 fd=open(path,O_CREAT|O_EXCL|O_RDWR,0600);if(fd<0)goto done;
 if(!ftruncate(fd,sizeof(*display_log))){void *mapped=mmap(0,sizeof(*display_log),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);
  if(mapped!=MAP_FAILED){display_log=mapped;memset(display_log,0,sizeof(*display_log));display_log->header=display_fallback.header;display_log->header.status=OBS_READY;display_enabled=1;}}
 close(fd);
 done:errno=saved;
}
/* saved points to this shim's saved r0-r3/ip/lr, followed by original stack args.
 * Endpoint objects are never dereferenced. Queue input is borrowed only for the
 * bounded synchronous copy; stock queueOutgoing reads/copies those same bytes. */
__attribute__((visibility("hidden"))) uintptr_t delphi_display_enter(const uint32_t *saved,uint32_t event,uint32_t caller){
 int saved_errno=errno;uint32_t zero=0,argc=event==1?8:event==2?3:4;unsigned i;
 uint32_t payload=0,flags=0;struct obs_header *h=&display_log->header;struct display_record *r;
 uintptr_t target=event>=1&&event<=3?display_targets[event-1]:0;
 if(!target)resolution_failure();
 if(!display_enabled||(uint32_t)getpid()!=display_owner)goto done;
 if(event==3){const unsigned char *data=(const unsigned char*)(uintptr_t)saved[2];
  if(saved[1]!=0||saved[3]<2||!data)goto done;
  if(saved[3]>DISPLAY_PAYLOAD){flags=1;}else if(data[0]||data[1]!=6)goto done;else payload=saved[3];
 }
 if(!__atomic_compare_exchange_n(&h->lock,&zero,1,1,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED)){dropped(h);goto done;}
 if(h->count>=DISPLAY_CAPACITY){dropped(h);goto unlock;}
 r=&display_log->records[h->count];r->sequence=h->count+1;r->event=event;
 r->thread=(uint32_t)(uintptr_t)pthread_self();r->argc=argc;r->caller=caller;
 for(i=0;i<argc;++i)r->args[i]=saved[i<4?i:i+2];
 r->payload_bytes=payload;r->flags=flags;
 if(payload)memcpy(r->payload,(const void*)(uintptr_t)saved[2],payload);
 __atomic_store_n(&r->committed,r->sequence,__ATOMIC_RELEASE);
 __atomic_store_n(&h->count,r->sequence,__ATOMIC_RELEASE);
 unlock:__atomic_store_n(&h->lock,0,__ATOMIC_RELEASE);
 done:errno=saved_errno;return target;
}
__attribute__((visibility("default"))) const struct display_file *delphi_display_view(void){return display_log;}
