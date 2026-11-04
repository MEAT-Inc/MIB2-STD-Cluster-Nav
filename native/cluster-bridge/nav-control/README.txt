HELD - November 4: stock orderly shutdown stalled on the unit.
Do not run the cycle command. Current action: updated map-session package:
 python scripts/collect_map_session.py --run --state broken --shutdown-stack
Capture while still stalled, return results, then reboot the radio.

Stock factory-map graceful lifecycle test - MU0890 Delphi only (preflight v2)
=============================================================

Purpose: verify functional factory-map recovery using an orderly SAL shutdown
and explicit factory-manager start. This test contains no recording, video
writer, preload shim, or live Android Auto integration.

The captured procman/libXSAL protocol and guarded cycle pass QNX emulation.
Actual factory graphics/component teardown and physical map recovery have NOT
yet been validated. A fresh process alone is not a passing map-recovery test.

1. Extract the entire ZIP into its own folder on the connected laptop.
2. Park the car and keep ignition on. Disconnect the phone from USB.
3. Confirm factory maps work on BOTH the head unit and virtual cockpit first.
   If Starting map persists from an earlier trial, reboot the radio first and
   wait until factory maps are visible. Do not start from an incomplete session.
4. From the extracted folder:
   python scripts/run_nav_graceful.py --run --phone-unplugged --factory-maps-working
5. Expect factory maps to disappear briefly. After the clean process cycle, the
   script waits 15 seconds then asks whether maps work on BOTH displays.
   Check both views before answering yes/no/unsure. If still loading, wait before
   answering. If prompted, keep the script window open until collection finishes.
6. Return the ENTIRE newly printed delphi-dump/_nav_graceful_* folder.

The helper verifies process identity, loaded instruction profiles, the factory
manager registry, and SAL namespace routes. It sends one shutdown request to
NavigationServer (app29,event0x163), waits for clean status0, then sends one
start request to procman (app1,event0x161,payload uint32 29). It never sends a
fallback signal or retries the cycle. Its 60-second alarm terminates only the
helper if control stalls; the host uses a longer command timeout.

Native helper uploads are confined to a unique /ramdisk/delphi-nav-cycle_*
directory. Exact NavigationServer, procman, and libXSAL file hashes are checked
before helper upload. Preflight v2 uses the previously working shell copy to a
regular RAM file before FTP retrieval, instead of FTP-reading /proc/boot files
directly. All reference bytes, copy logs, expected/actual sizes and hashes are
retained in the dump. A mismatch still blocks helper upload and all control.
Existing logs/threads and read-only copies of existing DTS rings
are collected; concurrently written rings are not atomic snapshots. Trace
settings and firmware files are unchanged. RAM artifacts are retained for review.

If the helper refuses or fails, do not rerun automatically. Return the folder.
If factory maps stay stuck, hold the radio power button for about 10 seconds to
reboot before any further experiment. A power-button reboot has been the user's
working recovery from earlier incomplete sessions.

Without --run the script only prints a plan and makes no connection.
Python 3.10+ and its standard library suffice on the laptop. Other connection
options are shown with --help. Package generation may require analysis tooling.

This trial is a prerequisite for fixing replay lifecycle handling; it does not
attempt recorded or live Android Auto maps in the cluster.
