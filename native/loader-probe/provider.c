#include "probe.h"
static unsigned calls;
uint32_t probe_register(void *receiver, void *endpoint) {
    ++calls;
    return (uint32_t)((uintptr_t)receiver ^ (uintptr_t)endpoint) ^ UINT32_C(0x80000001);
}
unsigned probe_provider_calls(void) { return calls; }
