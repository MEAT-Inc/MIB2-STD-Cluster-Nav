# MIB2 Cluster Navigation

Research and diagnostic tooling for Android Auto navigation video in the instrument cluster of a Delphi MIB2 infotainment system, with a separate initial CarPlay investigation.

**Status â€” October 29, 2026:** the phone accepted a secondary video/input pair and supplied a Google Maps H.264 stream. All 371 captured frames decode offboard at 800Ã—480. An offline MPEG-TS fixture preserves every decoded frame, but uses synthetic timing. **No video has been played through the physical cluster decoder.** The next prepared build measures native cluster geometry and phone-frame timestamps; it does not replace cluster output.

## Target system

| Item | Project context |
| --- | --- |
| Vehicle | User-reported 2019 USDM Volkswagen Golf R |
| Infotainment | Discover Media `3Q0035876B` |
| Software | MU0890 / `MST2_US_VW_P0890D` (`P` followed by zero) |
| Operating system | QNX Neutrino 6.5.0, ARM little-endian |
| Platform | TI-DRA74X-PG1.1; two Cortex-A15 processors |

Native offsets and fingerprints are specific to this build. Relocating the laptop project does not establish compatibility with another head unit or firmware train.

## Progress and evidence

| Area | Current result | Limits |
| --- | --- | --- |
| Acquisition | Initial verification records 562 matching byte-count/SHA256 comparisons; subsequent runtime and hardware captures are retained. | File hashes do not authenticate vendor origin or loaded-memory contents. |
| Native map transport | Traced `isoTX`, 188-byte MPEG-TS, PAT/PMT/PIDs, synchronous copies, queue backpressure, and single-writer ownership. | Complete MOST teardown and a safe source-substitution implementation remain open. Never add a competing `isoTX` writer. |
| HMI/control | Traced `screen-cda` application `0x55`, map activation/rate messages, geometry propagation, and SAL millisecond clock units. | Active native geometry and actual rate/timebase need measurement. |
| Observation | Real-app registration, configuration, outgoing discovery, and focus captured. The original offer has one video service; services 5/6 are audio sinks. | Offer/configuration observation alone does not prove received video. |
| Endpoint lifecycle | Native constructors/ownership and independent callback state were implemented and tested; later hardware evidence includes successful video 9/input 10 registration and negotiation. | Not a general ABI implementation for other firmware; continued lifecycle/cleanup coverage is required. |
| Secondary phone video | Latest collection records 371 frames, 371 ACKs, 2,776,803 saved bytes, no drops/errors/fallback, and verified stock process restoration. Offboard decoding shows Google Maps navigation at 800Ã—480 Baseline AVC. | No separate audio stream or physical cluster playback demonstrated. Raw capture lacks per-frame timing. |
| Offline mux | Real capture remuxed into 15,793 native-format TS packets; independent decoding produces identical RGB hashes for every frame. | Fixture uses explicit synthetic 30 fps, not measured phone timing or proof of cluster acceptance. |
| Cluster preflight | Read-only native geometry helper and bounded callback timing recorder are built; QNX synthetic tests and portable package gates are recorded passing. | Actual NavigationServer geometry read and timestamp measurement are pending hardware work. |
| Black-view investigation | A replacement explicit-cleanup workflow completed healthy phone sessions. The original forced-timer observer remains held. | Historical fault cause and recovery after a fault remain unproven; stock process restoration is not visual/session recovery. |

The latest summary is [CLUSTER-BRIDGE-PROGRESS.txt](delphi-analysis/CLUSTER-BRIDGE-PROGRESS.txt). Also see [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt), [display hardware findings](delphi-analysis/OBSERVER-DISPLAY-HARDWARE-REVIEW.txt), and the [black-view investigation](delphi-analysis/ANDROID-AUTO-BLACK-SCREEN-INVESTIGATION.txt). Historical sections can describe gates that later captures have completed.

The latest secondary-stream collection is `delphi-dump/_disconnect_observer_20261030_023947_1b83e2fa/` (about 10:39 p.m. Eastern on October 29; directory names use UTC). Its 18 artifact records and native/factory/stream assessments were independently reviewed. [video-review.json](delphi-analysis/cluster-bridge/video-review/video-review.json) records decoded source and remux pixel hashes; [frame-0180.png](delphi-analysis/cluster-bridge/video-review/frame-0180.png) shows the captured map. The offline TS fixture is evidence for byte/pixel preservation, not a deployment stream.

## Run from any checkout location

Clone or copy the complete project to any directory, including paths containing spaces. All commands below assume the repository root as the current directory. No Windows username, drive letter, Codex installation, or original checkout path is required. `.gitattributes` keeps shell scripts LF-terminated on Windows so they remain usable in Linux containers.

