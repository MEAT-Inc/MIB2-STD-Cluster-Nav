#include "libc-profile.h"
#include <string.h>
#include <limits.h>
int replay_libc_validate(const struct replay_libc_profile *p,const uint32_t f[3],int (*rd)(void *,uint32_t,void *,unsigned),void *ctx,uint32_t *out){uint32_t b;unsigned i;unsigned char h[20],code[32];if(out)*out=0;if(!p||!f||!rd||!out||f[1]<p->offset[1])return -1;b=f[1]-p->offset[1];if(!b||(b&4095)||b>UINT32_MAX-20)return -1;for(i=0;i<3;i++){if(p->offset[i]>UINT32_MAX-b||f[i]!=b+p->offset[i]||f[i]>UINT32_MAX-32)return -1;}if(rd(ctx,b,h,sizeof(h))||memcmp(h,"\177ELF\1\1\1",7)||h[16]!=3||h[17]||h[18]!=40||h[19])return -1;for(i=0;i<3;i++)if(rd(ctx,f[i],code,sizeof(code))||memcmp(code,p->code[i],sizeof(code)))return -1;*out=b;return 0;}
