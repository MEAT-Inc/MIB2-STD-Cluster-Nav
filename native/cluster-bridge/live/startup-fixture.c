#include "startup.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"STARTUP_FAIL line=%d\n",__LINE__);exit(1);}}while(0)
static unsigned char data[STARTUP_BYTES],key[LIVE_AU_LIMIT],out[LIVE_AU_LIMIT],au[LIVE_AU_LIMIT];
int main(void){struct live_startup s;unsigned n,f,i;int boot;startup_init(&s,data,key);memset(au,0x5a,sizeof(au));CHECK(startup_push(&s,au,10,8,0)<0);CHECK(!startup_push(&s,au,10,31,0));for(i=1;i<20;i++){au[0]=i;CHECK(!startup_push(&s,au,10,8,i*10));}for(i=0;i<3;i++){CHECK(startup_pop(&s,i*333,out,sizeof(out),&n,&f,&boot)==1&&boot&&n==10&&f==31&&out[0]==0x5a);}CHECK(!startup_pop(&s,999,out,sizeof(out),&n,&f,&boot));for(i=0;i<20;i++){CHECK(startup_pop(&s,1000+i*10,out,sizeof(out),&n,&f,&boot)==1&&!boot&&out[0]==(i?i:0x5a));}CHECK(!startup_pending(&s)&&s.emitted==20&&s.repeats==3);
 startup_init(&s,data,key);for(i=0;i<4;i++){memset(au,i,sizeof(au));CHECK(!startup_push(&s,au,sizeof(au),31,0));}CHECK(startup_push(&s,au,1,8,0)<0&&s.overflows==1);for(i=0;i<4;i++)CHECK(startup_pop(&s,1000,out,sizeof(out),&n,&f,&boot)==1&&out[0]==i&&out[n-1]==i);CHECK(!startup_push(&s,au,123,8,1000));CHECK(startup_pop(&s,2000,out,sizeof(out),&n,&f,&boot)==1&&n==123);
 startup_init(&s,data,key);for(i=0;i<64;i++)CHECK(!startup_push(&s,au,1,31,0));CHECK(startup_push(&s,au,1,8,0)<0);puts("LIVE_STARTUP_QNX_PASS first_idr_repeated=3 dependent_frames_delayed=1 source_order_bytes_preserved=1 byte_slot_bounds=1 ring_wrap=1");return 0;}
