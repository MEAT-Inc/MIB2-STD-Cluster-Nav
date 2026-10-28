#ifndef DELPHI_PROBE_H
#define DELPHI_PROBE_H
#include <stddef.h>
#include <stdint.h>
#define REG_SYMBOL "_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase"
#define PROBE_LIMIT 16
/* Synthetic ABI experiment only. This declaration is NOT a recovered C++ ABI. */
typedef uint32_t (*register_fn)(void *, void *);
uint32_t probe_register(void *, void *) __asm__(REG_SYMBOL);
struct probe_record { uintptr_t receiver, endpoint; uint32_t result; };
struct probe_snapshot { uint32_t version, ready, count, dropped; struct probe_record records[PROBE_LIMIT]; };
#endif
