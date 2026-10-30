#!/bin/sh
set -eu
w=$(mktemp -d /tmp/delphi-secondary.XXXXXX)
mkdir -p "$w/secondary-display" "$w/endpoint-factory" "$w/observer"
cp /src/native/secondary-display/*.[ch] "$w/secondary-display/"
cp /src/native/endpoint-factory/*.[ch] "$w/endpoint-factory/"
cp /src/native/observer/observer.c /src/native/observer/observer.h /src/native/observer/entry-arm.S "$w/observer/"
cd "$w/secondary-display"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags -fPIC -fvisibility=hidden -c ../endpoint-factory/probe.c -o probe.o
$P-gcc $flags -fPIC -fvisibility=hidden -c ../endpoint-factory/factory.c -o factory.o
$P-gcc $flags -fPIC -fvisibility=hidden -c runtime.c observer.c wire.c
$P-gcc $flags -fPIC -c ../observer/entry-arm.S -o entry.o
$P-gcc -shared probe.o factory.o runtime.o observer.o wire.o entry.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -lc -o libdelphi_observer.so
$P-gcc $flags wire-fixture.c wire.c -Wl,-z,noexecstack -o wire_fixture
$P-gcc $flags runtime-fixture.c runtime.c ../endpoint-factory/factory.c -Wl,-z,noexecstack -o runtime_fixture
$P-gcc $flags -fPIC -shared /src/native/observer/smoke/provider.c provider-extra.c -Wl,-soname,libautoreceiver.so -Wl,-z,noexecstack -o libautoreceiver.so
$P-gcc $flags forward-fixture.c -L. -lautoreceiver -Wl,-z,noexecstack -o secondary_forward_fixture
$P-gcc $flags -DSECONDARY_TESTING transaction-fixture.c runtime.c observer.c wire.c ../endpoint-factory/factory.c -Wl,-z,noexecstack -o transaction_fixture
$P-gcc $flags test-runner.c -Wl,-z,noexecstack -o secondary_test_runner
mkdir -p /src/native/secondary-display/build
cp libdelphi_observer.so libautoreceiver.so wire_fixture runtime_fixture secondary_forward_fixture secondary_test_runner transaction_fixture /src/native/secondary-display/build/
