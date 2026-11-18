"""Identity and failure diagnostics for the route-presentation gate."""
from pathlib import Path
import struct,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from review_route_policy import assess_route_policy
class PolicyTests(unittest.TestCase):
 def data(self,**values):
  w=[0]*128;w[:7]=[0x31545052,1,512,44,1,0,55];w[17]=1
  for i,v in values.items():w[int(i)]=v
  return struct.pack('<128I',*w)
 def test_ready(self):self.assertTrue(assess_route_policy(self.data(),44,55)['eligible'])
 def test_error_is_preserved(self):
  with self.assertRaisesRegex(RuntimeError,'startup error 4'):assess_route_policy(self.data(**{'5':4,'6':0}),44,55)
 def test_identity_remains_strict(self):
  for b,p,n in ((self.data(),45,55),(self.data(),44,56),(self.data(**{'18':1}),44,55),(bytes(512),44,55)):
   with self.assertRaises(ValueError):assess_route_policy(b,p,n)
 def test_deferred_then_released(self):
  v=assess_route_policy(self.data(**{'4':3,'7':2,'8':1,'9':1,'10':2,'16':2}),44,55);self.assertEqual(v['released'],1)
 def test_impossible_counters(self):
  with self.assertRaises(ValueError):assess_route_policy(self.data(**{'7':1,'8':2,'10':1,'16':1}),44,55)
 def test_v2_records_native_focus_and_refusal(self):
  b=bytearray(self.data(**{'1':2,'16':1,'18':1,'19':85,'20':1,'21':4,'22':0xffffffff,'25':3,'29':1,'30':12,'31':1,'32':1234,'34':1,'35':85,'36':1,'37':4}))
  v=assess_route_policy(b,44,55);self.assertEqual(v['last_request']['native_focus'],1);self.assertEqual(v['last_request']['decision'],'bridge_not_eligible');self.assertEqual(v['trace'][0]['monotonic_ms'],1234)
  struct.pack_into('<I',b,37*4,99)
  with self.assertRaisesRegex(ValueError,'trace decision'):assess_route_policy(b,44,55)
 def test_v2_rejects_hidden_trace_tail(self):
  with self.assertRaises(ValueError):assess_route_policy(self.data(**{'1':2,'127':1}),44,55)
 def test_firmware_native_focus_one_becomes_hmi_two(self):
  root=Path(__file__).resolve().parents[2];b=(root/'delphi-dump/extbin/apps/bin/AndroidAutoServices').read_bytes();ph=struct.unpack_from('<I',b,28)[0];size,n=struct.unpack_from('<HH',b,42)
  for i in range(n):
   typ,offset,va,_,filesize,*_=struct.unpack_from('<8I',b,ph+i*size)
   if typ==1 and va<=0x112760 and 0x112774<=va+filesize:
    words=struct.unpack_from('<5I',b,offset+0x112760-va);break
  else:self.fail('Captured focus conversion missing')
  self.assertEqual(words,(0xe3530001,0x1a000001,0xe3a03002,0xea000000,0xe3a03001))
  # cmp native,#1; bne other; mov HMI,#2; b done; other: mov HMI,#1.
  compare,yes,no=words[0]&255,words[2]&255,words[4]&255
  self.assertEqual(yes if 1==compare else no,2);self.assertEqual(yes if 2==compare else no,1)
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
