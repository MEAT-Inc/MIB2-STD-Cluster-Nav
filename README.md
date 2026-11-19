# MIB2 Cluster Navigation

Development and reverse engineering toward live Android Auto navigation in the instrument cluster of a Delphi MIB2 infotainment system.

**Status - November 19, 2026:** live Google Maps are user-confirmed and updating in the physical cluster. Recorded playback, owned live-frame transfer, native MPEG-TS delivery, and explicit cleanup back to working factory maps are demonstrated. Current work refines latency/layout, makes disconnect return consistent, and prepares repeatable startup/session handling. The current package remains a RAM-based single-session trial; persistent installation and automatic reconnect are not implemented.

## Target system

| Item | Project context |
| --- | --- |
| Vehicle | User-reported 2019 USDM Volkswagen Golf R |
| Infotainment | Discover Media `3Q0035876B` |
| Software | MU0890 / `MST2_US_VW_P0890D` (`P` followed by zero) |
| Operating system | QNX Neutrino 6.5.0, ARM little-endian |
| Platform | TI-DRA74X-PG1.1; two Cortex-A15 processors |

Native offsets, object layouts, and fingerprints are specific to this build. Laptop portability does not establish compatibility with another firmware train or head unit.

## Progress so far

| Stage | Demonstrated result | Remaining limits |
| --- | --- | --- |
| Acquisition and analysis | Firmware/configuration manifests, ELF/disassembly, Java HMI inspection, and hardware captures establish receiver, focus, map-control, and transport paths. | Hash consistency does not establish vendor authenticity or loaded-memory identity. |
| Secondary phone display | Video 9/input 10 registration, discovery negotiation, independent callback ownership, phone video reception, and ACK handling work on the unit. | The implementation is firmware-specific. |
| Geometry and timing | Phone and native map geometry match at 800x480. Callback measurements support microsecond timestamps and measured-time packetization. | This is evidence for the captured configuration, not all phones or firmware. |
| Packetizer and recorded replay | Native/Python MPEG-TS comparisons and decoded pixels agree. The November 4 v9 trial confirmed continuous recorded Google Maps playback and restored factory navigation. | Recorded playback is a separate milestone from live guidance. |
| Live-frame ownership | The bounded owned queue copies phone frames without retaining borrowed buffers. The input-only hardware review verified byte-identical copies and no queue drops. | Long-running overflow, resynchronization, and reconnect behavior need broader coverage. |
| Visible live maps | The November 18 v7 trial confirmed visible, updating maps: 436 source frames emitted, three bootstrap frames, 16,596 delivered packets, and no reported drops/transport errors. | That first success did not verify cluster factory-map return. Later trials address return handling. |
| Latency | The startup schedule retains a one-second initialization buffer, then catches up toward 250 ms steady buffering. Offboard v12 review preserves all 539 original frames/pixels and timestamp order without reencoding. | Configured buffering is not a measured end-to-end display-latency guarantee. |
| Extended live trial | November 19 v15 emitted 2,703 source frames and 129,465 packets / 24,339,420 bytes. Diagnostic recording stopped at its bound while forwarding continued. Live maps were confirmed. | Single-session operation still requires end-of-test cleanup; automatic reconnect is not implemented. |
| Factory return | Explicit cleanup in the latest trial verified stock process restoration and working radio/cluster maps. A prior November 18 trial also recorded automatic return verified. | Latest v15 recorded automatic return unverified, so disconnect return is not consistently complete. |
| Startup/deployment | Read-only startup preflight captured the boot script, process-manager configuration, mounts, paths, and backing storage. | Persistent boot integration, repeatable session reset, installer, rollback, and uninstall remain future work. |

CarPlay has initial screen-registration/H.264 analysis, but additional CarPlay display support is not established. Current implementation work centers on Android Auto.

## Hardware milestones and current evidence

### From saved playback to visible live navigation

The [recorded replay review](delphi-analysis/cluster-bridge/20261104-replay-v9-success/review.json) confirms continuous physical cluster playback and factory-map restoration. The [live-input review](delphi-analysis/cluster-bridge/20261110-live-input-v2-success/review.json) then verifies 354 owned frame copies, with approximately 2 ms median and 12 ms maximum source-to-copy delay in that capture.

Early live output reached the native transport and decoded correctly offboard but was not visible. The [v7 live-success review](delphi-analysis/cluster-bridge/20261118-v7-live-success/review.json), from `_disconnect_observer_20261118_140131_df3a9762`, records the first user-confirmed visible and updating live maps. That result supersedes the earlier README's unresolved-live-visibility status.

Native transport ownership, timestamp continuity, decoder startup/bootstrap, and temporary phone-route presentation handling are part of the live bridge. It uses the native descriptor rather than opening a second cluster writer. The original phone video remains un-reencoded in the current live path.

### Latency, layout, and extended forwarding

The [v12 startup review](delphi-analysis/cluster-bridge/20261118-v12-latency-review/startup-review.json) verifies original frame order, pixels, and scheduled timestamps while reducing the steady buffer to 250 ms after startup/catchup. The initial delay is still 1,000 ms, and the catchup schedule reaches the reduced delay after about four seconds in that offboard review.

Current v15 layout uses the full 800x480 map, density 140, 120-pixel horizontal UI insets, a 72-pixel content bottom inset, and a separate 64-pixel stable UI bottom inset. Turn-card positioning is phone-controlled and remains a visual refinement task; the inset values do not guarantee a particular card location.

The latest collection is `delphi-dump/_disconnect_observer_20261119_132442_fb46ba95/`. It records 2,705 input frames, 2,703 emitted source frames, 22,238,329 total input bytes, and 24,339,420 output transport bytes. No sink/timeline error or reported queue drop is recorded. These total-forwarding counters are distinct from the shorter diagnostic H.264 prefix: forwarding continues after recording limits are reached.

