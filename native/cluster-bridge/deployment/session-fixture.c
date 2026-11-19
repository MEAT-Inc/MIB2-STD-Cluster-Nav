#include "session.h"
#include <assert.h>
#include <stdio.h>

int main(void) {
    struct bridge_session s;
    unsigned i, bit;
    uint64_t g;
    bridge_session_init(&s);
    assert(bridge_session_factory(&s,0)==BRIDGE_NONE);
    for (i=0;i<10000;++i) {
        assert(bridge_session_begin(&s)==BRIDGE_PREPARE); g=s.generation;
        assert(g==(uint64_t)i+1);
        assert(bridge_session_begin(&s)==BRIDGE_NONE);
        assert(bridge_session_end(&s,g-1)==BRIDGE_NONE);
        assert(bridge_session_factory(&s,g)==BRIDGE_NONE);
        assert(bridge_session_release(&s,g,BRIDGE_RELEASE_ALL)==BRIDGE_NONE);
        if (i&1) bridge_session_ready(&s,g); /* Also exercise partial setup. */
        assert(bridge_session_end(&s,g)==BRIDGE_HANDBACK);
        assert(bridge_session_end(&s,g)==BRIDGE_NONE);
        bridge_session_ready(&s,g);
        assert(s.phase==BRIDGE_RETURNING);
        assert(bridge_session_begin(&s)==BRIDGE_NONE);
        assert(bridge_session_factory(&s,g-1)==BRIDGE_NONE);
        assert(bridge_session_factory(&s,g)==BRIDGE_RELEASE);
        assert(bridge_session_factory(&s,g)==BRIDGE_NONE);
        for(bit=1;bit<=8;bit<<=1) {
            assert(bridge_session_release(&s,g-1,bit)==BRIDGE_NONE);
            assert(bridge_session_release(&s,g,bit)==(bit==8?BRIDGE_REARM:BRIDGE_NONE));
            assert(bridge_session_release(&s,g,bit)==BRIDGE_NONE);
            if(bit!=8) assert(bridge_session_begin(&s)==BRIDGE_NONE);
        }
        assert(s.phase==BRIDGE_IDLE);
        assert(bridge_session_fault(&s,g)==BRIDGE_NONE);
    }
    assert(bridge_session_begin(&s)==BRIDGE_PREPARE); g=s.generation;
    assert(bridge_session_fault(&s,g)==BRIDGE_LOCKOUT);
    assert(bridge_session_begin(&s)==BRIDGE_NONE);
    assert(bridge_session_factory(&s,g)==BRIDGE_NONE);
    assert(bridge_session_release(&s,g,BRIDGE_RELEASE_ALL)==BRIDGE_NONE);
    assert(s.phase==BRIDGE_FAILED);
    bridge_session_init(&s); s.generation=UINT64_MAX;
    assert(bridge_session_begin(&s)==BRIDGE_LOCKOUT);
    bridge_session_init(&s); bridge_session_begin(&s); g=s.generation;
    bridge_session_end(&s,g); bridge_session_factory(&s,g);
    assert(bridge_session_release(&s,g,16)==BRIDGE_LOCKOUT);
    puts("SESSION_GATE_PASS: 10000 cycles, stale generations, partial setup, handback, quiescence, lockout, wrap");
    return 0;
}
