"""Gate and package the isolated, unpublished endpoint factory trial."""
from project_console import console_session, log as print
import hashlib,io,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'native/endpoint-factory'
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 q=(BASE/'qemu/qemu.log').read_text(errors='replace')
 for marker in ('ENDPOINT_FACTORY_QNX_TRIGGER_PASS','ENDPOINT_FACTORY_QNX_CALLBACK_ABI_PASS','ENDPOINT_FACTORY_QNX_OWNERSHIP_FAILURE_PASS cases=9','Process 3 (factory_fixture) exited status=0.','DELPHI_SMOKE_PASS mode=baseline calls=9 registers_stack_errno_return=pass','DELPHI_SMOKE_PASS mode=observed calls=9 registers_stack_errno_return=pass','DELPHI_SMOKE_QNX_SUITE_PASS','DELPHI_SMOKE_QNX_END'):
  if marker not in q:raise ValueError('Missing native test: '+marker)
 tested={r.split()[1]:r.split()[0] for r in (BASE/'qemu/factory-tested.sha256').read_text().splitlines()}
 for name in ('factory_fixture','libdelphi_observer.so'):
  if sha((BASE/'build'/name).read_bytes())!=tested.get(name):raise ValueError('Native artifact differs from QNX tested binary')
 hardware=json.loads((ROOT/'delphi-analysis/control-runtime/observer-phone-hardware-review.json').read_text())
 if not hardware.get('phone_session_trial_passed') or hardware.get('registrations')!=9 or hardware.get('dropped') or not hardware.get('assessment',{}).get('capture_validated'):raise ValueError('Safe phone-session gate not passed')
 controller=ROOT/'native/observer/disconnect-launch/build/observer_launch'
 if sha(controller.read_bytes())!='980107c5d5de2558375fd5e51583e266bfaafc9ed510e70cd581af7e5d8419ae':raise ValueError('Tested disconnected controller changed')
 b=(BASE/'build/libdelphi_observer.so').read_bytes();e=ELFFile(io.BytesIO(b));needs=[];imports=[];exports=[]
 if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or not 0<len(b)<=131072:raise ValueError('Wrong ABI/size')
 for seg in e.iter_segments():
  if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1:raise ValueError('Executable stack')
  if seg['p_type']=='PT_DYNAMIC':needs=[t.needed for t in seg.iter_tags() if t.entry.d_tag=='DT_NEEDED']
 for s in e.get_section_by_name('.dynsym').iter_symbols():
  if s['st_info']['bind']=='STB_GLOBAL':
   if s['st_shndx']=='SHN_UNDEF':imports.append(s.name)
   elif s['st_info']['type']=='STT_FUNC':exports.append(s.name)
 libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
 if needs!=['libc.so.3'] or set(imports)-libc:raise ValueError('Unverified runtime dependency/import')
 if set(exports)!={'_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase','delphi_observer_view','_init','_fini'}:raise ValueError('Unexpected exported hooks: '+repr(exports))
 scripts=('run_disconnected_observer.py','run_androidauto_observer.py','run_observer_smoke.py','delphi_inventory.py','project_console.py','decode_delphi_observer.py')
 tests=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_disconnected_observer.py')],cwd=ROOT,capture_output=True,text=True)
 if tests.returncode:raise ValueError('Workflow tests failed: '+tests.stdout+tests.stderr)
 release=BASE/'release';release.mkdir(exist_ok=True)
 blobs={'observer_launch':controller.read_bytes(),'libdelphi_observer.so':b}
 manifest=dict(kind='disconnected_observer_control_trial',experiment='isolated_endpoint_factory_probe',capture_profiles=[20],factory_report_version=2,factory_contract_revision=4,combined_callback_probe=True,phone_trial_enabled=True,factory_probe_hardware_tested=False,secondary_endpoints_registered=False,discovery_changed=False,files={n:dict(bytes=len(v),sha256=sha(v)) for n,v in blobs.items()},needed=needs,imports=sorted(imports),exports=sorted(exports),native_qnx_tested=True,controller_sha256=sha(controller.read_bytes()),phone_baseline_review_sha256=sha((ROOT/'delphi-analysis/control-runtime/observer-phone-hardware-review.json').read_bytes()),source_sha256={n:sha((BASE/n).read_bytes()) for n in ('factory.c','factory.h','probe.c','probe.h','profile.h')},scripts_sha256={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts})
 for n,v in blobs.items():(release/n).write_bytes(v)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(BASE/'README.txt',release/'README.txt')
 bundle=BASE/'endpoint-factory-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n in scripts:z.write(ROOT/'scripts'/n,'scripts/'+n)
  for n in (*blobs,'manifest.json','README.txt'):z.write(release/n,(release/n).relative_to(ROOT).as_posix())
 with tempfile.TemporaryDirectory(prefix='factory-portable-') as temp:
  p=Path(temp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  result=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_disconnected_observer.py'),'--phone-capture','--factory-probe'],cwd=p,capture_output=True,text=True)
  if result.returncode or 'Plan only' not in result.stdout or (p/'delphi-dump').exists():raise ValueError('Portable offline plan failed')
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_disconnected_observer as m;print(len(m.package(Path(sys.argv[1])/'native/endpoint-factory/release',phone=True,factory=True)))"
  result=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if result.returncode or result.stdout.strip()!='2':raise ValueError('Portable factory assets/gate failed: '+result.stderr)
 report=dict(bundle=str(bundle.relative_to(ROOT)),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),python_tests=tests.stderr.strip(),portable_plan_passed=True,portable_manifest_passed=True,manifest=manifest)
 (ROOT/'delphi-analysis/control-runtime/endpoint-factory-release.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
