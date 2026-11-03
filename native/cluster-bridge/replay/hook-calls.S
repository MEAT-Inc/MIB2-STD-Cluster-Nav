.syntax unified
.arm
.text
.macro CALL name, target, ret
.global \name
.type \name,%function
\name:
 push {r4,lr}
 bl \target
.global \ret
\ret:
 pop {r4,pc}
.size \name,.-\name
.endm
CALL test_open,open,test_open_return
CALL test_write,write,test_write_return
CALL test_close,close,test_close_return
.section .note.GNU-stack,"",%progbits
