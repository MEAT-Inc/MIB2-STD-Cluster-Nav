DELPHI STARTUP LAUNCHER TEST v1
=============================
This tests the radio startup hook, not automatic maps or phone reconnect yet.
It persistently appends a guarded launcher to the EXACT verified factory
/extbin/apps/hmi/HMI/runHMI.sh. The original script stays byte-for-byte intact
as the prefix. The factory JVM starts first. No app is stopped or preloaded.
The launcher writes one receipt of under 256 bytes per full radio boot.
No growing log, daemon, loop, network listener or route notification is added.

Use the extracted bundle on a Windows laptop with Python 3.10 or newer.
Keep all extracted files together. Commands run from the extracted folder.
Do not use while a previous observer trial is pending cleanup.

1. Park, unplug the phone, and connect the laptop to the radio by Ethernet.
   Complete any previous maps/observer trial cleanup using its original bundle.
   Preview the install (no connection or writes):
     python scripts/cluster_startup_launcher.py --install

2. Install the launcher test:
     python scripts/cluster_startup_launcher.py --install --run --phone-unplugged
   The script checks the live QNX identity, persistent mounts, procman config,
   and exact factory startup bytes. It stages and reads back the payload,
   runs QNX shell syntax checks, verifies a persistent factory backup, and
   replaces runHMI.sh by a same-directory rename only after verification.
   Unknown firmware, altered startup, or existing installation is refused.
   Keep the resulting delphi-dump/_startup_launcher_* folder.

3. With the phone still unplugged, perform a FULL radio restart using your
   normal radio restart procedure. Screen off/on alone may not restart QNX.
   Check that the radio reaches its normal home screen and stock functions
   work. Reconnect Ethernet if needed. Do not manually execute boot.sh.
   Collect the boot receipt:
     python scripts/cluster_startup_launcher.py --collect --run --phone-unplugged
   boot_receipt_verified=true proves this installation ran its startup hook.
   No receipt is a useful result too; return the folder without retrying install.

4. Restore factory startup after this test:
     python scripts/cluster_startup_launcher.py --rollback --run --phone-unplugged
   This restores only the exact bundled/verified factory startup bytes, with
   the original 777 permissions. It refuses an unexpectedly changed script.
   Backup and receipt files remain inert in /persistence/delphi-cluster-launcher-v1;
   no startup entry references them after rollback. A repeated rollback is safe.
   Restart once more and confirm normal radio startup.

Return ALL delphi-dump/_startup_launcher_* result folders for this test, and
report whether normal radio startup worked before and after rollback.

If a step fails or the laptop disconnects, keep the results and use the
rollback command once Ethernet and the radio shell are available. No reboot
is issued automatically by any command. Do not rerun install after a partial
failure; its existing-directory refusal protects the original backup.

Default endpoints: 192.168.1.4, FTP 21, Telnet 23, ftpuser/root. Use --help
for overrides and --ask-password when the FTP password is not the default.

This bundle is a launch-chain test. Automatic maps startup and repeatable
phone reconnect will be enabled only after session reset and factory-return
integration have passed their own tests.
