#ifndef DELPHI_HANDBACK_H
#define DELPHI_HANDBACK_H
#define HB_CAP (188u*4096u)
struct handback { unsigned char packet[188],data[HB_CAP]; unsigned used,skip,bytes,flags,zeros,pes_left; int candidate,unbounded,have_pcr,ready; uint64_t pcr,anchor; };
static void hb_reset_pes(struct handback *h){h->bytes=h->flags=h->zeros=0;h->candidate=h->unbounded=0;h->pes_left=0;}
/* A complete fresh SPS/PPS/IDR PES is required. No raw timeout fallback. */
static int hb_packet(struct handback *h,const unsigned char *p){unsigned off,pid,j;int idx,afc=tl_header(p,&off,&idx);if(afc<0||idx<0)return -1;pid=((p[1]&31)<<8)|p[2];if((afc&2)&&p[4]&&(p[5]&0x80))return -1;
 if((afc&2)&&p[4]&&(p[5]&0x10)){if(idx!=3||p[4]<7)return -1;h->pcr=tl_pcr(p+6);h->have_pcr=1;}
 if(pid==17&&(afc&1)&&(p[1]&0x40)){
  if(h->candidate&&h->unbounded&&h->flags==7&&h->have_pcr){h->ready=1;return 1;}
  hb_reset_pes(h);if(!h->have_pcr)return 0;if(off+9>188||p[off]||p[off+1]||p[off+2]!=1||p[off+3]!=0xe0||off+9+p[off+8]>188)return -1;
  h->candidate=1;h->anchor=h->pcr;h->pes_left=((unsigned)p[off+4]<<8)|p[off+5];h->unbounded=!h->pes_left;if(!h->unbounded){unsigned header=3+p[off+8];if(h->pes_left<header)return -1;h->pes_left-=header;}off+=9+p[off+8];
 }
 if(!h->candidate)return 0;
 if(h->bytes>HB_CAP-188){hb_reset_pes(h);return 0;}memcpy(h->data+h->bytes,p,188);h->bytes+=188;
 if(pid==17&&(afc&1)){unsigned end=188;if(!h->unbounded&&end-off>h->pes_left)end=off+h->pes_left;for(j=off;j<end;j++){unsigned v=p[j];if(h->zeros>=2&&h->zeros<256&&v==1){h->zeros=256;continue;}if(h->zeros==256){unsigned nal=v&31;if(nal==7)h->flags=1;else if(nal==8&&(h->flags&1))h->flags|=2;else if(nal==5&&(h->flags&3)==3)h->flags|=4;h->zeros=0;}if(!v){if(h->zeros<3)h->zeros++;}else h->zeros=0;}
  if(!h->unbounded){h->pes_left-=end-off;if(!h->pes_left){if(h->flags==7&&h->have_pcr){h->ready=1;return 1;}hb_reset_pes(h);}}
 }return 0;
}
#endif
