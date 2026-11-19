#ifndef DELPHI_DEPLOYMENT_SESSION_H
#define DELPHI_DEPLOYMENT_SESSION_H
#include <stdint.h>

/* Control-plane gate only. The caller serializes calls outside media callbacks.
 * No memory mappings, process restarts, route events or transport writes here.
 * Tokens are supervisor generations, never Android Auto's reusable session IDs. */
enum bridge_phase { BRIDGE_IDLE, BRIDGE_STARTING, BRIDGE_ACTIVE,
                    BRIDGE_RETURNING, BRIDGE_QUIESCING, BRIDGE_FAILED };
enum bridge_action { BRIDGE_NONE, BRIDGE_PREPARE, BRIDGE_HANDBACK,
                     BRIDGE_RELEASE, BRIDGE_REARM, BRIDGE_LOCKOUT };
enum bridge_release {
    BRIDGE_PRODUCER_STOPPED = 1, BRIDGE_CONSUMER_STOPPED = 2,
    BRIDGE_CALLBACKS_IDLE = 4, BRIDGE_ROUTE_RESET = 8,
    BRIDGE_RELEASE_ALL = 15
};
struct bridge_session {
    uint64_t generation;
    enum bridge_phase phase;
    unsigned released;
};
void bridge_session_init(struct bridge_session *);
enum bridge_action bridge_session_begin(struct bridge_session *);
/* Each completion belongs to the exact generation which requested it. */
enum bridge_action bridge_session_ready(struct bridge_session *, uint64_t);
enum bridge_action bridge_session_end(struct bridge_session *, uint64_t);
enum bridge_action bridge_session_factory(struct bridge_session *, uint64_t);
enum bridge_action bridge_session_release(struct bridge_session *, uint64_t, unsigned);
enum bridge_action bridge_session_fault(struct bridge_session *, uint64_t);
#endif
