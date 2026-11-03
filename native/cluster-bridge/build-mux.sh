#!/bin/sh
set -eu
w=$(mktemp -d /tmp/delphi-mux.XXXXXX)
cp /src/native/cluster-bridge/mux.h /src/native/cluster-bridge/mux.c /src/native/cluster-bridge/mux-fixture.c /src/native/cluster-bridge/mux-file.c "$w/"
cd "$w"
mkdir -p /src/native/cluster-bridge/mux-build
out=/src/native/cluster-bridge/mux-build
/usr/bin/gcc -B/usr/bin/ -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer mux.c mux-fixture.c -o mux-fixture-linux
./mux-fixture-linux
/usr/bin/gcc -B/usr/bin/ -std=c11 -O2 -Wall -Wextra -Werror mux.c mux-file.c -o mux-file-linux
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags -fPIC -c mux.c -o mux-qnx.o
$P-gcc $flags mux.c mux-fixture.c -Wl,-z,noexecstack -o mux-fixture-qnx
$P-gcc $flags mux.c mux-file.c -Wl,-z,noexecstack -o mux-file-qnx
cp mux-fixture-linux mux-file-linux mux-qnx.o mux-fixture-qnx mux-file-qnx "$out/"
