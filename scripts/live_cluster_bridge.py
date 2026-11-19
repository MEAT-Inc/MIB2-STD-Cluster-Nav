"""Orchestrate the live Nav sink with the existing disconnected AA workflow."""
from pathlib import Path
import ftplib,hashlib,io,json,re,struct,time
from project_console import log as print,prompt as input,status
from run_observer_smoke import retrieve
from run_cluster_replay import assess_controller,native_channel_missing,peers
from cluster_preflight import nav_pid

def digest(b):return hashlib.sha256(b).hexdigest()
def assess_output(b,pid=None):
 if len(b)!=512:raise ValueError('Live Nav report size')
 w=struct.unpack('<128I',b);version=w[67]
 if w[:3]!=(0x31504c52,1,512) or pid is not None and w[3]!=pid or not 0<w[3]<=0x7fffffff or w[4] not in (0,1,2,3,4) or version not in (1,2,3,4,5,6) or w[68]>2048 or w[69]>8388608 or w[72]>1 or w[75]>2097152 or w[75]%188:raise ValueError('Live Nav report identity/profile')
 if version==1 and any(w[76:]) or version>=2 and (w[79]>w[13] or w[76] not in (0,2,3,4) or w[77]>w[10] or w[78]>w[14]):raise ValueError('Live Nav close metrics')
 if version==2 and any(w[80:]) or version>=3 and ((any(w[87:]) if version==3 else any(w[102:]) if version==4 else any(w[105:]) if version==5 else any(w[110:])) or w[80]>3 or w[81]>1048576 or w[82]>4194304 or w[83]>64 or w[84]>(w[105] if version==6 else w[68]) or w[86]!=1000):raise ValueError('Live Nav startup metrics')
 if version>=4 and (w[87]>4 or w[88]>1 or w[97]>770048 or w[101]>64 or w[74]!=5 and w[101] or w[87] and not w[88] or w[87]==2 and (not w[89] or w[91]) or w[87]==3 and not w[91]):raise ValueError('Live Nav factory return metrics')
 if version>=5 and (w[102]!=250 or w[103:105]!=(4,5)):raise ValueError('Live Nav catchup timing profile')
 if version==6 and (w[105]<w[68] or w[108]>1 or w[109] not in (0,30)):raise ValueError('Live Nav extended profile')
 if w[4] in (1,2,3) and (w[22]!=7 or not w[36] or w[36]&4095):raise ValueError('Live Nav bootstrap incomplete')
 v=dict(profile_version=version,pid=w[3],status=w[4],error=w[5],frames=w[68],input_bytes=w[69],drops=w[70],source_pid=w[71],source_verified=bool(w[72]),sink_error=w[73],stop_reason=w[74],packets=w[10],bytes=w[11],rewritten_packets=w[62],suppressed_native_writes=w[8],bad_callers=w[20],closes=w[13],first_close_status=w[65],packets_at_first_close=w[66],timeline_error=w[63],active_closes=w[79] if version>=2 else None,first_active_close_status=w[76] if version>=2 else None,packets_at_active_close=w[77] if version>=2 else None,accepted_output_capture_bytes=w[75],transport_fd=struct.unpack_from('<i',b,60)[0])
 if version>=3:v.update(bootstrap_frames=w[80],bootstrap_keyframe_bytes=w[81],startup_peak_bytes=w[82],startup_peak_frames=w[83],source_frames_emitted=w[84],startup_overflows=w[85],startup_delay_ms=w[86])
 if version>=4:v['factory_return']=dict(state=w[87],requests=w[88],accepted_packets=w[89],discarded_packets=w[90],error=w[91],request_monotonic_ms=w[92]+(w[93]<<32),first_accepted_monotonic_ms=w[94]+(w[95]<<32),reason=w[96],recovery_buffer_peak_bytes=w[97],route_stop_observed=w[98],route_stop_monotonic_ms=w[99]+(w[100]<<32),discarded_source_frames=w[101])
 if version>=5:v.update(startup_initial_delay_ms=w[86],startup_delay_ms=w[102],catchup_pace_numerator=w[103],catchup_pace_denominator=w[104])
 if version==6:v.update(total_input_frames=w[105],total_input_bytes=w[106]+(w[107]<<32),diagnostic_prefix_truncated=bool(w[108]),live_seconds=w[109])
 return v

