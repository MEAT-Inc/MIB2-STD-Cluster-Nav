#define _POSIX_C_SOURCE 200809L
#include "replay.h"
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <stdlib.h>
static volatile uint32_t report[128];
static unsigned char capture[2];
static unsigned char file[32+8+376+8+188];
static unsigned sent,zero_mode,short_mode,forwarded;
static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"REPLAY_FAIL line=%d\n",__LINE__);exit(1);}}while(0)
static void put(unsigned at,unsigned v){file[at]=v;file[at+1]=v>>8;file[at+2]=v>>16;file[at+3]=v>>24;}
static int mock_open(const char *s,int f,...){(void)s;(void)f;errno=EDOM;return 17;}
static int mock_close(int f){if(f==90)CHECK(replay_write_impl(91,"x",1,0)==7);errno=ERANGE;return 23;}
static ssize_t mock_write(int f,const void *p,size_t n){ssize_t r;if(f==90||(f==17&&n==188))CHECK(replay_write_impl(91,"x",1,0)==7);pthread_mutex_lock(&lock);if(n==188&&((const unsigned char *)p)[0]==0x47){if(zero_mode)r=0;else if(short_mode)r=9;else {++sent;r=188;}}else {++forwarded;r=7;}pthread_mutex_unlock(&lock);errno=E2BIG;return r;}
static int geometry(void *p,int f){return __atomic_load_n((int *)p,__ATOMIC_ACQUIRE)&&f==17;}
static void pause_ms(unsigned ms){struct timespec t={ms/1000,(ms%1000)*1000000};nanosleep(&t,0);}
static void wait_status(unsigned state){unsigned i;for(i=0;i<500;i++){pause_ms(1);if(report[RP_STATUS]==state)return;}CHECK(0);}
static void inspect(void *opaque,volatile uint32_t *r){(void)opaque;CHECK(replay_write_impl(91,"x",1,0)==7);__atomic_fetch_add(&r[40],1,__ATOMIC_RELAXED);}
int main(void){int sane=0;struct replay_config cfg;memset(file,0,sizeof(file));put(0,RPL_MAGIC);put(4,1);put(8,sizeof(file));put(12,2);put(16,3);put(20,30);put(32,0);put(36,376);file[40]=file[228]=0x47;put(416,30);put(420,188);file[424]=0x47;memset(&cfg,0,sizeof(cfg));cfg.native_open=mock_open;cfg.native_write=mock_write;cfg.native_close=mock_close;cfg.geometry=geometry;cfg.opaque=&sane;cfg.file_bytes=file;cfg.file_size=sizeof(file);cfg.report=report;cfg.capture=capture;cfg.capture_capacity=sizeof(capture);cfg.open_lr=11;cfg.write_lr=22;cfg.close_lr=33;
 cfg.inspect=inspect;CHECK(!replay_init(&cfg));{unsigned i;for(i=0;i<1400&&!__atomic_load_n(&report[RP_INSPECT_HEARTBEAT],__ATOMIC_RELAXED);i++)pause_ms(1);CHECK(report[40]>0&&report[RP_INSPECT_HEARTBEAT]>0);}CHECK(replay_write_impl(90,"x",1,0)==7&&errno==E2BIG);CHECK(replay_close_impl(90,0)==23&&errno==ERANGE);CHECK(report[RP_HOOK_WRITES]>=4&&report[RP_HOOK_CLOSES]==1);CHECK(replay_open_impl("other",1,0,11)==17&&errno==EDOM);CHECK(replay_write_impl(17,"x",1,22)==7&&errno==E2BIG);CHECK(!report[RP_WRITES]);CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);CHECK(replay_write_impl(17,"x",1,22)==7);CHECK(report[RP_STATUS]==RPL_READY);CHECK(replay_write_impl(17,"yz",2,22)==7);CHECK(report[RP_CAPTURE_BYTES]==2&&capture[0]=='x'&&capture[1]=='y');CHECK(report[RP_NATIVE_WRITES]==2&&report[RP_NATIVE_BYTES]==14);__atomic_store_n(&sane,1,__ATOMIC_RELEASE);__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);errno=EDOM;CHECK(replay_write_impl(17,"x",1,22)==1&&errno==EDOM);wait_status(RPL_DONE);CHECK(sent==3&&report[RP_PACKETS]==3&&report[RP_GROUPS]==2);CHECK(report[RP_NATIVE_WRITES]==5&&report[RP_NATIVE_BYTES]==578&&report[RP_CAPTURE_BYTES]==2);CHECK(replay_write_impl(17,"x",1,99)==1);CHECK(report[RP_BAD_CALLERS]==1&&report[RP_STATUS]==RPL_ERROR);CHECK(replay_close_impl(17,33)==23&&errno==ERANGE);CHECK(replay_write_impl(17,"x",1,22)==7);replay_stop();
 memset((void *)report,0,sizeof(report));zero_mode=1;CHECK(!replay_init(&cfg));__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);CHECK(replay_write_impl(17,"x",1,22)==1);wait_status(RPL_ERROR);CHECK(report[RP_ZERO]==32&&report[RP_PACKETS]==0);CHECK(replay_write_impl(17,"x",1,22)==1);CHECK(replay_close_impl(17,33)==23);zero_mode=0;short_mode=1;replay_stop();memset((void *)report,0,sizeof(report));CHECK(!replay_init(&cfg));__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);CHECK(replay_write_impl(17,"x",1,22)==1);wait_status(RPL_ERROR);CHECK(report[RP_PACKETS]==0);replay_stop();
 memset((void *)report,0,sizeof(report));short_mode=0;__atomic_store_n(&sane,0,__ATOMIC_RELEASE);CHECK(!replay_init(&cfg));__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);CHECK(replay_write_impl(17,"x",1,99)==7);__atomic_store_n(&sane,1,__ATOMIC_RELEASE);CHECK(replay_write_impl(17,"x",1,22)==7);CHECK(report[RP_STATUS]==RPL_READY);replay_stop();
 /* Explicit arm starts replay without a first source frame. */
 memset((void *)report,0,sizeof(report));CHECK(!replay_init(&cfg));CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);pause_ms(1100);CHECK(report[RP_STATUS]==RPL_READY&&!report[RP_PACKETS]&&!report[RP_WRITES]);__atomic_store_n(&report[21],1,__ATOMIC_RELEASE);{unsigned i;for(i=0;i<1500&&report[RP_STATUS]!=RPL_DONE;i++)pause_ms(1);CHECK(report[RP_STATUS]==RPL_DONE&&report[RP_PACKETS]==3&&!report[RP_WRITES]);}CHECK(replay_write_impl(17,"x",1,22)==1);CHECK(report[RP_SUPPRESSED]==1);CHECK(replay_close_impl(17,33)==23);CHECK(replay_open_impl("/dev/transport_server/spawn/isoTX",1,0,11)==17);pause_ms(1100);CHECK(report[RP_PACKETS]==3);replay_stop();puts("REPLAY_ARMED_DESCRIPTOR_PASS prearm_passive=1 no_source_write=1 attempt_once=1 eof_mute=1");file[40]=0;CHECK(replay_init(&cfg)==-1);puts("REPLAY_FIXTURE_PASS forwarding_errno=1 unrelated_reentrant=1 idle_inspect=1 native_ownership=1 schedule=1 eof_mute=1 zero_short=1 fd_reuse=1 unknown_caller=1");return 0;}


