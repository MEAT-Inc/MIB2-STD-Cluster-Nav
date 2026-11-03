#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run secondary-display QNX emulator tests." "$@"
console_status STEP 'Running prerequisite native/cluster-bridge/build.sh.'
sh /src/native/cluster-bridge/build.sh
console_status STEP 'Running prerequisite native/endpoint-factory/build.sh.'
sh /src/native/endpoint-factory/build.sh
console_status STEP 'Running prerequisite native/secondary-display/build.sh.'
sh /src/native/secondary-display/build.sh
console_status STEP 'Running prerequisite native/observer/smoke/build.sh.'
sh /src/native/observer/smoke/build.sh
mkdir -p /w /src/native/secondary-display/qemu
cd /w
cp /src/native/observer/smoke/build/* /w/
cp /src/native/endpoint-factory/build/factory_fixture /w/
cp /src/native/secondary-display/build/* /w/
cp /src/native/cluster-bridge/build/nav_snapshot /w/
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    procmgr_symlink /proc/boot /ramdisk/delphi-observer-smoke_00000000000000000000000000000000
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    nav_snapshot --self-test
    factory_fixture
    wire_fixture
    runtime_fixture
    transaction_fixture
    secondary_test_runner
    smoke_qemu_runner
    display_msg "DELPHI_SMOKE_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
libautoreceiver.so
libdelphi_observer.so
observer_smoke
observer_smoke_guard
smoke_qemu_runner
nav_snapshot
factory_fixture
wire_fixture
runtime_fixture
transaction_fixture
secondary_forward_fixture
secondary_test_runner
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/secondary-display/qemu
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
console_status STEP 'Booting QNX emulator; results are being collected in the test log.'
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 25 ) | timeout 50 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
grep 'DELPHI_SMOKE_' "$w/qemu.log" || true
grep -q 'DELPHI_SMOKE_PASS mode=baseline calls=9' "$w/qemu.log"
grep -q 'DELPHI_SMOKE_PASS mode=observed calls=9' "$w/qemu.log"
grep -q 'DELPHI_SMOKE_TIMEOUT child_reaped=1' "$w/qemu.log"
grep -q 'DELPHI_SMOKE_QNX_SUITE_PASS' "$w/qemu.log"
grep -q 'DELPHI_SMOKE_QNX_END' "$w/qemu.log"
if grep -E 'terminated SIG' "$w/qemu.log" | grep -v 'observer_smoke) terminated SIGKILL'; then exit 1; fi
sha256sum observer_smoke observer_smoke_guard libautoreceiver.so libdelphi_observer.so > "$w/tested.sha256"

grep -q "ENDPOINT_FACTORY_QNX_OWNERSHIP_FAILURE_PASS cases=9" "$w/qemu.log"
sha256sum factory_fixture libdelphi_observer.so > "$w/factory-tested.sha256"

grep -q "wire fixtures passed" "$w/qemu.log"
grep -q "SECONDARY_RUNTIME_QNX_PASS" "$w/qemu.log"
grep -q "SECONDARY_HOOK_FORWARD_QNX_PASS" "$w/qemu.log"
grep -q "SECONDARY_TEST_RUNNER_PASS" "$w/qemu.log"
sha256sum libdelphi_observer.so libautoreceiver.so wire_fixture runtime_fixture secondary_forward_fixture > "$w/secondary-tested.sha256"

grep -q "SECONDARY_DISCOVERY_TRANSACTION_QNX_PASS" "$w/qemu.log"
sha256sum libdelphi_observer.so libautoreceiver.so wire_fixture runtime_fixture transaction_fixture secondary_forward_fixture > "$w/secondary-tested.sha256"

grep -q "NAV_SNAPSHOT_QNX_PASS" "$w/qemu.log"
sha256sum nav_snapshot > /src/native/cluster-bridge/nav-snapshot-tested.sha256
