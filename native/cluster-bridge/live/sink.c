#define _QNX_SOURCE 1
#include "sink.h"
#include "mux.h"
#include "deadline.h"
#include "startup.h"
#include "../../observer/launch/proc_guard.h"
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
struct meta_record {uint64_t timestamp,monotonic_ns;uint32_t offset,bytes,session,flags;};
struct metadata {uint32_t h[8];struct meta_record records[2048];};
struct live_sink {char token[33];uint32_t nonce[4],*report;volatile uint32_t *route;volatile uint32_t *nav;struct live_shared *q;struct metadata *meta;unsigned char *au;int video,sf,pf,prepared,have_frame,done,error;uint64_t prepared_ns,next_check;struct live_startup startup;unsigned char *startup_data,*startup_key;struct live_peer consumer;struct live_frame cached;pg_identity source,parent;};
static uint64_t clockns(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (uint64_t)t.tv_sec*1000000000ULL+t.tv_nsec;}
static void pause_ms(void){struct timespec t={0,1000000};nanosleep(&t,0);}
static void *mapping(const char *p,size_t n){int fd=open(p,O_CREAT|O_EXCL|O_RDWR,0600);void *m;if(fd<0)return 0;if(ftruncate(fd,n)){close(fd);return 0;}m=mmap(0,n,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);return m==MAP_FAILED?0:m;}
struct live_sink *live_sink_open(const char *token,volatile uint32_t *nav){struct live_sink *s;char p[128],hex[9];unsigned i;if(!token||strlen(token)!=32||strspn(token,"0123456789abcdef")!=32)return 0;s=calloc(1,sizeof(*s));if(!s)return 0;memcpy(s->token,token,33);s->nav=nav;s->video=-1;s->sf=s->pf=-1;for(i=0;i<4;i++){memcpy(hex,token+8*i,8);hex[8]=0;s->nonce[i]=strtoul(hex,0,16);}snprintf(p,sizeof(p),"/dev/shmem/delphi-live-%s.bin",token);s->q=mapping(p,sizeof(*s->q));snprintf(p,sizeof(p),"/dev/shmem/delphi-live-report-%s.bin",token);s->report=mapping(p,512);snprintf(p,sizeof(p),"/dev/shmem/delphi-live-timing-%s.bin",token);s->meta=mapping(p,sizeof(*s->meta));snprintf(p,sizeof(p),"/dev/shmem/delphi-live-video-%s.h264",token);s->video=open(p,O_CREAT|O_EXCL|O_WRONLY,0600);s->au=malloc(LIVE_AU_LIMIT);s->startup_data=malloc(STARTUP_BYTES);s->startup_key=malloc(LIVE_AU_LIMIT);startup_init(&s->startup,s->startup_data,s->startup_key);if(!s->q||!s->report||!s->meta||s->video<0||!s->au||!s->startup_data||!s->startup_key)return 0;s->report[0]=0x3152434c;s->report[1]=2;s->report[2]=512;s->report[3]=getpid();s->meta->h[0]=0x31544c43;s->meta->h[1]=1;s->meta->h[2]=getpid();s->meta->h[4]=32;s->meta->h[5]=2048;nav[67]=5;nav[86]=STARTUP_DELAY_MS;nav[102]=STARTUP_TARGET_DELAY_MS;nav[103]=STARTUP_PACE_NUMERATOR;nav[104]=STARTUP_PACE_DENOMINATOR;return s;}
/* Read-only, token scoped lifecycle evidence. Never manufacture a route event. */
static int route_stopped(struct live_sink *s){char p[128];struct stat st;int fd;volatile uint32_t *r=s->route;unsigned stops;uint64_t stop,prepared=s->prepared_ns/1000000ULL;if(!r){snprintf(p,sizeof(p),"/dev/shmem/delphi-route-policy-%s.bin",s->token);fd=open(p,O_RDONLY);if(fd<0)return 0;if(fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size!=512){close(fd);return 0;}r=mmap(0,512,PROT_READ,MAP_SHARED,fd,0);close(fd);if(r==MAP_FAILED)return 0;s->route=r;}if(r[0]!=0x31545052||r[1]!=3||r[2]!=512||r[3]!=(uint32_t)s->source.pid||r[6]!=(uint32_t)getpid()||r[114]!=1)return 0;stops=__atomic_load_n(&r[104],__ATOMIC_ACQUIRE);stop=(uint64_t)r[110]|(uint64_t)r[111]<<32;if(!stops||stops!=__atomic_load_n(&r[104],__ATOMIC_ACQUIRE)||stop<prepared||stop>clockns()/1000000ULL)return 0;s->nav[98]=stops;s->nav[99]=(uint32_t)stop;s->nav[100]=stop>>32;return 1;}
static int save(int fd,const void *p,size_t n){unsigned tries=0;size_t at=0;while(at<n&&tries++<32){ssize_t x=write(fd,(const char*)p+at,n-at);if(x<0&&errno==EINTR)continue;if(x<=0)return -1;at+=x;}return at==n?0:-1;}
/* Stop publication before draining the already-owned startup buffer. */
static int seal_input(struct live_sink *s){int rc=live_close(&s->consumer);if(rc&&!__atomic_load_n(&s->q->closed,__ATOMIC_ACQUIRE))return EPROTO;s->report[25]=1;return 0;}
static int finish(struct live_sink *s,int error,unsigned reason){uint64_t now=clockns();uint32_t *r=s->report;if(s->prepared){live_close(&s->consumer);r[22]=__atomic_load_n(&s->q->head,__ATOMIC_ACQUIRE);r[23]=r[22]-__atomic_load_n(&s->q->tail,__ATOMIC_ACQUIRE);}s->done=1;s->error=error;r[6]=error;r[19]=reason;r[17]=(uint32_t)now;r[18]=now>>32;s->nav[70]=r[9];s->nav[73]=error;s->nav[74]=reason;if(s->sf>=0)close(s->sf);if(s->pf>=0)close(s->pf);if(s->video>=0)close(s->video);s->sf=s->pf=s->video=-1;__atomic_store_n(&r[5],error?4:3,__ATOMIC_RELEASE);return error;}
int live_sink_poll(void *opaque){struct live_sink *s=opaque;uint32_t *r=s->report;uint64_t now=clockns();int rc;char expected[160];if(s->done)return -(s->error?s->error:ECANCELED);if(!now)return -finish(s,EIO,0);
 if(!s->prepared){if(__atomic_load_n(&s->q->magic,__ATOMIC_ACQUIRE)!=LIVE_MAGIC)return 0;s->sf=pg_open(s->q->producer_pid,0,&s->source);if(s->sf<0)return -finish(s,ESRCH,0);snprintf(expected,sizeof(expected),"/ramdisk/delphi-aa-observer_%s/AndroidAuto.original",s->token);
#ifndef LIVE_SINK_TEST
 if(strcmp(s->source.executable,expected)||s->source.base_address!=0x100000)return -finish(s,EPERM,0);
#endif
 s->pf=pg_open(s->source.parent,0,&s->parent);if(s->pf<0)return -finish(s,ESRCH,0);
#ifndef LIVE_SINK_TEST
 if(strcmp(s->parent.executable,"/proc/boot/procman"))return -finish(s,EPERM,0);
#endif
 if(pg_matches(s->sf,&s->source)||pg_matches(s->pf,&s->parent)||live_bind(&s->consumer,s->q,sizeof(*s->q),s->nonce,s->source.pid,getpid()))return -finish(s,EPROTO,0);
 s->prepared=1;s->prepared_ns=now;r[15]=(uint32_t)now;r[16]=now>>32;r[4]=s->source.pid;s->meta->h[3]=s->source.pid;s->nav[71]=s->source.pid;s->nav[72]=1;__atomic_store_n(&r[5],1,__ATOMIC_RELEASE);
 }
 if(now-s->prepared_ns>=LIVE_WAIT_NS)return -finish(s,ETIMEDOUT,4);
 if(now>=s->next_check){s->next_check=now+100000000ULL;if(pg_matches(s->sf,&s->source)||pg_matches(s->pf,&s->parent)){finish(s,0,1);return -ECANCELED;}}
 r[9]=__atomic_load_n(&s->q->dropped,__ATOMIC_ACQUIRE);r[10]=__atomic_load_n(&s->q->request_idr,__ATOMIC_ACQUIRE);if(r[9])return -finish(s,ENOBUFS,0);
 if(s->have_frame)return 1;
 rc=live_consume(&s->consumer,s->au,LIVE_AU_LIMIT,&s->cached);if(rc<0)return -finish(s,EPROTO,0);if(rc)s->have_frame=1;return rc;
}
int live_sink_run(void *opaque,ssize_t (*emit)(void *,const void *,size_t),void *output){struct live_sink *s=opaque;struct live_deadline d;struct live_mux mux;struct live_frame frame;uint64_t start=clockns();uint32_t *r=s->report;int error=0,accepting=1,source_ended=0;unsigned reason=0;if(!s->prepared||!s->have_frame||!start)return finish(s,EINVAL,0);live_deadline_init(&d,start);live_mux_init(&mux,emit,output);
 while(1){uint64_t now=clockns(),ms;int rc=0,bootstrap;unsigned bytes,flags;if(!now){error=EIO;break;}ms=(now-start)/1000000ULL;if(accepting&&route_stopped(s)){accepting=0;reason=5;s->nav[101]=s->startup.head-s->startup.tail;/* Stop immediately; queued projected pictures must not outlive disconnect. */break;}if(accepting){unsigned stop=live_deadline_reason(&d,now);if(stop){accepting=0;reason=stop;error=seal_input(s);if(error)break;}}
  if(accepting){if(s->have_frame){frame=s->cached;s->have_frame=0;rc=1;}else rc=live_consume(&s->consumer,s->au,LIVE_AU_LIMIT,&frame);if(rc<0){error=EPROTO;break;}if(source_ended&&!rc){accepting=0;reason=1;}}
  r[9]=__atomic_load_n(&s->q->dropped,__ATOMIC_ACQUIRE);r[10]=__atomic_load_n(&s->q->request_idr,__ATOMIC_ACQUIRE);if(r[9]){error=ENOBUFS;break;}
  if(rc){struct meta_record *m;now=clockns();if(!now){error=EIO;break;}ms=(now-start)/1000000ULL;if(r[7]>=2048||frame.bytes>8388608u-r[8]){accepting=0;reason=3;rc=0;r[24]++;error=seal_input(s);if(error)break;}else{if(save(s->video,s->au,frame.bytes)){error=EIO;break;}m=&s->meta->records[r[7]];m->timestamp=frame.timestamp;m->monotonic_ns=now;m->offset=r[8];m->bytes=frame.bytes;m->session=frame.session;m->flags=frame.flags;if(!r[7]){live_deadline_first(&d,now,
#ifdef LIVE_SINK_TEST
 1
#else
 30
#endif
 );r[11]=(uint32_t)frame.timestamp;r[12]=frame.timestamp>>32;}r[13]=(uint32_t)frame.timestamp;r[14]=frame.timestamp>>32;r[8]+=frame.bytes;r[7]++;__atomic_store_n(&s->meta->h[6],r[7],__ATOMIC_RELEASE);s->nav[68]=r[7];s->nav[69]=r[8];__atomic_store_n(&r[5],2,__ATOMIC_RELEASE);if(startup_push(&s->startup,s->au,frame.bytes,frame.flags,ms)){error=ENOBUFS;s->nav[85]=s->startup.overflows;break;}}}
  rc=startup_pop(&s->startup,ms,s->au,LIVE_AU_LIMIT,&bytes,&flags,&bootstrap);if(rc<0){error=EPROTO;break;}if(rc&&live_mux_push(&mux,s->au,bytes,flags,ms)!=1){error=s->nav[5]?s->nav[5]:EIO;break;}s->nav[80]=s->startup.repeats;s->nav[81]=s->startup.key_bytes;s->nav[82]=s->startup.peak_bytes;s->nav[83]=s->startup.peak_frames;s->nav[84]=s->startup.emitted;s->nav[85]=s->startup.overflows;
  if(!accepting&&!startup_pending(&s->startup))break;
  if(now>=s->next_check){s->next_check=now+100000000ULL;if(pg_matches(s->sf,&s->source)||pg_matches(s->pf,&s->parent))source_ended=1;}
  if(live_mux_tick(&mux,ms)){error=s->nav[5]?s->nav[5]:EPIPE;break;}pause_ms();
 }
 return finish(s,error,reason);
}
