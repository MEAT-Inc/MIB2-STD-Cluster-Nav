#define _QNX_SOURCE 1
#include "bench.h"
#include <stdlib.h>
#include <sys/pathmgr.h>
int main(int argc,char **argv) {
 /* Fixed synthetic paths; no vehicle target can be selected. */
 if(argc<2 || argc>3 || strcmp(argv[0],TARGET) || strcmp(argv[1],"-t"))return 120;
 if(argc==3 && strncmp(argv[2],"-X",2))return 121;
 if(!owned_redirect())return 122;
 if(pathmgr_unlink(TARGET) || owned_redirect())return 123;
 if(setenv("LD_PRELOAD","/proc/boot/libdelphi_observer.so",1))return 124;
 execv(ORIGINAL,argv);return 125;
}
