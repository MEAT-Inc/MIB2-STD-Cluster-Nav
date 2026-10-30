SECOND-ENDPOINT FACTORY + CALLBACK PROBE (FAST PROFILE)

Extract into the laptop project directory. Initially connect Ethernet with phone
unplugged, ignition on. Run:
  python scripts/run_disconnected_observer.py --run --phone-capture --factory-probe --phone-unplugged
At CAPTURE READY swap Ethernet for the phone and open Android Auto navigation.
Once navigation starts, unplug phone and reconnect Ethernet. Press Enter when
its link is ready. No90-second wait is required. The native20s
checkpoint leaves AndroidAuto running; Python waits for it if still pending.
Type PHONE REMOVED only with phone unplugged to request explicit cleanup.
Return the entire new delphi-dump/_disconnect_observer_* folder.

This build fixes the main-executable dladdr trigger which prevented the previous
probe from entering. Exact ET_EXEC caller and fingerprinted helper-byte checks
remain. It combines native video/input construction, independent shared ownership,
configuration/destruction and start/stop/codec/data/focus callback ABI checks.
Data checks verify both halves of a64-bit timestamp, borrowed-buffer identity,
offset/length and payload without retaining the borrowed bytes. Native Start/
Stop/Focus calls use local argument views whose exact read offsets are profiled;
no virtual protobuf calls, serialization or packet sends use those test views.

Candidate endpoints remain UNREGISTERED; no discovery, focus notification, ack,
input event or second stream is sent. Primary object/table snapshots must match.
Successful setup/ack/backpressure and real endpoint registration remain next.
Factory success does not reserve IDs9/10 or prove a working cluster stream.
Unknown object/refcount state is quarantined until process exit. No timed restart
or exception path authorizes cleanup. Native identity/lock checks remain active.
If cleanup was declined, use the exact printed resume folder:
  python scripts/run_disconnected_observer.py --resume "delphi-dump/<saved-folder>" --factory-probe --phone-unplugged
No --phone-capture on resume. Preserve a refused/partial result for review.
