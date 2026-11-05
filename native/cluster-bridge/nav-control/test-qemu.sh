#!/bin/sh
set -eu
w=/w
mkdir -p "$w"
cp /src/native/cluster-bridge/nav-control/*.[ch] "$w/"
cd "$w"
cp /src/native/cluster-bridge/nav-launch/proc_guard.[ch] .
cp /src/native/cluster-bridge/nav-control/fixtures/stall.* .
sed '/^int pg_interrupt(/,$d' proc_guard.c > proc_readonly.c
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags init-fixture.c proc_readonly.c dts-fixture.c -Wl,-E -Wl,-z,noexecstack -o sal_init_fixture
$P-gcc $flags control.c proc_readonly.c dts-fixture.c -Wl,-E -Wl,-z,noexecstack -o nav_cycle
$P-gcc $flags -DNAV_CONTROL_TEST control.c proc_readonly.c dts-fixture.c -Wl,-E -Wl,-z,noexecstack -o nav_cycle_test
$P-gcc $flags idle-fixture.c dts-fixture.c -Wl,-E -Wl,-z,noexecstack -o idle_fixture
cp /src/delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce/procman.captured procman
cp /src/delphi-dump/ramdisk/delphi-stage_4b0597ac42d84f0ca7dc8a8c7e138c00/01_libXSAL.so libXSAL.so
printf '%s\n' '-f /proc/boot/idle_fixture -n"navigationserver" -l0 -x1 -r -c0' > manager.cfg
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin .
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    sal_init_fixture
    display_msg "NAV_CONTROL_QNX_END"
}
[type=dir]
/etc
/extbin
/extbin/apps
/extbin/apps/bin
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
sal_init_fixture
nav_cycle
nav_cycle_test
idle_fixture
procman
manager.cfg
libXSAL.so
stall.stack
stall.mutex
stall.replay.stack
stall.replay.mutex
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/lib/libsocket.so.3" "$T/boot/sys/procnto-smp" .
printf '%s\n' 'libsocket.so.3' >> test.build
export MKIFS_PATH=$w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
out=/src/native/cluster-bridge/nav-control
mkdir -p "$out/build" "$out/qemu" fat
cp sal_init_fixture idle_fixture nav_cycle nav_cycle_test "$out/build/"
sha256sum *.[ch] > "$out/qemu/source.sha256"
cp test.build "$out/qemu/test.build"
mkifs test.build ifs.bin > "$out/qemu/mkifs.log" 2>&1
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 14 ) | timeout 35 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:$w/fat,format=raw,media=disk -display none -serial stdio > "$out/qemu/qemu.log" 2>&1 || true
grep -q NAV_STALL_CAPTURE_GUARD_PASS "$out/qemu/qemu.log"
grep -q NAV_RECOVER_HEALTHY_REFUSAL_PASS "$out/qemu/qemu.log"
grep -q NAV_RECOVER_STALE_REFUSAL_PASS "$out/qemu/qemu.log"
grep -q NAV_RECOVER_FACTORY_AUTORESTART_PASS "$out/qemu/qemu.log"
grep -q NAV_PAGE_READ_QNX_PASS "$out/qemu/qemu.log"
grep -q NAV_PAGE_STALE_IDENTITY_REFUSAL_PASS "$out/qemu/qemu.log"
grep -q NAV_PAGE_BAD_ADDRESS_REFUSAL_PASS "$out/qemu/qemu.log"
grep -q NAV_CONTROL_GUARDED_CYCLE_PASS "$out/qemu/qemu.log"
grep -q NAV_CONTROL_IDENTITY_REFUSAL_PASS "$out/qemu/qemu.log"
grep -q SAL_GRACEFUL_CONTROL_QNX_PASS "$out/qemu/qemu.log"
grep -q SAL_CLIENT_INIT_PASS "$out/qemu/qemu.log"
grep -q SAL_CLIENT_DEINIT_PASS "$out/qemu/qemu.log"
grep -q NAV_CONTROL_QNX_END "$out/qemu/qemu.log"
sha256sum "$out/build/sal_init_fixture" "$out/build/idle_fixture" "$out/build/nav_cycle" "$out/build/nav_cycle_test" > "$out/qemu/tested.sha256"
printf 'NAV_CONTROL_INIT_QNX_PASS\n'

grep -q NAV_REPLAY_STALL_CAPTURE_GUARD_PASS "$out/qemu/qemu.log"
