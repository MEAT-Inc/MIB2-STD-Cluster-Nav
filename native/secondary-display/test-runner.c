#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>
int main(void){pid_t p=fork();int status;if(!p){setenv("LD_PRELOAD","/proc/boot/libdelphi_observer.so",1);execl("/proc/boot/secondary_forward_fixture","secondary_forward_fixture",(char*)0);_exit(99);}if(p<0||waitpid(p,&status,0)!=p||!WIFEXITED(status)||WEXITSTATUS(status))return 1;puts("SECONDARY_TEST_RUNNER_PASS");return 0;}
