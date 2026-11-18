"""Package a read-only capture pinned to the failed live-output run."""
from project_console import console_session,status,log as print
from pathlib import Path
import ast,hashlib,json,struct,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
def main():
 from collect_live_failure import load_session_identity
 pin,source,manifest_bytes=load_session_identity(ROOT)
 for name in ('test_live_cluster_bridge.py','test_collect_live_failure.py','test_disconnected_observer.py'):
  status('Running '+name);v=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests'/name)],capture_output=True,text=True)
  if v.returncode:raise ValueError(v.stdout[-3000:]+v.stderr[-10000:])
 names={'collect_live_failure.py'}
 while True:
  added=set()
  for name in names:
   for x in ast.walk(ast.parse((ROOT/'scripts'/name).read_text())):
    modules=[q.name for q in x.names] if isinstance(x,ast.Import) else [x.module] if isinstance(x,ast.ImportFrom) else []
    for q in modules:
     n=(q or '').split('.')[0]+'.py'
     if (ROOT/'scripts'/n).is_file():added.add(n)
  if added<=names:break
  names|=added
 base=ROOT/'native/cluster-bridge/live-output';bundle=base/'live-failure-capture-laptop.zip'
 readme="""SESSION-BASED LIVE NAV FAILURE CAPTURE
===============================
Leave the radio in the current stuck state; do not reboot or rerun playback.
Keep phone unplugged, Ethernet connected, ignition on. Extract the entire ZIP.
The collector uses the latest previous live-output folder under delphi-dump.
This bundle includes the relevant saved session metadata, not a separate pin file.
Run:
 python scripts/collect_live_failure.py --run --phone-unplugged
To choose another previous result, append --session "delphi-dump/<folder>".
Return the entire delphi-dump/_live_failure_* folder.
This only copies existing logs and reads the pinned Nav threads and stack pages.
It sends no signal, shutdown, restart or video; uploads no native binary.
It refuses memory queries if the pinned process or manager identity changed.
It verifies the existing nav_cycle binary before invoking inspect/page only.
"""
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('README.txt',readme)
  archive='delphi-dump/'+source.name+'/'
  for name in ('disconnect-summary.json','live-bridge-summary.json','nav-controller-final.bin','nav-controller-pending.bin'):
   if (source/name).is_file():z.write(source/name,archive+name)
  z.writestr(archive+'live-release-manifest.json',manifest_bytes)
  for name in sorted(names):z.write(ROOT/'scripts'/name,'scripts/'+name)
 with tempfile.TemporaryDirectory() as t:
  root=Path(t)
  with zipfile.ZipFile(bundle) as z:z.extractall(root)
  v=subprocess.run([sys.executable,'-S','-B',str(root/'scripts/collect_live_failure.py')],cwd=root,capture_output=True,text=True)
  if v.returncode or 'Plan only' not in v.stdout or list((root/'delphi-dump').glob('_live_failure_*')):raise ValueError('Portable read-only plan failed '+v.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));from collect_live_failure import load_session_identity;print(load_session_identity(Path(sys.argv[1]))[0]['pid'])"
  v=subprocess.run([sys.executable,'-S','-B','-c',code,str(root)],cwd=root,capture_output=True,text=True)
  if v.returncode or v.stdout.strip()!=str(pin['pid']) or (root/'live-failure-pin.json').exists():raise ValueError('Portable prior-session resolution failed '+v.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),session_source=source.name,pin=pin,requires_pin_file=False,portable_session_resolution_passed=True,startup_race_regression_passed=True,readonly_collector_tests_passed=True,portable_plan_passed=True,vehicle_capture_needed=True)
 (base/'failure-capture-release.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
