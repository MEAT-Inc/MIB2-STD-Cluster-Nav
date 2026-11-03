"""One guarded stock navigation cycle; factory map recovery remains a visual check."""
from project_console import console_session, log as print
import argparse
import datetime as dt
import ftplib
import getpass
import hashlib
import io
import json
from pathlib import Path
import time
import uuid
import delphi_inventory as d
from run_observer_smoke import Shell
from collect_map_session import processes

ROOT = Path(__file__).resolve().parents[1]
RELEASE = Path('native/cluster-bridge/nav-control/release')
REFERENCES = {
 '/extbin/apps/bin/NavigationServer': (4909668, 'a999725350df8503c44a25da2676a8c1a99914a99a36f24bb6334a509def4afe'),
 '/proc/boot/procman': (196184, 'c32c018b515396bd0b322fb2014b45f2fba37d6000b2d178e9dc402c6845f05d'),
 '/proc/boot/libXSAL.so': (130364, 'b754301a9656e9d8f296d9ab0f9326749073cca602e79e63689d0290228ad4e1'),
}
sha = lambda b: hashlib.sha256(b).hexdigest()


def package(root):
 manifest = json.loads((root/RELEASE/'manifest.json').read_text())
 data = (root/RELEASE/'nav_cycle').read_bytes()
 if (manifest.get('kind') != 'stock_nav_graceful_cycle' or
     manifest.get('nav_app_id') != 29 or not manifest.get('qnx_guarded_cycle_passed') or
     manifest.get('files') != {'nav_cycle': {'bytes': len(data), 'sha256': sha(data)}} or
     not 0 < len(data) < 131072 or data[:7] != b'\x7fELF\x01\x01\x01' or
     data[16:20] != b'\x02\x00\x28\x00' or b'idle_fixture' in data):
  raise ValueError('Unverified production navigation helper')
 return data


def check_inspect(value, pid):
 fields = ('pid', 'start_time', 'manager_pid', 'manager_start')
 if (not isinstance(value, dict) or value.get('version') != 1 or
     value.get('readonly') is not True or value.get('app_id') != 29 or
     value.get('state') != 3 or value.get('pid') != pid or
     any(type(value.get(k)) is not int or value[k] <= 0 for k in fields) or
     value['manager_pid'] == pid or max(value['pid'], value['manager_pid']) > 0x7fffffff or
     max(value['start_time'], value['manager_start']) > 0xffffffffffffffff):
  raise ValueError('Incomplete or unexpected native process identity')
 return value


def assess_cycle(value, before, after, ident, newident):
 if (not isinstance(value, dict) or value.get('version') != 1 or
     value.get('process_cycle_verified') is not True or
     value.get('functional_maps_verified') is not False or
     value.get('signals_to_nav') is not False or
     value.get('stage') != 'new_process' or value.get('last_exit_raw') != 0 or
     value.get('old_pid') != before['NavigationServer'] or
     value.get('new_pid') != after['NavigationServer'] or
     value.get('new_start') != newident['start_time'] or
     before['NavigationServer'] == after['NavigationServer'] or
     ident['start_time'] == newident['start_time'] or
     any(ident[k] != newident[k] for k in ('manager_pid', 'manager_start')) or
     {k:v for k,v in before.items() if k != 'NavigationServer'} !=
     {k:v for k,v in after.items() if k != 'NavigationServer'}):
  raise ValueError('Stock process-cycle verification failed')


def read_bounded(ftp, path, limit):
 blob = bytearray()
 def receive(block):
  if len(blob) + len(block) > limit:
   raise ValueError('Transfer exceeds fixed limit: ' + path)
  blob.extend(block)
 ftp.retrbinary('RETR ' + path, receive)
 return bytes(blob)


