"""Cleanup-only behavior and AA-before-Nav ordering for interrupted sessions."""
from pathlib import Path
import sys,json,struct,tempfile,hashlib,ftplib
from unittest.mock import patch
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import finish_live_session as m
class FinishTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  root=Path(__file__).resolve().parents[2];source=root/'delphi-dump/_disconnect_observer_20261117_134509_a3a6c5c7';cls.source=source;cls.original=json.loads((source/'disconnect-summary.json').read_text());cls.state=json.loads((source/'live-bridge-summary.json').read_text());cls.manifest=(source/'live-release-manifest.json').read_bytes();cls.output=(source/'live-nav-armed.bin').read_bytes();cls.helper=(root/'native/cluster-bridge/keyframe-probe/release/observer_launch').read_bytes()
  prior=root/'delphi-dump/_disconnect_observer_20261110_140421_9fba06f2';old=json.loads((prior/'disconnect-summary.json').read_text())['remote_directory'];new=cls.original['remote_directory'];cls.pending=(prior/'controller-pending.bin').read_bytes().replace(old.encode(),new.encode());cls.final=(prior/'controller.bin').read_bytes().replace(old.encode(),new.encode())
 def test_aa_cleanup_checks_checkpoint_and_stock_pid(self):
  commands=[];remote=self.original['remote_directory'];pid=struct.unpack_from('<I',self.final,44)[0]
  def cmd(c,required=True):commands.append(c);return 1 if c.startswith('test -r /dev/shmem/delphi-aa-final-') else 0
  def fetch(n):return ('pid Arguments\n '+str(pid)+' AndroidAuto -t -X2\n').encode() if n.endswith('stock.txt') else b'LAUNCH_COMPLETE'
  state=m.cleanup_aa(cmd,lambda source,n:self.pending if 'aa-report-' in source else self.final,fetch,remote);self.assertEqual(state['restored_pid'],pid);self.assertEqual(sum('cleanup-disconnected' in c for c in commands),1)
 def test_corrupt_checkpoint_prevents_cleanup_command(self):
  commands=[]
  def cmd(c,required=True):commands.append(c);return 1 if 'aa-final-' in c else 0
  with self.assertRaises(ValueError):m.cleanup_aa(cmd,lambda *a:bytes(512),lambda *a:b'',self.original['remote_directory'])
  self.assertFalse(any('cleanup-disconnected' in c for c in commands))
 def simulate(self,fail_aa=False,inactive=False):
  order=[];owner=self
  class FTP:
   def __init__(self,**kw):pass
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def connect(self,*a):pass
   def login(self,*a):pass
   def voidcmd(self,*a):pass
   def retrbinary(self,c,take):take(owner.helper)
  class Shell:
   def __init__(self,*a):self.actions=[]
   def close(self):pass
   def command(self,c,required=True):self.actions.append(dict(command=c));return 0 if not c.startswith('test ! -e ') or inactive else 1
  class Bridge:
   def __init__(self,*a):self.state=dict(owner.state)
   def report(self,*a):return owner.output
   def capture_output(self,*a):pass
   def cleanup(self,*a):order.append('nav');self.state.update(restoration_verified=True,factory_maps_restored=True)
   def save(self):pass
  def aa(*a):
   order.append('aa')
   if fail_aa:raise RuntimeError('AA refused')
   return dict(restored_pid=42)
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)
   with patch.object(m,'ROOT',root),patch.object(m,'session_metadata',return_value=(self.source,self.original,self.state,self.manifest)),patch.object(m,'Shell',Shell),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'LiveBridge',Bridge),patch.object(m,'cleanup_aa',side_effect=aa),patch.object(m,'input',return_value='y'):code=m.main(['--run','--phone-unplugged'])
  return code,order
 def test_both_apps_are_finished_in_order(self):
  code,order=self.simulate();self.assertEqual(code,0);self.assertEqual(order,['aa','nav'])
 def test_aa_refusal_does_not_start_nav_cleanup(self):
  code,order=self.simulate(True);self.assertEqual(code,2);self.assertEqual(order,['aa'])
 def test_inactive_controllers_need_no_restart(self):
  code,order=self.simulate(inactive=True);self.assertEqual(code,0);self.assertEqual(order,[])
 def test_default_plan_has_no_radio_actions(self):
  with patch.object(m.ftplib,'FTP',side_effect=AssertionError('No network')):self.assertEqual(m.main([]),0)
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
