#include "observer.h"
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
extern int fixture_abi_call(void *);
struct capture { uint32_t args[4]; uint64_t vfp[8]; uint32_t sp; };
int main(void) {
    struct capture captured = {{0},{0},0};
    unsigned i;
    errno = ERANGE;
    if (!fixture_abi_call(&captured)) return 1;
    if (captured.args[0] != UINT32_C(0xeeee0004) || captured.args[1] != (uint32_t)(uintptr_t)&captured ||
        captured.args[2] != UINT32_C(0x5a5a1234) || captured.args[3] != UINT32_C(0xa5a55678) || captured.sp % 8) return 2;
    for (i=0;i<8;++i) if (captured.vfp[i] != UINT64_C(0x1122334400000000)+i) return 3;
    puts("OBSERVER_ARM_ABI_PASS args=r0-r3+stack callee_saved=r4-r11 vfp=d0-d7 alignment=8");
    return 0;
}
