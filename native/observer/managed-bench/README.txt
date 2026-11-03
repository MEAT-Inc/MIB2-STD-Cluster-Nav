Captured-manager integration bench (emulation only)

Purpose: test the actual hash-verified procman binary from the user's unit with
synthetic applications, rather than a hand-written model of its restart policy.
No captured AndroidAuto executable is run. No vehicle connection is made.

Build and QEMU launch: test-qemu.sh, inside the existing delphi-qnx65:qemu container
with the project mounted at /src. Host evidence review:
  python -B scripts/review_managed_bench.py
  python -B -m unittest discover -s scripts/tests -p test_managed_bench_review.py

The private emulator starts the captured manager under a unique XSAL instance.
Only its synthetic configuration is loaded. Its one app entry uses the built-in
androidauto app name, but the executable is /proc/boot/managed_child, a tiny fixture.
This name selects a known manager application ID, not the factory AndroidAuto app.
The configuration uses -l0 to avoid requiring an actual SAL app readiness handshake.

Verified sequence:
1. First synthetic child returns 7. The manager restarts it with -X1792.
2. The second child waits. A watchdog is armed before the runner installs a
   namespace redirect of the fixture's path. The runner sends SIGINT to this
   fixture, and the real manager restarts it through managed_wrapper with -X2.
3. The wrapper removes its owned redirect before exec, preserves argv, and sets
   LD_PRELOAD only for its own replacement process. The identical synthetic
   executable copy runs with the unchanged observer library. Nine original
   registration calls and nine captured records pass; parent remains procman.
4. The runner interrupts that fixture. The real manager starts the normal fixture
   path again with -X2, with no observer loaded. A normal zero exit is not restarted
   during the bounded 1.5 second observation window.
5. The runner terminates/reaps only the emulator manager it created. This expected
   SIGTERM and the two expected synthetic-child SIGINT events are checked explicitly.

Expected missing trace_config.json warnings are the stripped-down emulator setup.
All copied native fixtures are tested under QNX 6.5 ARM. The two fixture executable
copies are stored raw in the IFS and data=copy permits repeated execution.
No proprietary binary is bundled or redistributed by this test directory.

Limits:
- Hardcoded synthetic paths prevent selecting a vehicle target.
- This is an emulator fixture, not a production vehicle controller. Some failure
  branches rely on disposal of the entire emulator for complete process cleanup.
- The dummy app does not initialize SAL; the real app readiness/state protocol,
  shutdown cooperation, and behavior of all its dependent libraries are untested.
- The manager's signal-based recovery works here; SIGINT is not claimed to be a
  graceful AndroidAuto shutdown. Do not send it to the factory app from this bench.
- Namespace ownership/races and watchdog behavior on the actual unit still need
  private-path testing before any redirect of a factory executable.
- Real app executable-path/relative-resource assumptions, hash verification,
  PID/parent identity checks, bounded recovery and a Python-only laptop routine
  are still required before a supervised AndroidAuto observer experiment.