Prepared collection/laptop runners require **Python 3.10+** and its standard library. Use `python` below; substitute `python3` or `py -3` for the interpreter installed on your machine. Windows file publication by the general FTP collector requires hard-link support (normally local NTFS). Preserve the `scripts/` and `native/.../release/` layout when transferring a prepared package. Reports are created under the project's `delphi-dump/`; existing payloads are not replaced.

```shell
python scripts/collect_observer_preflight.py --help
python scripts/run_disconnected_observer.py --cluster-preflight
```

These display help/a plan without connecting or creating a capture. Script defaults locate the repository from `__file__`, independently of the launch directory. Explicit CLI input/output paths are relative to the current directory unless a script says otherwise. In particular, resume paths must identify the existing capture under this checkout; use the exact printed command.

Read [scripts/USAGE.txt](scripts/USAGE.txt), [preflight instructions](scripts/OBSERVER-PREFLIGHT.txt), and [cluster preflight instructions](native/cluster-bridge/README.txt) before vehicle work. Cluster preflight actively runs the established AndroidAuto observation lifecycle, but reads NavigationServer through a read-only helper without signaling/restarting it or opening/writing cluster transport. The phone must be removed before explicit cleanup. A timer checkpoint is not permission for a forced restart.

The original `scripts/run_androidauto_observer.py --run` remains disabled. Do not use an older timed observer package to recreate the black-view issue. Passive health/trace tools remain available; their logger completion does not by itself prove full phone-interval coverage or recovery.

### Optional offline analysis environment

Create a local environment using the Python installation on your machine:

```shell
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` in a POSIX shell, then install the optional dependencies:

```shell
python -m pip install -r requirements-analysis.txt
python -B -m unittest discover -s scripts -p "test_*.py" -v
python -B scripts/test_cluster_ts_mux.py
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

Windows PowerShell test wrappers locate the checkout via `$PSScriptRoot` and Python via `PATH`; optional `PYTHON` selects an interpreter executable. They do not require Codex. For a portable container build/test on any host, bind the current checkout to the container's `/src` mount:

```shell
docker run --rm --network none --mount "type=bind,source=.,target=/src" --workdir /src delphi-qnx65:qemu sh native/secondary-display/test-qemu.sh
```

Docker versions that require an absolute bind source can use the current directory expanded by the shell (`$(pwd)` on POSIX or `$PWD.Path` in PowerShell); this is a runtime value, not a fixed checkout location. Native build/test scripts run inside this container contract. `/src`, `/w`, `/tmp`, compiler paths, and QNX device/process paths such as `/proc` and `/dev/shmem` intentionally refer to container/target filesystems. They must not be rewritten as laptop-relative paths. Historical raw captures can retain original provenance paths and are not executable configuration.

Release manifests bind exact source/artifact hashes. Regenerate and validate the corresponding package after changing covered code; copying an arbitrary rebuilt library over a known-working release does not preserve its gates. ZIPs are ignored in Git and can be recreated by the corresponding `scripts/package_*.py` command. The new preflight package is built with `python scripts/package_secondary_stream.py --cluster-preflight`; it preserves the older secondary release unless explicitly rebuilt.

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
|   |-- cluster_ts_mux.py        Offline native-format TS mux
|   |-- inspect_secondary_video.py  AVC decode/remux pixel comparison
|   `-- project-python.ps1       PATH/override-based PowerShell Python helper
|-- native/
|   |-- observer/               Original observer and launch/cleanup benches
|   |-- endpoint-factory/       Native construction/ownership probe
|   |-- secondary-display/      Paired endpoints, callbacks, wire rewrite, timing
|   |-- cluster-bridge/         Read-only geometry helper and preflight release
|   |-- trace-reader/           Passive trace reader and tests
|   `-- loader-probe/           QNX loader experiments
|-- delphi-analysis/              Findings, static analysis, machine reviews
|   `-- cluster-bridge/video-review/  Source previews and offline TS fixture
|-- delphi-dump/                  Acquired firmware, manifests, and captures
|-- .tools/                      Optional local tools (ignored)
`-- .venv/                       Optional local Python environment (ignored)
```

Acquired firmware, discovery packets, video, configuration, and traces may contain private or proprietary data. Keep manifests with payloads and review evidence before sharing it. Hash consistency proves local integrity, not vendor authenticity. Native geometry/transport offsets are fixed target addresses, not portable firmware interfaces.

## Next steps

1. Collect native encoder geometry/writer state and phone callback timestamps with the prepared cluster preflight. Missing active factory-map geometry must remain a partial result, not a guessed resolution.
2. Establish the actual phone timestamp units and cluster geometry/cadence. The existing offline 30 fps fixture is deliberately synthetic.
3. Implement bounded owned-buffer IPC and one coherent source substitution through NavigationServer's existing writer, preserving activation, MOST ownership, and restoration.
4. Validate the actual cluster decoder and continue fault/recovery coverage. Do not infer working cluster maps from successful phone negotiation or offline muxing.
