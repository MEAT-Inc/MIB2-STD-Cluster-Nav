"""Package interrupted-session cleanup with the gated live-cluster v4 trial."""
from project_console import console_session,status,log as print
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile
from finish_live_session import session_metadata
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 source,original,state,manifest=session_metadata(ROOT)
 status('Building and checking live-cluster v4.')
 v=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/package_live_cluster.py')],capture_output=True,text=True)
 if v.returncode:raise ValueError(v.stdout[-3000:]+v.stderr[-10000:])
 base=ROOT/'native/cluster-bridge/live-output'
 with zipfile.ZipFile(base/'live-cluster-v4-laptop.zip') as z:entries={n:z.read(n) for n in z.namelist()}
 if 'scripts/finish_live_session.py' not in entries:raise ValueError('Cleanup dependency missing')
 prefix='delphi-dump/'+source.name+'/'
 for name in ('disconnect-summary.json','live-bridge-summary.json','live-release-manifest.json','nav-controller-final.bin','nav-controller-pending.bin'):
  p=source/name
  if p.is_file():entries[prefix+name]=p.read_bytes()
 entries['README.txt']=b'''FINISH PRIOR SESSION + LIVE CLUSTER v4
====================================
Extract the ENTIRE ZIP into a fresh folder on the connected laptop.
Park with ignition on, phone unplugged and Ethernet connected.
First run:
 python scripts/finish_live_session.py --run --phone-unplugged
This captures the interrupted v3 sender state and finishes its AA/Nav controllers.
It never starts video. If no controllers remain after a reboot, it only asks
whether factory maps work. No separate pin file is required.

Only after verified cleanup and working factory maps, run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
Select factory maps in the cluster at the confirmation prompt.
At CAPTURE READY swap Ethernet for the phone, start a Google Maps route and
watch for about 12 seconds of live updates. Unplug phone, reconnect Ethernet,
then complete PHONE REMOVED cleanup and the on-screen questions.

v4 keeps factory video passing through while waiting for the phone. It binds
and verifies the reader before handoff, caches the first complete codec/keyframe,
and only then takes over the existing cluster transport. No empty replacement
stream is sent while waiting. Failures now preserve the native error and metrics.

If the finish step fails, stop and return its results; do not start the trial.
Return entire delphi-dump/_live_finish_* and _disconnect_observer_* folders.
Local Python, portable-bundle and QNX fixture checks pass. Actual live cluster
video and restoration of the combined trial still need on-car verification.
'''
 bundle=base/'live-finish-and-cluster-v4-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(entries.items()):z.writestr(n,b)
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp)
  with zipfile.ZipFile(bundle) as z:
   if z.testzip():raise ValueError('Bundle CRC failed')
   z.extractall(root)
  for script,flags in (('finish_live_session.py',[]),('run_disconnected_observer.py',['--live-cluster'])):
   v=subprocess.run([sys.executable,'-S','-B',str(root/'scripts'/script),*flags],cwd=root,capture_output=True,text=True)
   if v.returncode or 'Plan only' not in v.stdout:raise ValueError('Portable plan '+script+v.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));from finish_live_session import session_metadata;print(session_metadata(Path(sys.argv[1]))[1]['remote_directory'])"
  v=subprocess.run([sys.executable,'-S','-B','-c',code,str(root)],cwd=root,capture_output=True,text=True)
  if v.returncode or v.stdout.strip()!=original['remote_directory'] or (root/'live-failure-pin.json').exists():raise ValueError('Portable previous-session identity '+v.stderr)
  for manifest_path in ('native/cluster-bridge/live-output/release/manifest.json','native/cluster-bridge/keyframe-probe/release/manifest.json'):
   p=root/manifest_path;m=json.loads(p.read_text())
   for n,e in m['files'].items():
    b=(p.parent/n).read_bytes()
    if len(b)!=e['bytes'] or sha(b)!=e['sha256']:raise ValueError('Packaged payload hash '+n)
   for n,digest in m['scripts_sha256'].items():
    if sha((root/'scripts'/n).read_bytes())!=digest:raise ValueError('Packaged script hash '+n)
 review=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),source_session=source.name,previous_session_identity_passed=True,portable_plans_passed=True,payload_script_hashes_passed=True,on_car_test_needed=True)
 (base/'finish-release-review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
