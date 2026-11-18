LIVE ANDROID AUTO CLUSTER TRIAL v6
==================================
This is live phone video, with no saved map clip available for playback.
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
answer whether live maps appeared and factory maps restored.
Return the entire delphi-dump/_disconnect_observer_* folder.

The existing native descriptor, app import guards, timeline handoff and exact
crash recovery are reused. No second cluster writer or extra Nav worker is added.
The consumer waits up to180 seconds for the phone, then runs up to30 seconds
from its first usable frame. Overflow or transport failure ends output.
If cleanup remains pending, keep the phone unplugged and use the SAME extracted
bundle with --resume "<result-folder>" --live-cluster --phone-unplugged.
This trial has passed local/QNX tests; on-car display
and restoration of the combined run remain to be verified.
