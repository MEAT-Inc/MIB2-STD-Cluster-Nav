.syntax unified
.arch armv7-a
.fpu vfpv3-d16
.arm
.text
.align 2
.global _ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase
.type _ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase, %function
_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase:
.fnstart
/* 24+64 bytes preserve 8-byte stack alignment. r4-r11 and d8-d15 are
 * preserved by the helper's AAPCS obligations. No object layout is accessed. */
    push {r0-r3,r12,lr}
    vpush {d0-d7}
    ldr r2, [sp, #84]  /* original caller LR */
    bl delphi_observer_enter
    str r0, [sp, #80]  /* tail target replaces saved caller-scratch r12 */
    vpop {d0-d7}
    pop {r0-r3,r12,lr}
    bx r12            /* native sees original LR/SP; returns/unwinds directly */
.cantunwind
.fnend
.size _ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase, .-_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase
.section .note.GNU-stack,"",%progbits
