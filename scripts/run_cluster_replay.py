"""Replay captured AA maps through the native cluster writer. Phone stays unplugged."""
from project_console import console_session, log as print, prompt as input, status, progress
import argparse,datetime as dt,ftplib,getpass,hashlib,io,json,re,shlex,struct,time,uuid
from pathlib import Path
import delphi_inventory as d
from run_observer_smoke import Shell,retrieve
from cluster_preflight import nav_pid,verify_navigation
ROOT=Path(__file__).resolve().parents[1]
PREFIX='/ramdisk/delphi-nav-bridge_'
NAMES=('nav_launch','libdelphi_cluster.so','replay.bin','replay_libc_check')
def sha(b):return hashlib.sha256(b).hexdigest()
def remote_root(v):
 if not re.fullmatch(re.escape(PREFIX)+r'[0-9a-f]{32}',v):raise ValueError('Invalid replay namespace')
 return v

def package(p):
 m=json.loads((p/'manifest.json').read_text())
 if m.get('hook_mode')!='app_import_slots' or m.get('startup_contract_revision')!=6 or m.get('canonical_image_exec') is not True or m.get('preserve_standard_streams') is not True or m.get('post_exec_identity_ack') is not True or m.get('activation_mode')!='armed_native_descriptor':raise ValueError('Old global-hook/name-guard replay bundle is held; extract the corrected v6 bundle')
 if m.get('kind')!='native_cluster_recorded_map_replay' or m.get('phone_must_stay_unplugged') is not True or m.get('live_phone_navigation') is not False or set(m['files'])!=set(NAMES):raise ValueError('Wrong replay release')
 result={}
 for name in NAMES:
  b=(p/name).read_bytes();entry=m['files'][name]
  if len(b)!=entry['bytes'] or sha(b)!=entry['sha256'] or not 0<len(b)<=(8388608 if name=='replay.bin' else 131072):raise ValueError('Release hash/size mismatch: '+name)
  result[name]=b
 return result,m

def assess_controller(b,remote,final):
 if len(b)!=512:raise ValueError('Controller size')
 w=struct.unpack_from('<16I',b);t=struct.unpack_from('<4Q',b,64);raw=b[96:224]
 if w[:3]!=(0x314e4c44,1,512) or w[15]!=1 or not all(t[:3]) or any(b[400:]) or b'\0' not in raw or raw.split(b'\0')[0].decode()!=remote or any(raw.split(b'\0',1)[1]):raise ValueError('Controller identity/layout')
 if any(not 0<x<=0x7fffffff for x in (w[10],w[12],w[13],w[14])) or len({w[10],w[12],w[13],w[14]})!=4:raise ValueError('Controller PID identity')
 if struct.unpack_from('<2I',b,256)!=(20,1):raise ValueError('Checkpoint not complete')
 if final:
  if w[3]!=6 or w[4] or w[5:9]!=(1,1,0,0) or w[9]!=1 or struct.unpack_from('<2I',b,264)!=(1,1) or not t[3] or not w[11] or w[11] in (w[10],w[12],w[13],w[14]):raise ValueError('Native stock restoration failed')
 else:
  if w[3]!=4 or w[9] or any(b[264:272]):raise ValueError('Not pending disconnected cleanup')
 cwd=b[272:400]
 if b'\0' not in cwd or not cwd.startswith(b'/') or any(cwd.split(b'\0',1)[1]):raise ValueError('Invalid inherited cwd')
 return dict(observed_pid=w[10],restored_pid=w[11],manager_pid=w[13],baseline_pid=w[14],phase=w[3],controller_error=w[4],cwd=cwd.split(b'\0')[0].decode(),restoration_verified=bool(w[9]))

