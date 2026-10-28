Synthetic native QNX loader fixture - not an AndroidAuto/car deployment package.

Launch mechanism resolved. Read ../../delphi-analysis/LAUNCH-MECHANISM-RESOLVED.txt.
Run .\scripts\test_qnx_probe.ps1 from the project root in PowerShell.
Linux baseline/linked/preloaded cases and all eight QNX subprocess cases pass.
The test also reproduces the old failure as a controlled data=uip negative case.
The corrected disposable QNX image explicitly uses data=copy for repeated runs.

These binaries contain synthetic code only. No vendor vehicle code is loaded.
Never preload libprobe_observer.so into AndroidAuto: unresolved forwarding uses
_exit(90), and the logger is single-threaded and does not preserve C++ unwinding.
run-qemu.sh copy runs the passing suite; run-qemu.sh uip checks the known failure.
No upload or vehicle launch script is included.
