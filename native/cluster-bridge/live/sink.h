#ifndef DELPHI_LIVE_SINK_H
#define DELPHI_LIVE_SINK_H
#include "queue.h"
#include <sys/types.h>
struct live_sink;
struct live_sink *live_sink_open(const char *,volatile uint32_t *);
int live_sink_poll(void *);
int live_sink_run(void *,ssize_t (*)(void *,const void *,size_t),void *);
#endif
