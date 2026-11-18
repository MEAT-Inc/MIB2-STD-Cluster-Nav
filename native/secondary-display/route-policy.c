#include "route-policy.h"
#include <string.h>
int route_apply(struct route_policy *p,int healthy,uint64_t ms,unsigned app,unsigned thread,unsigned event,const void *bytes,unsigned n){unsigned i,free_slot=ROUTE_SLOTS;uint32_t focus;const unsigned char *b=bytes;if(event!=ROUTE_EVENT||n!=12||!b||app>255||(thread!=ROUTE_UNKNOWN_THREAD&&(!thread||thread>255)))return 0;memcpy(&focus,b+8,4);if(focus!=ROUTE_PROJECTED&&focus!=ROUTE_NATIVE)return 0;
 for(i=0;i<ROUTE_SLOTS;i++){struct route_item *q=&p->items[i];if(!q->used){if(free_slot==ROUTE_SLOTS)free_slot=i;continue;}if(q->app==app&&q->thread==thread&&!memcmp(q->bytes,b,8)){if(focus==ROUTE_NATIVE){q->used=0;p->cancelled++;return 0;}free_slot=i;break;}}
 if(focus!=ROUTE_PROJECTED||!healthy||p->disabled||(p->deadline&&ms>=p->deadline)||free_slot==ROUTE_SLOTS)return 0;
 if(!p->deadline){p->deadline=ms+ROUTE_HOLD_MS;}p->items[free_slot].app=app;p->items[free_slot].thread=thread;memcpy(p->items[free_slot].bytes,b,12);p->items[free_slot].used=1;p->held++;return 1;}
void route_release(struct route_policy *p,route_send send){unsigned i;p->disabled=1;for(i=0;i<ROUTE_SLOTS;i++){struct route_item q=p->items[i];p->items[i].used=0;if(!q.used)continue;if(send(q.app,q.thread,ROUTE_EVENT,q.bytes,12)>0)p->released++;else p->errors++;}}
