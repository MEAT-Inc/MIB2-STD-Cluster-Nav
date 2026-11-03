.syntax unified
.arm
.text
.align 2
.global delphi_replay_open
.hidden delphi_replay_open
.type delphi_replay_open,%function
delphi_replay_open:
 mov r3,lr
 b replay_open_impl
.size delphi_replay_open,.-delphi_replay_open
.global delphi_replay_write
.hidden delphi_replay_write
.type delphi_replay_write,%function
delphi_replay_write:
 mov r3,lr
 b replay_write_impl
.size delphi_replay_write,.-delphi_replay_write
.global delphi_replay_close
.hidden delphi_replay_close
.type delphi_replay_close,%function
delphi_replay_close:
 mov r1,lr
 b replay_close_impl
.size delphi_replay_close,.-delphi_replay_close
.section .note.GNU-stack,"",%progbits
