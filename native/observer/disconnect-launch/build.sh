#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native observer/disconnect-launch binaries." "$@"
w=$(mktemp -d /tmp/delphi-disconnect-launch.XXXXXX)
cp /src/native/observer/disconnect-launch/controller.c /src/native/observer/disconnect-launch/launch.h /src/native/observer/observer.h "$w/"
cp /src/native/observer/launch/proc_guard.c /src/native/observer/launch/proc_guard.h "$w/"
cd "$w"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling observer_launch.'
$P-gcc $flags controller.c proc_guard.c -Wl,-z,noexecstack -o observer_launch
mkdir -p /src/native/observer/disconnect-launch/build
cp observer_launch /src/native/observer/disconnect-launch/build/
cp /src/native/observer/launch/fixture.c .
cp /src/native/observer/disconnect-launch/qemu-runner.c .
cp /src/native/observer/smoke/build/libautoreceiver.so .
console_status STEP 'Compiling launch_fixture.'
$P-gcc $flags fixture.c -L. -lautoreceiver -Wl,-z,noexecstack -o launch_fixture
console_status STEP 'Compiling launch_qemu_runner.'
$P-gcc $flags qemu-runner.c proc_guard.c -Wl,-z,noexecstack -o launch_qemu_runner
cp launch_fixture launch_qemu_runner /src/native/observer/disconnect-launch/build/
