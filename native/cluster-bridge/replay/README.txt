V5: launcher identifies NavigationServer only AFTER its nonce-bound module report
acknowledges exec. Publishing a wrapper PID/canonical pathname is insufficient:
QNX changes process start identity across exec, even when the PID is unchanged.
Exact PID/start/parent/image checks remain in force for arm and stock cleanup.
Native arm-refusal diagnostics are now collected even on a nonzero command exit.
If the prior V4 run refused cleanup, restart the head unit (hold its power button
about10seconds) before starting this build; the old pending identity cannot be
safely reused by the new controller. Start with healthy factory navigation.
V4: canonical NavigationServer executable, original stdout/stderr preserved.
Unrelated writes/closes bypass the replay lock. Native map-channel readiness,
retained hooks, encoder geometry and heartbeat are checked BEFORE arming.
Only the replay initializer writes its own bounded private startup log.
RECORDED ANDROID AUTO MAPS ON THE CLUSTER - FIRST DISPLAY TRIAL
This plays saved Google Maps video, NOT live navigation/current guidance.
Extract into laptop project. Ignition on, Ethernet connected. Keep phone
unplugged throughout. Select the factory navigation MAP VIEW in the cluster.
Run: python scripts/run_cluster_replay.py --run --phone-unplugged
The routine uses a RAM-only alias and supervised NavigationServer restart.
It leaves AndroidAuto,Most,TransportServer,DisplayManagement and procman running.
When asked, wait until the FACTORY map is visible IN THE CLUSTER, then press
Enter to arm the recorded-map playback. Type SKIP to restore without replay.
Watch the cluster for about48seconds. Stock NavigationServer is then restored;
answer whether the recorded Google Maps view appeared IN THE CLUSTER.
Ethernet stays connected; do not connect phone. Native opens/owns its transport
descriptor. The replay replaces its native packets only after explicit arming
and current800x480/fd checks; never opens a competing transport writer.
Clock-reset packets precede the saved recording. At EOF/error, native packets
remain muted until native channel close or explicit supervised stock cleanup.
No persistent firmware/config files changed. If interrupted/partial, follow:
 python scripts/run_cluster_replay.py --resume "delphi-dump/<folder>" --phone-unplugged
Return the ENTIRE new delphi-dump/_cluster_replay_* folder, even if partial.
QNX lifecycle,real preload caller/errno,arming and ownership tests passed.
Hardware trials have not yet delivered replay packets to the cluster. Live phone feeding
and phone-navigation cluster presentation remain later integration.
