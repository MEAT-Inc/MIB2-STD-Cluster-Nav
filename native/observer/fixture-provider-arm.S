.syntax unified
.arch armv7-a
.fpu vfpv3-d16
.arm
.text
.align 2
.global _ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase
.type _ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase,%function
_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase:
    ldr r12, =0xeeee0004
    cmp r0,r12
    bne fixture_native_registration
    stmia r1,{r0-r3}
    add r12,r1,#16
    vstmia r12,{d0-d7}
    mov r12,sp
    str r12,[r1,#80]
    b fixture_native_registration
.size _ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase,.-_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase
.section .note.GNU-stack,"",%progbits
