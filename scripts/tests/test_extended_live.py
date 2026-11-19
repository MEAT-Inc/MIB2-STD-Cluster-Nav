"""Extended-duration stream contracts and strict bounded-prefix evidence."""
from pathlib import Path
import argparse,copy,json,struct,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from live_run_options import add_live_arguments,options_bytes
from live_cluster_bridge import assess_output,output_delivered,native_factory_return_verified
from review_live_input import reader_report,assess_live
from review_route_policy import assess_route_policy,disconnect_verified
class ExtendedTests(unittest.TestCase):
 def test_duration_cli_is_opt_in_and_mutually_exclusive(self):
  p=argparse.ArgumentParser();add_live_arguments(p)
  self.assertIsNone(p.parse_args([]).live_seconds);self.assertEqual(p.parse_args(['--no-live-timeout']).live_seconds,0);self.assertEqual(p.parse_args(['--live-seconds','30']).live_seconds,30)
  with self.assertRaises(SystemExit):p.parse_args(['--live-seconds','60'])
  with self.assertRaises(SystemExit):p.parse_args(['--live-seconds','30','--no-live-timeout'])
 def test_options_bind_nonce_and_mode(self):
  token='12345678'*4;w=struct.unpack('<8I',options_bytes(token,0));self.assertEqual(w,(0x314f564c,1,32,0,*([0x12345678]*4)))
  for t,n in ((token,60),('X'*32,0),('1'*31,30)):
   with self.assertRaises(ValueError):options_bytes(t,n)
 def native(self):
  w=[0]*128;w[:5]=[0x31504c52,1,512,123,3]
  for i,v in ((22,7),(36,0x78000000),(67,6),(68,2),(69,36),(71,456),(72,1),(74,5),(10,100),(11,18800),(62,100),(84,5000),(86,1000),(87,2),(88,1),(89,10),(92,2000),(94,2050),(96,5),(98,1),(99,1999),(102,250),(103,4),(104,5),(105,5000),(106,90000),(108,1)):w[i]=v
  return w
 def test_long_stream_is_not_limited_by_diagnostic_prefix_counts(self):
  w=self.native();v=assess_output(struct.pack('<128I',*w),123);self.assertTrue(output_delivered(v,456,2));self.assertTrue(native_factory_return_verified(v))
  for i,value in ((70,1),(84,4999),(73,255)):
   bad=list(w);bad[i]=value;self.assertFalse(output_delivered(assess_output(struct.pack('<128I',*bad)),456,2))
  for i,value in ((108,2),(109,60),(110,1),(105,1),(67,5)):
   bad=list(w);bad[i]=value
   with self.subTest(i=i),self.assertRaises(ValueError):assess_output(struct.pack('<128I',*bad))
 def test_actual_capture_prefix_matches_after_stream_outgrows_recording(self):
  p=Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261118_201524_1f980346'
  summary=json.loads((p/'disconnect-summary.json').read_text());pid=summary['observed_pid'];secondary=copy.deepcopy(summary['secondary'])
  r=list(struct.unpack('<128I',(p/'live-reader.bin').read_bytes()));r[1]=3;r[22]=5000;r[23]=r[24]=0;r[25]=1;r[26]=5000;r[27]=90000000;r[28]=0;r[29]=1;r[30]=0
  secondary['frames']=5000;secondary['keyframe_probe']['ipc_frames']=5000
  args=[(p/'live-copy-timing.bin').read_bytes(),(p/'live-copy.h264').read_bytes(),(p/'timing.bin').read_bytes(),(p/'secondary.h264').read_bytes(),pid,secondary]
  v=assess_live(struct.pack('<128I',*r),*args);self.assertTrue(v['owned_live_copy_verified']);self.assertEqual(v['verification_scope'],'bounded_diagnostic_prefix')
  for i,value in ((9,1),(26,4999),(30,30)):
   bad=list(r);bad[i]=value;self.assertFalse(assess_live(struct.pack('<128I',*bad),*args)['owned_live_copy_verified'])
  bad=list(r);bad[31]=1
  with self.assertRaises(ValueError):reader_report(struct.pack('<128I',*bad),pid)
 def test_route_v4_keeps_disconnect_checks_and_legacy_reserved_words(self):
  p=Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261118_201524_1f980346';s=json.loads((p/'disconnect-summary.json').read_text());w=list(struct.unpack('<128I',(p/'route-policy.bin').read_bytes()));w[1]=4;w[119]=0
  v=assess_route_policy(struct.pack('<128I',*w),s['observed_pid'],s['live_bridge']['observed_pid']);self.assertFalse(v['bounded_trial']);self.assertTrue(disconnect_verified(v))
  w[120]=1
  with self.assertRaises(ValueError):assess_route_policy(struct.pack('<128I',*w),s['observed_pid'],s['live_bridge']['observed_pid'])
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
