#ifndef DELPHI_ROUTE_POLICY_H
#define DELPHI_ROUTE_POLICY_H
#include <stddef.h>
#include <stdint.h>
#define ROUTE_EVENT 0x1749u
#define ROUTE_SLOTS 16u
#define ROUTE_HOLD_MS 40000u
/* SAL native wrapper0x143d98 explicitly accepts -1 (unknown thread). */
#define ROUTE_UNKNOWN_THREAD 0xffffffffu
/* MU0890 SAL native enum, NOT DSI/HMI values: AndroidAutoServices
 * 0x112760..0x112774 maps native1 to HMI2, native2 to HMI1. */
enum {ROUTE_PROJECTED=1,ROUTE_NATIVE=2};
struct route_item {unsigned app,thread;unsigned char bytes[12];int used;};
struct route_policy {struct route_item items[ROUTE_SLOTS];uint64_t deadline;unsigned held,released,cancelled,errors;int disabled;};
typedef int (*route_send)(unsigned,unsigned,unsigned,const void*,unsigned);
/* This is a bounded bridge trial: hold only phone-route presentation requests.
 * End requests, all unrelated traffic and every unverified state pass through. */
int route_apply(struct route_policy*,int,uint64_t,unsigned,unsigned,unsigned,const void*,unsigned);
void route_release(struct route_policy*,route_send);
#endif
