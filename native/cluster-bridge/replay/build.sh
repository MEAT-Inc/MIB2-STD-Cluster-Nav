#!/bin/sh
set -eu
w=$(mktemp -d /tmp/delphi-replay.XXXXXX)
cp /src/native/cluster-bridge/replay/*.[chS] "$w/"
cd "$w"
python3 /src/scripts/generate_replay_libc_profile.py /opt/qnx650/target/qnx6/armle-v7/lib/libc.so.3 sdk-libc-profile.h
out=/src/native/cluster-bridge/replay/build
mkdir -p "$out"
/usr/bin/gcc -B/usr/bin/ -std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -pthread replay.c fixture.c -o fixture-linux
./fixture-linux
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
$P-gcc $flags replay.c fixture.c -Wl,-z,noexecstack -o replay_fixture
$P-gcc $flags -fPIC -fvisibility=hidden -c replay.c loader.c imports.c libc-check.c
$P-gcc $flags -fPIC -c entry-arm.S
$P-gcc -shared replay.o loader.o imports.o libc-check.o entry-arm.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_cluster.so -lc -o libdelphi_cluster.so
$P-gcc $flags -fPIC -fvisibility=hidden -c early-io.c
$P-gcc $flags -fPIC -c entry-legacy.S
$P-gcc $flags libc-check.c libc-fixture.c -Wl,-z,noexecstack -o replay_libc_fixture
$P-gcc $flags libc-check.c libc-preflight.c -Wl,-z,noexecstack -o replay_libc_check
$P-gcc $flags -DREPLAY_LOADER_TEST -DREPLAY_FORCE_PARTIAL_READ libc-check.c libc-preflight.c -Wl,-z,noexecstack -o replay_libc_check_test
$P-gcc $flags imports.c imports-fixture.c -Wl,-z,noexecstack -o replay_imports_fixture
$P-gcc $flags -DREPLAY_LOADER_TEST -DREPLAY_FORCE_PARTIAL_READ -fPIC -fvisibility=hidden -c loader.c -o loader-test.o
$P-gcc -shared replay.o loader-test.o imports.o libc-check.o entry-arm.o early-io.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_cluster_test.so -lc -o libdelphi_cluster_test.so
$P-gcc -shared replay.o loader-test.o imports.o libc-check.o entry-arm.o early-io.o entry-legacy.o -Wl,-z,now -Wl,-z,noexecstack -lc -o libdelphi_cluster_early_legacy.so
$P-gcc $flags -Wl,-E hook-fixture.c hook-calls.S -Wl,-z,noexecstack -o replay_hook_fixture
$P-gcc $flags hook-runner.c -Wl,-z,noexecstack -o replay_hook_runner
cp replay_libc_fixture replay_libc_check replay_libc_check_test replay_imports_fixture libdelphi_cluster_early_legacy.so fixture-linux replay_fixture libdelphi_cluster.so libdelphi_cluster_test.so replay_hook_fixture replay_hook_runner "$out/"
