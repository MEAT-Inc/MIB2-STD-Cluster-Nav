"""Guarded recovery ordering and refusal gates, without vehicle access."""
from pathlib import Path
import sys,json,hashlib,struct,tempfile,ftplib
from unittest.mock import patch
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import recover_live_failure as m
class RecoveryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  root=Path(__file__).resolve().parents[2];p=root/'delphi-dump/_live_failure_20261110_153835_06eec794';s=json.loads((p/'failure-summary.json').read_text());cls.pin=dict(s['pin']);cls.raw=(p/'controller-final.bin').read_bytes()
 def test_failed_controller_requires_exact_prior_state(self):
  m.failed_controller(self.raw,self.pin)
  for offset in (12,16,24,28,32,36,40,52,60,72,80,256,260,264,268):
   b=bytearray(self.raw);struct.pack_into('<I',b,offset,0xffffffff)
   with self.subTest(offset=offset),self.assertRaises(ValueError):m.failed_controller(b,self.pin)
 def test_success_record_requires_single_guarded_restart(self):
  v=dict(version=1,process_cycle_verified=True,signals_to_nav=True,termination_signal=9,stage='recover_restart',old_pid=self.pin['pid'],new_pid=2000000,new_start=self.pin['start_time']+1000)
  m.recovered_result(v,self.pin)
  for k,x in (('process_cycle_verified',False),('signals_to_nav',False),('termination_signal',2),('new_pid',self.pin['pid']),('new_start',self.pin['start_time']),('stage','identity')):
   w=dict(v);w[k]=x
   with self.subTest(k=k),self.assertRaises(ValueError):m.recovered_result(w,self.pin)
 def simulate(self,stale=False,refuse=False):
  pin=dict(self.pin);old=b'old verified helper';pin['helper_sha256']=hashlib.sha256(old).hexdigest();remote=pin['remote'];newpid=2000000;newstart=pin['start_time']+1000;files={'nav_cycle':b'new guarded helper','nav_finalize':b'new finalizer'};data={remote+'/nav_cycle':old,'/dev/shmem/delphi-nav-launch-active.bin':self.raw};commands=[];state={'cwd':remote,'active':True}
  final=bytearray(self.raw)
  for offset,x in ((12,6),(16,0),(32,0),(36,1),(44,newpid)):struct.pack_into('<I',final,offset,x)
  struct.pack_into('<Q',final,88,newstart)
  class FTP:
   def __init__(self,**kwargs):pass
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def connect(self,*args):pass
   def login(self,*args):pass
   def voidcmd(self,*args):pass
   def mkd(self,*args):pass
   def storbinary(self,c,b):data[c[5:]]=b.read()
   def retrbinary(self,c,take):
    if c[5:] not in data:raise ftplib.error_perm('550 Missing')
    take(data[c[5:]])
  class Shell:
   def __init__(self,*args):self.actions=[]
   def close(self):pass
   def command(self,c,required=True):
    commands.append(c);self.actions.append(dict(command=c));rc=0
    if c.startswith('cd '):state['cwd']=c[3:]
    elif c.startswith('cp '):_,src,dest=c.split();data[state['cwd']+'/'+dest]=data[src]
    elif c.startswith('test ! -e '):rc=int(state['active'])
    elif ' > ' in c:
     before,tail=c.split(' > ',1);dest=tail.split()[0]
     if ' inspect ' in before:
      pid=int(before.rsplit(' ',1)[1]);record=dict(version=1,readonly=True,app_id=29,state=3,pid=pid,start_time=(pin['start_time']+int(stale)) if pid==pin['pid'] else newstart,manager_pid=pin['manager_pid'],manager_start=pin['manager_start'])
     elif ' recover ' in before:
      record=dict(version=1,process_cycle_verified=not refuse,signals_to_nav=not refuse,termination_signal=9 if not refuse else 0,stage='recover_restart',old_pid=pin['pid'],new_pid=newpid,new_start=newstart);rc=3 if refuse else 0
     elif ' finalize-recovery ' in before:
      record={'finalized':True};state['active']=False;data['/dev/shmem/delphi-nav-launch-recovered-'+remote.rsplit('_',1)[1]+'.bin']=bytes(final)
     else:raise AssertionError('Unexpected command '+c)
     data[state['cwd']+'/'+dest]=json.dumps(record).encode()
    return rc
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);release=root/'native/cluster-bridge/recovery/release';release.mkdir(parents=True);manifest=dict(kind='exact_crash_nav_recovery',files={n:dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest()) for n,b in files.items()});(release/'manifest.json').write_text(json.dumps(manifest))
   for n,b in files.items():(release/n).write_bytes(b)
   with patch.object(m,'ROOT',root),patch.object(m,'load_session_identity',return_value=(pin,root,b'm')),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch.object(m,'input',return_value='y'):code=m.main(['--run','--phone-unplugged'])
   summary=json.loads(next((root/'delphi-dump').glob('*/recovery-summary.json')).read_text())
  return code,commands,summary
 def test_restart_then_finalize_once(self):
  code,c,s=self.simulate();self.assertEqual(code,0);recover=[i for i,x in enumerate(c) if './nav_cycle recover ' in x];final=[i for i,x in enumerate(c) if './nav_finalize finalize-recovery ' in x];self.assertEqual(len(recover),1);self.assertEqual(len(final),1);self.assertLess(recover[0],final[0]);self.assertTrue(s['restoration_verified'])
 def test_stale_identity_prevents_restart_and_finalization(self):
  code,c,s=self.simulate(stale=True);self.assertEqual(code,2);self.assertFalse(any(' recover ' in x or 'finalize-recovery ' in x for x in c))
 def test_guard_refusal_prevents_finalization(self):
  code,c,s=self.simulate(refuse=True);self.assertEqual(code,2);self.assertFalse(any('finalize-recovery ' in x for x in c))
 def test_default_plan_needs_no_radio(self):
  with patch.object(m.ftplib,'FTP',side_effect=AssertionError('No network')):self.assertEqual(m.main([]),0)
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
