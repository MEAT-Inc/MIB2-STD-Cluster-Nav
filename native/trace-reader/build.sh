#!/bin/sh
set -eu
work=$(mktemp -d /tmp/delphi-trace-reader.XXXXXX)
cp /src/native/trace-reader/reader.c "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
$P-gcc -std=gnu99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm reader.c -Wl,-z,noexecstack -lsocket -o trace_reader
mkdir -p /src/native/trace-reader/build
cp trace_reader /src/native/trace-reader/build/
