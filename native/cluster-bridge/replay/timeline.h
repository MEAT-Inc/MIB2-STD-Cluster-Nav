#ifndef DELPHI_TIMELINE_H
#define DELPHI_TIMELINE_H
#include <stdint.h>
#include <string.h>
#define TL_MASK UINT64_C(0x1ffffffff)
struct replay_timeline { unsigned cc[4],seen,used; unsigned char pending[188]; uint64_t pcr,ms,offset; int has_pcr; };
static int tl_index(unsigned pid){switch(pid){case 0:return 0;case 16:return 1;case 17:return 2;case 4096:return 3;default:return -1;}}
static uint64_t tl_stamp(const unsigned char *p){return ((uint64_t)((p[0]>>1)&7)<<30)|((uint64_t)p[1]<<22)|((uint64_t)(p[2]>>1)<<15)|((uint64_t)p[3]<<7)|(p[4]>>1);}
static void tl_put_stamp(unsigned char *p,uint64_t v){v&=TL_MASK;p[0]=(p[0]&0xf0)|((v>>29)&14)|1;p[1]=v>>22;p[2]=((v>>14)&254)|1;p[3]=v>>7;p[4]=((v<<1)&254)|1;}
static uint64_t tl_pcr(const unsigned char *p){return ((uint64_t)p[0]<<25)|((uint64_t)p[1]<<17)|((uint64_t)p[2]<<9)|((uint64_t)p[3]<<1)|(p[4]>>7);}
static void tl_put_pcr(unsigned char *p,uint64_t v){v&=TL_MASK;p[0]=v>>25;p[1]=v>>17;p[2]=v>>9;p[3]=v>>1;p[4]=(p[4]&127)|((v&1)<<7);}
static int tl_header(const unsigned char *p,unsigned *off,int *idx){unsigned afc=(p[3]>>4)&3;*off=4;if(p[0]!=0x47||(p[1]&0x80)||(p[3]&0xc0)||!afc)return -1;*idx=tl_index(((p[1]&31)<<8)|p[2]);if(afc&2){*off=5+p[4];if(*off>188)return -1;}if((afc&1)&&*off>=188)return -1;return (int)afc;}
static int tl_observe(struct replay_timeline *t,const unsigned char *p,uint64_t ms){unsigned off;int idx,afc=tl_header(p,&off,&idx);if(afc<0)return -1;if(idx<0)return 0;t->cc[idx]=p[3]&15;t->seen|=1u<<idx;if((afc&2)&&p[4]&&p[5]&0x10){if(idx!=3||p[4]<7)return -1;t->pcr=tl_pcr(p+6);t->ms=ms;t->has_pcr=1;}return 0;}
/* Native writes may split a TS packet into header/payload fragments. */
static int tl_feed(struct replay_timeline *t,const unsigned char *p,size_t n,uint64_t ms){if(n>1048576)return -1;while(n){size_t take=188-t->used;if(take>n)take=n;memcpy(t->pending+t->used,p,take);t->used+=(unsigned)take;p+=take;n-=take;if(t->used==188){t->used=0;if(tl_observe(t,t->pending,ms))return -1;}}return 0;}
static int tl_ready(const struct replay_timeline *t,uint64_t ms){return !t->used&&t->seen==15&&t->has_pcr&&ms>=t->ms&&ms-t->ms<=1000;}
static int tl_start(struct replay_timeline *t,uint64_t ms){if(!tl_ready(t,ms))return -1;/* Continue the accepted live clock, including time since its last PCR. */t->offset=(t->pcr+(ms-t->ms)*90+90)&TL_MASK;return 0;}
/* Factory startup uses payload-only MPEG-TS null packets as padding. */
static inline int tl_factory_null(const unsigned char *p,int afc){return afc==1&&(p[1]&0x5f)==0x1f&&p[2]==0xff;}
static int tl_rewrite_impl(struct replay_timeline *t,const unsigned char *src,unsigned char *p,int factory){unsigned off;int idx,afc;memcpy(p,src,188);afc=tl_header(p,&off,&idx);if(afc<0)return -1;
 if(factory&&tl_factory_null(p,afc))return 0;
 if(idx<0||!(t->seen&(1u<<idx)))return -1;
/* Discontinuity/reset markers are forbidden on this continuous handoff. */
 if((afc&2)&&p[4]&&(p[5]&0x80))return -1;
 if(afc&1){t->cc[idx]=(t->cc[idx]+1)&15;}p[3]=(p[3]&0xf0)|t->cc[idx];
 if((afc&2)&&p[4]&&(p[5]&0x10)){if(idx!=3||p[4]<7)return -1;tl_put_pcr(p+6,(tl_pcr(p+6)+t->offset)&TL_MASK);}
 if(idx==2&&(afc&1)&&(p[1]&0x40)){unsigned flags;unsigned char *q=p+off;if(off+9>188||q[0]||q[1]||q[2]!=1||q[3]!=0xe0)return -1;flags=q[7]>>6;if((flags!=2&&flags!=3)||q[8]<(flags==3?10:5)||off+9+q[8]>188)return -1;if((q[9]&0xf1)!=(flags==3?0x31:0x21)||(q[11]&1)!=1||(q[13]&1)!=1)return -1;tl_put_stamp(q+9,tl_stamp(q+9)+t->offset);if(flags==3){if((q[14]&0xf1)!=0x11||(q[16]&1)!=1||(q[18]&1)!=1)return -1;tl_put_stamp(q+14,tl_stamp(q+14)+t->offset);}}
 return 0;
}
static inline int tl_rewrite(struct replay_timeline *t,const unsigned char *src,unsigned char *p){return tl_rewrite_impl(t,src,p,0);}
static inline int tl_rewrite_factory(struct replay_timeline *t,const unsigned char *src,unsigned char *p){return tl_rewrite_impl(t,src,p,1);}
#endif
