#include "imports.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"IMPORTS_FAIL line=%d\n",__LINE__);exit(1);}}while(0)
static uint32_t slots[3];
static struct replay_import p[3];
static void reset(void){unsigned i;for(i=0;i<3;i++){slots[i]=100+i;p[i].slot=&slots[i];p[i].native=100+i;p[i].lazy=77;p[i].replacement=200+i;p[i].saved=0;}}
static void pristine(void){CHECK(slots[0]==100&&slots[1]==101&&slots[2]==102);}
int main(void){unsigned i;reset();CHECK(!replay_imports_install(p,3));for(i=0;i<3;i++)CHECK(slots[i]==200+i&&p[i].saved==100+i);CHECK(!replay_imports_restore(p,3));pristine();reset();slots[0]=slots[2]=77;CHECK(!replay_imports_install(p,3));CHECK(!replay_imports_restore(p,3));CHECK(slots[0]==77&&slots[1]==101&&slots[2]==77);
 reset();slots[2]=999;CHECK(replay_imports_install(p,3)==-1);CHECK(slots[0]==100&&slots[1]==101&&slots[2]==999);
 reset();p[2].slot=p[0].slot;CHECK(replay_imports_install(p,3)==-1);pristine();
 reset();p[2].slot=0;CHECK(replay_imports_install(p,3)==-1);pristine();
 reset();p[2].slot=(volatile uint32_t *)((unsigned char *)&slots[2]+1);CHECK(replay_imports_install(p,3)==-1);pristine();
 reset();p[2].replacement=0;CHECK(replay_imports_install(p,3)==-1);pristine();
 reset();p[2].replacement=p[2].native;CHECK(replay_imports_install(p,3)==-1);pristine();
 reset();p[2].native=0;CHECK(replay_imports_install(p,3)==-1);pristine();
 reset();CHECK(replay_imports_install(0,3)==-1);CHECK(replay_imports_install(p,2)==-1);pristine();
 reset();CHECK(!replay_imports_install(p,3));slots[1]=999;CHECK(replay_imports_restore(p,3)==-2);CHECK(slots[0]==100&&slots[1]==999&&slots[2]==102);
 reset();CHECK(replay_imports_restore(p,3)==-1);pristine();
 puts("REPLAY_IMPORTS_PASS resolved=1 lazy=1 validate_all_before_store=1 duplicate_alignment_null=1 restore=1 preserve_foreign=1");return 0;}
