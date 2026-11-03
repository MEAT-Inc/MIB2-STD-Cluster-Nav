from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import contextlib, io, json, tempfile, unittest
from unittest.mock import patch
import run_nav_graceful as m

class Tests(unittest.TestCase):
 def test_plan_and_missing_requirements_do_not_connect(self):
  with patch.object(m.ftplib, 'FTP') as ftp, patch.object(m, 'Shell') as shell, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
   self.assertEqual(m.main([]), 0)
   with self.assertRaises(SystemExit):
    m.main(['--run'])
  ftp.assert_not_called()
  shell.assert_not_called()

 def exercise(self, mode='good', visual='yes'):
  commands, db, cycles = [], {}, []
  ident = dict(version=1, readonly=True, pid=11, start_time=100, manager_pid=1, manager_start=50, app_id=29, state=3)
  newident = dict(ident, pid=21, start_time=200)
  before = b'11 NavigationServer\n12 Most\n13 TransportServer\n14 DisplayManagement\n15 screen-cda\n16 NavServices\n'
  after = before.replace(b'11 NavigationServer', b'21 NavigationServer')
  helper = b'helper'
  refs = {'/extbin/apps/bin/NavigationServer': b'nav', '/proc/boot/procman': b'pm', '/proc/boot/libXSAL.so': b'sal'}
  class FTP:
   def __init__(self, **kw): pass
   def __enter__(self): return self
   def __exit__(self, *args): pass
   def connect(self, *args): pass
   def login(self, *args): pass
   def voidcmd(self, *args): pass
   def close(self): pass
   def mkd(self, *args): pass
   def storbinary(self, command, stream): db[command.rsplit('/', 1)[-1]] = stream.read()
   def retrbinary(self, command, save):
    path = command[5:]
    if path in refs:
     save(refs[path] if mode != 'profile' else b'wrong')
    else:
     save(db[path.rsplit('/', 1)[-1]])
  class Shell:
   broken = False
   def __init__(self, *args): self.actions = []
   def close(self): pass
   def command(self, command, required=True):
    commands.append(command)
    self.actions.append(dict(command=command, exit_code=0))
    if './nav_cycle cycle ' in command:
     cycles.append(command)
     db['cycle.json'] = json.dumps(dict(version=1, process_cycle_verified=True, functional_maps_verified=False, signals_to_nav=False, stage='new_process', old_pid=11, new_pid=21, new_start=200, last_exit_raw=0)).encode() if mode != 'failure' else b''
     db['cycle-errors.txt'] = b'' if mode != 'failure' else b'refused'
     if mode == 'disconnect':
      self.broken = True
      raise EOFError('command connection lost')
     return 0 if mode != 'failure' else 3
    if ' > ' in command:
     action, out = command.split(' > ', 1)
     name = out.split()[0]
     if action == 'pidin arguments':
      db[name] = after if cycles and mode != 'failure' else before
     elif './nav_cycle inspect ' in action:
      db[name] = json.dumps(newident if action.endswith('21') else ident).encode()
     elif action.startswith('cp '):
      db[action.split()[-1]] = b'ring'
      db[name] = b''
     else:
      db[name] = b''
    return 0
  with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'ROOT', Path(tmp)), patch.object(m, 'REFERENCES', {k:(len(v),m.sha(v)) for k,v in refs.items()}), patch.object(m,'package',return_value=helper), patch.object(m.ftplib,'FTP',FTP), patch.object(m,'Shell',Shell), patch.object(m.time,'sleep'), patch('builtins.input',return_value=visual), contextlib.redirect_stdout(io.StringIO()):
   rc = m.main(['--run','--phone-unplugged','--factory-maps-working'])
   folder = next((Path(tmp)/'delphi-dump').iterdir())
   s = json.loads((folder/'nav-graceful-summary.json').read_text())
   for record in s['artifacts']:
    data = (folder/record['file']).read_bytes()
    self.assertEqual(len(data), record['bytes'])
    self.assertEqual(m.sha(data), record['sha256'])
   return rc, s, commands, cycles

 def test_success_is_one_clean_cycle_and_visual_report(self):
  rc, summary, commands, cycles = self.exercise()
  self.assertEqual(rc, 0)
  self.assertTrue(summary['process_cycle_verified'])
  self.assertTrue(summary['functional_maps_verified'])
  self.assertEqual(len(cycles), 1)
  self.assertFalse(any('kill' in c or 'nav_launch' in c or 'isoTX' in c for c in commands))
  self.assertTrue(any('/dev/shmem/DTS_Shm_1' in c for c in commands))

 def test_firmware_mismatch_never_controls(self):
  rc, summary, commands, cycles = self.exercise('profile')
  self.assertEqual(rc, 2)
  self.assertEqual(commands, [])
  self.assertEqual(cycles, [])
  self.assertEqual(summary['control_attempts'], 0)

 def test_refusal_retains_empty_artifacts_and_never_retries(self):
  rc, summary, commands, cycles = self.exercise('failure')
  self.assertEqual(rc, 2)
  self.assertEqual(len(cycles), 1)
  self.assertFalse(summary['process_cycle_verified'])
  self.assertFalse(summary['functional_maps_verified'])
  self.assertTrue(any(a['file']=='cycle.json' and a['bytes']==0 for a in summary['artifacts']))
  self.assertTrue(any(c.startswith('sloginfo -t') for c in commands))

 def test_new_process_does_not_certify_visible_maps(self):
  rc, summary, _, cycles = self.exercise(visual='no')
  self.assertEqual(rc, 2)
  self.assertTrue(summary['process_cycle_verified'])
  self.assertFalse(summary['functional_maps_verified'])
  self.assertEqual(len(cycles), 1)

 def test_command_disconnect_still_fetches_results_without_retry(self):
  rc, summary, commands, cycles = self.exercise('disconnect')
  self.assertEqual(rc, 2)
  self.assertEqual(len(cycles), 1)
  self.assertFalse(summary['process_cycle_verified'])
  self.assertTrue(any(a['file']=='cycle.json' and a['bytes']>0 for a in summary['artifacts']))
  self.assertTrue(any(a['file']=='cycle-errors.txt' and a['bytes']==0 for a in summary['artifacts']))
  self.assertFalse(any(c.startswith('sloginfo -t') for c in commands[commands.index(cycles[0])+1:]))

 def test_peer_restart_and_wrong_manager_fail_assessment(self):
  before = {'NavigationServer':11, 'Most':12}
  after = {'NavigationServer':21, 'Most':12}
  ident = dict(start_time=100, manager_pid=1, manager_start=50)
  new = dict(start_time=200, manager_pid=1, manager_start=50)
  v = dict(version=1, process_cycle_verified=True, functional_maps_verified=False, signals_to_nav=False, stage='new_process', last_exit_raw=0, old_pid=11, new_pid=21, new_start=200)
  m.assess_cycle(v,before,after,ident,new)
  for altered_after, altered_new in ((dict(after, Most=13),new),(after,dict(new,manager_start=51))):
   with self.assertRaises(ValueError):
    m.assess_cycle(v,before,altered_after,ident,altered_new)

if __name__ == '__main__':
 unittest.main()
