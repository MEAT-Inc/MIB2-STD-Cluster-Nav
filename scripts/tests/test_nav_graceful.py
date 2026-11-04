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

 def test_held_cycle_cannot_connect_or_upload(self):
  with patch.object(m.ftplib,'FTP') as ftp, patch.object(m,'Shell') as shell, patch.object(m,'package') as package, contextlib.redirect_stderr(io.StringIO()):
   with self.assertRaises(SystemExit):
    m.main(['--run','--phone-unplugged','--factory-maps-working'])
  ftp.assert_not_called()
  shell.assert_not_called()
  package.assert_not_called()

 def exercise(self, mode='good', visual='yes',diagnostic=False,recovery=False):
  commands, db, cycles = [], {}, []
  ident = dict(version=1, readonly=True, pid=11, start_time=100, manager_pid=1, manager_start=50, app_id=29, state=3)
  newident = dict(ident, pid=21, start_time=200)
  before = b'11 NavigationServer\n12 Most\n13 TransportServer\n14 DisplayManagement\n15 screen-cda\n16 NavServices\n'
  after = before.replace(b'11 NavigationServer', b'21 NavigationServer')
  helper = b'helper'
  refs = {'/extbin/apps/bin/NavigationServer': b'nav', '/proc/boot/procman': b'pm', '/proc/boot/libXSAL.so': b'sal', '/proc/boot/libc.so.3': b'libc'}
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
     raise AssertionError('FTP must never read QNX image files directly: '+path)
    save(db[path.rsplit('/', 1)[-1]])
  class Shell:
   broken = False
   def __init__(self, *args): self.actions = []
   def close(self): pass
   def command(self, command, required=True):
    commands.append(command)
    self.actions.append(dict(command=command, exit_code=0))
    if './nav_cycle cycle ' in command or './nav_cycle recover ' in command:
     cycles.append(command)
     db['cycle.json'] = json.dumps(dict(version=1, process_cycle_verified=True, functional_maps_verified=False, signals_to_nav=recovery, termination_signal=9 if recovery else 0, stage='recover_restart' if recovery else 'new_process', old_pid=11, new_pid=21, new_start=200, last_exit_raw=9 if recovery else 0)).encode() if mode != 'failure' else b''
     db['cycle-errors.txt'] = b'' if mode != 'failure' else b'refused'
     if mode=='recover_refused':
      db['cycle.json']=json.dumps(dict(version=1,process_cycle_verified=False,functional_maps_verified=False,signals_to_nav=False,termination_signal=0,stage='recover_guard',old_pid=11,new_pid=0,new_start=0,last_exit_raw=0)).encode()
      return 3
     if mode == 'disconnect':
      self.broken = True
      raise EOFError('command connection lost')
     return 0 if mode != 'failure' else 3
    if ' > ' in command:
     action, out = command.split(' > ', 1)
     name = out.split()[0]
     if action == 'pidin arguments':
      db[name] = after if cycles and mode not in ('failure','recover_refused') else before
     elif './nav_cycle inspect ' in action:
      db[name] = json.dumps(newident if action.endswith('21') else ident).encode()
     elif action.startswith('cp '):
      source, destination = action.split()[1:]
      db[name] = b''
      if source in refs:
       if mode == 'copy_failure' and source.endswith('/procman'):
        db[name] = b'cp: permission denied'
        return 1
       db[destination] = b'px' if mode=='profile' and source.endswith('/procman') else refs[source]
      else:
       db[destination] = b'ring'
     elif action.endswith(' regs'):
      pid=int(action.split()[2]);lines=[str(pid)+' 2 NavigationServer',' sp:0007eaa4 lr:01028088 pc:01038714',str(pid)+' 11 NavigationServer',' sp:00fcce1c lr:01028088 pc:01038714']
      db[name]=chr(10).join(lines).encode()
     elif action.endswith(' mem'):
      db[name]=b' libc.so.3 @ 1000000'
     elif './nav_cycle page ' in action:
      db[name]=bytes(4095 if mode=='short_page' else 4096)
      db[out.split('2>',1)[1].strip()]=b''
     else:
      db[name] = b''
    return 0
  with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'CYCLE_HELD', diagnostic or recovery), patch.object(m, 'ROOT', Path(tmp)), patch.object(m, 'REFERENCES', {k:(len(v),m.sha(v)) for k,v in refs.items()}), patch.object(m,'package',return_value=helper), patch.object(m.ftplib,'FTP',FTP), patch.object(m,'Shell',Shell), patch.object(m.time,'sleep'), patch('builtins.input',return_value=visual), contextlib.redirect_stdout(io.StringIO()):
   if recovery:
    release=Path(tmp)/'native/cluster-bridge/nav-control/recovery-release';release.mkdir(parents=True)
    pinned=dict(ident,start_time=101) if mode=='wrong_pin' else ident
    (release/'manifest.json').write_text(json.dumps(dict(recovery_identity=pinned)))
   rc = m.main(['--run','--phone-unplugged']+(['--recover-stalled'] if recovery else ['--factory-maps-working'])+(['--diagnose-shutdown'] if diagnostic else []))
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
  self.assertEqual(len(summary['reference_checks']), 4)
  self.assertTrue(all(v['matched'] for v in summary['reference_checks']))
  self.assertEqual(summary['preflight_revision'], 2)
  self.assertFalse(any('kill' in c or 'nav_launch' in c or 'isoTX' in c for c in commands))
  self.assertTrue(any('/dev/shmem/DTS_Shm_1' in c for c in commands))

 def test_firmware_mismatch_never_controls(self):
  rc, summary, commands, cycles = self.exercise('profile')
  self.assertEqual(rc, 2)
  self.assertTrue(any(c.startswith('cp /proc/boot/procman ') for c in commands))
  self.assertFalse(any('./nav_cycle' in c for c in commands))
  self.assertNotIn('helper_upload_verified', summary)
  self.assertEqual(cycles, [])
  self.assertEqual(summary['control_attempts'], 0)
  check = summary['reference_checks'][-1]
  self.assertEqual(check['source'], '/proc/boot/procman')
  self.assertEqual(check['actual_bytes'], check['expected_bytes'])
  self.assertNotEqual(check['actual_sha256'], check['expected_sha256'])
  self.assertFalse(check['matched'])
  self.assertTrue(any(a['file']=='procman.reference' for a in summary['artifacts']))
  self.assertIn('actual bytes=', summary['errors'][0]['error'])

 def test_reference_copy_failure_keeps_log_and_never_uploads_helper(self):
  rc, summary, commands, cycles = self.exercise('copy_failure')
  self.assertEqual(rc, 2)
  self.assertEqual(cycles, [])
  self.assertNotIn('helper_upload_verified', summary)
  self.assertEqual(summary['reference_checks'][-1]['copy_exit_code'], 1)
  self.assertTrue(any(a['file']=='procman.reference.copy.txt' and a['bytes']>0 for a in summary['artifacts']))
  self.assertFalse(any('./nav_cycle' in c for c in commands))

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

 def test_diagnostic_stall_captures_nine_pages_without_retry(self):
  rc, summary, commands, cycles=self.exercise('failure',diagnostic=True)
  self.assertEqual(rc,0)
  self.assertTrue(summary['diagnostics_complete'])
  self.assertEqual(summary['helper_exit_code'],3)
  self.assertEqual(len(summary['raw_pages']),9)
  self.assertFalse(summary['process_cycle_verified'])
  self.assertFalse(summary['functional_maps_verified'])
  self.assertEqual(len(cycles),1)
  self.assertEqual(sum('./nav_cycle page ' in c for c in commands),9)
  self.assertFalse(any('kill' in c or 'dd if=' in c for c in commands))

 def test_bad_or_partial_baseline_never_requests_shutdown(self):
  rc, summary, commands, cycles=self.exercise('short_page',diagnostic=True)
  self.assertEqual(rc,2)
  self.assertEqual(cycles,[])
  self.assertEqual(summary['control_attempts'],0)
  self.assertFalse(summary['diagnostics_complete'])
  self.assertTrue(any('Incomplete raw page' in e['error'] for e in summary['errors']))

 def test_allocator_page_parser_bounds(self):
  from collect_map_session import raw_stack_pages,libc_mapping
  lines=['11 2 NavigationServer',' sp:0007eaa4 pc:01038714','11 11 NavigationServer',' sp:00fcce1c pc:01038714']
  data=chr(10).join(lines).encode()
  self.assertEqual(raw_stack_pages(data,11),[(2,0x7eaa4,0x7e000),(11,0xfcce1c,0xfcc000)])
  self.assertEqual(libc_mapping(b' libc.so.3 @ 1000000'),0x1000000)
  for altered in (data.replace(b'0007eaa4',b'ffffeaa4'),data.replace(b'0007eaa4',b'0007eaa5'),data+chr(10).encode()+data):
   with self.assertRaises(ValueError):raw_stack_pages(altered,11)
  with self.assertRaises(ValueError):raw_stack_pages(data,99)
  with self.assertRaises(ValueError):libc_mapping(b' libc.so.3 @ 1000000'+chr(10).encode()+b' libc.so.3 @ 2000000')

 def test_pinned_recovery_is_one_action_then_maps_observation(self):
  rc,summary,commands,cycles=self.exercise(recovery=True)
  self.assertEqual(rc,0)
  self.assertEqual(len(cycles),1)
  self.assertIn('./nav_cycle recover ',cycles[0])
  self.assertFalse(any('./nav_cycle cycle ' in c for c in commands))
  self.assertTrue(summary['process_cycle_verified'])
  self.assertTrue(summary['functional_maps_verified'])
  self.assertTrue(summary['signals_to_nav'])
  self.assertEqual(summary['termination_signal'],9)

 def test_recovery_pin_mismatch_never_requests_action(self):
  rc,summary,commands,cycles=self.exercise('wrong_pin',recovery=True)
  self.assertEqual(rc,2)
  self.assertEqual(cycles,[])
  self.assertEqual(summary['control_attempts'],0)

 def test_native_crash_guard_refusal_never_retries(self):
  rc,summary,commands,cycles=self.exercise('recover_refused',recovery=True)
  self.assertEqual(rc,2)
  self.assertEqual(len(cycles),1)
  self.assertFalse(summary['signals_to_nav'])
  self.assertFalse(summary['process_cycle_verified'])

 def test_y_confirms_sequential_map_recovery(self):
  rc,summary,commands,cycles=self.exercise(visual=' Y ',recovery=True)
  self.assertEqual(rc,0)
  self.assertTrue(summary['process_cycle_verified'])
  self.assertTrue(summary['functional_maps_verified'])
  self.assertEqual(summary['user_reported_final_maps'],'yes')
  self.assertEqual(summary['map_confirmation_mode'],'sequential_location_toggle')
  self.assertFalse(summary['simultaneous_maps_required'])

 def test_n_is_recorded_as_explicit_no(self):
  rc,summary,commands,cycles=self.exercise(visual='N',recovery=True)
  self.assertEqual(rc,2)
  self.assertTrue(summary['process_cycle_verified'])
  self.assertFalse(summary['functional_maps_verified'])
  self.assertEqual(summary['user_reported_final_maps'],'no')

 def test_confirmation_normalizes_case_and_keeps_uncertainty(self):
  for value in ('yes','YES',' y ','Y'):self.assertEqual(m.map_confirmation(value),'yes')
  for value in ('no','NO',' n ','N'):self.assertEqual(m.map_confirmation(value),'no')
  for value in ('','unsure','maybe'):self.assertEqual(m.map_confirmation(value),'unsure')

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
