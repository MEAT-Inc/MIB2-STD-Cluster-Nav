LIVE ANDROID AUTO CLUSTER TRIAL v18
===================================
Bottom content inset is now96px (previously72). Top remains8px, left/right120,
stable top0/bottom64, full800x480 video and density140. The content midpoint
moves from208 to196px. Directions bubble and car/street positions may move.
This trial checks whether the Google Maps logo now clears the bottom border.
The v17 diagnostic-cap reporting correction and250ms steady buffering remain.

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
Check the complete Google Maps logo on the idle map. Also check the car,
street name and directions bubble during guidance. Run for about3 minutes,
then disconnect and finish normal cleanup. Expected recording saturation
should no longer fail preflight.
Return the complete delphi-dump/_disconnect_observer_* folder.

This remains a single phone-session temporary trial with explicit end-of-test cleanup.
Automatic boot installation and repeated phone reconnect without cleanup are
separate deployment work; this bundle does not install a persistent hook.
Use the separate startup-preflight bundle to collect the current boot script.
If cleanup is pending, resume with this SAME bundle and the saved result folder;
the chosen live limit is saved and cannot be changed during resume.
