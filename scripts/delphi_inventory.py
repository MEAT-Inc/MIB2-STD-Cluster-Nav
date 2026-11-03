#!/usr/bin/env python3
"""Read-only Delphi MIB2 FTP collection, with optional Telnet inventory. Stdlib only."""
from project_console import console_session, log as print, status
import argparse
import datetime as dt
import ftplib
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys
import time
import uuid

DEFAULT_OUTPUT = str(Path(__file__).resolve().parents[1] / 'delphi-dump')

FILES = tuple('/extbin/apps/bin/' + n for n in (
    'AndroidAuto', 'AndroidAutoServices', 'CarPlay', 'CarPlayServices',
    'AppConnect', 'ClusterServices', 'Most', 'MostCanRouter', 'TransportServer',
    'NavServices', 'NavigationServer', 'vwjxe.ifs', 'delphibin.ifs')) + tuple(
    '/extbin/apps/lib/' + n for n in (
    'libautoreceiver.so', 'libautoreceiver.so.1', 'libScreenStream.so',
    'libAirPlay.so', 'libAirPlaySupport.so', 'libiap2client.so',
    'libiap2client.so.1', 'ipod-drvr-iap2.so', 'mss-ipodiap2.so',
    'libRenderSystem.so', 'libNavConfigProvider.so', 'libclm_api.so'))
ROOTS = ('/extbin/apps/cfg', '/extbin/apps/hmi/HMI/config')
INVENTORY_COMMANDS = (
    'uname -a', 'pidin info', 'pidin arguments', 'mount',
    'ls -la /extbin/apps/bin', 'ls -la /extbin/apps/lib',
    'ls -la /extbin/apps/cfg', 'ls -la /extbin/apps/hmi/HMI/config',
)
UNIX_LIST = re.compile(
    r'^([bcdlps-])[rwxStTs-]{9}[+@.]?\s+\d+\s+\S+\s+\S+\s+(\d+)\s+'
    r'\S+\s+\d+\s+\S+\s+(.+)$')
