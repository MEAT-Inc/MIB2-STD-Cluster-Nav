# MIB2 Cluster Navigation

Research and diagnostic tooling for investigating Android Auto and CarPlay navigation video in the instrument cluster of a Delphi MIB2 infotainment system.

**Status — October 29, 2026:** real AndroidAuto registration/configuration/discovery observation is demonstrated. A replacement controller completed a healthy phone trial and waited for explicit cleanup after phone removal. A paired-endpoint factory probe is built and offboard tested; real firmware constructor execution is still pending. The original forced-timer restart runner remains disabled. Secondary video and cluster maps are not demonstrated, and recovery from the earlier black-view fault remains unproven.

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
| Endpoint factory | Recovered native VideoSink/InputSource construction and custom callback reference-count helpers. Built a private construction/destruction probe; nine QNX synthetic API cases and 29 Python tests are reported passing. | Real firmware constructors have not been executed by this probe. No new endpoints are registered or advertised. |
| Display fault investigation | The original forced-timer observer remains held. Replacement protocol-3 control waits for explicit cleanup after phone removal; a healthy phone run passed. | Root cause and recovery from a fault remain unconfirmed. A healthy run and process restoration do not prove visual recovery. |
| Passive tracing | A later 180-second door-scenario trace contains phone startup, configuration, focus/playback, codec and shutdown events; 7,665,178 bytes, unchanged stock PID, user-reported normal view. | The door did not reproduce the fault in that run. Cause and recovery remain unproven. |
| Replacement phone workflow | Healthy trial: nine registrations, eight known callers, zero drops; view reported normal after 136.672 seconds. Pending cleanup had no authorization; explicit cleanup then restored stock. | This verifies that captured trial, not every lifecycle/failure case. Door opening was reported but was not a timed challenge. |
| CarPlay | Initial screen-registration and H.264 references provide a separate research path. | Additional phone-display support remains unproven. |

Start with [INVESTIGATION-STATUS.txt](delphi-analysis/INVESTIGATION-STATUS.txt), [OBSERVER-DISPLAY-HARDWARE-REVIEW.txt](delphi-analysis/OBSERVER-DISPLAY-HARDWARE-REVIEW.txt), and [ANDROID-AUTO-BLACK-SCREEN-INVESTIGATION.txt](delphi-analysis/ANDROID-AUTO-BLACK-SCREEN-INVESTIGATION.txt). For the latest factory/workflow milestone, also read [ENDPOINT-FACTORY-PROBE-READY.txt](delphi-analysis/ENDPOINT-FACTORY-PROBE-READY.txt). These reports contain historical updates; newer evidence supersedes older pending-test statements.

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
| `_phone_trace_20261029_213916_05589f93/` | Door-scenario trace: startup/playback captured, 180,002 ms, 7,665,178 bytes; user reported normal view and no door-induced black view. |
| `_disconnect_observer_20261029_225707_669ee00c/` | Replacement controller: 20-second no-phone pending/explicit-cleanup lifecycle validated on unit. |
| `_disconnect_observer_20261029_233918_512db910/` | Healthy phone trial: nine registrations/zero drops, 136.672-second observation; cleanup only after explicit authorization, stock restoration verified. |

Directory timestamps use UTC. The healthy replacement-controller phone capture began around 7:39 p.m. Eastern on October 29. Its machine review records `phone_session_trial_passed=true`, but `display_recovery_verified=false`: no fault occurred from which to demonstrate recovery. The later passive trace provides actual startup/playback events, while the earlier baseline retained unverified manual coverage.

The display capture ties the same endpoint to registration, configuration, and focus. Captured configuration arguments are `1, 2, 0, 0, 160, 0, 10000` and match outgoing discovery fields. Focus arguments are `1,true`; they do not constitute an incoming focus response. Only the offer's resolution mapping is established; no frame-rate enum label is inferred.

