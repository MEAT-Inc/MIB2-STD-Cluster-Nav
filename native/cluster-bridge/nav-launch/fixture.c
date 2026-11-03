#define _QNX_SOURCE 1
#include "launch.h"
#include "proc_guard.h"
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdlib.h>
#include <sys/stat.h>
int main(int argc,char **argv){char cwd[128],config[32]={0};int fd;struct stat output,error;pg_identity self;unsigned i;uint32_t w[128]={0};const char *report=getenv("DELPHI_NAV_REPORT");struct timespec tick={0,100000000};
 printf("NAV_FIXTURE pid=%u argc=%d argv0=%s cwd=%s\n",(unsigned)getpid(),argc,argv[0],getcwd(cwd,sizeof(cwd))?cwd:"INVALID");fflush(stdout);
 if((argc!=3&&argc!=4)||strcmp(argv[0],"/extbin/apps/bin/NavigationServer")||strcmp(argv[1],"-fcfg")||strcmp(argv[2],NAV_CONFIG_REL)||(argc==4&&(strncmp(argv[3],"-X",2)||!argv[3][2]||strspn(argv[3]+2,"0123456789")!=strlen(argv[3]+2)))||!getcwd(cwd,sizeof(cwd))||strcmp(cwd,"/extbin/apps/bin"))return 90;
 if(!isatty(STDOUT_FILENO)||!isatty(STDERR_FILENO)||fstat(STDOUT_FILENO,&output)||fstat(STDERR_FILENO,&error)||!S_ISCHR(output.st_mode)||!S_ISCHR(error.st_mode)||output.st_rdev!=error.st_rdev)return 94;
 puts("NAV_STDIO_PRESERVED_PASS");fflush(stdout);
 fd=pg_open(getpid(),0,&self);if(fd<0||strcmp(self.executable,NAV_TARGET)||pg_matches(fd,&self))return 93;close(fd);puts("NAV_FIXTURE_CANONICAL_IMAGE_PASS");fflush(stdout);
 fd=open(argv[2],O_RDONLY);if(fd<0||read(fd,config,sizeof(config)-1)!=19||strcmp(config,"nav-fixture-config\n"))return 91;close(fd);
 if(report){fprintf(stderr,"NAV_FIXTURE_STDERR_RETAINED\n");fflush(stderr);w[0]=0x31504c52u;w[1]=1;w[2]=512;w[3]=getpid();w[4]=1;w[10]=9;w[11]=1692;fd=open(report,O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0||write(fd,w,sizeof(w))!=(ssize_t)sizeof(w))return 92;close(fd);puts("NAV_FIXTURE_ARGV_CWD_CONFIG_PASS");fflush(stdout);}
 for(i=0;i<700;++i){nanosleep(&tick,0);}
 return 8;
}
