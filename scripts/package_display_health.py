"""Build the standard-library-only read-only laptop diagnostics package."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
NAMES=('collect_display_health.py','collect_trace_snapshot.py','collect_trace_tcp.py','collect_observer_preflight.py','delphi_inventory.py','run_androidauto_observer.py','run_observer_smoke.py','decode_delphi_observer.py','decode_androidauto_display.py','DISPLAY-HEALTH-DIAGNOSTICS.txt')
def main():
    bundle=ROOT/'native/observer/display/black-screen-diagnostics-laptop.zip'
    if b'LIVE_EXPERIMENT_HOLD=True' not in (ROOT/'scripts/run_androidauto_observer.py').read_bytes():raise ValueError('Disruptive experiment hold is not enabled')
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for name in NAMES:z.write(ROOT/'scripts'/name,'scripts/'+name)
    with tempfile.TemporaryDirectory(prefix='delphi-health-package-') as temp:
        folder=Path(temp)
        with zipfile.ZipFile(bundle) as z:
            if len(z.namelist())!=len(NAMES):raise ValueError('Incorrect package contents')
            z.extractall(folder)
        for name in ('collect_display_health.py','collect_trace_snapshot.py','collect_trace_tcp.py'):
            script=folder/'scripts'/name
            result=subprocess.run([sys.executable,'-S','-B',str(script)],cwd=folder,capture_output=True,text=True)
            if result.returncode or 'Plan only' not in result.stdout or (folder/'delphi-dump').exists():raise ValueError('Portable offline plan failed: '+result.stderr)
        for args in (['--run'],['--run','--phone-capture','--display-capture']):
            result=subprocess.run([sys.executable,'-S','-B',str(folder/'scripts/run_androidauto_observer.py'),*args],cwd=folder,capture_output=True,text=True)
            if result.returncode!=2 or 'disabled' not in result.stderr or (folder/'delphi-dump').exists():raise ValueError('Live hold failed')
    report=dict(bundle=str(bundle.relative_to(ROOT)),bytes=bundle.stat().st_size,sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),portable_plan_passed=True,live_restart_blocked=True,contains_native_programs=False)
    (ROOT/'delphi-analysis/control-runtime/display-health-laptop-package-review.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
