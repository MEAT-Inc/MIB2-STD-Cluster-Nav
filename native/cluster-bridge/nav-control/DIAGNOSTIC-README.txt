Navigation shutdown allocator diagnostic v2 - native reader - November 4
====================================================
This is one controlled reproduction with automatic evidence collection.
The previous shutdown left NavMain and its timer blocked in libc __free on
__malloc_mutex. The built-in backtrace stopped before the navigation caller.
The radio has since been rebooted, so those caller frames are no longer available.

1. Extract this entire ZIP into its own folder on the connected laptop.
2. Park, keep ignition on, unplug the phone, and confirm factory maps work on
   the radio and cluster in turn using the location toggle before starting.
   They do not need to display maps simultaneously.
3. Run:
   python scripts/run_nav_graceful.py --run --diagnose-shutdown --phone-unplugged --factory-maps-working
4. Leave the script running until it prints the saved folder. No answers are
   requested during this diagnostic mode. Allow up to about two minutes.
5. Return the ENTIRE delphi-dump/_nav_shutdown_diag_* folder.
6. Reboot the radio after the script finishes if factory maps remain stuck.

This uses the same previously verified helper to request one orderly shutdown
and, only if clean exit is proven, one explicit factory-manager start.
The prior stock shutdown is EXPECTED to stall. The helper may report exit3.
The diagnostic result records that separately from whether memory collection
completed. It performs no automatic retry or fallback termination.

Before control, four exact firmware files are verified via RAM copies:
NavigationServer, procman, libXSAL, and libc. One baseline and two post-control
samples collect backtraces/registers/mappings and bounded raw memory. Each raw
sample copies one 4096-byte page containing NavMain SP, one containing timer SP,
and one containing the allocator mutex. Pages are read through the bundled nav_cycle page command using pread64, then
downloaded from the unique RAM directory. No dd or other optional target tool
is used. The native reader validates Nav PID/start/parent, executable/code
profiles, and manager identity before reading; it rechecks identities before
output. It emits exactly one 4096-byte page on success and no page after an
invalid/stale identity or failed memory read. These paths pass actual QNX
process-memory tests, including unmapped/misaligned address refusal. These are
non-atomic observations; no thread is suspended and no process memory is changed.
Existing system logs and DTS rings are retained too.

Normal graceful-cycle/replay tests remain held. This diagnostic command is
the only currently enabled control mode. It does not attempt playback.
A complete diagnostic capture does not mean navigation recovery succeeded.
