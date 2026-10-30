SECONDARY ANDROID AUTO VIDEO NEGOTIATION EXPERIMENT

Extract into the laptop project directory, replacing bundled scripts. Initially
phone unplugged, Ethernet connected, ignition on. Run:
  python scripts/run_disconnected_observer.py --run --secondary-stream --phone-unplugged
At CAPTURE READY connect phone, open navigation and START A ROUTE. Let it run
about10 seconds, then unplug phone and reconnect Ethernet. Follow the cleanup
prompt; PHONE REMOVED must only be entered with phone physically unplugged.
The20s native checkpoint leaves AA running. No90-second hold or extra door/
display questions. Use ONE phone connection per run; collect rather than
reconnecting the phone again inside the same experiment.

This is the first live second-stream experiment. It first self-checks the exact
native constructors, reference ownership, configuration index0, private native
key sets, callback ABI and destruction. Only a passing self-check allows two
real endpoints (video9/input10) to be registered in EMPTY router slots. Native
InputSource supports keycodes23/65536 and handles real binding/channel messages.
Wire metadata associates main video1/input2 with display0 and secondary9/10
with cluster display1. All other wire content is preserved.

The independent video adapter handles setup/start/stop/config/focus and records
borrowed H.264 bytes synchronously, bounded to8MiB. Frame acknowledgements use
only the secondary sink/session. No primary decoder/callback owner is reused.
No data is sent to the MOST/FPK cluster transport in this build. It will NOT yet
show maps in the instrument cluster; the result tests actual phone acceptance
and a separate video stream.

Original stock discovery is retained before registration. A failed first rewrite
falls back to stock bytes and removes only pointers still owned by this cohort;
a later rewrite failure can reuse the last known good response. Private diagnostic
objects remain valid until process exit; no unsafe descriptor-owned memory is
freed during rollback. Native teardown/reused-router checks retire the experiment.
The tested controller still cleans up only on explicit disconnected confirmation.
No firmware files/configuration are changed; the experiment lives in RAM.

Return the ENTIRE new delphi-dump/_disconnect_observer_* folder, including partial
results. It contains factory.bin, secondary.bin (registration/negotiation/frame
counters), secondary.h264 (possibly empty), discovery.bin (original and offered
plaintext discovery), native control results and transcripts. An empty video
file is a diagnostic outcome, not a successful stream.
If cleanup was declined, use the exact printed folder:
  python scripts/run_disconnected_observer.py --resume "delphi-dump/<saved-folder>" --secondary-stream --phone-unplugged
No --phone-capture on resume. Preserve refusal results; do not remove native
markers/locks to bypass identity checks. The old forced-timer observer stays held.
