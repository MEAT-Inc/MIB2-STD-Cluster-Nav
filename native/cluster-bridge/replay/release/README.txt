Recorded Android Auto cluster playback v9
========================================
Goal: sustained Google Maps playback in the instrument cluster.
This is a saved 20-second excerpt, not live phone navigation.

1. Extract the entire ZIP into a fresh folder on the connected laptop.
2. Start with working factory maps. If the previous failed test left maps stuck,
   reboot the radio first and wait for factory maps to render.
3. Park, keep ignition on, phone unplugged and Ethernet connected. Use the map
   location toggle to select factory maps IN THE CLUSTER. Radio and cluster
   maps are checked sequentially; simultaneous maps are not required.
4. Run:
   python scripts/run_cluster_replay.py --run --phone-unplugged --cluster-map-selected
5. After startup, select the factory map in the cluster again if needed.
   Press Enter at the playback prompt only when actual factory map graphics
   are visible. Enter SKIP if it remains at Starting map.
6. Observe the approximately20-second recording. Answer whether it played
   continuously, then check factory maps on radio and cluster in turn.
7. Return the entire new delphi-dump/_cluster_replay_* folder.

Changes in v9:
-259 recorded frames, reencoded as800x480 Baseline H.264 with an independent
 keyframe and repeated codec headers every five frames (52 keyframes).
 Original frame timestamps and color metadata are preserved. Pixels are
 reencoded; all frames passed the35dB minimum RGB PSNR gate (measured39.38dB
 minimum). The replay remains below the existing8MiB memory limit.
-Continues the accepted factory PCR/PTS/DTS clock and packet counters.
 Native fragmented writes are reassembled into188-byte packets. Handoff
 occurs only at a complete packet boundary; no clock reset packets are added.
-The exact captured replay NavMain/thread3 allocator SIGSEGV is recognized.
 The original stock NavMain/thread2 signature remains separate. Both require
 the captured fault frame, map-deletion caller, allocator owner and unchanged
 process identity. No generic termination fallback or heap repair is added.
-Saves playback completion and the continuous-visibility answer before cleanup.
 Records playback state/packet count at the first endpoint close and collects
 thread/register/backtrace/mapping diagnostics if cleanup fails.

MOST status and the bounded factory-video prefix are collected in the same run.
Only the existing owned transport descriptor writes replay video. Retry limits,
firmware reference checks and explicit arm requirements remain in force.
The new recovery signature and frequent-keyframe replay have passed offline/QNX
validation; functional restoration and continuous cluster playback need this
car test. Do not repeat the earlier v7/v8 trials.
