# MIB2 Cluster Navigation

Research and diagnostic tooling for investigating Android Auto and CarPlay navigation video in the instrument cluster of a Delphi MIB2 infotainment system.

**Status — October 28, 2026:** the native observer candidate has passed an isolated hardware smoke test on the unit using a synthetic registration provider. The capture records nine observer entries, zero drops, and unchanged stock AndroidAuto process identity. Firmware preflight and supervisor review are complete for the captured snapshots. Real AndroidAuto interception and phone-to-cluster video remain unproven.

Working folder: `.`.

## Target system

| Item | Project context |
| --- | --- |
| Vehicle | User-reported 2019 USDM Volkswagen Golf R |
| Infotainment | Discover Media, part number `3Q0035876B` |
| Software | MU0890 / `MST2_US_VW_P0890D` (`P` followed by zero) |
| Operating system | Inventory records QNX Neutrino 6.5.0 |
| Platform | ARM little-endian, TI-DRA74X-PG1.1; two Cortex-A15 processors |

Findings and sample fingerprints apply to this build. Compatibility with other units or software trains is unproven.

## Current progress

| Area | Latest evidence | Remaining work |
| --- | --- | --- |
| Acquisition | Initial software/configuration verification records 562 matching byte-count/SHA256 comparisons. Runtime bridge components and fresh vehicle preflight captures are available. | Manifest consistency is not vendor authentication or verification of loaded-memory bytes. |
| Native video transport | Traced the `isoTX` encoder path, 188-byte MPEG-TS format, matching reconstructed PAT/PMT CRCs, synchronous copy behavior, and single-writer channel ownership. A full queue returns zero bytes with EOK. | Complete MOST consumer lifecycle and abnormal reader-close handling remain unaudited. |
| Android Auto discovery | Identified protocol 1.3, service registration, discovery serialization, and buffer/queue ownership. Host fixtures exercise a secondary descriptor and buffer replacement. | The old schema lacks modern cluster-display metadata. Phone acceptance and a native discovery modification are unproven. |
| HMI/control bridge | Traced `screen-cda` application `0x55`, activation/deactivation/rate messages, response fields, geometry propagation, and SAL millisecond clock units. Java analysis converted 19,406 classes and decompiled 414 for targeted inspection. | Active geometry, measured cadence, and precise encoder parameter units need corroboration. Conversion checks are not full bytecode verification. |
| Native observer | Packaged an entry-only observer and decoder; host, QNX ARM, static, and packaging gates are reported passing. | Real application binding, constructor ordering, timing, and controlled stock restoration are not validated on the vehicle. |
| Vehicle preflight | Fresh `AndroidAuto` and both receiver-library aliases match expected SHA256 values. AndroidAuto was running with `-t`; its receiver mapping was identified. | Captured process IDs and addresses are snapshots. File hashes do not verify loaded-memory contents. |
| Supervisor review | Seven read-only checks succeeded. Process ancestry confirms AndroidAuto was a direct child of procman; configuration contains both AndroidAuto and AndroidAutoServices. | Vendor flag semantics/control API and a verified stock restoration procedure remain unresolved. |
| Isolated hardware smoke | Baseline and observed synthetic children passed against the actual unit runtime. The decoded trace contains nine records with zero drops; before/after stock PID/arguments match. procman and libc were acquired for offline analysis. | This does not test interception in real AndroidAuto, phone negotiation, or cluster video. |
| CarPlay | Initial screen registration and H.264 references provide a separate investigation path. | Additional phone-display support has not been established. |

The [consolidated status](delphi-analysis/INVESTIGATION-STATUS.txt) contains historical sections followed by updates. For current implementation evidence, start with [PRODUCTION-OBSERVER-RESULTS.txt](delphi-analysis/PRODUCTION-OBSERVER-RESULTS.txt) and the [observer instructions](native/observer/README.txt). Later captures supersede earlier statements that fingerprints, supervisor data, or an isolated hardware run are still missing. Some older instructions still state that no vehicle smoke test has run; use the captured result described below for current status.

### Latest vehicle evidence

[OBSERVER-PREFLIGHT-REVIEW.txt](delphi-analysis/OBSERVER-PREFLIGHT-REVIEW.txt) explains the initial map-parser false negative: `pidin` displayed the receiver as `bautoreceiver.so.1`, omitting the leading `li`. The corrected parser recognizes the shortened name. [OBSERVER-PREFLIGHT-LATEST-REVIEW.json](delphi-analysis/OBSERVER-PREFLIGHT-LATEST-REVIEW.json) records another passing standard preflight and 15 collector-review tests.

