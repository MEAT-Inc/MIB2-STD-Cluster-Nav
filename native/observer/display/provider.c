#include "../smoke/provider.c"
#include "display.h"
#include <string.h>
static unsigned extra_calls[3];
uint32_t config(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(CONFIG_SYMBOL);
uint32_t focus(uintptr_t,int,unsigned) __asm__(FOCUS_SYMBOL);
uint32_t queue(uintptr_t,unsigned,void*,unsigned) __asm__(QUEUE_SYMBOL);
uint32_t config(uintptr_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h){
 ++extra_calls[0];if(a!=0x13572468||b!=0x11111111||c!=0x22222222||d!=0x33333333||e!=0x44444444||f!=0x55555555||g!=0x66666666||h!=0x87654321||errno!=ERANGE)return 0;
 errno=EDOM;return 0xfedcba98;
}
uint32_t focus(uintptr_t a,int b,unsigned c){++extra_calls[1];if(a!=0x13572468||b!=-2||c!=1||errno!=ERANGE)return 0;errno=E2BIG;return 0x80000002;}
uint32_t queue(uintptr_t a,unsigned b,void *c,unsigned d){++extra_calls[2];if(a!=0x24681357||b!=0||!c||errno!=ERANGE||!(d==8||d==4097))return 0;errno=EAGAIN;return 0x80000003;}
unsigned display_native_calls(unsigned event){return event>=1&&event<=3?extra_calls[event-1]:0;}