def assess_replay(b,pid,manifest,final=False):
 if len(b)!=512:raise ValueError('Replay size')
 w=struct.unpack('<128I',b);app_only=manifest.get('hook_mode')=='app_import_slots';telemetry=app_only and manifest.get('startup_contract_revision',0)>=4
 if w[:4]!=(0x31504c52,1,512,pid) or w[4] not in (0,1,2,3,4) or w[21] not in (0,1) or (any(w[52:] if telemetry else w[37:]) if app_only else any(w[22:])):raise ValueError('Replay report identity/profile')
 if app_only and w[22]>7:raise ValueError('Unknown bootstrap stage')
 if app_only and manifest.get('startup_contract_revision',0)>=3 and w[4] in (1,2,3) and (not w[36] or w[36]&4095):raise ValueError('Validated libc base missing')
 if w[4] in (1,2,3) and (w[18]!=manifest['replay']['packets'] or w[19]!=manifest['files']['replay.bin']['bytes'] or app_only and w[22]!=7):raise ValueError('Replay not fully initialized')
 complete=w[4]==3 and w[21]==1 and not w[5] and w[10]==w[18] and w[11]==188*w[18] and w[16]==manifest['replay']['groups'] and w[6]>=1 and not w[20]
 if final and w[10]>manifest['replay']['packets']:raise ValueError('Replay sent too many packets')
 return dict(status=w[4],error=w[5],bootstrap_stage=w[22] if app_only else None,import_before=list(w[23:26]) if app_only else [],native_functions=list(w[26:29]) if app_only else [],import_slots=list(w[32:35]) if app_only else [],import_install_result=struct.unpack_from('<i',b,140)[0] if app_only else None,libc_base=w[36] if app_only else None,packets=w[10],bytes=w[11],suppressed_writes=w[8],zero_progress_writes=w[12],bad_callers=w[20],groups=w[16],packets_delivered=complete,physical_display_proven=False,hook_calls=dict(open=w[37],write=w[38],close=w[39]) if telemetry else None,retained_imports=list(w[40:43]) if telemetry else [],encoder=w[43] if telemetry else None,encoder_fd=struct.unpack_from('<i',b,176)[0] if telemetry else None,encoder_geometry=list(w[45:50]) if telemetry else [],inspection_heartbeat=w[50] if telemetry else None,inspection_error=w[51] if telemetry else None)

def native_channel_missing(b):
 w=struct.unpack('<128I',b);missing=[]
 if not w[6]:missing.append('no qualified native endpoint open')
 if w[15]&0x80000000 or w[44]&0x80000000 or w[15]!=w[44]:missing.append('native and encoder descriptor mismatch or absent')
 if not w[43]:missing.append('encoder absent')
 if tuple(w[45:50])!=(800,480,800,480,0):missing.append('encoder geometry is not native 800x480')
 if not all(w[29:32]) or w[40:43]!=w[29:32]:missing.append('application imports no longer point at replay wrappers')
 if not w[50]:missing.append('inspection heartbeat absent')
 if w[51]:missing.append('inspection error '+str(w[51]))
 return missing

def wait_native_channel(fetch_report,pid,manifest,seconds=60,clock=None,sleep=None):
 clock=clock or time.monotonic;sleep=sleep or time.sleep;deadline=clock()+seconds
 while True:
  progress('Waiting for the native map channel (limit '+str(seconds)+'s).', key='native-channel')
  b=fetch_report();v=assess_replay(b,pid,manifest);missing=native_channel_missing(b)
  if v['error'] or v['status']==4:missing.insert(0,'replay error '+str(v['error']))
  if not missing:return b,v,[]
  if v['error'] or v['status']==4 or clock()>=deadline:return b,v,missing
  sleep(.5)