RESERVED = re.compile(r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', re.I)


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe_name(name):
    if (not name or name in ('.', '..') or name.endswith((' ', '.'))
            or any(c in name for c in '/\\:<>"|?*')
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or RESERVED.match(name)):
        raise ValueError('Unsafe or Windows-incompatible remote entry name')
    return name


def remote_parts(remote):
    if not remote.startswith('/'):
        raise ValueError('Remote path must be absolute')
    return [safe_name(p) for p in remote[1:].split('/')]


def reject_link(path):
    # Reject Windows junctions/reparse points as well as ordinary symlinks.
    if path.exists() or path.is_symlink():
        s = path.lstat()
        if stat.S_ISLNK(s.st_mode) or getattr(s, 'st_file_attributes', 0) & 0x400:
            raise ValueError('Local symlink or reparse point refused')


def local_path(base, remote):
    parts = remote_parts(remote)
    target = base.joinpath(*parts)
    if os.path.commonpath((str(base), str(target.resolve()))) != str(base):
        raise ValueError('Local path escapes output directory')
    for p in [base, *reversed(list(target.parents)[:-1]), target]:
        # Check only components at or below base here; setup checks its ancestors.
        if p == base or base in p.parents:
            reject_link(p)
    return target


def parse_list(lines):
    entries = []
    for line in lines:
        if not line.strip() or re.fullmatch(r'total\s+\d+', line.strip()):
            continue
        m = UNIX_LIST.match(line)
        if not m:
            raise ValueError('Unrecognized FTP LIST format; refusing ambiguous recursion')
        kind, size, name = m.groups()
        if kind == 'l':
            name = name.split(' -> ', 1)[0]
        if name in ('.', '..'):
            continue
        safe_name(name)
        entries.append((name, {'d': 'dir', '-': 'file', 'l': 'link'}.get(kind, 'special'), int(size)))
    return entries


class Collector:
    def __init__(self, args, ftp_factory=ftplib.FTP):
        self.a = args
        requested = Path(args.output).absolute()
        for p in [requested, *requested.parents]:
            reject_link(p)
        requested.mkdir(parents=True, exist_ok=True)
        self.base = requested.resolve()
        self.run = self.base / ('_collection_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S_') + uuid.uuid4().hex[:8])
        self.run.mkdir()
        self.logfile = (self.run / 'collection.log').open('x', encoding='utf-8')
        self.manifest = (self.run / 'manifest.jsonl').open('x', encoding='utf-8')
        self.records = []
        self.ftp_factory = ftp_factory
        self.ftp = None
        self.seen = set()
        self.dir_ids = set()
        self.entry_count = 0

    def clean(self, value):
        value = str(value)
        for secret in (self.a.password, self.a.username, self.a.telnet_password):
            if secret:
                value = value.replace(secret, '[redacted]')
        return ''.join(c if c >= ' ' else ' ' for c in value)[:500]

    def log(self, msg):
        msg = utc() + ' ' + self.clean(msg)
        print(msg, flush=True)
        self.logfile.write(msg + '\n')
        self.logfile.flush()

    def record(self, remote, status, **extra):
        r = {'time_utc': utc(), 'remote_path': remote, 'status': status, **extra}
        self.records.append(r)
        self.manifest.write(json.dumps(r, ensure_ascii=True) + '\n')
        self.manifest.flush()

    def disconnect(self):
        if self.ftp:
            try:
                self.ftp.close()
            except OSError:
                pass
            self.ftp = None

    def connect(self):
        if self.ftp is None:
            f = self.ftp_factory(timeout=self.a.timeout, encoding=self.a.encoding)
            self.ftp = f
            f.connect(self.a.host, self.a.port)
            f.login(self.a.username, self.a.password)
            f.set_pasv(True)
            f.voidcmd('TYPE I')

    def retry(self, label, action):
        for attempt in range(1, self.a.retries + 2):
            try:
                self.connect()
                return action()
            except (OSError, EOFError, ftplib.Error, ValueError) as e:
                self.disconnect()
                self.log(f'{label}: attempt {attempt} failed: {type(e).__name__}: {self.clean(e)}')
                if attempt > self.a.retries:
                    raise
                time.sleep(min(attempt, 3))

    def listing(self, remote):
        def action():
            try:
                raw = list(self.ftp.mlsd(remote))
            except ftplib.error_perm as e:
                if str(e)[:3] not in ('500', '501', '502', '504'):
                    raise
                lines = []
                self.ftp.retrlines('LIST ' + remote, lines.append)
                return parse_list(lines)
            entries = []
            for name, facts in raw:
                kind = facts.get('type', '').lower()
                if kind in ('cdir', 'pdir') or name in ('.', '..'):
                    continue
                safe_name(name)
                # Some servers expose links via nonstandard type or unix.mode.
                if ('slink' in kind or 'symlink' in kind
                        or facts.get('unix.mode', '').startswith('12')):
                    kind = 'link'
                if kind == 'dir' and facts.get('unique'):
                    unique = facts['unique']
                    if unique in self.dir_ids:
                        kind = 'duplicate_directory'
                    else:
                        self.dir_ids.add(unique)
                size = facts.get('size')
                entries.append((name, kind, int(size) if size is not None else None))
            return entries
        return self.retry('List ' + remote, action)

    def download(self, remote, listed_size=None):
        part = None
        try:
            target = local_path(self.base, remote)
            key = str(target).casefold()
            if key in self.seen:
                raise ValueError('Duplicate or case-colliding destination refused')
            self.seen.add(key)
            target.parent.mkdir(parents=True, exist_ok=True)
            target = local_path(self.base, remote)
            if target.exists():
                if not target.is_file():
                    raise ValueError('Existing destination is not a regular file')
                h = hashlib.sha256()
                with target.open('rb') as existing:
                    for block in iter(lambda: existing.read(1024 * 1024), b''):
                        h.update(block)
                self.record(remote, 'existing_not_downloaded', local_path=str(target.relative_to(self.base)),
                            bytes=target.stat().st_size, sha256=h.hexdigest(),
                            note='Hash of existing local file; remote content not checked')
                self.log('Existing destination skipped: ' + remote)
                return
            part = target.with_name(target.name + '.' + uuid.uuid4().hex + '.part')
            # Reserve our own temporary name; only this run's file is reused on retries.
            with part.open('xb'):
                pass

            def transfer():
                self.ftp.voidcmd('TYPE I')
                try:
                    expected = self.ftp.size(remote)
                except ftplib.error_perm:
                    expected = listed_size
                if expected is None:
                    expected = listed_size
                h = hashlib.sha256()
                count = 0
                last = time.monotonic()
                with part.open('wb') as out:
                    def receive(data):
                        nonlocal count, last
                        out.write(data)
                        h.update(data)
                        count += len(data)
                        if time.monotonic() - last >= 2:
                            self.log(f'{remote}: {count:,} bytes received')
                            last = time.monotonic()
                    self.ftp.retrbinary('RETR ' + remote, receive, blocksize=65536)
                    out.flush()
                    os.fsync(out.fileno())
                if expected is not None and count != expected:
                    raise ValueError(f'Byte count mismatch: expected {expected}, received {count}')
                return count, h.hexdigest(), expected

            self.log('Downloading ' + remote)
            count, digest, expected = self.retry('Download ' + remote, transfer)
            local_path(self.base, remote)
            # Hard-link publication is atomic and fails if the destination exists.
            # Supported by normal NTFS Windows output folders; never replaces a file.
            os.link(part, target)
            part.unlink()
            self.record(remote, 'downloaded', local_path=str(target.relative_to(self.base)),
                        bytes=count, sha256=digest, expected_bytes=expected,
                        size_check='matched' if expected is not None else 'unavailable')
            self.log(f'Saved {remote}: {count:,} bytes, SHA256 {digest}')
        except (OSError, EOFError, ftplib.Error, ValueError) as e:
            self.record(remote, 'failed', error=self.clean(e),
                        partial_path=str(part.relative_to(self.base)) if part and part.exists() else None,
                        partial_bytes=part.stat().st_size if part and part.exists() else 0)
            self.log(f'FAILED {remote}: {type(e).__name__}: {self.clean(e)}')

    def walk(self, remote, depth=0):
        if depth > self.a.max_depth:
            self.record(remote, 'failed', error='Recursion depth limit reached')
            return
        try:
            local_path(self.base, remote)
            if depth == 0:
                parent, name = remote.rsplit('/', 1)
                matches = [e for e in self.listing(parent) if e[0] == name]
                if len(matches) != 1 or matches[0][1] != 'dir':
                    raise ValueError('Recursive root is missing, ambiguous, or not a plain directory')
            entries = self.listing(remote)
            local_path(self.base, remote).mkdir(parents=True, exist_ok=True)
        except (OSError, EOFError, ftplib.Error, ValueError) as e:
            self.record(remote, 'failed', error=self.clean(e))
            self.log('FAILED listing ' + remote + ': ' + self.clean(e))
            return
        # Manifest records the listing used to choose files, including skipped links.
        self.record(remote, 'listed', entries=[{'name': n, 'type': t, 'size': s} for n, t, s in entries])
        names = set()
        for name, kind, size in entries:
            self.entry_count += 1
            child = remote + '/' + name
            if self.entry_count > self.a.max_entries:
                self.record(remote, 'failed', error='Entry limit reached; remaining entries omitted')
                return
            if name.casefold() in names:
                self.record(child, 'failed', error='Case-colliding directory entry')
                continue
            names.add(name.casefold())
            try:
                safe_name(name)
                local_path(self.base, child)
            except (OSError, ValueError) as e:
                self.record(child, 'failed', error=self.clean(e))
                continue
            if kind == 'file':
                self.download(child, size)
            elif kind == 'dir':
                self.walk(child, depth + 1)
            else:
                self.record(child, 'skipped_' + kind)

    def finish(self, interrupted=False):
        self.disconnect()
        counts = {}
        for r in self.records:
            counts[r['status']] = counts.get(r['status'], 0) + 1
        incomplete = interrupted or any(k not in ('downloaded', 'listed', 'inventory_collected') for k in counts)
        summary = {'finished_utc': utc(), 'result': 'PARTIAL' if incomplete else 'COMPLETE',
                   'interrupted': interrupted, 'counts': counts,
                   'vehicle_context': {'model': '2019 USDM VW Golf R', 'part': '3Q0035876B',
                                       'train_reported': 'MST2_US_VW_P0890D', 'MU': '0890'},
                   'host': self.a.host, 'ftp_port': self.a.port,
                   'requested_files': FILES if not self.a.inventory_only else [],
                   'recursive_roots': ROOTS if not self.a.inventory_only else [],
                   'note': 'Local SHA256 and size checks do not establish authenticity. Context is user-reported.'}
        with (self.run / 'summary.json').open('x', encoding='utf-8') as out:
            json.dump(summary, out, indent=2)
        self.log(f"{summary['result']}: {counts}. Reports: {self.run}")
        self.manifest.close()
        self.logfile.close()
        return 2 if incomplete else 0


