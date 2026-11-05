/* Fixed-layout, read-only NavigationServer geometry snapshot. No stops/signals. */
#define _QNX_SOURCE 1
#include "../observer/launch/proc_guard.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#ifdef NAV_SNAPSHOT_TIMED
#define SNAP_TIME_FORMAT "\"monotonic_ns\":%llu,"
#define SNAP_TIME_ARGUMENT (unsigned long long)now_ns,
#else
#define SNAP_TIME_FORMAT ""
#define SNAP_TIME_ARGUMENT
#endif
static int read_exact(int fd,uint32_t address,void *out,size_t n){ssize_t got;if(address>0x7fffffffU||n>0x7fffffffU-address)return -1;do{got=pread(fd,out,n,(off_t)address);}while(got<0&&errno==EINTR);return got==(ssize_t)n?0:-1;}
struct sample {uint32_t pointer,rate,width,height,buffer_width,buffer_height,padding;int32_t writer;};
static int sample(int fd,uint32_t global,struct sample *s){unsigned char b[0x4c];memset(s,0,sizeof(*s));s->writer=-1;if(read_exact(fd,global,&s->pointer,4))return -1;if(!s->pointer)return 0;if((s->pointer&3)||s->pointer>0x7ffffed0U)return -1;if(read_exact(fd,s->pointer+0xe0,b,sizeof(b)))return -1;memcpy(&s->rate,b,4);memcpy(&s->width,b+0x18,4);memcpy(&s->height,b+0x1c,4);memcpy(&s->buffer_width,b+0x20,4);memcpy(&s->buffer_height,b+0x24,4);memcpy(&s->padding,b+0x28,4);memcpy(&s->writer,b+0x48,4);return 0;}
static int stable(int fd,uint32_t global,struct sample *s){struct sample second;if(sample(fd,global,s)||sample(fd,global,&second)||memcmp(s,&second,sizeof(*s)))return -1;return 0;}
static int self_test(void){pg_identity self;struct sample s;uint32_t object[0x130/4]={0},pointer=(uintptr_t)object;int fd=pg_open(getpid(),0,&self);if(fd<0)return 1;object[0xe0/4]=30;object[0xf8/4]=800;object[0xfc/4]=480;object[0x100/4]=832;object[0x104/4]=480;object[0x108/4]=32;object[0x128/4]=17;if(stable(fd,(uintptr_t)&pointer,&s)||s.width!=800||s.height!=480||s.buffer_width!=832||s.writer!=17||s.padding!=32||s.rate!=30)return 2;pointer=0;if(stable(fd,(uintptr_t)&pointer,&s)||s.pointer||s.writer!=-1)return 3;pointer=3;if(!stable(fd,(uintptr_t)&pointer,&s))return 4;if(!read_exact(fd,0xffffffffU,&s,4))return 5;if(pg_matches(fd,&self))return 6;close(fd);puts("NAV_SNAPSHOT_QNX_PASS readonly=1 stable_reads=1 absent_and_invalid_pointer=checked");return 0;}
int main(int argc,char **argv){char *end;unsigned long pid;pg_identity id,parent;struct sample s;unsigned char header[20],b[4];int fd=-1,pfd=-1,rc=2;const uint32_t addresses[]={0x1ee75c,0x22cdb4,0x1ee308};const unsigned char code[3][4]={{0x39,0xd4,0xfc,0xeb},{0xb4,0xd8,0xfb,0xeb},{0xe1,0xd5,0xfc,0xeb}};unsigned i;
#ifdef NAV_SNAPSHOT_TIMED
 uint64_t now_ns=0;struct timespec clock_sample;
#endif
 if(argc==2&&!strcmp(argv[1],"--self-test")){int result=self_test();
#ifdef NAV_SNAPSHOT_TIMED
 if(!result){if(clock_gettime(CLOCK_MONOTONIC,&clock_sample))return 7;puts("NAV_TIMED_SNAPSHOT_QNX_PASS readonly=1 monotonic_clock=1");}
#endif
 return result;}

 if(argc!=2||!argv[1][0]||strspn(argv[1],"0123456789")!=strlen(argv[1]))return 2;
 errno=0;pid=strtoul(argv[1],&end,10);if(errno||*end||!pid||pid>0x7fffffffU)return 2;
 fd=pg_open((pid_t)pid,0,&id);if(fd<0)goto done;
 if(strcmp(id.executable,"/extbin/apps/bin/NavigationServer")||id.base_address!=0x100000)goto done;
 pfd=pg_open(id.parent,0,&parent);if(pfd<0||strcmp(parent.executable,"/proc/boot/procman"))goto done;
 if(read_exact(fd,0x100000,header,sizeof(header))||memcmp(header,"\177ELF\1\1\1",7)||header[16]!=2||header[17]||header[18]!=40||header[19])goto done;
 for(i=0;i<3;++i)if(read_exact(fd,addresses[i],b,4)||memcmp(b,code[i],4))goto done;
 if(stable(fd,0x5aeab0,&s)||pg_matches(fd,&id)||pg_matches(pfd,&parent))goto done;
#ifdef NAV_SNAPSHOT_TIMED
 if(clock_gettime(CLOCK_MONOTONIC,&clock_sample))goto done;
 now_ns=(uint64_t)clock_sample.tv_sec*1000000000ULL+clock_sample.tv_nsec;
#endif
 printf("{" SNAP_TIME_FORMAT "\"version\":1,\"pid\":%lu,\"parent\":%u,\"start_time\":%llu,\"load_bias\":0,\"readonly\":true,\"stable\":true,\"encoder\":%u,\"rate_candidate\":%u,\"width\":%u,\"height\":%u,\"buffer_width\":%u,\"buffer_height\":%u,\"padding\":%u,\"writer_fd\":%d}\n",SNAP_TIME_ARGUMENT pid,(unsigned)id.parent,(unsigned long long)id.start_time,s.pointer,s.rate,s.width,s.height,s.buffer_width,s.buffer_height,s.padding,s.writer);rc=0;
 done:if(pfd>=0)close(pfd);if(fd>=0)close(fd);if(rc)fprintf(stderr,"NAV_SNAPSHOT_REFUSED code=%d error=%d\n",rc,errno);return rc;
}
