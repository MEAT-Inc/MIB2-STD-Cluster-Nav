#!/bin/sh
set -eu
sh /src/native/observer/build.sh qnx
w=/src/native/observer/build-qnx/qemu
mkdir -p "$w" /w
cp /src/native/observer/build-qnx/libdelphi_observer.so /src/native/observer/build-qnx/libautoreceiver.so /src/native/observer/build-qnx/libwrong.so /src/native/observer/build-qnx/observer_fixture /src/native/observer/build-qnx/observer_wrong /src/native/observer/build-qnx/observer_empty /src/native/observer/build-qnx/observer_runner /src/native/observer/build-qnx/observer_abi /w/
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
cd /w
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    display_msg "OBSERVER_QNX_START"
    observer_runner
    display_msg "OBSERVER_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
libm.so.2
libstdc++.so.6
procnto-smp
devc-serdebug
observer_runner
observer_abi
observer_fixture
observer_wrong
observer_empty
libautoreceiver.so
libwrong.so
libdelphi_observer.so
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/lib/libm.so.2" "$T/boot/sys/procnto-smp" .
cp "$(arm-unknown-nto-qnx6.5.0eabi-g++ -print-file-name=libstdc++.so)" libstdc++.so.6
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 30 ) | \
 timeout 55 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
grep 'OBSERVER_' "$w/qemu.log" || true
for name in baseline observed disabled repeated existing arm_abi; do
 grep -q "OBSERVER_CASE name=$name exit=0 expected=0" "$w/qemu.log"
done
for name in missing wrong_module; do
 grep -q "OBSERVER_CASE name=$name exit=125 expected=125" "$w/qemu.log"
done
grep -q 'OBSERVER_QNX_SUITE_PASS' "$w/qemu.log"
grep -q 'Process .* (observer_runner) exited status=0' "$w/qemu.log"
grep -q 'OBSERVER_QNX_END' "$w/qemu.log"
if grep -q 'terminated SIG' "$w/qemu.log"; then exit 1; fi
sha256sum /src/native/observer/build-qnx/libdelphi_observer.so > "$w/observer-tested.sha256"
