#!/bin/sh
set -eu
sh /src/native/cluster-bridge/replay/build.sh
mkdir -p /w /src/native/cluster-bridge/replay/qemu
cd /w
cp /src/native/cluster-bridge/replay/build/* /w/
cp /src/native/cluster-bridge/replay/hook-replay.bin /w/replay.bin
: > /w/isoTX
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    replay_libc_fixture
    replay_libc_check_test
    replay_imports_fixture
    replay_fixture
    replay_hook_runner
    display_msg "REPLAY_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
replay_fixture
replay_hook_runner
replay_hook_fixture
replay_imports_fixture
replay_libc_fixture
replay_libc_check_test
libdelphi_cluster_early_legacy.so
libdelphi_cluster_test.so
[type=dir]
/ramdisk
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000
/dev/transport_server
/dev/transport_server/spawn
[type=file]
[+raw]
/ramdisk/delphi-nav-bridge_00000000000000000000000000000000/replay.bin=/w/replay.bin
/dev/transport_server/spawn/isoTX=/w/isoTX
[-raw]
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
out=/src/native/cluster-bridge/replay/qemu
cp test.build "$out/test.build"
mkifs test.build ifs.bin > "$out/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 15 ) | timeout 40 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$out/qemu.log" 2>&1 || true
grep -q 'REPLAY_FIXTURE_PASS' "$out/qemu.log"
grep -q 'REPLAY_QNX_END' "$out/qemu.log"
if grep -q 'terminated SIG' "$out/qemu.log"; then exit 1; fi
grep -q "REPLAY_ACTUAL_PRELOAD_PASS" "$out/qemu.log"
grep -q "REPLAY_HOOK_RUNNER rc=0" "$out/qemu.log"
sha256sum /src/native/cluster-bridge/replay/build/libdelphi_cluster.so /src/native/cluster-bridge/replay/build/libdelphi_cluster_test.so replay_fixture > "$out/tested.sha256"
printf 'REPLAY_QNX_PASS\n'

grep -q "REPLAY_EARLY_LEGACY_EXIT126_PASS" "$out/qemu.log"
grep -q "REPLAY_EARLY_IO_PASS" "$out/qemu.log"
grep -q "REPLAY_IMPORTS_PASS" "$out/qemu.log"

grep -q "REPLAY_LIBC_PROFILE_PASS" "$out/qemu.log"
grep -q '"profile_matches":true' "$out/qemu.log"
sha256sum /src/native/cluster-bridge/replay/build/replay_libc_check >> "$out/tested.sha256"

grep -q "REPLAY_IDLE_IMPORT_INSPECTION_PASS" "$out/qemu.log"
