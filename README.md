# MIB2 Cluster Navigation

Development and reverse engineering toward live Android Auto navigation in the instrument cluster of a Delphi MIB2 infotainment system.

**Status - November 19, 2026:** live Google Maps are user-confirmed and updating in the physical cluster. The latest v17 trial also verified automatic return to factory maps and successful explicit cleanup. The v18 inset/layout changes are user-verified. Current work focuses on route/session reliability and deployment. Extended live forwarding works beyond diagnostic recording limits. Persistent installation and automatic phone reconnect remain unimplemented; the package is still a temporary single-session trial.

## Target system

| Item | Project context |
| --- | --- |
| Vehicle | User-reported 2019 USDM Volkswagen Golf R |
| Infotainment | Discover Media `3Q0035876B` |
| Software | MU0890 / `MST2_US_VW_P0890D` (`P` followed by zero) |
| Operating system | QNX Neutrino 6.5.0, ARM little-endian |
| Platform | TI-DRA74X-PG1.1; two Cortex-A15 processors |

Native offsets, object layouts, and fingerprints are specific to this build. Laptop portability does not establish compatibility with another firmware train or head unit.

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


## Radio debug mode and wired LAN setup

These steps apply to the Delphi MST2 unit described above. Configure the radio and laptop while parked, with the infotainment powered and the phone unplugged.

### Enable developer mode and Ethernet

