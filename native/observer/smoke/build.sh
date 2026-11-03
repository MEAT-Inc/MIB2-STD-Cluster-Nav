#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native observer/smoke binaries." "$@"
work=$(mktemp -d /tmp/delphi-smoke.XXXXXX)
cp /src/native/observer/smoke/*.c /src/native/observer/observer.h "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=c99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling libautoreceiver.so.'
$P-gcc $flags -fPIC -shared provider.c -Wl,-soname,libautoreceiver.so -Wl,-z,noexecstack -lc -o libautoreceiver.so
console_status STEP 'Compiling observer_smoke.'
$P-gcc $flags main.c -L. -lautoreceiver -Wl,-z,noexecstack -o observer_smoke
console_status STEP 'Compiling observer_smoke_guard.'
$P-gcc $flags guard.c -Wl,-z,noexecstack -o observer_smoke_guard
console_status STEP 'Compiling smoke_qemu_runner.'
$P-gcc $flags qemu-runner.c -Wl,-z,noexecstack -o smoke_qemu_runner
mkdir -p /src/native/observer/smoke/build
cp libautoreceiver.so observer_smoke observer_smoke_guard smoke_qemu_runner /src/native/observer/smoke/build/
