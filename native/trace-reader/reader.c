#define _POSIX_C_SOURCE 200112L
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <time.h>
#include <signal.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#ifndef TRACE_SECONDS
#define TRACE_SECONDS 180u
#endif
#ifndef TRACE_BYTES
#define TRACE_BYTES (16u*1024u*1024u)
#endif
#define PREFIX "/ramdisk/delphi-trace-reader_"
static uint64_t now_ms(void){struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return 0;return (uint64_t)t.tv_sec*1000u+t.tv_nsec/1000000u;}
static int write_all(int fd,const void *data,size_t n){const unsigned char *p=data;while(n){ssize_t r=write(fd,p,n);if(r<0&&errno==EINTR)continue;if(r<=0)return -1;p+=r;n-=r;}return 0;}
static int valid_root(const char *path){unsigned i,n=sizeof(PREFIX)-1;struct stat st;if(strlen(path)!=n+32||strncmp(path,PREFIX,n))return 0;for(i=0;i<32;++i)if(!((path[n+i]>='0'&&path[n+i]<='9')||(path[n+i]>='a'&&path[n+i]<='f')))return 0;return !lstat(path,&st)&&S_ISDIR(st.st_mode);}
static int wait_fd(int fd,int writing,uint64_t deadline){
 for(;;){fd_set set;struct timeval tv;uint64_t now=now_ms(),left;int r;
  if(!now){errno=EIO;return -1;}if(now>=deadline)return 0;left=deadline-now;if(left>1000)left=1000;
  FD_ZERO(&set);FD_SET(fd,&set);tv.tv_sec=left/1000;tv.tv_usec=(left%1000)*1000;
  r=select(fd+1,writing?0:&set,writing?&set:0,0,&tv);if(r<0&&errno==EINTR)continue;return r;
 }
}
int main(int argc,char **argv){
 char path[192],text[384];unsigned char buffer[16384];struct sockaddr_in address;struct sigaction action;
 int out=-1,report=-1,s=-1,rc=2,saved=0,flags,result;unsigned bytes=0;uint64_t start=0,elapsed=0,deadline;const char *reason="error";
 if(argc!=2||!valid_root(argv[1]))return 3;
 memset(&action,0,sizeof(action));sigemptyset(&action.sa_mask);action.sa_handler=SIG_IGN;
 if(sigaction(SIGHUP,&action,0)||sigaction(SIGPIPE,&action,0))return 4;
 /* An interactive ksh may make an asynchronous job its process-group leader.
  * Fork once only when setsid reports EPERM; detach that logger-only child.
  * This happens before files, sockets or threads exist. */
 if(setsid()<0){pid_t child;if(errno!=EPERM)return 4;child=fork();if(child<0)return 4;if(child>0)_exit(0);if(setsid()<0)return 4;}
 snprintf(path,sizeof(path),"%s/trace-report.txt",argv[1]);report=open(path,O_WRONLY|O_CREAT|O_EXCL,0644);if(report<0)return 5;
 snprintf(path,sizeof(path),"%s/trace.bin",argv[1]);out=open(path,O_WRONLY|O_CREAT|O_EXCL,0644);if(out<0)goto done;
 s=socket(AF_INET,SOCK_STREAM,0);if(s<0)goto done;if(s>=FD_SETSIZE){errno=EMFILE;goto done;}
 flags=fcntl(s,F_GETFL,0);if(flags<0||fcntl(s,F_SETFL,flags|O_NONBLOCK))goto done;
 memset(&address,0,sizeof(address));address.sin_family=AF_INET;
#ifdef __QNXNTO__
 address.sin_len=sizeof(address);
#endif
 address.sin_port=htons(15361);address.sin_addr.s_addr=htonl(INADDR_LOOPBACK);
 result=connect(s,(struct sockaddr*)&address,sizeof(address));
 if(result<0){socklen_t n=sizeof(result);if(errno!=EINPROGRESS)goto done;deadline=now_ms()+5000;
  do{result=wait_fd(s,1,deadline);}while(result==0&&now_ms()<deadline);
  if(result<=0){if(!result)errno=ETIMEDOUT;goto done;}if(getsockopt(s,SOL_SOCKET,SO_ERROR,&result,&n))goto done;if(result){errno=result;goto done;}
 }
 start=now_ms();if(!start){errno=EIO;goto done;}deadline=start+(uint64_t)TRACE_SECONDS*1000u;
 printf("TRACE_READER_READY pid=%u seconds=%u max_bytes=%u\n",(unsigned)getpid(),(unsigned)TRACE_SECONDS,(unsigned)TRACE_BYTES);fflush(stdout);
 while(bytes<TRACE_BYTES){ssize_t n;size_t want=TRACE_BYTES-bytes;if(want>sizeof(buffer))want=sizeof(buffer);
  if(now_ms()>=deadline){reason="duration";break;}
  result=wait_fd(s,0,deadline);if(result<0)goto done;if(!result)continue;
  n=recv(s,buffer,want,0);if(n<0&&(errno==EINTR||errno==EAGAIN))continue;if(n<0)goto done;
  if(!n){reason="peer_closed";break;}if(write_all(out,buffer,(size_t)n))goto done;bytes+=(unsigned)n;
 }
 if(bytes==TRACE_BYTES)reason="byte_limit";
 rc=bytes&&(!strcmp(reason,"duration")||!strcmp(reason,"byte_limit"))?0:2;
 done:saved=!strcmp(reason,"error")?errno:0;if(start)elapsed=now_ms()-start;
 if(s>=0)close(s);
 if(out>=0&&close(out)){saved=errno;rc=2;reason="error";}
 result=snprintf(text,sizeof(text),"TRACE_READER_REPORT version=1 pid=%u seconds=%u limit=%u bytes=%u elapsed_ms=%llu reason=%s rc=%d error=%d\n",(unsigned)getpid(),(unsigned)TRACE_SECONDS,(unsigned)TRACE_BYTES,bytes,(unsigned long long)elapsed,reason,rc,saved);
 if(write_all(report,text,(size_t)result)||close(report))return 6;
 printf("%s",text);fflush(stdout);return rc;
}
