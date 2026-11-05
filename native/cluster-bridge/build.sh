#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native cluster-bridge binaries." "$@"
w=$(mktemp -d /tmp/delphi-cluster.XXXXXX)
mkdir -p "$w/cluster-bridge" "$w/observer/launch"
cp /src/native/cluster-bridge/nav_snapshot.c "$w/cluster-bridge/"
cp /src/native/observer/launch/proc_guard.[ch] "$w/observer/launch/"
cd "$w/cluster-bridge"
# Compile only read/open/identity helpers. Exclude pg_interrupt and all later code.
sed '/^int pg_interrupt(/,$d' ../observer/launch/proc_guard.c > proc_readonly.c
P=arm-unknown-nto-qnx6.5.0eabi
console_status STEP 'Compiling nav_snapshot.'
$P-gcc -std=gnu11 -O2 -Wall -Wextra -Werror -ffunction-sections -fdata-sections -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm -I../observer/launch nav_snapshot.c proc_readonly.c -Wl,--gc-sections -Wl,-z,noexecstack -o nav_snapshot
$P-gcc -std=gnu11 -O2 -Wall -Wextra -Werror -ffunction-sections -fdata-sections -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm -I../observer/launch nav_snapshot.c proc_readonly.c -Wl,--gc-sections -Wl,-z,noexecstack -DNAV_SNAPSHOT_TIMED -o nav_snapshot_timed
mkdir -p /src/native/cluster-bridge/build
cp nav_snapshot nav_snapshot_timed /src/native/cluster-bridge/build/
