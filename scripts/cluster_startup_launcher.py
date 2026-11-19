"""Install, collect or roll back the bounded startup-witness car test. Stdlib only."""
from pathlib import Path
import argparse
import datetime as dt
import ftplib
import getpass
import hashlib
import io
import json
import re
import uuid
from project_console import console_session, log as print
from run_observer_smoke import Shell, retrieve
import delphi_inventory as d

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / 'native/cluster-bridge/deployment/launcher-release'
REMOTE = '/persistence/delphi-cluster-launcher-v1'
HMI = '/extbin/apps/hmi/HMI/runHMI.sh'
CFG = '/etc/procman_core.cfg'
STOCK_SHA = 'fcd910cfa317c60da4f352efce9bf8fd79b2f655475ce94f32ccabc7ef3e1182'
CFG_SHA = '004783991da86ca2956470636265be212ab189c5f393afa161affead873680a1'
SYSTEM = 'QNX localhost 6.5.0 2015/12/01-11:00:56EST TI-DRA74X-PG1.1 armle'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def valid_token(token):
    if not re.fullmatch('[0-9a-f]{32}', token):
        raise ValueError('Invalid installation identity')
    return token


def hook(stock, token):
    valid_token(token)
    return stock + ('''
# BEGIN DELPHI STARTUP WITNESS v1
case "$SYSTEM_RUNMODE" in
  ""|normal)
    if [ -r /persistence/delphi-cluster-launcher-v1/boot.sh ]; then
      /bin/sh /persistence/delphi-cluster-launcher-v1/boot.sh ''' + token + ''' </dev/null >/dev/null 2>&1 &
    fi
    ;;
esac
# END DELPHI STARTUP WITNESS v1
''').encode('ascii')


def package(path=PAYLOAD):
    manifest = json.loads((path / 'manifest.json').read_text())
    if (manifest.get('kind') != 'delphi_startup_witness_v1' or
            manifest.get('maps_bridge_enabled') is not False or
            set(manifest.get('files', {})) != {'runHMI.sh.stock', 'boot.sh'}):
        raise ValueError('Wrong startup-witness package')
    files = {name: (path / name).read_bytes() for name in manifest['files']}
    for name, data in files.items():
        if len(data) > 16384 or manifest['files'][name] != dict(bytes=len(data), sha256=sha(data)):
            raise ValueError('Package mismatch: ' + name)
    if sha(files['runHMI.sh.stock']) != STOCK_SHA:
        raise ValueError('Unsupported factory launch script')
    return files


def validate_identity(system, mounts, args, config, current, allowed):
    if not re.search(r'^' + re.escape(SYSTEM) + r'\s*$', system, re.M):
        raise ValueError('Unsupported QNX system')
    for device, mount in [('mmc0t177', 'extbin'), ('mmc0t180', 'persistence')]:
        if not re.search(r'^/dev/' + device + ' on /' + mount + r' type qnx6\s*$', mounts, re.M):
            raise ValueError('Persistent filesystem backing changed: /' + mount)
    if not re.search(r'^\s*\d+ procman -f /etc/procman_core\.cfg\s*$', args, re.M):
        raise ValueError('Unsupported active procman config')
    if sha(config) != CFG_SHA or current not in allowed:
        raise ValueError('Factory configuration or startup script differs; no replacement allowed')


def validate_receipt(data, token):
    valid_token(token)
    expected = (r'BOOT_WITNESS_V1\ninstallation=' + token +
                r'\nlaunch_pid=[1-9][0-9]{0,9}\nparent_pid=[0-9]{1,10}\nrunmode=(?:unset|normal)\n')
    if len(data) > 256 or not re.fullmatch(expected.encode(), data):
        raise ValueError('Invalid or unrelated boot receipt')
    return True


