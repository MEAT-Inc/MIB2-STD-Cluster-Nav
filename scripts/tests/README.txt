Python regression tests
=======================
From the repository root:
 python -B -m unittest discover -s scripts/tests -p "test_*.py" -v
 python -B scripts/tests/test_cluster_replay.py
The packet-reference suite is now test_native_transport_packet_reference.py and
is included in default discovery. Tests resolve shared production modules from
scripts/ and native fixtures from the repository root. Some tests require the
existing native test artifacts; no acquired software is executed by these tests.
Obsolete standalone model suites and PowerShell test launchers have been removed.
Native QNX shell harnesses stay beside their C sources in native/ because their
build recipes and generated test evidence use those established paths.
