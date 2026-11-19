"""Gate and package the bounded live phone-to-cluster presentation trial."""
from project_console import console_session,status,log as print
from pathlib import Path
import ast,hashlib,json,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parents[1]
from package_cluster_replay import elf_gate
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 review=json.loads((ROOT/'delphi-analysis/cluster-bridge/20261118-v12-latency-review/startup-review.json').read_text())
 if not review.get('sanitizers_passed') or not review.get('all_original_frames_and_pixels_preserved') or review.get('output_frames')!=542 or not review.get('frame_pts_follow_schedule') or review.get('steady_delay_ms')!=250:raise ValueError('Startup real-picture gate missing')
 for name,value in review['source_sha256'].items():
  if sha((ROOT/name).read_bytes())!=value:raise ValueError('Startup verified source changed '+name)
 base=ROOT/'native/cluster-bridge/live-output';out=base/'release';out.mkdir(parents=True,exist_ok=True)
 replay=ROOT/'native/cluster-bridge/replay';old=replay/'release';m=json.loads((old/'manifest.json').read_text())
 log=(replay/'qemu/qemu.log').read_text();checked={Path(x.split()[1]).name:x.split()[0] for x in (replay/'qemu/tested.sha256').read_text().splitlines()}
 for marker in ('LIVE_EXTENDED_QNX_PASS','LIVE_OPTIONS_QNX_PASS','LIVE_EXTENDED_OVERFLOW_QNX_PASS','LIVE_STARTUP_LATENCY_QNX_PASS','LIVE_DEADLINE_DRAIN_QNX_PASS','LIVE_NAV_SINK_QNX_PASS','LIVE_STARTUP_QNX_PASS','LIVE_NATIVE_RETURN_QNX_PASS','LIVE_ROUTE_STOP_QNX_PASS','startup_bootstrap_frames=3','first_frame_gate=1','completed_close_preserves_done=1','REPLAY_TIMELINE_PASS','REPLAY_FIXTURE_PASS','REPLAY_ACTUAL_PRELOAD_PASS','REPLAY_QNX_END'):
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
 m.update(kind='native_cluster_live_output',route_presentation_trial=True,route_presentation_hold_seconds=40,route_policy_report_version=4,route_disconnect_restore=True,route_disconnect_event=0x173e,route_started_event=0x173d,route_native_projected=1,route_native_native=2,route_presentation_extra_aa_threads_when_live=1,phone_must_stay_unplugged=False,phone_unplugged_before_launch_and_cleanup=True,cluster_display_proven=False,video_mode='live_original_baseline_no_reencode',live_report_version=6,extended_live_supported=True,automatic_factory_return_required=True,release_version=15,live_reader_report_version=3,bounded_input_closed_before_drain=True,startup_delay_ms=250,startup_initial_delay_ms=1000,startup_catchup_pace_numerator=4,startup_catchup_pace_denominator=5,startup_bootstrap_frames=3,startup_buffer_bytes=4194304,live_output_capture_limit=2097152,recorded_video_available=False,live_phone_navigation=True,on_car_tested=False,live_frame_wait_seconds=180,live_capture_seconds=30,timeline_mode='continue_live_clock_and_cc',activation_mode='native_clock_then_first_verified_phone_frame',single_native_descriptor=True,output_packetizer='native_bounded_live_mux',new_nav_threads=1)
 m['layout_trial']=dict(video_service_id=9,width_margin_total=0,height_margin_total=0,left_right_pixels=0,content_rectangle=[0,0,800,480],coded_dimensions=[800,480],density=140,ui_config_field=11,content_insets=dict(top=0,bottom=72,left=120,right=120),stable_content_insets=dict(top=0,bottom=64,left=120,right=120),ui_content_rectangle=[120,0,680,408],stable_ui_rectangle=[120,0,680,416],stable_ui_anchor_preserved=True,turn_card_position_on_car_verified=False,full_frame_map_requested=True,phone_honors_ui_insets_unverified=False,bottom_inset_on_car_verified=False,layout_on_car_verified=False,primary_configuration_unchanged=True,reencoded=False)
 m['source_sha256']={n:sha((ROOT/n).read_bytes()) for n in m.get('source_sha256',{})}
 m['files']={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()}
 m.setdefault('source_sha256',{}).update({p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for folder in (ROOT/'native/cluster-bridge/live',replay,ROOT/'native/cluster-bridge/nav-control',ROOT/'native/cluster-bridge/nav-launch',ROOT/'native/cluster-bridge/layout-margin') for p in folder.iterdir() if p.suffix in ('.c','.h','.sh','.S','.py')})
 for n in ('proc_guard.c','proc_guard.h'):
  p=ROOT/'native/observer/launch'/n;m['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p.read_bytes())
 for name,b in files.items():(out/name).write_bytes(b)
 (out/'manifest.json').write_text(json.dumps(m,indent=2))
 aa=ROOT/'native/cluster-bridge/keyframe-probe/release';am=json.loads((aa/'manifest.json').read_text())
 if not am.get('route_presentation_trial') or am.get('route_presentation_hold_seconds')!=40 or am.get('route_native_projected')!=1 or am.get('route_native_native')!=2 or am.get('route_policy_report_version')!=4 or not am.get('route_disconnect_restore'):raise ValueError('Rebuild the QNX-gated presentation-capable AA release first')
 for name,e in am['files'].items():
  if sha((aa/name).read_bytes())!=e['sha256']:raise ValueError('Validated AA input payload changed '+name)
 for test in ('test_extended_live.py','test_live_input.py','test_disconnected_observer.py','test_live_cluster_bridge.py','test_radio_ram.py','test_finish_live_session.py','test_route_policy.py'):
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
 readme="""LIVE ANDROID AUTO CLUSTER TRIAL v15
===================================
Full800x480 map, density140,120px horizontal UI insets. Map/content bottom inset
is72px; the separate stable UI bottom inset stays64px to preserve the previous
UI anchor. Actual turn-card positioning is phone-controlled and must be checked.
250ms steady buffering and the proven startup/catchup sequence are retained.

Extract the ENTIRE ZIP into a fresh folder. Park, ignition on, working factory
maps, phone unplugged and Ethernet connected. Configure/launch while parked.
Extended output (until phone disconnect or a verified failure):
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged --no-live-timeout
Bounded30-second trial (also the default when neither option is supplied):
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged --live-seconds 30

Only at CAPTURE READY swap Ethernet for phone. The extended mode has no active
video-duration cutoff. Diagnostic recording remains bounded at8MiB/2048 frames;
video forwarding and source/disconnect monitoring continue after recording stops.
After your test, park, unplug phone, reconnect Ethernet and finish the existing
PHONE REMOVED cleanup. Do not operate the laptop while driving. Leave the map
location button untouched until answering the automatic-return question.
Return the complete delphi-dump/_disconnect_observer_* folder.

This remains a single phone-session RAM trial with explicit end-of-test cleanup.
Automatic boot installation and repeated phone reconnect without cleanup are
separate deployment work; this bundle does not install a persistent hook.
Use the separate startup-preflight bundle to collect the current boot script.
If cleanup is pending, resume with this SAME bundle and the saved result folder;
the chosen live limit is saved and cannot be changed during resume.
"""
 (out/'README.txt').write_text(readme)
 bundle=base/'live-cluster-v15-laptop.zip'
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
 review=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),qnx_live_sink_passed=True,qnx_deadline_drain_passed=True,workflow_tests_passed=True,portable_plan_passed=True,horizontal_layout_preserved=True,added_bottom_ui_inset=72,stable_bottom_ui_inset=64,steady_added_delay_ms=250,on_car_tested=False)
 (base/'release-review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