class TelnetReader:
    """Minimal byte-stream Telnet client: rejects all negotiated options."""
    PROMPT = re.compile(rb'(?:^|[\r\n])[^\r\n]{0,160}[#$] ?$')

    def __init__(self, sock, timeout):
        self.sock = sock
        self.timeout = timeout
        self.state = 'data'
        self.command = None

    def decode(self, raw):
        out = bytearray()
        for b in raw:
            if self.state == 'data':
                if b == 255:
                    self.state = 'iac'
                else:
                    out.append(b)
            elif self.state == 'iac':
                if b == 255:
                    out.append(b)
                    self.state = 'data'
                elif b in (251, 252, 253, 254):
                    self.command = b
                    self.state = 'option'
                elif b == 250:
                    self.state = 'sub'
                else:
                    self.state = 'data'
            elif self.state == 'option':
                if self.command in (251, 253):
                    self.sock.sendall(bytes((255, 254 if self.command == 251 else 252, b)))
                self.state = 'data'
            elif self.state == 'sub':
                if b == 255:
                    self.state = 'sub_iac'
            elif self.state == 'sub_iac':
                self.state = 'data' if b == 240 else 'sub'
        return bytes(out)

    def read_until(self, patterns, on_data=None):
        data = bytearray()
        deadline = time.monotonic() + self.timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError('Telnet prompt timeout (no commands guessed)')
            self.sock.settimeout(remaining)
            raw = self.sock.recv(65536)
            if not raw:
                raise EOFError('Telnet connection closed before expected prompt')
            decoded = self.decode(raw)
            if on_data is not None:
                on_data(decoded)
            data.extend(decoded)
            if len(data) > 16 * 1024 * 1024:
                raise ValueError('Telnet response exceeded 16 MiB limit')
            for label, pattern in patterns:
                if pattern.search(data):
                    return label, bytes(data)

    def send(self, text):
        if '\r' in text or '\n' in text or '\xff' in text:
            raise ValueError('Invalid Telnet input')
        self.sock.sendall(text.encode('utf-8') + b'\r\n')


