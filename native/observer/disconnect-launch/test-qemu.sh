#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run observer/disconnect-launch QNX emulator tests." "$@"
console_status STEP 'Running prerequisite native/observer/disconnect-launch/build.sh.'
sh /src/native/observer/disconnect-launch/build.sh
mkdir -p /w /src/native/observer/disconnect-launch/qemu
cd /w
cp /src/native/observer/disconnect-launch/build/* /w/
cp /src/delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce/procman.captured /w/
printf '%s\n' '-f /extbin/apps/bin/AndroidAuto -n"androidauto" -l0 -x1 -r -c0 -a"-t"' > /w/launch-manager.cfg
cp /src/native/observer/smoke/build/libautoreceiver.so /w/
cp /src/native/observer/release/libdelphi_observer.so /w/
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    launch_qemu_runner
    display_msg "DISCONNECT_QNX_END"
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
/ramdisk
/ramdisk/delphi-aa-observer_00000000000000000000000000000000
/ramdisk/delphi-aa-observer_11111111111111111111111111111111
[type=link] /extbin/apps/lib/libautoreceiver.so.1=/extbin/apps/lib/libautoreceiver.so
[type=file]
[+raw]
/etc/procman_core.cfg=/w/launch-manager.cfg
/proc/boot/procman=/w/procman.captured
/extbin/apps/bin/AndroidAuto=/w/launch_fixture
/extbin/apps/lib/libautoreceiver.so=/w/libautoreceiver.so
libautoreceiver.so
/ramdisk/delphi-aa-observer_00000000000000000000000000000000/observer_launch=/w/observer_launch
/ramdisk/delphi-aa-observer_00000000000000000000000000000000/AndroidAuto.original=/w/launch_fixture
/ramdisk/delphi-aa-observer_00000000000000000000000000000000/receiver.reference=/w/libautoreceiver.so
/ramdisk/delphi-aa-observer_00000000000000000000000000000000/procman.reference=/w/procman.captured
/ramdisk/delphi-aa-observer_00000000000000000000000000000000/procman-core.cfg=/w/launch-manager.cfg
/ramdisk/delphi-aa-observer_00000000000000000000000000000000/libdelphi_observer.so=/w/libdelphi_observer.so
/ramdisk/delphi-aa-observer_11111111111111111111111111111111/observer_launch=/w/observer_launch
/ramdisk/delphi-aa-observer_11111111111111111111111111111111/AndroidAuto.original=/w/launch_fixture
/ramdisk/delphi-aa-observer_11111111111111111111111111111111/receiver.reference=/w/libautoreceiver.so
/ramdisk/delphi-aa-observer_11111111111111111111111111111111/procman.reference=/w/procman.captured
/ramdisk/delphi-aa-observer_11111111111111111111111111111111/procman-core.cfg=/w/launch-manager.cfg
/ramdisk/delphi-aa-observer_11111111111111111111111111111111/libdelphi_observer.so=/w/libdelphi_observer.so
[-raw]
launch_qemu_runner
launch-manager.cfg
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libsocket.so.3" "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/observer/disconnect-launch/qemu
cp test.build "$w/test.build"
runlog=$(mktemp "$w/qemu.XXXXXX")
echo "Emulator log: $runlog"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
console_status STEP 'Booting QNX emulator; results are being collected in the test log.'
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 105 ) | timeout -k 5 125 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$runlog" 2>&1 || true
cp "$runlog" "$w/qemu.log"
grep -E 'LAUNCH_.*PASS|LAUNCH_IDENTITY_|LAUNCH_RESTORED|LAUNCH_COMPLETE|LAUNCH_FAILED|LAUNCH_REFUSED|exited status=' "$w/qemu.log" || true
for marker in DISCONNECT_PENDING_NO_SIGNAL_PASS DISCONNECT_STATE_MISMATCH_REFUSED DISCONNECT_LOCK_REFUSED DISCONNECT_LATE_CLEANUP_PASS DISCONNECT_IDEMPOTENT_PASS DISCONNECT_ORPHAN_PENDING_PASS DISCONNECT_ORPHAN_CLEANUP_PASS DISCONNECT_QNX_SUITE_PASS DISCONNECT_QNX_END; do
    grep -q "$marker" "$w/qemu.log"
done
grep -q 'Process 3 (launch_qemu_runner) exited status=0.' "$w/qemu.log"
sha256sum observer_launch libdelphi_observer.so > "$w/tested.sha256"
