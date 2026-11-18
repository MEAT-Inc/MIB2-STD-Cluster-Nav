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
#define STALL_EXT_WORDS 209
/* Replay inserts its worker before NavMain. Exact second captured fault path:
 * AAF SIGSEGV reporting through the native logger instead of printf.
 * Thread2/printf remains the original guard; thread3/logger is separately pinned. */
static int stall_blob_tid(const uint32_t w[STALL_EXT_WORDS],const uint32_t m[2],uint32_t sp,uint32_t pid,uint32_t tid) {
 uint32_t owner=((pid&0x7fffu)<<16)|tid;
 if(tid==2)return stall_blob(w,m,sp,pid);
 if(tid!=3)return 0;
 int common=m[0]==0x80000000u&&(m[1]&0x7fffffffu)==owner&&
 w[0]==0x1028088&&w[10]==0x1338f4&&w[28]==0x133704&&w[46]==0x3df1dc;
 if(!common)return 0;
 /* Separately captured unarmed live teardown: __flist_dequeue_bin writes
  * through a null next-link while removing the coalesced free-list node.
  * Saved r0 is chunk+corrupted size; r1/r2/r3 links are zero. Exact signal,
  * caller, frame layout, arena registers and same-owner logger wait required. */
 if(w[56]==11&&w[57]==0x10278a8&&w[58]==4&&w[59]==2&&w[60]==0&&
    w[71]==11&&w[72]==2&&w[73]==0&&w[74]==11&&w[75]==0x10278a8&&w[76]==4&&
    w[104]==0&&w[105]==0&&w[106]==0&&w[108]==0x1075a00&&w[109]==0x1078ac8&&w[115]==0x10760cc&&
    w[116]==sp+0x2f4&&w[117]==0x10264b8&&w[118]==0x10278a8&&w[208]==0x1b8f2c&&
    w[107]&&w[110]&&w[107]<0xc0000000u&&w[110]<0xc0000000u&&
    (uint64_t)w[107]+w[110]<0xc0000000u&&w[103]==w[107]+w[110]&&w[107]==w[112])return 1;
 return
 w[56]==11&&w[57]==0x1026384&&w[58]==w[76]&&w[59]==1&&w[60]==0&&
 w[71]==11&&w[72]==1&&w[73]==0&&w[74]==11&&w[75]==0x1026384&&
 w[118]==0x1026384&&w[117]==0x1027fd4&&w[116]==sp+0x2f4&&
 w[208]==0x1b8f2c&&w[76]&&w[76]<0xc0000000u&&w[76]==w[107]+w[110];
}
#endif
