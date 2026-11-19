#define _POSIX_C_SOURCE 200809L
#include "replay.h"
#include "timeline.h"
#include "handback.h"
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <time.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"TIMELINE_FAIL line=%d\n",__LINE__);exit(1);}}while(0)
static volatile uint32_t report[128];
static unsigned char file[32+8+4*188],accepted[4][188];static unsigned written;
static void put(unsigned at,unsigned v){memcpy(file+at,&v,4);}
static int op(const char *p,int f,...){(void)p;(void)f;return 17;}
static int cl(int f){(void)f;return 0;}
static ssize_t wr(int f,const void *p,size_t n){(void)f;if(report[4]==RPL_ACTIVE){CHECK(n==188&&written<4);memcpy(accepted[written++],p,188);}return n;}
static int geo(void *p,int f){(void)p;return f==17;}
static void packet(unsigned char *p,unsigned pid,unsigned cc){memset(p,255,188);p[0]=0x47;p[1]=pid>>8;p[2]=pid;p[3]=0x10|cc;}
static unsigned char factory_output[3][188];
static unsigned factory_count;
static struct handback factory_scan;
static ssize_t factory_write(int fd,const void *p,size_t n){
 if(report[87]==1||report[87]==2){
  CHECK(fd==17&&n==188&&factory_count<3);
  memcpy(factory_output[factory_count++],p,n);
 }
 return n;
}
static int factory_live(void *opaque,ssize_t (*emit)(void *,const void *,size_t),void *emit_opaque){
 CHECK(emit(emit_opaque,opaque,188)==188);
 return 0;
}
static void factory_null_test(struct replay_config c,unsigned char src[4][188]){
 unsigned char null_packet[188],malformed[188],out[188],clock[188],key[188];
 static const unsigned char nal[]={0,0,1,0x67,0,0,1,0x68,0,0,1,0x65};
 struct replay_timeline t={0};
 unsigned i;

 /* Match the padding packets in the captured factory prefix. */
 packet(null_packet,0x1fff,15);
 memset(null_packet+4,0xce,184);
 t.seen=15;t.cc[2]=5;t.has_pcr=1;t.pcr=100;t.ms=50;
 CHECK(tl_rewrite(&t,null_packet,out)<0);
 CHECK(!tl_rewrite_factory(&t,null_packet,out)&&!memcmp(out,null_packet,188));
 CHECK(!tl_observe(&t,out,500)&&t.pcr==100&&t.ms==50&&t.cc[2]==5&&t.seen==15);
 memcpy(malformed,null_packet,188);malformed[1]|=0x80;
 CHECK(tl_rewrite_factory(&t,malformed,out)<0&&hb_packet(&factory_scan,malformed)<0);
 memcpy(malformed,null_packet,188);malformed[3]=0x30;malformed[4]=1;malformed[5]=0x80;
 CHECK(tl_rewrite_factory(&t,malformed,out)<0&&hb_packet(&factory_scan,malformed)<0);
 packet(malformed,42,0);
 CHECK(tl_rewrite_factory(&t,malformed,out)<0&&hb_packet(&factory_scan,malformed)<0);

 /* Padding between video packets must preserve the recovery candidate. */
 CHECK(!hb_packet(&factory_scan,src[2]));
 CHECK(!hb_packet(&factory_scan,src[3])&&factory_scan.candidate&&factory_scan.bytes==188);
 CHECK(!hb_packet(&factory_scan,null_packet)&&factory_scan.candidate&&factory_scan.bytes==188);

 memset((void *)report,0,sizeof(report));
 memcpy(clock,src[2],188);tl_put_pcr(clock+6,0);
 c.live_run=factory_live;c.live_opaque=clock;c.native_write=factory_write;
 CHECK(!replay_init(&c));
 CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);
 for(i=0;i<4;i++)CHECK(replay_write_impl(17,src[i],188,22)==188);
 __atomic_store_n(&report[21],1,__ATOMIC_RELEASE);
 CHECK(replay_write_impl(17,src[2],188,22)==188);
 for(i=0;i<1500&&!report[87];i++){struct timespec delay={0,1000000};nanosleep(&delay,0);}
 CHECK(report[87]==1&&report[4]==RPL_DONE);
 CHECK(replay_write_impl(17,null_packet,188,22)==188&&report[87]==1&&!factory_count);
 CHECK(replay_write_impl(17,src[2],188,22)==188);
 memcpy(key,src[3],188);key[8]=0;key[9]=13+sizeof(nal);memcpy(key+23,nal,sizeof(nal));
 CHECK(replay_write_impl(17,key,188,22)==188&&report[87]==2&&factory_count==1);
 CHECK(replay_write_impl(17,null_packet,188,22)==188&&report[87]==2&&factory_count==2);
 CHECK(!memcmp(factory_output[1],null_packet,188));
 memcpy(clock,src[2],188);tl_put_pcr(clock+6,12001000);
 CHECK(replay_write_impl(17,clock,188,22)==188&&report[87]==2&&factory_count==3&&report[89]==3);
 CHECK(((tl_pcr(factory_output[2]+6)-tl_stamp(factory_output[0]+18))&TL_MASK)==1000);
 CHECK((factory_output[0][3]&15)==((src[3][3]+1)&15));
 tl_put_pcr(clock+6,12000999);
 CHECK(replay_write_impl(17,clock,188,22)==188&&report[87]==3&&report[91]==EPROTO&&factory_count==3);
 CHECK(!replay_close_impl(17,33));
 replay_stop();
 puts("REPLAY_FACTORY_NULL_PASS recovery_candidate=1 preserved_null=1 rejects_malformed=1 rejects_unknown_pid=1 continuous_pcr=1 rejects_backward_pcr=1");
}

