#ifndef OBS_FIXTURE_H
#define OBS_FIXTURE_H
#include <stdint.h>
#include "observer.h"
extern "C" uint32_t registration(uintptr_t, uintptr_t, uint32_t, uint32_t, uint32_t, uint32_t) __asm__(OBS_SYMBOL);
extern "C" unsigned fixture_calls(void);
struct fixture_exception { int value; };
#define ARG2 UINT32_C(0x5a5a1234)
#define ARG3 UINT32_C(0xa5a55678)
#define ARG4 UINT32_C(0x13572468)
#define ARG5 UINT32_C(0x24681357)
#endif
