#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run observer/managed-bench QNX emulator tests." "$@"
console_status STEP 'Running prerequisite native/observer/managed-bench/build.sh.'
sh /src/native/observer/managed-bench/build.sh
mkdir -p /w /src/native/observer/managed-bench/qemu
cd /w
cp /src/native/observer/managed-bench/build/* /w/
cp /src/delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce/procman.captured /w/
printf '%s  %s\n' c32c018b515396bd0b322fb2014b45f2fba37d6000b2d178e9dc402c6845f05d /w/procman.captured | sha256sum -c -
cp /src/native/observer/managed-bench/manager.cfg /w/
cp /src/native/observer/release/libdelphi_observer.so /src/native/observer/smoke/build/libautoreceiver.so /w/

cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    managed_runner
    display_msg "MANAGED_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
libsocket.so.3
procman.captured
libdelphi_observer.so
libautoreceiver.so
[+raw]
managed_child
managed_original
[-raw]
managed_wrapper
managed_runner
manager.cfg
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/lib/libsocket.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/observer/managed-bench/qemu
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
console_status STEP 'Booting QNX emulator; results are being collected in the test log.'
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 25 ) | timeout 50 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
grep -E 'MANAGED_|Process .*exited|terminated SIG' "$w/qemu.log" || true
grep -q MANAGED_REAL_PROCMAN_RESTART_AND_CLEAN_EXIT_PASS "$w/qemu.log"
grep -q 'Process 3 (managed_runner) exited status=0.' "$w/qemu.log"
grep -q MANAGED_REAL_OBSERVER_CAPTURE_PASS "$w/qemu.log"
grep -q MANAGED_REAL_STOCK_RESTORE_PASS "$w/qemu.log"
grep -q MANAGED_QNX_END "$w/qemu.log"
sha256sum procman.captured managed_child managed_original managed_wrapper managed_runner libsocket.so.3 libdelphi_observer.so libautoreceiver.so > "$w/tested.sha256"
