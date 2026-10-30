ISOLATED SECOND-ENDPOINT FACTORY PROBE - NO SECOND DISPLAY ADVERTISED

Extract into the laptop project directory. Initially phone UNPLUGGED, Ethernet
connected, ignition on, car parked and driver door closed. Run:
  python scripts/run_disconnected_observer.py --run --phone-capture --factory-probe --phone-unplugged
At CAPTURE READY swap Ethernet for the phone, open AA navigation, and observe
for at least90 seconds. The probe runs once at native primary-video endpoint
initialization; that requires the phone. It constructs a private video9/input10
pair using the fingerprinted native constructors, attaches its OWN callback
adapter using native reference-count helpers, adds one known stock configuration,
and destroys both unregistered objects. Primary endpoint/table bytes are checked.

It does NOT register these objects, modify discovery, send focus/acks/input,
connect a decoder, or request a cluster video stream. IDs9/10 remain candidates;
a snapshot showing empty slots is not reservation or proof of later vacancy.
An ABI/profile failure refuses the probe and preserves normal forwarding. Native
addresses are byte-gated for this exact firmware. Unknown object/refcount state
is quarantined without guessed destruction; private memory is reclaimed when
the observed process exits at explicit cleanup.

After at least90 seconds unplug phone, reconnect Ethernet and answer prompts.
Type PHONE REMOVED only while phone is physically unplugged. Capture expiry does
NOT restart AA. The tested protocol3 controller performs explicit cleanup only.
Return the entire new delphi-dump/_disconnect_observer_* folder, including partial
results. Never delete/modify native markers or locks to bypass refusal.

If cleanup was declined, use the EXACT path printed by the script:
  python scripts/run_disconnected_observer.py --resume "delphi-dump/<saved-folder>" --factory-probe --phone-unplugged
Do not include --phone-capture with --resume. Keep phone unplugged during resume.
A native/probe refusal needs review before another attempt.

Validated offboard: ARM32 QNX constructor-API fixture, independent callback lifetime,
reference-count transitions, two successful lifecycles, allocation failures,
bad constructor/refcount quarantine; full DSO forwarding preserves original
registers/stack/errno/return in QNX smoke tests. Python validates report identity,
main endpoint/table preservation, failures and resume. Real native constructors
have NOT been executed by this new probe on car yet. No cluster-map display is
claimed. This resolves factory/ownership before endpoint registration experiments.
