#ifndef SECONDARY_RUNTIME_H
#define SECONDARY_RUNTIME_H
#include "../cluster-bridge/live/queue.h"
#include "../endpoint-factory/factory.h"
#include <pthread.h>
#define STREAM_MAGIC 0x31505253u
#define STREAM_LIMIT (8u*1024u*1024u)
/* Historical stage, not a visual display claim. */
enum {SMAGIC,SVERSION,SBYTES,SPID,SSTAGE,SERROR,SATTEMPTS,SFACTORY,SROUTER,SVIDEO,SINPUT,SCALLBACK,SVID,SINID,SBEFORE9,SBEFORE10,SREGISTERED,SPOPULATE,SREWRITES,SFALLBACK,SSETUP,SCODEC,SSTART,SSTOP,SCONFIG,SFOCUS,SFRAMES,SFRAMEBYTES,SSAVED,SCODECBYTES,SDROPPED,SACKS,SSESSION,SCHANNEL,SIOERROR,SWIREERROR,SBACKUP,STSLOW,STSHIGH,SLIMIT,SINSTALLED,SQUARANTINE,SKEYS};
struct stream_report { uint32_t w[128]; };
struct stream_native { struct factory_api object;int (*reg)(void*,void*);void (*focus)(void*,int,unsigned char);void (*ack)(void*,int,unsigned); };
#define TIMING_CAPACITY 2048u
struct stream_timing_record { uint32_t kind,session;uint64_t timestamp,monotonic_ns;uint32_t offset,requested,saved,reserved; };
struct stream_timing { uint32_t magic,version,pid,record_bytes,capacity,count,dropped,clock_error;struct stream_timing_record records[TIMING_CAPACITY]; };
_Static_assert(sizeof(struct stream_timing_record)==40,"timing record ABI");
_Static_assert(sizeof(struct stream_timing)==81952,"timing capture ABI");
struct stream_context { struct stream_native api;struct stream_report *report;void *router,*video,*input;struct stream_timing *timing;int fd,attempted,configured,active,session;_Atomic int armed,installed;pthread_mutex_t mutex;int probe_enabled;int probe_refresh_disabled;unsigned probe_requests;uint64_t probe_next_ns;int live_enabled,live_attempted;struct live_peer live;char live_path[128];uint32_t live_nonce[4];unsigned char *live_codec;unsigned live_codec_bytes; };
void stream_init(struct stream_context*,struct stream_report*,int);
void stream_arm(struct stream_context*,const struct stream_native*,void*);
int stream_install(struct stream_context*);
void stream_retire(struct stream_context*);
void stream_rollback(struct stream_context*);
#ifdef SECONDARY_TESTING
struct secondary_test_hooks {int (*populate)(void*,void*);int (*queue)(void*,unsigned char,void*,unsigned);int (*marshal)(void*,unsigned short,const void*,void*);void (*video_discovery)(void*,void*);void (*input_discovery)(void*,void*);};
void secondary_test_bind(const struct secondary_test_hooks*,const struct stream_native*,void*,struct stream_report*,int);
#endif
#endif
