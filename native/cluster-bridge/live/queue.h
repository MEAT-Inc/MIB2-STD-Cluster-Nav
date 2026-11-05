#ifndef DELPHI_LIVE_QUEUE_H
#define DELPHI_LIVE_QUEUE_H
#include <stddef.h>
#include <stdint.h>
#define LIVE_CAPACITY 4u
#define LIVE_AU_LIMIT (1024u*1024u)
#define LIVE_MAGIC 0x3156514cu
enum { LIVE_IDR=1,LIVE_SPS=2,LIVE_PPS=4,LIVE_SLICE=8,LIVE_RESYNC=16 };
struct live_slot {uint32_t bytes,sequence,session,flags;uint64_t timestamp;uint32_t reserved[2];unsigned char data[LIVE_AU_LIMIT];};
struct live_shared {uint32_t magic,version,bytes,capacity,head,tail,dropped,request_idr,closed,producer_pid,consumer_pid,nonce[4],reserved;struct live_slot slots[LIVE_CAPACITY];};
struct live_peer {struct live_shared *q;uint32_t nonce[4],producer_pid,consumer_pid,epoch,session;uint64_t last_timestamp;int need_idr,have_session,have_timestamp;};
struct live_frame {uint64_t timestamp;uint32_t bytes,session,flags;};
/* Caller owns a verified mapping for the complete structure. Exactly one producer
 * and one consumer. Ownership and nonce are fixed by their external lifecycle. */
int live_init(void *,size_t,const uint32_t[4],uint32_t,uint32_t);
int live_bind(struct live_peer *,void *,size_t,const uint32_t[4],uint32_t,uint32_t);
/* Copy borrowed spans before returning. No allocation, lock, I/O, wait or ACK.
 * 1 queued,0 full/drop,-1 malformed/profile/closed. Prefix is codec data only. */
int live_publish(struct live_peer *,const void *,size_t,const void *,size_t,uint32_t,uint64_t);
/* Copy before releasing slot. On overflow/session change, wait for IDR+SPS+PPS.
 * 1 complete frame,0 empty/resync/drop,-1 profile/size/closed error. */
int live_consume(struct live_peer *,void *,size_t,struct live_frame *);
int live_close(struct live_peer *);
#endif
