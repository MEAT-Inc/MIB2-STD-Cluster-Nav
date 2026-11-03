#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native observer/display binaries." "$@"
work=$(mktemp -d /tmp/delphi-display.XXXXXX)
mkdir -p "$work/native/observer/display"
cp /src/native/observer/observer.c /src/native/observer/observer.h /src/native/observer/entry-arm.S "$work/native/observer/"
cp /src/native/observer/display/*.[ch] /src/native/observer/display/*.S /src/native/observer/display/*.map "$work/native/observer/display/"
mkdir -p "$work/native/observer/smoke"
cp /src/native/observer/smoke/provider.c "$work/native/observer/smoke/"
cd "$work/native/observer/display"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling observer.o.'
$P-gcc $flags -fPIC -fvisibility=hidden -c observer.c -o observer.o
console_status STEP 'Compiling registration.o.'
$P-gcc $flags -fPIC -c ../entry-arm.S -o registration.o
console_status STEP 'Compiling display.o.'
$P-gcc $flags -fPIC -c entry-arm.S -o display.o
console_status STEP 'Compiling libdelphi_observer.so.'
$P-gcc -shared observer.o registration.o display.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -Wl,--version-script=exports.map -lc -o libdelphi_observer.so
console_status STEP 'Compiling libautoreceiver.so.'
$P-gcc $flags -fPIC -shared provider.c -Wl,-soname,libautoreceiver.so -Wl,-z,noexecstack -lc -o libautoreceiver.so
console_status STEP 'Compiling libregister_only.so.'
$P-gcc $flags -fPIC -shared ../smoke/provider.c -Wl,-soname,libautoreceiver.so -Wl,-z,noexecstack -lc -o libregister_only.so
console_status STEP 'Compiling display_fixture.'
$P-gcc $flags fixture.c -L. -lautoreceiver -Wl,-z,noexecstack -o display_fixture
console_status STEP 'Compiling display_qemu_runner.'
$P-gcc $flags qemu-runner.c -Wl,-z,noexecstack -o display_qemu_runner
mkdir -p /src/native/observer/display/build
cp libdelphi_observer.so libautoreceiver.so libregister_only.so display_fixture display_qemu_runner /src/native/observer/display/build/
