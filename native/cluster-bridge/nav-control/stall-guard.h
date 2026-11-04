#ifndef NAV_STALL_GUARD_H
#define NAV_STALL_GUARD_H
#include <stdint.h>
#define STALL_WORDS 193
/* Exact MU0890 nested SIGSEGV/free signal-frame signature, recovered on car.
 * No repair or mutation: match the already-faulted teardown before recovery. */
static int stall_blob(const uint32_t w[STALL_WORDS],const uint32_t m[2],uint32_t sp,uint32_t pid) {
 uint32_t owner=((pid&0x7fffu)<<16)|2u;
 return m[0]==0x80000000u&&(m[1]&0x7fffffffu)==owner&&
 w[0]==0x1028088&&w[10]==0x105708c&&w[26]==0x3df0a4&&
 w[55]==11&&w[56]==1&&w[57]==0&&w[59]==0x1026384&&
 w[102]==0x1026384&&w[101]==0x1027fd4&&w[100]==sp+0x2b4&&
 w[192]==0x1b8f2c&&w[60]&&w[60]<0xc0000000u&&w[60]==w[91]+w[94];
}
#endif
