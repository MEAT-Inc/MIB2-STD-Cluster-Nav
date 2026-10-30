Read-only Android Auto display configuration / discovery capture

Extract androidauto-display-capture-laptop.zip into the laptop project root.
Use Python 3 (standard library only on the connected laptop):
  python scripts/run_androidauto_observer.py --run --phone-capture --display-capture

Park the vehicle and keep infotainment powered. Start with Ethernet connected
and the phone unplugged. Wait for CAPTURE READY before changing USB devices.
Immediately replace the Ethernet adapter with the phone. Start Android Auto and
open navigation. Leave the phone connected for 90 seconds, reconnect Ethernet,
wait for its network link, then press Enter in the routine to collect.
The native capture window is 60 seconds; the watchdog restores stock AndroidAuto
without the laptop connection. AndroidAuto is restarted for capture/restoration.

The controller and stock hash/configuration/identity checks are unchanged from
the phone-registration capture that passed on this car. This observer extends
registration logging with video configuration, focus and outgoing control data.
It records this plus seven integer configuration arguments without reading the
VideoSink object. It copies only outgoing channel-0 buffers whose first two bytes
are 00 06 and whose length is 2..4096. Oversized candidates are metadata only.
Original arguments, return values and errno are preserved by tail forwarding.
No packet bytes, service descriptors, endpoint objects or firmware are changed.

The new observer passed QNX emulation; these three extra hooks have not yet been
proven on the real unit. The library-internal queue call might bypass preload;
a missing discovery record is an investigation result, not evidence of a second
display. Only exact known stock app, receiver and manager fingerprints are allowed.
The ZIP includes no proprietary unit programs or emulator fixtures.

The watchdog uses the tested one-shot RAM namespace redirect and child-only
LD_PRELOAD. It removes the redirect before running the observed app and verifies
a fresh stock PID under the original manager afterward. It ignores terminal
hangup in its independent session. SIGINT is sent only after held kernel identity
checks; checking and signaling are separate operations. Factory files are not
edited. If restoration cannot be verified, the active marker blocks another run.
Do not retry automatically after an incomplete result; return the whole folder.

Results stay in delphi-dump/_androidauto_observer_<timestamp>_<token8>.
Return the entire new folder, including display.bin and display-decoded.json
when available. A display pass needs verified stock restoration, valid base
registration evidence, a configuration record correlated to the registered video
object and known app caller, and a valid discovery response at the known receiver
caller. Missing extra data retains the base restoration/registration evidence
but cannot pass the display gate. The parser reports dropped records explicitly.
This capture does not enable Android Auto maps in the cluster.

Offline plan (no network):
  python scripts/run_androidauto_observer.py --phone-capture --display-capture
Offboard build: native/observer/display/test-qemu.sh in the QNX build container,
then python scripts/package_androidauto_display.py.
