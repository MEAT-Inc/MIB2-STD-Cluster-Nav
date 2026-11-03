#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run observer/path-test QNX emulator tests." "$@"
console_status STEP 'Running prerequisite native/observer/path-test/build.sh.'
sh /src/native/observer/path-test/build.sh
mkdir -p /w /src/native/observer/path-test/qemu
cd /w
cp /src/native/observer/path-test/build/* /w/
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
    path_qemu_runner
    display_msg "PATH_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
[type=dir]
/ramdisk
/ramdisk/delphi-path-test_00000000000000000000000000000000
[type=file]
[+raw]
/ramdisk/delphi-path-test_00000000000000000000000000000000/path_test=/w/path_test
/ramdisk/delphi-path-test_00000000000000000000000000000000/path_child=/w/path_child
/ramdisk/delphi-path-test_00000000000000000000000000000000/path_original=/w/path_original
/ramdisk/delphi-path-test_00000000000000000000000000000000/libautoreceiver.so=/w/libautoreceiver.so
/ramdisk/delphi-path-test_00000000000000000000000000000000/libdelphi_observer.so=/w/libdelphi_observer.so
[-raw]
path_qemu_runner
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/observer/path-test/qemu
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
console_status STEP 'Booting QNX emulator; results are being collected in the test log.'
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 25 ) | timeout 50 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
grep -E 'PATH_.*PASS|PATH_INVALID_|PATH_CHECK_FAILED|exited status=' "$w/qemu.log" || true
for marker in PATH_BASELINE_PASS PATH_ONE_SHOT_RESTORE_PASS PATH_AFTER_DETACH_FAILURE_PASS PATH_BEFORE_DETACH_FAILURE_PASS PATH_ORPHAN_WATCHDOG_PASS PATH_SUITE_PASS PATH_QNX_SUITE_PASS PATH_INVALID_FACTORY_TARGET_REJECTED PATH_QNX_END; do
    grep -q "$marker" "$w/qemu.log"
done
grep -q 'Process 3 (path_qemu_runner) exited status=0.' "$w/qemu.log"
if grep -E 'terminated SIG|PATH_CHECK_FAILED' "$w/qemu.log"; then exit 1; fi
sha256sum path_test path_child path_original libautoreceiver.so libdelphi_observer.so > "$w/tested.sha256"
