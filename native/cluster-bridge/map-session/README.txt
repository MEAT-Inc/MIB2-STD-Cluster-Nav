November 4: SHORT READ-ONLY SHUTDOWN STACK CAPTURE
================================================
The latest orderly shutdown entered native teardown but stalled with NavMain
waiting on a mutex reported as owned by that same thread. The trace reports an
SDK close failure followed by map-provider cleanup. The exact blocked call is
not identified. Do not repeat the graceful-cycle or replay experiments.

If still in that failed-test state, collect before reboot:
 python scripts/collect_map_session.py --run --state broken --shutdown-stack

Two short passes capture Nav threads, backtrace, registers and mappings, plus
MOST/screen waits, process inventory and retained log. No native helper upload,
shutdown, restart, signal or video is sent. Return the entire _map_session_*
folder, then reboot the radio to restore normal operation. If already rebooted,
do not recreate the failure by rerunning shutdown.

QNX6.5 pidin backtrace/regs documentation:
https://qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/p/pidin.html
Target backtrace/register support is not yet verified. Unsupported queries
are saved as optional errors and do not discard other diagnostics.

READ-ONLY MAP SESSION COMPARISON
V6 accepted5646 transport packets then32zero writes; no cluster image. A new
stock NavigationServer process was verified after cleanup, but factory map
rendering stayed Starting map until radio reboot. The replay release is held
while the map/MOST lifecycle is diagnosed. Do not extend its retry limit.

Extract this bundle into the laptop project. Ignitionon/Ethernet connected,
phone unplugged, select factory navigation map view in the cluster.
If still stuck at Starting map, BEFORE rebooting run:
 python scripts/collect_map_session.py --run --state broken
After it finishes, restart the radio normally (holdpower about10seconds if
needed), wait until factory maps work on both screens, then run:
 python scripts/collect_map_session.py --run --state healthy
If already rebooted, collect healthy ONLY; do not rerun V6 to force a failure.
Return both new delphi-dump/_map_session_* folders when available.
The state label records what YOU observe; the collector cannot certify pixels.

This runs existing pidin read-only queries twice2seconds apart for Nav,
NavServices,DisplayManagement,screen-cda,Most,TransportServer andMediaHandler
when present. It reads existing sloginfo output once (no clear/follow flags),
and lists coredump metadata. It does not read a serialdevice, pullcorepayloads,
enabletraces, preloadanything, restart/signalservices, or sendvideo. New outputs
are staged only in a unique RAM directory and copied locally with hashes. No
native executable is uploaded. Empty logs/missingoptionaldata are retained.

QNX6.5 query references:
https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/p/pidin.html
https://qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/s/sloginfo.html