def main(argv=None):
 p = argparse.ArgumentParser(description=__doc__)
 p.add_argument('--run', action='store_true')
 p.add_argument('--phone-unplugged', action='store_true')
 p.add_argument('--factory-maps-working', action='store_true')
 p.add_argument('--host', default='192.168.1.4')
 p.add_argument('--port', type=int, default=21)
 p.add_argument('--username', default='ftpuser')
 p.add_argument('--ask-password', action='store_true')
 p.add_argument('--telnet-port', type=int, default=23)
 p.add_argument('--telnet-user', default='root')
 p.add_argument('--timeout', type=float, default=90)
 a = p.parse_args(argv)
 if not 1 <= a.port <= 65535 or not 1 <= a.telnet_port <= 65535 or not 70 <= a.timeout <= 120:
  p.error('Ports must be 1..65535; timeout must be 70..120 seconds')
 if any(ord(c) < 32 or ord(c) == 127 for v in (a.host, a.username, a.telnet_user) for c in v):
  p.error('Control characters in connection arguments')
 if not a.run:
  print('Plan only. One clean stock navigation shutdown/start using the factory SAL events.')
  print('Run parked, phone unplugged, ignition on, factory maps working on both screens.')
  print('Use --run --phone-unplugged --factory-maps-working. No replay in this test.')
  return 0
 if not a.phone_unplugged or not a.factory_maps_working:
  p.error('--phone-unplugged and --factory-maps-working are required')
 payload = package(ROOT)
 base = ROOT/'delphi-dump'
 for parent in (base, *base.parents):
  d.reject_link(parent)
 base.mkdir(exist_ok=True)
 token = uuid.uuid4().hex
 remote = '/ramdisk/delphi-nav-cycle_' + token
 folder = base/('_nav_graceful_' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + token[:8])
 folder.mkdir()
 summary = dict(kind='stock_nav_graceful_cycle', remote=remote, artifacts=[], errors=[],
                process_cycle_verified=False, functional_maps_verified=False,
                user_reported_initial_maps='both_working', video_writes=False,
                signals_to_nav=False, control_attempts=0)
 password = getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
 shell = None
 cwd_verified = False
 total = 0
 def persist():
  (folder/'nav-graceful-summary.json').write_text(json.dumps(summary, indent=2))
 def ftp_connection():
  ftp = ftplib.FTP(timeout=a.timeout)
  try:
   ftp.connect(a.host, a.port)
   ftp.login(a.username, password)
   ftp.voidcmd('TYPE I')
   return ftp
  except BaseException:
   ftp.close()
   raise
 def save(name, data):
  nonlocal total
  if total + len(data) > 32*1024*1024:
   raise ValueError('Aggregate transfer limit exceeded')
  total += len(data)
  (folder/name).write_bytes(data)
  summary['artifacts'].append(dict(file=name, bytes=len(data), sha256=sha(data)))
  persist()
  return data
 def fetch(name):
  with ftp_connection() as ftp:
   return save(name, read_bounded(ftp, remote+'/'+name, 8*1024*1024))
 def capture(name, command, required=True):
  rc = shell.command(command+' > '+name+' 2>&1', required=False)
  shell.command('chmod 644 '+name)
  data = fetch(name)
  if required and rc:
   raise ValueError('Capture failed: '+name+' exit '+str(rc))
  if rc:
   summary['errors'].append(dict(file=name, error='optional capture exit '+str(rc)))
  return data
 def inspect(pid, name):
  data = capture(name, 'LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle inspect '+str(pid))
  return check_inspect(json.loads(data), pid)
 def snapshot(label, pids):
  for name in ('NavigationServer', 'Most', 'screen-cda'):
   capture(label+'-'+name+'-threads.txt', 'pidin -p '+str(pids[name])+' threads', required=False)
  capture(label+'-system-log.txt', 'sloginfo -t', required=False)
 persist()
 try:
  print('Checking exact unit firmware files before uploading the helper.')
  with ftp_connection() as ftp:
   for path, (size, expected) in REFERENCES.items():
    data = read_bounded(ftp, path, size+1)
    if len(data) != size or sha(data) != expected:
     raise ValueError('Unit profile mismatch: '+path)
   summary['unit_files_verified'] = True
   ftp.mkd(remote)
   ftp.storbinary('STOR '+remote+'/nav_cycle', io.BytesIO(payload))
   if read_bounded(ftp, remote+'/nav_cycle', 131072) != payload:
    raise ValueError('Helper upload readback mismatch')
  shell = Shell(a, folder)
  shell.command('cd '+remote)
  cwd_verified = True
  shell.command('chmod 500 nav_cycle')
  before = processes(capture('processes-before.txt', 'pidin arguments'))
  if not all(n in before for n in ('NavigationServer', 'Most', 'TransportServer', 'DisplayManagement', 'screen-cda', 'NavServices')):
   raise ValueError('Required map services absent')
  summary['processes_before'] = before
  ident = inspect(before['NavigationServer'], 'identity-before.json')
  summary['identity_before'] = ident
  snapshot('before', before)
  summary['control_attempts'] = 1
  persist()
  print('Requesting one orderly stock navigation restart. Factory maps will briefly disappear.')
  command = ('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle cycle '+
             ' '.join(str(ident[k]) for k in ('pid', 'start_time', 'manager_pid', 'manager_start'))+
             ' > cycle.json 2> cycle-errors.txt')
  rc = shell.command(command, required=False)
  summary['helper_exit_code'] = rc
  for name in ('cycle.json', 'cycle-errors.txt'):
   shell.command('chmod 644 '+name)
   fetch(name)
  if rc:
   raise ValueError('Native cycle incomplete/refused; no automatic retry. Exit '+str(rc))
  value = json.loads((folder/'cycle.json').read_text())
  time.sleep(15)
  after = processes(capture('processes-after.txt', 'pidin arguments'))
  summary['processes_after'] = after
  newident = inspect(after['NavigationServer'], 'identity-after.json')
  summary['identity_after'] = newident
  assess_cycle(value, before, after, ident, newident)
  summary['process_cycle_verified'] = True
  print('Clean process cycle verified. Waiting for your observation of both factory map views.')
  answer = input('Are factory maps visible on BOTH the head unit and cluster? [yes/no/unsure]: ').strip().lower()
  summary['user_reported_final_maps'] = answer if answer in ('yes', 'no') else 'unsure'
  summary['functional_maps_verified'] = answer == 'yes'
 except (OSError, EOFError, ValueError, RuntimeError, KeyError, KeyboardInterrupt, ftplib.Error) as exc:
  message = type(exc).__name__+': '+str(exc)
  summary['errors'].append(dict(error=message.replace(password, '[redacted]') if password else message))
 finally:
  # A lost command connection must not prevent independent FTP retrieval.
  if summary['control_attempts']:
   saved = {v['file'] for v in summary['artifacts']}
   for name in ('cycle.json', 'cycle-errors.txt'):
    if name not in saved:
     try:
      fetch(name)
     except (OSError, EOFError, ValueError, RuntimeError, ftplib.Error) as exc:
      summary['errors'].append(dict(file=name, error='Result retrieval: '+str(exc)))
  if shell and cwd_verified and not shell.broken:
   # Diagnostics only; never retry a cycle or send fallback signals after failure.
   try:
    final = processes(capture('processes-final.txt', 'pidin arguments', required=False))
    if all(n in final for n in ('NavigationServer', 'Most', 'screen-cda')):
     snapshot('after', final)
    for i in range(1, 5):
     name = 'DTS_Shm_'+str(i)+'.bin'
     rc = shell.command('cp /dev/shmem/DTS_Shm_'+str(i)+' '+name+' > trace-copy-'+str(i)+'.txt 2>&1', required=False)
     shell.command('chmod 644 trace-copy-'+str(i)+'.txt')
     fetch('trace-copy-'+str(i)+'.txt')
     if rc == 0:
      shell.command('chmod 644 '+name)
      fetch(name)
     else:
      summary['errors'].append(dict(file=name, error='optional ring copy exit '+str(rc)))
    summary['trace_note'] = 'Copies of existing concurrently written DTS rings; not atomic snapshots. Trace settings unchanged.'
   except (OSError, EOFError, ValueError, RuntimeError, KeyError, ftplib.Error) as exc:
    summary['errors'].append(dict(error='Final diagnostics: '+str(exc)))
  if shell:
   summary['actions'] = shell.actions
   shell.close()
  persist()
 print('Saved:', folder)
 print('Return the entire folder. No playback was attempted.')
 if not summary['functional_maps_verified']:
  print('Map recovery is unconfirmed. If maps remain stuck, reboot the radio before any further experiment.')
 return 0 if summary['process_cycle_verified'] and summary['functional_maps_verified'] else 2


if __name__ == '__main__':
 with console_session(__file__, __doc__):
  raise SystemExit(main())
