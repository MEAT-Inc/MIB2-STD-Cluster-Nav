#include <stdint.h>
#include <errno.h>
static unsigned calls;
uint32_t registration(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__("_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase");
uint32_t registration(uintptr_t a,uintptr_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f) {
    ++calls;
    if (c!=0x12345678u || d!=0x87654321u || e!=0x55aa55aau || f!=0xaa55aa55u || errno!=ERANGE)
        return 0;
    errno=EDOM;
    return (uint32_t)(a^b)^0x80000001u;
}
unsigned smoke_native_calls(void) { return calls; }
