#ifndef DELPHI_OBSERVER_H
#define DELPHI_OBSERVER_H
#include <stdint.h>
#define OBS_SYMBOL "_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase"
#define OBS_CAPACITY 1024u
#define OBS_THREAD_SLOTS 64u
#define OBS_MAGIC 0x314f4c44u /* DLO1, little endian */
#define OBS_VERSION 1u
#define OBS_READY 1u
#define OBS_LOG_DISABLED 2u
#define OBS_DROP_INEXACT 1u
#define OBS_THREAD_UNTRACKED 1u
struct obs_record {
    uint32_t sequence, thread, thread_sequence, receiver, endpoint, caller, flags, committed;
};
struct obs_header {
    uint32_t magic, version, header_bytes, record_bytes, capacity, pointer_bytes;
    uint32_t pid, native_address, module_base, status, count, dropped;
    uint32_t drop_flags, lock, reserved[18];
};
struct obs_file { struct obs_header header; struct obs_record records[OBS_CAPACITY]; };
/* This API is for cooperating diagnostic programs, never pointer/object decoding.
 * The shared file is append-only. Consumers must validate committed records. */
const struct obs_file *delphi_observer_view(void);
#endif
