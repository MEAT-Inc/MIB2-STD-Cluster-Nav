# MIB2 Cluster Navigation

Research and diagnostic tooling for Android Auto navigation video in the instrument cluster of a Delphi MIB2 infotainment system, with a separate initial CarPlay investigation.

**Status - November 3, 2026:** secondary phone map video, measured geometry/timing, and native MPEG-TS packetization are demonstrated. V6 delivered 5,646 replay packets (1,061,448 bytes) to TransportServer before queue backpressure stopped delivery. Visible recorded maps and live phone-to-cluster navigation remain unconfirmed. Replay remains held. Healthy/incomplete session comparison points to a lifecycle problem after abort-based restarts; a guarded orderly shutdown/start helper now passes QNX emulation. The next car gate is functional stock-map recovery on both screens.

## Target system

| Item | Project context |
| --- | --- |
| Vehicle | User-reported 2019 USDM Volkswagen Golf R |
| Infotainment | Discover Media `3Q0035876B` |
| Software | MU0890 / `MST2_US_VW_P0890D` (`P` followed by zero) |
| Operating system | QNX Neutrino 6.5.0, ARM little-endian |
| Platform | TI-DRA74X-PG1.1; two Cortex-A15 processors |

Native offsets and fingerprints are specific to this build. A portable laptop checkout does not establish compatibility with another head unit or firmware train.

## Progress so far

| Area | Demonstrated progress | Remaining limits |
| --- | --- | --- |
| Acquisition and analysis | Firmware/configuration collection, manifest verification, ELF/disassembly, Java HMI inspection, and successive hardware captures are retained in the repository. | Local hashes establish consistency, not vendor authenticity or loaded-memory identity. |
| Cluster control/transport | Traced HMI activation, `screen-cda`, NavigationServer encoder control, `isoTX`, MPEG-TS format, queue behavior, and single-writer ownership. | Complete live source substitution and MOST lifecycle handling remain unfinished. |
| Secondary phone video | Native video 9/input 10 endpoints, independent callback ownership, discovery negotiation, setup, focus, ACKs, and capture have worked on the unit. The latest timed capture contains 617 frames/617 ACKs, 5,485,067 bytes, and no reported drops or native/I/O/wire errors. | This is a received secondary stream, not physical cluster output. |
| Geometry and timing | Native image/buffer snapshots before and after the phone session are 800x480, padding 0, rate candidate 10. Every callback matches a captured AVC access unit. Timestamp measurements support microsecond source units. | Snapshots do not prove uninterrupted native writer activity during the phone route. Timestamp-unit evidence is empirical, not formal protocol verification. |
| Decode and packetizer | All 617 frames decode as 800x480 Baseline AVC. Recorded-timing Python remux is pixel-identical. Allocation-free native C produces byte-identical MPEG-TS to Python: 6,013,556 bytes. | Native packetization and offboard decoding do not prove acceptance by the physical cluster decoder. |
| Recorded cluster replay | V5 validated arming and stock process restoration. V6 initiated replay without waiting for the first factory video write and delivered 5,646 packets to TransportServer. | Delivery stopped after 32 zero-byte writes. Accepted bytes do not establish physical decoder acceptance or visible replay. |
| Native map session | Post-exec identity handling, qualified descriptors, retained hooks, 800x480 geometry, and replay activation have been exercised on the unit. Stock process restoration was verified after V6. | Factory maps remained at Starting map on both screens; process restoration is not functional map restoration. The blocked session dependency remains unidentified. |
| CarPlay | Initial screen-registration and H.264 references provide a separate investigation path. | Additional CarPlay display support is not established. |

The current summaries are [CLUSTER-BRIDGE-PROGRESS.txt](delphi-analysis/CLUSTER-BRIDGE-PROGRESS.txt) and [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt). They retain earlier milestones; use the newest dated section when older notes describe a completed gate as pending.

### Measured map capture and native packetization

The timed collection is `delphi-dump/_disconnect_observer_20261103_022700_3b445220/` (UTC folder name). The saved review reports 24 artifact size/hash checks, successful controller/factory/stream/timing assessments, and verified stock process restoration.

