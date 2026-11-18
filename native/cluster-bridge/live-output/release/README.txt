LIVE ANDROID AUTO CLUSTER TRIAL v9
==================================
V9 returns the existing cluster video channel to factory navigation after the
verified phone-service stop. Return waits for complete native SPS/PPS/IDR and
continues the same transport clock and continuity counters. After unplugging,
observe whether factory compass/map returns automatically BEFORE any manual
map-location toggle or cleanup. That observation is saved independently from
subsequent manual radio/cluster restoration checks. Both are required to pass.
If a stale mobile-navigation message is present before testing, reboot the radio
once and wait for working factory maps.
Secondary display requests 200 total horizontal margin pixels (100 per side)
and density160, preserving the original 800x480 coded frame. Phone rendering
and physical clipping remain to be verified.

This is live phone video. The initial phone codec/keyframe is repeated three
times while source frames are buffered in order. All original frames follow
with approximately one second of added delay; no re-encoding is used. This
tests whether the cluster missed the original single startup keyframe.
Park with ignition on, working factory maps, phone unplugged and Ethernet connected.
Extract the ENTIRE ZIP into a fresh laptop folder. Run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
Before uploading, RAM space is checked. Only hash-matching files from locally
archived, restored runs are eligible for removal; incomplete/active tests are
preserved. If30MiB is still unavailable, the script stops before any app launch.
In that case reboot the radio once, wait for factory maps, and rerun.
Select factory map graphics in the instrument cluster and confirm the arm prompt.
Use a browsable factory map with no VW route running.
This bounded trial defers only the phone-route handoff notification while the
verified live bridge is healthy (maximum40 seconds), acknowledging phone focus
through the stock native helper. Original notification is released on bridge
stop/failure/timeout; route-end and unrelated messages pass unchanged. There
is no stored firmware patch. This is a presentation prototype, not a final
production arbitration policy.
Only at CAPTURE READY swap Ethernet for phone. Start a Google Maps route promptly: the video window begins with the first phone frame.
Watch the cluster for about12 seconds of LIVE map updates. Unplug phone,
reconnect Ethernet, then press Enter. Complete PHONE REMOVED cleanup and
answer whether factory compass/map returned automatically before cleanup,
then whether live maps appeared and factory maps restored after cleanup.
Return the entire delphi-dump/_disconnect_observer_* folder.

The existing native descriptor, app import guards, timeline handoff and exact
crash recovery are reused. No second cluster writer or extra Nav worker is added.
The consumer waits up to180 seconds for the phone, then runs up to30 seconds
from its first usable frame. Overflow or transport failure ends output.
If cleanup remains pending, keep the phone unplugged and use the SAME extracted
bundle with --resume "<result-folder>" --live-cluster --phone-unplugged.
This trial has passed local/QNX tests; on-car display
and restoration of the combined run remain to be verified.
