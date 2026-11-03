from project_console import console_session
import io,unittest
from unittest.mock import Mock
from run_observer_smoke import Shell
class ShellCompletionTests(unittest.TestCase):
 def shell(self):
  s=Shell.__new__(Shell);s.broken=False;s.actions=[];s.transcript=io.StringIO();s.reader=Mock();return s
 def test_bare_async_rejected_before_send(self):
  s=self.shell()
  with self.assertRaises(ValueError):s.command('true &')
  s.reader.send.assert_not_called()
 def test_remote_syntax_error_stops_session_immediately(self):
  s=self.shell();s.reader.read_until.return_value=('syntax',b'\r\nksh: syntax error\r\n')
  with self.assertRaisesRegex(RuntimeError,'syntax error'):s.command('bad syntax')
  self.assertTrue(s.broken);self.assertEqual(s.actions[-1]['error'],'shell_syntax_error')
  with self.assertRaises(RuntimeError):s.command('another command')
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
