#define _QNX_SOURCE 1
#include <fcntl.h>
#include <unistd.h>
__attribute__((constructor(101))) static void early_io(void){int fd=open("/dev/shmem/replay-early.bin",O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0)_exit(125);if(write(fd,"early",5)!=5||close(fd))_exit(125);write(1,"REPLAY_EARLY_IO_PASS\n",21);}
