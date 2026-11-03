#define _QNX_SOURCE 1
#include "replay.h"
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/mman.h>
#include <sys/pathmgr.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
static int current=-1;
int test_open(const char*,int);ssize_t test_write(int,const void*,size_t);int test_close(int);
__attribute__((visibility("default"))) int test_geometry(void *p,int fd){(void)p;return fd==current;}
int main(void){struct timespec tick={0,1000000};uint32_t w[128];int report,i;struct stat st;const char *path=getenv("DELPHI_NAV_REPORT");if(!path)return 2;report=open(path,O_RDWR);if(report<0)return 3;{int tmp=open("/dev/shmem/replay-target.bin",O_CREAT|O_EXCL|O_RDWR,0600);if(tmp<0)return 12;close(tmp);if(pathmgr_symlink("/dev/shmem/replay-target.bin","/dev/transport_server/spawn/isoTX"))return 13;}current=test_open("/dev/transport_server/spawn/isoTX",1);if(current<0)return 4;errno=EDOM;if(test_write(current,"native",6)!=6||errno!=EDOM)return 5;for(i=0;i<1800;i++){if(pread(report,w,512,0)!=512)return 16;if(w[50])break;nanosleep(&tick,0);}if(!w[50]||w[51]||!w[37]||!w[38])return 17;for(i=0;i<3;i++)if(w[40+i]!=w[29+i])return 18;puts("REPLAY_IDLE_IMPORT_INSPECTION_PASS");{uint32_t *m=mmap(0,512,PROT_READ|PROT_WRITE,MAP_SHARED,report,0);if(m==MAP_FAILED||m[RP_STATUS]!=RPL_READY||m[RP_PACKETS])return 14;__atomic_store_n(&m[21],1,__ATOMIC_RELEASE);}for(i=0;i<1500;i++){if(pread(report,w,512,0)!=512)return 6;if(w[RP_STATUS]==RPL_DONE)break;if(w[RP_STATUS]==RPL_ERROR){printf("HOOK_ERROR native=%u packets=%u zero=%u bad=%u\n",w[RP_ERROR],w[RP_PACKETS],w[RP_ZERO],w[RP_BAD_CALLERS]);return 7;}nanosleep(&tick,0);}if(i==1500||w[RP_WRITES]!=1||w[RP_SUPPRESSED]||w[RP_PACKETS]!=3||w[RP_BYTES]!=564)return 8;if(test_write(current,"muted",5)!=5)return 9;if(test_close(current))return 10;if(stat("/dev/transport_server/spawn/isoTX",&st)||st.st_size!=570)return 11;close(report);puts("REPLAY_PRELOAD_ARMED_DESCRIPTOR_PASS no_source_write_after_arm=1");puts("REPLAY_ACTUAL_PRELOAD_PASS wrappers=3 caller_LR=1 schedule=1 errno=1");return 0;}
