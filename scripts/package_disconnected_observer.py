"""Package the Ethernet-only controller trial after native and portable gates."""
from project_console import console_session, log as print
import hashlib,io,json,shutil,struct,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
BASE=ROOT/'native/observer/disconnect-launch'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 q=(BASE/'qemu/qemu.log').read_text(errors='replace')
 markers=('DISCONNECT_PENDING_NO_SIGNAL_PASS','DISCONNECT_STATE_MISMATCH_REFUSED','DISCONNECT_LOCK_REFUSED','DISCONNECT_LATE_CLEANUP_PASS','DISCONNECT_IDEMPOTENT_PASS','DISCONNECT_ORPHAN_PENDING_PASS','DISCONNECT_ORPHAN_CLEANUP_PASS','DISCONNECT_QNX_SUITE_PASS','DISCONNECT_QNX_END','Process 3 (launch_qemu_runner) exited status=0.')
 if any(x not in q for x in markers):raise ValueError('Native lifecycle tests incomplete')
 tested={row.split()[1]:row.split()[0] for row in (BASE/'qemu/tested.sha256').read_text().splitlines()}
 blobs={'observer_launch':(BASE/'build/observer_launch').read_bytes(),'libdelphi_observer.so':(ROOT/'native/observer/release/libdelphi_observer.so').read_bytes()}
 if sha(blobs['libdelphi_observer.so'])!='cc425ccdc1a889caa2b4128a0a55f07cc8b26679065d7e293b274b80e83ad70c':raise ValueError('Original observer changed')
 libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
 assets={}
 for name,b in blobs.items():
  if sha(b)!=tested.get(name):raise ValueError('Native binary differs from QNX tested artifact: '+name)
  e=ELFFile(io.BytesIO(b));needs=[];imports=[]
  if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or not 0<len(b)<=131072:raise ValueError('Wrong ARM ABI/size')
  for seg in e.iter_segments():
   if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1:raise ValueError('Executable stack')
   if seg['p_type']=='PT_DYNAMIC':needs=[t.needed for t in seg.iter_tags() if t.entry.d_tag=='DT_NEEDED']
  for s in e.get_section_by_name('.dynsym').iter_symbols():
   if s['st_shndx']=='SHN_UNDEF' and s['st_info']['bind']=='STB_GLOBAL':imports.append(s.name)
  if needs!=['libc.so.3'] or set(imports)-libc:raise ValueError('Unverified runtime imports: '+name+' '+repr(set(imports)-libc))
  assets[name]=dict(bytes=len(b),sha256=sha(b),needed=needs,imports=sorted(imports))
 states={}
 for prefix,seconds in (('DISCONNECT',20),('DISCONNECT_ORPHAN',60)):
  pair=[]
  for stage in ('PENDING','FINAL'):
   lines=[s.split()[1] for s in q.splitlines() if s.startswith(prefix+'_'+stage+'_HEX ')]
   if len(lines)!=1:raise ValueError('Missing or ambiguous native state')
   b=bytes.fromhex(lines[0]);h=struct.unpack_from('<16I',b);flags=struct.unpack_from('<4I',b,256)
   if len(b)!=512 or h[:3]!=(0x314c4144,3,512) or h[4]!=0 or h[15]!=1 or any(b[272:]) or flags!=(seconds,1,int(stage=='FINAL'),int(stage=='FINAL')):raise ValueError('Invalid capture/cleanup state')
   if stage=='PENDING' and (h[3]!=4 or h[9] or h[11]):raise ValueError('Expiry unexpectedly restored/signaled')
   if stage=='FINAL' and (h[3]!=6 or h[9]!=1 or not h[11] or h[10]==h[11]):raise ValueError('Cleanup restoration not verified')
   states[prefix+'_'+stage]=dict(phase=h[3],observed_pid=h[10],restored_pid=h[11],capture_seconds=seconds,cleanup_authorized=flags[2],sha256=sha(b));pair.append(b)
  if pair[0][40:44]!=pair[1][40:44] or pair[0][64:88]!=pair[1][64:88] or pair[0][96:224]!=pair[1][96:224]:raise ValueError('Cleanup changed original process identity')
 scripts=('run_disconnected_observer.py','run_androidauto_observer.py','run_observer_smoke.py','delphi_inventory.py','project_console.py','decode_delphi_observer.py')
 check=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_disconnected_observer.py')],cwd=ROOT,capture_output=True,text=True)
 if check.returncode:raise ValueError('Python lifecycle regression failed: '+check.stdout+check.stderr)
 hardware=json.loads((ROOT/'delphi-analysis/control-runtime/disconnected-controller-hardware-review.json').read_text())
 if hardware.get('actual_unit_disconnected_controller_validated') is not True or hardware.get('native_sha256')!=sha(blobs['observer_launch']) or hardware['assessment'].get('controller_trial_passed') is not True or hardware['pending'].get('cleanup_authorized')!=0:raise ValueError('Actual-unit disconnected controller gate not cleared')
 release=BASE/'release';release.mkdir(exist_ok=True)
 manifest=dict(kind='disconnected_observer_control_trial',protocol_version=3,files=assets,hardware_tested=True,hardware_validation_scope="disconnected_20s_control_only",hardware_review_sha256=sha((ROOT/'delphi-analysis/control-runtime/disconnected-controller-hardware-review.json').read_bytes()),capture_seconds=20,capture_profiles=[20,60],phone_trial_enabled=True,phone_session_hardware_tested=False,expiry_signals_observed=False,cleanup_requires_explicit_disconnected_command=True,qnx_synthetic_lifecycle_passed=True,native_states=states,scripts_sha256={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts})
 for n,b in blobs.items():(release/n).write_bytes(b)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2))
 shutil.copy2(BASE/'README.txt',release/'README.txt')
 bundle=BASE/'disconnected-controller-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n in scripts:z.write(ROOT/'scripts'/n,'scripts/'+n)
  for n in (*blobs,'manifest.json','README.txt'):z.write(release/n,(release/n).relative_to(ROOT).as_posix())
 with tempfile.TemporaryDirectory(prefix='disconnect-portable-') as t:
  folder=Path(t)
  with zipfile.ZipFile(bundle) as z:z.extractall(folder)
  for args in ([],['--phone-capture']):
   result=subprocess.run([sys.executable,'-S','-B',str(folder/'scripts/run_disconnected_observer.py'),*args],cwd=folder,capture_output=True,text=True)
   if result.returncode or 'Plan only' not in result.stdout or (folder/'delphi-dump').exists():raise ValueError('Portable offline plan failed: '+result.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_disconnected_observer as m;print(len(m.package(Path(sys.argv[1])/'native/observer/disconnect-launch/release',phone=True)))"
  result=subprocess.run([sys.executable,'-S','-B','-c',code,str(folder)],cwd=folder,capture_output=True,text=True)
  if result.returncode or result.stdout.strip()!='2':raise ValueError('Portable manifest check failed: '+result.stderr)
 report=dict(bundle=str(bundle.relative_to(ROOT)),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),portable_plan_passed=True,portable_manifest_passed=True,python_tests=check.stderr.strip(),manifest=manifest)
 (ROOT/'delphi-analysis/control-runtime/disconnected-controller-release.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
