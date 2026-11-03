# MIB2 Cluster Navigation

Research and diagnostic tooling for Android Auto navigation video in the instrument cluster of a Delphi MIB2 infotainment system, with a separate initial CarPlay investigation.

**Status - November 3, 2026:** secondary Android Auto map video, native cluster geometry, recorded frame timing, and native MPEG-TS packetization are demonstrated. The first physical cluster replay remains incomplete: the latest vehicle run reached the native map channel but stopped before replay packets were sent. The V5 launcher corrects a reproduced post-exec identity race and is prepared for vehicle validation. **Visible Google Maps playback in the cluster and live phone-to-cluster navigation are not yet demonstrated.**

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
| Recorded cluster replay | A supervised NavigationServer launcher and app-only open/write/close hooks preserve native transport ownership. V4 observed two qualified opens, 2,540 tracked writes, matching encoder FD/800x480 geometry, retained hooks, and a live heartbeat. | V4 arming was refused, replay packets remained zero, and cleanup was refused. No decoder result can be inferred. |
| Latest launcher | V5 waits for a nonce-bound module report confirming initialization before recording the post-exec process identity. The failure was reproduced under QNX; the candidate has recorded emulator/workflow/package validation. | V5 has not yet been demonstrated on the vehicle. |
| CarPlay | Initial screen-registration and H.264 references provide a separate investigation path. | Additional CarPlay display support is not established. |

The current summaries are [CLUSTER-BRIDGE-PROGRESS.txt](delphi-analysis/CLUSTER-BRIDGE-PROGRESS.txt) and [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt). They retain earlier milestones; use the newest dated section when older notes describe a completed gate as pending.

### Measured map capture and native packetization

The timed collection is `delphi-dump/_disconnect_observer_20261103_022700_3b445220/` (UTC folder name). The saved review reports 24 artifact size/hash checks, successful controller/factory/stream/timing assessments, and verified stock process restoration.

One codec record plus 617 frame records account for every captured byte. Source timestamps span 48,266,456 units over approximately 48.204 local monotonic seconds, supporting conversion from relative microseconds to native milliseconds. This replaces the earlier synthetic 30 fps fixture for recorded playback. Matching native and phone dimensions mean no scaler is required on the geometry evidence for this particular configuration.

See [video-review.json](delphi-analysis/cluster-bridge/20261103-review/video-review.json), [native-mux-review.json](delphi-analysis/cluster-bridge/20261103-review/native-mux-review.json), and the [map preview](delphi-analysis/cluster-bridge/20261103-review/frame-0180.png). The recorded-timing native/Python TS comparison has SHA256 `dd0936938df0c1829e197071354db2b61f6596664f56317c844a17e3e5d8f0e0`. Older 371-frame/synthetic-timing artifacts remain historical evidence.

### Physical replay progress

Replay intentionally uses a saved map recording with the phone unplugged. It separates cluster decoder/writer validation from live phone-session policy. The shim uses NavigationServer's existing descriptor; it does not open a competing `isoTX` writer. Playback requires an explicit operator arm after the factory map appears in the cluster.

The vehicle iterations have narrowed the remaining startup issue:

- V1 did not complete startup/restoration; V2 stopped at a libc provenance check before installing hooks or sending replay packets.
- V3 initialized and armed, but observed no qualified native map-channel traffic; zero replay packets were sent.
- V4 restored canonical executable/stdio behavior and demonstrated native channel activity. Arming and cleanup rejected a stale process-start identity despite the observed PID remaining alive.
- QNX reproduction showed that a wrapper can publish the final PID/canonical pathname before `exec` changes the start identity. V5 waits for the initialized module's nonce-bound acknowledgement before capturing that identity, while retaining exact PID/start/parent/image checks and better refusal logs.

The latest reviewed V4 collection is `delphi-dump/_cluster_replay_20261103_123923_179465c3/`. Its channel telemetry is progress toward delivery, not evidence of replay or live maps. Read [CLUSTER-REPLAY-V5-EXEC-HANDOFF.txt](delphi-analysis/CLUSTER-REPLAY-V5-EXEC-HANDOFF.txt) and the [replay instructions](native/cluster-bridge/replay/README.txt) for the current candidate and the required reset of the prior refused-cleanup state before another vehicle attempt. No further vehicle action was performed for this documentation update.

### Stock mobile-navigation message

The reported "Navigation is active on the mobile device" message is consistent with the stock phone-navigation handover policy. Firmware analysis ties phone-route activity to BAP function 38/state 6 and AndroidAuto property `2910005`; it does not independently capture the exact displayed text or BAP traffic. The focus handler stops native route guidance, but those methods do not themselves establish transport closure or an encoder-rate change.

This is a separate presentation/control issue for the eventual live bridge. Globally falsifying phone-navigation state or merely clearing the message does not establish video ownership. See [MOBILE-NAVIGATION-MESSAGE-REVIEW.txt](delphi-analysis/MOBILE-NAVIGATION-MESSAGE-REVIEW.txt).


## Script console output