def native_factory_return_verified(v):
 r=v.get('factory_return',{})
 reason=v.get('stop_reason')
 stop_verified=(reason==5 and r.get('route_stop_observed',0)>0 and 0<r.get('route_stop_monotonic_ms',0)<=r.get('request_monotonic_ms',0)) or reason in (1,2,3)
 return bool(v.get('profile_version',0)>=4 and v.get('status')==3 and not any(v.get(k) for k in ('error','sink_error','drops','bad_callers','timeline_error')) and stop_verified and r.get('reason')==reason and r.get('state')==2 and r.get('requests')==1 and r.get('accepted_packets',0)>0 and not r.get('error') and 0<r.get('request_monotonic_ms',0)<=r.get('first_accepted_monotonic_ms',0))

def output_delivered(v,source,frames):
 count_ok=v.get('frames')==frames
 source_ok=v.get('profile_version',0)<3 or v.get('source_frames_emitted')==frames and not v.get('startup_overflows')
 if v.get('profile_version',0)>=4 and v.get('stop_reason')==5:
  emitted=v.get('source_frames_emitted',0);discarded=v.get('factory_return',{}).get('discarded_source_frames',0)
  count_ok=0<v.get('frames',0)<=frames
  source_ok=emitted>0 and emitted+discarded==v.get('frames') and not v.get('startup_overflows')
 if v.get('profile_version')==6:
  total=v['total_input_frames'];discarded=v.get('factory_return',{}).get('discarded_source_frames',0)
  rejected=1 if v.get('stop_reason')==3 and v.get('live_seconds')==30 and total==v['frames']+1 else 0
  source_ok=(v.get('source_frames_emitted',0)+discarded+rejected==total and not v.get('startup_overflows'))
 byte_count=188*v.get('packets',0)
 if v.get('profile_version')==6:byte_count&=0xffffffff
 return bool(count_ok and source_ok and v.get('source_verified') and v.get('source_pid')==source and frames and v.get('packets') and v.get('bytes')==byte_count and v['packets']==v.get('rewritten_packets') and not any(v.get(k) for k in ('error','sink_error','drops','bad_callers','timeline_error')))

def cleanup_allowed(handoff,authorized,aa_pending):return bool((not handoff or authorized) and not aa_pending)

def confirm_factory_map_locations(prompt):
 radio=prompt('Toggle factory maps to the RADIO. Once actual map graphics appear, do they work? [y/n/unknown]: ').strip().lower() in ('y','yes')
 cluster=prompt('Toggle factory maps back to the INSTRUMENT CLUSTER. Do actual map graphics appear without the mobile-navigation message? [y/n/unknown]: ').strip().lower() in ('y','yes')
 return dict(factory_radio_map_restored=radio,factory_cluster_map_restored=cluster,factory_maps_restored=radio and cluster)

