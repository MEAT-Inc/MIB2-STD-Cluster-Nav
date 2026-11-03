"""Release the gated secondary endpoint negotiation experiment after offboard checks."""
from project_console import console_session, log as print
import hashlib,io,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'native/secondary-display'
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
def sha(b):return hashlib.sha256(b).hexdigest()
def main(preflight=False):
 release_base=ROOT/'native/cluster-bridge' if preflight else BASE
 q=(BASE/'qemu/qemu.log').read_text(errors='replace')
 for marker in ('ENDPOINT_FACTORY_QNX_TRIGGER_PASS','ENDPOINT_FACTORY_QNX_CALLBACK_ABI_PASS','ENDPOINT_FACTORY_QNX_OWNERSHIP_FAILURE_PASS cases=9','wire fixtures passed','SECONDARY_RUNTIME_QNX_PASS','SECONDARY_DISCOVERY_TRANSACTION_QNX_PASS','SECONDARY_HOOK_FORWARD_QNX_PASS','SECONDARY_TEST_RUNNER_PASS','DELPHI_SMOKE_PASS mode=baseline calls=9 registers_stack_errno_return=pass','DELPHI_SMOKE_PASS mode=observed calls=9 registers_stack_errno_return=pass','DELPHI_SMOKE_QNX_SUITE_PASS','DELPHI_SMOKE_QNX_END'):
  if marker not in q:raise ValueError('Missing offboard gate: '+marker)
 tested={r.split()[1]:r.split()[0] for r in (BASE/'qemu/secondary-tested.sha256').read_text().splitlines()}
 for name in ('libdelphi_observer.so','wire_fixture','runtime_fixture','transaction_fixture','secondary_forward_fixture'):
  if sha((BASE/'build'/name).read_bytes())!=tested.get(name):raise ValueError('QNX-tested artifact changed: '+name)
 hardware=json.loads((ROOT/'delphi-analysis/control-runtime/endpoint-factory-hardware-review.json').read_text())
 if not hardware.get('native_constructors_and_ownership_verified') or not hardware.get('primary_unchanged') or not hardware.get('router_table_unchanged'):raise ValueError('Native constructor prerequisites not reviewed')
 controller=(ROOT/'native/observer/disconnect-launch/build/observer_launch').read_bytes()
 if sha(controller)!='980107c5d5de2558375fd5e51583e266bfaafc9ed510e70cd581af7e5d8419ae':raise ValueError('Tested disconnected controller changed')
 b=(BASE/'build/libdelphi_observer.so').read_bytes();e=ELFFile(io.BytesIO(b));needs=[];imports=[];exports=[]
 if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or not 0<len(b)<=131072:raise ValueError('Wrong ARM ABI/size')
 for seg in e.iter_segments():
  if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1:raise ValueError('Executable stack')
  if seg['p_type']=='PT_DYNAMIC':needs=[t.needed for t in seg.iter_tags() if t.entry.d_tag=='DT_NEEDED']
 for s in e.get_section_by_name('.dynsym').iter_symbols():
  if s['st_info']['bind']=='STB_GLOBAL':
   if s['st_shndx']=='SHN_UNDEF':imports.append(s.name)
   elif s['st_info']['type']=='STT_FUNC':exports.append(s.name)
 libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
 if needs!=['libc.so.3'] or set(imports)-libc:raise ValueError('Unverified runtime dependency/import: '+repr(set(imports)-libc))
 expected={'_init','_fini','_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase','delphi_observer_view','_ZN13MessageRouter32populateServiceDiscoveryResponseEP24ServiceDiscoveryResponse','_ZN13MessageRouter13queueOutgoingEhPvj'}
 if set(exports)!=expected:raise ValueError('Unexpected exported hooks: '+repr(exports))
 scripts=('secondary_timing.py','cluster_preflight.py','run_disconnected_observer.py','run_androidauto_observer.py','run_observer_smoke.py','delphi_inventory.py','project_console.py','decode_delphi_observer.py')
 tests=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_disconnected_observer.py')],cwd=ROOT,capture_output=True,text=True)
 if tests.returncode:raise ValueError('Workflow/report tests failed: '+tests.stdout+tests.stderr)
 source_files=[p for p in BASE.glob('*.[ch]')]+[ROOT/'native/endpoint-factory'/n for n in ('factory.c','factory.h','probe.c','probe.h','profile.h')]
 manifest=dict(kind='disconnected_observer_control_trial',experiment='secondary_endpoint_negotiation',capture_profiles=[20],phone_trial_enabled=True,factory_report_version=2,factory_contract_revision=4,secondary_stream_enabled=True,secondary_hardware_tested=False,cluster_transport_connected=False,video_service_id=9,input_service_id=10,display_id=1,capture_byte_limit=8388608,needed=needs,imports=sorted(imports),exports=sorted(exports),source_sha256={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in source_files},scripts_sha256={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts})
 blobs={'observer_launch':controller,'libdelphi_observer.so':b}
 if preflight:
  helper=(release_base/'build/nav_snapshot').read_bytes()
  if sha(helper)!=(release_base/'nav-snapshot-tested.sha256').read_text().split()[0] or 'NAV_SNAPSHOT_QNX_PASS' not in q:raise ValueError('Untested read-only helper')
  e=ELFFile(io.BytesIO(helper));symbols=list(e.get_section_by_name('.dynsym').iter_symbols());names={v.name for v in symbols if v.name and v['st_shndx']=='SHN_UNDEF' and v['st_info']['bind']=='STB_GLOBAL'};weak={v.name for v in symbols if v.name and v['st_shndx']=='SHN_UNDEF' and v['st_info']['bind']=='STB_WEAK'}
  if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or names-libc or weak-libc-{'__register_frame_info','__deregister_frame_info'} or names.intersection({'kill','pwrite','pwrite64','ptrace','spawn','spawnp','execv','system'}):raise ValueError('Snapshot helper ABI/imports differ: '+repr(names-libc))
  for seg in e.iter_segments():
   if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1:raise ValueError('Snapshot executable stack')
  helper_needs=[t.needed for seg in e.iter_segments() if seg['p_type']=='PT_DYNAMIC' for t in seg.iter_tags() if t.entry.d_tag=='DT_NEEDED']
  if helper_needs!=['libc.so.3'] or not 0<len(helper)<=131072:raise ValueError('Snapshot dependency/size differs')
  mux_tests=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_cluster_ts_mux.py')],cwd=ROOT,capture_output=True,text=True)
  if mux_tests.returncode:raise ValueError('Offline mux tests failed: '+mux_tests.stderr)
  video=json.loads((ROOT/'delphi-analysis/cluster-bridge/video-review/video-review.json').read_text())
  if video['decoded_frames']!=371 or not video['offline_remux']['decoded_pixels_identical'] or video['mux_source_sha256']!=sha((ROOT/'scripts/cluster_ts_mux.py').read_bytes()):raise ValueError('Real-video offline mux check missing or stale')
  blobs['nav_snapshot']=helper;manifest.update(factory_contract_revision=5,timing_capture_version=1,native_geometry_readonly=True,navigation_server_restart=False,navigation_snapshot_hardware_tested=False,navigation_snapshot_imports=sorted(names),navigation_snapshot_optional_weak_imports=sorted(weak))
  manifest['source_sha256']['native/cluster-bridge/nav_snapshot.c']=sha((release_base/'nav_snapshot.c').read_bytes())
  manifest['source_sha256']['native/cluster-bridge/build.sh']=sha((release_base/'build.sh').read_bytes())
  manifest['source_sha256']['native/observer/launch/proc_guard.c']=sha((ROOT/'native/observer/launch/proc_guard.c').read_bytes())
 manifest['files']={n:dict(bytes=len(v),sha256=sha(v)) for n,v in blobs.items()}
 release=release_base/'release';release.mkdir(exist_ok=True)
 for n,v in blobs.items():(release/n).write_bytes(v)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(release_base/'README.txt',release/'README.txt')
 bundle=release_base/('cluster-preflight-laptop.zip' if preflight else 'secondary-stream-laptop.zip')
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n in scripts:z.write(ROOT/'scripts'/n,'scripts/'+n)
  for n in (*blobs,'manifest.json','README.txt'):z.write(release/n,(release/n).relative_to(ROOT).as_posix())
 with tempfile.TemporaryDirectory(prefix='secondary-portable-') as temp:
  p=Path(temp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  result=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_disconnected_observer.py'),('--cluster-preflight' if preflight else '--secondary-stream')],cwd=p,capture_output=True,text=True)
  if result.returncode or 'Plan only' not in result.stdout or (p/'delphi-dump').exists():raise ValueError('Portable plan failed: '+result.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_disconnected_observer as m;print(len(m.package(Path(sys.argv[1])/('native/cluster-bridge/release' if {preflight} else 'native/secondary-display/release'),phone=True,factory=True,secondary=True,cluster={preflight})))"
  code=code.format(preflight=preflight)
  result=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if result.returncode or result.stdout.strip()!=('3' if preflight else '2'):raise ValueError('Portable package assets/gates failed: '+result.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),python_tests=tests.stderr.strip(),portable_plan_passed=True,portable_manifest_passed=True,manifest=manifest)
 (ROOT/('delphi-analysis/control-runtime/cluster-preflight-release.json' if preflight else 'delphi-analysis/control-runtime/secondary-stream-release.json')).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        import argparse
        p=argparse.ArgumentParser();p.add_argument('--cluster-preflight',action='store_true');main(p.parse_args().cluster_preflight)