One codec record plus 617 frame records account for every captured byte. Source timestamps span 48,266,456 units over approximately 48.204 local monotonic seconds, supporting conversion from relative microseconds to native milliseconds. This replaces the earlier synthetic 30 fps fixture for recorded playback. Matching native and phone dimensions mean no scaler is required on the geometry evidence for this particular configuration.

See [video-review.json](delphi-analysis/cluster-bridge/20261103-review/video-review.json), [native-mux-review.json](delphi-analysis/cluster-bridge/20261103-review/native-mux-review.json), and the [map preview](delphi-analysis/cluster-bridge/20261103-review/frame-0180.png). The recorded-timing native/Python TS comparison has SHA256 `dd0936938df0c1829e197071354db2b61f6596664f56317c844a17e3e5d8f0e0`. Older 371-frame/synthetic-timing artifacts remain historical evidence.

### Physical replay progress

Replay uses a saved map recording with the phone unplugged to separate physical decoder/writer validation from live phone-session presentation. It uses NavigationServer's existing descriptor and never opens a competing `isoTX` writer.

- V1/V2 stopped during startup/provenance checks before replay delivery.
- V3 initialized and armed but saw no qualified native map-channel traffic.
- V4 demonstrated native channel activity; stale pre-exec start identity prevented arming and cleanup.
- V5 corrected the reproduced identity race and verified arming/restoration on the unit, but no factory source writes arrived to activate playback.
- V6 allowed the idle worker to activate the same owned replay path after explicit arming and fresh descriptor/geometry/hook checks, without waiting for a source frame. TransportServer accepted 5,646 packets before 32 zero-byte writes exhausted the bounded retry policy.

The latest reviewed collection is `delphi-dump/_cluster_replay_20261103_132444_537435f0/`; its saved review verifies 23 artifacts. The final replay error is synthesized after the retry limit, not a direct operating-system I/O error. TransportServer's default queue limit is 1 MiB, and a full queue returns success with a zero count. More than 1 MiB accepted over the run is compatible with some initial draining or reader-held buffers; it does not prove that no consumer ran or that the decoder rejected the video.

Stock NavigationServer process restoration and unchanged peer process identities were verified. The user nevertheless observed Starting map on both factory screens until a whole-unit reboot restored them. The unresolved issue is the shared map/session lifecycle; encoder geometry and an open descriptor do not establish HMI/consumer readiness. Longer zero-write retries, codec changes, competing writers, or arbitrary peer restarts are not supported by the current evidence.

**Current next step: one orderly stock navigation cycle, with the phone unplugged.** Both read-only session captures have been reviewed (120 artifacts verified). The incomplete session has a Screen buffer-registration error after Nav aborts and a non-draining MOST video path; this correlation does not yet establish the stale owner or a proven repair.

The captured factory protocol and guarded helper pass private QNX emulation: Nav app29 receives shutdown event0x163, exits cleanly, then procman app1 receives start event0x161 with uint32 app29. A stale process identity is refused. Actual NavigationServer graphics/components have not been exercised by that synthetic test.

Use [the graceful-cycle instructions](native/cluster-bridge/nav-control/README.txt) and the generated nav-graceful-cycle-laptop.zip. Start with factory maps working on both screens, phone unplugged, parked and ignition on:
```shell
python scripts/run_nav_graceful.py --run --phone-unplugged --factory-maps-working
```
Return the complete printed _nav_graceful_* folder. The script separately records clean process recovery and your observation of maps on both screens. It sends no fallback signals, performs no replay, and never retries the cycle automatically.

See [CLUSTER-MAP-SESSION-READONLY.txt](delphi-analysis/CLUSTER-MAP-SESSION-READONLY.txt), [map-session collection instructions](native/cluster-bridge/map-session/README.txt), and [CLUSTER-REPLAY-V6-ACTIVATION.txt](delphi-analysis/CLUSTER-REPLAY-V6-ACTIVATION.txt). Earlier [V5 identity findings](delphi-analysis/CLUSTER-REPLAY-V5-EXEC-HANDOFF.txt) remain useful history. No vehicle action was performed for this README update.

### Stock mobile-navigation message

The reported "Navigation is active on the mobile device" message is consistent with the stock phone-navigation handover policy. Firmware analysis ties phone-route activity to BAP function 38/state 6 and AndroidAuto property `2910005`; it does not independently capture the exact displayed text or BAP traffic. The focus handler stops native route guidance, but those methods do not themselves establish transport closure or an encoder-rate change.