class LiveBridge:
 def __init__(self,root,args,folder,aa,password):
  self.root=root;self.args=args;self.folder=folder;self.aa=aa;self.password=password;self.token=aa['remote_directory'].rsplit('_',1)[1];self.remote='/ramdisk/delphi-nav-bridge_'+self.token;self.local=folder/'live-bridge-summary.json';self.state=json.loads(self.local.read_text()) if args.resume and self.local.exists() else dict(kind='live_cluster_output',remote=self.remote,started=False,cleanup_pending=False)
  if not re.fullmatch(r'[0-9a-f]{32}',self.token):raise ValueError('Invalid live Nav namespace')
  release=root/'native/cluster-bridge/live-output/release';snapshot=self.folder/'live-release-manifest.json'
  raw=snapshot.read_bytes() if args.resume and snapshot.exists() else (release/'manifest.json').read_bytes();self.manifest=json.loads(raw)
  if self.manifest.get('kind')!='native_cluster_live_output' or self.manifest.get('recorded_video_available') is not False:raise ValueError('Wrong live-output release')
  if set(self.manifest['files'])!={'nav_launch','libdelphi_cluster.so','replay.bin','replay_libc_check','nav_cycle','live_queue_prepare'}:raise ValueError('Live Nav payload set changed')
  self.files={} if args.resume else {n:(release/n).read_bytes() for n in self.manifest['files']}
  for n,b in self.files.items():
   e=self.manifest['files'][n]
   if len(b)!=e['bytes'] or digest(b)!=e['sha256']:raise ValueError('Live-output payload changed '+n)
  stamp=digest(raw)
  if args.resume and self.state.get('manifest_sha256')!=stamp:raise ValueError('Saved live Nav manifest differs from session')
  if snapshot.exists() and digest(snapshot.read_bytes())!=stamp:raise ValueError('Saved live release manifest differs')
  if not snapshot.exists():snapshot.write_bytes(raw)
  selected=getattr(args,'live_seconds',None);saved_limit=self.state.get('live_seconds',30)
  if args.resume and selected is not None and selected!=saved_limit:raise ValueError('Resume must use saved live-run limit')
  self.state['live_seconds']=saved_limit if args.resume else 30 if selected is None else selected
  if self.state['live_seconds']==0 and not self.manifest.get('extended_live_supported'):raise ValueError('Use the current extended-run bundle')
  self.state['manifest_sha256']=stamp;self.save()
 def save(self):self.local.write_text(json.dumps(self.state,indent=2))
 def ftp(self):
  f=ftplib.FTP(timeout=self.args.timeout);f.connect(self.args.host,self.args.port);f.login(self.args.username,self.password);f.voidcmd('TYPE I');return f
 def fetch(self,name):
  with self.ftp() as f:b=retrieve(f,self.remote+'/'+name)
  (self.folder/('nav-'+name)).write_bytes(b);return b
 def command(self,text,required=True):
  self.cmd('cd '+self.remote)
  try:return self.cmd(text,required=required)
  finally:self.cmd('cd '+self.aa['remote_directory'])
 def report(self,name='live-output.bin'):
  self.cmd('cp /dev/shmem/delphi-nav-report-'+self.token+'.bin '+name);self.cmd('chmod 644 '+name);return self.fetch_aa(name)
 def prepare(self,cmd,fetch,copy):
  self.cmd=cmd;self.fetch_aa=fetch;self.copy=copy
  with self.ftp() as f:
   f.mkd(self.remote)
   for name,b in self.files.items():
    status('Uploading live Nav payload: '+name);f.storbinary('STOR '+self.remote+'/'+name,io.BytesIO(b))
    if retrieve(f,self.remote+'/'+name)!=b:raise ValueError('Live Nav upload mismatch '+name)
  from live_run_options import options_bytes
  options=options_bytes(self.token,self.state['live_seconds'])
  with self.ftp() as f:
   f.storbinary('STOR '+self.remote+'/live-options.bin',io.BytesIO(options))
   if retrieve(f,self.remote+'/live-options.bin')!=options:raise ValueError('Live-run options upload mismatch')
  for name in self.files:
   if name!='replay.bin':self.cmd('chmod 500 '+self.remote+'/'+name)
  for name,ref in self.manifest['references'].items():
   self.cmd('cp '+ref['path']+' '+self.remote+'/'+name);self.cmd('chmod 644 '+self.remote+'/'+name);b=self.fetch(name)
   if len(b)!=ref['bytes'] or digest(b)!=ref['sha256']:raise ValueError('Nav firmware/config mismatch '+name)
  self.cmd('chmod 500 '+self.remote+'/NavigationServer.original')
  self.cmd('pidin -p NavigationServer arguments > nav-live-before.txt');self.cmd('chmod 644 nav-live-before.txt');pid=nav_pid(fetch('nav-live-before.txt'))
  code=self.command('LD_PRELOAD= ./replay_libc_check > libc-preflight.json 2> libc-preflight-errors.txt',False);self.cmd('chmod 644 '+self.remote+'/libc-preflight.json');v=json.loads(self.fetch('libc-preflight.json'));p=self.manifest['libc_profile'];base=v.get('base',0)
  if code or not v.get('profile_matches') or not base or base&4095 or v.get('functions')!=[base+x for x in p['offsets']] or v.get('entry_code')!=p['code']:raise ValueError('Live Nav libc preflight refused; Nav was not restarted')
  self.state.update(started=True,cleanup_pending=True,baseline_pid=pid);self.save()
  self.command('LD_PRELOAD= ./nav_launch start-disconnected '+self.remote+' '+str(pid)+' > start.txt 2>&1 & live_nav_job=$!')
  print('Select the factory map in the instrument cluster while the live output initializes. Stop any VW route guidance before this presentation trial.')
  b,v=self.wait_channel()
  if self.manifest.get('extended_live_supported') and (v.get('profile_version')!=6 or v.get('live_seconds')!=self.state['live_seconds']):raise ValueError('Native live-run settings differ from requested mode')
  self.state['observed_pid']=v['pid'];self.save()
  if input('Wait for actual factory map graphics IN THE CLUSTER. Press Enter to arm live output, or type SKIP to restore: ').strip().upper()=='SKIP':raise RuntimeError('Live output skipped')
  self.capture_native_prefix(b)
  self.state['factory_map_confirmed']=True;self.save()
 def most_snapshot(self,label):
  try:
   inventory='most-peers-'+label+'.txt';name='most-'+label+'.json'
   self.cmd('pidin arguments > '+inventory);self.cmd('chmod 644 '+inventory);pid=peers(self.fetch_aa(inventory)).get('Most')
   if not pid:raise ValueError('Most process missing from inventory')
   rc=self.command('LD_PRELOAD= ./nav_cycle most-status '+str(pid)+' > '+name+' 2>&1',False);self.cmd('chmod 644 '+self.remote+'/'+name);raw=self.fetch(name)
   self.state.setdefault('most_snapshots',[]).append(dict(file='nav-'+name,exit_code=rc,sha256=digest(raw)));self.save()
  except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:self.state.setdefault('diagnostic_errors',[]).append(dict(file='most-'+label,error=str(e)))
 def capture_native_prefix(self,b):
  n=struct.unpack_from('<I',b,53*4)[0]
  if not n:return
  try:
   if n>1048576:raise ValueError('Native map prefix exceeds bound')
   raw=self.copy('/dev/shmem/delphi-nav-source-'+self.token+'.bin','native-map-prefix.bin')
   if len(raw)!=1048576:raise ValueError('Native map prefix mapping size')
   (self.folder/'native-map-prefix.ts').write_bytes(raw[:n]);self.state['native_source_capture']=dict(bytes=n,sha256=digest(raw[:n]));self.save()
  except (OSError,ValueError,RuntimeError,ftplib.Error) as e:self.state.setdefault('diagnostic_errors',[]).append(dict(file='native-map-prefix.bin',error=str(e)))
 def wait_channel(self,timeout=120,clock=None,sleep=None):
  clock=clock or time.monotonic;sleep=sleep or time.sleep;until=clock()+timeout
  source='/dev/shmem/delphi-nav-report-'+self.token+'.bin'
  while clock()<until:
   # The launcher returns before the constructor creates/ftruncates this file.
   # Missing/empty report is normal bootstrap progress, never a cleanup trigger.
   if self.cmd('test -s '+source,required=False)==0:
    b=self.report('live-nav-ready.bin')
    if len(b)==512:
     w=struct.unpack('<128I',b)
     if w[4]==4:raise RuntimeError('Live Nav bootstrap refused at stage '+str(w[22])+' error '+str(w[5]))
     if w[4] in (1,2,3):
      v=assess_output(b);self.state['observed_pid']=v['pid'];self.save()
      if v['status']==1 and not native_channel_missing(b):return b,v
   sleep(.5)
  raise TimeoutError('Live Nav channel not ready; phone handoff cancelled')
 def navigation_image(self):
  b=(self.folder/'nav-NavigationServer.original').read_bytes();e=self.manifest['references']['NavigationServer.original']
  if len(b)!=e['bytes'] or digest(b)!=e['sha256']:raise ValueError('Saved verified Nav image changed')
  return b
 def phone_ready(self,cmd,fetch,copy,pid):
  self.cmd=cmd;self.fetch_aa=fetch;self.copy=copy
  if self.command('LD_PRELOAD= ./live_queue_prepare '+self.token+' '+str(pid)+' '+str(self.state['observed_pid'])+' > queue-bind.txt 2>&1',False):raise RuntimeError('Live queue binding refused; phone handoff cancelled')
  self.state['source_pid']=pid;self.save()
  b,v=self.wait_channel(timeout=45)
  if native_channel_missing(b):raise RuntimeError('Native map channel changed after AA startup')
  if self.manifest.get('startup_delay_ms'):self.most_snapshot('before-arm')
  if self.command('LD_PRELOAD= ./nav_launch arm-replay '+self.remote+' > arm.txt 2>&1',False):raise RuntimeError('Live Nav arm refused')
  requested=self.report('live-nav-arm-requested.bin');v=assess_output(requested,self.state['observed_pid'])
  if struct.unpack_from('<I',requested,84)[0]!=1:raise RuntimeError('Live Nav arm flag was not retained')
  if v['error'] or v['status'] not in (1,2):raise RuntimeError('Live Nav stopped before phone handoff')
  self.state['armed']=True;self.state['activation']='first_verified_phone_frame';self.save()
  if self.manifest.get('route_presentation_trial'):
   from review_route_policy import assess_route_policy
   until=time.monotonic()+10
   while True:
    policy=assess_route_policy(copy('/dev/shmem/delphi-route-policy-'+self.token+'.bin','route-policy-ready.bin'),pid,self.state['observed_pid'])
    if self.manifest.get('route_policy_report_version') and policy['version']!=self.manifest['route_policy_report_version']:raise RuntimeError('Route presentation report version differs from release; phone handoff cancelled')
    if self.manifest.get('extended_live_supported') and policy.get('live_seconds')!=self.state['live_seconds']:raise RuntimeError('Route policy live-run mode differs; phone handoff cancelled')
    if policy['eligible'] and policy['state']==1:break
    if time.monotonic()>=until:raise TimeoutError('Route presentation gate not ready; phone handoff cancelled')
    time.sleep(.2)
   self.state['route_policy_ready']=policy;self.save()
   print('Extended route presentation ready: handoff remains deferred while the verified bridge is healthy, until phone disconnect.' if self.state.get('live_seconds')==0 else 'Bounded route presentation trial ready: phone route handoff is deferred for at most 40 seconds while the verified bridge is healthy.')
  print('Live output armed; VW video continues until the first verified phone keyframe.')
 def capture_output(self,v):
  b=self.copy('/dev/shmem/delphi-nav-output-'+self.token+'.bin','nav-accepted-output.bin');n=v['accepted_output_capture_bytes']
  if len(b)!=2097152 or n>len(b):raise ValueError('Accepted-output mapping size')
  raw=b[:n];(self.folder/'nav-accepted-output.ts').write_bytes(raw)
  self.state['accepted_output_capture']=dict(bytes=n,sha256=digest(raw),bounded_prefix=True)
 def confirm_automatic_factory_return(self):
  if 'factory_automatic_return_observed' in self.state:return
  answer=input('BEFORE any map-location toggle or cleanup: after unplugging the phone, did the factory COMPASS or MAP return automatically IN THE CLUSTER, with the mobile-navigation message gone? [y/n/unknown]: ').strip().lower()
  self.state.update(factory_automatic_return_observed=answer in ('y','yes'),factory_automatic_return_answer=answer,factory_automatic_return_before_manual_toggle=True);self.save()
 def collect(self,cmd,fetch,copy):
  self.cmd=cmd;self.fetch_aa=fetch;self.copy=copy;self.confirm_automatic_factory_return();v=assess_output(self.report(),self.state['observed_pid']);self.state['output']=v;self.capture_output(v);self.most_snapshot('after-playback');self.state['live_maps_seen']=input('Did LIVE Android Auto maps appear and update IN THE INSTRUMENT CLUSTER during the route? [y/n/unknown]: ').strip().lower() in ('y','yes');self.save();return v
 def cleanup(self,cmd,fetch,copy):
  if not self.state.get('started'):return
  if self.state.get('restoration_verified'):
   if not self.state.get('factory_maps_restored'):self.confirm_factory_maps()
   return
  try:return self._cleanup(cmd,fetch,copy)
  finally:self.collect_lifecycle(cmd,copy)
 def collect_lifecycle(self,cmd,copy):
  if not hasattr(self,'folder'):return
  token=self.token
  sources=[(self.remote+'/'+n,'navlog-'+n) for n in ('start.txt','nav-startup.txt','cleanup.txt','queue-bind.txt')]
  sources.append(('/dev/shmem/delphi-route-policy-'+token+'.bin','route-policy-final.bin'))
  sources.extend(('/dev/shmem/delphi-nav-lifecycle-'+token+'-'+phase+'.txt','navlog-'+phase+'.txt') for phase in ('start-cycle','start-recover','cleanup-cycle','cleanup-recover'))
  for source,name in sources:
   try:
    if cmd('test -r '+source,required=False)==0:copy(source,name)
   except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:self.state.setdefault('diagnostic_errors',[]).append(dict(file=name,error=str(e)))
  self.save()
 def _cleanup(self,cmd,fetch,copy):
  self.cmd=cmd;self.fetch_aa=fetch;self.copy=copy
  if not self.state.get('started') or self.state.get('restoration_verified'):return
  try:
   self.state['output']=assess_output(self.report('live-output-before-cleanup.bin'),self.state.get('observed_pid'));self.capture_output(self.state['output'])
  except (OSError,ValueError,ftplib.Error):pass
  with self.ftp() as ftp:
   for name in ('nav_launch','nav_cycle'):
    b=retrieve(ftp,self.remote+'/'+name);e=self.manifest['files'][name]
    if len(b)!=e['bytes'] or digest(b)!=e['sha256']:raise ValueError('Staged Nav cleanup executable changed '+name)
  final='/dev/shmem/delphi-nav-launch-final-'+self.token+'.bin';pending='/dev/shmem/delphi-nav-launch-report-'+self.token+'.bin'
  if cmd('test -r '+final,required=False)!=0:
   until=time.monotonic()+35
   while cmd('test -r '+pending,required=False)!=0:
    if time.monotonic()>=until:raise TimeoutError('Live Nav cleanup checkpoint not ready')
    time.sleep(.5)
   assess_controller(copy(pending,'nav-controller-pending.bin'),self.remote,False)
   code=self.command('LD_PRELOAD= ./nav_launch cleanup-disconnected '+self.remote+' > cleanup.txt 2>&1',False);self.state['cleanup_exit']=code
  v=assess_controller(copy(final,'nav-controller-final.bin'),self.remote,True);self.state.update(v);self.state['cleanup_pending']=False
  cmd('pidin -p NavigationServer arguments > nav-live-restored.txt');cmd('chmod 644 nav-live-restored.txt')
  if nav_pid(fetch('nav-live-restored.txt'))!=v['restored_pid']:raise ValueError('Restored Nav PID mismatch')
  self.confirm_factory_maps()
 def confirm_factory_maps(self):
  # Eventual manual recovery cannot establish automatic pre-cleanup return.
  if getattr(self,'manifest',{}).get('automatic_factory_return_required') and 'factory_automatic_return_observed' not in self.state:
   self.state.update(factory_automatic_return_observed=False,factory_automatic_return_answer='unavailable_before_cleanup',factory_automatic_return_before_manual_toggle=False);self.save()
  self.state.update(confirm_factory_map_locations(input));self.save()
