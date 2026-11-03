V6 RECORDED ANDROID AUTO MAPS IN THE CLUSTER - DISPLAY TRIAL
This replays saved Google Maps video, not live navigation/current guidance.
V5 armed successfully and restored the stock NavigationServer process, but no
native video writes arrived. Its source-write-only activation never started.
V6 starts from the explicitly armed, already-open native descriptor after fresh
FD/800x480 geometry/import validation; no first native video frame is required.
It opens no competing writer. Native writes/closes remain serialized; at EOF or
error native packets stay muted until native close or supervised stock cleanup.
Any unknown caller, stale FD, invalid geometry or report error prevents takeover.
The V5 post-exec identity fix and exact process checks are retained unchanged.

Extract into the laptop project. Ignition on, Ethernet connected; keep phone
unplugged throughout. Select the navigation MAP VIEW in the instrument cluster.
The cluster may say Starting map: V6 no longer requires factory map pixels.
Run: python scripts/run_cluster_replay.py --run --phone-unplugged
After the native-channel checks, press Enter to arm, or SKIP to restore.
Playback should begin within about1second of arming and last about48seconds.
A10second activation deadline replaces an empty120second wait; missing channel,
transport errors and partial playback retain reports and trigger stock cleanup.
Observe whether the saved Google Maps view appears IN THE INSTRUMENT CLUSTER.
Process restoration is printed separately from video delivery/display success;
a verified new stock process does not prove that factory maps finished loading.
Return the ENTIRE new delphi-dump/_cluster_replay_* folder, even if partial.
If interrupted/pending use only the exact resume command printed by this build.
No persistent firmware/config files changed. Actual cluster replay is unproven
until this car test; live phone feeding and phone-session presentation follow.
