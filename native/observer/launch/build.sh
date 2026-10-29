#!/bin/sh
set -eu
work=$(mktemp -d /tmp/delphi-launch.XXXXXX)
cp /src/native/observer/launch/*.c /src/native/observer/launch/*.h /src/native/observer/observer.h "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags controller.c proc_guard.c -Wl,-z,noexecstack -o observer_launch
cp /src/native/observer/smoke/build/libautoreceiver.so .
$P-gcc $flags fixture.c -L. -lautoreceiver -Wl,-z,noexecstack -o launch_fixture
$P-gcc $flags qemu-runner.c proc_guard.c -Wl,-z,noexecstack -o launch_qemu_runner
mkdir -p /src/native/observer/launch/build
cp observer_launch launch_fixture launch_qemu_runner /src/native/observer/launch/build/
