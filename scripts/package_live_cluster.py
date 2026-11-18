"""Gate and package the bounded live phone-to-cluster presentation trial."""
from project_console import console_session,status,log as print
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
from package_cluster_replay import elf_gate
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 review=json.loads((ROOT/'delphi-analysis/cluster-bridge/20261118-v6-decoder-review/startup-review.json').read_text())
 if not review.get('sanitizers_passed') or not review.get('all_original_frames_and_pixels_preserved') or review.get('output_frames')!=408:raise ValueError('Startup real-picture gate missing')
 for name,value in review['source_sha256'].items():
  if sha((ROOT/name).read_bytes())!=value:raise ValueError('Startup verified source changed '+name)
 base=ROOT/'native/cluster-bridge/live-output';out=base/'release';out.mkdir(parents=True,exist_ok=True)
 replay=ROOT/'native/cluster-bridge/replay';old=replay/'release';m=json.loads((old/'manifest.json').read_text())
 log=(replay/'qemu/qemu.log').read_text();checked={Path(x.split()[1]).name:x.split()[0] for x in (replay/'qemu/tested.sha256').read_text().splitlines()}
 for marker in ('LIVE_NAV_SINK_QNX_PASS','LIVE_STARTUP_QNX_PASS','LIVE_NATIVE_RETURN_QNX_PASS','LIVE_ROUTE_STOP_QNX_PASS','startup_bootstrap_frames=3','first_frame_gate=1','completed_close_preserves_done=1','REPLAY_TIMELINE_PASS','REPLAY_FIXTURE_PASS','REPLAY_ACTUAL_PRELOAD_PASS','REPLAY_QNX_END'):
  if marker not in log:raise ValueError('Missing native gate '+marker)
 files={}
 for name,source in (('libdelphi_cluster.so',replay/'build/libdelphi_cluster_live.so'),('live_queue_prepare',replay/'build/live_queue_prepare')):
  b,meta=elf_gate(source)
  if checked.get(source.name)!=sha(b) or set(meta['imports'])&{'kill','ptrace','pwrite','pwrite64','system'}:raise ValueError('Live native binary unverified '+name)
  if b'LIVE_NAV_SINK_QNX_PASS' in b or b'LIVE_SINK_TEST' in b:raise ValueError('Test profile in production')
  files[name]=b;m.setdefault('elf',{})[name]=meta
 for name,directory,markers in (('nav_launch',ROOT/'native/cluster-bridge/nav-launch',('NAV_FINALIZE_RECOVERED_PASS','NAV_FINALIZE_ALIVE_REFUSAL_PASS','NAV_FINALIZE_STALE_REFUSAL_PASS')),('nav_cycle',ROOT/'native/cluster-bridge/nav-control',('NAV_LIVE_STALL_CAPTURE_GUARD_PASS','NAV_RECOVER_HEALTHY_REFUSAL_PASS','NAV_RECOVER_FACTORY_AUTORESTART_PASS'))):
  tested={Path(x.split()[1]).name:x.split()[0] for x in (directory/'qemu/tested.sha256').read_text().splitlines()};logtext=(directory/'qemu/qemu.log').read_text();b,meta=elf_gate(directory/'build'/name)
  if tested.get(name)!=sha(b) or not all(x in logtext for x in markers):raise ValueError('Lifecycle recovery gates '+name)
  files[name]=b;m.setdefault('elf',{})[name]=meta
 b=(old/'replay_libc_check').read_bytes()
 if sha(b)!=m['files']['replay_libc_check']['sha256']:raise ValueError('Validated libc preflight changed')
 files['replay_libc_check']=b
 files['replay.bin']=(replay/'hook-replay.bin').read_bytes()
 m.pop('replay',None)
 m.update(kind='native_cluster_live_output',route_presentation_trial=True,route_presentation_hold_seconds=40,route_policy_report_version=3,route_disconnect_restore=True,route_disconnect_event=0x173e,route_started_event=0x173d,route_native_projected=1,route_native_native=2,route_presentation_extra_aa_threads_when_live=1,phone_must_stay_unplugged=False,phone_unplugged_before_launch_and_cleanup=True,cluster_display_proven=False,video_mode='live_original_baseline_no_reencode',live_report_version=4,automatic_factory_return_required=True,release_version=9,startup_delay_ms=1000,startup_bootstrap_frames=3,startup_buffer_bytes=4194304,live_output_capture_limit=2097152,recorded_video_available=False,live_phone_navigation=True,on_car_tested=False,live_frame_wait_seconds=180,live_capture_seconds=30,timeline_mode='continue_live_clock_and_cc',activation_mode='native_clock_then_first_verified_phone_frame',single_native_descriptor=True,output_packetizer='native_bounded_live_mux',new_nav_threads=1)
 m['layout_trial']=dict(video_service_id=9,width_margin_total=200,height_margin_total=0,left_right_pixels=100,content_rectangle=[100,0,700,480],coded_dimensions=[800,480],density=160,phone_rendering_test_needed=True,primary_configuration_unchanged=True)
 m['source_sha256']={n:sha((ROOT/n).read_bytes()) for n in m.get('source_sha256',{})}
 m['files']={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()}
 m.setdefault('source_sha256',{}).update({p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for folder in (ROOT/'native/cluster-bridge/live',replay,ROOT/'native/cluster-bridge/nav-control',ROOT/'native/cluster-bridge/nav-launch',ROOT/'native/cluster-bridge/layout-margin') for p in folder.iterdir() if p.suffix in ('.c','.h','.sh','.S','.py')})
 for n in ('proc_guard.c','proc_guard.h'):
  p=ROOT/'native/observer/launch'/n;m['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
 for name,b in files.items():(out/name).write_bytes(b)
 (out/'manifest.json').write_text(json.dumps(m,indent=2))
 aa=ROOT/'native/cluster-bridge/keyframe-probe/release';am=json.loads((aa/'manifest.json').read_text())
 if not am.get('route_presentation_trial') or am.get('route_presentation_hold_seconds')!=40 or am.get('route_native_projected')!=1 or am.get('route_native_native')!=2 or am.get('route_policy_report_version')!=3 or not am.get('route_disconnect_restore'):raise ValueError('Rebuild the QNX-gated presentation-capable AA release first')
 for name,e in am['files'].items():
  if sha((aa/name).read_bytes())!=e['sha256']:raise ValueError('Validated AA input payload changed '+name)
 for test in ('test_live_input.py','test_disconnected_observer.py','test_live_cluster_bridge.py','test_radio_ram.py','test_finish_live_session.py','test_route_policy.py'):
  status('Running '+test);v=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests'/test)],capture_output=True,text=True)
  if v.returncode:raise ValueError(v.stdout[-2000:]+v.stderr[-10000:])
 names=set(am['scripts_sha256'])|{'live_cluster_bridge.py','run_cluster_replay.py','radio_ram.py'}
 # Include local imports recursively so the extracted ZIP runs with stdlib only.
 while True:
  added=set()
  for n in names:
   for s in ast.walk(ast.parse((ROOT/'scripts'/n).read_text())):
    imports=[x.name for x in s.names] if isinstance(s,ast.Import) else [s.module] if isinstance(s,ast.ImportFrom) else []
    for x in imports:
     p=(x or '').split('.')[0]+'.py'
     if (ROOT/'scripts'/p).is_file():added.add(p)
  if added<=names:break
  names|=added
 m['scripts_sha256']={n:sha((ROOT/'scripts'/n).read_bytes()) for n in names};am['scripts_sha256']=dict(m['scripts_sha256'])
 (out/'manifest.json').write_text(json.dumps(m,indent=2))
 from radio_ram import build_cleanup_plan
 cleanup=build_cleanup_plan(ROOT);(out/'cleanup-plan.json').write_text(json.dumps(cleanup,indent=2))
 m['cleanup_plan_sha256']=sha((out/'cleanup-plan.json').read_bytes());(out/'manifest.json').write_text(json.dumps(m,indent=2))
 readme="""LIVE ANDROID AUTO CLUSTER TRIAL v9
==================================
V9 returns the existing cluster video channel to factory navigation after the
verified phone-service stop. Return waits for complete native SPS/PPS/IDR and
continues the same transport clock and continuity counters. After unplugging,
observe whether factory compass/map returns automatically BEFORE any manual
map-location toggle or cleanup. That observation is saved independently from
subsequent manual radio/cluster restoration checks. Both are required to pass.
If a stale mobile-navigation message is present before testing, reboot the radio
once and wait for working factory maps.
Secondary display requests 200 total horizontal margin pixels (100 per side)
and density160, preserving the original 800x480 coded frame. Phone rendering
and physical clipping remain to be verified.

This is live phone video. The initial phone codec/keyframe is repeated three
times while source frames are buffered in order. All original frames follow
with approximately one second of added delay; no re-encoding is used. This
tests whether the cluster missed the original single startup keyframe.
Park with ignition on, working factory maps, phone unplugged and Ethernet connected.
Extract the ENTIRE ZIP into a fresh laptop folder. Run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
Before uploading, RAM space is checked. Only hash-matching files from locally
archived, restored runs are eligible for removal; incomplete/active tests are
preserved. If30MiB is still unavailable, the script stops before any app launch.
In that case reboot the radio once, wait for factory maps, and rerun.
Select factory map graphics in the instrument cluster and confirm the arm prompt.
Use a browsable factory map with no VW route running.
This bounded trial defers only the phone-route handoff notification while the
verified live bridge is healthy (maximum40 seconds), acknowledging phone focus
through the stock native helper. Original notification is released on bridge
stop/failure/timeout; route-end and unrelated messages pass unchanged. There
is no stored firmware patch. This is a presentation prototype, not a final
production arbitration policy.
Only at CAPTURE READY swap Ethernet for phone. Start a Google Maps route promptly: the video window begins with the first phone frame.
Watch the cluster for about12 seconds of LIVE map updates. Unplug phone,
reconnect Ethernet, then press Enter. Complete PHONE REMOVED cleanup and
answer whether factory compass/map returned automatically before cleanup,
then whether live maps appeared and factory maps restored after cleanup.
Return the entire delphi-dump/_disconnect_observer_* folder.

The existing native descriptor, app import guards, timeline handoff and exact
crash recovery are reused. No second cluster writer or extra Nav worker is added.
The consumer waits up to180 seconds for the phone, then runs up to30 seconds
from its first usable frame. Overflow or transport failure ends output.
If cleanup remains pending, keep the phone unplugged and use the SAME extracted
bundle with --resume "<result-folder>" --live-cluster --phone-unplugged.
This trial has passed local/QNX tests; on-car display
and restoration of the combined run remain to be verified.
"""
 (out/'README.txt').write_text(readme)
 bundle=base/'live-cluster-v9-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('README.txt',readme)
  for n in sorted(names):z.write(ROOT/'scripts'/n,'scripts/'+n)
  for n in (*files,'manifest.json','README.txt','cleanup-plan.json'):z.write(out/n,(out/n).relative_to(ROOT).as_posix())
  for n in am['files']:z.write(aa/n,(aa/n).relative_to(ROOT).as_posix())
  z.writestr((aa/'manifest.json').relative_to(ROOT).as_posix(),json.dumps(am,indent=2))
 with tempfile.TemporaryDirectory() as temp:
  p=Path(temp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  v=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_disconnected_observer.py'),'--live-cluster'],cwd=p,capture_output=True,text=True)
  if v.returncode or 'Plan only' not in v.stdout or (p/'delphi-dump').exists():raise ValueError('Portable live plan failed '+v.stderr)
  code="import sys,json;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import live_cluster_bridge;import run_disconnected_observer as m;print(len(m.package(Path(sys.argv[1])/'native/cluster-bridge/keyframe-probe/release',phone=True,factory=True,secondary=True,cluster=True,probe=True)))"
  v=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if v.returncode or v.stdout.strip()!='4':raise ValueError('Portable live imports/assets '+v.stderr)
 # Produce a separately labeled optional all-UI density trial from the same gate.
 optional_source=ROOT/'native/secondary-display/build/libdelphi_observer_keyframe_density140.so'
 secondary=ROOT/'native/secondary-display'
 optional_checked={Path(x.split()[1]).name:x.split()[0] for x in (secondary/'qemu/layout-margin-tested.sha256').read_text().splitlines()}
 alt,alt_meta=elf_gate(optional_source)
 if optional_checked.get(optional_source.name)!=sha(alt):raise ValueError('Optional density140 native binary unverified')
 baseline_meta=elf_gate(aa/'libdelphi_observer.so')[1]
 if any(set(alt_meta[k])!=set(baseline_meta[k]) for k in ('imports','exports','needed')):raise ValueError('Optional density140 ABI changed')
 optional=base/'live-cluster-v9-margin200-density140-laptop.zip'
 optional_note='OPTIONAL V9 MARGIN200 / DENSITY140 ALL-UI TRIAL\nDensity140 requests approximately 12.5% smaller whole UI, including text, than density160. Phone rendering and on-car clipping remain unverified. Use this separate bundle only to compare against the default margin200 / density160 trial.\n\n'
 with zipfile.ZipFile(bundle) as source,zipfile.ZipFile(optional,'w',zipfile.ZIP_DEFLATED) as z:
  for name in source.namelist():
   raw=source.read(name)
   if name==(aa/'libdelphi_observer.so').relative_to(ROOT).as_posix():raw=alt
   elif name in ((aa/'manifest.json').relative_to(ROOT).as_posix(),(out/'manifest.json').relative_to(ROOT).as_posix()):
    variant=json.loads(raw);variant['layout_trial']=dict(variant['layout_trial'],density=140,optional_all_ui_scaling=True,approximate_relative_scale=0.875)
    if name==(aa/'manifest.json').relative_to(ROOT).as_posix():variant['files']['libdelphi_observer.so']=dict(bytes=len(alt),sha256=sha(alt))
    raw=json.dumps(variant,indent=2).encode()
   elif name in ('README.txt',(out/'README.txt').relative_to(ROOT).as_posix()):raw=(optional_note+readme.replace('density160, preserving','density140, preserving')).encode()
   z.writestr(name,raw)
 with tempfile.TemporaryDirectory() as temp:
  p=Path(temp)
  with zipfile.ZipFile(optional) as z:
   if z.testzip() is not None:raise ValueError('Optional density140 ZIP corrupted')
   z.extractall(p)
  for manifest_path in (aa/'manifest.json',out/'manifest.json'):
   rel=manifest_path.relative_to(ROOT);variant=json.loads((p/rel).read_text())
   for n,e in variant['files'].items():
    raw=(p/rel.parent/n).read_bytes()
    if len(raw)!=e['bytes'] or sha(raw)!=e['sha256']:raise ValueError('Optional density140 payload hash '+n)
   for n,h in variant['scripts_sha256'].items():
    if sha((p/'scripts'/n).read_bytes())!=h:raise ValueError('Optional density140 script hash '+n)
  v=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_disconnected_observer.py'),'--live-cluster'],cwd=p,capture_output=True,text=True)
  if v.returncode or 'Plan only' not in v.stdout or (p/'delphi-dump').exists():raise ValueError('Optional density140 portable plan failed '+v.stderr)
  v=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if v.returncode or v.stdout.strip()!='4':raise ValueError('Optional density140 portable imports/assets '+v.stderr)
 review=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),qnx_live_sink_passed=True,workflow_tests_passed=True,portable_plan_passed=True,on_car_tested=False,optional_density140_bundle=optional.relative_to(ROOT).as_posix(),optional_density140_sha256=sha(optional.read_bytes()))
 (base/'release-review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
