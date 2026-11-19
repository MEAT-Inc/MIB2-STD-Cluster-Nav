"""Regression for long-run diagnostic-cap preflight reporting."""
from pathlib import Path
import sys,copy,json,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_disconnected_observer import assess_cluster_preflight
class Tests(unittest.TestCase):
 def report(self):return json.loads((Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261119_172654_55abb3da/disconnect-summary.json').read_text())
 def test_actual_successful_v16_was_only_failed_by_legacy_capture_requirement(self):
  s=self.report();self.assertFalse(s['cluster_preflight_passed']);v=assess_cluster_preflight(s);self.assertTrue(v['passed']);self.assertTrue(v['expected_recording_limit']);self.assertEqual(v['timing_scope'],'bounded_diagnostic_prefix')
 def test_real_failures_and_unexpected_truncation_remain_failures(self):
  for key,field,value in (('timing','clock_error',1),('timing','source_timestamp_regressed',True),('timing','records',100),('live_input','owned_live_copy_verified',False),('live_input','all_copied_access_units_match',False),('live_output','drops',1),('live_output','total_input_frames',999),('live_output','total_input_bytes',999),('native_before','active_geometry_observed',False)):
   s=self.report();s[key][field]=value
   if key=='timing' and field=='records':s['timing']['raw_bytes_accounted']=1000
   with self.subTest(field=field):self.assertFalse(assess_cluster_preflight(s)['passed'])
  for k,v in (('live_seconds',30),('navigation_identity_unchanged',False),('live_cluster_requested',False)):
   s=self.report();s[k]=v;self.assertFalse(assess_cluster_preflight(s)['passed'])
 def test_complete_timed_capture_keeps_legacy_behavior(self):
  s=self.report();s['live_seconds']=30;s['timing']['complete']=True;self.assertTrue(assess_cluster_preflight(s)['passed']);s['navigation_identity_unchanged']=False;self.assertFalse(assess_cluster_preflight(s)['passed'])
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
