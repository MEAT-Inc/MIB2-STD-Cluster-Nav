"""Exercise startup install/collection/rollback transactions without a car."""
from pathlib import Path
import ftplib
import re
import shlex
import os
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cluster_startup_launcher as m

TOKEN = '12345678' * 4
EVIDENCE = m.ROOT / 'delphi-dump/_deployment_preflight_20261119_131638_794286b0/deployment-preflight'
STOCK = (EVIDENCE / 'runHMI.sh').read_bytes()
FILES = {'runHMI.sh.stock': STOCK,
         'boot.sh': (m.ROOT / 'native/cluster-bridge/deployment/boot-witness.sh').read_bytes()}


class FakeCar:
    """Tiny filesystem transaction simulator; shell syntax is tested separately."""
    def __init__(self, folder, fail_at=None):
        self.folder = folder
        self.files = {m.HMI: STOCK, m.CFG: (EVIDENCE / 'procman_core.cfg').read_bytes()}
        self.dirs = set()
        self.operations = []
        self.fail_at = fail_at
        self.active_observer = False
        self.ftp = self

    def mkd(self, path):
        self.mutation('FTP MKD ' + path)
        if path in self.dirs:
            raise OSError('exists')
        self.dirs.add(path)

    def mutation(self, operation):
        self.operations.append(operation)
        if len(self.operations) == self.fail_at:
            raise OSError('simulated interruption')

    def read(self, path, limit=16384):
        if path not in self.files:
            raise ftplib.error_perm('550 missing')
        data = self.files[path]
        if len(data) > limit:
            raise ValueError('size')
        return data

    def put(self, path, data):
        self.mutation('put ' + path)
        self.files[path] = data

    def identity(self, allowed):
        m.validate_identity((EVIDENCE / 'system.txt').read_text(),
                            (EVIDENCE / 'mounts.txt').read_text(),
                            (EVIDENCE / 'procman-arguments.txt').read_text(),
                            self.files[m.CFG], self.files[m.HMI], allowed)
        return self.files[m.HMI]

    stage = m.Car.stage

    def cmd(self, command):
        if command == 'pidin arguments':
            return '42 /ramdisk/delphi-aa-observer_x/AndroidAuto.original' if self.active_observer else '42 AndroidAuto'
        for segment in command.split(' && '):
            words = shlex.split(segment)
            if words[0] == 'test':
                if words[1:3] == ['!', '-e']:
                    assert words[3] not in self.files
                elif words[1] == '-d':
                    if words[2] not in self.dirs:
                        raise OSError('not directory')
                continue
            if words[:2] == ['/bin/sh', '-n']:
                assert words[2] in self.files
                continue
            self.mutation(segment)
            if words[0] == 'mkdir':
                if words[1] in self.dirs:
                    raise OSError('exists')
                self.dirs.add(words[1])
            elif words[0] == 'cp':
                self.files[words[2]] = self.files[words[1]]
            elif words[:2] == ['mv', '-f']:
                self.files[words[3]] = self.files.pop(words[2])
            elif words[0] not in ('chmod', 'sync'):
                raise AssertionError('Unexpected command ' + segment)
        return ''


