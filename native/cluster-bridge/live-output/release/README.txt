LIVE ANDROID AUTO CLUSTER TRIAL v15
===================================
Full800x480 map, density140,120px horizontal UI insets. Map/content bottom inset
is72px; the separate stable UI bottom inset stays64px to preserve the previous
UI anchor. Actual turn-card positioning is phone-controlled and must be checked.
250ms steady buffering and the proven startup/catchup sequence are retained.

Extract the ENTIRE ZIP into a fresh folder. Park, ignition on, working factory
maps, phone unplugged and Ethernet connected. Configure/launch while parked.
Extended output (until phone disconnect or a verified failure):
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged --no-live-timeout
Bounded30-second trial (also the default when neither option is supplied):
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged --live-seconds 30

Only at CAPTURE READY swap Ethernet for phone. The extended mode has no active
video-duration cutoff. Diagnostic recording remains bounded at8MiB/2048 frames;
video forwarding and source/disconnect monitoring continue after recording stops.
After your test, park, unplug phone, reconnect Ethernet and finish the existing
PHONE REMOVED cleanup. Do not operate the laptop while driving. Leave the map
location button untouched until answering the automatic-return question.
Return the complete delphi-dump/_disconnect_observer_* folder.

This remains a single phone-session RAM trial with explicit end-of-test cleanup.
Automatic boot installation and repeated phone reconnect without cleanup are
separate deployment work; this bundle does not install a persistent hook.
Use the separate startup-preflight bundle to collect the current boot script.
If cleanup is pending, resume with this SAME bundle and the saved result folder;
the chosen live limit is saved and cannot be changed during resume.
