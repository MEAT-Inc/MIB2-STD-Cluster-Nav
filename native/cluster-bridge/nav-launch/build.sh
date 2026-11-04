#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native cluster-bridge/nav-launch binaries." "$@"
w=$(mktemp -d /tmp/delphi-nav-launch.XXXXXX)
cp /src/native/cluster-bridge/nav-launch/*.[ch] "$w/"
cd "$w"
sed '/^int pg_interrupt(/,/^}/d' proc_guard.c > proc_readonly.c
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling nav_launch.'
$P-gcc $flags controller.c proc_readonly.c -Wl,-z,noexecstack -o nav_launch
console_status STEP 'Compiling nav_launch_race_fixture.'
$P-gcc $flags -DNAV_LAUNCH_RACE_FIXTURE controller.c proc_readonly.c -Wl,-z,noexecstack -o nav_launch_race_fixture
console_status STEP 'Compiling nav_launch_fixture.'
$P-gcc $flags fixture.c proc_guard.c -Wl,-z,noexecstack -o nav_launch_fixture
console_status STEP 'Compiling libnav_fixture.so.'
$P-gcc $flags -fPIC -shared fixture-preload.c -Wl,-z,noexecstack -o libnav_fixture.so
$P-gcc $flags lifecycle-fixture.c proc_guard.c -Wl,-z,noexecstack -o nav_lifecycle_fixture
console_status STEP 'Compiling nav_launch_qemu_runner.'
$P-gcc $flags qemu-runner.c proc_guard.c -Wl,-z,noexecstack -o nav_launch_qemu_runner
mkdir -p /src/native/cluster-bridge/nav-launch/build
cp nav_lifecycle_fixture nav_launch nav_launch_race_fixture nav_launch_fixture libnav_fixture.so nav_launch_qemu_runner /src/native/cluster-bridge/nav-launch/build/
