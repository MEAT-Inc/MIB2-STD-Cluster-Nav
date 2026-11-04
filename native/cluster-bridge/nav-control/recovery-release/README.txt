Stalled NavigationServer recovery - captured session only
========================================================
The captured shutdown fault is SIGSEGV in libc _list_release during map-object
delete. The factory signal handler calls printf, which re-enters free while
that thread already owns __malloc_mutex. This leaves the process alive and
prevents the factory process manager from restarting it.

This trial is restricted to the exact PID/start/parent session from
_nav_shutdown_diag_20261104_144616_5cd1a4aa. It refuses a different session,
a healthy process, or a different crash. Do not reboot before this trial.

1. Extract the complete ZIP on the connected laptop. Park, keep ignition on,
   phone unplugged. Leave the current Starting map failure as it is.
2. Run:
   python scripts/run_nav_graceful.py --run --recover-stalled --phone-unplugged
3. The helper checks the exact repeated fault frame and allocator-owner
   signature, confirms the factory manager has autorestart enabled, then sends
   SIGKILL once to this already-crashed NavigationServer process.
   It does not send another shutdown request or change heap/code/firmware.
4. The factory manager should start a fresh stock NavigationServer. The helper
   verifies the new PID/start/parent/code and recorded SIGKILL exit status.
5. Check factory maps on BOTH head unit and cluster before answering the script.
   A fresh process alone does not establish functional map recovery.
6. Return the entire delphi-dump/_nav_stall_recovery_* folder.

If any check fails, the helper refuses without choosing another process.
There is no retry, alternative signal, or extra start request. A PID recheck
and kill are separate system calls; they are not an atomic procfs operation.
If recovery does not restore maps, keep the result folder and reboot the radio
manually. This is a recovery trial; visible Android Auto playback is still
pending. Normal cycle/replay modes remain held.
