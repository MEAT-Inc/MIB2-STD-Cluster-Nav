Synthetic native QNX loader fixture - not an AndroidAuto/car deployment package.

Launch mechanism resolved. Read ../../delphi-analysis/LAUNCH-MECHANISM-RESOLVED.txt.
From the project root, with the prepared Docker images:
 docker run --rm --network none --mount "type=bind,source=$PWD,target=/src" --workdir /src delphi-qnx65:8.5 sh native/loader-probe/build.sh host
 docker run --rm --network none --mount "type=bind,source=$PWD,target=/src" --workdir /src delphi-qnx65:qemu sh native/loader-probe/run-qemu.sh uip
 docker run --rm --network none --mount "type=bind,source=$PWD,target=/src" --workdir /src delphi-qnx65:qemu sh native/loader-probe/run-qemu.sh copy
The retired PowerShell wrapper and standalone static validator have been removed.
Linux baseline/linked/preloaded cases and all eight QNX subprocess cases pass.
The test also reproduces the old failure as a controlled data=uip negative case.
The corrected disposable QNX image explicitly uses data=copy for repeated runs.

These binaries contain synthetic code only. No vendor vehicle code is loaded.
Never preload libprobe_observer.so into AndroidAuto: unresolved forwarding uses
_exit(90), and the logger is single-threaded and does not preserve C++ unwinding.
run-qemu.sh copy runs the passing suite; run-qemu.sh uip checks the known failure.
No upload or vehicle launch script is included.