class Car:
    def __init__(self, shell, ftp, folder):
        self.shell, self.ftp, self.folder = shell, ftp, folder

    def read(self, path, limit=16384):
        return retrieve(self.ftp, path, limit)

    def cmd(self, command):
        self.shell.command(command)
        return self.shell.last_response.decode('utf-8', errors='replace').replace('\r', '')

    def put(self, path, data):
        self.ftp.storbinary('STOR ' + path, io.BytesIO(data))
        if self.read(path) != data:
            raise ValueError('Readback mismatch: ' + path)

    def identity(self, allowed):
        readings = {name: self.cmd(command) for name, command in (
            ('system', 'uname -a'), ('mounts', 'mount'),
            ('procman', 'pidin -p procman arguments'))}
        for name, text in readings.items():
            (self.folder / (name + '.txt')).write_text(text)
        config, current = self.read(CFG), self.read(HMI)
        validate_identity(readings['system'], readings['mounts'], readings['procman'],
                          config, current, allowed)
        self.cmd('test -f ' + HMI + ' && test ! -L ' + HMI +
                 ' && test ! -L /extbin && test ! -L /extbin/apps &&'
                 ' test ! -L /extbin/apps/hmi && test ! -L /extbin/apps/hmi/HMI &&'
                 ' test ! -L /persistence')
        return current

    def stage(self, data, token):
        stage = '/ramdisk/delphi-startup-' + valid_token(token)
        # Create as the FTP user so uploads remain writable without mode 777.
        self.ftp.mkd(stage)
        self.cmd('chmod 755 ' + stage)
        for name, blob in data.items():
            self.put(stage + '/' + name, blob)
        return stage


def install(car, files, token):
    stock = files['runHMI.sh.stock']
    car.identity([stock])
    # Existing observer experiments must be cleaned up through their own bundle.
    args = car.cmd('pidin arguments')
    if re.search(r'(?:/ramdisk/delphi-|AndroidAuto\.original|NavigationServer\.original)', args):
        raise ValueError('An existing bridge experiment is active; finish its cleanup first')
    candidate = hook(stock, token)
    stage = car.stage({'runHMI.sh.candidate': candidate, 'boot.sh': files['boot.sh'],
                       'installation.id': (token + '\n').encode()}, token)
    # QNX's own shell must accept both scripts before any persistent write.
    car.cmd('/bin/sh -n ' + stage + '/runHMI.sh.candidate && /bin/sh -n ' + stage + '/boot.sh')
    # mkdir refuses an existing install, symlink or partial earlier transaction.
    car.cmd('mkdir ' + REMOTE + ' && chmod 755 ' + REMOTE)
    car.cmd('cp ' + HMI + ' ' + REMOTE + '/runHMI.sh.stock && chmod 644 ' + REMOTE + '/runHMI.sh.stock')
    if car.read(REMOTE + '/runHMI.sh.stock') != stock:
        raise ValueError('Persistent backup mismatch; launch script untouched')
    for name in ('installation.id', 'boot.sh', 'runHMI.sh.candidate'):
        car.cmd('cp ' + stage + '/' + name + ' ' + REMOTE + '/' + name +
                ' && chmod 644 ' + REMOTE + '/' + name)
    if (car.read(REMOTE + '/boot.sh') != files['boot.sh'] or
            car.read(REMOTE + '/runHMI.sh.candidate') != candidate or
            car.read(REMOTE + '/installation.id') != (token + '\n').encode()):
        raise ValueError('Persistent staging mismatch; launch script untouched')
    # Last identity check precedes replacement. Never FTP directly onto runHMI.sh.
    car.identity([stock])
    sibling = HMI + '.delphi-' + token
    car.cmd('test ! -e ' + sibling + ' && cp ' + REMOTE + '/runHMI.sh.candidate ' + sibling +
            ' && chmod 777 ' + sibling)
    if car.read(sibling) != candidate:
        raise ValueError('Atomic replacement staging mismatch')
    car.cmd('mv -f ' + sibling + ' ' + HMI + ' && sync')
    if car.read(HMI) != candidate:
        raise ValueError('Post-install verification failed; use --rollback --run')
    return dict(installed=True, installation=token, reboot_verified=False,
                maps_bridge_enabled=False, stock_sha256=sha(stock), candidate_sha256=sha(candidate))


def installation(car):
    car.cmd('test -d ' + REMOTE + ' && test ! -L ' + REMOTE)
    token = valid_token(car.read(REMOTE + '/installation.id', 64).decode().strip())
    return token


