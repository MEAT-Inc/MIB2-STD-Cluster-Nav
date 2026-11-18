#ifndef DELPHI_LIVE_MUX_H
#define DELPHI_LIVE_MUX_H
#include "queue.h"
#include <sys/types.h>
struct live_mux {ssize_t (*write)(void *,const void *,size_t);void *opaque;uint64_t last_ms,psi_ms,pcr_ms;unsigned cc[3];int timed,psi,pcr,started,failed;};
void live_mux_init(struct live_mux *,ssize_t (*)(void *,const void *,size_t),void *);
/* Call at least every32 synthetic milliseconds when the feed is active. */
int live_mux_tick(struct live_mux *,uint64_t);
/* Complete owned AnnexB AU. Flags are live_frame flags. 1 emitted,0 waits for
 * codec+IDR,-1 sticky failure. No allocation, clock, descriptor or OS action.
 * Callback must consume exactly188 bytes; output errors are never retried here.
 * Feed output through the proven native timeline handoff before transport use. */
int live_mux_push(struct live_mux *,const void *,size_t,uint32_t,uint64_t);
#endif
