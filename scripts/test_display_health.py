import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import collect_display_health as m
class HealthTests(unittest.TestCase):
 def test_plan_never_connects_or_creates_dump(self):
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory') as remote,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main([]),0);remote.assert_not_called();self.assertFalse((Path(t)/'delphi-dump').exists())
 def test_run_requires_observed_state(self):
  with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main(['--run'])
 def test_fixed_commands_have_no_mutations(self):
  self.assertEqual(len({n for n,c in m.COMMANDS}),len(m.COMMANDS))
  for name,c in m.COMMANDS:
   self.assertTrue(c.startswith(('uname ','pidin ','ls ','sloginfo ')))
   self.assertFalse(any(x in c for x in (';','|','>','kill','reboot','LD_PRELOAD','-w','sloginfo -c')))
 def test_parser_and_black_snapshot_never_health_pass(self):
  before=b'42 /extbin/apps/bin/AndroidAuto -t\n10 screen-cda -z\n20 /ifs2/j9 -x\n'
  after=before.replace(b'42 ',b'43 ')
  self.assertEqual(m.process_ids(before)['AndroidAuto'],[42])
  def inventory(a,folder,commands):
   (folder/'processes.txt').write_bytes(before)
   return [dict(command=c,file=n+'.txt',exit_code=0) for n,c in commands],{'processes':before,'processes-end':after}
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory',side_effect=inventory),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main(['--run','--state','black']),0)
   r=json.loads(next(Path(t).glob('delphi-dump/*/display-health-summary.json')).read_text())
   self.assertTrue(r['collection_complete']);self.assertTrue(r['ui_fault_reported']);self.assertFalse(r['display_recovery_verified']);self.assertEqual(r['changed_processes'],['AndroidAuto'])
 def test_partial_snapshot_retains_fault(self):
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory',return_value=([{'stage':'telnet','error':'EOFError'}],{})),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main(['--run','--state','black']),1)
   r=json.loads(next(Path(t).glob('delphi-dump/*/display-health-summary.json')).read_text());self.assertTrue(r['ui_fault_reported']);self.assertFalse(r['collection_complete'])
if __name__=='__main__':unittest.main()
