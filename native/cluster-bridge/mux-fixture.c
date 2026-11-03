/* Independent TS/PES decoder and boundary/failure tests; no firmware needed. */
#include "mux.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned char au[CLUSTER_MUX_MAX_AU+1];
static unsigned char pes[CLUSTER_MUX_MAX_AU+32];
struct sink {unsigned count,fail_at,psi[2],pcr_count;int cc[3];size_t pes_n;uint64_t expected_ms;};
static uint32_t crc(const unsigned char *p,size_t n){uint32_t v=0xffffffffu;unsigned j;while(n--){v^=(uint32_t)*p++<<24;for(j=0;j<8;++j)v=(v<<1)^((v&0x80000000u)?0x04c11db7u:0);}return v;}
static uint64_t ts(const unsigned char *p){assert((p[0]&1)&&(p[2]&1)&&(p[4]&1));return ((uint64_t)(p[0]&14)<<29)|((uint64_t)p[1]<<22)|((uint64_t)(p[2]&254)<<14)|((uint64_t)p[3]<<7)|(p[4]>>1);}
static int collect(void *v,const unsigned char *p,size_t n){
 struct sink *s=v;unsigned pid,afc,cc,slot,section,j;size_t off=4;uint64_t base;
 assert(n==188);++s->count;if(s->fail_at==s->count)return 17;
 assert(p[0]==0x47 && !(p[1]&0x80));pid=((p[1]&31)<<8)|p[2];afc=(p[3]>>4)&3;cc=p[3]&15;assert(afc);
 if(afc&2){off=5+p[4];assert(off<=188);}
 if(pid==0x1000){assert(p[3]==0x20 && p[4]==183 && p[5]==0x10);base=((uint64_t)p[6]<<25)|((uint64_t)p[7]<<17)|((uint64_t)p[8]<<9)|((uint64_t)p[9]<<1)|(p[10]>>7);assert(base==((uint32_t)s->expected_ms*90u));assert((p[10]&127)==0x7e && p[11]==0);for(j=12;j<188;++j)assert(p[j]==0xff);++s->pcr_count;return 188;}
 assert(afc&1);slot=pid==0?0:pid==0x10?1:2;assert(pid==0 || pid==0x10 || pid==0x11);
 assert(cc==(unsigned)((s->cc[slot]+1)&15));s->cc[slot]=(int)cc;
 if(afc&2 && p[4]){assert(p[5]==0);for(j=6;j<off;++j)assert(p[j]==0xff);}
 if(pid==0x11){if(p[1]&64)assert(s->pes_n==0);assert(s->pes_n+188-off<=sizeof(pes));memcpy(pes+s->pes_n,p+off,188-off);s->pes_n+=188-off;}
 else{assert((p[1]&64)&&p[off++]==0);section=3+((p[off+1]&15)<<8)+p[off+2];assert(section==188-off && crc(p+off,section)==0);if(!pid){assert(p[off]==0 && p[off+10]==0xe0 && p[off+11]==0x10);}else{assert(p[off]==2 && p[off+8]==0xf0 && p[off+9]==0 && p[off+12]==0x1b && p[off+13]==0xe0 && p[off+14]==0x11);}++s->psi[slot];}
 return 188;
}
static void reset(struct cluster_mux *m,struct sink *s){memset(s,0,sizeof(*s));s->cc[0]=s->cc[1]=s->cc[2]=-1;cluster_mux_init(m,collect,s);}
static void make_au(size_t n,int idr){memset(au,0x88,n);au[0]=au[1]=au[2]=0;au[3]=1;au[4]=(unsigned char)(idr?0x65:0x41);}
static void check_pes(size_t n,uint64_t ms){uint32_t dts=(uint32_t)ms*90u,len=(uint32_t)n+13;assert(!memcmp(pes,"\0\0\1\xe0",4));assert((((unsigned)pes[4]<<8)|pes[5])==(len<=65535?len:0));assert(pes[6]==0x80&&pes[7]==0xc0&&pes[8]==10);assert((pes[9]>>4)==3&&(pes[14]>>4)==1);assert(ts(pes+9)==(uint64_t)dts+1 && ts(pes+14)==dts);assert(!memcmp(pes+19,au,n));}
int main(void){
 struct cluster_mux m;struct sink s;size_t sizes[]={5,164,165,166,349,65522,65523,CLUSTER_MUX_MAX_AU};unsigned i,count;uint64_t ms;
 reset(&m,&s);make_au(5,0);assert(cluster_mux_push(&m,au,5,0)==0 && !s.count);make_au(5,1);assert(cluster_mux_push(&m,au,5,0)==1);assert(s.pes_n==24);check_pes(5,0);
 reset(&m,&s);
 for(i=0;i<sizeof(sizes)/sizeof(sizes[0]);++i){ms=(uint64_t)i*40;s.expected_ms=ms;s.pes_n=0;make_au(sizes[i],i==0);assert(cluster_mux_push(&m,au,sizes[i],ms)==1);assert(s.pes_n==sizes[i]+19);check_pes(sizes[i],ms);}
 assert(s.cc[2]>=0); /* Large AU crosses continuity wraps; collector checks every packet. */
 reset(&m,&s);for(i=0;i<=664;i+=4){s.expected_ms=i;assert(cluster_mux_tick(&m,i)==1);}assert(s.psi[0]==3&&s.psi[1]==3&&s.pcr_count==21);
 reset(&m,&s);make_au(40,1);for(ms=47721858;ms<=47721860;++ms){s.expected_ms=ms;s.pes_n=0;assert(cluster_mux_push(&m,au,40,ms)==1);check_pes(40,ms);}s.expected_ms=UINT64_MAX;assert(cluster_mux_tick(&m,UINT64_MAX)==1);
 reset(&m,&s);make_au(1000,1);s.fail_at=5;assert(cluster_mux_push(&m,au,1000,0)==-1&&m.failed);count=s.count;assert(cluster_mux_push(&m,au,1000,1)==-1);assert(cluster_mux_tick(&m,2)==-1&&s.count==count);
 reset(&m,&s);s.expected_ms=5;assert(cluster_mux_tick(&m,5)==1);count=s.count;assert(cluster_mux_tick(&m,4)==-1&&s.count==count);
 reset(&m,&s);make_au(sizeof(au),1);assert(cluster_mux_push(&m,au,sizeof(au),0)==-1 && !s.count);
 reset(&m,&s);assert(cluster_mux_push(&m,0,0,0)==-1 && !s.count);
 reset(&m,&s);make_au(5,1);au[4]|=128;assert(cluster_mux_push(&m,au,5,0)==-1 && !s.count);
 reset(&m,&s);make_au(8,1);au[5]=au[6]=0;au[7]=1;assert(cluster_mux_push(&m,au,8,0)==-1 && !s.count);
 puts("CLUSTER_MUX_FIXTURE_PASS");return 0;
}
