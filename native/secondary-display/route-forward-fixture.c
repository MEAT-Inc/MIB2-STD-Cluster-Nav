#include <stdio.h>
extern int SAL_Send(unsigned,unsigned,unsigned,const void*,unsigned);
extern int SAL_Publish(unsigned,const void*,unsigned);
int main(void){unsigned b[3]={123,0,2};if(SAL_Send(85,1,0x1749,b,12)!=1421||SAL_Send(85,1,0x1234,b,12)!=1421||SAL_Send(85,1,0x1749,b,8)!=1417)return 1;if(SAL_Publish(0x173e,0,0)!=1709||SAL_Publish(0x9999,b,12)!=1721)return 2;puts("ROUTE_POLICY_PRELOAD_FORWARD_PASS exact_abi=1 inactive_no_interference=1");return 0;}