The host-only paired descriptor adds illustrative video service 9 and input service 10 for display 1. It has not been advertised on the unit. Existing router occupancy is not established, and primary callback/decoder ownership must not be reused for a secondary stream. See the display hardware review and `control-runtime/endpoint-abi-*` artifacts for the recovered ABI evidence.

## Black-view investigation and replacement workflow

The reported failure affects the Android Auto view while car/settings/radio remain usable. Recovery required a ten-second power-button hold; opening the driver door during an experiment appeared associated, with ignition on or the engine running. This is not established as a whole-unit crash, an expected interruption, or an ignition-off event.

Earlier watchdog/controller success verifies process identity and restoration, not rendering health, USB rebind, focus recovery, or a healthy phone session. The timed restart could interact with an active session; door-related visibility/lifecycle handling and instrumentation stalls remain hypotheses. Existing evidence does not identify the cause.

`scripts/run_androidauto_observer.py` still refuses live `--run` variants. The separate `run_disconnected_observer.py` uses a validated replacement controller: its 60-second checkpoint does not restart the app. The observed app and bounded log stay active until the phone is physically removed and explicit cleanup is requested. Timer expiry, controller loss, or an exception does not signal the observed app. This workflow does interrupt/restart AndroidAuto at launch and authorized cleanup; it is distinct from passive tracing. Preserve pending markers/results and use the exact saved-profile resume instructions rather than forcing a retry.

The first passive phone-trace launch failed because a bare background `&` was combined with the shell completion suffix. The corrected launcher stores `$!` before the completion marker; the fix was checked against QNX ksh syntax and negative controls. The subsequent hardware capture demonstrates that this reader can collect trace bytes on the unit. It does not prove the black-view cause or recovery.

## Paired-endpoint factory probe

`native/endpoint-factory/` now contains an isolated private VideoSink 9/InputSource 10 construction/destruction probe using byte-locked native helper profiles. Corrected static tracing recovers the InputSource constructor and the receiver's custom `{count-pointer, object-pointer}` ownership layout. An independent callback adapter and native reference-count transitions replace guesses based on a standard C++ shared pointer or copied primary objects.

The probe must preserve the primary VideoSink and full router-table snapshots. It does not register the private objects, change discovery, or send focus/ack/media/input messages. Unknown object/refcount state is quarantined until process exit rather than passed to guessed destructors. Candidate empty slots are observations, not reservations.

Saved release evidence reports nine ARM32 QNX synthetic API cases, full-DSO forwarding/timeout checks, 29 Python tests, and portable plan/manifest checks passing. Synthetic helpers do not prove the real firmware constructor ABI. The release explicitly has `factory_probe_hardware_tested=false`, `secondary_endpoints_registered=false`, and `discovery_changed=false`.

The next hardware gate described by the repository is this isolated factory probe using the replacement explicit-cleanup workflow, not another baseline or a secondary-stream advertisement. Details and limits are in [native/endpoint-factory/README.txt](native/endpoint-factory/README.txt). This README review did not run it or connect to the vehicle.

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
|   |-- run_androidauto_observer.py  Original timed observer; hold enforced
|   |-- run_disconnected_observer.py  Replacement explicit-cleanup/factory runner
|   |-- package_endpoint_factory.py  Factory probe packaging
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
|   |   |-- launch/                Original real-app/display releases (live hold)
|   |   `-- disconnect-launch/     Validated explicit-cleanup controller
|   |-- endpoint-factory/          Private constructor/ownership probe and fixture
|   |-- trace-reader/              Bounded passive logger, tests, and release
|   `-- loader-probe/              Isolated QNX loader experiment
|-- delphi-analysis/
|   |-- control-runtime/           Hardware reviews, ABI/discovery/trace evidence
|   |-- extracted/                 Image extraction artifacts
|   |-- display-hmi-java/          Java HMI analysis
|   `-- bench/                     Optional bench investigation plan
|-- delphi-dump/                   Acquisition, observer, health, and trace captures
|   |-- _disconnect_observer_*/    Replacement controller and phone-trial evidence
|   `-- delphi-inventory.txt       Original inventory transcript
`-- .tools/                       Local dependencies (Git-ignored)
```

