LIVE INPUT TEST v1
==================
Goal: move actual phone frames through the new owned queue and determine whether
secondary focus refreshes produce fresh keyframes. It writes RAM captures; this
test does not replace the cluster video writer.

1. Extract the entire ZIP into a fresh folder on the connected laptop.
2. Park, ignition on, phone unplugged, Ethernet connected, working factory maps.
3. Run:
 python scripts/run_disconnected_observer.py --run --keyframe-probe --phone-unplugged
4. Select the factory map in the cluster at the prompt.
5. At CAPTURE READY swap Ethernet for phone, start a Google Maps route, and let
 it run about12 seconds. Unplug phone, reconnect Ethernet, then press Enter.
6. Follow the existing explicit phone-disconnected cleanup prompts.
7. Return the entire delphi-dump/_disconnect_observer_* folder.

This run:
-Adds at most three native focus notifications on secondary video channel9,
 after the current frame ACK. No extra AndroidAuto thread is created.
-Copies borrowed phone frames into a fixed four-slot/1MiB-per-frame queue.
 A separate bounded reader writes live-copy.h264 plus timing data in RAM.
 Frames are checked byte-for-byte against the receiver capture on the laptop.
-Samples native map geometry once per second with the same unit monotonic clock,
 without restarting NavigationServer or opening the cluster transport.
-Uses the existing validated AndroidAuto launch and disconnected cleanup.
 Queue overflow drops data and waits for codec+IDR; it never blocks phone ACKs.
 The capture reader stops within30 seconds or when its source process ends.
