#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native observer/transaction binaries." "$@"
work=$(mktemp -d /tmp/delphi-transaction.XXXXXX)
cp /src/native/observer/transaction/*.c /src/native/observer/transaction/bench.h /src/native/observer/observer.h "$work/"
cp /src/native/observer/smoke/build/libautoreceiver.so /src/native/observer/release/libdelphi_observer.so "$work/"
cd "$work"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=c99 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling tx_stock.'
$P-gcc $flags stock.c -L. -lautoreceiver -Wl,-z,noexecstack -o tx_stock
cp tx_stock tx_original
console_status STEP 'Compiling tx_control.'
$P-gcc $flags control.c -Wl,-z,noexecstack -o tx_control
mkdir -p /src/native/observer/transaction/build
cp tx_stock tx_original tx_control /src/native/observer/transaction/build/
