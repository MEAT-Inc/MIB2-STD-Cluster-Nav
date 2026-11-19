#include "session.h"

void bridge_session_init(struct bridge_session *s) {
    s->generation = 0; s->phase = BRIDGE_IDLE; s->released = 0;
}
static int current(const struct bridge_session *s, uint64_t generation) {
    return generation && generation == s->generation;
}
enum bridge_action bridge_session_begin(struct bridge_session *s) {
    if (s->phase != BRIDGE_IDLE) return BRIDGE_NONE;
    if (s->generation == UINT64_MAX) {
        s->phase = BRIDGE_FAILED; return BRIDGE_LOCKOUT;
    }
    ++s->generation; s->released = 0; s->phase = BRIDGE_STARTING;
    return BRIDGE_PREPARE;
}
enum bridge_action bridge_session_ready(struct bridge_session *s, uint64_t g) {
    if (!current(s,g) || s->phase != BRIDGE_STARTING) return BRIDGE_NONE;
    s->phase = BRIDGE_ACTIVE; return BRIDGE_NONE;
}
enum bridge_action bridge_session_end(struct bridge_session *s, uint64_t g) {
    if (!current(s,g)) return BRIDGE_NONE;
    /* A partial setup may already own transport. Always demand factory proof. */
    if (s->phase != BRIDGE_STARTING && s->phase != BRIDGE_ACTIVE) return BRIDGE_NONE;
    s->phase = BRIDGE_RETURNING; return BRIDGE_HANDBACK;
}
enum bridge_action bridge_session_factory(struct bridge_session *s, uint64_t g) {
    if (!current(s,g) || s->phase != BRIDGE_RETURNING) return BRIDGE_NONE;
    s->phase = BRIDGE_QUIESCING; return BRIDGE_RELEASE;
}
enum bridge_action bridge_session_release(struct bridge_session *s, uint64_t g,
                                         unsigned proof) {
    if (!current(s,g) || s->phase != BRIDGE_QUIESCING) return BRIDGE_NONE;
    if (!proof || (proof & ~BRIDGE_RELEASE_ALL)) {
        s->phase = BRIDGE_FAILED; return BRIDGE_LOCKOUT;
    }
    s->released |= proof;
    if (s->released != BRIDGE_RELEASE_ALL) return BRIDGE_NONE;
    s->phase = BRIDGE_IDLE; return BRIDGE_REARM;
}
enum bridge_action bridge_session_fault(struct bridge_session *s, uint64_t g) {
    if (!current(s,g) || s->phase == BRIDGE_IDLE || s->phase == BRIDGE_FAILED)
        return BRIDGE_NONE;
    /* Never clear a wire/profile/process-identity fault by reconnecting. */
    s->phase = BRIDGE_FAILED; return BRIDGE_LOCKOUT;
}
