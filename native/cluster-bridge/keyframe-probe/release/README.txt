LIVE INPUT TEST v9
==================
Goal: verify actual phone frames through the owned queue after a delayed phone
connection, with factory encoder sampling during the live feed. It writes RAM captures; this
test does not replace the cluster video writer.

1. Extract the entire ZIP into a fresh folder on the connected laptop.
2. Park, ignition on, phone unplugged, Ethernet connected, working factory maps.
3. Run:
 python scripts/run_disconnected_observer.py --run --live-input --phone-unplugged
4. Select the factory map in the cluster at the prompt.
5. At CAPTURE READY swap Ethernet for phone, start a Google Maps route, and let
 it run about12 seconds. Unplug phone, reconnect Ethernet, then press Enter.
6. Follow the existing explicit phone-disconnected cleanup prompts.
7. Return the entire delphi-dump/_disconnect_observer_* folder.

This run:
-Disables ineffective focus refresh notifications. No extra AndroidAuto thread
 is created. Waits up to180 seconds for the first usable phone frame.
-Copies borrowed phone frames into a fixed four-slot/1MiB-per-frame queue.
 A separate bounded reader writes live-copy.h264 plus timing data in RAM.
 Frames are checked byte-for-byte against the receiver capture on the laptop.
-Samples native map geometry once per second with the same unit monotonic clock,
 without restarting NavigationServer or opening the cluster transport.
-Uses the existing validated AndroidAuto launch and disconnected cleanup.
 Queue overflow drops data and waits for codec+IDR; it never blocks phone ACKs.
 The capture reader stops30 seconds after the first usable frame, or when its
 source process ends. The connection wait has a separate180-second limit.
