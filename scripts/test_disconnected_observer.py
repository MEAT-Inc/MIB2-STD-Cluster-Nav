"""Offline gates for the new version3 capture/cleanup split. No vehicle access."""
import contextlib,ftplib,io,json,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_disconnected_observer as m
from test_androidauto_observer import AssessmentTests
def factory_report(status=1):
 h=[0]*64;h[:18]=[0x31504645,2,256,43,1,1,status,0,0,0x78000000,0x1000,0x2000,0,0,0,0,1,1];h[18:30]=[0,1,1,1,1,1,1,1,1,1,0,0];h[30:37]=[1,1,1,1,1,1,10];h[37]=1;h[38]=0x124e54;return struct.pack('<64I',*h)
def secondary_raw():return b'\0\0\0\1\x67\x42\0\x1e'+b'\0\0\0\1\x65'+bytes(range(7))
def secondary_report(empty=False):
 h=[0]*128;h[:4]=[0x31505253,1,512,43];h[4]=3 if empty else 5;h[6:19]=[1,1,0x1000,0x3000,0x4000,0x5000,9,10,0,0,2,1,1];h[36]=386;h[39]=8388608;h[40]=1;h[42]=2
 if not empty:h[20:34]=[1,1,1,1,1,1,2,12,len(secondary_raw()),8,0,2,37,9]
 return struct.pack('<128I',*h)
def discovery_capture(empty=False):
 b=bytearray(24600);struct.pack_into('<6I',b,0,0x32534344,43,0 if empty else 2,0 if empty else 2,0,0 if empty else 1)
 if not empty:b[24:26]=b'\0\6';b[8216:8218]=b'\0\6'
 return bytes(b)
class SecondaryReportTests(unittest.TestCase):
 def test_received_video_is_not_a_cluster_transport_claim(self):
  r=m.assess_secondary(secondary_report(),secondary_raw(),43,0x1000);self.assertTrue(r['secondary_video_received']);self.assertTrue(r['secondary_trial_passed']);self.assertEqual(r['annexb_nal_types'],[5,7]);self.assertFalse(r['cluster_transport_connected'])
 def test_no_phone_setup_remains_an_observation(self):
  r=m.assess_secondary(secondary_report(True),b'',43,0x1000);self.assertTrue(r['secondary_attempt_completed']);self.assertFalse(r['secondary_video_received']);self.assertEqual(r['state'],'awaiting_phone_setup')
 def test_report_identity_reserved_and_size_mutations_reject(self):
  for off in (0,4,8,12,16,32,48,52,56,60,64,156,160,168,508):
   b=bytearray(secondary_report());struct.pack_into('<I',b,off,0xffffffff)
   with self.subTest(off=off),self.assertRaises(ValueError):m.assess_secondary(b,secondary_raw(),43,0x1000)
 def test_partial_capture_does_not_pass(self):
  r=m.assess_secondary(secondary_report(),secondary_raw()[:-1],43,0x1000);self.assertTrue(r['secondary_video_received']);self.assertFalse(r['secondary_trial_passed'])
class DiscoveryCaptureTests(unittest.TestCase):
 def test_packet_headers_and_empty_capture(self):
  self.assertTrue(m.assess_discovery_capture(discovery_capture(),43)['captured']);self.assertFalse(m.assess_discovery_capture(discovery_capture(True),43)['captured'])
 def test_wrong_identity_and_bounds_reject(self):
  for offset in (0,4,8,12,16,20,24,8216):
   b=bytearray(discovery_capture());struct.pack_into('<I',b,offset,0xffffffff)
   with self.subTest(offset=offset),self.assertRaises(ValueError):m.assess_discovery_capture(b,43)
class FactoryReportTests(unittest.TestCase):
 def test_exact_factory_report_and_mutations(self):
  b,root,refs=DisconnectedTests().fixture(False,60,1)
  with patch.object(m.old,'REFERENCES',refs):trace=m.assess_final(b,root,60)['decoded_log']
  result=m.assess_factory(factory_report(),43,0,trace);self.assertTrue(result['isolated_factory_passed']);self.assertFalse(result['secondary_endpoints_registered'])
  for offset in (0,4,8,12,16,20,24,28,32,36,40,44,48,56,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,124,128,132,136,140,144,148,152,156,252):
   bad=bytearray(factory_report());struct.pack_into('<I',bad,offset,0xffffffff)
   with self.subTest(offset=offset),self.assertRaises(ValueError):m.assess_factory(bad,43,0,trace)
