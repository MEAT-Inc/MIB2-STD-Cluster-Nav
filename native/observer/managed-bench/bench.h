#ifndef MANAGED_BENCH_H
#define MANAGED_BENCH_H
#include <string.h>
#include <unistd.h>
#define REPORT "/dev/shmem/delphi-managed-bench"
#define TARGET "/proc/boot/managed_child"
#define ORIGINAL "/proc/boot/managed_original"
#define WRAPPER "/proc/boot/managed_wrapper"
struct report {
 volatile unsigned count,pid,ppid,observed,last_observed,records;
 volatile int extra_code;
 volatile unsigned guard_armed,guard_done,guard_removed;
};
static inline int owned_redirect(void) {
 char path[256];ssize_t n=readlink(TARGET,path,sizeof(path)-1);
 if(n<0)return 0;
 path[n]=0;return !strcmp(path,WRAPPER);
}
#endif
