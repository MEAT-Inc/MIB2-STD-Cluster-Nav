CLUSTER BRIDGE PREFLIGHT - NATIVE GEOMETRY + PHONE FRAME TIMING
Extract into the laptop project, replacing bundled files. Start ignition on,
phone unplugged, Ethernet connected. Run:
  python scripts/run_disconnected_observer.py --run --cluster-preflight --phone-unplugged
The script first asks you to display the factory VW navigation map in the cluster.
Keep Ethernet connected. It reads the stock NavigationServer encoder geometry
and descriptor state through a fixed read-only process-memory helper. It checks
firmware bytes and process identity; it does not restart/stop/signal NavigationServer
or open/write the cluster transport. If the factory map cannot be displayed,
press Enter anyway; inactive geometry is recorded as partial, not a false pass.
Then the already-tested AndroidAuto launch lifecycle runs. At CAPTURE READY swap
Ethernet for phone and start a navigation route. Run about10 seconds, unplug phone,
reconnect Ethernet, then press Enter and follow the explicit PHONE REMOVED cleanup.
One phone connection per run. No native cluster video is replaced in this build.
This adds an81952-byte timing.bin with each codec/frame callback offset, size,
phone timestamp and local monotonic timestamp, bounded to2048 records. The video
capture remains8MiB. Native before/after snapshots corroborate unchanged identity.
Return the ENTIRE new delphi-dump/_disconnect_observer_* folder, even if partial.
If pending, use the exact folder printed by the script:
  python scripts/run_disconnected_observer.py --resume "delphi-dump/<saved-folder>" --cluster-preflight --phone-unplugged
No --phone-capture on resume. Never remove locks/markers to bypass refusal.
A passing result establishes needed dimensions/timing; it does not certify the
physical cluster decoder or activate a replacement MOST stream.