class DisconnectedTests(unittest.TestCase):
 def fixture(self,pending=False,seconds=20,count=0):
  b,root,refs=AssessmentTests().fixture(count=count);r=bytearray(b['controller.bin']);struct.pack_into('<I',r,4,3);struct.pack_into('<4I',r,256,seconds,1,0 if pending else 1,0 if pending else 1)
  if pending:
   struct.pack_into('<I',r,12,4);struct.pack_into('<I',r,36,0);struct.pack_into('<I',r,44,0);struct.pack_into('<Q',r,88,0)
  b['controller.bin']=bytes(r);return b,root,refs
 def test_plan_no_network(self):
  with patch.object(m,'package') as p,patch.object(m.ftplib,'FTP') as ftp,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main([]),0);p.assert_not_called();ftp.assert_not_called()
 def test_requires_physical_phone_removal(self):
  with patch.object(m.ftplib,'FTP') as ftp,contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main(['--run'])
  ftp.assert_not_called()
 def test_pending_not_restored(self):
  b,root,_=self.fixture(True);r=m.validate_report(b['controller.bin'],root,True);self.assertEqual(r['phase'],4);self.assertEqual(r['cleanup_authorized'],0)
  with self.assertRaises(ValueError):m.validate_report(b['controller.bin'],root,False)
 def test_final_restores_even_zero_phone_calls(self):
  b,root,refs=self.fixture(False)
  with patch.object(m.old,'REFERENCES',refs):r=m.assess_final(b,root)
  self.assertTrue(r['controller_trial_passed']);self.assertTrue(r['completed_restored']);self.assertFalse(r['captured_registration']);self.assertFalse(r['display_recovery_verified'])
 def test_v3_flags_and_reserved_reject(self):
  for pending in (False,True):
   b,root,_=self.fixture(pending)
   for offset in (0,4,8,12,16,60,96,256,260,264,268,272,508):
    raw=bytearray(b['controller.bin']);struct.pack_into('<I',raw,offset,0xffffffff)
    with self.subTest(pending=pending,offset=offset),self.assertRaises(ValueError):m.validate_report(raw,root,pending)
 def test_final_needs_explicit_authorization(self):
  b,root,refs=self.fixture();raw=bytearray(b['controller.bin']);struct.pack_into('<I',raw,264,0);b['controller.bin']=bytes(raw)
  with patch.object(m.old,'REFERENCES',refs),self.assertRaises(ValueError):m.assess_final(b,root)
 def test_phone_package_gate(self):
  with tempfile.TemporaryDirectory() as temp:
   p=Path(temp);files={n:n.encode() for n in m.old.NAMES}
   for n,b in files.items():(p/n).write_bytes(b)
   manifest=dict(kind='disconnected_observer_control_trial',files={n:dict(bytes=len(b),sha256=m.old.sha(b)) for n,b in files.items()})
   (p/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaises(ValueError):m.package(p,phone=True)
   manifest.update(phone_trial_enabled=True,capture_profiles=[20,60]);(p/'manifest.json').write_text(json.dumps(manifest));self.assertEqual(m.package(p,phone=True),files)
class WorkflowTests(unittest.TestCase):
 def simulate(self,mode='',resume=False,phone=False,factory=False,seconds=None,secondary=False):
  if secondary:phone=factory=True
  state=dict(data={},commands=[],connections=0)
  seconds=seconds or (20 if factory else (60 if phone else 20))
  pending,fixture_root,refs=DisconnectedTests().fixture(True,seconds,1 if phone else 0)
  final,_,_=DisconnectedTests().fixture(False,seconds,1 if phone else 0)
  uploads={name:name.encode() for name in m.old.NAMES}
  class FTP:
   def __init__(self,**kw):state['connections']+=1
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def connect(self,*args):
    if mode=='connectfail':raise TimeoutError('offline connection timeout')
   def login(self,*args):pass
   def voidcmd(self,*args):pass
   def mkd(self,path):state['remote']=path
   def storbinary(self,cmd,source):state['data'][cmd[5:]]=source.read()
   def retrbinary(self,cmd,save):
    if cmd[5:] not in state['data']:raise ftplib.error_perm('550 absent')
    save(state['data'][cmd[5:]])
  class Shell:
   def __init__(self,a,folder):self.broken=False;self.actions=[];self.closed=False;state.setdefault('shells',[]).append(self)
   def close(self):self.closed=True
   def command(self,cmd,required=True):
    state['commands'].append(cmd);self.actions.append(dict(command=cmd))
    if cmd.startswith('cd ') and mode=='cd':raise RuntimeError('failed cd')
    remote=state['remote'];data=state['data']
    if cmd.startswith('cp '):
     source,dest=cmd.split()[1:];data[remote+'/'+dest]=pending[dest] if dest in refs or dest=='procman-core.cfg' else data[source]
    if '> stock-' in cmd:
     name=cmd.split('> ')[1].split()[0];data[remote+'/'+name]=final['stock-after.txt'] if 'after' in name else final['stock-before.txt']
    if 'start-disconnected ' in cmd:
     data[remote+'/start.txt']=final['launch.txt'].replace(fixture_root.encode(),remote.encode()).split(b'LAUNCH_RESTORED')[0]
     data['/dev/shmem/delphi-aa-report-'+remote[-32:]+'.bin']=pending['controller.bin'].replace(fixture_root.encode(),remote.encode())
     return 0 if ' & ' in cmd else 2
    if 'cleanup-disconnected ' in cmd:
     data[remote+'/cleanup.txt']=b'LAUNCH_RESTORED\nLAUNCH_COMPLETE\n'
     if mode=='cleanupfail':return 3
     data['/dev/shmem/delphi-aa-final-'+remote[-32:]+'.bin']=final['controller.bin'].replace(fixture_root.encode(),remote.encode())
     data['/dev/shmem/delphi-observer-aa-'+remote[-32:]+'.bin']=final['observer.bin']
     if factory:data['/dev/shmem/delphi-endpoint-factory-'+remote[-32:]+'.bin']=factory_report(status=2 if mode=='factoryfail' else 1)
     if secondary:
      data['/dev/shmem/delphi-secondary-report-'+remote[-32:]+'.bin']=secondary_report(mode=='noframes')
      data['/dev/shmem/delphi-secondary-video-'+remote[-32:]+'.h264']=b'' if mode=='noframes' else secondary_raw()
      data['/dev/shmem/delphi-secondary-discovery-'+remote[-32:]+'.bin']=discovery_capture()
    if cmd.startswith('test -r '):
     state['pending_checks']=state.get('pending_checks',0)+1
     return 1 if mode=='pendingnever' or mode=='pendinglater' and state['pending_checks']<3 else 0
    if cmd.startswith('test -f '):return 0 if cmd[8:] in data else 1
    if cmd.startswith('if test -r '):
     source=cmd.split()[3].rstrip(';');dest=cmd.split(' cp ')[1].split(';')[0].split()[1]
     if source in data:data[remote+'/'+dest]=data[source]
    return 0
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   def answer(prompt):
    if prompt.startswith('Once navigation'):
     self.assertTrue(state['shells'][-1].closed);return ''
    self.assertNotIn('driver door',prompt.lower());self.assertNotIn('displaying normally',prompt.lower())
    self.assertFalse(any('cleanup-disconnected ' in c for c in state['commands']))
    return 'later' if mode=='decline' or resume and state.get('first',True) else 'PHONE REMOVED'
  with patch.object(m,'ROOT',root),patch.object(m,'package',return_value=uploads),patch.object(m.old,'REFERENCES',refs),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch.object(m,'wait_for_capture_ready',side_effect=RuntimeError('not ready') if mode=='readyfail' else None,return_value=f'LAUNCH_READY capture_seconds={seconds}\n'.encode()),patch.object(m.time,'sleep'),(patch.object(m.time,'monotonic',side_effect=[0,0,0,0,31]) if mode=='pendingnever' else contextlib.nullcontext()),patch('builtins.input',side_effect=answer),contextlib.redirect_stdout(io.StringIO()):
    code=m.main(['--run','--phone-unplugged']+(['--phone-capture'] if phone else [])+(['--secondary-stream'] if secondary else ['--factory-probe'] if factory else []))
    folder=next((root/'delphi-dump').iterdir());summary=json.loads((folder/'disconnect-summary.json').read_text())
    if resume:
     self.assertTrue(summary['cleanup_pending']);state['first']=False;state['commands']=[]
     if mode=='tamper':state['data'][state['remote']+'/observer_launch']+=b'tamper'
     code=m.main(['--resume',str(folder),'--phone-unplugged']+(['--secondary-stream'] if secondary else ['--factory-probe'] if factory else []));summary=json.loads((folder/'disconnect-summary.json').read_text())
  return code,state,summary
 def test_decline_leaves_pending_no_cleanup(self):
  code,s,r=self.simulate('decline');self.assertEqual(code,2);self.assertTrue(r['cleanup_pending']);self.assertFalse(r['operator_cleanup_confirmed']);self.assertFalse(any('cleanup-disconnected ' in c for c in s['commands']))
 def test_explicit_cleanup_once(self):
  code,s,r=self.simulate();self.assertEqual(code,0);self.assertTrue(r['controller_trial_passed']);self.assertFalse(r['display_recovery_verified']);self.assertEqual(sum('cleanup-disconnected ' in c for c in s['commands']),1)
 def test_cleanup_failure_preserves_pending_without_retry(self):
  code,s,r=self.simulate('cleanupfail');self.assertEqual(code,2);self.assertTrue(r['cleanup_pending']);self.assertIn('error',r);self.assertEqual(sum('cleanup-disconnected ' in c for c in s['commands']),1)
 def test_failed_cd_has_no_relative_writes(self):
  code,s,r=self.simulate('cd');self.assertEqual(code,2);self.assertEqual(len(s['commands']),1);self.assertFalse(r['controller_trial_passed'])
 def test_resume_same_root_without_restart(self):
  code,s,r=self.simulate(resume=True);self.assertEqual(code,0);self.assertFalse(any('start-disconnected ' in c for c in s['commands']));self.assertEqual(sum('cleanup-disconnected ' in c for c in s['commands']),1)
 def test_resume_tamper_refused_before_shell(self):
  code,s,r=self.simulate('tamper',resume=True);self.assertEqual(code,2);self.assertFalse(s['commands']);self.assertTrue(r['cleanup_pending'])
 def test_phone_handoff_and_disconnected_cleanup(self):
  code,s,r=self.simulate(phone=True);self.assertEqual(code,0);self.assertTrue(r['phone_capture_completed']);self.assertEqual(r['capture_seconds'],60);self.assertTrue(r['captured_registration']);self.assertEqual(len(s['shells']),2)
  launches=[c for c in s['commands'] if 'start-disconnected ' in c];self.assertEqual(len(launches),1);self.assertTrue(launches[0].endswith('phone > start.txt 2>&1 & delphi_aa_job=$!'))
  self.assertFalse(any('wait ' in c or 'kill ' in c for c in s['commands']));self.assertEqual(sum('cleanup-disconnected ' in c for c in s['commands']),1)
 def test_phone_capture_passes_from_registration_without_observation_prompts(self):
  code,s,r=self.simulate(phone=True);self.assertEqual(code,0);self.assertTrue(r['controller_trial_passed']);self.assertTrue(r['phone_capture_completed'])
 def test_readiness_failure_never_handoffs_or_cleans_up(self):
  code,s,r=self.simulate('readyfail',phone=True);self.assertEqual(code,2);self.assertFalse(r.get('phone_handoff_ready',False));self.assertFalse(any('cleanup-disconnected ' in c for c in s['commands']))
 def test_phone_resume_keeps_profile_no_second_start(self):
  code,s,r=self.simulate(resume=True,phone=True);self.assertEqual(code,0);self.assertTrue(r['phone_capture_completed']);self.assertTrue(r['phone_capture_requested']);self.assertFalse(any('start-disconnected ' in c for c in s['commands']))
 def test_phone_decline_never_cleans_up(self):
  code,s,r=self.simulate('decline',phone=True);self.assertEqual(code,2);self.assertTrue(r['cleanup_pending']);self.assertFalse(any('cleanup-disconnected ' in c for c in s['commands']))
 def test_connection_timeout_never_launches_controller(self):
  code,s,r=self.simulate('connectfail');self.assertEqual(code,2);self.assertFalse(s['commands']);self.assertFalse(r.get('native_launch_requested',False))
 def test_factory_probe_passes_with_phone_and_native_report(self):
  code,s,r=self.simulate(phone=True,factory=True);self.assertEqual(code,0);self.assertTrue(r['factory_probe_passed']);self.assertTrue(r['phone_capture_completed']);self.assertFalse(r['factory_probe']['secondary_endpoints_registered'])
 def test_factory_refusal_preserves_stock_restoration_without_passing(self):
  code,s,r=self.simulate('factoryfail',phone=True,factory=True);self.assertEqual(code,2);self.assertTrue(r['controller_trial_passed']);self.assertFalse(r['cleanup_pending']);self.assertFalse(r['factory_probe_passed']);self.assertEqual(sum('cleanup-disconnected ' in c for c in s['commands']),1)
 def test_factory_resume_uses_same_experiment_without_relaunch(self):
  code,s,r=self.simulate(resume=True,phone=True,factory=True);self.assertEqual(code,0);self.assertTrue(r['factory_probe_passed']);self.assertFalse(any('start-disconnected ' in c for c in s['commands']))
 def test_factory_without_phone_profile_rejected_before_network(self):
  with patch.object(m.ftplib,'FTP') as ftp,contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main(['--run','--factory-probe','--phone-unplugged'])
  ftp.assert_not_called()
 def test_factory_uses_fast_twenty_second_phone_capture_without_suffix(self):
  code,s,r=self.simulate(phone=True,factory=True,seconds=20);self.assertEqual(code,0);self.assertEqual(r['capture_seconds'],20);self.assertTrue(r['phone_capture_completed'])
  launch=next(c for c in s['commands'] if 'start-disconnected ' in c);self.assertTrue(launch.endswith('> start.txt 2>&1 & delphi_aa_job=$!'));self.assertNotIn(' phone ',launch)
 def test_early_reconnect_polls_without_failing_copy(self):
  code,s,r=self.simulate('pendinglater',phone=True,factory=True);self.assertEqual(code,0);self.assertEqual(s['pending_checks'],3);self.assertTrue(r['factory_probe_passed'])
 def test_missing_checkpoint_never_authorizes_cleanup(self):
  code,s,r=self.simulate('pendingnever',phone=True,factory=True);self.assertEqual(code,2);self.assertIn('checkpoint not ready',r['error']);self.assertFalse(any('cleanup-disconnected ' in c for c in s['commands']))
 def test_secondary_receives_and_preserves_cleanup(self):
  code,s,r=self.simulate(secondary=True);self.assertEqual(code,0);self.assertTrue(r['secondary_video_received']);self.assertTrue(r['secondary_trial_passed']);self.assertTrue(r['factory_probe_passed']);self.assertEqual(r['capture_seconds'],20)
 def test_secondary_no_frames_still_keeps_native_restoration(self):
  code,s,r=self.simulate('noframes',secondary=True);self.assertEqual(code,2);self.assertTrue(r['controller_trial_passed']);self.assertFalse(r['secondary_video_received']);self.assertEqual(r['secondary']['state'],'awaiting_phone_setup')
 def test_secondary_resume_uses_same_experiment(self):
  code,s,r=self.simulate(resume=True,secondary=True);self.assertEqual(code,0);self.assertTrue(r['secondary_video_received']);self.assertFalse(any('start-disconnected ' in c for c in s['commands']))
class ReadinessTests(unittest.TestCase):
 def test_twenty_second_readiness_after_checkpoint_is_accepted(self):
  data=b'LAUNCH_READY capture_seconds=20\nLAUNCH_CAPTURE_DONE\nLAUNCH_AWAITING_DISCONNECTED_CLEANUP\n'
  with patch.object(m.time,'monotonic',return_value=1):self.assertEqual(m.wait_for_capture_ready(lambda:data,0,20),data)
 def test_wrong_profile_is_bounded(self):
  with patch.object(m.time,'monotonic',side_effect=[1,26]),patch.object(m.time,'sleep'),self.assertRaises(RuntimeError):m.wait_for_capture_ready(lambda:b'LAUNCH_READY capture_seconds=60\n',0,20)
if __name__=='__main__':unittest.main()