The working tree contains substantial staged and unstaged research/tooling changes. This README update does not commit or publish them; availability in a fresh checkout may differ. Earlier preflight payload directories and the original observer ZIP are absent locally. Preserve acquisition manifests with payloads. Raw discovery contains unit identifiers; configuration, environments, and traces may contain private data.

## Using the tools

```powershell
Set-Location -LiteralPath '.'
```

Read [scripts/USAGE.txt](scripts/USAGE.txt), [OBSERVER-PREFLIGHT.txt](scripts/OBSERVER-PREFLIGHT.txt), and [DISPLAY-HEALTH-DIAGNOSTICS.txt](scripts/DISPLAY-HEALTH-DIAGNOSTICS.txt) for scope and prerequisites. General collectors use Python 3.10+ and the standard library; research/native builds require their documented dependencies. Substitute `python` for `py -3` if needed.

Inspect workflow plans without connecting:

```powershell
py -3 .\scripts\collect_display_health.py
py -3 .\scripts\run_phone_trace.py
py -3 .\scripts\run_disconnected_observer.py --phone-capture --factory-probe --phone-unplugged
```

The passive phone-trace runner's opt-in mode stages a bounded RAM-only loopback reader and leaves AndroidAuto running. Its documented handoff starts on Ethernet, waits for `LOGGER READY`, swaps to the phone with the door closed, waits 210 seconds, then reconnects Ethernet for collection. The reader stops at 180 seconds or 16 MiB. A logger-complete result does not establish manual handoff coverage. Review the existing successful baseline before deciding on another capture.

FTP access to DTS named memory objects was rejected on this unit; older snapshot instructions are historical, not a reason to repeat that failed acquisition. TraceServer's enabled text backend on TCP 15361 provides the current trace source. Baseline collectors avoid replacing an existing trace consumer and do not change filters or clear buffers. FTP/Telnet use the documented trusted direct connection and are unencrypted.

The factory plan is not a vehicle run. The opt-in procedure, phone-removal confirmation, and same-profile resume requirements are in the factory instructions. No further baseline repeat is requested by the latest report. Factory success would still not enable endpoint registration, phone discovery changes, or cluster maps.

For local display-capture review:

```powershell
py -3 .\scripts\review_androidauto_display.py .\delphi-dump\_androidauto_observer_20261029_130447_557863fc
```

Python unit-test discovery remains available with `py -3 -m unittest discover -s .\scripts -p "test_*.py" -v`; native and separately named research tests have their own runners. Saved reports describe wire/ABI, QNX fixture, runner, and shell-completion validation. This README review verifies saved evidence and does not rerun native suites or connect to the vehicle.

## Next steps

1. Review the endpoint-factory release and perform its narrow constructor/ownership hardware gate using the explicit disconnected-cleanup workflow; preserve refusals and restoration evidence. No further baseline repeat is requested.
2. After a passing factory gate, implement independent streaming callbacks, decoder/channel/session/focus/ack state, input display association, registration rollback, and complete cleanup/disconnect/backpressure behavior offboard.
3. Verify router vacancy at actual registration and working endpoint lifecycle before advertising paired descriptors. Then establish phone acceptance and secondary video under this Delphi handshake.
4. Continue diagnosing the historical black-view issue without treating healthy trials as fault recovery. Keep the original forced-timer runner held.
5. Establish geometry/codec compatibility and exclusive FPK/TransportServer/MOST ownership/restoration before attempting cluster routing.

Healthy observation with explicit cleanup is demonstrated. Real factory-probe execution, secondary-video negotiation, recovery from the prior fault, and working cluster maps remain open.
