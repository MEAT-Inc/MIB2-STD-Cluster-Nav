"""Prepare an offline startup-hook review; never connect to or install on the radio."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from project_console import console_session, log as print
from cluster_startup_launcher import hook

ROOT = Path(__file__).resolve().parents[1]
STOCK = {
    'runHMI.sh': ('/extbin/apps/hmi/HMI/runHMI.sh',
                  'fcd910cfa317c60da4f352efce9bf8fd79b2f655475ce94f32ccabc7ef3e1182'),
    'procman_core.cfg': ('/etc/procman_core.cfg',
                        '004783991da86ca2956470636265be212ab189c5f393afa161affead873680a1'),
}
# Review placeholder only. The laptop installer creates a fresh real identity.
HOOK = hook(b'', '0' * 32)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_bounded(path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 1048576:
        raise ValueError('Missing, linked or oversized evidence: ' + str(path))
    return path.read_bytes()


def review(evidence):
    evidence = Path(evidence)
    summary = json.loads(read_bounded(evidence / 'preflight-summary.json'))
    if summary.get('read_only') is not True or summary.get('persistent_write_performed') is not False:
        raise ValueError('Expected read-only preflight evidence')
    commands = summary.get('commands', [])
    required = {
        'system.txt': 'uname -a', 'mounts.txt': 'mount',
        'paths.txt': 'ls -ld /etc /etc/procman_core.cfg /extbin /extbin/apps/hmi/HMI /extbin/apps/hmi/HMI/runHMI.sh /persistence /extbin/.boot /ffs',
        'procman-arguments.txt': 'pidin -p procman arguments',
    }
    for name, command in required.items():
        if sum(r.get('file') == name and r.get('command') == command and r.get('exit_code') == 0
               for r in commands) != 1:
            raise ValueError('Required preflight command failed or ambiguous: ' + name)
    content = {}
    for name, (remote, expected) in STOCK.items():
        data = read_bounded(evidence / name)
        rows = [r for r in summary['files'] if r.get('file') == name]
        if (len(rows) != 1 or rows[0].get('path') != remote or
                rows[0].get('bytes') != len(data) or rows[0].get('sha256') != digest(data) or
                digest(data) != expected):
            raise ValueError('Unsupported or changed firmware file: ' + name)
        content[name] = data
    mounts = read_bounded(evidence / 'mounts.txt').decode()
    for device, mount in (('mmc0t177', 'extbin'), ('mmc0t180', 'persistence')):
        if not re.search(r'^/dev/' + device + r' on /' + mount + r' type qnx6\s*$', mounts, re.M):
            raise ValueError('Unexpected persistent backing for /' + mount)
    system = read_bounded(evidence / 'system.txt').decode()
    if not re.search(r'^QNX localhost 6\.5\.0 2015/12/01-11:00:56EST TI-DRA74X-PG1\.1 armle\s*$', system, re.M):
        raise ValueError('Unsupported target system')
    args = read_bounded(evidence / 'procman-arguments.txt').decode()
    if not re.search(r'^\s*\d+ procman -f /etc/procman_core\.cfg\s*$', args, re.M):
        raise ValueError('Active procman config not established')
    cfg = content['procman_core.cfg'].decode()
    if not re.search(r'^\s*-f\s+/extbin/apps/hmi/HMI/runHMI\.sh\s+-n"hmi"\s+-p21\s+-c0\s*$', cfg, re.M):
        raise ValueError('Expected HMI launch chain absent')
    if b'$J9VM  $VMOPTIONS $PARAMETERS de.vw.mib.MIBMain &' not in content['runHMI.sh']:
        raise ValueError('Stock JVM launch absent')
    return content


def prepare(evidence, output):
    content = review(evidence)
    stock = content['runHMI.sh']
    candidate = stock + HOOK
    report = {
        'schema_version': 1,
        'review_only': True, 'install_ready': False, 'remote_write_performed': False,
        'evidence': str(Path(evidence).resolve()),
        'hook': STOCK['runHMI.sh'][0],
        'stock_script_sha256': digest(stock),
        'procman_config_sha256': STOCK['procman_core.cfg'][1],
        'candidate_sha256': digest(candidate),
        'factory_prefix_unchanged': candidate[:len(stock)] == stock,
        'rollback_sha256': digest(stock),
        'runtime_root_candidate': '/persistence/delphi-cluster-launcher-v1',
        'candidate_installation_identity_is_placeholder': True,
        'blocked_on': [
            'Integrate the generation gate with replay, sink, producer and route-policy lifecycle.',
            'Verify factory return and complete callback quiescence before each new queue.',
            'Verify repeated attach/detach with the same processes and process replacement.',
            'Implement a bounded, identity-checked native supervisor and boot.sh entry point.',
            'Test hook syntax and execution on QNX; verify normal boot, SWDL bypass and rollback.',
            'Re-read live firmware hashes and backing immediately before installation.',
        ],
    }
    # New directory only: no overwriting an earlier review or a symlink target.
    output = Path(output)
    if not output.is_absolute():
        output = Path.cwd() / output
    for parent in (output, *output.parents):
        if parent.is_symlink():
            raise ValueError('Linked output path: ' + str(parent))
    output.mkdir(parents=True, exist_ok=False)
    (output / 'runHMI.sh.candidate').write_bytes(candidate)
    (output / 'runHMI.sh.stock').write_bytes(stock)
    (output / 'startup-review.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence', type=Path, help='deployment-preflight folder')
    p.add_argument('--output', type=Path, required=True, help='new local review folder')
    a = p.parse_args(argv)
    print(json.dumps(prepare(a.evidence, a.output), indent=2))
    return 0


if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
