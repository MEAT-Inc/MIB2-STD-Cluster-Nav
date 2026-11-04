Recorded Android Auto map playback v7 - lifecycle recovery
=========================================================
Goal: show the saved Google Maps recording in the cluster. Phone remains unplugged.

The factory map is selectable on the radio OR cluster using the location button.
Check each location in turn, then leave the actual factory map visible IN THE
CLUSTER before starting. Simultaneous maps are not required.

1. Extract the entire v7 ZIP into a fresh folder on the connected laptop.
2. Park, keep ignition on, phone unplugged, Ethernet connected. Select a working
   factory map in the instrument cluster.
3. Run:
   python scripts/run_cluster_replay.py --run --phone-unplugged --cluster-map-selected
4. Startup uses the now car-validated SAL shutdown. If and only if the exact
   captured map-cleanup crash occurs, the helper terminates that already-crashed
   process once so the factory manager can restart it. This may take about
   25 seconds. The launcher allows a longer startup window.
5. Select the factory map in the cluster again if needed. The script waits for
   actual accepted native map writes. At the prompt, confirm that real factory
   map graphics are visibly rendering before pressing Enter. If stuck at
   Starting map/Starting navigation, type SKIP; do not authorize playback.
6. Observe the saved recording. After playback, the same validated lifecycle
   restores stock navigation. Report recording visibility separately from
   whether factory maps work on radio and cluster when each is selected.
7. Return the entire new delphi-dump/_cluster_replay_* folder.

Additional evidence is collected during this same run:
- MOST readiness flags and video-transmit thread state before/after playback.
- Bounded first1MiB of actual accepted factory video, before explicit arming.
  The report gives valid prefix length; the rest of the mapping is padding.
- Actual accepted native byte/write counts and per-edge lifecycle helper logs.

Codec, packetization, recorded timing, zero-write retry limits and single-writer
ownership remain as previously validated. The recorder uses the existing owned
descriptor. No extra isoTX writer is opened. Source copying is bounded memory
copying without new I/O/allocation in the write hook.
MOST snapshots are read-only and unit-specific; they do not force readiness.

Process restart alone is not a claim of functional map restoration, and bytes
accepted by TransportServer are not a claim that recorded pixels were visible.
A full unit reboot remains manual if an unrecognized failure leaves maps stuck.
Do not run the earlier v6 package; its lifecycle is obsolete.
