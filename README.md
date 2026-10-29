# MIB2 Cluster Navigation

Research and diagnostic tooling for investigating Android Auto and CarPlay navigation video in the instrument cluster of a Delphi MIB2 infotainment system.

**Status — October 29, 2026:** real AndroidAuto registration, video configuration, outgoing discovery, and focus calls have been observed on the unit. The discovery offer contains one video service. A secondary phone display and working cluster maps have not been demonstrated. **Live restart/observer experiments are disabled while a persistent Android Auto black-view issue is investigated.** Current work uses existing evidence and passive tracing.

Working folder: `.`.

## Target system

| Item | Project context |
| --- | --- |
| Vehicle | User-reported 2019 USDM Volkswagen Golf R |
| Infotainment | Discover Media, part number `3Q0035876B` |
| Software | MU0890 / `MST2_US_VW_P0890D` (`P` followed by zero) |
| Operating system | QNX Neutrino 6.5.0 |
| Platform | ARM little-endian, TI-DRA74X-PG1.1; two Cortex-A15 processors |

Findings and fingerprints apply to this build. Compatibility with other units or software trains is unproven.

## Current progress

| Area | Evidence available | Remaining limits |
| --- | --- | --- |
| Acquisition | Initial software/configuration verification records 562 matching byte-count/SHA256 comparisons; runtime and hardware captures are available locally. | File consistency does not establish vendor authenticity or loaded-memory identity. |
| Native cluster transport | Traced `isoTX`, 188-byte MPEG-TS, reconstructed PAT/PMT CRCs, synchronous copying, and single-writer ownership. A full queue returns zero bytes with EOK. | MOST consumer lifecycle and abnormal reader-close behavior remain incomplete. |
| HMI/control bridge | Traced `screen-cda` application `0x55`, activation/deactivation/rate messaging, geometry propagation, and SAL millisecond clock units. Java analysis converted 19,406 classes and decompiled 414 for inspection. | Active cluster geometry, measured cadence, and encoder parameter units need corroboration. |
| Registration observer | Real-app phone capture contains nine entry records, zero drops, and eight known AndroidAuto caller matches, including video registration. | Pointer identities do not establish object ownership or a usable secondary endpoint. |
| Display/discovery capture | Later hardware capture contains nine registrations and three display records, all with zero drops. Configuration, outgoing queue/discovery, and focus refer to the same video endpoint. | Offered configuration is not the phone's selected codec or a captured media stream. |
| Discovery offer | A 386-byte response advertises services 1–8; only service 1 has video configuration. Native resolution enum 1 maps to 800×480. Services 5/6 are audio sinks. | No display ID/type metadata or secondary display is present. Active negotiated geometry is not proven by the offer. |
| Secondary endpoint research | Static analysis recovers vtable/callback slots and the native construction chain. A host-only 430-byte paired video/input descriptor preserves original discovery bytes. | No second endpoints exist; router slots, lifecycle, input binding, phone acceptance, and transport integration remain unproven. |
| Display fault investigation | Android Auto black-view reports coexist with working VW menus/radio. Restart experiments are blocked in the current runner. | Root cause and recovery are unconfirmed. Process restoration does not prove visual/session recovery. |
| Passive tracing | TCP baseline and a later 180-second phone-mode logger capture completed; latest raw trace is 7,692,296 bytes with unchanged AndroidAuto PID. | Manual phone-interval coverage and display recovery remain explicitly unverified. |
| CarPlay | Initial screen-registration and H.264 references provide a separate research path. | Additional phone-display support remains unproven. |

Start with [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt), [OBSERVER-DISPLAY-HARDWARE-REVIEW.txt](delphi-analysis/OBSERVER-DISPLAY-HARDWARE-REVIEW.txt), and [ANDROID-AUTO-BLACK-SCREEN-INVESTIGATION.txt](delphi-analysis/ANDROID-AUTO-BLACK-SCREEN-INVESTIGATION.txt). These contain historical updates; newer raw captures can supersede older statements that a test is still pending.

## Hardware milestones and their limits

The investigation progressed through firmware/process preflight, synthetic host/QNX tests, isolated hardware smoke, private-path/watchdog checks, real-app registration observation, and display/discovery capture. Supervisor evidence establishes AndroidAuto's procman parent and configuration entries. The diagnostic controller demonstrated a fresh stock process after observed execution, but **that process check does not establish that the Android Auto view or USB session recovered**.

