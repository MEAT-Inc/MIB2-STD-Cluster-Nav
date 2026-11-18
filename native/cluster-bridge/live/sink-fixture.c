#define _QNX_SOURCE 1
#include "sink.h"
#include "../replay/replay.h"
#include "../replay/timeline.h"
#include <sys/mman.h>
#include <sys/wait.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"LIVE_SINK_FAIL line=%d errno=%d\n",__LINE__,errno);exit(1);}}while(0)
#include <errno.h>
static volatile uint32_t report[128];
static unsigned char file[32+8+4*188],src[4][188];
static unsigned char output_capture[188*128];
static unsigned pictures,packets;static uint64_t minimum;
static int op(const char *p,int f,...){(void)p;(void)f;return 17;}
static int cl(int f){(void)f;return 0;}
static ssize_t wr(int fd,const void *data,size_t n){const unsigned char *p=data;if(report[4]==RPL_ACTIVE){unsigned off=4,afc=(p[3]>>4)&3;CHECK(fd==17&&n==188&&p[0]==0x47);packets++;if(afc&2)off=5+p[4];if((p[1]&0x1f)==0&&p[2]==17&&(p[1]&0x40)){CHECK(off+19+18<=188);CHECK(tl_stamp(p+off+9)>=minimum);CHECK(!memcmp(p+off+19,"\0\0\1\x67\x42\x80\x1f\0\0\1\x68\xee\0\0\1\x65\x88\x84",18));pictures++;}}return n;}
static int geometry(void *p,int fd){(void)p;return fd==17;}
static void pause_ms(unsigned n){struct timespec t={n/1000,(n%1000)*1000000};nanosleep(&t,0);}
static void packet(unsigned char *p,unsigned pid){memset(p,255,188);p[0]=0x47;p[1]=pid>>8;p[2]=pid;p[3]=0x13;}
int main(void){const char *token="22222222222222222222222222222222";struct replay_config c={0};struct replay_timeline t={0};unsigned char rewritten[188];struct live_sink *sink;pid_t child;int status,fd;unsigned i;struct live_shared *q;struct live_peer producer;const uint32_t nonce[4]={0x22222222,0x22222222,0x22222222,0x22222222};unsigned char codec[]={0,0,1,0x67,0x42,0x80,0x1f,0,0,1,0x68,0xee},au[]={0,0,1,0x65,0x88,0x84};char path[160];
 sink=live_sink_open(token,report);CHECK(sink);snprintf(path,sizeof(path),"/dev/shmem/delphi-live-%s.bin",token);fd=open(path,O_RDWR);CHECK(fd>=0);q=mmap(0,sizeof(*q),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);CHECK(q!=MAP_FAILED);
 child=fork();CHECK(child>=0);if(!child){pause_ms(200);CHECK(!live_init(q,sizeof(*q),nonce,getpid(),getppid()));CHECK(!live_bind(&producer,q,sizeof(*q),nonce,getpid(),getppid()));pause_ms(200);for(i=0;i<20;i++){CHECK(live_publish(&producer,codec,sizeof(codec),au,sizeof(au),37,(uint64_t)i*10000)==1);pause_ms(5);}_exit(0);}
 packet(src[0],0);packet(src[1],16);packet(src[2],4096);src[2][3]=0x23;src[2][4]=183;src[2][5]=16;memset(src[2]+6,0,6);src[2][10]=0x7e;tl_put_pcr(src[2]+6,12000000);minimum=12000000;
 packet(src[3],17);src[3][1]|=64;memcpy(src[3]+4,"\0\0\1\xe0\0\0\x80\xc0\x0a",9);src[3][13]=0x31;src[3][18]=0x11;tl_put_stamp(src[3]+13,12000001);tl_put_stamp(src[3]+18,12000000);
 {uint32_t h[8]={RPL_MAGIC,1,sizeof(file),1,4,0,0,0};memcpy(file,h,32);h[0]=0;h[1]=4*188;memcpy(file+32,h,8);memcpy(file+40,src,sizeof(src));}
 for(i=0;i<4;i++)CHECK(!tl_feed(&t,src[i],188,100));CHECK(!tl_start(&t,100)&&!tl_rewrite(&t,src[3],rewritten));
 c.native_open=op;c.native_write=wr;c.native_close=cl;c.geometry=geometry;c.report=report;c.open_lr=11;c.write_lr=22;c.close_lr=33;c.file_bytes=file;c.file_size=sizeof(file);c.timeline_required=1;c.live_capture=output_capture;c.live_capture_capacity=sizeof(output_capture);c.live_run=live_sink_run;c.live_poll=live_sink_poll;c.live_opaque=sink;CHECK(!replay_init(&c));CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);for(i=0;i<4;i++)CHECK(replay_write_impl(17,src[i],188,22)==188);__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);CHECK(replay_write_impl(17,src[3],188,22)==188);pause_ms(100);CHECK(report[4]==RPL_READY&&!packets&&!pictures);CHECK(!replay_close_impl(17,33));CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);for(i=0;i<4;i++)CHECK(replay_write_impl(17,src[i],188,22)==188);pause_ms(200);CHECK(report[4]==RPL_READY&&!packets&&!pictures&&report[72]==1);for(i=0;i<2500&&(report[4]==RPL_READY||report[4]==RPL_ACTIVE);i++)pause_ms(1);CHECK(report[4]==RPL_DONE&&!report[5]&&report[68]==20&&report[69]==360&&report[71]==(uint32_t)child&&report[72]==1&&!report[70]&&!report[73]&&pictures==23&&report[80]==3&&report[84]==20&&report[86]==1000&&report[10]==packets&&report[62]==packets&&report[75]==188*packets&&output_capture[0]==0x47);CHECK(waitpid(child,&status,0)==child&&WIFEXITED(status)&&!WEXITSTATUS(status));CHECK(!replay_close_impl(17,33));pause_ms(100);CHECK(report[4]==RPL_DONE&&!report[5]);replay_stop();puts("LIVE_NAV_SINK_QNX_PASS startup_bootstrap_frames=3 source_frames_preserved=20 queue_owned_frames=20 native_descriptor_only=1 no_empty_output_before_phone=1 timeline_rewrite=1 original_au_bytes=1 zero_drops=1 source_identity=1 no_recorded_packets=1 completed_close_preserves_done=1 first_frame_gate=1 native_passthrough_before_phone=1 prephone_reopen=1");return 0;}
