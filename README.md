# MIB2 Cluster Navigation

Research and diagnostic tooling for investigating Android Auto and CarPlay navigation video in the instrument cluster of a Delphi MIB2 infotainment system.

**Status — October 28, 2026:** the native registration observer candidate is built and packaged, with passing host and QNX ARM emulator results recorded. Fresh vehicle firmware/process preflight checks pass, and a subsequent read-only supervisor capture is ready for review. A working phone-to-cluster video integration and live observer binding remain unproven.

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
| Supervisor capture | The latest supervisor-only acquisition contains seven successful read-only commands, including process ancestry and `/etc/procman_core.cfg`. | Interpret supervision/restart policy and establish a verified restoration plan. `ready_for_review` does not establish deployment readiness. |
| CarPlay | Initial screen registration and H.264 references provide a separate investigation path. | Additional phone-display support has not been established. |

The [consolidated status](delphi-analysis/INVESTIGATION-STATUS.txt) contains historical sections followed by updates. For current implementation evidence, start with [PRODUCTION-OBSERVER-RESULTS.txt](delphi-analysis/PRODUCTION-OBSERVER-RESULTS.txt) and the [observer instructions](native/observer/README.txt). Later reports and captures supersede earlier statements that fingerprints or supervisor data have not been collected.

### Latest vehicle evidence

[OBSERVER-PREFLIGHT-REVIEW.txt](delphi-analysis/OBSERVER-PREFLIGHT-REVIEW.txt) explains the initial map-parser false negative: `pidin` displayed the receiver as `bautoreceiver.so.1`, omitting the leading `li`. The corrected parser recognizes the shortened name. [OBSERVER-PREFLIGHT-LATEST-REVIEW.json](delphi-analysis/OBSERVER-PREFLIGHT-LATEST-REVIEW.json) records another passing standard preflight and 15 collector-review tests.

The newer [supervisor capture summary](delphi-dump/_observer_preflight_20261029_000006_d6c5d4d0/preflight-summary.json) records all seven commands completing with exit code zero, `supervisor_capture_included=true`, and `ready_for_review=true`. It did not collect fresh firmware hashes; those belong to the preceding full captures. Its UTC-stamped directory corresponds to approximately 8:00 p.m. Eastern on October 28.

Earlier review notes request a supervisor-only run; that run is now present. The next step is to review its evidence, rather than repeat acquisition solely because an older report still requests it. The capture explicitly records `deployment_authorized=false`. No live observer launch, stock-process restart, or successful cluster-video test is evidenced by these preflight results.

## Observer candidate

The current package is [delphi-observer-v1.zip](native/observer/delphi-observer-v1.zip). The [release directory](native/observer/release/README.txt) contains the shared library, decoder, manifest, and operating limitations.

The observer records existing `registerService` call entries: caller address, opaque receiver/endpoint identities, process/thread IDs, and accepted-record sequences. It tail-forwards to the original function, replacing the earlier enter/leave design. It does not inspect endpoint objects, modify discovery, request video, or record return values, completion, or duration.

Logging uses a fixed RAM mapping with 1,024 records and a nonwaiting try-lock. Contended/full logs drop metadata while retaining forwarding. Logging failures disable logging; failure to resolve the original function or verify its owning module refuses startup with exit code 125. These behaviors and limits are detailed in [native/observer/README.txt](native/observer/README.txt).

The recorded validation includes eight QNX ARM cases; multithreaded fixtures with 2,024 native calls; return/errno, exception, recursion, fork-forwarding, and ARM ABI checks; and eight decoder tests. The fixture C++ runtime is synthetic, not the vendor runtime. Those saved results were reviewed for this README update; the suites were not rerun.

The [release manifest](native/observer/release/manifest.json) still records `vehicle_validated=false`, `runtime_fingerprints_verified=false`, and `deployment_ready=false`. Its fingerprint flag predates the later successful file preflight; the later evidence does not automatically certify the release for deployment or validate real application interception.

`native/observer/smoke/` also contains local smoke-fixture sources and built artifacts. At this review it is untracked work in progress, with no completed vehicle-validation report; its presence is not evidence of a successful vehicle run.

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
|   |-- delphi_inventory.py      Selected FTP collection and optional inventory
|   |-- collect_delphi_runtime.py  Runtime component acquisition/staging
|   |-- inspect_delphi.py        Manifest verification and ELF/string triage
|   |-- decode_delphi_observer.py  Capture decoder
|   |-- test_delphi_observer.ps1  Host/QNX validation and packaging
|   `-- ...                     Discovery/HMI/transport research and tests
|-- native/
|   |-- observer/               Sources, fixtures, build outputs, and release ZIP
|   |   |-- release/            Library, decoder, manifest, and instructions
|   |   `-- smoke/              Local smoke-fixture work in progress
|   `-- loader-probe/           Isolated QNX loader experiment and emulator setup
|-- delphi-analysis/             Findings, disassembly, JSON, and string extracts
|   |-- extracted/              Extracted image artifacts
|   |-- display-hmi-java/       Java HMI analysis
|   `-- bench/                  Optional bench investigation plan
|-- delphi-dump/                 Acquired files and per-run collection reports
|   |-- delphi-inventory.txt    Original inventory transcript
|   `-- _observer_preflight_*/  Fresh preflight commands, payloads, and summaries
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

Current full preflight collects fourteen shell commands plus three fresh firmware files; supervisor-only mode collects seven commands without FTP. Each creates a fresh `delphi-dump/_observer_preflight_*` directory. It does not upload files, stop/restart processes, or launch the observer. Process environment is saved locally. The existing supervisor capture should be reviewed before deciding whether a refresh is needed.

The general inventory collector defaults to the project's `delphi-dump/`, preserves existing final files, and keeps `_collection_*` reports. The runtime collector's optional `--stage-boot-files` mode creates temporary remote RAM-disk copies; read [RUNTIME-COLLECTION.txt](scripts/RUNTIME-COLLECTION.txt) for that distinct behavior. FTP/Telnet are unencrypted and use the documented trusted direct service connection.

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

1. Review the completed supervisor capture to establish actual process ownership, respawn policy, and a verified stock restoration procedure; avoid hard-coding captured PIDs.
2. Finish and validate the isolated smoke fixture, documenting its results separately from real AndroidAuto interception.
3. Establish a controlled diagnostic launch plan and verify real application binding, constructor ordering, and timing before treating the observer as vehicle validated.
4. Collect/decode registration evidence without modifying discovery or requesting cluster video.
5. Complete receiver lifetime/input contracts, remaining MOST lifecycle analysis, and active geometry/rate/codec corroboration before evaluating secondary phone video and transport integration.

The next milestone is a verified diagnostic observation path on the actual unit. Cluster-navigation integration remains future work.
