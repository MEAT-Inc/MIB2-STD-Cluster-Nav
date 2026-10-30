OBSERVER PHONE SESSION TRIAL - EXPLICIT DISCONNECTED CLEANUP

Extract into the laptop project folder. Park the car, ignition on.
Initially connect Ethernet, with phone physically UNPLUGGED. Run:
  python scripts/run_disconnected_observer.py --run --phone-capture --phone-unplugged

The 60-second capture checkpoint DOES NOT restart AndroidAuto. The observed
app and bounded observer log remain active until explicit cleanup. There is
no forced timed restart, including on laptop/controller loss.

After90 seconds unplug the phone, reconnect Ethernet, wait for link, then press
Enter at the laptop prompt. Type exactly
PHONE REMOVED only when the phone is physically unplugged; this requests the
identity-checked cleanup and verifies a fresh stock AndroidAuto process.

Anything else leaves cleanup pending and prints the exact resume command:
  python scripts/run_disconnected_observer.py --resume "delphi-dump/<saved-folder>" --phone-unplugged
Do NOT add --phone-capture to resume. Keep phone unplugged during resume.
Return the ENTIRE new delphi-dump/_disconnect_observer_* folder, even if partial.

The default without --phone-capture remains the20s Ethernet-only control test.
The native controller and original v1 observer are unchanged from the successful
hardware control trial. This runner temporarily redirects ONE supervised launch
to a RAM copy and restarts AA at the start and explicit disconnected cleanup.
Factory files/configuration stay intact. A pending marker blocks overlapping
experiments. Never remove markers/locks to bypass a refusal. Do not retry a
refused cleanup automatically; preserve the results for review.

Validation: real unit20s pending/explicit cleanup verified, native QNX synthetic
60s/controller-loss/identity/lock/idempotence tests, Python handoff/resume/failure
tests. Phone-session health still needs this trial. No endpoint registration is
changed. No secondary video stream or cluster map is enabled by this package.
The old timed observer runner remains disabled.