int main(void){struct replay_timeline t={0},v;struct replay_config c={0};unsigned char src[4][188],out[188];uint64_t baseline;unsigned i;
 packet(src[0],0,7);packet(src[1],16,15);packet(src[2],4096,9);src[2][3]=0x29;src[2][4]=183;src[2][5]=16;memset(src[2]+6,0,6);src[2][10]=0x7e;tl_put_pcr(src[2]+6,12000000);
 packet(src[3],17,3);src[3][1]|=0x40;memcpy(src[3]+4,"\0\0\1\xe0\0\0\x80\xc0\x0a",9);src[3][13]=0x31;src[3][18]=0x11;tl_put_stamp(src[3]+13,12000001);tl_put_stamp(src[3]+18,12000000);
 CHECK(!tl_ready(&t,100));for(i=0;i<4;i++)CHECK(!tl_observe(&t,src[i],100));CHECK(tl_ready(&t,100));CHECK(!tl_ready(&t,1101));CHECK(!tl_start(&t,101));baseline=12000180;CHECK(t.offset==baseline);
 v=t;CHECK(!tl_rewrite(&v,src[3],out));CHECK((out[3]&15)==4);CHECK(tl_stamp(out+13)==12000001+baseline);CHECK(tl_stamp(out+18)==12000000+baseline);CHECK(!memcmp(out+23,src[3]+23,165));
 CHECK(!tl_rewrite(&v,src[1],out));CHECK((out[3]&15)==0);CHECK(!tl_rewrite(&v,src[2],out));CHECK((out[3]&15)==9&&tl_pcr(out+6)==12000000+baseline);
 v=t;CHECK(!tl_feed(&v,src[0],4,101)&&v.used==4&&!tl_ready(&v,101));CHECK(tl_start(&v,101)<0);CHECK(!tl_feed(&v,src[0]+4,184,101)&&!v.used&&tl_ready(&v,101));v=t;v.pcr=TL_MASK-80;v.ms=100;CHECK(!tl_start(&v,101)&&v.offset==99);CHECK(!tl_rewrite(&v,src[3],out));CHECK(tl_stamp(out+13)==12000100);
 memcpy(out,src[2],188);out[5]|=128;CHECK(tl_rewrite(&t,out,accepted[0])<0);memcpy(out,src[3],188);out[13]&=~1;CHECK(tl_rewrite(&t,out,accepted[0])<0);
 memset(file,0,sizeof(file));put(0,RPL_MAGIC);put(4,1);put(8,sizeof(file));put(12,1);put(16,4);put(20,0);put(32,0);put(36,4*188);
 /* Recorded timestamps begin at zero; only transport header fields may change. */
 memcpy(file+40,src,sizeof(src));tl_put_pcr(file+40+2*188+6,0);tl_put_stamp(file+40+3*188+13,1);tl_put_stamp(file+40+3*188+18,0);
 c.native_open=op;c.native_write=wr;c.native_close=cl;c.geometry=geo;c.file_bytes=file;c.file_size=sizeof(file);c.report=report;c.open_lr=11;c.write_lr=22;c.close_lr=33;c.timeline_required=1;
 CHECK(!replay_init(&c));CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);for(i=0;i<4;i++){CHECK(replay_write_impl(17,src[i],4,22)==4);CHECK(replay_write_impl(17,src[i]+4,184,22)==184);}CHECK(report[56]==15&&report[55]==1);CHECK(replay_write_impl(17,src[0],4,22)==4&&report[64]==4);__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);CHECK(replay_write_impl(17,src[0]+4,184,22)==184&&report[4]==RPL_READY&&!report[64]);
 /* Arm on a real source callback. The callback is suppressed after ownership. */
 CHECK(replay_write_impl(17,src[3],188,22)==188);
 for(i=0;i<1500&&report[4]!=RPL_DONE;i++){struct timespec delay={0,1000000};nanosleep(&delay,0);}
 CHECK(report[4]==RPL_DONE&&!report[5]&&written==4&&report[62]==4);baseline=(uint64_t)report[60]|((uint64_t)report[61]<<32);CHECK(baseline>=12000090&&baseline<=12090000);
 CHECK(tl_pcr(accepted[2]+6)==baseline);CHECK(tl_stamp(accepted[3]+13)==baseline+1&&tl_stamp(accepted[3]+18)==baseline);CHECK((accepted[0][3]&15)==8&&(accepted[1][3]&15)==0&&(accepted[3][3]&15)==4);
 CHECK(!memcmp(accepted[3]+23,file+40+3*188+23,165));CHECK(!replay_close_impl(17,33));CHECK(report[65]==RPL_DONE&&report[66]==4);CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);CHECK(((uint64_t)report[60]|((uint64_t)report[61]<<32))==baseline&&report[62]==4);replay_stop();factory_null_test(c,src);puts("REPLAY_TIMELINE_PASS live_clock=1 continuity=1 wrap33=1 malformed_refusal=1 worker=1 payload_unchanged=1 split_native_writes=1 packet_boundary=1");return 0;}
