"""Package guarded crash recovery and the corrected live-cluster trial."""
from project_console import console_session,status,log as print
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
from package_cluster_replay import elf_gate
from collect_live_failure import load_session_identity
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 pin,source,old_manifest=load_session_identity(ROOT)
 # Preserve verified provenance before rebuilding the current live release.
 snapshot=source/'live-release-manifest.json'
 if not snapshot.exists():snapshot.write_bytes(old_manifest)
 base=ROOT/'native/cluster-bridge/recovery';release=base/'release';release.mkdir(parents=True,exist_ok=True);files={};elf={}
 for name,folder,source_name,markers in (('nav_cycle',ROOT/'native/cluster-bridge/nav-control','nav_cycle',('NAV_LIVE_STALL_CAPTURE_GUARD_PASS','NAV_RECOVER_HEALTHY_REFUSAL_PASS','NAV_RECOVER_STALE_REFUSAL_PASS','NAV_RECOVER_FACTORY_AUTORESTART_PASS')),('nav_finalize',ROOT/'native/cluster-bridge/nav-launch','nav_launch',('NAV_FINALIZE_ALIVE_REFUSAL_PASS','NAV_FINALIZE_STALE_REFUSAL_PASS','NAV_FINALIZE_RECOVERED_PASS'))):
  log=(folder/'qemu/qemu.log').read_text();tested={Path(x.split()[1]).name:x.split()[0] for x in (folder/'qemu/tested.sha256').read_text().splitlines()};b,meta=elf_gate(folder/'build'/source_name)
  if tested.get(source_name)!=sha(b) or not all(x in log for x in markers):raise ValueError('Recovery QNX gates failed '+name)
  if b'recover-fixture' in b or b'NAV_PREEXEC_CANONICAL_RACE_PROVEN' in b:raise ValueError('Test profile in production helper')
  files[name]=b;elf[name]=meta
 for n,b in files.items():(release/n).write_bytes(b)
 manifest=dict(kind='exact_crash_nav_recovery',on_car_tested=False,files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()},elf=elf,crash_guard='MU0890 recorded NavMain allocator SIGSEGV; mutex owner and exact frame rechecked twice',captured_variants=3,finalization='no signals; new canonical factory instance required; separate immutable recovered report',source_sha256={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for folder in (ROOT/'native/cluster-bridge/nav-control',ROOT/'native/cluster-bridge/nav-launch') for p in folder.iterdir() if p.suffix in ('.c','.h','.sh')})
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2))
 for test in ('test_recover_live_failure.py','test_live_cluster_bridge.py','test_collect_live_failure.py'):
  status('Running '+test);v=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests'/test)],capture_output=True,text=True)
  if v.returncode:raise ValueError(v.stdout[-2000:]+v.stderr[-10000:])
 status('Building corrected live-cluster v3 bundle.')
 v=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/package_live_cluster.py')],capture_output=True,text=True)
 if v.returncode:raise ValueError(v.stdout[-3000:]+v.stderr[-10000:])
 names={'recover_live_failure.py'}
 while True:
  added=set()
  for n in names:
   for node in ast.walk(ast.parse((ROOT/'scripts'/n).read_text())):
    modules=[q.name for q in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) else []
    for q in modules:
     name=(q or '').split('.')[0]+'.py'
     if (ROOT/'scripts'/name).is_file():added.add(name)
  if added<=names:break
  names|=added
 live=ROOT/'native/cluster-bridge/live-output/live-cluster-v3-laptop.zip';entries={}
 with zipfile.ZipFile(live) as z:
  for n in z.namelist():entries[n]=z.read(n)
 for n in names:entries['scripts/'+n]=(ROOT/'scripts'/n).read_bytes()
 for n in (*files,'manifest.json'):entries[(release/n).relative_to(ROOT).as_posix()]=(release/n).read_bytes()
 archive='delphi-dump/'+source.name+'/'
 for n in ('disconnect-summary.json','live-bridge-summary.json','nav-controller-final.bin','nav-controller-pending.bin'):
  if (source/n).is_file():entries[archive+n]=(source/n).read_bytes()
 entries[archive+'live-release-manifest.json']=old_manifest
 entries['README.txt']=b"""GUARDED RECOVERY + LIVE CLUSTER v3
=================================
Keep the radio in its current stuck state, phone unplugged and Ethernet connected.
Extract the ENTIRE ZIP into a fresh folder. No separate pin file is needed.
First run:
 python scripts/recover_live_failure.py --run --phone-unplugged
This checks the saved session and exact recorded SIGSEGV twice, then terminates
only that already-faulted Nav process so the factory manager can restart it.
The controller is finalized only after a different canonical factory process
is verified. The original failure record is preserved.

Only if recovery reports verified restoration AND factory maps work, run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
Confirm factory maps in the cluster at the arm prompt. At CAPTURE READY connect
the phone, start a Google Maps route and watch about12 seconds of live cluster
updates. Unplug phone, reconnect Ethernet, and complete PHONE REMOVED cleanup.

If recovery refuses or maps remain unavailable, do not start the live trial.
Return all new delphi-dump/_live_recovery_* and _disconnect_observer_* folders.
The native guard, finalization and laptop checks passed locally/QNX. Recovery
of this current fault and the live picture still require on-car verification.
"""
 bundle=base/'live-recovery-and-cluster-v3-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for name,b in sorted(entries.items()):z.writestr(name,b)
 with tempfile.TemporaryDirectory() as t:
  root=Path(t)
  with zipfile.ZipFile(bundle) as z:z.extractall(root)
  for script,flags in (('recover_live_failure.py',[]),('run_disconnected_observer.py',['--live-cluster'])):
   v=subprocess.run([sys.executable,'-S','-B',str(root/'scripts'/script),*flags],cwd=root,capture_output=True,text=True)
   if v.returncode or 'Plan only' not in v.stdout:raise ValueError('Portable plan '+script+v.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));from collect_live_failure import load_session_identity;print(load_session_identity(Path(sys.argv[1]))[0]['pid'])"
  v=subprocess.run([sys.executable,'-S','-B','-c',code,str(root)],cwd=root,capture_output=True,text=True)
  if v.returncode or v.stdout.strip()!=str(pin['pid']) or (root/'live-failure-pin.json').exists():raise ValueError('Portable prior-session identity '+v.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),qnx_crash_guard_passed=True,qnx_finalization_passed=True,host_recovery_tests_passed=True,portable_plans_passed=True,previous_session_identity_passed=True,on_car_recovery_test_needed=True)
 (base/'release-review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
