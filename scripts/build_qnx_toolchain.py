"""Build the pinned QNX compiler with Git modes/symlinks restored in a tar context.
Windows checkout materializes symlinks as small text files. Never execute these.
The tar is for Docker only and does not change the checkout or acquired dump.
"""
from pathlib import Path
import io, subprocess, tarfile, json, hashlib, argparse
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT / '.tools/qnx65-armv7-toolchain'
PIN = 'baa45224f18ae6b13c2e9c77c6663bb8181eb6a1'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sysroot-only', action='store_true')
    args = parser.parse_args()
    target = 'qnx-sdp' if args.sysroot_only else 'base-env'
    tag = 'delphi-qnx65:sysroot' if args.sysroot_only else 'delphi-qnx65:8.5'
    head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
    if head != PIN:
        raise SystemExit('Unexpected toolchain source revision: ' + head)
    raw = subprocess.check_output(['git', '-C', str(REPO), 'ls-files', '--stage', '-z', '--',
        'sdp', 'gcc', 'binutils', 'tools', 'cross', 'Dockerfile', 'entrypoint.sh'])
    archive = ROOT / ('.tools/qnx-sysroot-context.tar' if args.sysroot_only else '.tools/qnx-build-context.tar')
    entries = []
    with tarfile.open(archive, 'w') as tf:
        for entry in raw.split(b'\0'):
            if not entry: continue
            meta, name = entry.split(b'\t', 1)
            mode, oid, stage = meta.decode().split()
            name = name.decode('utf-8')
            if stage != '0' or mode not in ('100644', '100755', '120000'):
                raise RuntimeError('Unsupported Git entry: ' + name)
            file = REPO / name
            if not file.is_file(): raise RuntimeError('Missing sparse file: ' + name)
            data = file.read_bytes()
            ti = tarfile.TarInfo(name)
            ti.mtime = 0
            if mode == '120000':
                ti.type = tarfile.SYMTYPE
                ti.linkname = data.decode('utf-8').strip()
                ti.mode = 0o777
                tf.addfile(ti)
            else:
                # Git text checkouts on Windows can have CRLF. Binary files are unchanged.
                if b'\0' not in data: data = data.replace(b'\r\n', b'\n')
                ti.mode = 0o755 if mode == '100755' else 0o644
                ti.size = len(data)
                tf.addfile(ti, io.BytesIO(data))
            entries.append({'name': name, 'mode': mode, 'sha256': hashlib.sha256(data).hexdigest()})
    (ROOT / '.tools/qnx-build-context.json').write_text(json.dumps({'revision': head, 'entries': entries}, indent=2))
    print('Docker context prepared:', len(entries), 'files; Git symlinks and executable modes restored.', flush=True)
    with archive.open('rb') as source, (ROOT / ('.tools/qnx-sysroot-build.log' if args.sysroot_only else '.tools/qnx-toolchain-tar-build.log')).open('wb') as log:
        result = subprocess.run(['docker', 'build', '--platform=linux/amd64', '--target', target,
            '--build-arg', 'BASE=base-8.5', '-t', tag, '-'], stdin=source, stdout=log, stderr=subprocess.STDOUT)
    print('Docker build exit:', result.returncode, flush=True)
    raise SystemExit(result.returncode)
if __name__ == '__main__': main()