The same summary records `live_maps_seen=true`, verified cleanup/restoration, and working factory maps in both selected locations, but `automatic_factory_return_verified=false`. Factory return recorded an internal error value of 71; its cause needs review. Explicit cleanup succeeded. A prior collection, `_disconnect_observer_20261118_213635_2455dc3c`, records automatic return verified, so the latest result should not be generalized into either universal success or universal failure.

### Deployment readiness

The startup collection is `delphi-dump/_deployment_preflight_20261119_131638_794286b0/deployment-preflight/`. It contains the actual startup script, process-manager arguments/configuration, mount/path information, and storage checks. The [deployment notes](native/cluster-bridge/deployment/deployment-readiness.txt) identify `procman` launching `runHMI.sh`; the presence of `/extbin/.boot` alone does not prove a boot-hook contract.

The extended trial removes the active video-duration limit when explicitly requested, but remains one phone session with explicit cleanup. The attempted/done/queue state is currently one-shot. Adding that trial to a boot script would not provide a repeatable attach/detach lifecycle. No persistent installation was performed by these packages.

## Repository contents

```text
.
|-- README.md                     Current overview and milestones
|-- requirements-analysis.txt    Optional offline Python dependencies
|-- scripts/                     Collection, packaging, review, and trial tools
|   |-- run_disconnected_observer.py  Current live-input/live-cluster entry point
|   |-- live_cluster_bridge.py   Live output orchestration
|   |-- live_run_options.py      Bounded/extended trial options
|   |-- collect_cluster_deployment.py  Read-only startup preflight
|   |-- run_cluster_replay.py    Recorded playback experiment
|   |-- run_nav_graceful.py      Guarded native lifecycle/recovery tools
|   |-- finish_live_session.py   Existing session cleanup workflow
|   `-- tests/                  Existing Python regression suites
|-- native/
|   |-- observer/               Receiver observation and managed launch
|   |-- endpoint-factory/       Native construction/ownership work
|   |-- secondary-display/      Paired endpoints and phone callbacks
|   |-- cluster-bridge/
|   |   |-- replay/             Recorded playback hooks and launcher
|   |   |-- nav-control/        Native lifecycle and captured-state recovery
|   |   |-- live/               Owned frame queue, startup scheduling, and consumer
|   |   |-- live-output/        Live transport/presentation release
|   |   |-- layout-margin/      Layout/inset work
|   |   `-- deployment/         Startup/deployment readiness notes
|   `-- loader-probe/           QNX loader experiments
|-- delphi-analysis/              Findings and dated machine reviews
|   `-- cluster-bridge/         Recorded, input, live-display, and latency evidence
|-- delphi-dump/                  Acquired firmware and per-run captures
|-- .tools/                      Optional local dependencies (ignored)
`-- .venv/                       Optional local Python environment (ignored)
```

[CLUSTER-BRIDGE-PROGRESS.txt](delphi-analysis/CLUSTER-BRIDGE-PROGRESS.txt) and [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt) preserve earlier investigation stages. Their leading summaries stop at November 4; use the later dated reviews and returned captures for current progress. Historical one-off instructions are not the current vehicle procedure.


## Portable setup and use

Clone or copy the complete project to any directory. Commands below run from the repository root; no machine-specific drive, username, or Codex installation is required. Defaults locate project assets relative to the scripts. Explicit relative CLI paths normally resolve from the current working directory. Keep the `scripts/` and matching `native/.../release/` structure together when extracting laptop packages.

Prepared laptop runners require Python 3.10+ and the standard library. Use `python`, `python3`, or `py -3` according to your installation. Inspect the current trial plan without connecting:

```shell
python scripts/run_disconnected_observer.py --live-cluster --no-live-timeout
```

The [live-trial instructions](native/cluster-bridge/live-output/release/README.txt) describe the matching package, firmware/asset checks, vehicle workflow, and explicit phone-disconnected cleanup. The runner stages RAM artifacts and controls the observed processes; it is an experimental trial, not an installer or unattended deployment. Use the same package and saved profile for a pending-session resume.

Optional offline dependencies can be installed in a local environment:

```shell
python -m venv .venv
```

Activate `.venv/Scripts/Activate.ps1` in PowerShell or `source .venv/bin/activate` in a POSIX shell, then:

```shell
python -m pip install -r requirements-analysis.txt
```

Native rebuilding uses the pinned QNX toolchain and Docker emulator environment described by the relevant native build scripts and historical setup notes. Container mount paths such as `/src` and QNX paths such as `/proc` and `/dev/shmem` intentionally refer to their own filesystems. They are not fixed host checkout paths. `.gitattributes` keeps shell source line endings usable in Linux containers.

Release manifests bind exact payload/source hashes. Rebuild the matching package after changing covered files; do not combine arbitrary binaries and scripts from different releases. ZIPs and local dependency directories are ignored by Git. Captures may include private or proprietary material; keep manifests with payloads and review artifacts before sharing.

## Next steps

1. Make automatic return to the factory map reliable on physical phone disconnect, including presentation-policy release and native-stream handoff; review the latest return error before claiming completion.
2. Refine and verify map/turn-card layout and measure end-to-end latency beyond the configured buffer values.
3. Implement repeatable attach/detach/session reset and startup supervision, using the captured launch chain instead of assuming a boot hook.
4. Package version-checked persistent deployment with backups, rollback, and uninstall only after repeated sessions and factory restoration are validated.

Visible live navigation is demonstrated. Reliable automatic return, repeated-session operation, and persistent installation remain the main unfinished milestones.
