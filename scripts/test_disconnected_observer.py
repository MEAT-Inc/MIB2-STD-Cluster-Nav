"""Offline gates for the new version3 capture/cleanup split. No vehicle access."""
import contextlib,ftplib,io,json,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_disconnected_observer as m
from test_androidauto_observer import AssessmentTests
def factory_report(status=1):
 h=[0]*64;h[:18]=[0x31504645,1,256,43,1,1,status,0,0,0x78000000,0x1000,0x2000,0,0,0,0,1,1];h[18:30]=[0,1,1,1,1,1,1,1,1,1,0,0];return struct.pack('<64I',*h)
class FactoryReportTests(unittest.TestCase):
 def test_exact_factory_report_and_mutations(self):
  b,root,refs=DisconnectedTests().fixture(False,60,1)
  with patch.object(m.old,'REFERENCES',refs):trace=m.assess_final(b,root,60)['decoded_log']
  result=m.assess_factory(factory_report(),43,0,trace);self.assertTrue(result['isolated_factory_passed']);self.assertFalse(result['secondary_endpoints_registered'])
  for offset in (0,4,8,12,16,20,24,28,32,36,40,44,48,56,64,68,72,76,80,84,88,92,96,100,104,108,112,116,120,252):
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
 def simulate(self,mode='',resume=False,phone=False,factory=False,seconds=None):
  state=dict(data={},commands=[],connections=0)
  seconds=seconds or (60 if phone else 20)
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
  with patch.object(m,'ROOT',root),patch.object(m,'package',return_value=uploads),patch.object(m.old,'REFERENCES',refs),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch.object(m,'wait_for_capture_ready',side_effect=RuntimeError('not ready') if mode=='readyfail' else None,return_value=f'LAUNCH_READY capture_seconds={seconds}\n'.encode()),patch('builtins.input',side_effect=answer),contextlib.redirect_stdout(io.StringIO()):
    code=m.main(['--run','--phone-unplugged']+(['--phone-capture'] if phone else [])+(['--factory-probe'] if factory else []))
    folder=next((root/'delphi-dump').iterdir());summary=json.loads((folder/'disconnect-summary.json').read_text())
    if resume:
     self.assertTrue(summary['cleanup_pending']);state['first']=False;state['commands']=[]
     if mode=='tamper':state['data'][state['remote']+'/observer_launch']+=b'tamper'
     code=m.main(['--resume',str(folder),'--phone-unplugged']+(['--factory-probe'] if factory else []));summary=json.loads((folder/'disconnect-summary.json').read_text())
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
if __name__=='__main__':unittest.main()

