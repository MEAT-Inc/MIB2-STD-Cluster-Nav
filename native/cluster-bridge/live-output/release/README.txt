LIVE ANDROID AUTO CLUSTER TRIAL v14
===================================
Keeps the full800x480 map, density140 and120px horizontal UI insets.
Requests64px bottom UI inset so the tilted-view vehicle icon stays inside the
visible map. Video margins stay zero; the map background still fills the frame.

Retains the proven first-second startup keyframes at0/333/666ms. After that,
video catches up at1.25x for about3seconds, then keeps250ms of added buffering
instead of1000ms. All original coded pictures remain in order; no re-encoding
or picture drops are used. Actual cluster decoder latency needs an on-car check.

Extract the ENTIRE ZIP into a fresh laptop folder. Park, ignition on, factory
maps working, phone unplugged and Ethernet connected. Run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
At CAPTURE READY swap Ethernet for phone and start a route promptly. Once startup
has settled, compare the cluster with the radio and check the car icon in tilted
and top-down views. Check that the directions box still fits and no black bars
appear. Unplug phone, reconnect Ethernet and follow the usual cleanup prompts.
Do not toggle map location until answering the automatic-return question.
Return the whole delphi-dump/_disconnect_observer_* folder with visual feedback.

The bounded30-second trial still starts at the FIRST phone video frame. Automatic
return at the deadline is expected; the v11 graceful completion fix is retained.
If cleanup is pending, keep phone unplugged and resume with this SAME bundle.
