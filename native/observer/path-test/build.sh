#!/bin/sh
set -eu
work=$(mktemp -d /tmp/delphi-path-test.XXXXXX)
cp /src/native/observer/path-test/*.c /src/native/observer/path-test/bench.h /src/native/observer/observer.h "$work/"
cp /src/native/observer/smoke/build/libautoreceiver.so /src/native/observer/release/libdelphi_observer.so "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=c99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags child.c -L. -lautoreceiver -Wl,-z,noexecstack -o path_child
cp path_child path_original
$P-gcc $flags control.c -Wl,-z,noexecstack -o path_test
$P-gcc $flags qemu-runner.c -Wl,-z,noexecstack -o path_qemu_runner
mkdir -p /src/native/observer/path-test/build
cp path_child path_original path_test path_qemu_runner /src/native/observer/path-test/build/
