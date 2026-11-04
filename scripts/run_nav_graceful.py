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
from collect_map_session import processes, capture_allocator_pages

ROOT = Path(__file__).resolve().parents[1]
CYCLE_HELD = True
RELEASE = Path('native/cluster-bridge/nav-control/release')
REFERENCES = {
 '/extbin/apps/bin/NavigationServer': (4909668, 'a999725350df8503c44a25da2676a8c1a99914a99a36f24bb6334a509def4afe'),
 '/proc/boot/procman': (196184, 'c32c018b515396bd0b322fb2014b45f2fba37d6000b2d178e9dc402c6845f05d'),
 '/proc/boot/libc.so.3': (490310, '76ff9b07201a77ad231905741b25a97fd722a163c26a7ca0e36f17331bd12e9b'),
 '/proc/boot/libXSAL.so': (130364, 'b754301a9656e9d8f296d9ab0f9326749073cca602e79e63689d0290228ad4e1'),
}
sha = lambda b: hashlib.sha256(b).hexdigest()


def package(root,diagnostic=False,recovery=False):
 release=root/(Path('native/cluster-bridge/nav-control/recovery-release') if recovery else RELEASE)
 manifest = json.loads((release/'manifest.json').read_text())
 data = (release/'nav_cycle').read_bytes()
 if (manifest.get('kind') != ('nav_stalled_recovery' if recovery else 'nav_shutdown_allocator_diagnostic' if diagnostic else 'stock_nav_graceful_cycle') or
     manifest.get('nav_app_id') != 29 or (recovery and manifest.get('qnx_recovery_guard_passed') is not True) or (diagnostic and manifest.get('qnx_page_reader_passed') is not True) or not manifest.get('qnx_guarded_cycle_passed') or
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


def assess_cycle(value, before, after, ident, newident,recovery=False):
 if (not isinstance(value, dict) or value.get('version') != 1 or
     value.get('process_cycle_verified') is not True or
     value.get('functional_maps_verified') is not False or
     value.get('signals_to_nav') is not recovery or
     value.get('stage') != ('recover_restart' if recovery else 'new_process') or value.get('last_exit_raw') != (9 if recovery else 0) or (recovery and value.get('termination_signal') != 9) or
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


def map_confirmation(answer):
 value=answer.strip().casefold()
 return {'y':'yes','yes':'yes','n':'no','no':'no'}.get(value,'unsure')


def main(argv=None):
 p = argparse.ArgumentParser(description=__doc__)
 p.add_argument('--run', action='store_true')
 p.add_argument('--diagnose-shutdown',action='store_true',help='One controlled reproduction with automatic baseline and stalled allocator capture; normal cycle stays held')
 p.add_argument('--recover-stalled',action='store_true',help='Recover only the pinned already-crashed navigation session, not a healthy process')
 p.add_argument('--phone-unplugged', action='store_true')
 p.add_argument('--factory-maps-working', action='store_true',help='Factory maps checked on radio and cluster in turn using the location toggle; simultaneous maps are not required')
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
  print('Run parked, phone unplugged, ignition on, factory maps checked in each location using the toggle.')
  print('Normal cycle is held. The approved diagnostic requires --run --diagnose-shutdown --phone-unplugged --factory-maps-working.')
  return 0
 if a.recover_stalled and a.diagnose_shutdown:p.error('Choose diagnostic shutdown or stalled recovery, not both')
 if not a.phone_unplugged or (not a.recover_stalled and not a.factory_maps_working):
  p.error('--phone-unplugged and --factory-maps-working are required')
 if CYCLE_HELD and not (a.diagnose_shutdown or a.recover_stalled):
  p.error('Graceful-cycle tests are held: stock shutdown stalled on the unit. Use collect_map_session.py --run --state broken --shutdown-stack for the read-only capture.')
 payload = package(ROOT,diagnostic=a.diagnose_shutdown,recovery=a.recover_stalled)
 expected_identity=None
 if a.recover_stalled:
  expected_identity=json.loads((ROOT/'native/cluster-bridge/nav-control/recovery-release/manifest.json').read_text())['recovery_identity']
  check_inspect(expected_identity,expected_identity['pid'])
 base = ROOT/'delphi-dump'
 for parent in (base, *base.parents):
  d.reject_link(parent)
 base.mkdir(exist_ok=True)
 token = uuid.uuid4().hex
 remote = '/ramdisk/delphi-nav-cycle_' + token
 folder = base/(('_nav_stall_recovery_' if a.recover_stalled else '_nav_shutdown_diag_' if a.diagnose_shutdown else '_nav_graceful_') + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S') + '_' + token[:8])
 folder.mkdir()
 summary = dict(kind='nav_stalled_recovery' if a.recover_stalled else 'nav_shutdown_allocator_diagnostic' if a.diagnose_shutdown else 'stock_nav_graceful_cycle',diagnostic_mode=a.diagnose_shutdown,diagnostic_revision=2,page_reader='native_guarded_pread64',raw_pages=[],diagnostics_complete=False, remote=remote, artifacts=[], errors=[],
                process_cycle_verified=False, functional_maps_verified=False,
                user_reported_initial_maps='stalled_from_pinned_capture' if a.recover_stalled else 'each_location_checked_sequentially',map_confirmation_mode='sequential_location_toggle',simultaneous_maps_required=False, video_writes=False,
                signals_to_nav=None if a.recover_stalled else False, control_attempts=0,
                preflight_revision=2, reference_checks=[])
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
  # QNX image-filesystem files use the established shell-to-RAM copy route.
  # FTP reads only regular staged files; preserve every checked byte locally.
  with ftp_connection() as ftp:
   ftp.mkd(remote)
  shell = Shell(a, folder)
  shell.command('cd '+remote)
  cwd_verified = True
  for path, (size, expected) in REFERENCES.items():
   name = path.rsplit('/', 1)[-1]+'.reference'
   log = name+'.copy.txt'
   check = dict(source=path, file=name, method='shell_copy_to_ram_then_ftp',
                expected_bytes=size, expected_sha256=expected, matched=False)
   summary['reference_checks'].append(check)
   rc = shell.command('cp '+path+' '+name+' > '+log+' 2>&1', required=False)
   check['copy_exit_code'] = rc
   shell.command('chmod 644 '+log)
   fetch(log)
   if rc:
    raise ValueError('Reference copy failed: '+path+' exit '+str(rc))
   shell.command('chmod 644 '+name)
   data = fetch(name)
   actual = sha(data)
   check.update(actual_bytes=len(data), actual_sha256=actual,
                matched=len(data)==size and actual==expected)
   persist()
   if not check['matched']:
    raise ValueError('Unit profile mismatch: '+path+'; expected bytes='+str(size)+
                     ' sha256='+expected+'; actual bytes='+str(len(data))+
                     ' sha256='+actual+'; saved '+name)
  summary['unit_files_verified'] = True
  persist()
  with ftp_connection() as ftp:
   ftp.storbinary('STOR '+remote+'/nav_cycle', io.BytesIO(payload))
   if read_bounded(ftp, remote+'/nav_cycle', 131072) != payload:
    raise ValueError('Helper upload readback mismatch')
  summary['helper_upload_verified'] = True
  shell.command('chmod 500 nav_cycle')
  before = processes(capture('processes-before.txt', 'pidin arguments'))
  if not all(n in before for n in ('NavigationServer', 'Most', 'TransportServer', 'DisplayManagement', 'screen-cda', 'NavServices')):
   raise ValueError('Required map services absent')
  summary['processes_before'] = before
  ident = inspect(before['NavigationServer'], 'identity-before.json')
  summary['identity_before'] = ident
  if a.recover_stalled and ident!=expected_identity:raise ValueError('Current navigation identity does not match the pinned stalled session; no recovery attempted')
  snapshot('before', before)
  if a.diagnose_shutdown:
   summary['raw_pages'].extend(capture_allocator_pages(shell,capture,fetch,before['NavigationServer'],'raw-before',ident))
  summary['control_attempts'] = 1
  persist()
  print('Recovering the pinned map-cleanup crash through factory autorestart.' if a.recover_stalled else 'Requesting one orderly stock navigation restart. Factory maps will briefly disappear.')
  command = ('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle '+('recover ' if a.recover_stalled else 'cycle ')+
             ' '.join(str(ident[k]) for k in ('pid', 'start_time', 'manager_pid', 'manager_start'))+
             ' > cycle.json 2> cycle-errors.txt')
  started=time.monotonic()
  rc = shell.command(command, required=False)
  summary['cycle_elapsed_seconds']=round(time.monotonic()-started,3)
  summary['helper_exit_code'] = rc
  for name in ('cycle.json', 'cycle-errors.txt'):
   shell.command('chmod 644 '+name)
   fetch(name)
  value = json.loads((folder/'cycle.json').read_text())
  summary['signals_to_nav']=value.get('signals_to_nav')
  summary['termination_signal']=value.get('termination_signal',0)
  if rc:
   raise ValueError('Native action incomplete/refused; no automatic retry. Exit '+str(rc))
  time.sleep(15)
  after = processes(capture('processes-after.txt', 'pidin arguments'))
  summary['processes_after'] = after
  newident = inspect(after['NavigationServer'], 'identity-after.json')
  summary['identity_after'] = newident
  assess_cycle(value, before, after, ident, newident,recovery=a.recover_stalled)
  summary['process_cycle_verified'] = True
  if not a.diagnose_shutdown:
   print('Navigation process restart verified. Check the radio map, then use the map-location button to check the cluster map.')
   answer = map_confirmation(input('Does the map work in EACH location when selected with the toggle? Simultaneous display is not required. [y/yes, n/no, unsure]: '))
   summary['user_reported_final_maps'] = answer
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
  if shell and cwd_verified and not shell.broken and summary.get('unit_files_verified'):
   # Diagnostics only; never retry a cycle or send fallback signals after failure.
   try:
    final = processes(capture('processes-final.txt', 'pidin arguments', required=False))
    if all(n in final for n in ('NavigationServer', 'Most', 'screen-cda')):
     snapshot('after', final)
     if a.diagnose_shutdown and summary['control_attempts']:
      for sample in (1,2):
       time.sleep(2 if sample==1 else 6)
       current=processes(capture('raw-after-'+str(sample)+'-processes.txt','pidin arguments'))
       if current!=final:raise ValueError('Map service PID changed during diagnostic capture')
       current_identity=inspect(current['NavigationServer'],'raw-after-'+str(sample)+'-identity.json')
       summary['raw_pages'].extend(capture_allocator_pages(shell,capture,fetch,current['NavigationServer'],'raw-after-'+str(sample),current_identity))
      summary['diagnostics_complete']=len(summary['raw_pages'])==9
      persist()
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
 if a.diagnose_shutdown:
  print('Diagnostic memory collection complete:',summary['diagnostics_complete'],'; native helper exit:',summary.get('helper_exit_code'))
  return 0 if summary['diagnostics_complete'] else 2
 return 0 if summary['process_cycle_verified'] and summary['functional_maps_verified'] else 2


if __name__ == '__main__':
 with console_session(__file__, __doc__):
  raise SystemExit(main())
