# MIB2 Cluster Navigation

Development and reverse engineering toward live Android Auto navigation in the instrument cluster of a Delphi MIB2 infotainment system.

**Status - November 18, 2026:** continuous recorded Google Maps playback in the physical cluster is confirmed, with factory maps restored afterward. The live bridge receives phone frames, carries them through an owned queue, and writes them through the native cluster transport. The latest accepted output decodes correctly offboard, but visible live maps are **not yet confirmed**. Current work focuses on live presentation and decoder compatibility.

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

| Stage | Demonstrated result | Current limit |
| --- | --- | --- |
| Acquisition and analysis | Firmware/configuration collection, manifests, ELF/disassembly, Java HMI inspection, and hardware captures establish the receiver and map-control paths. | File hashes establish consistency, not vendor authenticity or loaded-memory identity. |
| Secondary phone display | Video 9/input 10 registration, discovery negotiation, independent callbacks, phone video reception, and ACK handling have worked on the unit. | These endpoints alone do not establish physical cluster presentation. |
| Geometry and timing | Phone video and native image/buffer geometry are 800x480. Callback timestamps support microsecond units; recorded playback uses measured timing rather than guessed frame rate. | Evidence is specific to the captured configuration. |
| Native packetizer | Native C and Python produce matching recorded-timing MPEG-TS; independent decoding verifies source/remux pixel agreement. | A decodable stream is not by itself proof of physical decoder presentation. |
| Factory-map lifecycle | Guarded lifecycle/recovery work restored factory navigation, confirmed by the user on radio and cluster when selected in turn. | The location toggle selects one display at a time; simultaneous factory maps are not a requirement. |
| Physical recorded replay | The November 4 v9 trial confirmed continuous recorded Google Maps playback in the cluster, 31,669 packets, and verified process/factory-map restoration. | This is saved-video playback, not live guidance. |
| Owned live input | The November 10 input trial verified 354 copied access units byte-for-byte, with no queue drops; median source-to-copy delay was about 2 ms and maximum about 12 ms. Native geometry remained active during sampled phone-video intervals. | This input-only trial did not connect the queue to cluster transport. |
| Combined live output | The November 18 v6 trial delivered 405 live frames in 11,083 transport packets, with no reported frame drops, sink error, or timeline error. Factory maps were restored. | The operator reported no visible live maps. |
| Presentation and decoder analysis | Live route-focus handling, accepted-output capture, and stream comparisons are implemented. The latest accepted transport decodes to 405 frames pixel-identical to the phone capture. | The remaining on-unit visibility/decoder cause is unresolved. |

CarPlay has initial screen-registration/H.264 analysis, but additional CarPlay display support is not established. Current implementation work centers on Android Auto.

## Confirmed hardware milestones

### Recorded maps reached the physical cluster

The saved review for `delphi-dump/_cluster_replay_20261104_194219_44022e92/` records 37 verified artifacts, continuous recorded-map playback confirmed by the user, and restored factory navigation. Peer process identities remained unchanged. The successful recording used 259 reencoded 800x480 Baseline frames with a keyframe and repeated headers every five frames, preserving recorded timestamps and color metadata.

This supersedes the earlier replay iterations that stopped at startup, identity checks, absent source writes, or transport backpressure. The earlier results remain useful history, but physical recorded playback is now a completed milestone. See [recorded replay review](delphi-analysis/cluster-bridge/20261104-replay-v9-success/review.json) and [replay documentation](native/cluster-bridge/replay/README.txt).

The separate [factory-map recovery review](delphi-analysis/cluster-bridge/20261104-recovery-success-review/review.json) records successful native recovery and the user's confirmation of map rendering in each selected location. Its follow-up corrects an earlier visual-answer parsing false negative; that successful recovery does not need to be repeated solely because an older summary reported an incomplete result.

### Live input and transport now work together

The [live-input review](delphi-analysis/cluster-bridge/20261110-live-input-v2-success/review.json) verifies an owned copy of borrowed phone frames through the bounded queue. Capture/consumer work is separated from phone callback ownership, with overflow handling designed to avoid blocking phone ACKs.

The latest combined collection is `delphi-dump/_disconnect_observer_20261118_125442_314326f0/`. It records:

