Synthetic one-shot launch transaction bench

This directory is an emulation-only prototype. It is not a vehicle deployment
package. All redirect paths are compile-time fixed to synthetic /proc/boot/tx_*
executables; there is no AndroidAuto target or configurable path argument.

Passed on QNX 6.5 ARM in QEMU:
1. Original synthetic executable runs without the observer.
2. A process-manager namespace symlink shadows an existing executable. The wrapper
   removes its own redirect before exec, loads the unchanged observer candidate,
   and preserves the child PID, parent PID and argv. A subsequent launch uses the
   original executable with no observer. Child preload does not leak to parent.
3. Failure after detachment returns an error; a modeled manager retry launches
   the original executable successfully.
4. Failure before detachment leaves the redirect for the armed watchdog to remove;
   the subsequent original executable launch succeeds.
5. Installer exit leaves an independent watchdog, which removes its owned redirect
   and allows normal launch. Original/copy fixture contents remain equal.

Evidence: qemu/qemu.log, qemu/tested.sha256, qemu/summary.json.
The controller must exit 0 and all positive markers must be present.
The bench uses FNV-32 for in-image fixture identity; the host report records SHA256.

The IFS stores the two fixture executables as raw bytes, preserving their equality
for file hashing; data=copy allows repeated execution. Kernel/system files retain
normal mkifs processing. All build scratch files reside in disposable Linux /tmp.

Build/test within the existing delphi-qnx65:qemu container:
  sh native/observer/transaction/test-qemu.sh
The container must bind this project at /src. No new PowerShell routine is needed.

Limitations before any real AndroidAuto launcher:
- This models manager parenthood and retry, and does not run captured procman.
- Verify the actual graceful stop, application state, start and readiness protocol.
- Resolve real executable path selection, argv (including manager-added -X values),
  working directory, inherited environment and executable-path assumptions.
- Add ownership/race checks, unique RAM paths, cryptographic target checks, bounded
  recovery and collection to a Python laptop runner. Recheck pathmgr behavior on
  the actual unit using private synthetic paths before any factory-path redirect.
- Test observer interposition at the real app-to-receiver boundary. Full-map phone
  negotiation and cluster video remain separate, unimplemented gates.

No factory files, startup configuration or live vehicle processes were changed.
