#include "mux.h"
#include <string.h>
static const unsigned char pat[]={0x00,0xb0,0x0d,0x00,0x00,0xc1,0x00,0x00,0x00,0x01,0xe0,0x10,0x2d,0x50,0x98,0x1b};
static const unsigned char pmt[]={0x02,0xb0,0x21,0x00,0x01,0xc1,0x00,0x00,0xf0,0x00,0xf0,0x00,0x1b,0xe0,0x11,0xf0,0x0f,0x2a,0x07,0x7f,0xff,0x00,0x00,0x05,0xdd,0xdf,0x28,0x04,0x42,0x80,0x32,0x3f,0xfe,0xe6,0x1f,0x98};
static int fail(struct cluster_mux *m){m->failed=1;return -1;}
static int time_at(struct cluster_mux *m,uint64_t ms){
 if(m->failed)return -1;
 if(m->have_time && ms<m->last_ms)return fail(m);
 m->last_ms=ms;m->have_time=1;return 1;
}
static int emit(struct cluster_mux *m,const unsigned char *p){
 if(m->failed)return -1;
 if(!m->emit || m->emit(m->opaque,p,188)!=188)return fail(m);
 return 1;
}
/* Both spans are borrowed; at most one TS packet is assembled on the stack. */
static int payload(struct cluster_mux *m,unsigned pid,unsigned slot,
 const unsigned char *a,size_t na,const unsigned char *b,size_t nb,int start){
 unsigned char p[188];size_t n=na+nb,spare,pos;
 if(n>184)return fail(m);
 spare=184-n;p[0]=0x47;p[1]=(unsigned char)((pid>>8)|(start?0x40:0));p[2]=(unsigned char)pid;
 p[3]=(unsigned char)((spare?0x30:0x10)|m->cc[slot]);m->cc[slot]=(m->cc[slot]+1)&15;
 pos=4;
 if(spare){p[pos++]=(unsigned char)(spare-1);if(spare>1){p[pos++]=0;memset(p+pos,0xff,spare-2);pos+=spare-2;}}
 if(na)memcpy(p+pos,a,na);
 if(nb)memcpy(p+pos+na,b,nb);
 return emit(m,p);
}
void cluster_mux_init(struct cluster_mux *m,cluster_mux_emit cb,void *opaque){
 memset(m,0,sizeof(*m));m->emit=cb;m->opaque=opaque;
}
static int pcr(struct cluster_mux *m,uint64_t ms){
 unsigned char p[188];uint32_t base=(uint32_t)ms*90u;
 memset(p,0xff,sizeof(p));p[0]=0x47;p[1]=0x10;p[2]=0;p[3]=0x20;p[4]=183;p[5]=0x10;
 p[6]=(unsigned char)(base>>25);p[7]=(unsigned char)(base>>17);p[8]=(unsigned char)(base>>9);p[9]=(unsigned char)(base>>1);
 p[10]=(unsigned char)(((base&1u)<<7)|0x7e);p[11]=0;return emit(m,p);
}
int cluster_mux_tick(struct cluster_mux *m,uint64_t ms){
 unsigned char zero=0;
 if(time_at(m,ms)<0)return -1;
 if(!m->have_psi || ms-m->psi_ms>=332){
  if(payload(m,0,0,&zero,1,pat,sizeof(pat),1)<0)return -1;
  if(payload(m,0x10,1,&zero,1,pmt,sizeof(pmt),1)<0)return -1;
  m->psi_ms=ms;m->have_psi=1;
 }
 if(!m->have_pcr || ms-m->pcr_ms>=32){
  if(pcr(m,ms)<0)return -1;
  m->pcr_ms=ms;m->have_pcr=1;
 }
 return 1;
}
static void stamp(unsigned char *p,uint64_t v,unsigned prefix){
 p[0]=(unsigned char)(prefix|((v>>29)&14)|1);p[1]=(unsigned char)(v>>22);
 p[2]=(unsigned char)(((v>>14)&254)|1);p[3]=(unsigned char)(v>>7);
 p[4]=(unsigned char)(((v<<1)&254)|1);
}
/* Match non-overlapping three/four-byte Annex B prefixes, as the reference does. */
static unsigned prefix(const unsigned char *p,size_t n){
 if(n>=4 && p[0]==0 && p[1]==0 && p[2]==0 && p[3]==1)return 4;
 if(n>=3 && p[0]==0 && p[1]==0 && p[2]==1)return 3;
 return 0;
}
int cluster_mux_push(struct cluster_mux *m,const unsigned char *au,size_t n,uint64_t ms){
 unsigned char h[19];size_t i,pos,total,take,hn,an;unsigned k,slice=0,idr=0;uint32_t dts,len;
 if(time_at(m,ms)<0)return -1;
 if(!au || !n || n>CLUSTER_MUX_MAX_AU || !prefix(au,n))return fail(m);
 for(i=0;i<n;){k=prefix(au+i,n-i);if(!k){++i;continue;}
  i+=k;if(i==n || (au[i]&128))return fail(m);
  if((au[i]&31)==1)slice=1;
  if((au[i]&31)==5){slice=1;idr=1;}
 }
 if(!slice)return fail(m);
 if(!m->started && !idr)return 0;
 m->started=1;if(cluster_mux_tick(m,ms)<0)return -1;
 dts=(uint32_t)ms*90u;len=(uint32_t)n+13u;
 h[0]=0;h[1]=0;h[2]=1;h[3]=0xe0;
 h[4]=(unsigned char)(len<=65535?len>>8:0);h[5]=(unsigned char)(len<=65535?len:0);
 h[6]=0x80;h[7]=0xc0;h[8]=10;
 stamp(h+9,(uint64_t)dts+1,0x30);stamp(h+14,dts,0x10);
 total=n+sizeof(h);
 for(pos=0;pos<total;pos+=take){
  take=total-pos;if(take>184)take=184;
  hn=pos<sizeof(h)?sizeof(h)-pos:0;if(hn>take)hn=take;an=take-hn;
  if(payload(m,0x11,2,hn?h+pos:0,hn,an?au+(pos+hn-sizeof(h)):0,an,pos==0)<0)return -1;
 }
 return 1;
}
