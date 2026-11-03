#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native observer/path-test binaries." "$@"
work=$(mktemp -d /tmp/delphi-path-test.XXXXXX)
cp /src/native/observer/path-test/*.c /src/native/observer/path-test/bench.h /src/native/observer/observer.h "$work/"
cp /src/native/observer/smoke/build/libautoreceiver.so /src/native/observer/release/libdelphi_observer.so "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=c99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling path_child.'
$P-gcc $flags child.c -L. -lautoreceiver -Wl,-z,noexecstack -o path_child
cp path_child path_original
console_status STEP 'Compiling path_test.'
$P-gcc $flags control.c -Wl,-z,noexecstack -o path_test
console_status STEP 'Compiling path_qemu_runner.'
$P-gcc $flags qemu-runner.c -Wl,-z,noexecstack -o path_qemu_runner
mkdir -p /src/native/observer/path-test/build
cp path_child path_original path_test path_qemu_runner /src/native/observer/path-test/build/