def collect_inventory(c):
    a = c.a
    transcript = c.run / 'vehicle-inventory.txt'
    # Authentication responses are never placed in the transcript.
    try:
        c.log('Connecting to Telnet for fixed read-only inventory commands')
        with socket.create_connection((a.host, a.telnet_port), timeout=a.timeout) as sock:
            t = TelnetReader(sock, a.timeout)
            prompts = [('login', re.compile(rb'(?i)(?:login|username):\s*$')),
                       ('password', re.compile(rb'(?i)password:\s*$')),
                       ('shell', t.PROMPT)]
            label, _ = t.read_until(prompts)
            if label == 'login':
                t.send(a.telnet_user)
                label, _ = t.read_until(prompts)
            if label == 'password':
                password = a.telnet_password
                if password is None:
                    password = getpass.getpass('Telnet password (Enter if blank): ')
                t.send(password)
                label, _ = t.read_until(prompts)
            if label != 'shell':
                raise ValueError('Telnet authentication failed or unexpected prompt')
            with transcript.open('x', encoding='utf-8') as out:
                out.write('Delphi read-only inventory collected ' + utc() + '\n')
                out.write('Reported vehicle: 2019 USDM Golf R / 3Q0035876B / MST2_US_VW_P0890D / MU0890\n')
                for command in INVENTORY_COMMANDS:
                    c.log('Inventory: ' + command)
                    marker = 'CODEX_INVENTORY_' + uuid.uuid4().hex
                    # A unique output marker avoids mistaking a # in command output
                    # for the shell prompt. printf is shell output only.
                    t.send(command + "; printf '\\n" + marker + ":%s\\n' \"$?\"")
                    done = re.compile(rb'(?:^|[\r\n])' + marker.encode('ascii') + rb':(\d+)\r?\n')
                    _, response = t.read_until([('done', done)])
                    code = int(done.search(response).group(1))
                    # Some shells echo the command; retain output as evidence.
                    out.write('\n===== ' + command + ' =====\n')
                    out.write(response.decode(a.encoding, errors='replace'))
                    out.flush()
                    if code:
                        c.record(None, 'failed', stage='inventory_command', command=command, exit_code=code)
        digest = hashlib.sha256(transcript.read_bytes()).hexdigest()
        c.record(None, 'inventory_collected', local_path=str(transcript.relative_to(c.base)),
                 bytes=transcript.stat().st_size, sha256=digest,
                 note='Commands completed to shell prompt; inspect output for command-level errors.')
    except (OSError, EOFError, ValueError) as e:
        c.record(None, 'failed', stage='telnet_inventory', error=c.clean(e),
                 partial_path=str(transcript.relative_to(c.base)) if transcript.exists() else None)
        c.log('FAILED Telnet inventory: ' + c.clean(e))


