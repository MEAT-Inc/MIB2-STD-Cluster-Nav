#ifndef DELPHI_REPLAY_LIBC_PROFILE_H
#define DELPHI_REPLAY_LIBC_PROFILE_H
#include <stdint.h>
/* Entry order: open, write, close. Captured bytes must have no relocations. */
struct replay_libc_profile { uint32_t offset[3]; unsigned char code[3][32]; };
/* Read callback returns 0 on success, nonzero on failure. No process writes.
 * On failure *base is cleared; on success it is the validated mapping base. */
int replay_libc_validate(const struct replay_libc_profile *,const uint32_t functions[3],int (*read_bytes)(void *,uint32_t,void *,unsigned),void *,uint32_t *base);
#endif
