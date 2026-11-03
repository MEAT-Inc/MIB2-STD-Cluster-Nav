/* Synthetic Nav receiver: test process-manager/SAL contract, not GPU teardown. */
#define _QNX_SOURCE 1
#include "sal-fixture-api.h"
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <time.h>
static struct api a;static int done;
static void run(void *unused){const uint32_t *m;int f;uint32_t pid=getpid();(void)unused;
 if(a.queue(32,8,(void*)malloc,(void*)free)!=1||a.subscribe(0x163,1)!=1)_exit(21);
 if(a.send(1,0,0x162,0,0)!=1)_exit(24);
 f=open("/dev/shmem/sal-target-ready.bin",O_CREAT|O_EXCL|O_WRONLY,0600);if(f<0||write(f,&pid,4)!=4)_exit(22);close(f);puts("SAL_RECEIVER_READY");fflush(stdout);
 m=a.receive();if(!m||m[3]!=0x163||m[1]!=0)_exit(23);puts("SAL_GRACEFUL_STOP_RECEIVED");fflush(stdout);__atomic_store_n(&done,1,__ATOMIC_RELEASE);}
int main(void){struct thread_attr t;struct timespec tick={0,1000000};unsigned tid=1;if(resolve(&a)||initialize(&a,30))return 11;a.thread_attr(&t);t.name="NavGracefulFixture";t.id=1;t.stack=65536;if(a.create(run,0,&t)!=1)return 12;
 while(!__atomic_load_n(&done,__ATOMIC_ACQUIRE)){nanosleep(&tick,0);}
 a.wait_destroyed(&tid,1);a.deinit();unlink("/dev/shmem/sal-target-ready.bin");puts("SAL_RECEIVER_CLEAN_EXIT");fflush(stdout);return 0;}
