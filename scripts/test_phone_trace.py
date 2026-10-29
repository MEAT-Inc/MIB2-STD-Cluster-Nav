import contextlib,ftplib,io,json,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_phone_trace as m
class PhoneTraceTests(unittest.TestCase):
 def simulate(self,mode=''):
  state={'data':{},'commands':[],'sessions':[],'inputs':0,'now':0}
  class FTP:
   def __init__(self,**kw):pass
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def connect(self,*args):pass
   def login(self,*args):pass
   def voidcmd(self,*args):pass
   def mkd(self,path):state['remote']=path
   def storbinary(self,cmd,f):state['data'][cmd[5:]]=f.read()
   def retrbinary(self,cmd,save):
    data=state['data'].get(cmd[5:])
    if data is None:raise ftplib.error_perm('550')
    if mode=='transfer_partial' and cmd.endswith('/trace.bin'):save(data[:3]);raise TimeoutError('interrupted transfer')
    if mode=='slow_transfer' and cmd.endswith('/trace.bin'):state['now']+=121
    save(data+(b'bad' if mode=='tamper' and cmd.endswith('trace_reader') else b''))
  class Shell:
   def __init__(self,a,folder):self.broken=False;self.actions=[];self.closed=False;state['sessions'].append(self)
   def close(self):self.closed=True
   def command(self,cmd,required=True):
    if self.closed:raise AssertionError('closed session reused')
    if cmd.rstrip().endswith('&'):raise AssertionError('Invalid bare background command would break Shell completion marker')
    self.actions.append(dict(command=cmd,exit_code=0));state['commands'].append(cmd)
    if cmd.startswith('cd ') and mode=='collect_cd' and len(state['sessions'])==2:raise RuntimeError('bad collection cd')
    remote=state['remote']+'/'
    if '> stock-' in cmd:state['data'][remote+cmd.split('> ')[1].split()[0]]=(b'99' if mode=='pid_change' and 'after' in cmd else b'42')+b' AndroidAuto -t\n'
    if '> trace-before' in cmd:state['data'][remote+'trace-before.txt']=b'*.15361 x.22 ESTABLISHED' if mode=='busy' else b'*.15361 *.* LISTEN'
    if '> maps-' in cmd:state['data'][remote+cmd.split('> ')[1].split()[0]]=b'normal libraries'
    if '> trace-after' in cmd:state['data'][remote+'trace-after.txt']=b'*.15361 LISTEN'
    if './trace_reader ' in cmd:state['data'][remote+'trace-job.txt']=b'TRACE_READER_READY pid=43 seconds=180 max_bytes=16777216\n'
  def prompt(text):
   state['inputs']+=1
   if state['inputs']==1:state['now']=0 if mode=='too_short' else 211
   if state['inputs']==1:
    self.assertTrue(state['sessions'][0].closed)
    remote=state['remote']+'/'
    reason='peer_closed' if mode=='partial' else 'duration';rc=2 if mode=='partial' else 0
    state['data'][remote+'trace.bin']=b'AA trace'
    state['data'][remote+'trace-report.txt']=('TRACE_READER_REPORT version=1 pid=43 seconds=180 limit=16777216 bytes=8 elapsed_ms=180001 reason='+reason+' rc='+str(rc)+' error=0\n').encode()
    return ''
   return 'y' if state['inputs']==2 else 'n'
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'package',return_value=b'executable'),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch('builtins.input',side_effect=prompt),patch.object(m.time,'monotonic',side_effect=lambda:state['now']),contextlib.redirect_stdout(io.StringIO()):
   code=m.main(['--run']);folder=next(Path(t).glob('delphi-dump/*'));r=json.loads((folder/'phone-trace-summary.json').read_text())
  return code,state,r
 def test_plan_no_network(self):
  with patch.object(m,'package') as package,patch.object(m.ftplib,'FTP') as ftp,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main([]),0);package.assert_not_called();ftp.assert_not_called()
 def test_two_session_success_no_app_control(self):
  code,s,r=self.simulate();self.assertEqual(code,0);self.assertTrue(r['stock_pid_unchanged']);self.assertFalse(r['display_recovery_verified']);self.assertEqual(len(s['sessions']),2)
  self.assertTrue(next(c for c in s['commands'] if './trace_reader ' in c).endswith('& delphi_trace_job=$!'))
  for cmd in s['commands']:self.assertFalse(any(word in cmd for word in ('kill','reboot','observer_launch','pathmgr','cp ')))
 def test_busy_backend_no_handoff(self):
  _,s,r=self.simulate('busy');self.assertEqual(s['inputs'],0);self.assertFalse(any('./trace_reader ' in c for c in s['commands']));self.assertFalse(r['capture_complete'])
 def test_tampered_upload_no_shell(self):
  _,s,r=self.simulate('tamper');self.assertFalse(s['sessions']);self.assertFalse(r['capture_complete'])
 def test_pid_change_or_partial_fails_capture_gate(self):
  for mode in ('pid_change','partial'):
   with self.subTest(mode=mode):code,s,r=self.simulate(mode);self.assertEqual(code,2);self.assertFalse(r['capture_complete'])
 def test_collect_cd_failure_no_relative_writes(self):
  code,s,r=self.simulate('collect_cd');self.assertEqual(code,2);self.assertTrue(s['commands'][-1].startswith('cd '))
 def test_early_handoff_and_slow_transfer_fail(self):
  for mode in ('too_short','slow_transfer'):
   with self.subTest(mode=mode):code,s,r=self.simulate(mode);self.assertEqual(code,2);self.assertFalse(r['capture_complete'])
 def test_partial_transfer_preserved(self):
  code,s,r=self.simulate('transfer_partial');self.assertEqual(code,2)
  part=next(a for a in r['artifacts'] if a.get('file')=='trace.bin.partial');self.assertEqual(part['bytes'],3);self.assertEqual(part['status'],'partial')
 def test_report_mutations(self):
  valid=b'TRACE_READER_REPORT version=1 pid=43 seconds=180 limit=16777216 bytes=1 elapsed_ms=180001 reason=duration rc=0 error=0\n'
  self.assertTrue(m.assess_report(valid,b'a',43)['capture_complete'])
  for raw,pid,blob in ((valid,44,b'a'),(valid,43,b'aa'),(valid.replace(b'180001',b'2'),43,b'a'),(valid.replace(b'reason=duration',b'reason=byte_limit'),43,b'a'),(b'bad',43,b'a')):
   with self.assertRaises(ValueError):m.assess_report(raw,blob,pid)
 def test_readiness_ended_and_bad_pid(self):
  with patch.object(m.time,'monotonic',return_value=0):
   for data in (b'TRACE_READER_REPORT',b'TRACE_READER_READY pid=0 seconds=180 max_bytes=16777216\n'):
    with self.assertRaises(ValueError):m.ready(lambda:data,0)
if __name__=='__main__':unittest.main()
