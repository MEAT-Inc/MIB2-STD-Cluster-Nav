#define _QNX_SOURCE 1
#include "queue.h"
#include "../../observer/launch/proc_guard.h"
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
int main(int argc,char **argv){char path[160],expected[160],hex[9],*end;uint32_t nonce[4],aa,nav;pg_identity source,consumer,parent;int a=-1,n=-1,p=-1,fd=-1,rc=3;struct stat st;struct live_shared *q;unsigned i;if(argc!=4||strlen(argv[1])!=32||strspn(argv[1],"0123456789abcdef")!=32)return 2;aa=strtoul(argv[2],&end,10);if(*end||!aa||aa>0x7fffffff)return 2;nav=strtoul(argv[3],&end,10);if(*end||!nav||nav>0x7fffffff||nav==aa)return 2;for(i=0;i<4;i++){memcpy(hex,argv[1]+8*i,8);hex[8]=0;nonce[i]=strtoul(hex,0,16);}a=pg_open(aa,0,&source);n=pg_open(nav,0,&consumer);snprintf(expected,sizeof(expected),"/ramdisk/delphi-aa-observer_%s/AndroidAuto.original",argv[1]);if(a<0||n<0||strcmp(source.executable,expected)||strcmp(consumer.executable,"/extbin/apps/bin/NavigationServer")||source.base_address!=0x100000||consumer.base_address!=0x100000||source.parent!=consumer.parent)goto done;p=pg_open(source.parent,0,&parent);if(p<0||strcmp(parent.executable,"/proc/boot/procman")||pg_matches(a,&source)||pg_matches(n,&consumer)||pg_matches(p,&parent))goto done;snprintf(path,sizeof(path),"/dev/shmem/delphi-live-%s.bin",argv[1]);if(lstat(path,&st)||!S_ISREG(st.st_mode))goto done;fd=open(path,O_RDWR);if(fd<0||fstat(fd,&st)||!S_ISREG(st.st_mode)||(uint64_t)st.st_size!=sizeof(*q))goto done;q=mmap(0,sizeof(*q),PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);if(q==MAP_FAILED)goto done;for(i=0;i<64;i++)if(((unsigned char*)q)[i]){munmap(q,sizeof(*q));goto done;}if(!pg_matches(a,&source)&&!pg_matches(n,&consumer)&&!pg_matches(p,&parent)&&!live_init(q,sizeof(*q),nonce,aa,nav))rc=0;munmap(q,sizeof(*q));done:if(fd>=0)close(fd);if(a>=0)close(a);if(n>=0)close(n);if(p>=0)close(p);if(!rc)puts("LIVE_NAV_QUEUE_BOUND");return rc;}
