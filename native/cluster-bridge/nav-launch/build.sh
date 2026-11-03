#!/bin/sh
set -eu
w=$(mktemp -d /tmp/delphi-nav-launch.XXXXXX)
cp /src/native/cluster-bridge/nav-launch/*.[ch] "$w/"
cd "$w"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags controller.c proc_guard.c -Wl,-z,noexecstack -o nav_launch
$P-gcc $flags -DNAV_LAUNCH_RACE_FIXTURE controller.c proc_guard.c -Wl,-z,noexecstack -o nav_launch_race_fixture
$P-gcc $flags fixture.c proc_guard.c -Wl,-z,noexecstack -o nav_launch_fixture
$P-gcc $flags -fPIC -shared fixture-preload.c -Wl,-z,noexecstack -o libnav_fixture.so
$P-gcc $flags qemu-runner.c proc_guard.c -Wl,-z,noexecstack -o nav_launch_qemu_runner
mkdir -p /src/native/cluster-bridge/nav-launch/build
cp nav_launch nav_launch_race_fixture nav_launch_fixture libnav_fixture.so nav_launch_qemu_runner /src/native/cluster-bridge/nav-launch/build/
