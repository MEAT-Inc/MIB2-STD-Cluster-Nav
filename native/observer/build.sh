#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native observer binaries." "$@"
project=/src
scratch=$(mktemp -d /tmp/delphi-observer.XXXXXX)
mkdir -p "$scratch/native/observer"
for f in "$project"/native/observer/*; do [ ! -f "$f" ] || cp "$f" "$scratch/native/observer/"; done
cd "$scratch"
mode=${1:-qnx}
src=native/observer
case "$mode" in
 qnx) CC=arm-unknown-nto-qnx6.5.0eabi-gcc; CXX=arm-unknown-nto-qnx6.5.0eabi-g++; arch='-march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'; asm=entry-arm.S; provider_args="-DFIXTURE_ARM_ENTRY $src/fixture-provider-arm.S"; libs=''; out=$src/build-qnx ;;
 host) PATH=/usr/bin:/bin; export PATH; CC=gcc; CXX=g++; arch=''; asm=entry-host.S; provider_args=''; libs='-ldl -pthread'; out=$src/build-host ;;
 *) exit 2 ;;
esac
mkdir -p "$out"
common="-O2 -Wall -Wextra -Werror -fno-strict-aliasing $arch"
console_status STEP 'Compiling observer.o.'
$CC $common -std=gnu11 -fPIC -fvisibility=hidden -c "$src/observer.c" -o "$out/observer.o"
console_status STEP 'Compiling entry.o.'
$CC $arch -fPIC -c "$src/$asm" -o "$out/entry.o"
console_status STEP 'Compiling libdelphi_observer.so.'
$CC $arch -shared "$out/observer.o" "$out/entry.o" -Wl,-z,noexecstack -Wl,-z,now -Wl,-soname,libdelphi_observer.so -Wl,--version-script="$src/exports.map" $libs -lc -o "$out/libdelphi_observer.so"
console_status STEP 'Compiling libautoreceiver.so.'
$CXX $common -std=c++11 -fPIC -shared "$src/fixture-provider.cpp" $provider_args -Wl,-soname,libautoreceiver.so $libs -o "$out/libautoreceiver.so"
console_status STEP 'Compiling observer_fixture.'
$CXX $common -std=c++11 "$src/fixture-main.cpp" -L"$out" -lautoreceiver $libs -o "$out/observer_fixture"
console_status STEP 'Compiling libwrong.so.'
$CXX $common -std=c++11 -fPIC -shared "$src/fixture-provider.cpp" $provider_args -Wl,-soname,libwrong.so $libs -o "$out/libwrong.so"
console_status STEP 'Compiling observer_wrong.'
$CXX $common -std=c++11 "$src/fixture-main.cpp" -L"$out" -lwrong $libs -o "$out/observer_wrong"
console_status STEP 'Compiling observer_runner.'
$CC $common "$src/fixture-runner.c" -o "$out/observer_runner"
console_status STEP 'Compiling observer_empty.'
$CC $common "$src/empty.c" -o "$out/observer_empty"

if [ "$mode" = qnx ]; then
 $CC $common -c "$src/fixture-abi.c" -o "$out/abi-main.o"
 $CXX $common "$out/abi-main.o" "$src/fixture-abi-arm.S" -L"$out" -lautoreceiver -o "$out/observer_abi"
fi
mkdir -p "$project/$out"
cp "$out/"* "$project/$out/"