def collect(car, files):
    token = installation(car)
    candidate = hook(files['runHMI.sh.stock'], token)
    current = car.identity([files['runHMI.sh.stock'], candidate])
    if car.read(REMOTE + '/runHMI.sh.stock') != files['runHMI.sh.stock']:
        raise ValueError('Remote rollback backup mismatch')
    if car.read(REMOTE + '/boot.sh') != files['boot.sh']:
        raise ValueError('Installed witness differs from this bundle')
    try:
        receipt = car.read(REMOTE + '/receipt.txt', 256)
    except ftplib.error_perm as exc:
        if not str(exc).startswith('550'):
            raise
        return dict(installation=token, installed=current == candidate,
                    boot_receipt_verified=False, reason='No boot receipt; radio may not have fully restarted')
    (car.folder / 'receipt.txt').write_bytes(receipt)
    validate_receipt(receipt, token)
    return dict(installation=token, installed=current == candidate, boot_receipt_verified=True,
                maps_bridge_enabled=False, receipt_sha256=sha(receipt))


def rollback(car, files):
    stock = files['runHMI.sh.stock']
    # A repeated rollback remains safe even if persistent staging was incomplete.
    if car.read(HMI) == stock:
        car.identity([stock])
        return dict(factory_startup_restored=True, already_stock=True)
    token = installation(car)
    candidate = hook(stock, token)
    car.identity([candidate])
    if car.read(REMOTE + '/runHMI.sh.stock') != stock:
        raise ValueError('Remote backup changed; refusing restoration')
    sibling = HMI + '.delphi-rollback-' + uuid.uuid4().hex
    car.cmd('test ! -e ' + sibling + ' && cp ' + REMOTE + '/runHMI.sh.stock ' + sibling +
            ' && chmod 777 ' + sibling + ' && /bin/sh -n ' + sibling)
    if car.read(sibling) != stock:
        raise ValueError('Rollback staging mismatch')
    car.identity([candidate])
    car.cmd('mv -f ' + sibling + ' ' + HMI + ' && sync')
    if car.read(HMI) != stock:
        raise ValueError('Factory startup restoration not verified')
    return dict(factory_startup_restored=True, stock_sha256=STOCK_SHA,
                inert_backup_retained=REMOTE)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    for name in ('install', 'collect', 'rollback'):
        action.add_argument('--' + name, action='store_true')
    p.add_argument('--run', action='store_true')
    p.add_argument('--phone-unplugged', action='store_true')
    p.add_argument('--host', default='192.168.1.4')
    p.add_argument('--port', type=int, default=21)
    p.add_argument('--telnet-port', type=int, default=23)
    p.add_argument('--username', default='ftpuser')
    p.add_argument('--telnet-user', default='root')
    p.add_argument('--ask-password', action='store_true')
    p.add_argument('--timeout', type=float, default=60)
    a = p.parse_args(argv)
    if not 15 <= a.timeout <= 120 or not all(1 <= n <= 65535 for n in (a.port, a.telnet_port)):
        p.error('Invalid timeout or port')
    files = package()
    operation = 'install' if a.install else 'collect' if a.collect else 'rollback'
    print('Startup witness v1: ' + operation + '. Maps bridge is not enabled by this test.')
    if not a.run:
        print('Plan only. Add --run --phone-unplugged with the parked car connected by Ethernet.')
        return 0
    if not a.phone_unplugged:
        p.error('Use --phone-unplugged after unplugging the phone and finishing any observer cleanup')
    base = ROOT / 'delphi-dump'
    for parent in (base, *base.parents):
        d.reject_link(parent)
    base.mkdir(exist_ok=True)
    token = uuid.uuid4().hex
    folder = base / ('_startup_launcher_' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + token[:8])
    folder.mkdir()
    report = dict(operation=operation, success=False, maps_bridge_enabled=False)
    shell = None
    try:
        password = getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
        shell = Shell(a, folder)
        with ftplib.FTP(timeout=a.timeout) as ftp:
            ftp.connect(a.host, a.port)
            ftp.login(a.username, password)
            car = Car(shell, ftp, folder)
            report.update(install(car, files, token) if a.install else
                          collect(car, files) if a.collect else rollback(car, files))
        report['success'] = True
    except Exception as exc:
        report['error'] = type(exc).__name__ + ': ' + str(exc)
        print(report['error'])
        print('Return this results folder. If installation was interrupted, --rollback --run --phone-unplugged can restore the verified factory script.')
    finally:
        if shell:
            report['actions'] = shell.actions
            shell.close()
        (folder / 'launcher-summary.json').write_text(json.dumps(report, indent=2) + '\n')
        print('Results: ' + str(folder))
    if report['success']:
        print('Install verified. Fully restart the radio, then run --collect.' if a.install else json.dumps(report, indent=2))
    return 0 if report['success'] else 2


if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
