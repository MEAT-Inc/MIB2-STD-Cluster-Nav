#define _GNU_SOURCE 1
#include "fixture.h"
#include <errno.h>
#include <dlfcn.h>
#include <setjmp.h>
#include <stdlib.h>
static unsigned calls;
extern "C" unsigned fixture_calls(void) { return __atomic_load_n(&calls, __ATOMIC_RELAXED); }
#ifdef FIXTURE_ARM_ENTRY
#define PROVIDER_ENTRY fixture_native_registration
#else
#define PROVIDER_ENTRY registration
#endif
extern "C" uint32_t PROVIDER_ENTRY(uintptr_t a, uintptr_t b, uint32_t c, uint32_t d, uint32_t e, uint32_t f) {
    __atomic_fetch_add(&calls, 1, __ATOMIC_RELAXED);
    if (c != ARG2 || d != ARG3 || e != ARG4 || f != ARG5 || errno != ERANGE) abort();
    if (a == UINT32_C(0xeeee0001)) throw fixture_exception{99};
    if (a == UINT32_C(0xeeee0002)) siglongjmp(*(sigjmp_buf *)b, 7);
    if (a == UINT32_C(0xeeee0003)) {
        typedef uint32_t (*fn)(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t);
        fn nested = (fn)dlsym(RTLD_DEFAULT, OBS_SYMBOL);
        if (!nested) abort();
        errno = ERANGE;
        return nested(0x1234, 0x5678, ARG2, ARG3, ARG4, ARG5);
    }
    errno = EDOM;
    return (uint32_t)(a ^ b) ^ UINT32_C(0x80000001);
}
