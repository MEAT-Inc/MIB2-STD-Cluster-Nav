#include "startup.h"
#include "mux.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static unsigned char data[STARTUP_BYTES],key[LIVE_AU_LIMIT],input[LIVE_AU_LIMIT],output[LIVE_AU_LIMIT];
static ssize_t save(void *p,const void *b,size_t n){return fwrite(b,1,n,p)==n?(ssize_t)n:-1;}
static int read_frame(FILE *f,uint64_t *ms,uint32_t *n,uint32_t *flags){unsigned char h[16];size_t got=fread(h,1,16,f);if(!got)return 0;if(got!=16)return -1;memcpy(ms,h,8);memcpy(n,h+8,4);memcpy(flags,h+12,4);if(!*n||*n>LIVE_AU_LIMIT||fread(input,1,*n,f)!=*n)return -1;return 1;}
int main(int argc,char **argv){struct live_startup s;struct live_mux m;FILE *in,*out;uint64_t ms=0,next;uint32_t n,flags;unsigned bytes,oflags;int have,boot,rc;if(argc!=3)return 2;in=fopen(argv[1],"rb");out=fopen(argv[2],"wb");if(!in||!out)return 3;startup_init(&s,data,key);live_mux_init(&m,save,out);have=read_frame(in,&next,&n,&flags);while(have||startup_pending(&s)){if(have<0||ms>121000)return 4;while(have&&next<=ms){if(startup_push(&s,input,n,flags,next))return 5;have=read_frame(in,&next,&n,&flags);if(have<0)return 6;}while((rc=startup_pop(&s,ms,output,sizeof(output),&bytes,&oflags,&boot))>0)if(live_mux_push(&m,output,bytes,oflags,ms)!=1)return 7;if(rc<0||live_mux_tick(&m,ms))return 8;ms++;}fclose(in);if(fclose(out))return 9;printf("LIVE_STARTUP_FILE_PASS source_frames=%u bootstrap_frames=%u peak_bytes=%u peak_frames=%u delay_ms=%u\n",s.emitted,s.repeats,s.peak_bytes,s.peak_frames,STARTUP_DELAY_MS);return 0;}
