"""Build the separate read-only startup-evidence laptop bundle."""
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tempfile,zipfile
from project_console import console_session,log as print
ROOT=Path(__file__).resolve().parents[1]
def main():
 names={'collect_cluster_deployment.py'}
 while True:
  added=set()
  for name in names:
   for n in ast.walk(ast.parse((ROOT/'scripts'/name).read_text())):
    imports=[x.name for x in n.names] if isinstance(n,ast.Import) else [n.module] if isinstance(n,ast.ImportFrom) else []
    for module in imports:
     f=(module or '').split('.')[0]+'.py'
     if (ROOT/'scripts'/f).is_file():added.add(f)
  if added<=names:break
  names|=added
 readme='''READ-ONLY CLUSTER STARTUP PREFLIGHT
==================================
Extract into a fresh laptop folder. Park, radio on, Ethernet connected. Run:
 python scripts/collect_cluster_deployment.py --run
This reads currentrunHMI.sh,procmanconfig,mounts and path metadata. No observed
app is restarted, no preload/alias is installed, and no radio file is changed.
Missing paths are recorded. Return the whole delphi-dump/_deployment_preflight_*
folder. This is separate from the extended live maps test and needs no cleanup.
'''
 out=ROOT/'native/cluster-bridge/deployment';out.mkdir(exist_ok=True)
 bundle=out/'startup-preflight-laptop.zip'
 hashes={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in names}
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('README.txt',readme);z.writestr('manifest.json',json.dumps(dict(read_only=True,scripts_sha256=hashes),indent=2))
  for n in sorted(names):z.write(ROOT/'scripts'/n,'scripts/'+n)
 with tempfile.TemporaryDirectory() as td:
  root=Path(td)
  with zipfile.ZipFile(bundle) as z:
   assert z.testzip() is None;z.extractall(root)
  v=subprocess.run([sys.executable,'-S','-B',str(root/'scripts/collect_cluster_deployment.py')],cwd=root,capture_output=True,text=True)
  if v.returncode or 'Plan only' not in v.stdout or (root/'delphi-dump').exists():raise ValueError('Read-only portable plan failed '+v.stderr)
 print(json.dumps(dict(bundle=str(bundle),bytes=bundle.stat().st_size,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),portable_readonly_plan_passed=True),indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
