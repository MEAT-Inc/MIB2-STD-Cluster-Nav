#define _QNX_SOURCE 1
#include "display.h"
#include <dlfcn.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
extern uint32_t registration(uintptr_t,uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(OBS_SYMBOL);
extern uint32_t config(uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t) __asm__(CONFIG_SYMBOL);
extern uint32_t focus(uintptr_t,int,unsigned) __asm__(FOCUS_SYMBOL);
extern uint32_t queue(uintptr_t,unsigned,void*,unsigned) __asm__(QUEUE_SYMBOL);
extern unsigned smoke_native_calls(void),display_native_calls(unsigned);
static uint32_t call_config(void){errno=ERANGE;return config(0x13572468,0x11111111,0x22222222,0x33333333,0x44444444,0x55555555,0x66666666,0x87654321);}
int main(int argc,char **argv){
 unsigned i,total=4;unsigned char data[8]={0,6,10,4,8,1,24,3},wrong[8]={0,8,10,4,8,1,24,3};
 const struct display_file *(*view)(void)=0;void *symbol=dlsym(RTLD_DEFAULT,"delphi_display_view");
 int observed=argc==2&&strcmp(argv[1],"baseline");
 if(sizeof(symbol)!=sizeof(view))return 2;
 memcpy(&view,&symbol,sizeof(view));
 for(i=0;i<9;++i){errno=ERANGE;if(registration(0x1000+i,0x2000+i,0x12345678,0x87654321,0x55aa55aa,0xaa55aa55)!=0x80003001u||errno!=EDOM)return 3;}
 if(call_config()!=0xfedcba98||errno!=EDOM)return 4;
 errno=ERANGE;if(focus(0x13572468,-2,1)!=0x80000002||errno!=E2BIG)return 5;
 errno=ERANGE;if(queue(0x24681357,0,data,8)!=0x80000003||errno!=EAGAIN)return 6;
 errno=ERANGE;if(queue(0x24681357,0,wrong,8)!=0x80000003||errno!=EAGAIN)return 7;
 errno=ERANGE;if(queue(0x24681357,0,(void*)1,4097)!=0x80000003||errno!=EAGAIN)return 8;
 if(data[0]||data[1]!=6||wrong[1]!=8||smoke_native_calls()!=9)return 9;
 if(argc==2&&!strcmp(argv[1],"full")){for(i=0;i<35;++i)if(call_config()!=0xfedcba98||errno!=EDOM)return 10;total+=35;}
 if(display_native_calls(1)!=(total==4?1:36)||display_native_calls(2)!=1||display_native_calls(3)!=3)return 11;
 if(observed){const struct display_file *f;if(!view)return 12;f=view();
  if(!strcmp(argv[1],"disabled")){if(f->header.status!=(OBS_READY|OBS_LOG_DISABLED)||f->header.count)return 13;}
  else {
   const struct display_record *r=f->records;
   if(f->header.magic!=DISPLAY_MAGIC||f->header.status!=OBS_READY||!f->header.count||f->header.count>32||f->header.count+f->header.dropped!=total)return 14;
   if(!strcmp(argv[1],"observed")&&f->header.count==4){
    if(r[0].event!=1||r[0].argc!=8||r[0].args[0]!=0x13572468||r[0].args[7]!=0x87654321||r[1].event!=2||r[1].args[1]!=0xfffffffe||r[2].event!=3||r[2].payload_bytes!=8||memcmp(r[2].payload,data,8)||r[3].flags!=1||r[3].payload_bytes)return 15;
    printf("DISPLAY_HEADER ");for(i=0;i<128;++i)printf("%02x",((const unsigned char*)&f->header)[i]);puts("");
    for(i=0;i<4;++i){unsigned j;printf("DISPLAY_RECORD ");for(j=0;j<64+r[i].payload_bytes;++j)printf("%02x",((const unsigned char*)&r[i])[j]);puts("");for(j=r[i].payload_bytes;j<4096;++j)if(r[i].payload[j])return 16;}
    for(i=4*4160;i<32*4160;++i)if(((const unsigned char*)f->records)[i])return 17;
    puts("DISPLAY_ZERO_TAILS_OK");
   }
   printf("DISPLAY_LOG count=%u dropped=%u\n",f->header.count,f->header.dropped);
  }
 }else if(view)return 18;
 printf("DISPLAY_FIXTURE_PASS mode=%s\n",argv[1]);return 0;
}
