"""Package the bounded live-input/phone-keyframe test after QNX and host gates."""
from project_console import console_session,log as print,status
from pathlib import Path
import hashlib,io,json,re,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 base=ROOT/'native/cluster-bridge/keyframe-probe';release=base/'release';release.mkdir(parents=True,exist_ok=True)
 native=ROOT/'native/secondary-display';log=(native/'qemu/qemu.log').read_text()
 for marker in ('unknown_thread_target=1','native_projected_1_hmi_2=1','ROUTE_HOOK_QNX_PASS','ROUTE_POLICY_PRELOAD_FORWARD_PASS','ROUTE_POLICY_PRELOAD_RUNNER_PASS','ROUTE_POLICY_QNX_PASS','SECONDARY_KEYFRAME_PROBE_PASS','LIVE_CAPTURE_QNX_PASS','LIVE_CAPTURE_DELAY_POLICY_PASS','LIVE_MUX_QNX_PASS','NAV_TIMED_SNAPSHOT_QNX_PASS','SECONDARY_RUNTIME_QNX_PASS','SECONDARY_DISCOVERY_TRANSACTION_QNX_PASS','SECONDARY_HOOK_FORWARD_QNX_PASS','DELPHI_SMOKE_QNX_SUITE_PASS'):
  if marker not in log:raise ValueError('Missing native gate: '+marker)
 if 'LIVE_QUEUE_PROCESS_PASS' not in (ROOT/'native/cluster-bridge/live/qemu/qemu.log').read_text():raise ValueError('Live queue cross-process gate')
 checked={Path(line.split()[1]).name:line.split()[0] for line in (native/'qemu/keyframe-probe-tested.sha256').read_text().splitlines()}
 sources={'libdelphi_observer.so':native/'build/libdelphi_observer_keyframe.so','nav_snapshot':ROOT/'native/cluster-bridge/build/nav_snapshot_timed','live_capture':native/'build/live_capture'}
 files={}
 libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
 exports_expected={'SAL_Send','_init','_fini','_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase','delphi_observer_view','_ZN13MessageRouter32populateServiceDiscoveryResponseEP24ServiceDiscoveryResponse','_ZN13MessageRouter13queueOutgoingEhPvj'}
 for name,path in sources.items():
  b=path.read_bytes()
  if checked.get(path.name)!=sha(b):raise ValueError('Native gate hash changed '+name)
  e=ELFFile(io.BytesIO(b));needs=[t.needed for s in e.iter_segments() if s['p_type']=='PT_DYNAMIC' for t in s.iter_tags() if t.entry.d_tag=='DT_NEEDED']
  if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or not 0<len(b)<=131072 or needs!=['libc.so.3']:raise ValueError('Native ABI/dependencies '+name)
  symbols=list(e.get_section_by_name('.dynsym').iter_symbols());imports={s.name for s in symbols if s['st_shndx']=='SHN_UNDEF' and s['st_info']['bind']=='STB_GLOBAL'};weak={s.name for s in symbols if s['st_shndx']=='SHN_UNDEF' and s['st_info']['bind']=='STB_WEAK'}
  if imports-libc or weak-libc-{'__register_frame_info','__deregister_frame_info','_ITM_registerTMCloneTable','_ITM_deregisterTMCloneTable'} or imports.intersection({'kill','ptrace','pwrite','pwrite64','system'}):raise ValueError('Unverified/dangerous native imports '+name+str(dict(global_missing=sorted(imports-libc),weak_missing=sorted(weak-libc-{'__register_frame_info','__deregister_frame_info','_ITM_registerTMCloneTable','_ITM_deregisterTMCloneTable'}),forbidden=sorted(imports.intersection({'kill','ptrace','pwrite','pwrite64','system'})))))
  if any(s['p_type']=='PT_GNU_STACK' and s['p_flags']&1 for s in e.iter_segments()):raise ValueError('Executable stack')
  if name=='libdelphi_observer.so' and {s.name for s in symbols if s['st_info']['bind']=='STB_GLOBAL' and s['st_info']['type']=='STT_FUNC' and s['st_shndx']!='SHN_UNDEF'}!=exports_expected:raise ValueError('Observer exports changed')
  if name=='live_capture' and b'LIVE_CAPTURE_QNX_PASS' in b:raise ValueError('Capture test profile in release')
  files[name]=b
 original=ROOT/'native/cluster-bridge/release';manifest=json.loads((original/'manifest.json').read_text());files['observer_launch']=(original/'observer_launch').read_bytes()
 if sha(files['observer_launch'])!=manifest['files']['observer_launch']['sha256']:raise ValueError('Validated controller changed')
 for test in ('test_live_input.py','test_disconnected_observer.py'):
  status('Running '+test)
  result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests'/test)],cwd=ROOT,capture_output=True,text=True)
  if result.returncode:raise ValueError(result.stderr[-16000:])
 manifest.update(route_presentation_trial=True,route_presentation_hold_seconds=40,route_presentation_event=0x1749,route_native_projected=1,route_native_native=2,route_policy_report_version=2,route_phone_ack_helper=[0x1189e0,0x119840],route_presentation_extra_aa_threads_when_live=1,keyframe_probe_enabled=True,keyframe_probe_max_requests=0,focus_refresh_disabled=True,live_wait_for_first_frame_seconds=180,live_owned_frame_capture=True,live_queue_capacity=4,live_frame_limit=1048576,live_capture_limit=8388608,live_capture_timeout_seconds=30,navigation_live_sampling_readonly=True,navigation_restart=False,cluster_transport_connected=False,on_car_tested=False,factory_contract_revision=6)
 manifest['files']={name:dict(bytes=len(b),sha256=sha(b)) for name,b in files.items()}
 scripts=tuple(dict.fromkeys(tuple(manifest['scripts_sha256'])+('review_secondary_keyframes.py','review_live_input.py','project_console.py','decode_androidauto_display.py')))
 manifest['scripts_sha256']={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts}
 manifest['source_sha256'].update({p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for folder in (native,ROOT/'native/cluster-bridge/live') for p in folder.iterdir() if p.suffix in ('.c','.h','.sh')})
 manifest['source_sha256']['native/cluster-bridge/nav_snapshot.c']=sha((ROOT/'native/cluster-bridge/nav_snapshot.c').read_bytes())
 for name,b in files.items():(release/name).write_bytes(b)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2))
 readme="""LIVE INPUT TEST v2
==================
Goal: verify actual phone frames through the owned queue after a delayed phone
connection, with factory encoder sampling during the live feed. It writes RAM captures; this
test does not replace the cluster video writer.

1. Extract the entire ZIP into a fresh folder on the connected laptop.
2. Park, ignition on, phone unplugged, Ethernet connected, working factory maps.
3. Run:
 python scripts/run_disconnected_observer.py --run --live-input --phone-unplugged
4. Select the factory map in the cluster at the prompt.
5. At CAPTURE READY swap Ethernet for phone, start a Google Maps route, and let
 it run about12 seconds. Unplug phone, reconnect Ethernet, then press Enter.
6. Follow the existing explicit phone-disconnected cleanup prompts.
7. Return the entire delphi-dump/_disconnect_observer_* folder.

This run:
-Disables ineffective focus refresh notifications. No extra AndroidAuto thread
 is created. Waits up to180 seconds for the first usable phone frame.
-Copies borrowed phone frames into a fixed four-slot/1MiB-per-frame queue.
 A separate bounded reader writes live-copy.h264 plus timing data in RAM.
 Frames are checked byte-for-byte against the receiver capture on the laptop.
-Samples native map geometry once per second with the same unit monotonic clock,
 without restarting NavigationServer or opening the cluster transport.
-Uses the existing validated AndroidAuto launch and disconnected cleanup.
 Queue overflow drops data and waits for codec+IDR; it never blocks phone ACKs.
 The capture reader stops30 seconds after the first usable frame, or when its
 source process ends. The connection wait has a separate180-second limit.
"""
 (release/'README.txt').write_text(readme)
 bundle=base/'live-input-v2-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n in scripts:z.write(ROOT/'scripts'/n,'scripts/'+n)
  for n in (*files,'manifest.json','README.txt'):z.write(release/n,(release/n).relative_to(ROOT).as_posix())
 with tempfile.TemporaryDirectory() as temp:
  p=Path(temp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  result=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_disconnected_observer.py'),'--live-input'],cwd=p,capture_output=True,text=True)
  if result.returncode or 'Plan only' not in result.stdout or (p/'delphi-dump').exists():raise ValueError('Portable plan '+result.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_disconnected_observer as m;print(len(m.package(Path(sys.argv[1])/'native/cluster-bridge/keyframe-probe/release',phone=True,factory=True,secondary=True,cluster=True,probe=True)))"
  result=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if result.returncode or result.stdout.strip()!='4':raise ValueError('Portable assets '+result.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),qnx_gates_passed=True,workflow_tests_passed=True,portable_plan_passed=True,portable_assets_passed=True,cluster_transport_connected=False,manifest=manifest)
 (base/'release-review.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
