#ifndef DELPHI_LIVE_OPTIONS_H
#define DELPHI_LIVE_OPTIONS_H
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <errno.h>
/* Exact token-scoped little-endian v1 options; absence keeps the bounded default. */
static int live_options_load(const char *token,unsigned *seconds){
 char path[160],hex[9];unsigned char b[33];uint32_t w[8];struct stat st;int fd;size_t at=0;unsigned i;
 if(!token||strlen(token)!=32||strspn(token,"0123456789abcdef")!=32)return -1;
 *seconds=30;snprintf(path,sizeof(path),"/ramdisk/delphi-nav-bridge_%s/live-options.bin",token);
 fd=open(path,O_RDONLY);if(fd<0)return errno==ENOENT?0:-1;
 if(fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size!=32){close(fd);return -1;}
 while(at<sizeof(b)){ssize_t n=read(fd,b+at,sizeof(b)-at);if(n<0&&errno==EINTR)continue;if(n<0){close(fd);return -1;}if(!n)break;at+=n;}close(fd);if(at!=32)return -1;
 for(i=0;i<8;i++)w[i]=(uint32_t)b[i*4]|(uint32_t)b[i*4+1]<<8|(uint32_t)b[i*4+2]<<16|(uint32_t)b[i*4+3]<<24;
 if(w[0]!=0x314f564c||w[1]!=1||w[2]!=32||(w[3]!=0&&w[3]!=30))return -1;
 for(i=0;i<4;i++){memcpy(hex,token+8*i,8);hex[8]=0;if(w[4+i]!=(uint32_t)strtoul(hex,0,16))return -1;}
 *seconds=w[3];return 0;
}
#endif
