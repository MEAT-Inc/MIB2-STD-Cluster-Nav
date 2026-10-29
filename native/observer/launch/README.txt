HOLD: persistent black screen reported on hardware. Live --run experiments are
disabled in the Python runner pending display-failure diagnosis. Do not use an
older ZIP to bypass this hold. Use the read-only collect_display_health.py.
The launch procedure below is historical and currently suspended.

Real AndroidAuto registration observer experiment

Purpose: capture the real app's service-registration call sites before changing
Android Auto video negotiation or routing any video to the instrument cluster.
This test does not enable cluster maps. The private-path hardware gate has passed.

On the connected laptop, extract androidauto-phone-capture-laptop.zip into the existing
project folder, preserving scripts/ and native/ folders. Python standard library:
  python scripts/run_androidauto_observer.py
shows the offline plan. To run the actual experiment from that project root:
  python scripts/run_androidauto_observer.py --run --phone-capture
Start with Ethernet connected and the phone unplugged. Wait for CAPTURE READY.
Then unplug the Ethernet adapter and connect the phone to the car immediately.
Open your navigation app in Android Auto and leave the phone connected for 90
seconds. Then unplug the phone, reconnect Ethernet, wait for its network link,
and press Enter in the Python routine to collect results. Follow the terminal
prompts; do not swap USB before CAPTURE READY. Park the vehicle and keep the
infotainment powered. AndroidAuto will be interrupted/restarted for the observed
launch, then interrupted/restarted again for stock restoration. The capture window is 60 seconds. The on-unit watchdog restores stock behavior
while the laptop is disconnected; allow the full 90 seconds before reconnecting.

Before any interrupt, the Python routine:
- Stages two hash-verified diagnostic files in a fresh private RAM directory.
- Copies the app, receiver library and manager into that private directory and
  downloads them to verify the exact known unit sizes and SHA256 fingerprints.
- Checks the copied manager configuration for the reviewed AndroidAuto -r entry.
- Requires the same unique AndroidAuto PID in its initial and fresh snapshots.
The proprietary files are copied from your own unit; they are not in the ZIP.

The native controller checks the app's kernel-reported executable, PID, parent
and start time. Its manager must be the expected procman executable. It compares
stock files/configuration byte-for-byte with the freshly verified private copies.
It arms an independent watchdog before installing a one-shot namespace redirect.
The manager launches the wrapper; it removes the redirect before exec, preserves
its manager-supplied argv and working directory/environment, and adds the observer
only to that replacement process. A preexisting nonempty LD_PRELOAD is refused.
No factory executable, library or startup file is edited.

The watchdog captures for 20 seconds by default, or 60 seconds in --phone-capture, removes any owned redirect, signals
only the identity-checked observed process, and verifies a fresh stock process
under the same manager. It uses SIGINT, matching the captured manager's existing
termination helper. SIGINT is not claimed to be a cooperative graceful shutdown.
Kernel identity checks and signaling are separate operations, not an atomic
compare-and-signal guarantee. There is no fallback to another PID or signal.
The watchdog ignores SIGHUP and owns a separate session so ordinary terminal
hangup/controller death does not cancel restoration. It emits readiness and final
completion itself, so the controller can disappear during the USB swap. Both the
default and longer phone window are covered in emulation, including hangup recovery.

All metadata stays in RAM. A fresh exclusive coordination marker is created at
/dev/shmem/delphi-aa-observer-active.bin. It is removed only after verified stock
restoration. If restoration cannot be verified, the retained marker blocks another
experiment. Do not rerun automatically after an incomplete result; return the
whole results folder. An instrumentation process could remain active if the app
ignores SIGINT or restoration fails; a unit restart may then be needed after review.

Evidence is saved under common delphi-dump/_androidauto_observer_<timestamp>_<token8>.
Return the entire new folder. A pass requires:
- The exact reviewed binary/configuration inputs and successful remote actions.
- A valid 512-byte controller report, verified process identities and restoration.
- A stable decoded log owned by the observed process with the original receiver
  symbol at the reviewed offset, and intercepted callers matching known call sites
  in the verified AndroidAuto image, normalized by its reported load base.
The video-registration call site is reported separately. No endpoint object is
read, fabricated or modified. The caller-address record itself demonstrates the
interposition; external debugger/shared-library name metadata is not used as proof.

The report parser accepts the previous version-1 hardware result and current
version-2 results with explicit 20/60-second profiles.
A complete restored experiment with zero registration calls has exit code 2 and
is reported separately. It may need a later phone-session capture. Unknown results,
failed restoration, changed identities, wrong binaries or unmatched callers fail
closed; none are treated as proof of Android Auto map support.

Build and review (offboard only): native/observer/launch/test-qemu.sh in the existing
QNX container, then python scripts/package_androidauto_observer.py. The emulation
uses a synthetic app with your acquired process manager; it never runs the real
AndroidAuto binary. No emulator helpers or proprietary inputs are distributed.
