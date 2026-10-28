#!/bin/sh
# Run from the project root. Outputs are isolated from all acquired files.
set -eu
mode=${1:-qnx}
case "$mode" in
  qnx) CC=arm-unknown-nto-qnx6.5.0eabi-gcc; out=native/loader-probe/build-qnx
       arch='-march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'; libs='' ;;
  host) PATH=/usr/bin:/bin; export PATH; CC=${CC:-gcc}; out=native/loader-probe/build-host; arch='-D_GNU_SOURCE'; libs='-ldl' ;;
  *) echo 'usage: build.sh [qnx|host]' >&2; exit 2 ;;
esac
mkdir -p "$out"
src=native/loader-probe
common="-std=c99 -O2 -Wall -Wextra -Werror -fno-strict-aliasing $arch"
$CC $common -fPIC -shared "$src/provider.c" -Wl,-soname,libprobe_provider.so -o "$out/libprobe_provider.so"
$CC $common -fPIC -shared "$src/observer.c" -Wl,-soname,libprobe_observer.so $libs -o "$out/libprobe_observer.so"
$CC $common "$src/main.c" -L"$out" -lprobe_provider $libs -o "$out/probe_main"
$CC $common "$src/main.c" -L"$out" -lprobe_observer -lprobe_provider $libs -o "$out/probe_linked"
$CC $common "$src/runner.c" $libs -o "$out/probe_runner"
if [ "$mode" = host ]; then
  LD_LIBRARY_PATH="$out" "$out/probe_main"
  LD_LIBRARY_PATH="$out" "$out/probe_linked" --linked
  LD_LIBRARY_PATH="$out" LD_PRELOAD="$PWD/$out/libprobe_observer.so" "$out/probe_main" --preloaded
fi
