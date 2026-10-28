#include "probe.h"
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>
extern unsigned probe_provider_calls(void);
static unsigned receiver, endpoint;
int main(int argc, char **argv) {
    unsigned i;
    int expected_observer = argc == 2 && (strcmp(argv[1], "--preloaded") == 0 || strcmp(argv[1], "--linked") == 0);
    const struct probe_snapshot *(*snapshot)(void) = 0;
    void *symbol = dlsym(RTLD_DEFAULT, "probe_observer_snapshot");
    uint32_t expected = (uint32_t)((uintptr_t)&receiver ^ (uintptr_t)&endpoint) ^ UINT32_C(0x80000001);
    if (argc > 2 || (argc == 2 && !expected_observer)) return 2;
    if (sizeof(symbol) != sizeof(snapshot)) return 3;
    memcpy(&snapshot, &symbol, sizeof(snapshot));
    if ((snapshot != 0) != expected_observer) return 4;
    for (i = 0; i < PROBE_LIMIT + 3; ++i)
        if (probe_register(&receiver, &endpoint) != expected) return 5;
    if (probe_provider_calls() != PROBE_LIMIT + 3) return 6;
    if (snapshot) {
        const struct probe_snapshot *s = snapshot();
        if (s->version != 1 || !s->ready || s->count != PROBE_LIMIT || s->dropped != 3) return 7;
        for (i = 0; i < s->count; ++i)
            if (s->records[i].receiver != (uintptr_t)&receiver ||
                s->records[i].endpoint != (uintptr_t)&endpoint ||
                s->records[i].result != expected) return 8;
    }
    printf("DELPHI_PROBE_PASS mode=%s calls=%u bounded_records=%u drops=%u\n",
           snapshot ? argv[1] + 2 : "baseline", probe_provider_calls(),
           snapshot ? snapshot()->count : 0, snapshot ? snapshot()->dropped : 0);
    return 0;
}
