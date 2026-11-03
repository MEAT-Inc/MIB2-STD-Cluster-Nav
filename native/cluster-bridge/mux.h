#ifndef CLUSTER_MUX_H
#define CLUSTER_MUX_H
#include <stddef.h>
#include <stdint.h>
#define CLUSTER_MUX_MAX_AU (1024u * 1024u)
/* Return 188 only after consuming the complete packet. Failure is sticky;
 * the mux never retries an emitted packet or a partially emitted AU. */
typedef int (*cluster_mux_emit)(void *, const unsigned char *, size_t);
struct cluster_mux {
 cluster_mux_emit emit; void *opaque;
 uint64_t last_ms, psi_ms, pcr_ms;
 unsigned char cc[3];
 unsigned failed, started, have_time, have_psi, have_pcr;
};
void cluster_mux_init(struct cluster_mux *, cluster_mux_emit, void *);
/* -1 failed, 0 waiting for first IDR, 1 AU emitted. Caller retains complete AU.
 * AU boundaries are supplied by caller; elementary framing is validated only. */
int cluster_mux_push(struct cluster_mux *, const unsigned char *, size_t, uint64_t);
/* Caller must tick at least every 32 relative milliseconds, including no-video
 * intervals. Timestamps may be equal, but must never move backwards. */
int cluster_mux_tick(struct cluster_mux *, uint64_t);
#endif
