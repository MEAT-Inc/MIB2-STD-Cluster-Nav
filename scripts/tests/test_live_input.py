from pathlib import Path
import sys,struct,json,hashlib,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import run_disconnected_observer as workflow
from secondary_timing import assess_timing
from review_live_input import assess_live,nal_flags,reader_report
from review_secondary_keyframes import assess_probe
class LiveInputTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261103_022700_3b445220';cls.raw=(p/'secondary.h264').read_bytes();cls.timing=(p/'timing.bin').read_bytes();base=struct.unpack('<128I',(p/'secondary.bin').read_bytes());cls.pid=base[3];cls.report_original=(p/'secondary.bin').read_bytes();cls.router=base[8]
  sec=workflow.assess_secondary(cls.report_original,cls.raw,cls.pid,cls.router);v=assess_timing(cls.timing,cls.raw,cls.pid,sec);meta=bytearray(65568);parts=[];codec=b'';offset=0;count=0
  for r in v['records_detail']:
   b=cls.raw[r['offset']:r['offset']+r['saved']]
   if r['kind']==1:codec=b
   if r['kind']==2:
    b=codec+b if nal_flags(b)&1 else b;flags=nal_flags(b)|(16 if not count else 0);parts.append(b);struct.pack_into('<QQ4I',meta,32+count*32,r['timestamp'],r['monotonic_ns']+2000000,offset,len(b),r['session'],flags);offset+=len(b);count+=1
  struct.pack_into('<8I',meta,0,0x31544c43,1,777,cls.pid,32,2048,count,0);r=[0]*128;r[:9]=[0x3152434c,1,512,777,cls.pid,3,0,count,offset];cls.reader=struct.pack('<128I',*r);cls.meta=bytes(meta);cls.copy=b''.join(parts);sec['keyframe_probe']=dict(ipc_attached=True,ipc_error=0,ipc_dropped=0,ipc_malformed=0,ipc_consumer_pid=777,ipc_frames=count);cls.secondary=sec
 def test_real_captured_frames_owned_byte_identity(self):
  v=assess_live(self.reader,self.meta,self.copy,self.timing,self.raw,self.pid,self.secondary);self.assertTrue(v['owned_live_copy_verified']);self.assertEqual(v['frames'],617);self.assertEqual(v['source_to_copy_median_ms'],2);self.assertFalse(v['cluster_transport_connected'])
 def test_empty_reader_never_claims_byte_identity_or_live_copy(self):
  b=bytearray(self.reader);struct.pack_into('<II',b,28,0,0);meta=bytearray(self.meta);struct.pack_into('<I',meta,24,0);meta[32:]=bytes(len(meta)-32)
  v=assess_live(bytes(b),bytes(meta),b'',self.timing,self.raw,self.pid,self.secondary)
  self.assertFalse(v['owned_live_copy_verified']);self.assertFalse(v['all_copied_access_units_match'])
 def test_missing_concurrent_samples_are_unknown(self):
  from review_live_input import assess_native_geometry
  v=assess_native_geometry(b'',1,[dict(kind=2,monotonic_ns=1)])
  self.assertFalse(v['observation_available']);self.assertEqual(v['samples_during_phone_video'],0)
 def test_unbound_native_epipe_is_diagnosed_only_with_exact_consumer(self):
  p=Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261117_134509_a3a6c5c7/live-reader-ready.bin';b=p.read_bytes()
  with self.assertRaises(ValueError):reader_report(b,1822798)
  v=reader_report(b,1822798,consumer_pid=1548373,allow_unbound=True);self.assertEqual(v['error'],32);self.assertEqual(v['source_pid'],0);self.assertEqual(v['state'],4)
  with self.assertRaises(ValueError):reader_report(b,1822798,consumer_pid=1548374,allow_unbound=True)
 def test_corrupt_copy_never_passes(self):
  b=bytearray(self.copy);b[-1]^=1;v=assess_live(self.reader,self.meta,bytes(b),self.timing,self.raw,self.pid,self.secondary);self.assertFalse(v['owned_live_copy_verified'])
 def test_metadata_bounds_and_identity_refused(self):
  for offset in (0,4,8,12,16,20,24,28,48,52,56,60,65564):
   b=bytearray(self.meta);struct.pack_into('<I',b,offset,0xffffffff)
   with self.subTest(offset=offset),self.assertRaises(ValueError):assess_live(self.reader,b,self.copy,self.timing,self.raw,self.pid,self.secondary)
 def test_reader_unknown_reserved_or_wrong_pid_refused(self):
  b=bytearray(self.reader);struct.pack_into('<I',b,127*4,1)
  with self.assertRaises(ValueError):reader_report(b,self.pid)
  with self.assertRaises(ValueError):reader_report(self.reader,self.pid+1)
 def test_v2_planned_cutoff_accounts_for_published_queue_tail(self):
  meta=bytearray(self.meta);count=struct.unpack_from('<I',meta,24)[0]-4;end=struct.unpack_from('<I',meta,32+count*32+16)[0]
  struct.pack_into('<I',meta,24,count);meta[32+count*32:]=bytes(len(meta)-32-count*32)
  reader=bytearray(self.reader)
  for i,v in ((1,2),(7,count),(8,end),(19,2),(22,count+4),(23,4),(25,1)):struct.pack_into('<I',reader,i*4,v)
  secondary=dict(self.secondary);secondary['keyframe_probe']=dict(self.secondary['keyframe_probe'],ipc_closed=True)
  v=assess_live(reader,meta,self.copy[:end],self.timing,self.raw,self.pid,secondary)
  self.assertTrue(v['owned_live_copy_verified']);self.assertEqual(v['reader']['unconsumed_published_frames'],4)
  for i,value in ((1,1),(6,255),(9,1),(22,count+3),(25,0)):
   bad=bytearray(reader);struct.pack_into('<I',bad,i*4,value)
   if i==1:
    with self.assertRaises(ValueError):assess_live(bad,meta,self.copy[:end],self.timing,self.raw,self.pid,secondary)
   else:self.assertFalse(assess_live(bad,meta,self.copy[:end],self.timing,self.raw,self.pid,secondary)['owned_live_copy_verified'])
 def test_reader_v2_reserved_and_queue_bounds_remain_strict(self):
  b=bytearray(self.reader);struct.pack_into('<I',b,4,2)
  for i,value in ((22,2054),(23,5),(24,2),(25,2),(26,1),(127,1)):
   bad=bytearray(b);struct.pack_into('<I',bad,i*4,value)
   with self.assertRaises(ValueError):reader_report(bad,self.pid)
 def test_probe_report_requires_explicit_mode(self):
  w=list(struct.unpack('<128I',self.report_original));w[43]=1;w[44]=3;w[45]=1;w[46]=w[26];w[48]=1;w[50]=w[26];w[55]=777;b=struct.pack('<128I',*w)
  with self.assertRaises(ValueError):workflow.assess_secondary(b,self.raw,self.pid,self.router)
  self.assertEqual(workflow.assess_secondary(b,self.raw,self.pid,self.router,probe=True)['keyframe_probe']['ipc_frames'],617)
 def probe_fixture(self,responses=True):
  codec=b'\x00\x00\x01\x67\x42\x80\x1f\x00\x00\x01\x68\xee';key=b'\x00\x00\x01\x65\x88\x84';pred=b'\x00\x00\x01\x41\x9a\x21';events=[(1,1,codec),(2,1000000000,key)]
  for n in range(3):events.extend(((3,(2+n*2)*1000000000,b''),(2,(2+n*2)*1000000000+100000000,key if responses else pred)))
  raw=bytearray();data=bytearray(81952)
  for i,(kind,mono,part) in enumerate(events):struct.pack_into('<IIQQ4I',data,32+40*i,kind,37,mono//1000,mono,len(raw),len(part),len(part),0);raw.extend(part)
  struct.pack_into('<8I',data,0,0x314d4954,1,51,40,2048,len(events),0,0)
  sec=dict(frames=4,codec_saved_bytes=len(codec),session=37,keyframe_probe=dict(requests=3,idr_frames=4 if responses else 1,clock_error=0))
  return bytes(data),bytes(raw),sec
 def test_refresh_response_correlated_without_claiming_cluster_video(self):
  t,b,s=self.probe_fixture();v=assess_probe(t,b,51,s);self.assertTrue(v['phone_refresh_produces_fresh_idr']);self.assertEqual(v['focus_refresh_requests'],3);self.assertFalse(v['cluster_transport_connected'])
 def test_ignored_refresh_not_reported_as_success(self):
  t,b,s=self.probe_fixture(False);self.assertFalse(assess_probe(t,b,51,s)['phone_refresh_produces_fresh_idr'])
 def test_legacy_parser_rejects_new_control_records(self):
  t,b,s=self.probe_fixture()
  with self.assertRaises(ValueError):assess_timing(t,b,51,s)
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
