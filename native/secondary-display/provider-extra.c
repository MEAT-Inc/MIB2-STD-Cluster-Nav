#include <errno.h>
int pop(void*,void*) __asm__("_ZN13MessageRouter32populateServiceDiscoveryResponseEP24ServiceDiscoveryResponse");
int queue(void*,unsigned char,void*,unsigned) __asm__("_ZN13MessageRouter13queueOutgoingEhPvj");
int pop(void *a,void*b){if(a!=(void*)0x1234||b!=(void*)0x5678||errno!=ERANGE)return 0;errno=EDOM;return 0x334455;}
int queue(void*a,unsigned char ch,void*b,unsigned n){if(a!=(void*)0x1234||ch!=7||b!=(void*)0x5678||n!=19||errno!=ERANGE)return 0;errno=EDOM;return 0x223344;}

int SAL_Send(unsigned app,unsigned thread,unsigned event,const void *bytes,unsigned n){(void)app;(void)thread;(void)event;(void)bytes;return 1409+(int)n;}
