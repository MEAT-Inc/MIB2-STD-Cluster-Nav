import contextlib,ftplib,hashlib,io,json,re,shlex,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_cluster_replay as m
LOG=(m.ROOT/'native/cluster-bridge/nav-launch/qemu/qemu.log').read_text()
def state(final=False):return bytes.fromhex(re.search(r'^NAV_DISCONNECT_'+('FINAL' if final else 'PENDING')+r'_HEX ([0-9a-f]+)$',LOG,re.M)[1])
def report(pid,done=False):
 w=[0]*128;w[:6]=[0x31504c52,1,512,pid,3 if done else 1,0];w[6]=1;w[7]=2;w[8]=1 if done else 0;w[10]=3 if done else 0;w[11]=564 if done else 0;w[16]=2 if done else 0;w[17]=30;w[18]=3;w[19]=612;w[21]=int(done);w[22]=7;w[36]=0x78000000;w[15]=17;w[29:32]=[200,201,202];w[37:40]=[1,2,3];w[40:43]=w[29:32];w[43]=0x123400;w[44]=17;w[45:50]=[800,480,800,480,0];w[50]=1;return struct.pack('<128I',*w)
class Tests(unittest.TestCase):
 def test_plan_and_phone_attestation_no_network(self):
  with patch.object(m.ftplib,'FTP') as ftp,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main([]),0)
  ftp.assert_not_called()
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main(['--run'])
 def test_controller_actual_qnx_reports_and_corruption(self):
  root=state()[96:224].split(b'\0')[0].decode()
  self.assertTrue(m.assess_controller(state(True),root,True)['restoration_verified']);self.assertEqual(m.assess_controller(state(),root,False)['phase'],4)
  for offset in (0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,72,80,88,96,256,260,264,268,272,400,508):
   b=bytearray(state(True));struct.pack_into('<I',b,offset,0)
   if b==state(True):continue
   if offset in (64,72,80,88):struct.pack_into('<Q',b,offset,0)
   with self.subTest(offset=offset),self.assertRaises(ValueError):m.assess_controller(b,root,True)
 def test_delivery_never_implies_visible_maps(self):
  manifest=dict(hook_mode='app_import_slots',startup_contract_revision=6,canonical_image_exec=True,preserve_standard_streams=True,post_exec_identity_ack=True,activation_mode="armed_native_descriptor",replay=dict(packets=3,groups=2),files={'replay.bin':dict(bytes=612)})
  v=m.assess_replay(report(22,True),22,manifest,True);self.assertTrue(v['packets_delivered']);self.assertFalse(v['physical_display_proven'])
  for i in (0,1,2,3,4,18,19,21,22,127):
   b=bytearray(report(22,True));struct.pack_into('<I',b,i*4,0xffffffff)
   with self.subTest(i=i),self.assertRaises(ValueError):m.assess_replay(b,22,manifest,True)
 def run_fake(self,mode='',resume=False):
  pending,final=state(),state(True);oldroot=pending[96:224].split(b'\0')[0].decode();w=struct.unpack_from('<16I',final);files={n:(bytes(612) if n=='replay.bin' else n.encode()) for n in m.NAMES};refs={n:dict(path='/stock/'+n,bytes=len(n),sha256=m.sha(n.encode())) for n in ('NavigationServer.original','NavServer.cfg.reference','procman.reference','procman-core.cfg')};profile=dict(offsets=[0x100,0x200,0x300],code=['11'*32,'22'*32,'33'*32]);manifest=dict(libc_profile=profile,hook_mode='app_import_slots',startup_contract_revision=6,canonical_image_exec=True,preserve_standard_streams=True,post_exec_identity_ack=True,activation_mode="armed_native_descriptor",references=refs,replay=dict(packets=3,groups=2),files={n:dict(bytes=len(v),sha256=m.sha(v)) for n,v in files.items()});db={v['path']:n.encode() for n,v in refs.items()};commands=[];remote=None
  class FTP:
   def __init__(self,**kw):pass
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def connect(self,*a):pass
   def login(self,*a):pass
   def voidcmd(self,*a):pass
   def mkd(self,p):nonlocal remote;remote=p
   def storbinary(self,c,f):db[c[5:]]=f.read()
   def retrbinary(self,c,save):
    if c[5:] not in db:raise ftplib.error_perm('550 missing')
    save(db[c[5:]])
  class Shell:
   def __init__(self,*a):self.actions=[];self.broken=False
   def close(self):pass
   def command(self,c,required=True):
    commands.append(c);self.actions.append(dict(command=c));token=remote[-32:]
    if c.startswith('cp '):
     _,src,dest=shlex.split(c)
     if src not in db:
      if required:raise RuntimeError('copy source absent')
      return 1
     db[remote+'/'+dest]=db[src]
    if c.startswith('test -r '):return 0 if (c[8:] if c[8:].startswith('/') else remote+'/'+c[8:]) in db else 1
    if 'pidin -p NavigationServer' in c:db[remote+'/'+c.split('> ')[1].split()[0]]=('%d NavigationServer -fcfg ../cfg/NAV/v0/NC/Delphi/NavServer.cfg\n'%(w[11] if 'after' in c else w[14])).encode()
    if 'pidin arguments >' in c:db[remote+'/'+c.split('> ')[1].split()[0]]=b'123 Most\n124 TransportServer\n125 AndroidAuto -t\n'
    if './replay_libc_check ' in c:
     db[remote+'/libc-preflight-errors.txt']=b'';db[remote+'/libc-preflight.json']=json.dumps(dict(version=1,profile_matches=mode!='preflightfail',base=0x78000000,functions=[0x78000000+v for v in profile['offsets']],entry_code=profile['code'])).encode()
     if mode=='preflightfail':return 1
    if 'start-disconnected ' in c:
     db['/dev/shmem/delphi-nav-launch-report-'+token+'.bin']=pending.replace(oldroot.encode(),remote.encode());db['/dev/shmem/delphi-nav-report-'+token+'.bin']=report(w[10]);db[remote+'/start.txt']=b'LAUNCH_OBSERVED\n';db[remote+'/nav-startup.txt']=b'REPLAY_INIT ready\n'
     if mode=='channelmissing':
      bad=bytearray(report(w[10]));struct.pack_into('<I',bad,6*4,0);db['/dev/shmem/delphi-nav-report-'+token+'.bin']=bytes(bad)
     if mode=='bootstrapfail':
      bad=bytearray(report(w[10]));struct.pack_into('<I',bad,16,4);struct.pack_into('<I',bad,20,1003);struct.pack_into('<I',bad,22*4,3);struct.pack_into('<2I',bad,18*4,0,0);db['/dev/shmem/delphi-nav-report-'+token+'.bin']=bytes(bad);db[remote+'/nav-startup.txt']=b'REPLAY_INIT failed stage=3 error=1003\n'
    if 'arm-replay ' in c:
     if mode=='armfail':
      db[remote+'/arm.txt']=b'NAV_REPLAY_ARM_REFUSED reason=identity\n';return 3
     db[remote+'/arm.txt']=b'NAV_REPLAY_ARMED\n';db['/dev/shmem/delphi-nav-report-'+token+'.bin']=report(w[10],True)
     if mode=='activationfail':
      armed=bytearray(report(w[10]));struct.pack_into('<I',armed,21*4,1);db['/dev/shmem/delphi-nav-report-'+token+'.bin']=bytes(armed)
    if 'cleanup-disconnected ' in c:
     db[remote+'/cleanup.txt']=b'LAUNCH_RESTORED\nLAUNCH_COMPLETE\n'
     if mode=='cleanupfail':return 3
     db['/dev/shmem/delphi-nav-launch-final-'+token+'.bin']=final.replace(oldroot.encode(),remote.encode())
    return 0
  def answer(prompt):
   if prompt.startswith('Select '):
    if mode=='interrupt':raise KeyboardInterrupt()
    return 'SKIP' if mode=='skip' else ''
   return 'n' if mode=='invisible' else 'y'
  ticks=iter(range(0,100000,20))
  with patch.object(m.time,'monotonic',side_effect=lambda:next(ticks)),tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'package',return_value=(files,manifest)),patch.object(m,'verify_navigation'),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch.object(m.time,'sleep'),patch('builtins.input',side_effect=answer),contextlib.redirect_stdout(io.StringIO()):
   rc=m.main(['--run','--phone-unplugged']);folder=next((Path(t)/'delphi-dump').iterdir());summary=json.loads((folder/'replay-summary.json').read_text())
   if resume:
    mode='';commands.clear();rc=m.main(['--resume',str(folder),'--phone-unplugged']);summary=json.loads((folder/'replay-summary.json').read_text())
  return rc,summary,commands
 def test_visible_replay_restore_and_one_arm(self):
  rc,s,c=self.run_fake();self.assertEqual(rc,0);self.assertTrue(s['restoration_verified']);self.assertTrue(s['cluster_maps_seen']);self.assertEqual(sum('arm-replay' in x for x in c),1);self.assertEqual(sum('cleanup-disconnected' in x for x in c),1)
 def test_arm_refusal_keeps_native_log_and_cleans_up_without_playback(self):
  rc,s,c=self.run_fake('armfail');self.assertEqual(rc,2);self.assertEqual(s['arm_command_exit'],3);self.assertIn('arm.txt',{v['file'] for v in s['artifacts']});self.assertIn('details saved in arm.txt',s['error']);self.assertTrue(s['restoration_verified']);self.assertFalse(s.get('cluster_maps_seen',False));self.assertEqual(sum('arm-replay' in x for x in c),1)
 def test_no_native_frames_does_not_preclude_complete_replay(self):
  b=bytearray(report(22,True))
  for i in (7,8,9,38):struct.pack_into('<I',b,i*4,0)
  manifest=dict(hook_mode='app_import_slots',startup_contract_revision=6,replay=dict(packets=3,groups=2),files={'replay.bin':dict(bytes=612)})
  self.assertTrue(m.assess_replay(b,22,manifest,True)['packets_delivered'])
  self.assertFalse(m.assess_replay(b,22,manifest,True)['physical_display_proven'])
 def test_stalled_activation_collects_report_and_restores_without_long_wait(self):
  rc,s,c=self.run_fake('activationfail');self.assertEqual(rc,2);self.assertTrue(s['activation_failed']);self.assertTrue(s['restoration_verified']);self.assertIn('within 10 seconds',s['error']);self.assertEqual(sum('arm-replay' in x for x in c),1)
 def test_successful_transport_with_no_visible_map_is_partial(self):
  rc,s,c=self.run_fake('invisible');self.assertEqual(rc,2);self.assertTrue(s['replay']['packets_delivered']);self.assertFalse(s['cluster_maps_seen'])
 def test_skip_restores_without_arming(self):
  rc,s,c=self.run_fake('skip');self.assertEqual(rc,2);self.assertTrue(s['restoration_verified']);self.assertFalse(any('arm-replay' in x for x in c));self.assertEqual(sum('cleanup-disconnected' in x for x in c),1)
 def test_interrupt_restores_without_arming(self):
  rc,s,c=self.run_fake('interrupt');self.assertEqual(rc,2);self.assertTrue(s['restoration_verified']);self.assertFalse(any('arm-replay' in x for x in c))
 def test_refused_cleanup_does_not_retry_or_claim_restoration(self):
  rc,s,c=self.run_fake('cleanupfail');self.assertEqual(rc,2);self.assertTrue(s['cleanup_pending']);self.assertFalse(s['restoration_verified']);self.assertEqual(sum('cleanup-disconnected' in x for x in c),1)
 def test_resume_restores_without_second_launch_or_arm(self):
  rc,s,c=self.run_fake('cleanupfail',resume=True);self.assertEqual(rc,0);self.assertTrue(s['restoration_verified']);self.assertNotIn('error',s);self.assertTrue(s['previous_errors']);self.assertFalse(any('start-disconnected' in x or 'arm-replay' in x for x in c));self.assertEqual(sum('cleanup-disconnected' in x for x in c),1)
 def test_early_bootstrap_failure_retains_startup_logs_and_never_arms(self):
  rc,s,c=self.run_fake('bootstrapfail');self.assertEqual(rc,2);self.assertTrue(s['restoration_verified']);self.assertIn('stage 3 code 1003',s['error']);self.assertFalse(any('arm-replay' in x for x in c));self.assertTrue({'start.txt','nav-startup.txt'}<={v['file'] for v in s['artifacts']})
 def test_loading_and_error_reports_do_not_require_completed_payload_profile(self):
  mft=dict(hook_mode='app_import_slots',startup_contract_revision=4,replay=dict(packets=3,groups=2),files={'replay.bin':dict(bytes=612)})
  b=bytearray(report(22));struct.pack_into('<I',b,16,0);struct.pack_into('<I',b,22*4,1);struct.pack_into('<2I',b,18*4,0,0);self.assertEqual(m.assess_replay(b,22,mft)['status'],0)
  struct.pack_into('<I',b,16,4);struct.pack_into('<I',b,20,1004);self.assertEqual(m.assess_replay(b,22,mft)['error'],1004)
 def test_old_global_hook_bundle_is_held_before_asset_reads(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'manifest.json').write_text(json.dumps(dict(kind='native_cluster_recorded_map_replay')))
   with self.assertRaisesRegex(ValueError,'global-hook'):m.package(p)
 def test_missing_channel_collects_diagnostics_restores_and_never_arms(self):
  rc,s,c=self.run_fake('channelmissing');self.assertEqual(rc,2);self.assertTrue(s['restoration_verified']);self.assertFalse(s['native_channel']['ready']);self.assertIn('no qualified native endpoint open',s['native_channel']['missing']);self.assertFalse(any('arm-replay' in x for x in c));self.assertIn('replay-channel.bin',{v['file'] for v in s['artifacts']})
 def test_channel_gate_checks_each_native_condition(self):
  good=report(22);self.assertEqual(m.native_channel_missing(good),[])
  for i,value in ((6,0),(15,0xffffffff),(44,99),(43,0),(45,799),(46,479),(47,832),(48,479),(49,32),(40,0),(29,0),(50,0),(51,9)):
   bad=bytearray(good);struct.pack_into('<I',bad,i*4,value)
   with self.subTest(i=i):self.assertTrue(m.native_channel_missing(bad))
 def test_older_report_remains_readable_for_resume(self):
  old=bytearray(report(22));old[37*4:]=bytes((128-37)*4);manifest=dict(hook_mode='app_import_slots',startup_contract_revision=3,replay=dict(packets=3,groups=2),files={'replay.bin':dict(bytes=612)})
  self.assertIsNone(m.assess_replay(old,22,manifest)['hook_calls'])
 def test_profile_mismatch_never_restarts_or_arms_navigation(self):
  rc,s,c=self.run_fake('preflightfail');self.assertEqual(rc,2);self.assertFalse(s.get('native_launch_requested',False));self.assertFalse(any('start-disconnected' in x or 'arm-replay' in x or 'cleanup-disconnected' in x for x in c));self.assertIn('not restarted',s['error']);self.assertFalse(s['libc_preflight']['profile_matches'])
if __name__=='__main__':unittest.main()
