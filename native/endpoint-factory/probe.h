#ifndef DELPHI_FACTORY_PROBE_H
#define DELPHI_FACTORY_PROBE_H
#include "factory.h"
#define FACTORY_MAGIC 0x31504645u
struct factory_report {
 uint32_t magic,version,bytes,pid,started,done,status,error;
 uint32_t app_bias,receiver_base,router,main_endpoint;
 uint32_t slot9_before,slot10_before,slot9_after,slot10_after,primary_unchanged,table_unchanged;
 struct factory_result result;
 uint32_t reserved[34];
};
#endif
