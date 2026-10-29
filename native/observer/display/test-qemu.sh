#!/bin/sh
set -eu
sh /src/native/observer/display/build.sh
mkdir -p /w /src/native/observer/display/qemu
cd /w
cp /src/native/observer/display/build/* /w/

cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    display_qemu_runner
    display_msg "DISPLAY_QNX_END"
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
display_fixture
display_qemu_runner
/missing/libautoreceiver.so=/w/libregister_only.so
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
w=/src/native/observer/display/qemu
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 25 ) | timeout -k 5 50 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
grep -E 'DISPLAY_.*PASS|DISPLAY_CASE_FAILED|DISPLAY_LOG|exited status=' "$w/qemu.log" || true
for marker in DISPLAY_QNX_SUITE_PASS DISPLAY_ZERO_TAILS_OK DISPLAY_QNX_END; do grep -q "$marker" "$w/qemu.log"; done
for mode in baseline observed disabled full; do grep -q "DISPLAY_FIXTURE_PASS mode=$mode" "$w/qemu.log"; done
if grep -E 'terminated SIG|DISPLAY_CASE_FAILED' "$w/qemu.log"; then exit 1; fi
sha256sum libdelphi_observer.so libautoreceiver.so display_fixture > "$w/tested.sha256"
