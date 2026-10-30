#define main factory_fixture_original_main
#include "../endpoint-factory/fixture.c"
#undef main
#include "runtime.h"
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
static unsigned reg_calls,ack_calls,focus_calls;static void *expected_video;
static int reg(void *router,void *endpoint){unsigned id=get(endpoint,12);uint32_t *slot=(uint32_t*)((char*)router+0x100+id*4);++reg_calls;if(mode>=3&&id==10){if(mode==4)put(router,0x100+9*4,0xaabbcc00);return 0;}if(*slot)return 0;*slot=(uintptr_t)endpoint;return 1;}
static void ack(void *v,int session,unsigned count_ack){if(v!=expected_video||session!=37||count_ack!=1)++bad;++ack_calls;}
static void focus_native(void *v,int m,unsigned char unsolicited){if(v!=expected_video||m!=1||!unsolicited)++bad;++focus_calls;}
int main(void){
 struct stream_native api={{allocate,deallocate,video_ctor,input_ctor,wrap,attach,release,video_delete,input_delete,add_config,count,media_start,media_stop,codec,data,focus,input_key,0x80001000,0x80002000},reg,focus_native,ack};
 struct stream_timing timing;struct stream_context c;struct stream_report report;unsigned char router[0x500],payload[16];unsigned k,scenario;uint32_t start_view[3]={0,37,0},io[4];struct factory_shared borrowed={0,io};struct stat st;int fd;
 for(scenario=0;scenario<4;++scenario){
  memset(router,0,sizeof(router));for(k=1;k<=8;++k)put(router,0x100+k*4,0x20000000+k*4);
  attempt=fail_at=bad=0;mode=scenario==1?3:scenario==3?4:0;reg_calls=ack_calls=focus_calls=0;
  if(scenario==2)put(router,0x100+9*4,0xbbccdd00);
  fd=open("/dev/shmem/secondary-runtime-fixture.bin",O_RDWR|O_CREAT|O_EXCL,0600);if(fd<0)return 1;
  stream_init(&c,&report,fd);memset(&timing,0,sizeof(timing));c.timing=&timing;stream_arm(&c,&api,router);
  if(scenario==0){
   if(!stream_install(&c)||reg_calls!=2||report.w[SREGISTERED]!=2||!c.installed)return 2;
   expected_video=c.video;((unsigned char*)c.video)[4]=1;((unsigned char*)c.video)[5]=9;
   if(((int(*)(void*,int))vt(c.video)[5])(cb(c.video),3)||api.object.media_start(c.video,start_view))return 3;
   for(k=0;k<sizeof(payload);++k)payload[k]=(unsigned char)k;
   if(api.object.codec(c.video,payload,8))return 4;
   io[0]=(uintptr_t)payload;io[1]=16;io[2]=2;io[3]=15;
   if(api.object.data(c.video,0x123456789abcdef0ULL,&borrowed,3))return 5;
   (void)((int(*)(void*,int,unsigned char))vt(c.video)[9])(cb(c.video),1,1);
   if(report.w[SFRAMES]!=1||report.w[SSAVED]!=18||ack_calls!=1||focus_calls!=1||report.w[STSLOW]!=0x9abcdef0||report.w[STSHIGH]!=0x12345678||report.w[SCHANNEL]!=9||bad)return 6;
   if(fstat(fd,&st)||st.st_size!=18)return 7;
   if(timing.count!=2||timing.clock_error||timing.records[0].kind!=1||timing.records[0].offset||timing.records[0].saved!=8||timing.records[1].kind!=2||timing.records[1].timestamp!=0x123456789abcdef0ULL||timing.records[1].offset!=8||timing.records[1].saved!=10||!timing.records[1].monotonic_ns)return 15;
   timing.count=TIMING_CAPACITY;
   report.w[SSAVED]=STREAM_LIMIT;
   (void)api.object.data(c.video,1,&borrowed,3);
   if(ack_calls!=2||report.w[SDROPPED]!=1||report.w[SSAVED]!=STREAM_LIMIT||timing.dropped!=1)return 8;
   stream_rollback(&c);if(get(router,0x100+9*4)||get(router,0x100+10*4))return 9;
  }else{
   if(stream_install(&c)||c.installed||report.w[SREGISTERED])return 10;
   if(scenario==1&&(get(router,0x100+9*4)||get(router,0x100+10*4)))return 11;
   if(scenario==2&&(attempt||reg_calls||get(router,0x100+9*4)!=0xbbccdd00))return 12;
   if(scenario==3&&get(router,0x100+9*4)!=0xaabbcc00)return 13;
  }
  for(k=1;k<=8;++k)if(get(router,0x100+k*4)!=0x20000000+k*4)return 14;
  close(fd);unlink("/dev/shmem/secondary-runtime-fixture.bin");pthread_mutex_destroy(&c.mutex);
  /* Only synthetic fixture allocations; live diagnostic objects intentionally
   * remain valid until process exit, including rollback quarantine. */
  for(k=0;k<32;++k)if(allocations[k]){free(allocations[k]);allocations[k]=0;}
 }
 puts("SECONDARY_RUNTIME_QNX_PASS registration=paired rollback=owned_only capture=bounded ack=private_session");return 0;
}
