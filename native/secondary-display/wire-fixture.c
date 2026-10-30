/* Host/QNX: cc -std=c99 -Wall -Wextra -Werror wire.c wire-fixture.c -o wire-fixture */
#include "wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static const unsigned char source[]={
 0,6,
 10,6,8,1,26,2,48,3,
 10,6,8,2,34,2,8,23,
 10,6,8,5,26,2,48,9,
 10,6,8,6,26,2,56,9,
 10,12,8,9,26,8,8,3,48,0,56,0,72,7,
 10,8,8,10,34,4,8,23,40,0,
 0x9d,6,1,2,3,4
};
static const unsigned char expected[]={
 0,6,
 10,8,8,1,26,4,48,0,56,0,
 10,8,8,2,34,4,8,23,40,0,
 10,6,8,5,26,2,48,9,
 10,6,8,6,26,2,56,9,
 10,12,8,9,26,8,8,3,72,7,48,1,56,1,
 10,8,8,10,34,4,8,23,40,1,
 0x9d,6,1,2,3,4
};
static void rejected(const unsigned char *p,unsigned n,unsigned cap)
{
 unsigned char out[16384]; unsigned got=99;
 assert(!cluster_wire_rewrite(p,n,out,cap,&got)); assert(got==0);
}
int main(void)
{
 unsigned char out[16384], bad[sizeof source+16], saved[sizeof source];
 const unsigned idpos[]={5,13,37,51};
 unsigned n=0,i;
 memcpy(saved,source,sizeof source);
 assert(cluster_wire_rewrite(source,sizeof source,out,sizeof out,&n));
 assert(n==sizeof expected && !memcmp(out,expected,n));
 assert(!memcmp(source,saved,sizeof source));
 assert(cluster_wire_rewrite(source,sizeof source,out,sizeof expected,&n));
 /* Repeating the transform preserves the exact canonical result. */
 assert(cluster_wire_rewrite(expected,sizeof expected,out,sizeof out,&n));
 assert(n==sizeof expected && !memcmp(out,expected,n));
 rejected(source,sizeof source,sizeof expected-1);
 rejected(source,sizeof source,16385);
 for(i=0;i<58;i++) rejected(source,i,sizeof out);
 for(i=0;i<4;i++) {
   memcpy(bad,source,sizeof source); bad[idpos[i]]=11;
   rejected(bad,sizeof source,sizeof out); /* each required association missing */
   memcpy(bad,source,sizeof source); bad[idpos[i]]=5;
   rejected(bad,sizeof source,sizeof out); /* occupied/duplicate ID */
 }
 memcpy(bad,source,sizeof source); bad[5]=0;
 rejected(bad,sizeof source,sizeof out);
 memcpy(bad,source,sizeof source); bad[5]=255;
 rejected(bad,sizeof source,sizeof out);
 memcpy(bad,source,sizeof source); bad[38]=34;
 rejected(bad,sizeof source,sizeof out); /* wrong descriptor kind */
 memcpy(bad,source,sizeof source); bad[38]=24;
 rejected(bad,sizeof source,sizeof out); /* descriptor wrong wire */
 memcpy(bad,source,sizeof source); bad[42]=50;
 rejected(bad,sizeof source,sizeof out); /* metadata wrong wire */
 memcpy(bad,source,sizeof source); bad[sizeof source]=0;
 rejected(bad,sizeof source+1,sizeof out);
 memcpy(bad,source,sizeof source); bad[sizeof source]=8;
 memset(bad+sizeof source+1,255,10);
 rejected(bad,sizeof source+11,sizeof out); /* overflowing uint64 */
 memcpy(bad,source,sizeof source); bad[sizeof source]=11;
 rejected(bad,sizeof source+1,sizeof out); /* group */
 memcpy(bad,source,sizeof source); bad[sizeof source]=18;
 bad[sizeof source+1]=127;
 rejected(bad,sizeof source+2,sizeof out); /* truncated bytes */
 memcpy(bad,source,sizeof source); bad[sizeof source]=17;
 rejected(bad,sizeof source+1,sizeof out); /* truncated fixed64 */
 memcpy(bad,source,sizeof source); bad[sizeof source]=0x80;
 rejected(bad,sizeof source+1,sizeof out); /* truncated tag */
 assert(!memcmp(source,saved,sizeof source));
 puts("wire fixtures passed"); return 0;
}
