.syntax unified
.arm
.text
.global open
open: b delphi_replay_open
.global write
write: b delphi_replay_write
.global close
close: b delphi_replay_close
.section .note.GNU-stack,"",%progbits
