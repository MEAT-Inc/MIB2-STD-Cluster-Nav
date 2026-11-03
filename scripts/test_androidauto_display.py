from project_console import console_session
import json,struct,unittest
from decode_androidauto_display import assess,decode,discovery,HEADER,RECORD,CAPACITY,MAGIC
class DisplayTests(unittest.TestCase):
 def sample(self):
  b=bytearray(HEADER+CAPACITY*RECORD)
  struct.pack_into('<32I',b,0,MAGIC,1,HEADER,RECORD,CAPACITY,4,123,0x7808df74,0x78000000,1,3,0,0,0,0x7808db50,0x7807f5d8,*([0]*16))
  specs=[(1,[0x1000,1,2,3,4,5,6,7],b''),(2,[0x1000,0xfffffffe,1],b''),(3,[0x2000,0,0x3000,8],bytes.fromhex('00060a0408011803'))]
  for i,(event,args,payload) in enumerate(specs):
   off=HEADER+i*RECORD;struct.pack_into('<16I',b,off,i+1,event,3,len(args),0x125014,*args,*([0]*(8-len(args))),len(payload),0,i+1);b[off+64:off+64+len(payload)]=payload
  return b
 def test_valid_scalar_and_discovery(self):
  r=decode(self.sample());self.assertEqual(r['count'],3);self.assertEqual(r['records'][0]['integer_parameters'],[1,2,3,4,5,6,7]);self.assertEqual(r['records'][1]['integer_parameters'],[-2,1]);self.assertEqual(r['records'][2]['discovery']['advertised_service_ids'],[1])
 def test_json_serializable(self):
  self.assertEqual(json.loads(json.dumps(decode(self.sample())))["count"],3)
 def test_assessment_correlates_numeric_pointers_and_callers(self):
  b=self.sample();struct.pack_into('<I',b,HEADER+2*RECORD+16,0x780761f0)
  registration={'decoded_log':{'pid':123,'records':[{'endpoint':'0x00001000','caller':'0x00124e54'}]},'executable_load_bias':0}
  self.assertTrue(assess(b,registration)['display_capture_validated'])
  registration['decoded_log']['pid']=124
  with self.assertRaises(ValueError):assess(b,registration)
  registration['decoded_log']['pid']=123
  struct.pack_into('<I',b,HEADER+2*RECORD+16,0x780761f4)
  self.assertFalse(assess(b,registration)['display_capture_validated'])
 def test_mutations_rejected(self):
  for offset in (0,4,8,12,16,20,24,36,40,48,52,64,HEADER,HEADER+4,HEADER+8,HEADER+12,HEADER+52,HEADER+56,HEADER+60,HEADER+100,HEADER+3*RECORD):
   b=self.sample();struct.pack_into('<I',b,offset,0xffffffff)
   with self.subTest(offset=offset),self.assertRaises(ValueError):decode(b)
 def test_truncated_file_and_payload(self):
  with self.assertRaises(ValueError):decode(self.sample()[:-1])
  for payload in (b'\x00\x05',b'\x00\x06\x0a\x80',b'\x00\x06\x00',b'\x00\x06\x0a\x04\x08\x01'):
   with self.subTest(payload=payload),self.assertRaises(ValueError):discovery(payload)
 def test_duplicate_service_ids(self):
  with self.assertRaises(ValueError):discovery(bytes.fromhex('00060a0208010a020801'))
 def test_scalar_event_cannot_carry_payload(self):
  b=self.sample();struct.pack_into('<I',b,HEADER+52,1)
  with self.assertRaises(ValueError):decode(b)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