This is a separate presentation/control issue for the eventual live bridge. Globally falsifying phone-navigation state or merely clearing the message does not establish video ownership. See [MOBILE-NAVIGATION-MESSAGE-REVIEW.txt](delphi-analysis/MOBILE-NAVIGATION-MESSAGE-REVIEW.txt).


## Run from any checkout location

Clone or copy the complete project to any directory, including paths containing spaces. All commands below assume the repository root as the current directory. No Windows username, drive letter, Codex installation, or original checkout path is required. `.gitattributes` keeps shell scripts LF-terminated on Windows so they remain usable in Linux containers.

Prepared collection/laptop runners require **Python 3.10+** and its standard library. Use `python` below; substitute `python3` or `py -3` for the interpreter installed on your machine. Windows file publication by the general FTP collector requires hard-link support (normally local NTFS). Preserve the `scripts/` and `native/.../release/` layout when transferring a prepared package. Reports are created under the project's `delphi-dump/`; existing payloads are not replaced.

```shell
python scripts/collect_observer_preflight.py --help
python scripts/collect_map_session.py
```

These display help/a plan without connecting or creating a capture. Script defaults locate the repository from `__file__`, independently of the launch directory. Explicit CLI input/output paths are relative to the current directory unless a script says otherwise. In particular, resume paths must identify the existing capture under this checkout; use the exact printed command.

Read [scripts/USAGE.txt](scripts/USAGE.txt), and [current map-session instructions](native/cluster-bridge/map-session/README.txt) before vehicle work. The current collector is read-only; its default invocation shows a plan without connecting. Replay runners remain held pending functional map restoration. Use the graceful-cycle package instructions for the next vehicle test; the read-only collector remains available for comparison.

### Optional offline analysis environment

Create a local environment using the Python installation on your machine:

