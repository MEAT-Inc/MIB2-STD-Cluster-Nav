#include "libc-profile.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"LIBC_PROFILE_FAIL line=%d\n",__LINE__);exit(1);}}while(0)
static unsigned char memory[4096];
static struct replay_libc_profile p;
static uint32_t f[3],base;
static int fail_read;
static int rd(void *ctx,uint32_t a,void *out,unsigned n){(void)ctx;if(fail_read||a<0x100000||a-0x100000>sizeof(memory)||n>sizeof(memory)-(a-0x100000))return -1;memcpy(out,memory+a-0x100000,n);return 0;}
static void reset(void){unsigned i,j;memset(memory,0,sizeof(memory));memcpy(memory,"\177ELF\1\1\1",7);memory[16]=3;memory[18]=40;fail_read=0;for(i=0;i<3;i++){p.offset[i]=(i+1)*0x100;f[i]=0x100000+p.offset[i];for(j=0;j<32;j++)memory[p.offset[i]+j]=p.code[i][j]=(unsigned char)(i*32+j);}base=123;}
static void bad(void){CHECK(replay_libc_validate(&p,f,rd,0,&base)==-1&&base==0);}
int main(void){reset();CHECK(!replay_libc_validate(&p,f,rd,0,&base)&&base==0x100000);reset();p.offset[0]++;bad();reset();p.code[2][31]^=1;bad();reset();memory[0]=0;bad();reset();memory[5]=2;bad();reset();memory[16]=2;bad();reset();memory[18]=3;bad();reset();fail_read=1;bad();reset();f[1]=p.offset[1]-1;bad();reset();f[1]++;bad();reset();f[1]=p.offset[1];bad();reset();p.offset[0]=0xffffffffu;bad();reset();f[0]=0xfffffff0u;p.offset[0]=f[0]-0x100000;bad();reset();f[2]+=4096;bad();reset();CHECK(replay_libc_validate(0,f,rd,0,&base)==-1&&base==0);base=123;CHECK(replay_libc_validate(&p,0,rd,0,&base)==-1&&base==0);base=123;CHECK(replay_libc_validate(&p,f,0,0,&base)==-1&&base==0);CHECK(replay_libc_validate(&p,f,rd,0,0)==-1);puts("REPLAY_LIBC_PROFILE_PASS relative_symbols=1 elf32_arm_dyn=1 code32=1 bounds=1 read_failure=1");return 0;}
