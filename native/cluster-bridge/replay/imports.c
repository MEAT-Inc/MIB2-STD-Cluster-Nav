#include "imports.h"
#include <stddef.h>
static int descriptors(struct replay_import *p,unsigned n){unsigned i,j;if(!p||n!=3)return -1;for(i=0;i<n;i++){if(!p[i].slot||((uintptr_t)p[i].slot&3)||!p[i].native||!p[i].lazy||!p[i].replacement)return -1;for(j=0;j<i;j++)if(p[j].slot==p[i].slot)return -1;}return 0;}
static int rollback(struct replay_import *p,unsigned n){int failed=0;while(n){uint32_t expected;--n;expected=p[n].replacement;if(!__atomic_compare_exchange_n(p[n].slot,&expected,p[n].saved,0,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST)&&expected!=p[n].saved)failed=1;}return failed?-2:0;}
int replay_imports_install(struct replay_import *p,unsigned n){unsigned i;if(descriptors(p,n))return -1;for(i=0;i<n;i++){uint32_t v=__atomic_load_n(p[i].slot,__ATOMIC_SEQ_CST);if(v!=p[i].native&&v!=p[i].lazy)return -1;if(v==p[i].replacement)return -1;}
 for(i=0;i<n;i++)p[i].saved=__atomic_load_n(p[i].slot,__ATOMIC_SEQ_CST);
 /* Revalidate the saved values too: a resolver may have run between reads. */
 for(i=0;i<n;i++)if((p[i].saved!=p[i].native&&p[i].saved!=p[i].lazy)||p[i].saved==p[i].replacement)return -1;
 for(i=0;i<n;i++){uint32_t expected=p[i].saved;if(!__atomic_compare_exchange_n(p[i].slot,&expected,p[i].replacement,0,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST))return rollback(p,i)?-2:-1;}return 0;}
int replay_imports_restore(struct replay_import *p,unsigned n){unsigned i;if(descriptors(p,n))return -1;for(i=0;i<n;i++)if((p[i].saved!=p[i].native&&p[i].saved!=p[i].lazy)||p[i].saved==p[i].replacement)return -1;return rollback(p,n);}
