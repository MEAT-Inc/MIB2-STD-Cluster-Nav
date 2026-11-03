#ifndef DELPHI_REPLAY_H
#define DELPHI_REPLAY_H
#include <stddef.h>
#include <stdint.h>
#include <sys/types.h>
enum { RPL_MAGIC=0x314c5052, RPL_REPORT_MAGIC=0x31504c52, RPL_READY=1,RPL_ACTIVE,RPL_DONE,RPL_ERROR };
enum { RP_MAGIC,RP_VERSION,RP_SIZE,RP_PID,RP_STATUS,RP_ERROR,RP_OPENS,RP_WRITES,RP_SUPPRESSED,RP_REQUESTED,RP_PACKETS,RP_BYTES,RP_ZERO,RP_CLOSES,RP_GENERATION,RP_FD,RP_GROUPS,RP_DURATION,RP_EXPECTED,RP_LOADED,RP_BAD_CALLERS };
enum { RP_HOOK_OPENS=37,RP_HOOK_WRITES=38,RP_HOOK_CLOSES=39,RP_INSPECT_HEARTBEAT=50 };
struct replay_config {
 int (*native_open)(const char *,int,...);
 ssize_t (*native_write)(int,const void *,size_t);
 int (*native_close)(int);
 int (*geometry)(void *,int);
 void *opaque;
 const unsigned char *file_bytes;
 size_t file_size;
 volatile uint32_t *report;
 uintptr_t open_lr,write_lr,close_lr;
 int defer_ready;
 void (*inspect)(void *,volatile uint32_t *);
};
void replay_bind_callbacks(int (*)(const char *,int,...),ssize_t (*)(int,const void *,size_t),int (*)(int));
int replay_init(const struct replay_config *);
void replay_stop(void);
int replay_publish_ready(void);
int replay_open_impl(const char *,int,unsigned,uintptr_t);
ssize_t replay_write_impl(int,const void *,size_t,uintptr_t);
int replay_close_impl(int,uintptr_t);
#endif


