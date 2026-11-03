/* Offline only. Records: LE u32 length,u32 flags,u64 relative_ms,payload.
 * flags=0: complete Annex B AU; flags=1: explicit tick, length must be zero.
 * No implicit clocks, scheduling, endpoint access, or output retry. */
#include "mux.h"
#include <stdio.h>
#include <string.h>
static unsigned char au[CLUSTER_MUX_MAX_AU];
static uint32_t le32(const unsigned char *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t le64(const unsigned char *p){return (uint64_t)le32(p)|((uint64_t)le32(p+4)<<32);}
static int output(void *v,const unsigned char *p,size_t n){return (int)fwrite(p,1,n,(FILE *)v);}
int main(int argc,char **argv){
 FILE *in,*out;struct cluster_mux m;unsigned char h[16];size_t got;uint32_t n,flags;int result=1;
 if(argc!=3 || !strcmp(argv[1],argv[2])){fprintf(stderr,"usage: mux-file input.records output.ts (distinct files)\n");return 2;}
 in=fopen(argv[1],"rb");if(!in){perror("input");return 2;}
 out=fopen(argv[2],"wb");if(!out){perror("output");fclose(in);return 2;}
 cluster_mux_init(&m,output,out);
 for(;;){
  got=fread(h,1,sizeof(h),in);
  if(!got){if(!ferror(in)&&m.started&&!m.failed)result=0;break;}
  if(got!=sizeof(h))break;
  n=le32(h);flags=le32(h+4);
  if(flags==1){if(n || cluster_mux_tick(&m,le64(h+8))<0)break;continue;}
  if(flags || !n || n>sizeof(au) || fread(au,1,n,in)!=n)break;
  if(cluster_mux_push(&m,au,n,le64(h+8))<0)break;
 }
 if(fclose(in))result=1;
 if(fclose(out))result=1;
 if(result)fprintf(stderr,"mux-file: invalid input or output failure; partial output must be discarded\n");
 return result;
}
