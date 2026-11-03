#define _QNX_SOURCE 1
#include <process.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/wait.h>
int main(void){int rc;if(setenv("DELPHI_NAV_REPORT","/dev/shmem/delphi-nav-report-00000000000000000000000000000000.bin",1)||setenv("LD_PRELOAD","/proc/boot/libdelphi_cluster_test.so",1))return 2;if(setenv("LD_PRELOAD","/proc/boot/libdelphi_cluster_early_legacy.so",1))return 3;rc=spawnl(P_WAIT,"/proc/boot/replay_hook_fixture","replay_hook_fixture",(char*)0);if(!WIFEXITED(rc)||WEXITSTATUS(rc)!=126){printf("EARLY_LEGACY_UNEXPECTED rc=%d\n",rc);return 4;}puts("REPLAY_EARLY_LEGACY_EXIT126_PASS");if(setenv("LD_PRELOAD","/proc/boot/libdelphi_cluster_test.so",1))return 5;rc=spawnl(P_WAIT,"/proc/boot/replay_hook_fixture","replay_hook_fixture",(char*)0);unsetenv("LD_PRELOAD");printf("REPLAY_HOOK_RUNNER rc=%d\n",rc);return rc;}
