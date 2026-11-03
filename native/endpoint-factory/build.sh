#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native endpoint-factory binaries." "$@"
w=$(mktemp -d /tmp/delphi-factory.XXXXXX)
cp /src/native/endpoint-factory/*.[ch] "$w/"
# Keep observer include relative inside this private Linux build tree.
mkdir -p "$w/src/endpoint-factory" "$w/src/observer"
cp /src/native/observer/observer.c /src/native/observer/observer.h "$w/src/observer/"
cp /src/native/endpoint-factory/*.[ch] "$w/src/endpoint-factory/"
cd "$w/src/endpoint-factory"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling probe.o.'
$P-gcc $flags -fPIC -fvisibility=hidden -c probe.c -o probe.o
console_status STEP 'Compiling factory.o.'
$P-gcc $flags -fPIC -fvisibility=hidden -c factory.c -o factory.o
console_status STEP 'Compiling entry.o.'
$P-gcc $flags -fPIC -c /src/native/observer/entry-arm.S -o entry.o
console_status STEP 'Compiling libdelphi_observer.so.'
$P-gcc -shared probe.o factory.o entry.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -lc -o libdelphi_observer.so
console_status STEP 'Compiling factory_fixture.'
$P-gcc $flags fixture.c factory.c -Wl,-z,noexecstack -lc -o factory_fixture
mkdir -p /src/native/endpoint-factory/build
cp libdelphi_observer.so factory_fixture /src/native/endpoint-factory/build/
