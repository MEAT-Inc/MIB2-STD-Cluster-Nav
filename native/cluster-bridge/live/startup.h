#ifndef DELPHI_LIVE_STARTUP_H
#define DELPHI_LIVE_STARTUP_H
#include "queue.h"
#define STARTUP_DELAY_MS 1000u
#define STARTUP_TARGET_DELAY_MS 250u
#define STARTUP_PACE_NUMERATOR 4u
#define STARTUP_PACE_DENOMINATOR 5u
#define STARTUP_CATCHUP_INPUT_MS ((STARTUP_DELAY_MS-STARTUP_TARGET_DELAY_MS)*STARTUP_PACE_DENOMINATOR)
#define STARTUP_BYTES (4u*1024u*1024u)
#define STARTUP_SLOTS 64u
#define STARTUP_REPEATS 3u
struct startup_record {uint64_t due;uint32_t offset,bytes,flags;};
struct live_startup {unsigned char *data,*key;struct startup_record rows[STARTUP_SLOTS];unsigned head,tail,used,write_at,read_at,key_bytes,repeats,emitted,peak_bytes,peak_frames,overflows;uint32_t key_flags;uint64_t first_ms,next_repeat,last_due;int started;};
void startup_init(struct live_startup*,void*,void*);
int startup_push(struct live_startup*,const void*,unsigned,unsigned,uint64_t);
/* 1 complete AU,0 not due,-1 invalid state. Bootstrap IDRs always precede P frames. */
int startup_pop(struct live_startup*,uint64_t,void*,size_t,unsigned*,unsigned*,int*);
unsigned startup_pending(const struct live_startup*);
#endif
