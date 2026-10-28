"""Fresh, read-only vehicle preflight for the Delphi observer. Python stdlib only."""
import argparse
import datetime as dt
import ftplib
import getpass
import hashlib
import json
from pathlib import Path
import re
import socket
import uuid
import delphi_inventory as d

COMMANDS = (
    ('system', 'uname -a'), ('kernel', 'pidin info'),
    ('processes', 'pidin arguments'),
    ('android-arguments', 'pidin -p AndroidAuto arguments'),
    ('android-environment', 'pidin -p AndroidAuto environment'),
    ('android-maps', 'pidin -p AndroidAuto mapinfo'),
    ('android-fds', 'pidin -p AndroidAuto fds'),
    ('ram-paths', 'ls -ld /dev/shmem /ramdisk'),
    ('loader', 'ls -l /usr/lib/ldqnx.so.2 /proc/boot/libc.so.3'),
)
FILES = ('/extbin/apps/bin/AndroidAuto', '/extbin/apps/lib/libautoreceiver.so',
         '/extbin/apps/lib/libautoreceiver.so.1')
MAX_FILE = 16 * 1024 * 1024

def normalize(data):
    return data.replace(b'\r\x00', b'\n').replace(b'\r', b'\n')

def has_android_process(data):
    return bool(re.search(rb'(?m)^\s*\d+\s+[^\n]*\bAndroidAuto\b', normalize(data)))

def receiver_mapping(data):
    """pidin uses a fixed-width name field; require a long, unique suffix."""
    aliases = ('libautoreceiver.so', 'libautoreceiver.so.1')
    matches = []
    for m in re.finditer(rb'(?m)^\s*([A-Za-z0-9_.-]+)\s+@\s*([0-9a-fA-F]+)\b', normalize(data)):
        name = m.group(1).decode('ascii')
        expected = [alias for alias in aliases if len(name) >= 12 and alias.endswith(name)]
        if len(expected) == 1:
            matches.append(dict(displayed_name=name, expected_basename=expected[0],
                mapping_start='0x' + format(int(m.group(2), 16), '08x'),
                name_truncated=name != expected[0]))
    return matches[0] if len(matches) == 1 else None

SUPERVISOR_COMMANDS = (
    ('process-family', 'pidin family'),
    ('procman-arguments', 'pidin -p procman arguments'),
    ('procman-fds', 'pidin -p procman fds'),
    ('procman-maps', 'pidin -p procman mapinfo'),
    ('procman-core', 'cat /etc/procman_core.cfg'),
    ('android-arguments', 'pidin -p AndroidAuto arguments'),
    ('android-maps', 'pidin -p AndroidAuto mapinfo'),
)

def inventory(a, run, commands=COMMANDS):
    rows = []
    responses = {}
    prompts = [('login', re.compile(rb'(?i)(?:login|username):\s*$')),
               ('password', re.compile(rb'(?i)password:\s*$')), ('shell', d.TelnetReader.PROMPT)]
    try:
        with socket.create_connection((a.host, a.telnet_port), timeout=a.timeout) as sock:
            reader = d.TelnetReader(sock, a.timeout)
            label, _ = reader.read_until(prompts)
            if label == 'login':
                reader.send(a.telnet_user)
                label, _ = reader.read_until(prompts)
            if label == 'password':
                reader.send(getpass.getpass('Telnet password (Enter if blank): '))
                label, _ = reader.read_until(prompts)
            if label != 'shell': raise ValueError('Telnet login did not reach a shell')
            for name, command in commands:
                print('Read-only: ' + command, flush=True)
                marker = 'OP' + uuid.uuid4().hex[:12]
                done = re.compile(marker.encode() + rb':([0-9]+):END')
                path = run / (name + '.txt')
                with path.open('x', encoding='utf-8') as out:
                    out.write('COMMAND ' + command + '\n')
                    out.flush()
                    def save(chunk):
                        out.write(normalize(chunk).decode('utf-8', errors='replace'))
                        out.flush()
                    reader.send(command + '; echo ' + marker + ':$?:END')
                    _, response = reader.read_until([('done', done)], on_data=save)
                code = int(done.search(response).group(1))
                responses[name] = response
                rows.append(dict(command=command, file=path.name, exit_code=code))
    except (OSError, EOFError, ValueError) as exc:
        # Never reuse a timed-out session; FTP acquisition is independent.
        rows.append(dict(stage='telnet', error=type(exc).__name__ + ': ' + str(exc)))
    return rows, responses

