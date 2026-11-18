"""Read-only collector behavior, stale helper refusal and portable plan gates."""
from pathlib import Path
import sys,json,hashlib,tempfile,types,ftplib,struct
from unittest.mock import patch
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import collect_live_failure as m
class CaptureTests(unittest.TestCase):
 def make_session(self,root,remote,helper,name='_disconnect_observer_20261110_150334_aaaaaaaa'):
  folder=root/'delphi-dump'/name;folder.mkdir(parents=True);b=bytearray(512);struct.pack_into('<4I',b,0,0x314e4c44,1,512,4);struct.pack_into('<I',b,40,123);struct.pack_into('<I',b,52,321);struct.pack_into('<4Q',b,64,1,654,456,0);b[96:96+len(remote)]=remote.encode();manifest=json.dumps(dict(kind='native_cluster_live_output',files=dict(nav_cycle=dict(bytes=len(helper),sha256=hashlib.sha256(helper).hexdigest())))).encode()
  (folder/'live-release-manifest.json').write_bytes(manifest);(folder/'nav-controller-final.bin').write_bytes(b);(folder/'live-bridge-summary.json').write_text(json.dumps(dict(started=True,cleanup_pending=True,remote=remote,manifest_sha256=hashlib.sha256(manifest).hexdigest())));(folder/'disconnect-summary.json').write_text(json.dumps(dict(live_cluster_requested=True,remote_directory='/ramdisk/delphi-aa-observer_'+remote.rsplit('_',1)[1],artifacts=[dict(file='nav-controller-final.bin',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())])))
  return folder
 def simulate(self,bad_helper=False):
  remote='/ramdisk/delphi-nav-bridge_'+'a'*32;helper=b'verified existing helper';pin=dict(remote=remote,pid=123,start_time=456,manager_pid=321,manager_start=654,helper_sha256=hashlib.sha256(helper).hexdigest());data={remote+'/nav_cycle':b'changed' if bad_helper else helper};commands=[];opened=[]
  for n in ('start.txt','nav-startup.txt','cleanup.txt','libc-preflight.json'):data[remote+'/'+n]=b'log\n'
  class FTP:
   def __init__(self,**kwargs):pass
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def connect(self,*args):pass
   def login(self,*args):pass
   def voidcmd(self,*args):pass
   def retrbinary(self,c,take):
    path=c[5:]
    if path not in data:raise ftplib.error_perm('550 Missing')
    take(data[path])
  class Shell:
   def __init__(self,*args):self.actions=[];opened.append(True)
   def close(self):pass
   def command(self,c,required=True):
    commands.append(c);self.actions.append(dict(command=c,exit_code=0))
    if c.startswith('test -r '):return int(c[8:] not in data)
    if c.startswith('cp '):
     _,src,dest=c.split();data[remote+'/'+dest]=data[src];return 0
    if ' > ' in c:
     before,out=c.split(' > ',1);dest=out.split()[0];blob=json.dumps({k:pin[k] for k in ('pid','start_time','manager_pid','manager_start')}).encode() if ' inspect ' in before else bytes(4096) if ' page ' in before else b'captured\n';data[remote+'/'+dest]=blob
     if ' 2> ' in out:data[remote+'/'+out.split(' 2> ')[1]]=b''
    return 0
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);self.make_session(root,remote,helper);self.assertFalse((root/'live-failure-pin.json').exists())
   with patch.object(m,'ROOT',root),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch.object(m,'register_snapshot',return_value={3:dict(sp=0x5da64)}),patch.object(m,'libc_mapping',return_value=0x1000000):code=m.main(['--run','--phone-unplugged'])
   summary=json.loads(next((root/'delphi-dump').glob('*/failure-summary.json')).read_text())
  return code,commands,opened,summary
 def test_reads_bounded_pages_and_never_restarts(self):
  code,commands,opened,s=self.simulate();self.assertEqual(code,0);self.assertTrue(s['complete']);self.assertFalse(s['signals']);self.assertFalse(s['service_restarts']);self.assertFalse(s['video'])
  helpers=[c.split('./nav_cycle ',1)[1].split()[0] for c in commands if './nav_cycle ' in c]
  self.assertEqual(set(helpers),{'inspect','page'});self.assertEqual(helpers.count('inspect'),2);self.assertLessEqual(helpers.count('page'),98)
  self.assertFalse(any(c.startswith(('kill ','rm ','reboot ')) or 'cleanup-disconnected' in c or 'start-disconnected' in c for c in commands))
 def test_changed_helper_is_not_executed(self):
  code,commands,opened,s=self.simulate(True);self.assertEqual(code,2);self.assertFalse(opened);self.assertFalse(commands)
 def test_latest_session_and_explicit_selection(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);remote='/ramdisk/delphi-nav-bridge_'+'a'*32;old=self.make_session(root,remote,b'helper');new=self.make_session(root,remote,b'helper','_disconnect_observer_20261111_150334_bbbbbbbb')
   self.assertEqual(m.load_session_identity(root)[1],new)
   self.assertEqual(m.load_session_identity(root,old.relative_to(root))[1],old)
 def test_latest_restored_session_does_not_fall_back_to_stale_process(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);remote='/ramdisk/delphi-nav-bridge_'+'a'*32;old=self.make_session(root,remote,b'helper');new=self.make_session(root,remote,b'helper','_disconnect_observer_20261111_150334_bbbbbbbb');p=new/'live-bridge-summary.json';state=json.loads(p.read_text());state['restoration_verified']=True;p.write_text(json.dumps(state))
   with self.assertRaises(ValueError):m.load_session_identity(root)
   self.assertEqual(m.load_session_identity(root,old)[1],old)
 def test_changed_controller_or_manifest_refused_before_connection(self):
  for name in ('nav-controller-final.bin','live-release-manifest.json'):
   with self.subTest(name=name),tempfile.TemporaryDirectory() as t:
    root=Path(t);folder=self.make_session(root,'/ramdisk/delphi-nav-bridge_'+'a'*32,b'helper');p=folder/name;p.write_bytes(p.read_bytes()+b'changed')
    with self.assertRaises(ValueError):m.load_session_identity(root)
 def test_default_plan_has_no_network_or_pin_dependency(self):
  with patch.object(m.ftplib,'FTP',side_effect=AssertionError('No network')):self.assertEqual(m.main([]),0)
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