The [supervisor capture summary](delphi-dump/_observer_preflight_20261029_000006_d6c5d4d0/preflight-summary.json) records seven successful commands. The local follow-up review confirms AndroidAuto's procman parent and configuration entries for both smartphone processes. The `-l20`, `-x10`, `-r`, and `-c15` values are captured evidence; their precise vendor semantics are not assumed. Captured PIDs must not be hard-coded into a controller.

The latest local smoke collection is `delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce/`, approximately 8:51 p.m. Eastern on October 28 (the directory name uses UTC). Its `smoke-summary.json` records `passed=true`, `stock_processes_unchanged=true`, and `actual_androidauto_interposition_tested=false`. Baseline/observed children used the actual unit's libc/loader with a synthetic provider in a private RAM namespace. The decoded log contains nine entries and zero drops; procman/libc copies were retained for offline analysis.

The local `delphi-analysis/control-runtime/hardware-review.json` independently records seven verified artifact hashes and the same hardware result. These new smoke captures, control-runtime findings, and some runner/release files are pending local changes outside this README-only commit; a fresh remote checkout may not yet contain them. Their paths are listed as local evidence rather than download links.

The isolated test uploaded and executed synthetic test files in RAM. It did not instrument or restart the managed AndroidAuto process, modify startup configuration, or test cluster transport. A successful hardware fixture is a narrower result than successful real application interposition.

## Observer candidate

The [observer release instructions](native/observer/release/README.txt) describe the shared library, decoder, manifest, and operating limitations. The previously referenced `native/observer/delphi-observer-v1.zip` is absent from the current working tree; use the unpacked release files. The local smoke release is separate and includes a synthetic provider, guarded test executables, and the observer candidate.

The observer records existing `registerService` call entries: caller address, opaque receiver/endpoint identities, process/thread IDs, and accepted-record sequences. It tail-forwards to the original function, replacing the earlier enter/leave design. It does not inspect endpoint objects, modify discovery, request video, or record return values, completion, or duration.

Logging uses a fixed RAM mapping with 1,024 records and a nonwaiting try-lock. Contended/full logs drop metadata while retaining forwarding. Logging failures disable logging; failure to resolve the original function or verify its owning module refuses startup with exit code 125. These behaviors and limits are detailed in [native/observer/README.txt](native/observer/README.txt).

The recorded validation includes eight QNX ARM cases; multithreaded fixtures with 2,024 native calls; return/errno, exception, recursion, fork-forwarding, and ARM ABI checks; and eight decoder tests. The fixture C++ runtime is synthetic, not the vendor runtime. Those saved results were reviewed for this README update; the suites were not rerun.

The [release manifest](native/observer/release/manifest.json) still records `vehicle_validated=false`, `runtime_fingerprints_verified=false`, and `deployment_ready=false`. These flags predate later file preflight and isolated hardware evidence. The manifest has not been recertified: the later results do not establish real application interception or deployment readiness.

The smoke fixture now has a recorded isolated hardware pass. Its local runner, release, and source updates remain pending outside this documentation commit. Emulator baseline/observed/watchdog controls and nine offline runner tests are reported passing in the local supervisor review; this README review did not rerun them.

## Repository contents

```text
.\
|-- README.md                     Project overview and current status
|-- .gitignore                   Excludes local tooling and Python caches
|-- scripts/                     Collection, analysis, build, and test tools
|   |-- USAGE.txt                General setup and collection instructions
|   |-- OBSERVER-PREFLIGHT.txt   Read-only vehicle preflight instructions
|   |-- RUNTIME-COLLECTION.txt   Targeted runtime acquisition notes
|   |-- collect_observer_preflight.py  Full/supervisor-only preflight collector
|   |-- run_observer_smoke.py   Local plan/opt-in isolated hardware runner
|   |-- inspect_control_runtime.py  Local acquired-runtime analysis
|   |-- trace_procman_control.py  Local process-manager control tracing
|   |-- delphi_inventory.py      Selected FTP collection and optional inventory
|   |-- collect_delphi_runtime.py  Runtime component acquisition/staging
|   |-- inspect_delphi.py        Manifest verification and ELF/string triage
|   |-- decode_delphi_observer.py  Capture decoder
|   |-- test_delphi_observer.ps1  Host/QNX validation and packaging
|   `-- ...                     Discovery/HMI/transport research and tests
|-- native/
|   |-- observer/               Sources, fixtures, build outputs, and release files
|   |   |-- release/            Library, decoder, manifest, and instructions
|   |   `-- smoke/              Smoke fixture, local release, and hardware runner support
|   `-- loader-probe/           Isolated QNX loader experiment and emulator setup
|-- delphi-analysis/             Findings, disassembly, JSON, and string extracts
|   |-- control-runtime/        Local hardware verification and runtime analysis
|   |-- extracted/              Extracted image artifacts
|   |-- display-hmi-java/       Java HMI analysis
|   `-- bench/                  Optional bench investigation plan
|-- delphi-dump/                 Acquired files and per-run collection reports
|   |-- delphi-inventory.txt    Original inventory transcript
|   |-- _observer_preflight_*/  Preflight commands, payloads, and summaries
|   `-- _observer_smoke_*/      Local isolated hardware logs and runtime captures
`-- .tools/                     Local analysis/build dependencies (Git-ignored)
```

