#include <errno.h>
#include <stdint.h>
#include <stdio.h>
int pop(void*,void*) __asm__("_ZN13MessageRouter32populateServiceDiscoveryResponseEP24ServiceDiscoveryResponse");
int queue(void*,unsigned char,void*,unsigned) __asm__("_ZN13MessageRouter13queueOutgoingEhPvj");
int main(void){errno=ERANGE;if(pop((void*)0x1234,(void*)0x5678)!=0x334455||errno!=EDOM)return 1;errno=ERANGE;if(queue((void*)0x1234,7,(void*)0x5678,19)!=0x223344||errno!=EDOM)return 2;puts("SECONDARY_HOOK_FORWARD_QNX_PASS");return 0;}
