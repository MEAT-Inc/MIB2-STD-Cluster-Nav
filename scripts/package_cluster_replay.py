"""Gate and package the first recorded-map cluster display trial."""
from project_console import console_session, log as print
import hashlib,io,json,struct,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'native/cluster-bridge';R=BASE/'replay';N=BASE/'nav-launch';C=BASE/'nav-control'
sys.path.insert(0,str(ROOT/'.tools/python'));sys.path.insert(0,str(ROOT/'.tools/video-python'))
from elftools.elf.elffile import ELFFile
from cluster_ts_mux import ClusterTSMux
from native_transport_packet_reference import validate_ts
sha=lambda b:hashlib.sha256(b).hexdigest()
def elf_gate(p):
 b=p.read_bytes();e=ELFFile(io.BytesIO(b));imports=[];exports=[];needed=[]
 if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or not 0<len(b)<=131072:raise ValueError('Native ABI/size')
 for s in e.iter_segments():
  if s['p_type']=='PT_GNU_STACK' and s['p_flags']&1:raise ValueError('Executable stack')
  if s['p_type']=='PT_DYNAMIC':needed=[t.needed for t in s.iter_tags() if t.entry.d_tag=='DT_NEEDED']
 for s in e.get_section_by_name('.dynsym').iter_symbols():
  if s['st_info']['bind']=='STB_GLOBAL':
   if s['st_shndx']=='SHN_UNDEF':imports.append(s.name)
   elif s['st_info']['type']=='STT_FUNC':exports.append(s.name)
 libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
 if needed!=['libc.so.3'] or set(imports)-libc:raise ValueError('Unverified native dependencies')
 return b,dict(imports=imports,exports=exports,needed=needed)
