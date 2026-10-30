/* Separate observer variant. No registration or descriptor injection. */
#define delphi_observer_enter delphi_registration_log_enter
#include "../observer/observer.c"
#undef delphi_observer_enter
#include "probe.h"
#include "profile.h"
_Static_assert(sizeof(struct factory_report)==256,"factory report wire size");
static struct factory_report fallback_report,*report=&fallback_report;
static int probe_enabled;
__attribute__((constructor)) static void probe_initialize(void){
 const char *p=getenv("DELPHI_OBSERVER_LOG"),*prefix="/dev/shmem/delphi-observer-aa-";char path[160];unsigned j,n=strlen(prefix);int fd,saved=errno;
 report->magic=FACTORY_MAGIC;report->version=1;report->bytes=sizeof(*report);report->pid=getpid();
 if(!p||strncmp(p,prefix,n)||strlen(p)!=n+36||strcmp(p+n+32,".bin"))goto done;
 for(j=0;j<32;++j)if(!((p[n+j]>='0'&&p[n+j]<='9')||(p[n+j]>='a'&&p[n+j]<='f')))goto done;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-endpoint-factory-%.*s.bin",32,p+n);
 fd=open(path,O_RDWR|O_CREAT|O_EXCL,0600);if(fd<0)goto done;
 if(!ftruncate(fd,sizeof(*report))){void *m=mmap(0,sizeof(*report),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);if(m!=MAP_FAILED){report=m;memset(m,0,sizeof(*report));*report=fallback_report;probe_enabled=1;}}
 close(fd);
 done:errno=saved;
}
static uint32_t word_at(const void *p,unsigned offset){uint32_t n;memcpy(&n,(const char*)p+offset,4);return n;}
static int profile_matches(uintptr_t bias,uintptr_t receiver){unsigned j;for(j=0;j<sizeof(profile_spans)/sizeof(profile_spans[0]);++j){const struct profile_span *s=&profile_spans[j];uintptr_t b=s->receiver?receiver:bias;if(memcmp((void*)(b+s->address),s->bytes,s->size))return 0;}return 1;}
static void run_probe(uintptr_t receiver,uintptr_t endpoint,uintptr_t caller){
 Dl_info app;uintptr_t bias,base;uint32_t zero=0;unsigned char primary[0x50],table[0x400];struct factory_api api;int rc;
 if(!probe_enabled||!dladdr((void*)caller,&app)||!app.dli_fname||strcmp(basename_of(app.dli_fname),"AndroidAuto.original"))return;
 bias=(uintptr_t)app.dli_fbase-0x100000u;
 if(caller!=bias+0x124e54u||!__atomic_compare_exchange_n(&report->started,&zero,1,0,__ATOMIC_ACQUIRE,__ATOMIC_RELAXED))return;
 base=(uintptr_t)logfile->header.module_base;report->app_bias=bias;report->receiver_base=base;report->router=receiver;report->main_endpoint=endpoint;
 if((uintptr_t)native_target-base!=0x76facu||!profile_matches(bias,base)){report->error=1;goto refused;}
 if(!endpoint||!receiver||word_at((void*)endpoint,0)!=base+0x117358u||word_at((void*)endpoint,8)!=receiver||word_at((void*)endpoint,12)!=1){report->error=2;goto refused;}
 memcpy(primary,(void*)endpoint,sizeof(primary));memcpy(table,(void*)(receiver+0x100),sizeof(table));
 report->slot9_before=word_at(table,9*4);report->slot10_before=word_at(table,10*4);
 memset(&api,0,sizeof(api));
 api.allocate=(void*(*)(unsigned))(bias+0x10513c);api.deallocate=(void(*)(void*))(bias+0x104a40);
 api.video_ctor=(void(*)(void*,unsigned char,void*,unsigned char))(bias+0x12165c);
 api.input_ctor=(void(*)(void*,unsigned char,void*))(bias+0x121ab0);
 api.wrap=(void(*)(struct factory_shared*,void*))(bias+0x125d64);
 api.attach=(void(*)(void*,const struct factory_shared*))(bias+0x125b5c);
 api.release=(void(*)(struct factory_shared*))(bias+0x11b430);
 api.video_delete=(void(*)(void*))(base+0x8e304);api.input_delete=(void(*)(void*))(base+0x7a30c);
 api.add_config=(int(*)(void*,int,int,int,int,int,int,int))(base+0x8df74);api.config_count=(unsigned(*)(void*))(base+0x8db34);
 api.video_vptr=base+0x117358;api.input_vptr=base+0x117070;
 rc=factory_run(&api,(void*)receiver,&report->result);
 report->primary_unchanged=!memcmp(primary,(void*)endpoint,sizeof(primary));report->table_unchanged=!memcmp(table,(void*)(receiver+0x100),sizeof(table));
 report->slot9_after=word_at((void*)receiver,0x100+9*4);report->slot10_after=word_at((void*)receiver,0x100+10*4);
 if(rc||!report->primary_unchanged||!report->table_unchanged){report->error=100+report->result.error;goto refused;}
 report->status=1;__atomic_store_n(&report->done,1,__ATOMIC_RELEASE);return;
 refused:report->status=2;__atomic_store_n(&report->done,1,__ATOMIC_RELEASE);
}
__attribute__((visibility("hidden"))) uintptr_t delphi_observer_enter(uintptr_t receiver,uintptr_t endpoint,uintptr_t caller){
 int saved=errno;uintptr_t target=delphi_registration_log_enter(receiver,endpoint,caller);
 run_probe(receiver,endpoint,caller);errno=saved;return target;
}