def peers(data):
 result={}
 for line in data.decode(errors='replace').splitlines():
  m=re.match(r'\s*(\d+)\s+(\S+)',line)
  if m:
   name=m[2].rsplit('/',1)[-1]
   if name in ('Most','MostCanRouter','TransportServer','DisplayManagement','AndroidAuto','screen-cda','procman'):
    if name in result:raise ValueError('Duplicate peer: '+name)
    result[name]=int(m[1])
 return result

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--run',action='store_true');g.add_argument('--resume',type=Path);p.add_argument('--phone-unplugged',action='store_true');p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--ask-password',action='store_true');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=90);a=p.parse_args(argv)
 if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 60<=a.timeout<=180:p.error('Invalid ports/timeout')
 print('RECORDED MAP REPLAY: this is the saved map video, not live guidance. Keep phone unplugged throughout.')
 if not a.run and not a.resume:print('Plan only: --run --phone-unplugged; ignition on, Ethernet connected. Select factory map on cluster when requested.');return 0
 if not a.phone_unplugged:p.error('--phone-unplugged is required for the entire replay and cleanup')
 files,manifest=package(ROOT/'native/cluster-bridge/replay/release');base=ROOT/'delphi-dump'
 for parent in (base,*base.parents):d.reject_link(parent)
 base.mkdir(exist_ok=True)
 if a.resume:
  folder=a.resume.resolve()
  if folder.parent!=base.resolve() or not re.fullmatch(r'_cluster_replay_[0-9_]+_[0-9a-f]{8}',folder.name):raise ValueError('Resume outside replay collection')
  summary=json.loads((folder/'replay-summary.json').read_text());remote=remote_root(summary['remote']);session=folder/('resume-'+uuid.uuid4().hex[:8]);session.mkdir()
  if summary['controller_sha256']!=sha(files['nav_launch']):raise ValueError('Resume controller differs')
  for field in ('error','cleanup_error'):
   if field in summary:summary.setdefault('previous_errors',[]).append(summary.pop(field))
  summary.update(restoration_verified=False,cleanup_pending=True,cluster_maps_seen=False,peer_pids_unchanged=False)
 else:
  token=uuid.uuid4().hex;remote=remote_root(PREFIX+token);folder=base/('_cluster_replay_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8]);folder.mkdir();session=folder
  summary=dict(remote=remote,controller_sha256=sha(files['nav_launch']),replay_source='recorded_android_auto',cleanup_pending=False,restoration_verified=False,artifacts=[],actions=[])
 manifest_blob=json.dumps(manifest,sort_keys=True).encode()
 if not a.resume:
  (folder/'release-manifest.json').write_bytes(manifest_blob);summary.update(shim_sha256=sha(files['libdelphi_cluster.so']),replay_sha256=sha(files['replay.bin']),release_manifest_sha256=sha(manifest_blob))
 else:
  saved=(folder/'release-manifest.json').read_bytes()
  if sha(saved)!=summary.get('release_manifest_sha256'):raise ValueError('Saved release provenance changed')
  manifest=json.loads(saved)
 token=remote[-32:];shell=None;password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser';blobs={p.name:p.read_bytes() for p in folder.iterdir() if p.is_file() and p.name!='replay-summary.json'}
 def persist():(folder/'replay-summary.json').write_text(json.dumps(summary,indent=2))
 def fetch(name):
  with ftplib.FTP(timeout=a.timeout) as ftp:
   progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
   ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
   if name in ('nav-startup.txt','libc-preflight-errors.txt'):
    data=bytearray()
    def save_log(block):
     if len(data)+len(block)>1048576:raise ValueError('Startup log exceeds1MiB')
     data.extend(block)
    ftp.retrbinary('RETR '+remote+'/'+name,save_log);b=bytes(data)
   else:b=retrieve(ftp,remote+'/'+name)
  (folder/name).write_bytes(b);blobs[name]=b;summary['artifacts']=[x for x in summary['artifacts'] if x['file']!=name]+[dict(file=name,bytes=len(b),sha256=sha(b))];return b
 def cmd(s,required=True):return shell.command(s,required=required)
 def copy(source,name):cmd('cp '+shlex.quote(source)+' '+name);cmd('chmod 644 '+name);return fetch(name)
 cleanup_attempted=False
 def startup_logs():
  if not shell or shell.broken:return
  for name in ('start.txt','nav-startup.txt'):
   try:
    if cmd('test -r '+name,False)==0:cmd('chmod 644 '+name);fetch(name)
   except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:summary.setdefault('diagnostic_errors',[]).append(dict(file=name,error=str(e)))
 def cleanup_native():
  nonlocal cleanup_attempted
  startup_logs()
  summary['cleanup_pending']=True;persist()
  final_path='/dev/shmem/delphi-nav-launch-final-'+token+'.bin'
  if cmd('test -r '+final_path,False)!=0:
   pending=wait_copy('/dev/shmem/delphi-nav-launch-report-'+token+'.bin','controller-pending.bin',35);summary['pending_state']=assess_controller(pending,remote,False)
  cleanup_attempted=True
  summary['cleanup_command_exit']=cmd('LD_PRELOAD= ./nav_launch cleanup-disconnected '+shlex.quote(remote)+' > cleanup.txt 2>&1',False);summary['cleanup_marker_complete']=b'LAUNCH_COMPLETE' in fetch('cleanup.txt')
  state=assess_controller(copy(final_path,'controller.bin'),remote,True);summary.update(state);summary['cleanup_pending']=False
  cmd('pidin -p NavigationServer arguments > nav-after.txt');cmd('chmod 644 nav-after.txt')
  if nav_pid(fetch('nav-after.txt'))!=state['restored_pid']:raise ValueError('Restored Nav PID differs')
  cmd('pidin arguments > peers-after.txt');cmd('chmod 644 peers-after.txt');summary['peers_after']=peers(fetch('peers-after.txt'));summary['peer_pids_unchanged']=summary.get('peers_before')==summary['peers_after']
  summary['replay']=assess_replay(copy('/dev/shmem/delphi-nav-report-'+token+'.bin','replay.bin.report'),state['observed_pid'],manifest,True)
 def wait_copy(source,name,seconds):
  end=time.monotonic()+seconds
  while cmd('test -r '+source,False):
   if time.monotonic()>end:raise TimeoutError('Native report not ready: '+name)
   time.sleep(.5)
  return copy(source,name)
 persist()
 try:
  with ftplib.FTP(timeout=a.timeout) as ftp:
   progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
   ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
   if not a.resume:
    ftp.mkd(remote)
    for name,b in files.items():
     status('Uploading and verifying payload: '+name)
     ftp.storbinary('STOR '+remote+'/'+name,io.BytesIO(b))
     if retrieve(ftp,remote+'/'+name)!=b:raise ValueError('Upload readback mismatch')
   elif retrieve(ftp,remote+'/nav_launch')!=files['nav_launch']:raise ValueError('Staged controller changed')
  shell=Shell(a,session);cmd('cd '+shlex.quote(remote))
  if a.resume:
   for name,ref in manifest['references'].items():
    b=fetch(name)
    if len(b)!=ref['bytes'] or sha(b)!=ref['sha256']:raise ValueError('Saved stock reference changed')
  if not a.resume:
   for name in ('nav_launch','libdelphi_cluster.so','replay_libc_check'):cmd('chmod 500 '+name)
   for name,ref in manifest['references'].items():
    b=copy(ref['path'],name)
    if len(b)!=ref['bytes'] or sha(b)!=ref['sha256']:raise ValueError('Stock firmware/config differs: '+name)
   verify_navigation(blobs['NavigationServer.original']);cmd('chmod 500 NavigationServer.original')
   cmd('pidin -p NavigationServer arguments > nav-before.txt');cmd('chmod 644 nav-before.txt');pid=nav_pid(fetch('nav-before.txt'))
   cmd('pidin arguments > peers-before.txt');cmd('chmod 644 peers-before.txt');summary['peers_before']=peers(fetch('peers-before.txt'))
   preflight_code=cmd('LD_PRELOAD= ./replay_libc_check > libc-preflight.json 2> libc-preflight-errors.txt',False)
   cmd('chmod 644 libc-preflight-errors.txt');fetch('libc-preflight-errors.txt');cmd('chmod 644 libc-preflight.json');preflight=json.loads(fetch('libc-preflight.json'));summary['libc_preflight']=preflight;persist()
   profile=manifest['libc_profile'];base_address=preflight.get('base',0)
   if preflight_code or preflight.get('version')!=1 or preflight.get('profile_matches') is not True or not base_address or base_address&4095 or preflight.get('functions')!=[base_address+v for v in profile['offsets']] or preflight.get('entry_code')!=profile['code']:raise RuntimeError('Libc preflight mismatch; NavigationServer was not restarted')
   print('Captured libc profile matches; starting the navigation replay setup.',flush=True)
   summary['native_launch_requested']=True;summary['cleanup_pending']=True;persist();cmd('LD_PRELOAD= ./nav_launch start-disconnected '+shlex.quote(remote)+' '+str(pid)+' > start.txt 2>&1 & nav_replay_job=$!')
   print('Select the factory navigation MAP VIEW in the instrument cluster. The test will substitute the saved Android Auto map recording.',flush=True)
   deadline=time.monotonic()+25
   while True:
    ready=wait_copy('/dev/shmem/delphi-nav-report-'+token+'.bin','replay-ready.bin',max(0,deadline-time.monotonic()));w=struct.unpack('<128I',ready)
    if not any(w):
     if time.monotonic()>deadline:raise TimeoutError('Bootstrap header never initialized')
     time.sleep(.2);continue
    summary['bootstrap']=assess_replay(ready,w[3],manifest)
    if w[4]==4:raise RuntimeError('Replay bootstrap failed at stage '+str(w[22])+' code '+str(w[5]))
    if w[4]==1:break
    if time.monotonic()>deadline:raise TimeoutError('Replay initialization stalled at stage '+str(w[22]))
    time.sleep(.2)
   print('Waiting up to 60 seconds for the native map channel. Select the factory navigation MAP VIEW in the instrument cluster.',flush=True)
   channel,channel_state,missing=wait_native_channel(lambda:copy('/dev/shmem/delphi-nav-report-'+token+'.bin','replay-channel.bin'),w[3],manifest)
   summary['native_channel']=dict(ready=not missing,missing=missing,report=channel_state);persist()
   if missing:raise RuntimeError('Native map channel unavailable; recording was not armed: '+'; '.join(missing))
   if input('Select the navigation MAP VIEW IN THE CLUSTER (it may say Starting map). Press Enter to play the recording; type SKIP to restore instead: ').strip().upper()=='SKIP':raise RuntimeError('Replay skipped by operator')
   summary['arm_command_exit']=cmd('LD_PRELOAD= ./nav_launch arm-replay '+shlex.quote(remote)+' > arm.txt 2>&1',False);fetch('arm.txt');persist()
   if summary['arm_command_exit']:raise RuntimeError('Replay arm refused (code '+str(summary['arm_command_exit'])+'); details saved in arm.txt')
   activation_deadline=time.monotonic()+10;end=time.monotonic()+120;last=None
   while time.monotonic()<end:
    if cmd('test -r /dev/shmem/delphi-nav-report-'+token+'.bin',False)==0:
     b=copy('/dev/shmem/delphi-nav-report-'+token+'.bin','replay-progress.bin');w=struct.unpack('<128I',b)
     progress('Replay packets delivered: '+str(w[10])+' / '+str(manifest['replay']['packets']), key='replay-packets')
     if w[4]!=last:print('Replay state:',{1:'waiting for native map writer',2:'playing recorded map',3:'recording finished',4:'stopped with error'}.get(w[4],'initializing'),flush=True);last=w[4]
     if w[4] in (3,4):break
     if w[15]&0x80000000 and w[4]==2:summary['native_channel_closed_early']=True;break
     if w[4]==1 and time.monotonic()>=activation_deadline:
      summary['activation_failed']=True;summary['activation_report']=assess_replay(b,w[3],manifest);persist();raise RuntimeError('Armed replay did not activate within 10 seconds; current descriptor/hook/encoder report saved')
    time.sleep(.5)
   else:summary['playback_timeout']=True
  cleanup_native()
  summary['cluster_maps_seen']=input('Did the recorded Google Maps view appear IN THE INSTRUMENT CLUSTER? [y/n/unknown]: ').strip().lower() in ('y','yes')
 except (OSError,EOFError,ValueError,RuntimeError,KeyboardInterrupt,ftplib.Error) as e:summary['error']=(type(e).__name__+': '+str(e)).replace(password,'[redacted]')
 finally:
  if shell and not shell.broken and summary.get('native_launch_requested') and not summary.get('restoration_verified') and not cleanup_attempted:
   try:cleanup_native()
   except (OSError,EOFError,ValueError,RuntimeError,KeyboardInterrupt,ftplib.Error) as e:summary['cleanup_error']=type(e).__name__+': '+str(e)
  if shell and not shell.broken and summary.get('native_launch_requested'):
   for name in ('start.txt','nav-startup.txt','cleanup.txt'):
    if shell.broken:break
    try:
     if cmd('test -r '+name,False)==0:cmd('chmod 644 '+name);fetch(name)
    except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:summary.setdefault('diagnostic_errors',[]).append(dict(file=name,error=str(e)))
   for name,command in (('nav-current.txt','pidin -p NavigationServer arguments'),('peers-current.txt','pidin arguments'),('nav-path-current.txt','ls -l /extbin/apps/bin/NavigationServer')):
    if shell.broken:break
    try:cmd(command+' > '+name+' 2>&1',False);cmd('chmod 644 '+name,False);fetch(name)
    except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:summary.setdefault('diagnostic_errors',[]).append(dict(file=name,error=str(e)))
  if shell:
   summary['actions']=summary.get('actions',[])+shell.actions;shell.close()
  persist()
 print('Saved:',folder)
 status('Stock NavigationServer process restoration: '+('VERIFIED' if summary.get('restoration_verified') else 'NOT VERIFIED'), 'OK' if summary.get('restoration_verified') else 'WARN')
 print('Replay packets delivered:',summary.get('replay',{}).get('packets',0),'/',manifest['replay']['packets'])
 if summary['cleanup_pending']:print('Cleanup pending. Keep phone unplugged; resume: python scripts/run_cluster_replay.py --resume "'+str(folder)+'" --phone-unplugged')
 passed=summary.get('restoration_verified') and summary.get('peer_pids_unchanged') and summary.get('replay',{}).get('packets_delivered') and summary.get('cluster_maps_seen')
 print('Recorded maps confirmed on cluster; live phone navigation remains separate.' if passed else 'Return this collection, including any partial result.')
 return 0 if passed else 2
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