def download(a, password, remote, run, expected):
    path = run / remote.lstrip('/')
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + '.partial')
    last_error = None
    for attempt in range(2):
        digest, size = hashlib.sha256(), 0
        try:
            with ftplib.FTP(timeout=a.timeout) as ftp:
                ftp.connect(a.host, a.port)
                ftp.login(a.username, password)
                ftp.voidcmd('TYPE I')
                with partial.open('wb') as output:
                    def save(block):
                        nonlocal size
                        size += len(block)
                        if size > MAX_FILE: raise ValueError('Remote file exceeds 16 MiB limit')
                        output.write(block)
                        digest.update(block)
                    ftp.retrbinary('RETR ' + remote, save)
                if not size: raise ValueError('Zero-byte response')
            partial.replace(path)
            actual = digest.hexdigest()
            return dict(remote=remote, local=str(path.relative_to(run)), bytes=size,
                        sha256=actual, expected_sha256=expected, matches_expected=actual == expected)
        except (OSError, EOFError, ftplib.Error, ValueError) as exc:
            last_error = type(exc).__name__ + ': ' + str(exc)
            if password: last_error = last_error.replace(password, '[redacted]')
    return dict(remote=remote, error=last_error, matches_expected=False)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='192.168.1.4')
    parser.add_argument('--port', type=int, default=21)
    parser.add_argument('--telnet-port', type=int, default=23)
    parser.add_argument('--username', default='ftpuser')
    parser.add_argument('--telnet-user', default='root')
    parser.add_argument('--supervisor-only', action='store_true', help='Read process-manager configuration and process ancestry; skip FTP downloads')
    parser.add_argument('--ask-password', action='store_true', help='Prompt for a non-default FTP password')
    parser.add_argument('--timeout', type=float, default=20)
    a = parser.parse_args(argv)
    if not 0 < a.timeout <= 120 or not 1 <= a.port <= 65535 or not 1 <= a.telnet_port <= 65535:
        parser.error('Invalid timeout/port')
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'native/observer/release/manifest.json').read_text())
    expected = manifest['expected_target_sha256']
    # Existing collector guards against symlink/reparse-point output roots.
    base = root / 'delphi-dump'
    d.reject_link(base)
    base.mkdir(exist_ok=True)
    run = base / ('_observer_preflight_' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8])
    run.mkdir()
    print('Saving fresh acquisition to ' + str(run), flush=True)
    password = getpass.getpass('FTP password: ') if a.ask_password and not a.supervisor_only else 'ftpuser'
    commands = SUPERVISOR_COMMANDS if a.supervisor_only else COMMANDS
    rows, responses = inventory(a, run, commands)
    files = []
    for remote in (() if a.supervisor_only else FILES):
        print('Fresh FTP read: ' + remote, flush=True)
        key = 'AndroidAuto' if remote.endswith('/AndroidAuto') else 'libautoreceiver.so'
        files.append(download(a, password, remote, run, expected[key]))
    commands_ok = len(rows) == len(commands) and all(r.get('exit_code') == 0 for r in rows)
    active = has_android_process(responses.get('android-arguments', b''))
    mapping = receiver_mapping(responses.get('android-maps', b''))
    mapped = mapping is not None
    hashes_match = bool(files) and all(f['matches_expected'] for f in files)
    ready = commands_ok and active and mapped and (a.supervisor_only or hashes_match)
    summary = dict(acquired_utc=dt.datetime.now(dt.timezone.utc).isoformat(), read_only=True,
        mode='supervisor' if a.supervisor_only else 'preflight', commands=rows, files=files, fresh_hashes_verified=hashes_match, receiver_mapping=mapping, all_commands_ok=commands_ok, android_process_found=active,
        receiver_in_mapinfo=mapped, ready_for_review=ready, deployment_authorized=False)
    (run / 'preflight-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('Firmware hashes: ' + ('not recollected (supervisor-only)' if a.supervisor_only else 'MATCH' if hashes_match else 'MISMATCH / INCOMPLETE'))
    print('AndroidAuto process: ' + ('found' if active else 'not found'))
    print('Receiver in runtime maps: ' + ('found' if mapped else 'not found'))
    print('Result: ' + ('READY FOR REVIEW' if ready else 'INCOMPLETE - review preflight-summary.json'))
    print('No upload, restart, process termination or vehicle file write was performed.')
    return 0 if ready else 1
if __name__ == '__main__': raise SystemExit(main())
