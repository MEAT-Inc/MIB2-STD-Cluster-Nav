#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Build native secondary-display binaries." "$@"
w=$(mktemp -d /tmp/delphi-secondary.XXXXXX)
mkdir -p "$w/cluster-bridge/layout-margin"
cp /src/native/cluster-bridge/layout-margin/*.[ch] "$w/cluster-bridge/layout-margin/"
mkdir -p "$w/secondary-display" "$w/endpoint-factory" "$w/observer" "$w/cluster-bridge/live"
cp /src/native/secondary-display/*.[ch] "$w/secondary-display/"
cp /src/native/endpoint-factory/*.[ch] "$w/endpoint-factory/"
cp /src/native/observer/observer.c /src/native/observer/observer.h /src/native/observer/entry-arm.S "$w/observer/"
cp /src/native/cluster-bridge/live/*.[ch] "$w/cluster-bridge/live/"
mkdir -p "$w/observer/launch"
cp /src/native/observer/launch/proc_guard.[ch] "$w/observer/launch/"
cd "$w/secondary-display"
P=arm-unknown-nto-qnx6.5.0eabi
flags='-std=gnu11 -O2 -Wall -Wextra -Werror -fno-strict-aliasing -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -marm'
console_status STEP 'Compiling probe.o.'
$P-gcc $flags -fPIC -fvisibility=hidden -c ../endpoint-factory/probe.c -o probe.o
console_status STEP 'Compiling factory.o.'
$P-gcc $flags -fPIC -fvisibility=hidden -c ../endpoint-factory/factory.c -o factory.o
console_status STEP 'Compiling native object files.'
$P-gcc $flags -fPIC -fvisibility=hidden -c runtime.c observer.c wire.c
$P-gcc $flags -fPIC -fvisibility=hidden -c ../cluster-bridge/live/queue.c -o live-queue.o
console_status STEP 'Compiling entry.o.'
$P-gcc $flags -fPIC -c ../observer/entry-arm.S -o entry.o
console_status STEP 'Compiling libdelphi_observer.so.'
$P-gcc -shared live-queue.o probe.o factory.o runtime.o observer.o wire.o entry.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -lc -o libdelphi_observer.so
console_status STEP 'Compiling bounded live-input reader and fixture.'
sed '/^int pg_interrupt(/,$d' ../observer/launch/proc_guard.c > proc_readonly.c
$P-gcc $flags ../cluster-bridge/live/capture.c ../cluster-bridge/live/queue.c proc_readonly.c -I../observer/launch -Wl,-z,noexecstack -o live_capture
$P-gcc $flags -DLIVE_CAPTURE_TEST ../cluster-bridge/live/capture.c ../cluster-bridge/live/queue.c proc_readonly.c -I../observer/launch -Wl,-z,noexecstack -o live_capture_test
console_status STEP 'Compiling native live packetizer fixture.'
$P-gcc $flags ../cluster-bridge/live/mux.c ../cluster-bridge/live/mux-fixture.c -Wl,-z,noexecstack -o live_mux_fixture
/usr/bin/gcc -B/usr/bin/ -std=gnu11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer ../cluster-bridge/live/mux.c ../cluster-bridge/live/mux-fixture.c -o live_mux_host
./live_mux_host
cp live_mux_host /src/native/cluster-bridge/live/build/
console_status STEP 'Compiling bounded route-presentation policy.'
$P-gcc $flags route-hook-fixture.c route-policy.c -Wl,-z,noexecstack -o route_hook_fixture
$P-gcc $flags route-policy.c route-policy-fixture.c -Wl,-z,noexecstack -o route_policy_fixture
$P-gcc $flags -fPIC -fvisibility=hidden -I../observer/launch -c route-policy.c route-hook.c proc_readonly.c
console_status STEP 'Compiling scoped secondary focus/keyframe probe variant.'
$P-gcc $flags -DSECONDARY_KEYFRAME_PROBE -fPIC -fvisibility=hidden -c observer.c -o observer-probe.o
# Margin200 is the standard secondary profile; density140 also shrinks secondary text.
$P-gcc $flags -fPIC -fvisibility=hidden -c ../cluster-bridge/layout-margin/wire-margin.c -o wire-margin.o
$P-gcc $flags -DLAYOUT_DENSITY_DPI=140 -fPIC -fvisibility=hidden -c ../cluster-bridge/layout-margin/wire-margin.c -o wire-margin-density140.o
$P-gcc $flags -DMARGIN_WIDTH_PIXELS=0 -DLAYOUT_DENSITY_DPI=140 -DLAYOUT_UI_INSET_PIXELS=120 -DLAYOUT_UI_BOTTOM_INSET_PIXELS=72 -DLAYOUT_UI_STABLE_BOTTOM_INSET_PIXELS=64 -fPIC -fvisibility=hidden -c ../cluster-bridge/layout-margin/wire-margin.c -o wire-uiinsets.o
$P-gcc -shared route-policy.o route-hook.o proc_readonly.o live-queue.o probe.o factory.o runtime.o observer-probe.o wire-margin.o entry.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -lc -o libdelphi_observer_keyframe.so
$P-gcc -shared route-policy.o route-hook.o proc_readonly.o live-queue.o probe.o factory.o runtime.o observer-probe.o wire-margin-density140.o entry.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -lc -o libdelphi_observer_keyframe_density140.so
$P-gcc -shared route-policy.o route-hook.o proc_readonly.o live-queue.o probe.o factory.o runtime.o observer-probe.o wire-uiinsets.o entry.o -Wl,-z,now -Wl,-z,noexecstack -Wl,-soname,libdelphi_observer.so -lc -o libdelphi_observer_keyframe_uiinsets.so
$P-gcc $flags ../cluster-bridge/layout-margin/margin-fixture.c -Wl,-z,noexecstack -o margin_wire_fixture
$P-gcc $flags -DLAYOUT_DENSITY_DPI=140 ../cluster-bridge/layout-margin/margin-fixture.c -Wl,-z,noexecstack -o margin_density140_fixture
$P-gcc $flags -DMARGIN_WIDTH_PIXELS=0 -DLAYOUT_DENSITY_DPI=140 -DLAYOUT_UI_INSET_PIXELS=120 -DLAYOUT_UI_BOTTOM_INSET_PIXELS=72 -DLAYOUT_UI_STABLE_BOTTOM_INSET_PIXELS=64 ../cluster-bridge/layout-margin/uiinsets-fixture.c -Wl,-z,noexecstack -o uiinsets_wire_fixture
$P-gcc $flags probe-fixture.c runtime.c ../cluster-bridge/live/queue.c ../endpoint-factory/factory.c -Wl,-z,noexecstack -o keyframe_probe_fixture
console_status STEP 'Compiling wire_fixture.'
$P-gcc $flags wire-fixture.c wire.c -Wl,-z,noexecstack -o wire_fixture
console_status STEP 'Compiling runtime_fixture.'
$P-gcc $flags runtime-fixture.c runtime.c ../cluster-bridge/live/queue.c ../endpoint-factory/factory.c -Wl,-z,noexecstack -o runtime_fixture
console_status STEP 'Compiling libautoreceiver.so.'
$P-gcc $flags -fPIC -shared /src/native/observer/smoke/provider.c provider-extra.c -Wl,-soname,libautoreceiver.so -Wl,-z,noexecstack -o libautoreceiver.so
console_status STEP 'Compiling secondary_forward_fixture.'
$P-gcc $flags forward-fixture.c -L. -lautoreceiver -Wl,-z,noexecstack -o secondary_forward_fixture
console_status STEP 'Compiling transaction_fixture.'
$P-gcc $flags -DSECONDARY_TESTING transaction-fixture.c runtime.c observer.c wire.c ../cluster-bridge/live/queue.c ../endpoint-factory/factory.c -Wl,-z,noexecstack -o transaction_fixture
console_status STEP 'Compiling route presentation forwarding fixtures.'
$P-gcc $flags route-forward-fixture.c -L. -lautoreceiver -Wl,-z,noexecstack -o route_forward_fixture
$P-gcc $flags route-forward-runner.c -Wl,-z,noexecstack -o route_forward_runner
console_status STEP 'Compiling secondary_test_runner.'
$P-gcc $flags test-runner.c -Wl,-z,noexecstack -o secondary_test_runner
mkdir -p /src/native/secondary-display/build
cp uiinsets_wire_fixture libdelphi_observer_keyframe_uiinsets.so margin_wire_fixture margin_density140_fixture libdelphi_observer_keyframe_density140.so route_hook_fixture route_forward_fixture route_forward_runner route_policy_fixture live_mux_fixture live_capture live_capture_test libdelphi_observer_keyframe.so keyframe_probe_fixture libdelphi_observer.so libautoreceiver.so wire_fixture runtime_fixture secondary_forward_fixture secondary_test_runner transaction_fixture /src/native/secondary-display/build/