Python tools, PowerShell launchers, and container shell scripts share a simple console style: an interactive run clears the screen, then shows the script name, version, supplied arguments, and use case. Timestamped steps and a final completion/error line separate each phase. Nested scripts keep the parent output visible. Polling/transfer progress is throttled to avoid flooding the screen.

Colors distinguish steps (blue), information (cyan), success (green), warnings (yellow), errors (red), and operator prompts (magenta). Set `NO_COLOR=1` to disable colors. Redirected output has no colors or screen-clearing codes; banners and progress go to stderr so stdout can still carry JSON/data. Existing diagnostic transcripts and saved report formats are preserved.

Shared helpers are `scripts/project_console.py`, `scripts/project-console.ps1`, and `scripts/project-console.sh`. New Python commands should use this pattern:

```python
"""Describe when to use this script."""
from project_console import console_session, status


def main():
    status('Checking input files.')
    # Perform work and report meaningful phases with status(...).
    return 0


if __name__ == '__main__':
    with console_session(__file__, __doc__, version='1.0'):
        raise SystemExit(main())
```

Use `progress(...)` for repeated waits, `prompt(...)` for operator questions, and `status(message, 'WARN')` or `'ERROR'` for problems. The initial shared script version is `1.0`; individual scripts can supply their own version. Portable package definitions include the Python helper. Previously generated archives and release snapshots acquire the changes when rebuilt through their normal validation gates.

## Run from any checkout location

Clone or copy the complete project to any directory, including paths containing spaces. All commands below assume the repository root as the current directory. No Windows username, drive letter, Codex installation, or original checkout path is required. `.gitattributes` keeps shell scripts LF-terminated on Windows so they remain usable in Linux containers.

Prepared collection/laptop runners require **Python 3.10+** and its standard library. Use `python` below; substitute `python3` or `py -3` for the interpreter installed on your machine. Windows file publication by the general FTP collector requires hard-link support (normally local NTFS). Preserve the `scripts/` and `native/.../release/` layout when transferring a prepared package. Reports are created under the project's `delphi-dump/`; existing payloads are not replaced.

```shell
python scripts/collect_observer_preflight.py --help
python scripts/run_cluster_replay.py
```

These display help/a plan without connecting or creating a capture. Script defaults locate the repository from `__file__`, independently of the launch directory. Explicit CLI input/output paths are relative to the current directory unless a script says otherwise. In particular, resume paths must identify the existing capture under this checkout; use the exact printed command.

Read [scripts/USAGE.txt](scripts/USAGE.txt), [preflight instructions](scripts/OBSERVER-PREFLIGHT.txt), and [current replay instructions](native/cluster-bridge/replay/README.txt) before vehicle work. The current replay experiment restarts NavigationServer under its supervisor and requires the phone to remain unplugged. It uses recorded video and explicit arming/cleanup. Default runner invocation shows a plan without connecting. Follow the current bundle instructions rather than an earlier replay release.

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

Release manifests bind exact source/artifact hashes. Regenerate and validate the corresponding package after changing covered code; copying an arbitrary rebuilt library over a known-working release does not preserve its gates. ZIPs are ignored in Git and can be recreated by the corresponding `scripts/package_*.py` command. The current recorded-replay package is generated by `python scripts/package_cluster_replay.py`. The preflight package remains available through `python scripts/package_secondary_stream.py --cluster-preflight` for its documented measurement scope.

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
|   |-- run_cluster_replay.py    Supervised recorded-map replay runner
|   |-- package_cluster_replay.py  Replay package generation
|   |-- inspect_secondary_video.py  AVC decode/remux pixel comparison
|   `-- project-python.ps1       PATH/override-based PowerShell Python helper
|-- native/
|   |-- observer/               Original observer and launch/cleanup benches
|   |-- endpoint-factory/       Native construction/ownership probe
|   |-- secondary-display/      Paired endpoints, callbacks, wire rewrite, timing
|   |-- cluster-bridge/         Geometry helper, native mux, replay hooks/launcher
|   `-- loader-probe/           QNX loader experiments
|-- delphi-analysis/              Findings, static analysis, machine reviews
|   `-- cluster-bridge/         Video/mux reviews and replay iteration evidence
|-- delphi-dump/                  Acquired firmware, manifests, and captures
|-- .tools/                      Optional local tools (ignored)
`-- .venv/                       Optional local Python environment (ignored)
```

Acquired firmware, discovery packets, video, configuration, and traces may contain private or proprietary data. Keep manifests with payloads and review evidence before sharing it. Hash consistency proves local integrity, not vendor authenticity. Native geometry/transport offsets are fixed target addresses, not portable firmware interfaces.

## Next steps

1. Validate the V5 post-exec identity handoff on the vehicle, confirm native channel readiness, and deliver the recorded stream to the physical cluster decoder.
2. Confirm visible recorded Google Maps playback and verified stock restoration. A recorded-map result must be reported separately from live/current navigation.
3. After physical replay works, implement bounded live phone-to-native IPC/source substitution while preserving timing, backpressure, single-writer ownership, and cleanup.
4. Address phone-session cluster presentation only while verified video is owned and healthy, preserving truthful phone-navigation state and restoring stock behavior on failure.

The current milestone is physical recorded-map delivery. A working live phone-to-cluster navigation bridge remains future work.
