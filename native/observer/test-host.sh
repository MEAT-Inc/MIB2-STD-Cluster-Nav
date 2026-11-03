#!/bin/sh
set -eu
. /src/scripts/project-console.sh
console_start "Run observer host tests." "$@"
console_status STEP 'Running prerequisite native/observer/build.sh.'
sh /src/native/observer/build.sh host
scratch=$(mktemp -d /tmp/delphi-observer-host.XXXXXX)
cp /src/native/observer/build-host/* "$scratch/"
cd "$scratch"
export LD_LIBRARY_PATH=$scratch
console_status STEP 'Running ./observer_fixture --baseline'
./observer_fixture --baseline
LD_PRELOAD="$scratch/libdelphi_observer.so" DELPHI_OBSERVER_LOG="/tmp/delphi-observer-host-$$.bin" ./observer_fixture
LD_PRELOAD="$scratch/libdelphi_observer.so" DELPHI_OBSERVER_LOG=/invalid/disabled ./observer_fixture --disabled
set +e
LD_PRELOAD="$scratch/libdelphi_observer.so" ./observer_empty
result=$?
set -e
[ "$result" = 125 ]
echo OBSERVER_MISSING_ORIGINAL_PASS
cp "/tmp/delphi-observer-host-$$.bin" /src/native/observer/build-host/host-capture.bin
