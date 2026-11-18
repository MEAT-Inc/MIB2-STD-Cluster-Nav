#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
int main(void){pid_t p=fork();int status;if(!p){unsetenv("DELPHI_OBSERVER_LOG");setenv("LD_PRELOAD","/proc/boot/libdelphi_observer_keyframe.so",1);execl("/proc/boot/route_forward_fixture","route_forward_fixture",(char*)0);_exit(99);}if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status)||WEXITSTATUS(status))return 1;puts("ROUTE_POLICY_PRELOAD_RUNNER_PASS");return 0;}
