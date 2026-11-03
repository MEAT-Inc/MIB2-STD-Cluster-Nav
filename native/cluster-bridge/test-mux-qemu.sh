#!/bin/sh
set -eu
sh /src/native/cluster-bridge/build-mux.sh
mkdir -p /w /src/native/cluster-bridge/mux-qemu
cd /w
cp /src/native/cluster-bridge/mux-build/mux-fixture-qnx /w/
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    mux-fixture-qnx
    display_msg "CLUSTER_MUX_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
mux-fixture-qnx
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
out=/src/native/cluster-bridge/mux-qemu
cp test.build "$out/test.build"
mkifs test.build ifs.bin > "$out/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 15 ) | timeout 40 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$out/qemu.log" 2>&1 || true
grep -q 'CLUSTER_MUX_FIXTURE_PASS' "$out/qemu.log"
grep -q 'CLUSTER_MUX_QNX_END' "$out/qemu.log"
if grep -q 'terminated SIG' "$out/qemu.log"; then exit 1; fi
sha256sum mux-fixture-qnx > "$out/tested.sha256"
printf 'CLUSTER_MUX_QNX_PASS\n'
