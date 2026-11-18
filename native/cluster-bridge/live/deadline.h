#ifndef DELPHI_LIVE_DEADLINE_H
#define DELPHI_LIVE_DEADLINE_H
#include <stdint.h>
#define LIVE_WAIT_NS (180ULL*1000000000ULL)
struct live_deadline { uint64_t waiting_until,active_until; };
static void live_deadline_init(struct live_deadline *d,uint64_t now){d->waiting_until=now+LIVE_WAIT_NS;d->active_until=0;}
static void live_deadline_first(struct live_deadline *d,uint64_t now,unsigned seconds){if(!d->active_until)d->active_until=now+(uint64_t)seconds*1000000000ULL;}
/* 4 means no usable first frame within the bounded connection window. */
static unsigned live_deadline_reason(const struct live_deadline *d,uint64_t now){return d->active_until?(now>=d->active_until?2:0):(now>=d->waiting_until?4:0);}
#endif
