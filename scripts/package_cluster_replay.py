"""Gate and package the first recorded-map cluster display trial."""
from project_console import console_session, log as print
import hashlib,io,json,struct,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'native/cluster-bridge';R=BASE/'replay';N=BASE/'nav-launch'
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
 for d,markers in ((R,('REPLAY_FIXTURE_PASS','REPLAY_ARMED_DESCRIPTOR_PASS','REPLAY_PRELOAD_ARMED_DESCRIPTOR_PASS','REPLAY_IDLE_IMPORT_INSPECTION_PASS','REPLAY_ACTUAL_PRELOAD_PASS','REPLAY_HOOK_RUNNER rc=0','REPLAY_QNX_END','REPLAY_EARLY_LEGACY_EXIT126_PASS','REPLAY_EARLY_IO_PASS','REPLAY_IMPORTS_PASS','REPLAY_LIBC_PROFILE_PASS','"profile_matches":true')),(N,('NAV_FIXTURE_ARGV_CWD_CONFIG_PASS','NAV_STDIO_PRESERVED_PASS','NAV_POST_EXEC_IDENTITY_PASS','NAV_PRODUCTION_LIFECYCLE_PASS','NAV_FIXTURE_CANONICAL_IMAGE_PASS','NAV_REPLAY_ARM_PASS','NAV_REPLAY_ARM_REFUSED','NAV_DISCONNECT_PENDING_NO_SIGNAL_PASS','NAV_DISCONNECT_STATE_MISMATCH_REFUSED','NAV_DISCONNECT_LOCK_REFUSED','NAV_DISCONNECT_LATE_CLEANUP_PASS','NAV_DISCONNECT_IDEMPOTENT_PASS','NAV_DISCONNECT_ORPHAN_CLEANUP_PASS','NAV_DISCONNECT_QNX_SUITE_PASS'))):
  log=(d/'qemu/qemu.log').read_text();checked={Path(v.split()[1]).name:v.split()[0] for v in (d/'qemu/tested.sha256').read_text().splitlines()};name='nav_launch' if d==N else 'libdelphi_cluster.so'
  if not all(v in log for v in markers) or checked[name]!=sha((d/'build'/name).read_bytes()):raise ValueError('Native QNX gate failed')
 files={};elf={}
 for name,p in (('nav_launch',N/'build/nav_launch'),('libdelphi_cluster.so',R/'build/libdelphi_cluster.so'),('replay_libc_check',R/'build/replay_libc_check')):files[name],elf[name]=elf_gate(p)
 if checked.get('replay_libc_check')!=sha(files['replay_libc_check']):
  helper_checked={Path(v.split()[1]).name:v.split()[0] for v in (R/'qemu/tested.sha256').read_text().splitlines()}
  if helper_checked.get('replay_libc_check')!=sha(files['replay_libc_check']):raise ValueError('Untested libc preflight helper')
 if b'NAV_PREEXEC_CANONICAL_RACE_PROVEN' in files['nav_launch']:raise ValueError('Race-delay fixture in production launcher')
 if set(elf['libdelphi_cluster.so']['exports'])!={'_init','_fini'}:raise ValueError('Wrong shim exports')
 if any(n.encode() in files['libdelphi_cluster.so'] for n in ('test_geometry','test_open_return','test_write_return')):raise ValueError('Test profile in production')
 source=ROOT/'delphi-dump/_disconnect_observer_20261103_022700_3b445220';review=json.loads((ROOT/'delphi-analysis/cluster-bridge/20261103-review/video-review.json').read_text());raw=(source/'secondary.h264').read_bytes()
 if sha(raw)!=review['source_sha256'] or review['decoded_frames']!=617 or not review['offline_remux']['original_timing_preserved']:raise ValueError('Source capture gate')
 data=(source/'timing.bin').read_bytes();rows=[struct.unpack_from('<IIQQ4I',data,32+40*i) for i in range(struct.unpack_from('<I',data,20)[0])];frames=[v for v in rows if v[0]==2];codec=[v for v in rows if v[0]==1];groups=[];clock=0
 def emit(p):
  if not groups or groups[-1][0]!=clock:groups.append([clock,bytearray()])
  groups[-1][1].extend(p);return len(p)
 mux=ClusterTSMux(emit);tick=0
 for i,v in enumerate(frames):
  ms=(v[2]-frames[0][2])//1000
  while tick<ms:clock=tick;mux.tick(clock);tick+=16
  clock=ms;au=raw[v[4]:v[4]+v[6]]
  if i==0:au=raw[:codec[0][6]]+au
  if not mux.push(au,clock):raise ValueError('Missing first IDR')
 if sha(b''.join(v[1] for v in groups))!=review['offline_remux']['sha256']:raise ValueError('Schedule changed')
 prelude=b''.join(bytes((0x47,pid>>8,pid&255,0x20,183,0x80))+b'\xff'*182 for pid in (0,0x10,0x11,0x1000));groups[0][1][:0]=prelude;ts=b''.join(v[1] for v in groups);validate_ts(ts)
 import av
 hashes=[]
 with av.open(io.BytesIO(ts),format='mpegts') as movie:
  for f in movie.decode(video=0):hashes.append(sha(f.to_ndarray(format='rgb24').tobytes()))
 if hashes!=review['decoded_rgb_sha256']:raise ValueError('Clock reset changed pixels')
 body=b''.join(struct.pack('<II',t,len(b))+b for t,b in groups);files['replay.bin']=struct.pack('<8I',0x314c5052,1,len(body)+32,len(groups),len(ts)//188,groups[-1][0],0,0)+body
 if len(files['replay.bin'])>8388608:raise ValueError('Replay too large')
 refs={}
 for name,remote,p in (('NavigationServer.original','/extbin/apps/bin/NavigationServer',source/'NavigationServer.reference'),('NavServer.cfg.reference','/extbin/apps/cfg/NAV/v0/NC/Delphi/NavServer.cfg',ROOT/'delphi-dump/extbin/apps/cfg/NAV/v0/NC/Delphi/NavServer.cfg'),('procman.reference','/proc/boot/procman',source/'procman.reference'),('procman-core.cfg','/etc/procman_core.cfg',source/'procman-core.cfg')):
  b=p.read_bytes();refs[name]=dict(path=remote,bytes=len(b),sha256=sha(b))
 if refs['NavigationServer.original']['sha256']!='a999725350df8503c44a25da2676a8c1a99914a99a36f24bb6334a509def4afe':raise ValueError('Wrong NavigationServer')
 tests=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_cluster_replay.py')],cwd=ROOT,capture_output=True,text=True)
 if tests.returncode:raise ValueError(tests.stderr)
 scripts=('run_cluster_replay.py','cluster_preflight.py','run_observer_smoke.py','delphi_inventory.py','project_console.py','decode_delphi_observer.py');sources=[p for d in (R,N) for p in d.iterdir() if p.suffix in ('.c','.h','.S','.sh')]
 manifest=dict(kind='native_cluster_recorded_map_replay',hook_mode='app_import_slots',startup_contract_revision=6,activation_mode="armed_native_descriptor",post_exec_identity_ack=True,canonical_image_exec=True,preserve_standard_streams=True,libc_profile=json.loads((R/'unit-libc-profile.json').read_text()),phone_must_stay_unplugged=True,live_phone_navigation=False,on_car_tested=False,cluster_display_proven=False,replay=dict(source_collection=source.name,frames=617,width=800,height=480,duration_ms=groups[-1][0],groups=len(groups),packets=len(ts)//188,transport_sha256=sha(ts),clock_discontinuity_prelude=True,explicit_arm_required=True),references=refs,elf=elf,files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()},scripts_sha256={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts},source_sha256={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in sources})
 release=R/'release';release.mkdir(exist_ok=True)
 for n,b in files.items():(release/n).write_bytes(b)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2));(release/'README.txt').write_bytes((R/'README.txt').read_bytes());bundle=R/'cluster-map-replay-v6-laptop.zip'
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
  if result.returncode or result.stdout.strip()!='4':raise ValueError('Portable assets: '+result.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),decoded617_frames_preserved=True,portable_plan_passed=True,portable_assets_passed=True,workflow_tests=tests.stderr.strip(),manifest=manifest)
 (ROOT/'delphi-analysis/control-runtime/cluster-map-replay-release.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
