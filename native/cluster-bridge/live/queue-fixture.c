#define _GNU_SOURCE 1
#define _QNX_SOURCE 1
#include "queue.h"
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"LIVE_QUEUE_FAIL line=%d\n",__LINE__);exit(1);}}while(0)
static const uint32_t nonce[4]={1,2,3,4};
static const unsigned char codec[]={0,0,0,1,0x67,0x42,0x80,0x1f,0,0,0,1,0x68,0xee,0x21};
static unsigned char idr[]={0,0,0,1,0x65,0x88,0x84,0x21,0x7f};
static const unsigned char predicted[]={0,0,1,0x41,0x9a,0x22,0x7f};
static void pause_ms(void){struct timespec t={0,1000000};nanosleep(&t,0);}
int main(void){
 struct live_shared *q=mmap(0,sizeof(*q),PROT_READ|PROT_WRITE,MAP_SHARED|MAP_ANON,-1,0);struct live_peer producer,reader,bad;struct live_frame f;unsigned char *out=malloc(LIVE_AU_LIMIT);uint32_t other[4]={1,2,3,5};unsigned i;pid_t child;int done=0,status=0;uint64_t last=0;unsigned received=0;
 CHECK(q!=MAP_FAILED&&out);CHECK(!live_init(q,sizeof(*q),nonce,101,202));CHECK(!live_bind(&producer,q,sizeof(*q),nonce,101,202));CHECK(!live_bind(&reader,q,sizeof(*q),nonce,101,202));
 CHECK(live_bind(&bad,q,sizeof(*q)-1,nonce,101,202)<0&&live_publish(&bad,0,0,idr,sizeof(idr),0,0)<0);CHECK(live_bind(&bad,q,sizeof(*q),other,101,202)<0);CHECK(live_bind(&bad,q,sizeof(*q),nonce,102,202)<0);
 CHECK(live_publish(&producer,0,0,predicted,sizeof(predicted),7,1)==1);CHECK(!live_consume(&reader,out,LIVE_AU_LIMIT,&f)&&q->request_idr);
 CHECK(live_publish(&producer,0,0,idr,sizeof(idr),7,2)==1);CHECK(!live_consume(&reader,out,LIVE_AU_LIMIT,&f));
 CHECK(live_publish(&producer,codec,sizeof(codec),idr,sizeof(idr),7,UINT64_C(0x123456789abcdef0))==1);idr[8]=0x55;CHECK(live_consume(&reader,out,LIVE_AU_LIMIT,&f)==1);CHECK(f.timestamp==UINT64_C(0x123456789abcdef0)&&f.bytes==sizeof(codec)+sizeof(idr)&&out[f.bytes-1]==0x7f&&!q->request_idr);idr[8]=0x7f;
 for(i=0;i<LIVE_CAPACITY;i++)CHECK(live_publish(&producer,0,0,predicted,sizeof(predicted),7,i)==1);
 CHECK(live_publish(&producer,0,0,predicted,sizeof(predicted),7,9)==0&&q->dropped==1);CHECK(!live_consume(&reader,out,LIVE_AU_LIMIT,&f)&&q->tail==q->head);
 CHECK(live_publish(&producer,0,0,predicted,sizeof(predicted),7,10)==1&&!live_consume(&reader,out,LIVE_AU_LIMIT,&f));
 CHECK(live_publish(&producer,codec,sizeof(codec),idr,sizeof(idr),7,11)==1&&live_consume(&reader,out,LIVE_AU_LIMIT,&f)==1);
 CHECK(live_publish(&producer,0,0,predicted,sizeof(predicted),8,12)==1&&!live_consume(&reader,out,LIVE_AU_LIMIT,&f));
 CHECK(live_publish(&producer,codec,sizeof(codec),idr,sizeof(idr),8,13)==1&&live_consume(&reader,out,LIVE_AU_LIMIT,&f)==1);
 q->head=q->tail=UINT_MAX-1;
 for(i=0;i<3;i++){CHECK(live_publish(&producer,codec,sizeof(codec),idr,sizeof(idr),8,i+14)==1);CHECK(live_consume(&reader,out,LIVE_AU_LIMIT,&f)==1&&f.timestamp==i+14);}
 CHECK(q->head==1&&q->tail==1);
 CHECK(live_publish(&producer,0,0,idr,LIVE_AU_LIMIT+1u,8,1)<0);
 CHECK(live_publish(&producer,predicted,sizeof(predicted),idr,sizeof(idr),8,1)<0);
 CHECK(!live_consume(&reader,out,LIVE_AU_LIMIT,&f));CHECK(live_publish(&producer,codec,sizeof(codec),idr,sizeof(idr),8,14)==1);q->slots[q->tail%LIVE_CAPACITY].bytes=LIVE_AU_LIMIT+1;CHECK(live_consume(&reader,out,LIVE_AU_LIMIT,&f)<0&&q->request_idr);
 CHECK(!live_close(&reader)&&live_publish(&producer,0,0,predicted,sizeof(predicted),8,15)<0&&live_consume(&reader,out,LIVE_AU_LIMIT,&f)<0);
 puts("LIVE_QUEUE_POLICY_PASS owned_copy=1 nonce_pid=1 overflow_resync=1 codec_idr_gate=1 session_gate=1 wrap32=1 bounds=1 close=1");fflush(0);
 __atomic_store_n(&q->magic,0,__ATOMIC_RELEASE);child=fork();CHECK(child>=0);
 if(!child){
  struct live_peer writer;unsigned spins;pid_t own=getpid(),parent=getppid();
  for(spins=0;spins<5000&&__atomic_load_n(&q->magic,__ATOMIC_ACQUIRE)!=LIVE_MAGIC;spins++)pause_ms();
  if(live_bind(&writer,q,sizeof(*q),nonce,(uint32_t)own,(uint32_t)parent))_exit(2);
  for(i=0;i<500;i++){int key=i%5==0;int rc=live_publish(&writer,key?codec:0,key?sizeof(codec):0,key?idr:predicted,key?sizeof(idr):sizeof(predicted),9,i);if(rc<0)_exit(3);pause_ms();}
  _exit(0);
 }
 CHECK(!live_init(q,sizeof(*q),nonce,(uint32_t)child,(uint32_t)getpid()));CHECK(!live_bind(&reader,q,sizeof(*q),nonce,(uint32_t)child,(uint32_t)getpid()));
 for(i=0;i<10000;i++){
  int rc=live_consume(&reader,out,LIVE_AU_LIMIT,&f);CHECK(rc>=0);
  if(rc){int key=(f.flags&LIVE_IDR)!=0;CHECK(f.session==9&&(!received||f.timestamp>last)&&f.timestamp<500);CHECK(f.bytes==(key?sizeof(codec)+sizeof(idr):sizeof(predicted)));CHECK(!memcmp(out,key?codec:predicted,key?sizeof(codec):sizeof(predicted)));last=f.timestamp;received++;}
  if(!done){pid_t x=waitpid(child,&status,WNOHANG);CHECK(x==0||x==child);if(x==child)done=1;}
  if(done&&q->head==q->tail)break;
  pause_ms();
 }
 CHECK(done&&WIFEXITED(status)&&!WEXITSTATUS(status)&&received>=20);CHECK(!live_close(&reader));free(out);munmap(q,sizeof(*q));puts("LIVE_QUEUE_PROCESS_PASS cross_process=1 acquire_release=1 sequence=1 bounded_backpressure=1");return 0;
}
