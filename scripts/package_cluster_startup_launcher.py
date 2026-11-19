"""Build and independently check the portable startup launcher car-test bundle."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from project_console import console_session, log as print
from prepare_cluster_startup import review
from cluster_startup_launcher import package

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'native/cluster-bridge/deployment'
EVIDENCE = ROOT / 'delphi-dump/_deployment_preflight_20261119_131638_794286b0/deployment-preflight'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    tests = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/tests/test_cluster_startup_launcher.py')],
                           cwd=ROOT, capture_output=True, text=True)
    if tests.returncode or 'skipped=' in tests.stderr:
        raise ValueError('Launcher transaction/shell tests incomplete: ' + tests.stdout + tests.stderr)
    stock = review(EVIDENCE)['runHMI.sh']
    files = {'runHMI.sh.stock': stock, 'boot.sh': (BASE / 'boot-witness.sh').read_bytes()}
    release = BASE / 'launcher-release'
    release.mkdir(exist_ok=True)
    for name, data in files.items():
        (release / name).write_bytes(data)
    manifest = dict(kind='delphi_startup_witness_v1', maps_bridge_enabled=False,
                    on_car_tested=False, persistent_startup_write=True,
                    files={n: dict(bytes=len(b), sha256=sha(b)) for n, b in files.items()})
    (release / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    package(release)
    names = {'cluster_startup_launcher.py'}
    while True:
        added = set()
        for name in names:
            for node in ast.walk(ast.parse((ROOT / 'scripts' / name).read_text())):
                modules = ([x.name for x in node.names] if isinstance(node, ast.Import) else
                           [node.module] if isinstance(node, ast.ImportFrom) else [])
                for module in modules:
                    dependency = (module or '').split('.')[0] + '.py'
                    if (ROOT / 'scripts' / dependency).is_file():
                        added.add(dependency)
        if added <= names:
            break
        names |= added
    manifest['scripts_sha256'] = {n: sha((ROOT / 'scripts' / n).read_bytes()) for n in sorted(names)}
    (release / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    bundle = BASE / 'startup-launcher-v1-laptop.zip'
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(BASE / 'launcher-README.txt', 'README.txt')
        for n in sorted(names):
            z.write(ROOT / 'scripts' / n, 'scripts/' + n)
        for n in (*files, 'manifest.json'):
            z.write(release / n, (release / n).relative_to(ROOT).as_posix())
    with tempfile.TemporaryDirectory() as td:
        extracted = Path(td)
        with zipfile.ZipFile(bundle) as z:
            assert z.testzip() is None
            z.extractall(extracted)
        for action in ('install', 'collect', 'rollback'):
            result = subprocess.run([sys.executable, '-S', '-B',
                                     str(extracted / 'scripts/cluster_startup_launcher.py'), '--' + action],
                                    cwd=extracted, capture_output=True, text=True)
            if result.returncode or 'Plan only' not in result.stdout or (extracted / 'delphi-dump').exists():
                raise ValueError('Portable ' + action + ' plan failed: ' + result.stdout + result.stderr)
        # Package validation must fail before connecting if a payload is damaged.
        (extracted / 'native/cluster-bridge/deployment/launcher-release/boot.sh').write_bytes(b'bad')
        result = subprocess.run([sys.executable, '-S', '-B',
                                 str(extracted / 'scripts/cluster_startup_launcher.py'), '--install'],
                                cwd=extracted, capture_output=True, text=True)
        if not result.returncode or 'Package mismatch' not in result.stderr:
            raise ValueError('Tampered payload was not refused')
    report = dict(bundle=str(bundle), bytes=bundle.stat().st_size, sha256=sha(bundle.read_bytes()),
                  portable_plans_passed=True, tampered_payload_refused=True,
                  transaction_and_shell_tests=tests.stderr.strip(),
                  shell_validation_scope='Git Bash with isolated factory-JVM stubs; live QNX syntax gate runs before persistent writes',
                  on_car_tested=False, maps_bridge_enabled=False)
    (BASE / 'launcher-package-review.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
