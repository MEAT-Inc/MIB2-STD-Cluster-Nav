Isolated observer smoke test - first unit hardware check

Run on the connected laptop from the project root. Keep the car stationary,
infotainment on, Ethernet connected, and phone unplugged.

Review the verified local plan (no connection or vehicle write):
  python scripts/run_observer_smoke.py
Execute the explicitly opt-in test:
  python scripts/run_observer_smoke.py --run
Optional address/password:
  python scripts/run_observer_smoke.py --run --host 192.168.1.4 --ask-password

Needed on the laptop: scripts/run_observer_smoke.py, delphi_inventory.py and
 decode_delphi_observer.py beside it, plus native/observer/smoke/release/ in
this project layout. Only Python's standard library is needed; no Docker or
QNX compiler is needed to run the prepared test on the laptop.

Vehicle actions
- FTP creates one new /ramdisk/delphi-observer-smoke_<32hex> directory.
- Four verified files are uploaded and read back byte-for-byte before execution:
  observer_smoke, observer_smoke_guard, libdelphi_observer.so, libautoreceiver.so.
- The library named libautoreceiver.so here is a tiny SYNTHETIC call counter,
  not the acquired Volkswagen library. It exists only in the unique RAM folder.
- The private Telnet shell changes into that verified new directory. Only its
  files receive permissions; no working-directory failure can cause relative
  result writes elsewhere.
- A guard starts baseline and observed synthetic children. The observed child
  receives the preload and private library path; no global environment changes.
- Each child makes nine synthetic registration calls. The observer writes up to nine
  pointer/sequence records, with any drops accounted, into /dev/shmem/delphi-observer-smoke-<32hex>.bin.
- The guard polls its own unreaped child and can kill/reap only that child after
  approximately ten seconds. It never targets a process by name or supplied PID.
- Stock AndroidAuto PID/arguments are recorded before and after and must match.
- Copies of /proc/boot/procman and /proc/boot/libc.so.3 are placed in the private
  RAM folder as *.captured for FTP acquisition/offline analysis. They are data,
  are not executed, and do not become replacement runtime libraries.

There is no termination/restart of AndroidAuto or procman, no phone connection,
no navigation transport access, no factory library replacement and no persistent
startup/configuration edit. Ordinary factory behavior continues. If its PID
changes naturally during the snapshot window, the runner conservatively reports
failure and retains the evidence; it does not attempt a factory-process restore.

Results
Everything downloaded goes to delphi-dump/_observer_smoke_<time>_<id>/.
smoke-summary.json records commands, return codes, hashes and pass/failure.
observer-decoded.json contains the synthetic trace. Preserve the directory even
if the test fails. If the Telnet session times out it is not reused; a fresh FTP
connection still attempts to collect evidence. Existing files/directories are not
reused. RAM artifacts/logs are retained until explicitly removed or rebooted.

Proof scope
The identical production-candidate observer is loaded against the unit's real
libc/loader/CPU, using synthetic inputs and a synthetic provider. A pass proves
that isolated path only: it does not prove interposition in real AndroidAuto,
its native C++ behavior, phone display negotiation, video reception or cluster
navigation. actual_androidauto_interposition_tested remains false in the result.

Offline checks before release
QNX emulation: baseline, preload and an intentional watchdog timeout all pass.
Nine Python tests cover default plan-only behavior, RAM path restrictions,
upload corruption, failed cd, timed-out session, stock PID changes and trace
validation. Four release hashes are tied to those QNX-tested binaries. Static
ELF checks require ARM32 LE EABI5, no executable stack and no C++ runtime.
Build/test internals use the existing local Docker compiler/emulator; the car
runner itself is Python-only. No test has been executed on the vehicle yet.
