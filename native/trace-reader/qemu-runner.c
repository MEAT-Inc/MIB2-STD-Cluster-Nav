#define _POSIX_C_SOURCE 200112L
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <stdio.h>
static int run(const char *program,const char *arg1,const char *arg2){pid_t p=fork();int s;if(p<0)return 127;if(!p){if(arg2)execl(program,program,arg1,arg2,(char*)0);else execl(program,program,arg1,(char*)0);_exit(127);}if(waitpid(p,&s,0)!=p||!WIFEXITED(s))return 127;return WEXITSTATUS(s);}
int main(void){int bad;if(run("/proc/boot/trace_reader","/invalid-root",0)!=3)return 1;puts("TRACE_READER_QNX_LOADER_ROOT_REFUSAL_PASS");if(run("/proc/boot/ksh","-n","/proc/boot/launch-good.sh"))return 2;puts("TRACE_READER_QNX_KSH_GOOD_WIRE_PASS");bad=run("/proc/boot/ksh","-n","/proc/boot/launch-bad.sh");if(!bad||bad==127)return 3;puts("TRACE_READER_QNX_KSH_BAD_WIRE_REJECTED");fflush(stdout);return 0;}
