#!/bin/sh
set -eu
sh /src/native/observer/transaction/build.sh
mkdir -p /w /src/native/observer/transaction/qemu
cd /w
cp /src/native/observer/transaction/build/* /w/
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
    tx_control
    display_msg "TX_QNX_END"
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
[+raw]
tx_stock
tx_original
[-raw]
tx_control
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/observer/transaction/qemu
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 25 ) | timeout 50 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
grep 'TX_' "$w/qemu.log" || true
for marker in TX_BASELINE_PASS TX_ONE_SHOT_AND_STOCK_RESTORE_PASS TX_FAILURE_FALLBACK_PASS TX_PRE_DETACH_FAILURE_RESTORE_PASS TX_ORPHAN_WATCHDOG_RESTORE_PASS TX_TRANSACTION_SUITE_PASS TX_QNX_END; do
    grep -q "$marker" "$w/qemu.log"
done
grep -q 'Process 3 (tx_control) exited status=0.' "$w/qemu.log"
if grep -E 'terminated SIG|TX_CHECK_FAILED' "$w/qemu.log"; then exit 1; fi
sha256sum tx_stock tx_original tx_control libautoreceiver.so libdelphi_observer.so > "$w/tested.sha256"
