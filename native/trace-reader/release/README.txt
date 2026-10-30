PASSIVE DOOR-EVENT TEST: stock AndroidAuto, no restart or instrumentation

The closed-door baseline passed on this unit: 180 seconds/7692296 bytes, stock
PID684110 unchanged, video startup/playback captured and user observed normal AA.
The next test compares one driver-door action with the SAME passive logger.

Extract passive-phone-trace-laptop.zip into the laptop project root, overwriting
the included files. Keep the vehicle parked, ignition ON as in the reported fault,
head unit powered, Ethernet attached and phone unplugged. Run:
  python scripts/run_phone_trace.py --run --scenario door --ignition on

1. Only at LOGGER READY swap Ethernet for the phone and open AA navigation.
2. The laptop asks if AA is displaying normally NOW. Enter y only if it is.
   If not, the door action is skipped and the routine still collects the trace.
3. The routine waits 30 seconds, then prompts you to open and close the driver
   door ONCE and immediately press Enter. It skips the action if too little
   capture time remains. If prompted, do the action then, not earlier.
4. Observe whether AA goes black and returns. If the VW menus still work, leave
   the unit on so the trace can be collected before any head-unit reboot.
5. Wait until at least210 seconds TOTAL since LOGGER READY. Reconnect Ethernet,
   press Enter, and answer the screen/door/recovery questions honestly (u=unknown).
Return the entire new delphi-dump/_phone_trace_* folder, including partial results.
If no LOGGER READY appears, leave Ethernet connected and return that folder.

The reader receives existing TraceServer text from 127.0.0.1:15361 and writes only
new files in a fresh private /ramdisk directory. It exits after180 seconds,16MiB,
closure or error. It does not signal, hook, redirect, stop or restart AndroidAuto,
change filters/USB/settings, or edit factory files. Logger hangup survival, local
loopback networking and bounded capture have now passed on this actual unit.
A logger-only fork may detach from ksh job control before sockets/files exist;
that fork never concerns another process. RAM output stays until a unit reboot.

The collector checks stock AA PID before/after and records your observations
separately. If a PID changes during this door test, that is evidence to review;
it is never automatically retried or repaired by sending a signal. Transfer
failures preserve .partial bytes. Early buffer-cap stops, malformed final reports,
short host waits and transfer errors cannot pass the full-window capture gate.
Manual event timing is approximate; logs and your observation must be correlated.
Receiving a complete trace does not by itself prove display recovery or cluster
maps. The original disruptive/restart observer remains disabled.

Baseline mode, only if specifically needed:
  python scripts/run_phone_trace.py --run
It keeps the door closed. Do not use baseline mode for the requested door test.

Validation: seven real-loopback host cases, QNX loader/root refusal and exact
QNX ksh positive/negative launch-wire checks pass. The same native reader SHA256
is confirmed by the successful unit capture. Thirteen Python workflow tests and
the portable standard-library-only baseline/door plans pass. No acquired binaries
or emulator fixtures are distributed. The native reader is unchanged for this test.
