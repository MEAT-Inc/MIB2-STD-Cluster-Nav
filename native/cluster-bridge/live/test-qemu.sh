#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run live frame queue cross-process QNX tests." "$@"
mkdir -p /w /src/native/cluster-bridge/live/qemu /src/native/cluster-bridge/live/build
cd /w
cp /src/native/cluster-bridge/live/*.[ch] /w/
console_status STEP 'Checking live queue under host sanitizers.'
/usr/bin/gcc -B/usr/bin/ -std=gnu11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer queue.c queue-fixture.c -o queue-host
./queue-host
console_status STEP 'Compiling QNX cross-process queue fixture.'
arm-unknown-nto-qnx6.5.0eabi-gcc -std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm queue.c queue-fixture.c -Wl,-z,noexecstack -o queue-fixture
cp queue-fixture /src/native/cluster-bridge/live/build/
cp /src/.tools/qnx65-armv7-toolchain/tests/qemu/startup-virt /src/.tools/qnx65-armv7-toolchain/tests/qemu/libstartup.a /src/.tools/qnx65-armv7-toolchain/tests/qemu/devc-serdebug /src/.tools/qnx65-armv7-toolchain/tests/qemu/u-boot.bin /w/
sed 's/\r$//' /src/.tools/qnx65-armv7-toolchain/tests/qemu/ifs-header.build > test.build
cat >> test.build <<'EOF'
[+script] .script = {
    procmgr_symlink ../../proc/boot/libc.so.3 /usr/lib/ldqnx.so.2
    devc-serdebug -e -F -S
    waitfor /dev/ser1 4
    reopen /dev/ser1
    queue-fixture
    display_msg "LIVE_QUEUE_QNX_END"
}
[type=link] /usr/lib/ldqnx.so.2=/proc/boot/libc.so.3
[type=file]
[data=copy]
[perms=+r,+x]
libc.so.3
procnto-smp
devc-serdebug
queue-fixture
EOF
T=/opt/qnx650/target/qnx6/armle-v7
cp "$T/lib/libc.so.3" "$T/boot/sys/procnto-smp" /w/
export MKIFS_PATH=/w:$T/boot/sys:$T/bin:$T/lib:$T/usr/lib
out=/src/native/cluster-bridge/live/qemu
cp test.build "$out/test.build"
mkifs test.build ifs.bin > "$out/mkifs.log" 2>&1
mkdir -p fat
cp ifs.bin fat/
console_status STEP 'Booting QNX emulator; results are being collected in the test log.'
( printf '\n'; sleep 4; printf 'virtio scan\n'; sleep 2; printf 'fatload virtio 0:1 0x40200000 ifs.bin\n'; sleep 3; printf 'go 0x40200000\n'; sleep 15 ) | timeout 40 qemu-system-arm -M virt -nic none -m 256 -cpu cortex-a15 -bios u-boot.bin -drive file=fat:rw:/w/fat,format=raw,media=disk -display none -serial stdio > "$out/qemu.log" 2>&1 || true
grep -q 'LIVE_QUEUE_PROCESS_PASS' "$out/qemu.log"
grep -q 'LIVE_QUEUE_QNX_END' "$out/qemu.log"
if grep -q 'terminated SIG' "$out/qemu.log"; then exit 1; fi
sha256sum queue-fixture > "$out/tested.sha256"
printf 'LIVE_QUEUE_QNX_PASS\n'

grep -q LIVE_QUEUE_POLICY_PASS "$out/qemu.log"
sha256sum queue.c queue.h queue-fixture.c > "$out/source.sha256"