def parser():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--host', default='192.168.1.4')
    p.add_argument('--port', type=int, default=21, help='FTP port')
    p.add_argument('--username', default='ftpuser')
    p.add_argument('--ask-password', action='store_true', help='Prompt for FTP password instead of default ftpuser')
    p.add_argument('--output', default=DEFAULT_OUTPUT, help='Shared project dump root; existing files are never replaced')
    p.add_argument('--timeout', type=float, default=30, help='Socket/command timeout in seconds')
    p.add_argument('--retries', type=int, default=2, help='Additional FTP attempts, restarting failed files from byte zero')
    p.add_argument('--encoding', default='utf-8', help='FTP names and Telnet output encoding')
    p.add_argument('--max-depth', type=int, default=32)
    p.add_argument('--max-entries', type=int, default=50000)
    p.add_argument('--collect-inventory', action='store_true', help='Collect inventory over Telnet before FTP')
    p.add_argument('--inventory-only', action='store_true', help='Collect Telnet inventory without FTP downloads')
    p.add_argument('--telnet-port', type=int, default=23)
    p.add_argument('--telnet-user', default='root')
    p.add_argument('--ask-telnet-password', action='store_true', help='Prompt before connecting; otherwise prompt only if requested by server')
    return p


def main(argv=None):
    p = parser()
    a = p.parse_args(argv)
    if a.timeout <= 0 or a.retries < 0 or a.max_depth < 0 or a.max_entries < 1:
        p.error('Timeout/limits must be positive; retries and depth may be zero')
    if not 1 <= a.port <= 65535 or not 1 <= a.telnet_port <= 65535:
        p.error('Ports must be between 1 and 65535')
    try:
        ''.encode(a.encoding)
        for value in (a.host, a.username, a.telnet_user):
            if any(ord(c) < 32 or ord(c) == 127 for c in value):
                raise ValueError('Control characters in connection arguments')
        a.password = getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
        a.telnet_password = getpass.getpass('Telnet password (Enter if blank): ') if a.ask_telnet_password else None
        c = Collector(a)
    except (LookupError, OSError, ValueError) as e:
        print(f'Cannot initialize collection: {type(e).__name__}: {e}', file=sys.stderr)
        return 1
    interrupted = False
    try:
        c.log('Starting read-only collection. FTP credentials are not logged.')
        if a.collect_inventory or a.inventory_only:
            collect_inventory(c)
        if not a.inventory_only:
            # A failed initial login should not incur 25 separate retry sequences.
            try:
                c.retry('Initial FTP connection', lambda: None)
            except (OSError, EOFError, ftplib.Error, ValueError) as e:
                c.record(None, 'failed', stage='ftp_connection', error=c.clean(e))
            else:
                for remote in FILES:
                    c.download(remote)
                for root in ROOTS:
                    c.walk(root)
    except KeyboardInterrupt:
        interrupted = True
        c.log('Interrupted; any temporary .part files are incomplete.')
    except Exception as e:
        interrupted = True
        c.record(None, 'failed', stage='unexpected', error=c.clean(e))
        c.log('Unexpected failure: ' + c.clean(e))
    return c.finish(interrupted)


if __name__ == '__main__':
    with console_session(__file__, __doc__):
        sys.exit(main())

