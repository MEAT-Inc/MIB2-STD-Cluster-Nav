"""Small shared console UI. Data/file output stays unchanged when redirected."""
import builtins
from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
import re
import subprocess
import sys
import textwrap
import time

SCRIPT_VERSION = '1.0'
_active = False
_progress_times = {}
_COLORS = {'INFO': '96', 'STEP': '94', 'OK': '92', 'WARN': '93', 'ERROR': '91', 'ACTION': '95'}


def _terminal(stream):
    return bool(getattr(stream, 'isatty', lambda: False)())


def _ansi(stream):
    if not _terminal(stream) or 'NO_COLOR' in os.environ or os.environ.get('TERM') == 'dumb':
        return False
    if os.name == 'nt':
        # Enable ANSI in both Windows Terminal and the classic Command Prompt.
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetStdHandle.restype = wintypes.HANDLE
        kernel.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        handle = kernel.GetStdHandle(-11 if stream is sys.stdout else -12)
        mode = wintypes.DWORD()
        if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel.SetConsoleMode(handle, mode.value | 4))
    return True


def _label(level, stream):
    label = f'[{datetime.now():%H:%M:%S}] [{level:6}]'
    return f'\033[{_COLORS[level]}m{label}\033[0m' if _ansi(stream) else label


def redact_arguments(args):
    """Hide password/token values while keeping the invocation useful."""
    result, hide_next = [], False
    for arg in args:
        if hide_next:
            result.append('***')
            hide_next = False
            continue
        key = arg.split('=', 1)[0]
        sensitive = key.startswith('-') and re.search(r'password|passwd|token|secret|api[-_]?key', key, re.I)
        if sensitive and not key.startswith('--ask-'):
            if '=' in arg:
                arg = key + '=***'
            else:
                hide_next = True
        result.append(arg)
    return result


def log(*values, sep=' ', end='\n', file=None, flush=True):
    """A print-compatible human log; preserve redirected/file output exactly."""
    stream = sys.stdout if file is None else file
    if not _active or not _terminal(stream):
        return builtins.print(*values, sep=sep, end=end, file=stream, flush=flush)
    message = sep.join(map(str, values))
    for line in message.split('\n'):
        builtins.print(_label('INFO', stream), line, end=end, file=stream, flush=flush)


def status(message, level='STEP'):
    """Progress belongs on stderr so stdout can still contain JSON or other data."""
    if _active:
        builtins.print(_label(level, sys.stderr), message, file=sys.stderr, flush=True)


def progress(message, key='progress', interval=5):
    """Show activity during polling without printing the same step every half second."""
    if not _active:
        return
    now = time.monotonic()
    if now - _progress_times.get(key, float('-inf')) >= interval:
        _progress_times[key] = now
        status(message)


def prompt(message):
    if _active:
        message = '\n' + _label('ACTION', sys.stderr) + ' ' + message
    return builtins.input(message)


@contextmanager
def console_session(script, use_case=None, version=SCRIPT_VERSION, enabled=True):
    """Wrap CLI entry points; imports stay quiet and nested calls keep history."""
    global _active
    if not enabled or _active:
        yield
        return
    previous_depth = os.environ.get('PROJECT_CONSOLE_DEPTH')
    nested = bool(previous_depth)
    os.environ['PROJECT_CONSOLE_DEPTH'] = '1'
    _active = True
    _progress_times.clear()
    started = time.monotonic()
    try:
        if not nested and _terminal(sys.stderr):
            if os.name == 'nt':
                subprocess.run(['cmd.exe', '/d', '/c', 'cls'], stdout=sys.stderr, stderr=sys.stderr, check=False)
            else:
                sys.stderr.write('\033[2J\033[H')
        rule = '=' * 72
        builtins.print('\n' + rule, file=sys.stderr, flush=True)
        builtins.print(f'{Path(script).name} | version {version}', file=sys.stderr)
        arguments = subprocess.list2cmdline(redact_arguments(sys.argv[1:])) or '(none)'
        purpose = ' '.join((use_case or Path(script).stem.replace('_', ' ')).split())
        builtins.print(textwrap.fill('Arguments: ' + arguments, width=88, subsequent_indent='           '), file=sys.stderr)
        builtins.print(textwrap.fill('Use case: ' + purpose, width=88, subsequent_indent='          '), file=sys.stderr)
        builtins.print(rule, file=sys.stderr, flush=True)
        status('Starting script.')
        try:
            yield
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
            status(f'Finished with exit {code} ({time.monotonic() - started:.1f}s).', 'OK' if code == 0 else 'ERROR')
            raise
        except KeyboardInterrupt:
            status('Interrupted by operator.', 'WARN')
            raise
        except BaseException as exc:
            status(f'{type(exc).__name__}: {exc}', 'ERROR')
            raise
        else:
            status(f'Finished ({time.monotonic() - started:.1f}s).', 'OK')
    finally:
        _active = False
        if previous_depth is None:
            os.environ.pop('PROJECT_CONSOLE_DEPTH', None)
        else:
            os.environ['PROJECT_CONSOLE_DEPTH'] = previous_depth
