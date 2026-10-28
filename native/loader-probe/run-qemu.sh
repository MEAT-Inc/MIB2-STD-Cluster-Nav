#!/bin/sh
# Container-only QNX synthetic test. No vehicle/network access.
set -eu
cd /src
sh native/loader-probe/build.sh qnx
data_mode=${1:-copy}
case "$data_mode" in copy|uip) ;; *) exit 2 ;; esac
w=/src/native/loader-probe/build-qnx/qemu
[ "$data_mode" = copy ] || w=$w-uip
mkdir -p "$w"
cp native/loader-probe/build-qnx/probe_main native/loader-probe/build-qnx/probe_runner native/loader-probe/build-qnx/probe_linked native/loader-probe/build-qnx/libprobe_*.so "$w/"
cp .tools/qnx65-armv7-toolchain/tests/qemu/startup-virt .tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a .tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug .tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin "$w/"
# Existing upstream header's linker expects this fixed container path.
mkdir -p /w
cp "$w/"* /w/
cd /w
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    display_msg "DELPHI_QNX_START"
    probe_runner
    display_msg "DELPHI_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=link] /proc/boot/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
probe_runner
probe_main
probe_linked
libprobe_provider.so
libprobe_observer.so
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" .
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
if [ "$data_mode" = uip ]; then sed -i "s/data=copy/data=uip/" test.build; fi
cp test.build "$w/test.build"
mkifs test.build ifs.bin > "$w/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 25 ) | \
 timeout 50 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$w/qemu.log" 2>&1 || true
# All eight subprocesses must pass, including repeated launch and restoration.
grep 'DELPHI_' "$w/qemu.log" || true
if [ "$data_mode" = uip ]; then
    grep -q 'DELPHI_QNX_CASE name=baseline exit=0 executable_present=0' "$w/qemu.log"
    grep -q 'DELPHI_QNX_CASE name=baseline_repeat exit=14 executable_present=0' "$w/qemu.log"
    grep -q 'DELPHI_EXEC_FAIL mode=0 errno=2' "$w/qemu.log"
    if grep -q 'DELPHI_QNX_SUITE_PASS' "$w/qemu.log"; then exit 1; fi
    echo 'DELPHI_UIP_NEGATIVE_CONTROL_PASS: baseline alone consumes the executable.'
else
    for name in baseline baseline_repeat preload preload_repeat provider basename linked restore_baseline; do
        grep -q "DELPHI_QNX_CASE name=$name exit=0 executable_present=1" "$w/qemu.log"
    done
    grep -q 'DELPHI_PROBE_PASS mode=preloaded calls=19 bounded_records=16 drops=3' "$w/qemu.log"
    grep -q 'DELPHI_QNX_SUITE_PASS' "$w/qemu.log"
    grep -q 'Process .* (probe_runner) exited status=0' "$w/qemu.log"
fi
grep -q 'DELPHI_QNX_END' "$w/qemu.log"
if grep -q 'terminated SIG' "$w/qemu.log"; then exit 1; fi