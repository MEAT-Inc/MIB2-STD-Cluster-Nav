"""Offline guards for combined live output and disconnected cleanup."""
from pathlib import Path
import sys,struct,unittest,tempfile,json,hashlib,types
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from live_cluster_bridge import assess_output,cleanup_allowed,output_delivered,native_factory_return_verified,LiveBridge
from unittest.mock import patch
class LiveBridgeTests(unittest.TestCase):
 def report(self):
  w=[0]*128;w[:5]=[0x31504c52,1,512,123,3];w[22]=7;w[36]=0x78000000;w[67]=1;w[68]=354;w[71]=456;w[72]=1;return struct.pack('<128I',*w)
 def test_live_identity_and_frames(self):
  v=assess_output(self.report(),123);self.assertEqual(v['frames'],354);self.assertEqual(v['source_pid'],456)
 def test_wrong_pid_profile_and_reserved_rejected(self):
  with self.assertRaises(ValueError):assess_output(self.report(),999)
  for index in (0,1,2,4,22,36,67,75,127):
   b=bytearray(self.report());struct.pack_into('<I',b,index*4,0xffffffff)
   with self.subTest(index=index),self.assertRaises(ValueError):assess_output(b,123)
 def test_phone_attestation_and_aa_cleanup_gate_nav_cleanup(self):
  self.assertFalse(cleanup_allowed(True,False,False));self.assertFalse(cleanup_allowed(True,True,True));self.assertTrue(cleanup_allowed(True,True,False));self.assertTrue(cleanup_allowed(False,False,False))
 def test_delivery_requires_matching_source_counts_and_native_packet_ack(self):
  v=dict(source_verified=True,source_pid=456,frames=20,packets=100,bytes=18800,rewritten_packets=100)
  self.assertTrue(output_delivered(v,456,20))
  for key,value in (('source_verified',False),('source_pid',457),('frames',19),('packets',0),('bytes',18799),('rewritten_packets',99),('sink_error',5),('timeline_error',1)):
   b=dict(v);b[key]=value;self.assertFalse(output_delivered(b,456,20),key)
 def test_missing_bootstrap_report_is_polled_before_copy(self):
  b=LiveBridge.__new__(LiveBridge);b.token='a'*32;b.state={};b.save=lambda:None;events=[];ready=bytearray(self.report());struct.pack_into('<I',ready,16,1)
  availability=iter((1,1,0));times=iter((0,1,2,3))
  def cmd(c,required=True):events.append('probe');return next(availability)
  def report(n):events.append('copy');return bytes(ready)
  b.cmd=cmd;b.report=report
  with patch('live_cluster_bridge.native_channel_missing',return_value=[]):b.wait_channel(clock=lambda:next(times),sleep=lambda _:None)
  self.assertEqual(events,['probe','probe','probe','copy']);self.assertEqual(b.state['observed_pid'],123)
 def test_bootstrap_timeout_does_not_copy_missing_report(self):
  b=LiveBridge.__new__(LiveBridge);b.token='a'*32;b.cmd=lambda *a,**kw:1;b.report=lambda *a:self.fail('Missing report must not be copied');times=iter((0,1,3))
  with self.assertRaises(TimeoutError):b.wait_channel(timeout=2,clock=lambda:next(times),sleep=lambda _:None)
 def test_zero_bootstrap_header_waits_for_ready(self):
  b=LiveBridge.__new__(LiveBridge);b.token='a'*32;b.state={};b.save=lambda:None;b.cmd=lambda *a,**kw:0;ready=bytearray(self.report());struct.pack_into('<I',ready,16,1);responses=iter((bytes(512),bytes(ready)));b.report=lambda n:next(responses);times=iter((0,1,2))
  with patch('live_cluster_bridge.native_channel_missing',return_value=[]):b.wait_channel(clock=lambda:next(times),sleep=lambda _:None)
 def test_saved_manifest_allows_cleanup_without_current_payloads(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);folder=root/'session';folder.mkdir();remote='/ramdisk/delphi-nav-bridge_'+'a'*32;names=('nav_launch','libdelphi_cluster.so','replay.bin','replay_libc_check','nav_cycle','live_queue_prepare');raw=json.dumps(dict(kind='native_cluster_live_output',recorded_video_available=False,files={n:dict(bytes=1,sha256=hashlib.sha256(b'x').hexdigest()) for n in names})).encode();(folder/'live-release-manifest.json').write_bytes(raw);(folder/'live-bridge-summary.json').write_text(json.dumps(dict(remote=remote,manifest_sha256=hashlib.sha256(raw).hexdigest(),started=True,cleanup_pending=True)));args=types.SimpleNamespace(resume=folder);b=LiveBridge(root,args,folder,dict(remote_directory='/ramdisk/delphi-aa-observer_'+'a'*32),'pw');self.assertEqual(b.files,{})
 def test_phone_ready_requests_arm_without_waiting_for_video(self):
  b=LiveBridge.__new__(LiveBridge);b.manifest={};b.state={'observed_pid':123};b.token='a'*32;b.remote='/ramdisk/delphi-nav-bridge_'+b.token;b.save=lambda:None;events=[];raw=bytearray(self.report());struct.pack_into('<I',raw,16,1);struct.pack_into('<I',raw,84,1);b.wait_channel=lambda **kw:(bytes(raw),{});b.report=lambda name:bytes(raw);b.command=lambda c,*args:events.append(c) or 0
  with patch('live_cluster_bridge.native_channel_missing',return_value=[]):b.phone_ready(lambda *a:0,lambda *a:b'',lambda *a:b'',456)
  self.assertIn('live_queue_prepare',events[0]);self.assertIn('arm-replay',events[1]);self.assertEqual(b.state['activation'],'first_verified_phone_frame')
 def test_phone_handoff_requires_verified_policy_ready(self):
  b=LiveBridge.__new__(LiveBridge);b.manifest={'route_presentation_trial':True};b.state={'observed_pid':123};b.token='a'*32;b.remote='/ramdisk/delphi-nav-bridge_'+b.token;b.save=lambda:None;raw=bytearray(self.report());struct.pack_into('<I',raw,16,1);struct.pack_into('<I',raw,84,1);b.wait_channel=lambda **kw:(bytes(raw),{});b.report=lambda name:bytes(raw);b.command=lambda *a:0
  policy=[0]*128;policy[:7]=[0x31545052,1,512,456,1,0,123];policy[17]=1
  with patch('live_cluster_bridge.native_channel_missing',return_value=[]):b.phone_ready(lambda *a:0,lambda *a:b'',lambda *a:struct.pack('<128I',*policy),456)
  self.assertTrue(b.state['route_policy_ready']['eligible'])
  policy[5]=2
  with patch('live_cluster_bridge.native_channel_missing',return_value=[]),self.assertRaisesRegex(RuntimeError,'startup error 2'):b.phone_ready(lambda *a:0,lambda *a:b'',lambda *a:struct.pack('<128I',*policy),456)
 def test_v2_active_close_telemetry_is_bounded(self):
  b=bytearray(self.report())
  for index,value in ((67,2),(13,2),(10,100),(14,3),(76,2),(77,99),(78,2),(79,1)):struct.pack_into('<I',b,index*4,value)
  self.assertEqual(assess_output(b,123)['active_closes'],1)
  struct.pack_into('<I',b,77*4,101)
  with self.assertRaises(ValueError):assess_output(b,123)
 def test_v3_preserves_source_frame_accounting_and_bounds(self):
  b=bytearray(self.report())
  for i,v in ((67,3),(10,1000),(11,188000),(62,1000),(80,3),(81,2742),(82,575245),(83,27),(84,354),(86,1000)):struct.pack_into('<I',b,i*4,v)
  v=assess_output(b,123);self.assertEqual(v['startup_delay_ms'],1000);self.assertTrue(output_delivered(v,456,354))
  struct.pack_into('<I',b,84*4,353);self.assertFalse(output_delivered(assess_output(b,123),456,354));struct.pack_into('<I',b,84*4,354)
  for index,value in ((80,4),(81,1048577),(82,4194305),(83,65),(84,355),(86,0),(87,1)):
   copy=bytearray(b);struct.pack_into('<I',copy,index*4,value)
   with self.subTest(index=index),self.assertRaises(ValueError):assess_output(copy,123)
  struct.pack_into('<I',b,85*4,1);self.assertFalse(output_delivered(assess_output(b,123),456,354))
 def test_v4_native_return_requires_verified_stop_and_accepted_factory_output(self):
  b=bytearray(self.report())
  for i,v in ((67,4),(74,5),(86,1000),(87,2),(88,1),(89,100),(92,1000),(94,1200),(96,5),(98,1),(99,900)):struct.pack_into('<I',b,i*4,v)
  self.assertTrue(native_factory_return_verified(assess_output(b,123)))
  for i,v in ((87,1),(89,0),(94,999),(98,0)):
   copy=bytearray(b);struct.pack_into('<I',copy,i*4,v)
   if i==89:
    with self.assertRaises(ValueError):assess_output(copy,123)
   else:self.assertFalse(native_factory_return_verified(assess_output(copy,123)))
  for i,v in ((87,5),(88,2),(97,770049),(101,65),(102,1)):
   copy=bytearray(b);struct.pack_into('<I',copy,i*4,v)
   with self.subTest(i=i),self.assertRaises(ValueError):assess_output(copy,123)
 def test_disconnect_discarded_tail_is_accounted_without_claiming_all_reader_frames_emitted(self):
  v=dict(profile_version=4,stop_reason=5,source_frames_emitted=18,frames=20,source_verified=True,source_pid=456,packets=100,bytes=18800,rewritten_packets=100,factory_return={'discarded_source_frames':2})
  self.assertTrue(output_delivered(v,456,22))
  for field,value in (('source_frames_emitted',17),('startup_overflows',1),('frames',23),('source_frames_emitted',0)):
   bad=dict(v);bad[field]=value;self.assertFalse(output_delivered(bad,456,22))
  v['stop_reason']=1;self.assertFalse(output_delivered(v,456,22))
 def test_v5_latency_profile_is_explicit_and_legacy_v4_remains_strict(self):
  b=bytearray(self.report())
  for i,v in ((67,5),(68,354),(84,354),(86,1000),(102,250),(103,4),(104,5),(10,100),(11,18800),(62,100)):struct.pack_into('<I',b,i*4,v)
  v=assess_output(b,123);self.assertEqual(v['startup_delay_ms'],250);self.assertEqual(v['startup_initial_delay_ms'],1000);self.assertTrue(output_delivered(v,456,354))
  for i,value in ((86,250),(102,1000),(103,5),(104,4),(105,1),(127,1),(67,4)):
   bad=bytearray(b);struct.pack_into('<I',bad,i*4,value)
   with self.subTest(i=i),self.assertRaises(ValueError):assess_output(bad,123)
 def test_planned_timeout_returns_without_claiming_a_disconnect_event(self):
  b=bytearray(self.report())
  for i,v in ((67,4),(74,2),(86,1000),(87,2),(88,1),(89,100),(92,1000),(94,1200),(96,2)):struct.pack_into('<I',b,i*4,v)
  self.assertTrue(native_factory_return_verified(assess_output(b,123)))
  for i,v in ((4,4),(5,255),(70,1),(73,255),(91,5),(96,5)):
   bad=bytearray(b);struct.pack_into('<I',bad,i*4,v)
   if i==91:
    with self.assertRaises(ValueError):assess_output(bad,123)
   else:self.assertFalse(native_factory_return_verified(assess_output(bad,123)))
 def test_actual_v10_error_is_preserved_despite_visible_video_and_successful_recovery(self):
  p=Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261118_192938_41991359'
  v=assess_output((p/'live-output.bin').read_bytes())
  self.assertEqual(v['error'],255);self.assertEqual(v['factory_return']['state'],2)
  self.assertFalse(native_factory_return_verified(v))
  self.assertFalse(output_delivered(v,v['source_pid'],v['frames']))
 def test_automatic_return_observation_persists_before_manual_recovery(self):
  b=LiveBridge.__new__(LiveBridge);b.state={};b.manifest={'automatic_factory_return_required':True};saved=[];b.save=lambda:saved.append(dict(b.state))
  with patch('live_cluster_bridge.input',side_effect=['n','y','y']):
   b.confirm_automatic_factory_return();b.confirm_factory_maps()
  self.assertFalse(b.state['factory_automatic_return_observed']);self.assertTrue(b.state['factory_maps_restored']);self.assertTrue(saved[0]['factory_automatic_return_before_manual_toggle']);self.assertNotIn('factory_maps_restored',saved[0])
  with patch('live_cluster_bridge.input',side_effect=AssertionError('Must not overwrite original observation')):b.confirm_automatic_factory_return()
 def test_manual_restoration_without_prior_observation_cannot_prove_automatic_return(self):
  b=LiveBridge.__new__(LiveBridge);b.state={};b.manifest={'automatic_factory_return_required':True};b.save=lambda:None
  with patch('live_cluster_bridge.input',side_effect=['y','y']):b.confirm_factory_maps()
  self.assertTrue(b.state['factory_maps_restored']);self.assertFalse(b.state['factory_automatic_return_observed']);self.assertFalse(b.state['factory_automatic_return_before_manual_toggle'])
 def test_cleanup_does_not_touch_nav_without_start_or_after_restore(self):
  for state in ({'started':False},{'started':True,'restoration_verified':True,'factory_maps_restored':True}):
   b=LiveBridge.__new__(LiveBridge);b.state=state
   def forbidden(*args,**kwargs):raise AssertionError('No Nav command should run')
   b.cleanup(forbidden,forbidden,forbidden)
 def test_radio_only_cannot_mark_factory_map_restoration_complete(self):
  b=LiveBridge.__new__(LiveBridge);b.state={'started':True,'restoration_verified':True,'factory_maps_restored':False};b.save=lambda:None
  def forbidden(*args,**kw):raise AssertionError('Visual recheck must not restart Nav')
  with patch('live_cluster_bridge.input',side_effect=['y','n']):b.cleanup(forbidden,forbidden,forbidden)
  self.assertTrue(b.state['factory_radio_map_restored']);self.assertFalse(b.state['factory_cluster_map_restored']);self.assertFalse(b.state['factory_maps_restored'])
  with patch('live_cluster_bridge.input',side_effect=['y','yes']):b.cleanup(forbidden,forbidden,forbidden)
  self.assertTrue(b.state['factory_maps_restored'])
 def test_corrupt_pending_controller_refuses_restart(self):
  b=LiveBridge.__new__(LiveBridge);b.state={'started':True,'observed_pid':123};b.token='a'*32;b.remote='/ramdisk/delphi-nav-bridge_'+b.token;b.report=lambda *a:self.report();b.capture_output=lambda v:None;b.files={'nav_launch':b'nav','nav_cycle':b'cycle'};b.manifest={'files':{n:dict(bytes=len(v),sha256=__import__('hashlib').sha256(v).hexdigest()) for n,v in b.files.items()}};commands=[]
  class FTP:
   def __enter__(self):return self
   def __exit__(self,*a):pass
  b.ftp=lambda:FTP()
  def cmd(c,required=True):commands.append(c);return 1 if 'launch-final-' in c else 0
  with patch('live_cluster_bridge.retrieve',side_effect=lambda ftp,path:b.files[path.rsplit('/',1)[1]]),self.assertRaises(ValueError):b.cleanup(cmd,lambda n:b'',lambda src,n:bytes(512))
  self.assertFalse(any('cleanup-disconnected' in c for c in commands))
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
