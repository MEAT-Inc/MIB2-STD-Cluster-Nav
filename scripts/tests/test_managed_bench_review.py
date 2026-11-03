"""Negative evidence controls for the managed-launch integration checker."""
from pathlib import Path as _TestPath
import sys as _test_sys
_test_sys.path.insert(0, str(_TestPath(__file__).resolve().parents[1]))
from project_console import console_session
import unittest
from pathlib import Path
from review_managed_bench import assess,ROOT
class ReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.log=(ROOT/"native/observer/managed-bench/qemu/qemu.log").read_text()
 def test_valid(self):self.assertTrue(assess(self.log)["passed"])
 def test_changed_parent(self):
  with self.assertRaises(ValueError):assess(self.log.replace("ppid="+str(assess(self.log)["manager_pid"]),"ppid=99999",1))
 def test_wrong_wait_status(self):
  with self.assertRaises(ValueError):assess(self.log.replace("extra=-X1792","extra=-X7"))
 def test_observer_leaked(self):
  with self.assertRaises(ValueError):assess(self.log.replace("MANAGED_OBSERVER observed=0 records=0","MANAGED_OBSERVER observed=1 records=9",1))
 def test_fatal_signal(self):
  with self.assertRaises(ValueError):assess(self.log+"\nProcess 999 (unknown) terminated SIGSEGV code=0 by process 3 value=0.\n")
 def test_missing_restore(self):
  with self.assertRaises(ValueError):assess(self.log.replace("MANAGED_REAL_STOCK_RESTORE_PASS",""))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