1. Connect a supported vehicle diagnostic interface, such as OBDeleven or VCDS, and open control module **5F - Information Electronics / Multimedia**.
2. In OBDeleven, select **Change service > Development mode**, then **Adaptation > Developer mode > Activated**, and save. In VCDS, select the corresponding Developer mode adaptation using the access/session procedure supported by your unit. See the [MIB2 research instructions](https://github.com/mattcabb/mib2std-toolbox/blob/master/Research/README.md#enabling-developer-mode).
3. Hold the radio's **MENU** button for about 10 seconds to open **Testmode Menue**. Open **Green Engineering Menu > debugging mlp**.
4. Select **Ethernet** using the tuning/selection knob and press it to enable the option. Developer mode alone does not enable the USB network adapter.
5. Reboot the radio by holding the power/volume knob for about 10 seconds, then allow it to start normally. Connect the USB Ethernet adapter to the radio's normal media/Android Auto USB port.
6. Reopen **debugging mlp** to confirm the radio's Ethernet address before connecting the tools. The address used throughout this project is `192.168.1.4`.

The Ethernet menu sequence is documented in a [firsthand Delphi P0890D setup guide](https://robpol86.com/mib2_comp_media.html#enabling-ethernet). Menu labels and diagnostic access requirements can differ across firmware; use the Delphi procedure rather than instructions for another MIB vendor. Change only the developer/Ethernet settings needed here.

### USB Ethernet adapters and cabling

Connect:

```text
Radio media USB port -> compatible USB-to-Ethernet adapter -> Ethernet cable -> laptop Ethernet port
```

The radio-side adapter must have a chipset/USB identity supported by the radio's QNX drivers. An adapter working on Windows does not establish radio compatibility. The repository inventory includes ASIX and SMSC network drivers, but the presence of a driver does not guarantee support for every adapter using that chip family.

| Adapter choice | Guidance |
| --- | --- |
| ASIX AX88772A-based USB 2.0 10/100 adapter | A working AX88772A adapter is documented on the same P0890D firmware in the [firsthand guide](https://robpol86.com/mib2_comp_media.html#root-shell). [Plugable USB2-E100](https://plugable.com/products/usb2-e100) is a manufacturer-documented AX88772A example; its exact USB identity still needs to be accepted by the radio. |
| D-Link DUB-E100 | Check the hardware revision and chipset before buying or substituting one. Earlier ASIX versions and later revisions are not interchangeable assumptions: [D-Link's D1 release notes](https://support.dlink.com/resource/products/dub-e100/REVD/DUB-E100_REVD_RELEASENOTES_2.4.0_MAC_EN.PDF) explicitly record a change from AX88772B to AX88772C and a changed USB ID. Use a revision already verified with your Delphi unit. |
| Generic USB 3.x/Gigabit or USB-C hub Ethernet | Do not assume compatibility from the connector or advertised speed; verify the radio-side chipset, USB identity, and actual link. |

A standard Cat5e/Cat6 Ethernet cable is sufficient. If the laptop has no RJ45 port, use a second USB Ethernet adapter supported by the laptop's operating system; it does not need to be the same model as the radio-side adapter. A USB-C-to-USB-A connector adapter changes the connector, not radio driver support. The single radio USB port is shared with the phone: follow the trial's handoff procedure when switching from Ethernet to Android Auto.

### Laptop IP configuration and services

Set a **manual IPv4 address on the laptop Ethernet interface connected to the radio**, not on Wi-Fi:

| Setting | Project configuration |
| --- | --- |
| Radio / script `--host` | `192.168.1.4` - confirm in `debugging mlp` |
| Laptop Ethernet IPv4 | `192.168.1.10` |
| Subnet mask / prefix | `255.255.255.0` / `24` |
| Default gateway | Leave blank |
| DNS servers | Leave blank |
| FTP | TCP `21`; username `ftpuser`, password `ftpuser` |
| Telnet | TCP `23`; username `root`; this project's documented setup uses a blank password |

These addresses and service defaults are also recorded in [scripts/USAGE.txt](scripts/USAGE.txt). Use the actual working credentials if your unit differs; the tools provide password prompts. FTP/Telnet are unencrypted, so use the direct wired connection rather than exposing these services to a shared network.

On Windows, open `ncpa.cpl`, choose the connected Ethernet adapter, then **Properties > Internet Protocol Version 4 (TCP/IPv4) > Properties**. Enter the manual address/mask above. Record the previous settings and restore them after the session if needed. Avoid another active adapter or VPN route using `192.168.1.0/24`.

Check the connection before starting a vehicle workflow:

```powershell
ping 192.168.1.4
Test-NetConnection 192.168.1.4 -Port 21
Test-NetConnection 192.168.1.4 -Port 23
```

If the connection fails, check radio Ethernet enablement after reboot, adapter recognition/link LEDs, cable, the selected laptop interface, and the address shown in `debugging mlp`. A failed ping alone is not a substitute for checking the required TCP services. If FTP login succeeds but transfers fail, check passive-data connections and the laptop firewall rule for the Python/FTP client. The project scripts do not enable developer mode, change laptop IP settings, or activate radio services automatically.


## Portable setup and use

Clone or copy the complete project to any directory. Commands below run from the repository root; no machine-specific drive, username, or Codex installation is required. Defaults locate project assets relative to the scripts. Explicit relative CLI paths normally resolve from the current working directory. Keep the `scripts/` and matching `native/.../release/` structure together when extracting laptop packages.

Prepared laptop runners require Python 3.10+ and the standard library. Use `python`, `python3`, or `py -3` according to your installation. Most release ZIP archives are not tracked in the source tree. The V18 bundle is available from this repository's [Releases page](https://github.com/MEAT-Inc/MIB2-STD-Cluster-Nav/releases). Download V18 and extract the entire bundle into a fresh folder, preserving its directory structure. Start parked with ignition on, working factory maps, the phone unplugged, and Ethernet connected using the IP settings above. From the extracted bundle root, start live output:

```shell
python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged --no-live-timeout
```

1. Follow the prompts to select the factory map in the cluster and confirm startup.
2. Only after **CAPTURE READY**, unplug the Ethernet adapter from the radio USB port, connect the phone, and start a Google Maps route in Android Auto.
3. Live output continues until phone disconnect or a verified failure. Diagnostic recording is bounded at 8 MiB/2,048 frames; reaching that limit does not stop live forwarding.
4. To finish, park, unplug the phone, reconnect Ethernet, and continue the laptop prompts. Confirm **PHONE REMOVED** only when the phone is physically unplugged. Leave the map-location button untouched until answering the automatic-return question.
5. Keep the complete result folder under `delphi-dump/_disconnect_observer_*`. If cleanup is pending, resume using the same V18 bundle and the saved profile; do not start another session over it.

For a bounded 30-second live trial, replace `--no-live-timeout` with `--live-seconds 30`. The extended command above has no active video-duration cutoff. Configure and operate the laptop while parked.

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
