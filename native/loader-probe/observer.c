#include "probe.h"
#include <dlfcn.h>
#include <string.h>
#include <unistd.h>
static register_fn next_register;
static struct probe_snapshot state;
/* Single-thread fixture: no allocations or I/O within the successful wrapper.
 * No vendor object access. NOT a production concurrent logger or car shim. */
__attribute__((constructor)) static void initialize(void) {
    void *symbol = dlsym(RTLD_NEXT, REG_SYMBOL);
    /* POSIX dlsym function conversion; reject unsupported pointer sizes. */
    if (sizeof(symbol) == sizeof(next_register))
        memcpy(&next_register, &symbol, sizeof(next_register));
    state.version = 1;
    state.ready = next_register != 0 && next_register != probe_register;
}
uint32_t probe_register(void *receiver, void *endpoint) {
    uint32_t result;
    if (!state.ready) _exit(90); /* Synthetic test fails closed, never deploy this. */
    result = next_register(receiver, endpoint);
    if (state.count < PROBE_LIMIT) {
        struct probe_record *r = &state.records[state.count++];
        r->receiver = (uintptr_t)receiver;
        r->endpoint = (uintptr_t)endpoint;
        r->result = result;
    } else if (state.dropped != UINT32_MAX) ++state.dropped;
    return result;
}
const struct probe_snapshot *probe_observer_snapshot(void) { return &state; }