def main():
 for d,markers in ((R,('REPLAY_TIMELINE_PASS','REPLAY_FIXTURE_PASS','REPLAY_ARMED_DESCRIPTOR_PASS','REPLAY_PRELOAD_ARMED_DESCRIPTOR_PASS','REPLAY_IDLE_IMPORT_INSPECTION_PASS','REPLAY_ACTUAL_PRELOAD_PASS','REPLAY_HOOK_RUNNER rc=0','REPLAY_QNX_END','REPLAY_EARLY_LEGACY_EXIT126_PASS','REPLAY_EARLY_IO_PASS','REPLAY_IMPORTS_PASS','REPLAY_LIBC_PROFILE_PASS','"profile_matches":true')),(N,('NAV_LIFECYCLE_DELAYED_START_PASS','NAV_LIFECYCLE_INTEGRATION_PASS','NAV_FIXTURE_ARGV_CWD_CONFIG_PASS','NAV_STDIO_PRESERVED_PASS','NAV_POST_EXEC_IDENTITY_PASS','NAV_PRODUCTION_LIFECYCLE_PASS','NAV_FIXTURE_CANONICAL_IMAGE_PASS','NAV_REPLAY_ARM_PASS','NAV_REPLAY_ARM_REFUSED','NAV_DISCONNECT_PENDING_NO_SIGNAL_PASS','NAV_DISCONNECT_STATE_MISMATCH_REFUSED','NAV_DISCONNECT_LOCK_REFUSED','NAV_DISCONNECT_LATE_CLEANUP_PASS','NAV_DISCONNECT_IDEMPOTENT_PASS','NAV_DISCONNECT_ORPHAN_CLEANUP_PASS','NAV_DISCONNECT_QNX_SUITE_PASS'))):
  log=(d/'qemu/qemu.log').read_text();checked={Path(v.split()[1]).name:v.split()[0] for v in (d/'qemu/tested.sha256').read_text().splitlines()};name='nav_launch' if d==N else 'libdelphi_cluster.so'
  if not all(v in log for v in markers) or checked[name]!=sha((d/'build'/name).read_bytes()):raise ValueError('Native QNX gate failed')
 files={};elf={}
 for name,p in (('nav_launch',N/'build/nav_launch'),('libdelphi_cluster.so',R/'build/libdelphi_cluster.so'),('replay_libc_check',R/'build/replay_libc_check'),('nav_cycle',C/'build/nav_cycle')):files[name],elf[name]=elf_gate(p)
 if checked.get('replay_libc_check')!=sha(files['replay_libc_check']):
  helper_checked={Path(v.split()[1]).name:v.split()[0] for v in (R/'qemu/tested.sha256').read_text().splitlines()}
  if helper_checked.get('replay_libc_check')!=sha(files['replay_libc_check']):raise ValueError('Untested libc preflight helper')
 control_log=(C/'qemu/qemu.log').read_text()
 control_checked={Path(v.split()[1]).name:v.split()[0] for v in (C/'qemu/tested.sha256').read_text().splitlines()}
 for marker in ('NAV_REPLAY_STALL_CAPTURE_GUARD_PASS','NAV_STALL_CAPTURE_GUARD_PASS','NAV_RECOVER_HEALTHY_REFUSAL_PASS','NAV_RECOVER_FACTORY_AUTORESTART_PASS','NAV_PAGE_READ_QNX_PASS','SAL_GRACEFUL_CONTROL_QNX_PASS'):
  if marker not in control_log:raise ValueError('Lifecycle helper QNX gate missing '+marker)
 if control_checked.get('nav_cycle')!=sha(files['nav_cycle']) or b'recover-fixture' in files['nav_cycle']:raise ValueError('Lifecycle helper release mismatch')
 if 'kill' in elf['nav_launch']['imports']:raise ValueError('Controller still imports generic kill')
 if b'NAV_PREEXEC_CANONICAL_RACE_PROVEN' in files['nav_launch']:raise ValueError('Race-delay fixture in production launcher')
 if set(elf['libdelphi_cluster.so']['exports'])!={'_init','_fini'}:raise ValueError('Wrong shim exports')
 if any(n.encode() in files['libdelphi_cluster.so'] for n in ('test_geometry','test_open_return','test_write_return')):raise ValueError('Test profile in production')
 source=ROOT/'delphi-dump/_disconnect_observer_20261103_022700_3b445220';review=json.loads((ROOT/'delphi-analysis/cluster-bridge/20261103-review/video-review.json').read_text());raw=(source/'secondary.h264').read_bytes()
 if sha(raw)!=review['source_sha256'] or review['decoded_frames']!=617 or not review['offline_remux']['original_timing_preserved']:raise ValueError('Source capture gate')
 keyroot=ROOT/'delphi-analysis/cluster-bridge/20261104-keyframe-replay';keyreview=json.loads((keyroot/'review.json').read_text());keyraw=(keyroot/'secondary-keyframes.h264').read_bytes();scheduled=(keyroot/'replay-keyframes.bin').read_bytes()
 if keyreview['source_sha256']!=sha(raw) or keyreview['encoded_sha256']!=sha(keyraw) or keyreview['replay_sha256']!=sha(scheduled) or not keyreview['fits_current_8MiB_limit'] or keyreview['keyframe_interval_frames']!=5 or keyreview['keyframe_count']!=(keyreview['decoded_frames']+4)//5:raise ValueError('Frequent-keyframe source gate')
 frame_count=keyreview['decoded_frames']
 if not 1<=frame_count<617 or keyreview['original_frame_times_ms'][-1]>20000:raise ValueError('Bounded excerpt gate')
 head=struct.unpack_from('<8I',scheduled);groups=[];at=32
 if head[0:2]!=(0x314c5052,1) or head[2]!=len(scheduled) or any(head[6:]) or not 0<head[3]<10000:raise ValueError('Keyframe schedule header')
 for i in range(head[3]):
  t,n=struct.unpack_from('<II',scheduled,at);at+=8
  if not n or n%188 or at+n>len(scheduled) or groups and t<groups[-1][0]:raise ValueError('Keyframe schedule bounds')
  groups.append([t,scheduled[at:at+n]]);at+=n
 ts=b''.join(v[1] for v in groups);validate_ts(ts)
 if at!=len(scheduled) or len(ts)//188!=head[4] or groups[-1][0]!=head[5] or head[5]!=keyreview['original_frame_times_ms'][-1]:raise ValueError('Keyframe schedule accounting')
 import av,math,itertools
 import numpy as np
 original=av.open(io.BytesIO(raw),format='h264');movie=av.open(io.BytesIO(ts),format='mpegts');codec=movie.streams.video[0].codec_context
 if codec.profile not in ('Baseline','Constrained Baseline') or (codec.width,codec.height)!=(800,480):raise ValueError('Keyframe codec profile')
 hashes=[];psnr=[];seen_keys=[];times=[]
 for i,(old,f) in enumerate(zip(itertools.islice(original.decode(video=0),frame_count),movie.decode(video=0),strict=True)):
  oldpixels=old.to_ndarray(format='rgb24');pixels=f.to_ndarray(format='rgb24');delta=oldpixels.astype(np.float32)-pixels.astype(np.float32);mse=float(np.mean(delta*delta));psnr.append(99.0 if not mse else 10*math.log10(255*255/mse));hashes.append(sha(pixels.tobytes()));times.append(f.pts)
  if f.key_frame:seen_keys.append(i)
 if len(hashes)!=frame_count or seen_keys!=list(range(0,frame_count,5)) or times!=[t*90+1 for t in keyreview['original_frame_times_ms']] or min(psnr)<35:raise ValueError('Keyframe decoded video/timing/quality gate')
 files['replay.bin']=scheduled
 if len(scheduled)>8388608:raise ValueError('Replay too large')
 refs={}
 for name,remote,p in (('NavigationServer.original','/extbin/apps/bin/NavigationServer',source/'NavigationServer.reference'),('NavServer.cfg.reference','/extbin/apps/cfg/NAV/v0/NC/Delphi/NavServer.cfg',ROOT/'delphi-dump/extbin/apps/cfg/NAV/v0/NC/Delphi/NavServer.cfg'),('procman.reference','/proc/boot/procman',source/'procman.reference'),('procman-core.cfg','/etc/procman_core.cfg',source/'procman-core.cfg')):
  b=p.read_bytes();refs[name]=dict(path=remote,bytes=len(b),sha256=sha(b))
 for name,remote,p in (('libc.so.3.reference','/proc/boot/libc.so.3',ROOT/'delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce/libc.so.3.captured'),('libXSAL.so.reference','/proc/boot/libXSAL.so',ROOT/'delphi-dump/ramdisk/delphi-stage_4b0597ac42d84f0ca7dc8a8c7e138c00/01_libXSAL.so')):
  b=p.read_bytes();refs[name]=dict(path=remote,bytes=len(b),sha256=sha(b))
 if refs['NavigationServer.original']['sha256']!='a999725350df8503c44a25da2676a8c1a99914a99a36f24bb6334a509def4afe':raise ValueError('Wrong NavigationServer')
 tests=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_cluster_replay.py')],cwd=ROOT,capture_output=True,text=True)
 if tests.returncode:raise ValueError(tests.stderr)
 scripts=('run_cluster_replay.py','cluster_preflight.py','run_observer_smoke.py','delphi_inventory.py','project_console.py','decode_delphi_observer.py');sources=[p for d in (R,N,C) for p in d.iterdir() if p.suffix in ('.c','.h','.S','.sh')]
 manifest=dict(kind='native_cluster_recorded_map_replay',hook_mode='app_import_slots',startup_contract_revision=9,activation_mode="native_frames_then_explicit_arm",lifecycle_mode="sal_shutdown_exact_crash_recovery",timeline_mode="continue_live_clock_and_cc",video_mode="periodic_idr",cluster_map_selected_required=True,native_source_capture_limit=1048576,post_exec_identity_ack=True,canonical_image_exec=True,preserve_standard_streams=True,libc_profile=json.loads((R/'unit-libc-profile.json').read_text()),phone_must_stay_unplugged=True,live_phone_navigation=False,on_car_tested=False,cluster_display_proven=False,replay=dict(source_collection=source.name,frames=frame_count,original_source_frames=617,width=800,height=480,duration_ms=groups[-1][0],groups=len(groups),packets=len(ts)//188,transport_sha256=sha(ts),clock_discontinuity_prelude=False,keyframe_interval_frames=5,keyframe_count=(frame_count+4)//5,pixels_reencoded=True,minimum_rgb_psnr_db=min(psnr),explicit_arm_required=True),references=refs,elf=elf,files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()},scripts_sha256={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts},source_sha256={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in sources})
 release=R/'release';release.mkdir(exist_ok=True)
 for n,b in files.items():(release/n).write_bytes(b)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2));(release/'README.txt').write_bytes((R/'README.txt').read_bytes());bundle=R/'cluster-map-replay-v9-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n in scripts:z.write(ROOT/'scripts'/n,'scripts/'+n)
  for n in (*files,'manifest.json','README.txt'):z.write(release/n,(release/n).relative_to(ROOT).as_posix())
 with tempfile.TemporaryDirectory(prefix='cluster-replay-portable-') as temp:
  p=Path(temp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  result=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_cluster_replay.py')],cwd=p,capture_output=True,text=True)
  if result.returncode or 'Plan only' not in result.stdout or (p/'delphi-dump').exists():raise ValueError('Portable plan: '+result.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_cluster_replay as r;print(len(r.package(Path(sys.argv[1])/'native/cluster-bridge/replay/release')[0]))"
  result=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if result.returncode or result.stdout.strip()!='5':raise ValueError('Portable assets: '+result.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),decoded_excerpt_frames_verified=frame_count,original_source_frames=617,original_timing_preserved=True,pixels_reencoded=True,keyframe_count=(frame_count+4)//5,minimum_rgb_psnr_db=min(psnr),portable_plan_passed=True,portable_assets_passed=True,workflow_tests=tests.stderr.strip(),manifest=manifest)
 (ROOT/'delphi-analysis/control-runtime/cluster-map-replay-release.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