This outline includes local work in progress as well as tracked files. Keep acquisition manifests with their payloads. String extracts, disassembly, and decompiled artifacts require interpretation using the associated findings.

## Using the tools

```powershell
Set-Location -LiteralPath '.'
```

Read [scripts/USAGE.txt](scripts/USAGE.txt) for general setup and [OBSERVER-PREFLIGHT.txt](scripts/OBSERVER-PREFLIGHT.txt) for the current Python preflight interface. Historical notes mention a PowerShell preflight wrapper; the current entry point is `collect_observer_preflight.py`.

The general collectors use Python 3.10+ and the standard library. Research utilities and native builds have script-specific dependencies; native validation uses prepared Docker/toolchain/emulator images. Substitute `python` for `py -3` if appropriate.

Show collector options without connecting:

```powershell
py -3 .\scripts\delphi_inventory.py --help
py -3 .\scripts\collect_observer_preflight.py --help
```

For a future read-only supervisor refresh with the documented direct connection established:

```powershell
py -3 .\scripts\collect_observer_preflight.py --supervisor-only
```

Current full preflight collects fourteen shell commands plus three fresh firmware files; supervisor-only mode collects seven commands without FTP. Each creates a fresh `delphi-dump/_observer_preflight_*` directory. It does not upload files, stop/restart processes, or launch the observer. Process environment is saved locally. The existing supervisor capture has been reviewed for ancestry/configuration; its presence alone does not resolve the control API or restoration procedure.

The general inventory collector defaults to the project's `delphi-dump/`, preserves existing final files, and keeps `_collection_*` reports. The runtime collector's optional `--stage-boot-files` mode creates temporary remote RAM-disk copies; read [RUNTIME-COLLECTION.txt](scripts/RUNTIME-COLLECTION.txt) for that distinct behavior. FTP/Telnet are unencrypted and use the documented trusted direct service connection.

The local smoke runner defaults to a plan without connecting:

```powershell
py -3 .\scripts\run_observer_smoke.py
```

Its explicit `--run` mode uploads and executes synthetic tests in a fresh RAM directory, collects logs/runtime copies, and checks stock process identity before/after. It is an active hardware test, unlike read-only preflight. Review `native/observer/smoke/README.txt` and the local release before any rerun; the existing successful capture makes another run unnecessary for documenting this milestone. These runner files are pending outside this README commit.

Offline validation commands:

```powershell
py -3 -m unittest discover -s .\scripts -p "test_*.py" -v
.\scripts\test_delphi_observer.ps1
.\scripts\test_qnx_probe.ps1
py -3 .\scripts\validate_qnx_probe.py
```

Python discovery covers matching test modules; separately named research and native checks have their own runners. `inspect_delphi.py` regenerates verification/ELF/string reports from its hard-coded project dump path and selects the first globbed manifest. Confirm the intended acquisition before rerunning it when multiple manifests exist.

Decode a copied observer capture with the script below; the filename is an example, not an existing capture claim:

```powershell
py -3 .\scripts\decode_delphi_observer.py .\delphi-dump\observer\capture.bin --output .\delphi-dump\observer\capture.json
```

Inventories, environments, configuration files, and logs may contain private data. Review acquisition artifacts before sharing them.

## Next steps

1. Continue offline analysis of the acquired procman/libc binaries to establish the actual supervision/control mechanism and a verified stock restoration procedure.
2. Reconcile release/readiness metadata and historical instructions with the successful preflight and isolated hardware evidence; review and publish the pending smoke tooling/evidence separately.
3. Establish a controlled real-application diagnostic launch plan, including original-symbol binding, constructor ordering, timing, and return to stock behavior.
4. Collect/decode actual registration evidence before changing discovery or requesting cluster video.
5. Complete receiver lifetime/input contracts, remaining MOST lifecycle analysis, and active geometry/rate/codec corroboration before evaluating secondary phone video and transport integration.

The isolated hardware observation path now works. The next milestone is verified observation of the real AndroidAuto application; cluster-navigation integration remains future work.
