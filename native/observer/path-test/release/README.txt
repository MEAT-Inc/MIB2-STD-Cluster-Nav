Private-path observer and watchdog hardware check

This is the next hardware gate toward observing AndroidAuto display registration.
It tests whether this unit can redirect an existing executable in a private RAM
folder, remove that redirect before exec, load the existing observer, and restore
normal launches after failures. It does not stop or instrument factory AndroidAuto.

On the car-connected laptop, extract observer-path-test-laptop.zip into the project
folder, preserving its scripts/ and native/ folders. Python standard library only:
  python scripts/run_observer_path_test.py
shows the offline plan. To perform the test:
  python scripts/run_observer_path_test.py --run
Use --host ADDRESS if your unit does not use 192.168.1.4. Existing FTP/Telnet defaults
match the smoke collector; --ask-password prompts for a different FTP password.

Keep the Ethernet adapter connected and the phone unplugged for this test. Park
the vehicle and keep the infotainment unit powered throughout the run. It normally
finishes in under a minute; evidence downloads may take longer.

Exact remote actions:
- Create a fresh /ramdisk/delphi-path-test_<random 32-hex token> directory by FTP.
- Upload five small files and verify each by downloading and comparing all bytes.
- Record factory AndroidAuto PID and arguments before and after the private test.
- Execute path_test, which accepts only that strictly named private directory.
- Redirect only that directory's path_child name to its own path_test wrapper.
  Factory executable/library paths cannot be supplied as redirect targets.
- Run six short synthetic app launches. Only the second loads the observer.
- Exercise one-shot restore, failures before/after detachment, and watchdog cleanup
  when the installer exits. A watchdog is armed before each redirect is installed.
- Collect report.bin, observer.bin, the test log and two stock process snapshots.

Outputs are in the existing common delphi-dump/_observer_path_<timestamp>_<token8>
folder. Return that entire folder for review. PATH TEST PASS requires all native
markers, all commands returning zero, a valid 208-byte six-launch report, matching
observer trace, successful watchdog restoration, and unchanged stock PID/argv.

Private RAM evidence is retained until removed explicitly or the unit reboots.
Each child has a bounded wait; a hung synthetic child may be killed/reaped by its
own parent. Factory apps and their process manager are never signaled or restarted.
The routine edits no startup configuration and loads no files into a factory app.

Scope: this confirms the actual unit's pathname/observer behavior in private RAM.
It does not prove real AndroidAuto interposition, secondary video negotiation or
maps in the instrument cluster. The later supervised observer experiment depends
on this result; do not apply these binaries to factory executable paths.

Build-only qemu-runner and filesystem utilities are excluded from the portable
package. They exist solely to test these exact five files in the emulator.
