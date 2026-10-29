#define _QNX_SOURCE 1
#include "bench.h"
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/pathmgr.h>
#include <sys/wait.h>
#include <unistd.h>
static const char *root=PATH_PREFIX "00000000000000000000000000000000";
static int dump(const char *name,const char *label) {
 unsigned char bytes[512];ssize_t n,i;int fd=open(name,O_RDONLY);if(fd<0)return 1;
 printf("%s ",label);
 while((n=read(fd,bytes,sizeof(bytes)))>0)for(i=0;i<n;++i)printf("%02x",bytes[i]);
 puts("");close(fd);return n<0?2:0;
}
int main(void) {
 int status;pid_t child;


 if(!setup_paths(root) || !regular_file(TX_TARGET))return 13;
 child=fork();if(!child){execl(TX_WRAPPER,"path_test",root,"suite",(char*)0);_exit(99);}
 if(child<0 || waitpid(child,&status,0)!=child || !WIFEXITED(status) || WEXITSTATUS(status))return 14;
 if(dump(TX_REPORT,"PATH_REPORT_HEX") || dump(tx_log,"PATH_TRACE_HEX"))return 15;
 child=fork();if(!child){execl(TX_WRAPPER,"path_test","/extbin/apps/bin","suite",(char*)0);_exit(99);}
 if(child<0 || waitpid(child,&status,0)!=child || !WIFEXITED(status) || WEXITSTATUS(status)!=2)return 16;
 puts("PATH_INVALID_FACTORY_TARGET_REJECTED");
 puts("PATH_QNX_SUITE_PASS");return 0;
}
