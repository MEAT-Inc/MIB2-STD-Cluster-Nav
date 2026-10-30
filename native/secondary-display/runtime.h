#ifndef SECONDARY_RUNTIME_H
#define SECONDARY_RUNTIME_H
#include "../endpoint-factory/factory.h"
#include <pthread.h>
#define STREAM_MAGIC 0x31505253u
#define STREAM_LIMIT (8u*1024u*1024u)
/* Historical stage, not a visual display claim. */
enum {SMAGIC,SVERSION,SBYTES,SPID,SSTAGE,SERROR,SATTEMPTS,SFACTORY,SROUTER,SVIDEO,SINPUT,SCALLBACK,SVID,SINID,SBEFORE9,SBEFORE10,SREGISTERED,SPOPULATE,SREWRITES,SFALLBACK,SSETUP,SCODEC,SSTART,SSTOP,SCONFIG,SFOCUS,SFRAMES,SFRAMEBYTES,SSAVED,SCODECBYTES,SDROPPED,SACKS,SSESSION,SCHANNEL,SIOERROR,SWIREERROR,SBACKUP,STSLOW,STSHIGH,SLIMIT,SINSTALLED,SQUARANTINE,SKEYS};
struct stream_report { uint32_t w[128]; };
struct stream_native { struct factory_api object;int (*reg)(void*,void*);void (*focus)(void*,int,unsigned char);void (*ack)(void*,int,unsigned); };
struct stream_context { struct stream_native api;struct stream_report *report;void *router,*video,*input;int fd,attempted,configured,active,session;_Atomic int armed,installed;pthread_mutex_t mutex; };
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