Key local collections:

| Collection under `delphi-dump/` | Result |
| --- | --- |
| `_androidauto_observer_20261029_040547_7c22f85f/` | No-phone real-app launch/restoration completed; no registration calls captured. |
| `_androidauto_observer_20261029_042655_dbdaa2d1/` | Phone session: nine registration records, zero drops, video caller seen, process restoration verified. |
| `_androidauto_observer_20261029_130447_557863fc/` | Display/discovery capture: 14 artifact checks, 35 successful actions, nine registrations and three display records; process restoration verified. |
| `_trace_tcp_20261029_201038_afbf8699/` | Thirty-second TCP trace baseline; no matching AndroidAuto startup/focus/visibility/shutdown events reported in that phone-unplugged window. |
| `_phone_trace_20261029_205440_f6999121/` | Logger did not start: background-command composition produced invalid `&;` syntax. No phone handoff occurred. |
| `_phone_trace_20261029_210643_a37ee951/` | Corrected launcher: 180,002 ms capture, 7,692,296 bytes, native error zero, unchanged stock PID. User entered normal phone view and no door opening. |

Directory timestamps use UTC. The latest listed passive capture began around 5:06 p.m. Eastern on October 29. Its summary records `capture_complete=true`, `logger_completed=true`, `phone_interval_verified=false`, and `display_recovery_verified=false`. A reported normal view in this baseline does not resolve the earlier fault. The trace needs event/timing analysis before claiming coverage of the whole phone session.

The display capture ties the same endpoint to registration, configuration, and focus. Captured configuration arguments are `1, 2, 0, 0, 160, 0, 10000` and match outgoing discovery fields. Focus arguments are `1,true`; they do not constitute an incoming focus response. Only the offer's resolution mapping is established; no frame-rate enum label is inferred.

The host-only paired descriptor adds illustrative video service 9 and input service 10 for display 1. It has not been advertised on the unit. Existing router occupancy is not established, and primary callback/decoder ownership must not be reused for a secondary stream. See the display hardware review and `control-runtime/endpoint-abi-*` artifacts for the recovered ABI evidence.

## Black-view investigation and current hold

The reported failure affects the Android Auto view while car/settings/radio remain usable. Recovery required a ten-second power-button hold; opening the driver door during an experiment appeared associated, with ignition on or the engine running. This is not established as a whole-unit crash, an expected interruption, or an ignition-off event.

Earlier watchdog/controller success verifies process identity and restoration, not rendering health, USB rebind, focus recovery, or a healthy phone session. The timed restart could interact with an active session; door-related visibility/lifecycle handling and instrumentation stalls remain hypotheses. Existing evidence does not identify the cause.

`scripts/run_androidauto_observer.py` now refuses live `--run` variants before connection or interruption, with no CLI override. Do not use an older observer bundle to recreate the fault. Offline decoding and analysis remain available. The current investigation collects display health and existing trace output without restarting AndroidAuto, injecting focus events, resetting USB, or changing trace filters.

The first passive phone-trace launch failed because a bare background `&` was combined with the shell completion suffix. The corrected launcher stores `$!` before the completion marker; the fix was checked against QNX ksh syntax and negative controls. The subsequent hardware capture demonstrates that this reader can collect trace bytes on the unit. It does not prove the black-view cause or recovery.

## Repository contents