class LauncherTests(unittest.TestCase):
    def test_real_shell_preserves_factory_launch_and_guards_witness(self):
        bash = Path('C:/Program Files/Git/bin/bash.exe')
        if not bash.is_file():
            self.skipTest('Local Git Bash unavailable; QNX syntax is checked again before install')
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            root, ram, tools = base / 'persistent', base / 'ram', base / 'bin'
            for folder in (root, ram, tools):
                folder.mkdir()
            jvm = base / 'jvm.txt'
            (tools / 'on').write_text('#!/bin/sh\nprintf "JVM_LAUNCHED\\n" >> ' + shlex.quote(jvm.as_posix()) + '\n')
            (tools / 'waitfor').write_text('#!/bin/sh\nexit 0\n')
            witness = FILES['boot.sh'].replace(m.REMOTE.encode(), root.as_posix().encode())
            witness = witness.replace(b'/ramdisk/delphi-startup-witness-v1', (ram / 'lock').as_posix().encode())
            (root / 'boot.sh').write_bytes(witness)
            candidate = m.hook(STOCK, TOKEN).replace(m.REMOTE.encode(), root.as_posix().encode())
            script = base / 'runHMI.sh'
            script.write_bytes(candidate)
            env = os.environ.copy()
            env['PATH'] = tools.as_posix() + ':' + '/usr/bin:/bin'
            env['JVM_TEST_PATH'] = jvm.as_posix()
            for mode in ('normal', 'swdl', 'unknown', ''):
                with self.subTest(mode=mode):
                    env['SYSTEM_RUNMODE'] = mode
                    receipt = root / 'receipt.txt'
                    receipt.unlink(missing_ok=True)
                    lock = ram / 'lock'
                    if lock.exists():
                        lock.rmdir()
                    jvm.unlink(missing_ok=True)
                    result = subprocess.run([str(bash), '-c', '. ' + shlex.quote(script.as_posix()) + '; wait'],
                                            env=env, capture_output=True, text=True, timeout=15)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(jvm.read_text(), 'JVM_LAUNCHED\n')
                    if mode in ('', 'normal'):
                        m.validate_receipt(receipt.read_bytes(), TOKEN)
                        receipt.write_bytes(b'UNCHANGED')
                        repeat = subprocess.run([str(bash), str(root / 'boot.sh'), TOKEN],
                                                env=env, capture_output=True, timeout=15)
                        self.assertEqual(repeat.returncode, 0, repeat.stderr)
                        self.assertEqual(receipt.read_bytes(), b'UNCHANGED')
                    else:
                        self.assertFalse(receipt.exists())

    def test_install_boot_collect_rollback_and_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            car = FakeCar(Path(td))
            result = m.install(car, FILES, TOKEN)
            self.assertTrue(result['installed'])
            self.assertFalse(result['reboot_verified'])
            self.assertEqual(car.files[m.HMI], m.hook(STOCK, TOKEN))
            self.assertEqual(car.files[m.REMOTE + '/runHMI.sh.stock'], STOCK)
            self.assertFalse(m.collect(car, FILES)['boot_receipt_verified'])
            car.files[m.REMOTE + '/receipt.txt'] = (
                'BOOT_WITNESS_V1\ninstallation=' + TOKEN +
                '\nlaunch_pid=234\nparent_pid=123\nrunmode=unset\n').encode()
            self.assertTrue(m.collect(car, FILES)['boot_receipt_verified'])
            self.assertTrue(m.rollback(car, FILES)['factory_startup_restored'])
            self.assertEqual(car.files[m.HMI], STOCK)
            self.assertTrue(m.rollback(car, FILES)['already_stock'])

    def test_each_interruption_preserves_old_or_complete_new_script_and_rollback(self):
        with tempfile.TemporaryDirectory() as td:
            complete = FakeCar(Path(td))
            m.install(complete, FILES, TOKEN)
            for boundary in range(1, len(complete.operations) + 1):
                car = FakeCar(Path(td), fail_at=boundary)
                with self.subTest(boundary=boundary):
                    with self.assertRaises(OSError):
                        m.install(car, FILES, TOKEN)
                    self.assertIn(car.files[m.HMI], (STOCK, m.hook(STOCK, TOKEN)))
                    car.fail_at = None
                    self.assertTrue(m.rollback(car, FILES)['factory_startup_restored'])
                    self.assertEqual(car.files[m.HMI], STOCK)

    def test_unknown_firmware_and_active_experiment_refused_without_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            for changed in ('script', 'config', 'observer'):
                car = FakeCar(Path(td))
                if changed == 'observer':
                    car.active_observer = True
                else:
                    car.files[m.HMI if changed == 'script' else m.CFG] += b'changed'
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    m.install(car, FILES, TOKEN)
                self.assertEqual(car.operations, [])

    def test_existing_install_and_changed_script_or_backup_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            car = FakeCar(Path(td))
            m.install(car, FILES, TOKEN)
            before = dict(car.files)
            with self.assertRaises(ValueError):
                m.install(car, FILES, TOKEN)
            self.assertEqual(car.files, before)
            car.files[m.HMI] += b'changed'
            with self.assertRaises(ValueError):
                m.rollback(car, FILES)
            car.files[m.HMI] = before[m.HMI]
            car.files[m.REMOTE + '/runHMI.sh.stock'] += b'changed'
            with self.assertRaises(ValueError):
                m.rollback(car, FILES)
            self.assertEqual(car.files[m.HMI], before[m.HMI])

    def test_receipt_and_installation_identity_are_exact(self):
        good = ('BOOT_WITNESS_V1\ninstallation=' + TOKEN +
                '\nlaunch_pid=234\nparent_pid=123\nrunmode=normal\n').encode()
        self.assertTrue(m.validate_receipt(good, TOKEN))
        for bad in (good + b'junk', good.replace(TOKEN.encode(), b'0' * 32),
                    good.replace(b'normal', b'swdl'), good * 5):
            with self.assertRaises(ValueError):
                m.validate_receipt(bad, TOKEN)
        for token in ('../etc', TOKEN + ';', 'F' * 32, ''):
            with self.assertRaises(ValueError):
                m.hook(STOCK, token)


if __name__ == '__main__':
    from project_console import console_session
    with console_session(__file__, __doc__):
        unittest.main()
