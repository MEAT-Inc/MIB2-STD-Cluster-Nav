"""Package the standard-library-only read-only map-session collector."""
from project_console import console_session, log as print
import hashlib,json,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'native/cluster-bridge/map-session'
def main():
 t=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_collect_map_session.py')],cwd=ROOT,capture_output=True,text=True)
 if t.returncode:raise RuntimeError(t.stderr)
 files={('scripts/'+n):(ROOT/'scripts'/n).read_bytes() for n in ('collect_map_session.py','run_observer_smoke.py','delphi_inventory.py','project_console.py','decode_delphi_observer.py')};files['README.txt']=(OUT/'README.txt').read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();manifest=dict(kind='readonly_map_session_snapshot',service_restarts=False,preload=False,video_writes=False,files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()});files['manifest.json']=json.dumps(manifest,indent=2).encode();bundle=OUT/'map-session-diagnostics-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  for n,v in manifest['files'].items():
   b=(p/n).read_bytes()
   if len(b)!=v['bytes'] or sha(b)!=v['sha256']:raise ValueError('Extracted hash mismatch')
  r=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/collect_map_session.py')],cwd=p,capture_output=True,text=True)
  if r.returncode or 'Plan only' not in r.stdout or (p/'delphi-dump').exists():raise ValueError('Portable nonconnecting plan failed: '+r.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),workflow_tests=t.stderr.strip(),portable_plan_passed=True,manifest=manifest);(OUT/'release-review.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