```text
.\
|-- README.md                       Overview, current evidence, and next steps
|-- scripts/
|   |-- USAGE.txt                  General acquisition setup
|   |-- OBSERVER-PREFLIGHT.txt      Read-only firmware/process checks
|   |-- DISPLAY-HEALTH-DIAGNOSTICS.txt  Health/trace procedures and history
|   |-- delphi_inventory.py         FTP collector and optional inventory
|   |-- collect_delphi_runtime.py   Runtime acquisition/optional RAM staging
|   |-- run_androidauto_observer.py  Historical live observer; current hold enforced
|   |-- decode_androidauto_display.py  Display/discovery decoder
|   |-- review_androidauto_display.py  Local capture verification
|   |-- collect_display_health.py   Read-only process/display/log inventory
|   |-- collect_trace_snapshot.py   Historical DTS snapshot attempt
|   |-- collect_trace_tcp.py        Bounded laptop TCP trace baseline
|   |-- run_phone_trace.py          Passive on-unit logger and USB-handoff workflow
|   `-- ...                        Analysis, packaging, and offline test utilities
|-- native/
|   |-- observer/                  Candidate, fixtures, and diagnostic launch stages
|   |   |-- release/               Original observer library/decoder/manifest
|   |   |-- smoke/, path-test/     Isolated hardware stages
|   |   |-- transaction/, managed-bench/  QNX launch/restoration benches
|   |   `-- launch/                Real-app/display observer releases (live hold)
|   |-- trace-reader/              Bounded passive logger, tests, and release
|   `-- loader-probe/              Isolated QNX loader experiment
|-- delphi-analysis/
|   |-- control-runtime/           Hardware reviews, ABI/discovery/trace evidence
|   |-- extracted/                 Image extraction artifacts
|   |-- display-hmi-java/          Java HMI analysis
|   `-- bench/                     Optional bench investigation plan
|-- delphi-dump/                   Acquisition, observer, health, and trace captures
|   `-- delphi-inventory.txt       Original inventory transcript
`-- .tools/                       Local dependencies (Git-ignored)
```

The working tree contains substantial staged and unstaged research/tooling changes. This README update does not commit or publish them; availability in a fresh checkout may differ. Earlier preflight payload directories and the original observer ZIP are absent locally. Preserve acquisition manifests with payloads. Raw discovery contains unit identifiers; configuration, environments, and traces may contain private data.

## Using the tools

```powershell
Set-Location -LiteralPath '.'
```

Read [scripts/USAGE.txt](scripts/USAGE.txt), [OBSERVER-PREFLIGHT.txt](scripts/OBSERVER-PREFLIGHT.txt), and [DISPLAY-HEALTH-DIAGNOSTICS.txt](scripts/DISPLAY-HEALTH-DIAGNOSTICS.txt) for scope and prerequisites. General collectors use Python 3.10+ and the standard library; research/native builds require their documented dependencies. Substitute `python` for `py -3` if needed.

Inspect passive workflow plans without connecting:

```powershell
py -3 .\scripts\collect_display_health.py
py -3 .\scripts\run_phone_trace.py
```

The passive phone-trace runner's opt-in mode stages a bounded RAM-only loopback reader and leaves AndroidAuto running. Its documented handoff starts on Ethernet, waits for `LOGGER READY`, swaps to the phone with the door closed, waits 210 seconds, then reconnects Ethernet for collection. The reader stops at 180 seconds or 16 MiB. A logger-complete result does not establish manual handoff coverage. Review the existing successful baseline before deciding on another capture.

FTP access to DTS named memory objects was rejected on this unit; older snapshot instructions are historical, not a reason to repeat that failed acquisition. TraceServer's enabled text backend on TCP 15361 provides the current trace source. Baseline collectors avoid replacing an existing trace consumer and do not change filters or clear buffers. FTP/Telnet use the documented trusted direct connection and are unencrypted.

For local display-capture review:

```powershell
py -3 .\scripts\review_androidauto_display.py .\delphi-dump\_androidauto_observer_20261029_130447_557863fc
```

Python unit-test discovery remains available with `py -3 -m unittest discover -s .\scripts -p "test_*.py" -v`; native and separately named research tests have their own runners. Saved reports describe wire/ABI, QNX fixture, runner, and shell-completion validation. This README review verifies saved evidence and does not rerun native suites or connect to the vehicle.

## Next steps

1. Correlate the completed passive trace with USB, AndroidAuto/AppConnect, visibility/focus, graphics, and user-observed timing. Establish actual phone-interval coverage rather than inferring it from logger duration.
2. Diagnose the persistent black view and define explicit visual/session recovery criteria. Keep disruptive observer/restart experiments held until the fault is understood and recovery is demonstrated.
3. Continue offboard endpoint factory/lifecycle work: independent video/input objects, callbacks, decoder/focus/ack state, cleanup, disconnect, and backpressure handling. Verify router slots before emitting new descriptors.
4. Only after those gates, evaluate phone acceptance and a secondary stream, then geometry/codec and MPEG-TS/MOST compatibility with exclusive writer ownership/restoration.

Registration and outgoing-discovery observation are demonstrated. Reliable visual recovery and a working cluster-navigation integration remain open.
