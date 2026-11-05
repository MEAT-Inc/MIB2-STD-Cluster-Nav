#define _QNX_SOURCE 1
#include "queue.h"
#include "../../observer/launch/proc_guard.h"
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#define META_CAP 2048u
struct meta_record {uint64_t timestamp,monotonic_ns;uint32_t offset,bytes,session,flags;};
struct metadata {uint32_t h[8];struct meta_record records[META_CAP];};
_Static_assert(sizeof(struct meta_record)==32,"live timing ABI");
static uint64_t now_ns(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (uint64_t)t.tv_sec*1000000000ULL+t.tv_nsec;}
static void pause_ms(void){struct timespec t={0,1000000};nanosleep(&t,0);}
static int write_all(int fd,const void *p,size_t n){unsigned tries=0;size_t at=0;while(at<n&&tries++<32){ssize_t x=write(fd,(const char*)p+at,n-at);if(x<0&&errno==EINTR)continue;if(x<=0)return -1;at+=(size_t)x;}return at==n?0:-1;}
static int make(const char *path,size_t bytes,void **mapped){int fd=open(path,O_CREAT|O_EXCL|O_RDWR,0600);if(fd<0)return -1;if(ftruncate(fd,bytes)){close(fd);return -1;}*mapped=mmap(0,bytes,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(*mapped==MAP_FAILED){*mapped=0;return -1;}return 0;}
static int token_ok(const char *s){return s&&strlen(s)==32&&strspn(s,"0123456789abcdef")==32;}
static int sample_nav(pid_t nav,int out,int errors){char number[24];pid_t child;int status;snprintf(number,sizeof(number),"%u",(unsigned)nav);child=fork();if(!child){if(dup2(out,STDOUT_FILENO)<0||dup2(errors,STDERR_FILENO)<0)_exit(126);execl("./nav_snapshot","nav_snapshot",number,(char*)0);_exit(127);}if(child<0)return -1;while(waitpid(child,&status,0)<0)if(errno!=EINTR)return -1;return WIFEXITED(status)&&!WEXITSTATUS(status)?0:-1;}
static int run(const char *token,pid_t producer,unsigned seconds,pid_t nav,int testing){
 char qpath[128],rpath[128],vpath[128],mpath[128],npath[128],epath[128],expected[160];uint32_t nonce[4],*r=0;struct live_shared *q=0;struct metadata *m=0;struct live_peer consumer;struct live_frame frame;pg_identity peer,parent;int peerfd=-1,parentfd=-1,out=-1,navout=-1,naverr=-1,result=3;unsigned i,reason=0,loops=0;uint64_t start,end,next_sample=0;unsigned char *owned=0;
 if(!token_ok(token)||producer<=0||seconds<1||seconds>30)return 2;
 for(i=0;i<4;i++){char text[9];memcpy(text,token+i*8,8);text[8]=0;nonce[i]=(uint32_t)strtoul(text,0,16);}
 peerfd=pg_open(producer,0,&peer);if(peerfd<0)return 3;
 snprintf(expected,sizeof(expected),"/ramdisk/delphi-aa-observer_%s/AndroidAuto.original",token);
#ifndef LIVE_CAPTURE_TEST
 (void)testing;
 if(strcmp(peer.executable,expected)||peer.base_address!=0x100000)goto done;
#else
 if(!testing&&(strcmp(peer.executable,expected)||peer.base_address!=0x100000))goto done;
#endif
 parentfd=pg_open(peer.parent,0,&parent);if(parentfd<0)goto done;
#ifndef LIVE_CAPTURE_TEST
 if(strcmp(parent.executable,"/proc/boot/procman"))goto done;
#else
 if(!testing&&strcmp(parent.executable,"/proc/boot/procman"))goto done;
#endif
 if(pg_matches(peerfd,&peer)||pg_matches(parentfd,&parent))goto done;
 snprintf(qpath,sizeof(qpath),"/dev/shmem/delphi-live-%s.bin",token);snprintf(rpath,sizeof(rpath),"/dev/shmem/delphi-live-report-%s.bin",token);snprintf(vpath,sizeof(vpath),"/dev/shmem/delphi-live-video-%s.h264",token);snprintf(mpath,sizeof(mpath),"/dev/shmem/delphi-live-timing-%s.bin",token);
 if(make(rpath,512,(void**)&r))goto done;
 r[0]=0x3152434c;r[1]=1;r[2]=512;r[3]=getpid();r[4]=producer;
 if(make(qpath,sizeof(*q),(void**)&q)||make(mpath,sizeof(*m),(void**)&m))goto done;
 if(nav){snprintf(npath,sizeof(npath),"/dev/shmem/delphi-live-nav-%s.jsonl",token);snprintf(epath,sizeof(epath),"/dev/shmem/delphi-live-nav-%s.errors.txt",token);navout=open(npath,O_CREAT|O_EXCL|O_WRONLY,0600);naverr=open(epath,O_CREAT|O_EXCL|O_WRONLY,0600);if(navout<0||naverr<0)goto done;}
 out=open(vpath,O_WRONLY|O_CREAT|O_EXCL,0600);owned=malloc(LIVE_AU_LIMIT);if(out<0||!owned)goto done;
 m->h[0]=0x31544c43;m->h[1]=1;m->h[2]=getpid();m->h[3]=producer;m->h[4]=32;m->h[5]=META_CAP;
 if(live_init(q,sizeof(*q),nonce,(uint32_t)producer,(uint32_t)getpid())||live_bind(&consumer,q,sizeof(*q),nonce,(uint32_t)producer,(uint32_t)getpid()))goto done;
 start=now_ns();if(!start)goto done;end=start+(uint64_t)seconds*1000000000ULL;r[15]=(uint32_t)start;r[16]=start>>32;__atomic_store_n(&r[5],1,__ATOMIC_RELEASE);
 while(1){uint64_t current=now_ns();if(!current){r[6]=EIO;goto stop;}if(current>=end)break;
  int rc=live_consume(&consumer,owned,LIVE_AU_LIMIT,&frame);if(rc<0){r[6]=EPROTO;goto stop;}
  if(rc){struct meta_record *record;
   if(r[7]>=META_CAP||frame.bytes>8388608u-r[8]){reason=3;break;}
   if(write_all(out,owned,frame.bytes)){r[6]=errno?errno:EIO;goto stop;}
   record=&m->records[r[7]];record->timestamp=frame.timestamp;record->monotonic_ns=now_ns();record->offset=r[8];record->bytes=frame.bytes;record->session=frame.session;record->flags=frame.flags;
   if(!r[7]){r[11]=(uint32_t)frame.timestamp;r[12]=frame.timestamp>>32;}r[13]=(uint32_t)frame.timestamp;r[14]=frame.timestamp>>32;r[8]+=frame.bytes;r[7]++;__atomic_store_n(&m->h[6],r[7],__ATOMIC_RELEASE);__atomic_store_n(&r[5],2,__ATOMIC_RELEASE);
  }
  r[9]=__atomic_load_n(&q->dropped,__ATOMIC_ACQUIRE);r[10]=__atomic_load_n(&q->request_idr,__ATOMIC_ACQUIRE);
  if(nav&&current>=next_sample){if(sample_nav(nav,navout,naverr))r[21]++;r[20]++;next_sample=current+1000000000ULL;}
  if(++loops%100==0&&(pg_matches(peerfd,&peer)||pg_matches(parentfd,&parent))){reason=1;break;}
  pause_ms();
 }
 if(!reason){reason=2;}result=0;
 stop:(void)live_close(&consumer);r[19]=reason;start=now_ns();r[17]=(uint32_t)start;r[18]=start>>32;
 done:if(result&&r&&!r[6])r[6]=errno?errno:EINVAL;if(out>=0)close(out);if(navout>=0)close(navout);if(naverr>=0)close(naverr);free(owned);if(r)__atomic_store_n(&r[5],result?4:3,__ATOMIC_RELEASE);if(q&&q!=MAP_FAILED){munmap(q,sizeof(*q));unlink(qpath);}if(m&&m!=MAP_FAILED)munmap(m,sizeof(*m));if(r&&r!=MAP_FAILED)munmap(r,512);if(peerfd>=0)close(peerfd);if(parentfd>=0)close(parentfd);return result;
}
#ifdef LIVE_CAPTURE_TEST
static int self_test(void){
 const char *token="11111111111111111111111111111111";uint32_t nonce[4]={0x11111111,0x11111111,0x11111111,0x11111111};pid_t p;int rc,status,fd;unsigned i;char path[160];uint32_t report[128];struct stat st;
 p=fork();if(p<0)return 1;
 if(!p){struct live_shared *q;struct live_peer writer;unsigned char codec[]={0,0,1,0x67,0x42,0x80,0x1f,0,0,1,0x68,0xee},idr[]={0,0,1,0x65,0x88,0x84};snprintf(path,sizeof(path),"/dev/shmem/delphi-live-%s.bin",token);
  for(i=0;i<5000;i++){fd=open(path,O_RDWR);if(fd>=0){struct stat qs;if(!fstat(fd,&qs)&&(uint64_t)qs.st_size==sizeof(*q))break;close(fd);fd=-1;}pause_ms();}if(fd<0)_exit(2);q=mmap(0,sizeof(*q),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);close(fd);if(q==MAP_FAILED)_exit(3);
  for(i=0;i<5000&&__atomic_load_n(&q->magic,__ATOMIC_ACQUIRE)!=LIVE_MAGIC;i++)pause_ms();
  if(live_bind(&writer,q,sizeof(*q),nonce,getpid(),getppid()))_exit(4);
  for(i=0;i<20;i++){if(live_publish(&writer,codec,sizeof(codec),idr,sizeof(idr),37,(uint64_t)i*100000)<0)_exit(5);pause_ms();pause_ms();pause_ms();}
  munmap(q,sizeof(*q));_exit(0);
 }
 rc=run(token,p,2,0,1);if(waitpid(p,&status,0)!=p||!WIFEXITED(status)||WEXITSTATUS(status)||rc)return 6;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-live-report-%s.bin",token);fd=open(path,O_RDONLY);if(fd<0||read(fd,report,512)!=512)return 7;close(fd);
 if(report[5]!=3||report[6]||report[7]!=20||report[8]!=360)return 8;
 snprintf(path,sizeof(path),"/dev/shmem/delphi-live-video-%s.h264",token);if(stat(path,&st)||st.st_size!=360)return 9;
 {const char *names[]={"delphi-live-","delphi-live-report-","delphi-live-video-","delphi-live-timing-"};const char *ext[]={".bin",".bin",".h264",".bin"};for(i=0;i<4;i++){snprintf(path,sizeof(path),"/dev/shmem/%s%s%s",names[i],token,ext[i]);unlink(path);}}
 puts("LIVE_CAPTURE_QNX_PASS cross_process=1 source_identity=1 owned_copy=1 frame_metadata=1 bounded_files=1 no_transport=1");return 0;
}
#endif
int main(int argc,char **argv){
 char *end;unsigned long pid,seconds,nav;int detach=0;struct sigaction sa;
 memset(&sa,0,sizeof(sa));sa.sa_handler=SIG_DFL;sigemptyset(&sa.sa_mask);if(sigaction(SIGCHLD,&sa,0))return 2;
#ifdef LIVE_CAPTURE_TEST
 if(argc==2&&!strcmp(argv[1],"--self-test"))return self_test();
#endif
 if(argc==6&&!strcmp(argv[1],"--detach")){detach=1;argv++;argc--;}
 if(argc!=5||!token_ok(argv[1])||!argv[2][0]||strspn(argv[2],"0123456789")!=strlen(argv[2]))return 2;
 pid=strtoul(argv[2],&end,10);if(*end||!pid||pid>0x7fffffff)return 2;seconds=strtoul(argv[3],&end,10);if(*end||seconds<1||seconds>30)return 2;nav=strtoul(argv[4],&end,10);if(*end||!nav||nav>0x7fffffff)return 2;
 if(detach){pid_t child=fork();if(child<0)return 3;if(child){printf("LIVE_CAPTURE_DETACHED pid=%u\n",(unsigned)child);return 0;}if(setsid()<0)_exit(126);{int fd=open("/dev/null",O_RDONLY);if(fd>=0){dup2(fd,STDIN_FILENO);if(fd>2)close(fd);}}}
 return run(argv[1],(pid_t)pid,(unsigned)seconds,(pid_t)nav,0);
}