```shell
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in a POSIX shell, then install the optional dependencies:

```shell
python -m pip install -r requirements-analysis.txt
python -B -m unittest discover -s scripts/tests -p "test_*.py" -v
python -B scripts/tests/test_cluster_ts_mux.py
```

The dependency file covers ELF/disassembly, extraction helpers, and video analysis; collectors do not need these packages. Analysis scripts accept installed packages and may also use optional local `.tools/python/` or `.tools/video-python/` directories. `inspect_delphi.py` defaults to this checkout's `delphi-dump/` and `delphi-analysis/`, accepts `--dump`, `--output`, and `--manifest`, and handles Windows or POSIX separators in saved manifest paths. It rejects paths outside the dump. It regenerates reports; without `--manifest`, it selects the first sorted collection manifest.

QNX IFS extraction additionally needs `.tools/dumpifs/dumpifs.py`; Java conversion needs the converter at `.tools/display-hmi-jxe2jar/`, its CFR JAR, and a suitable JDK on `JAVA_HOME` or `PATH`. These optional third-party tools are not vendored or automatically downloaded by the analysis scripts. Source acquisition/provenance is recorded in the relevant analysis reports. Install them only if reproducing those stages.

### Native build and emulator prerequisites

Prepared laptop releases require neither Docker nor a QNX compiler to run. Rebuilding or validating native artifacts requires Linux containers in Docker, the pinned toolchain source, and local compiler/emulator images. From the repository root:

```shell
git clone https://github.com/luka-dev/qnx65-armv7-toolchain.git .tools/qnx65-armv7-toolchain
git -C .tools/qnx65-armv7-toolchain checkout baa45224f18ae6b13c2e9c77c6663bb8181eb6a1
python scripts/build_qnx_toolchain.py
docker build -f native/loader-probe/Qemu.Dockerfile -t delphi-qnx65:qemu native/loader-probe
```

These setup commands require network access and can take substantial time. The Python builder preserves Git symlinks/executable modes and normalizes text line endings for Docker, including on Windows. `.tools/` and `.venv/` are local dependencies, excluded from Git.

For a portable native container build/test on any host, bind the current checkout to the container's `/src` mount:

```shell
docker run --rm --network none --mount "type=bind,source=.,target=/src" --workdir /src delphi-qnx65:qemu sh native/secondary-display/test-qemu.sh
```

Docker versions that require an absolute bind source can use the current directory expanded by the shell (`$(pwd)` on POSIX or `$PWD.Path` in PowerShell); this is a runtime value, not a fixed checkout location. Native build/test scripts run inside this container contract. `/src`, `/w`, `/tmp`, compiler paths, and QNX device/process paths such as `/proc` and `/dev/shmem` intentionally refer to container/target filesystems. They must not be rewritten as laptop-relative paths. Historical raw captures can retain original provenance paths and are not executable configuration.

Release manifests bind exact source/artifact hashes. Regenerate and validate the corresponding package after changing covered code; copying an arbitrary rebuilt library over a known-working release does not preserve its gates. ZIPs are ignored in Git and can be recreated by the corresponding `scripts/package_*.py` command. The current read-only collection package is generated by `python scripts/package_map_session.py`. Recorded-replay packages can be generated by `python scripts/package_cluster_replay.py`, but a successful package build does not lift the current replay hold. The preflight package remains available through `python scripts/package_secondary_stream.py --cluster-preflight` for its documented measurement scope.

Obsolete standalone prototypes, early experiment packagers, and PowerShell wrappers
have been removed. Current runners still share modules in `scripts/`; Python test
suites live in `scripts/tests/`. Native fixtures, release hashes, and acquired
evidence remain at their existing paths. Historical reports and release README
snapshots may refer to retired tools.

## Repository contents

```text
.
|-- README.md                     Overview, portability, and current progress
|-- .gitattributes              Portable source line endings and binary handling
|-- requirements-analysis.txt    Optional offline Python dependencies
|-- scripts/                     Collectors, reviews, packagers, and tests
|   |-- inspect_delphi.py        Portable manifest verification and ELF triage
|   |-- run_disconnected_observer.py  Explicit-cleanup observation/probe runner
|   |-- cluster_preflight.py     Native geometry/identity validation
|   |-- secondary_timing.py      Bounded callback timestamp assessment
|   |-- cluster_ts_mux.py        Recorded-timing TS reference mux
|   |-- collect_map_session.py  Current read-only map-session comparison
|   |-- package_map_session.py  Map-session laptop package
|   |-- run_cluster_replay.py    Recorded-map replay runner (currently held)
|   |-- package_cluster_replay.py  Replay package generation
|   |-- inspect_secondary_video.py  AVC decode/remux pixel comparison
|   `-- tests/                  Python regression suites
|-- native/
|   |-- observer/               Original observer and launch/cleanup benches
|   |-- endpoint-factory/       Native construction/ownership probe
|   |-- secondary-display/      Paired endpoints, callbacks, wire rewrite, timing
|   |-- cluster-bridge/         Geometry helper, mux/replay, map-session collection
|   `-- loader-probe/           QNX loader experiments
|-- delphi-analysis/              Findings, static analysis, machine reviews
|   `-- cluster-bridge/         Video/mux reviews and replay iteration evidence
|-- delphi-dump/                  Acquired firmware, manifests, and captures
|-- .tools/                      Optional local tools (ignored)
`-- .venv/                       Optional local Python environment (ignored)
```

Acquired firmware, discovery packets, video, configuration, and traces may contain private or proprietary data. Keep manifests with payloads and review evidence before sharing it. Hash consistency proves local integrity, not vendor authenticity. Native geometry/transport offsets are fixed target addresses, not portable firmware interfaces.

## Next steps

1. Run the prepared single orderly stock-map cycle and verify factory maps return on both screens. The captured protocol and guarded cycle pass QNX; physical component teardown remains untested.
2. If functional recovery passes, replace replay's abort-based lifecycle with the validated orderly shutdown/explicit-start path. If it fails, use the collected existing traces to identify the remaining shared-session dependency.
3. Resume controlled recorded playback only after a concrete lifecycle fix; verify sustained delivery and visible Google Maps pixels in the cluster.
4. After physical replay works, implement bounded live phone-to-native source substitution and phone-session presentation while preserving timing, backpressure, single-writer ownership, and stock restoration.

Secondary video reception and initial transport delivery are demonstrated. Visible recorded cluster maps and a working live navigation bridge remain future milestones.
