#!/bin/sh
set -eu
sh /src/native/trace-reader/build.sh
w=$(mktemp -d /tmp/delphi-trace-qemu.XXXXXX)
cp /src/native/trace-reader/qemu-runner.c "$w/"
cd "$w"
P=arm-unknown-nto-qnx6.5.0eabi
$P-gcc -std=gnu99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm qemu-runner.c -Wl,-z,noexecstack -o trace_qemu_runner
T=/opt/qnx650/target/qnx6/armle-v7
cp /src/native/trace-reader/build/trace_reader .
cp /src/native/trace-reader/qemu/launch-good.sh /src/native/trace-reader/qemu/launch-bad.sh .
cp "$T/bin/ksh" .
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin .
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" .
cp "$(find "$T" -name libsocket.so.3 -print -quit)" .
sed -e 's/\r$//' -e "s|/w/|$w/|g" /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
 procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
 devc-serdebug -e -F -S
 waitfor /dev/ser1 4
 reopen /dev/ser1
 trace_qemu_runner
 display_msg "TRACE_READER_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
libsocket.so.3
procnto-smp
devc-serdebug
trace_reader
trace_qemu_runner
ksh
launch-good.sh
launch-bad.sh
EOF
export MKIFS_PATH=$w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
mkifs test.build ifs.bin
mkdir fat
cp ifs.bin fat/
mkdir -p /src/native/trace-reader/qemu
log=/src/native/trace-reader/qemu/qemu.log
(printf '\n';sleep 4;printf 'virtio scan\n';sleep 2;printf 'fatload virtio 0:1 0x40200000 ifs.bin\n';sleep 3;printf 'go 0x40200000\n';sleep 15) | timeout -k 5 35 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:$w/fat,format=raw,media=disk -display none -serial stdio > "$log" 2>&1 || true
grep -q TRACE_READER_QNX_LOADER_ROOT_REFUSAL_PASS "$log"
grep -q TRACE_READER_QNX_KSH_GOOD_WIRE_PASS "$log"
grep -q TRACE_READER_QNX_KSH_BAD_WIRE_REJECTED "$log"
grep -q TRACE_READER_QNX_END "$log"
grep -q 'trace_qemu_runner) exited status=0' "$log"
sha256sum trace_reader launch-good.sh launch-bad.sh > /src/native/trace-reader/qemu/tested.sha256
printf 'TRACE_READER_QNX_PASS (loader/root refusal only; networking tested on host)\n'
