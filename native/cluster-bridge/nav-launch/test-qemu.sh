#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run cluster-bridge/nav-launch QNX emulator tests." "$@"
console_status STEP 'Running prerequisite native/cluster-bridge/nav-launch/build.sh.'
sh /src/native/cluster-bridge/nav-launch/build.sh
mkdir -p /w /src/native/cluster-bridge/nav-launch/qemu
cd /w
cp /src/native/cluster-bridge/nav-launch/build/* /w/
cp /src/delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce/procman.captured /w/
printf '%s\n' '-f /extbin/apps/bin/NavigationServer -n"navigationserver" -l0 -x1 -r -c0 -a"-fcfg" -a"../cfg/NAV/v0/NC/Delphi/NavServer.cfg"' > /w/launch-manager.cfg
printf 'nav-fixture-config\n' > /w/NavServer.cfg
cp /src/native/cluster-bridge/nav-launch/build/libnav_fixture.so /w/libdelphi_cluster.so
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    nav_launch_qemu_runner
    display_msg "NAV_DISCONNECT_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
libsocket.so.3
procnto-smp
devc-serdebug
[type=dir]
/etc
/extbin
/extbin/apps
/extbin/apps/bin
/extbin/apps/lib
/extbin/apps/cfg
/extbin/apps/cfg/NAV
/extbin/apps/cfg/NAV/v0
/extbin/apps/cfg/NAV/v0/NC
/extbin/apps/cfg/NAV/v0/NC/Delphi
/ramdisk
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111
[type=file]
[+raw]
/etc/procman_core.cfg=/w/launch-manager.cfg
/proc/boot/procman=/w/procman.captured
/extbin/apps/bin/NavigationServer=/w/nav_launch_fixture
/extbin/apps/cfg/NAV/v0/NC/Delphi/NavServer.cfg=/w/NavServer.cfg
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/nav_launch=/w/nav_launch
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/NavigationServer.original=/w/nav_launch_fixture
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/NavServer.cfg.reference=/w/NavServer.cfg
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/procman.reference=/w/procman.captured
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/procman-core.cfg=/w/launch-manager.cfg
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/libdelphi_cluster.so=/w/libdelphi_cluster.so
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111/nav_launch=/w/nav_launch_race_fixture
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111/NavigationServer.original=/w/nav_launch_fixture
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111/NavServer.cfg.reference=/w/NavServer.cfg
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111/procman.reference=/w/procman.captured
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111/procman-core.cfg=/w/launch-manager.cfg
/ramdisk/delphi-nav-bridge_11111111111111111111111111111111/libdelphi_cluster.so=/w/libdelphi_cluster.so
[-raw]
nav_launch_qemu_runner
launch-manager.cfg
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libsocket.so.3" "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/cluster-bridge/nav-launch/qemu
cp test.build "$w/test.build"
runlog=$(mktemp "$w/qemu.XXXXXX")
echo "Emulator log: $runlog"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
console_status STEP 'Booting QNX emulator; results are being collected in the test log.'
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 70 ) | timeout -k 5 90 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$runlog" 2>&1 || true
cp "$runlog" "$w/qemu.log"
grep -E 'LAUNCH_.*PASS|LAUNCH_IDENTITY_|LAUNCH_RESTORED|LAUNCH_COMPLETE|LAUNCH_FAILED|LAUNCH_REFUSED|exited status=' "$w/qemu.log" || true
for marker in NAV_PRODUCTION_LIFECYCLE_PASS NAV_PREEXEC_CANONICAL_RACE_PROVEN NAV_POST_EXEC_IDENTITY_PASS NAV_FIXTURE_CANONICAL_IMAGE_PASS NAV_STDIO_PRESERVED_PASS NAV_REPLAY_ARM_PASS NAV_DISCONNECT_PENDING_NO_SIGNAL_PASS NAV_DISCONNECT_STATE_MISMATCH_REFUSED NAV_DISCONNECT_LOCK_REFUSED NAV_DISCONNECT_LATE_CLEANUP_PASS NAV_DISCONNECT_IDEMPOTENT_PASS NAV_DISCONNECT_ORPHAN_PENDING_PASS NAV_DISCONNECT_ORPHAN_CLEANUP_PASS NAV_DISCONNECT_QNX_SUITE_PASS NAV_DISCONNECT_QNX_END; do
    grep -q "$marker" "$w/qemu.log"
done
grep -q 'Process 3 (nav_launch_qemu_runner) exited status=0.' "$w/qemu.log"
grep -q NAV_FIXTURE_ARGV_CWD_CONFIG_PASS "$w/qemu.log"
sha256sum nav_launch nav_launch_race_fixture libdelphi_cluster.so > "$w/tested.sha256"
