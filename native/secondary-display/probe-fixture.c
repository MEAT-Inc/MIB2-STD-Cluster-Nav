#define main factory_fixture_original_main
#include "../endpoint-factory/fixture.c"
#undef main
#include "runtime.h"
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
static unsigned acks,refreshes,expected_ack;
static void *expected_video;static struct live_shared *expected_shared;static uint32_t expected_head;
static int reg(void *r,void *v){unsigned id=get(v,12);put(r,0x100+id*4,(uintptr_t)v);return 1;}
static void ack(void *v,int session,unsigned n){if(v!=expected_video||session!=37||n!=1||(expected_shared&&expected_shared->head!=expected_head))++bad;acks++;}
static void refresh(void *v,int mode,unsigned char unrequested){if(v!=expected_video||mode!=1||unrequested!=1||acks!=expected_ack)++bad;refreshes++;}
int main(void){
 struct stream_native api={{allocate,deallocate,video_ctor,input_ctor,wrap,attach,release,video_delete,input_delete,add_config,count,media_start,media_stop,codec,data,focus,input_key,0x80001000,0x80002000},reg,refresh,ack};
 struct stream_context c;struct stream_report report;struct stream_timing *timing=calloc(1,sizeof(*timing));unsigned char router[0x500]={0},payload[]={0,0,0,1,0x65,0x88,0x84,0x21};uint32_t io[4],start_view[3]={0,37,0};struct factory_shared b={0,io};unsigned i;struct live_shared *shared=calloc(1,sizeof(*shared));struct live_peer reader;struct live_frame frame;unsigned char received[64];uint32_t nonce[4]={1,2,3,4};static const unsigned char config[]={0,0,1,0x67,0x42,0x80,0x1f,0,0,1,0x68,0xee};int fd=open("/dev/shmem/keyframe-probe-fixture.bin",O_CREAT|O_EXCL|O_RDWR,0600);
 if(fd<0||!timing)return 1;
 for(i=1;i<=8;i++)put(router,0x100+i*4,0x20000000+i*4);
 stream_init(&c,&report,fd);c.timing=timing;stream_arm(&c,&api,router);if(!stream_install(&c))return 2;expected_video=c.video;((unsigned char*)c.video)[4]=1;((unsigned char*)c.video)[5]=9;
 if(((int(*)(void*,int))vt(c.video)[5])(cb(c.video),3)||api.object.media_start(c.video,start_view))return 3;
 if(!shared||live_init(shared,sizeof(*shared),nonce,getpid(),1)||live_bind(&c.live,shared,sizeof(*shared),nonce,getpid(),1)||live_bind(&reader,shared,sizeof(*shared),nonce,getpid(),1))return 12;
 c.live_enabled=1;c.live_attempted=1;c.live_codec=malloc(65536);if(!c.live_codec)return 13;
 if(api.object.codec(c.video,(void*)config,sizeof(config)))return 14;
 c.probe_enabled=1;report.w[43]=1;io[0]=(uintptr_t)payload;io[1]=sizeof(payload);io[2]=0;io[3]=sizeof(payload);
 /* A different callback session must not ACK or request a refresh. */
 ((int(*)(void*,int,uint64_t,const struct factory_shared*,const void*,unsigned))vt(c.video)[3])(cb(c.video),99,0,&b,payload,sizeof(payload));
 if(acks||refreshes)return 4;
 expected_shared=shared;expected_head=shared->head+1;
 if(api.object.data(c.video,1,&b,0)||refreshes||acks!=1||live_consume(&reader,received,sizeof(received),&frame)!=1||frame.bytes!=sizeof(config)+sizeof(payload))return 5;
 for(i=0;i<4;i++){c.probe_next_ns=1;expected_ack=acks+1;expected_head=shared->head+1;if(api.object.data(c.video,2+i,&b,0)||live_consume(&reader,received,sizeof(received),&frame)!=1||memcmp(received,config,sizeof(config))||memcmp(received+sizeof(config),payload,sizeof(payload)))return 6;}
 if(report.w[50]!=5||report.w[51]||report.w[52]||refreshes!=3||acks!=5||report.w[44]!=3||report.w[45]!=5||report.w[47]||bad)return 7;
 {unsigned probes=0;for(i=0;i<timing->count;i++)if(timing->records[i].kind==3){probes++;if(timing->records[i].requested||timing->records[i].saved)return 8;}if(probes!=3)return 9;}
 for(i=1;i<=8;i++)if(get(router,0x100+i*4)!=0x20000000+i*4)return 10;
 c.active=0;c.probe_next_ns=1;expected_head=shared->head;if(api.object.data(c.video,7,&b,0)||refreshes!=3)return 11;
 close(fd);unlink("/dev/shmem/keyframe-probe-fixture.bin");pthread_mutex_destroy(&c.mutex);free(timing);free(c.live_codec);free(shared);
 for(i=0;i<32;i++)if(allocations[i])free(allocations[i]);
 puts("SECONDARY_KEYFRAME_PROBE_PASS scoped_channel9=1 ack_before_refresh=1 requests_max3=1 active_session_only=1 timing_markers=1 primary_unchanged=1 no_extra_thread=1 callback_owned_queue=1 codec_copy=1");return 0;
}