- 405 live frames and 1,788,313 input bytes, with zero reported drops.
- 11,083 rewritten MPEG-TS packets / 2,083,604 accepted output bytes through the native descriptor.
- No sink or timeline error; stock process and factory maps restored after cleanup.
- `live_maps_seen=false`: the user did not confirm visible live navigation.

The [v6 decoder comparison](delphi-analysis/cluster-bridge/20261118-v6-decoder-review/review.json) reports that accepted transport output decodes to the same 405 frame pixels as the phone capture. This narrows the remaining issue beyond basic acquisition or packet-byte corruption, but it does not identify why the physical cluster did not show the live stream.

### Presentation and decoder work remains

The [v5 presentation review](delphi-analysis/cluster-bridge/20261117-v5-presentation-review/review.json) found a mismatch between native and HMI focus enum values, plus a completed-sink polling error. V6 corrected those paths and added a bounded phone-route presentation prototype. That prototype temporarily defers the relevant route handoff while verified live output is healthy, then releases the original notification. It is not a finished production arbitration policy.

The latest stream comparison also distinguishes the phone's single initial IDR/header set from the proven recording's repeated keyframes/headers and from native encoder parameters. These are investigation leads, not an established decoder root cause. The reported stock mobile-navigation message and BAP/focus policy are documented in [MOBILE-NAVIGATION-MESSAGE-REVIEW.txt](delphi-analysis/MOBILE-NAVIGATION-MESSAGE-REVIEW.txt).

## Repository contents

```text
.
|-- README.md                     Current overview and milestones
|-- requirements-analysis.txt    Optional offline Python dependencies
|-- scripts/                     Collection, packaging, review, and trial tools
|   |-- run_disconnected_observer.py  Current input/live-cluster trial entry point
|   |-- live_cluster_bridge.py   Live output orchestration
|   |-- run_cluster_replay.py    Recorded playback experiment
|   |-- run_nav_graceful.py      Guarded native lifecycle/recovery tools
|   |-- inspect_secondary_video.py  Video decode/remux review
|   |-- finish_live_session.py   Existing live-session cleanup workflow
|   `-- tests/                  Existing Python regression suites
|-- native/
|   |-- observer/               Receiver observation and managed launch components
|   |-- endpoint-factory/       Native construction/ownership work
|   |-- secondary-display/      Paired endpoints and phone-stream callbacks
|   |-- cluster-bridge/
|   |   |-- replay/             Recorded playback hooks and launcher
|   |   |-- nav-control/        Native lifecycle and captured-state recovery
|   |   |-- live/               Owned frame queue and consumer components
|   |   |-- keyframe-probe/     Input capture/review release
|   |   `-- live-output/        Combined live transport/presentation release
|   `-- loader-probe/           QNX loader experiments
|-- delphi-analysis/              Findings and derived reviews
|   `-- cluster-bridge/         Dated capture, replay, input, and live-output reviews
|-- delphi-dump/                  Acquired firmware and per-run evidence
|-- .tools/                      Optional local dependencies (ignored)
`-- .venv/                       Optional local Python environment (ignored)
```

[CLUSTER-BRIDGE-PROGRESS.txt](delphi-analysis/CLUSTER-BRIDGE-PROGRESS.txt) and [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt) preserve the earlier investigation. Some summary sections stop at November 4; the dated November 10–18 machine reviews and returned captures document later progress. Historical instructions and one-off recovery bundles should not be treated as current actions.

## Portable setup and use

Clone or copy the complete project to any directory. Commands below run from the repository root; no machine-specific drive, username, or Codex installation is required. Defaults locate project assets relative to the scripts. Explicit relative CLI paths normally resolve from the current working directory. Keep the `scripts/` and matching `native/.../release/` structure together when extracting laptop packages.

Prepared laptop runners require Python 3.10+ and the standard library. Use `python`, `python3`, or `py -3` according to your installation. Inspect the current trial plan without connecting:

```shell
python scripts/run_disconnected_observer.py --live-cluster
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

1. Resolve the gap between correctly decoded accepted live output and the absence of visible cluster maps, using the latest presentation, decoder-parameter, keyframe/header, and handoff evidence.
2. Demonstrate visible, sustained live map updates on the physical cluster together with verified factory-map restoration.
3. Complete longer-session coverage for overflow, resynchronization, disconnects, transport backpressure, native ownership, and presentation-policy release.
4. Consolidate validated behavior into a repeatable package once live display is proven. Recorded playback, live transport delivery, and visible live guidance remain distinct milestones.
