"""Verify shared console output, exit handling, and portable CLI startup."""
from pathlib import Path as _TestPath
import sys as _test_sys
_test_sys.path.insert(0, str(_TestPath(__file__).resolve().parents[1]))
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from project_console import console_session
import project_console as console


class ConsoleTests(unittest.TestCase):
    def test_banner_data_and_exit_code(self):
        out, err = io.StringIO(), io.StringIO()
        with patch.object(sys, 'argv', ['example.py', '--password=private', '--host', 'unit']), redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as raised:
                with console_session('example.py', 'Inspect captured firmware.', version='2.3'):
                    console.log('{"result": true}')
                    console.status('Checking captured files.')
                    raise SystemExit(2)
        self.assertEqual(raised.exception.code, 2)
        self.assertEqual(out.getvalue(), '{"result": true}\n')
        self.assertIn('example.py | version 2.3', err.getvalue())
        self.assertIn('Inspect captured firmware.', err.getvalue())
        self.assertIn('--password=*** --host unit', err.getvalue())
        self.assertIn('[ERROR ]', err.getvalue())
        self.assertNotIn('private', err.getvalue())
        self.assertNotIn('\033', out.getvalue() + err.getvalue())

    def test_sensitive_argument_forms(self):
        args = ['--ask-password', '--telnet-password', 'private', '--api-key=secret', '--token', 'abc', '--run']
        self.assertEqual(console.redact_arguments(args), ['--ask-password', '--telnet-password', '***', '--api-key=***', '--token', '***', '--run'])

    def test_poll_progress_is_throttled(self):
        err = io.StringIO()
        with redirect_stderr(err), console_session('poll.py', 'Wait for a report.'):
            with patch.object(console.time, 'monotonic', side_effect=[0, 1, 6]):
                for _ in range(3):
                    console.progress('Still waiting.', interval=5)
        self.assertEqual(err.getvalue().count('Still waiting.'), 2)

    def test_nested_sessions_and_environment_restored(self):
        err = io.StringIO()
        with patch.dict(os.environ, {'PROJECT_CONSOLE_DEPTH': 'outer'}), redirect_stderr(err):
            with console_session('outer.py', 'Run parent.'):
                with console_session('child.py', 'Run child.'):
                    console.status('Child work.')
            self.assertEqual(os.environ['PROJECT_CONSOLE_DEPTH'], 'outer')
        self.assertEqual(err.getvalue().count('| version'), 1)
        self.assertIn('Child work.', err.getvalue())
        self.assertFalse(console._active)

    def test_failure_does_not_swallow_exception(self):
        err = io.StringIO()
        with redirect_stderr(err), self.assertRaisesRegex(ValueError, 'bad file'):
            with console_session('inspect.py', 'Inspect files.'):
                raise ValueError('bad file')
        self.assertIn('[ERROR ] ValueError: bad file', err.getvalue())
        self.assertNotIn('[OK', err.getvalue())
        self.assertFalse(console._active)

    def test_file_output_preserved(self):
        data, err = io.StringIO(), io.StringIO()
        with redirect_stderr(err), console_session('write.py', 'Write data.'):
            console.log('a', 'b', sep=',', end='', file=data)
        self.assertEqual(data.getvalue(), 'a,b')

    def test_no_color_override(self):
        class Terminal(io.StringIO):
            def isatty(self):
                return True
        with patch.dict(os.environ, {'NO_COLOR': ''}):
            self.assertFalse(console._ansi(Terminal()))

    def test_terminal_labels_and_color(self):
        class Terminal(io.StringIO):
            def isatty(self):
                return True
        output, err = Terminal(), io.StringIO()
        with patch.dict(os.environ, {'PROJECT_CONSOLE_DEPTH': 'outer'}), patch.object(console, '_ansi', return_value=True), redirect_stdout(output), redirect_stderr(err):
            with console_session('color.py', 'Show readable output.'):
                console.log('First step.\nSecond step.')
                console.status('Needs attention.', 'WARN')
        self.assertEqual(output.getvalue().count('[INFO  ]'), 2)
        self.assertIn('\033[96m', output.getvalue())
        self.assertIn('\033[93m', err.getvalue())

    def test_portable_plan_runs_with_only_bundled_scripts(self):
        scripts = Path(__file__).resolve().parents[1]
        names = ('project_console.py', 'run_cluster_replay.py', 'cluster_preflight.py',
                 'run_observer_smoke.py', 'delphi_inventory.py', 'decode_delphi_observer.py',
                 'collect_map_session.py')
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'scripts'
            target.mkdir()
            for name in names:
                shutil.copy2(scripts / name, target / name)
            for name in ('run_cluster_replay.py', 'collect_map_session.py'):
                result = subprocess.run([sys.executable, '-S', '-B', str(target / name)], cwd=folder, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(name + ' | version', result.stderr)
                self.assertIn('Plan only', result.stdout)
                self.assertNotIn('\033', result.stdout + result.stderr)
            self.assertFalse((Path(folder) / 'delphi-dump').exists())


if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
