.syntax unified
.arch armv7-a
.fpu vfpv3-d16
.arm
.text
.macro DISPLAY_ENTRY name,event
.align 2
.global \name
.type \name,%function
\name:
.fnstart
 push {r0-r3,r12,lr}
 vpush {d0-d7}
 add r0,sp,#64
 mov r1,#\event
 ldr r2,[sp,#84]
 bl delphi_display_enter
 str r0,[sp,#80]
 vpop {d0-d7}
 pop {r0-r3,r12,lr}
 bx r12
.cantunwind
.fnend
.size \name,.-\name
.endm
DISPLAY_ENTRY _ZN9VideoSink25addSupportedConfigurationEiiiiiii,1
DISPLAY_ENTRY _ZN9VideoSink13setVideoFocusEib,2
DISPLAY_ENTRY _ZN13MessageRouter13queueOutgoingEhPvj,3
.section .note.GNU-stack,"",%progbits
