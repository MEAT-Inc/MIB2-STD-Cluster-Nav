#ifndef PATH_TEST_BENCH_H
#define PATH_TEST_BENCH_H
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#define PATH_PREFIX "/ramdisk/delphi-path-test_"
#define PATH_MAGIC 0x31545044u
static char test_root[128],tx_target[192],tx_copy[192],tx_wrapper[192],tx_report_path[192],tx_library[192],tx_search[224],tx_log[192];
#define TX_TARGET tx_target
#define TX_COPY tx_copy
#define TX_WRAPPER tx_wrapper
#define TX_REPORT tx_report_path
struct path_run { unsigned sequence,pid,ppid,observed,records,args_ok; };
struct tx_report {
 unsigned magic,version,bytes;
 volatile unsigned armed,done,watchdog_finished,watchdog_removed;
 volatile unsigned app_runs,observed_runs,last_pid,last_ppid,arguments_ok;
 unsigned reserved[4];
 struct path_run runs[6];
};
static int setup_paths(const char *root) {
 unsigned n=(unsigned)strlen(PATH_PREFIX),i;struct stat st;
 if(strlen(root)!=n+32 || strncmp(root,PATH_PREFIX,n))return 0;
 for(i=0;i<32;++i)if(!((root[n+i]>='0'&&root[n+i]<='9')||(root[n+i]>='a'&&root[n+i]<='f')))return 0;
 if(lstat(root,&st) || !S_ISDIR(st.st_mode))return 0;
 strcpy(test_root,root);
 snprintf(tx_target,sizeof(tx_target),"%s/path_child",root);
 snprintf(tx_copy,sizeof(tx_copy),"%s/path_original",root);
 snprintf(tx_wrapper,sizeof(tx_wrapper),"%s/path_test",root);
 snprintf(tx_report_path,sizeof(tx_report_path),"/dev/shmem/delphi-path-report-%s.bin",root+n);
 snprintf(tx_library,sizeof(tx_library),"%s/libdelphi_observer.so",root);
 snprintf(tx_search,sizeof(tx_search),"%s:/proc/boot",root);
 snprintf(tx_log,sizeof(tx_log),"/dev/shmem/delphi-observer-path-%s.bin",root+n);
 return 1;
}
static int regular_file(const char *path) { struct stat st;return !lstat(path,&st) && S_ISREG(st.st_mode); }
#endif
