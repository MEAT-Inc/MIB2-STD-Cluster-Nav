#!/bin/sh
set -eu
work=$(mktemp -d /tmp/delphi-managed.XXXXXX)
cp /src/native/observer/managed-bench/*.c /src/native/observer/managed-bench/bench.h /src/native/observer/observer.h "$work/"
cp /src/native/observer/smoke/build/libautoreceiver.so "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=c99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags child.c -L. -lautoreceiver -Wl,-z,noexecstack -o managed_child
cp managed_child managed_original
$P-gcc $flags wrapper.c -Wl,-z,noexecstack -o managed_wrapper
$P-gcc $flags runner.c -Wl,-z,noexecstack -o managed_runner
mkdir -p /src/native/observer/managed-bench/build
cp managed_child managed_original managed_wrapper managed_runner /src/native/observer/managed-bench/build/
