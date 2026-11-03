from project_console import console_session
import contextlib,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import collect_map_session as m
class Tests(unittest.TestCase):
 def test_plan_has_no_connection_or_output(self):
  with patch.object(m.ftplib,'FTP') as ftp,patch.object(m,'Shell') as shell,contextlib.redirect_stdout(io.StringIO()):self.assertEqual(m.main([]),0)
  ftp.assert_not_called();shell.assert_not_called()
 def test_ambiguous_or_invalid_pid_rejected(self):
  for b in (b'1 NavigationServer\n2 NavigationServer\n',b'0 Most\n'):
   with self.assertRaises(ValueError):m.processes(b)
 def test_readonly_capture_empty_log_hashes_and_state_label(self):
  db={};commands=[];inventory=b'11 NavigationServer -fcfg cfg\n12 Most\n13 TransportServer\n14 DisplayManagement\n15 screen-cda\n'
  class Shell:
   def __init__(self,*args):self.actions=[]
   def close(self):pass
   def command(self,c,required=True):
    commands.append(c);self.actions.append(dict(command=c,exit_code=0))
    if ' > ' in c:
     cmd,out=c.split(' > ',1);name=out.split()[0];db[name]=inventory if cmd=='pidin arguments' else b'' if cmd.startswith('sloginfo') else (cmd+' snapshot').encode()
    return 0
  class FTP:
   def __init__(self,**kw):pass
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def connect(self,*args):pass
   def login(self,*args):pass
   def voidcmd(self,*args):pass
   def retrbinary(self,c,save):save(db[c.rsplit('/',1)[-1]])
  with tempfile.TemporaryDirectory() as tmp,patch.object(m,'ROOT',Path(tmp)),patch.object(m,'Shell',Shell),patch.object(m.ftplib,'FTP',FTP),patch.object(m.time,'sleep'),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main(['--run','--state','broken']),0);folder=next((Path(tmp)/'delphi-dump').iterdir());s=json.loads((folder/'map-session-summary.json').read_text());self.assertTrue(s['same_process_ids']);self.assertTrue(s['collection_complete']);self.assertEqual(s['user_reported_state'],'broken');self.assertEqual(len(s['artifacts']),44)
   for x in s['artifacts']:
    b=(folder/x['file']).read_bytes();self.assertEqual(len(b),x['bytes']);self.assertEqual(m.hashlib.sha256(b).hexdigest(),x['sha256'])
   self.assertEqual((folder/'system-log.txt').read_bytes(),b'')
  self.assertTrue(all(c.startswith(('mkdir /ramdisk/delphi-map-state_','cd /ramdisk/delphi-map-state_','chmod 644 ','pidin ','sloginfo -t ','ls -lt /sdc1/coredumps')) for c in commands));self.assertFalse(any(x in c for c in commands for x in ('kill','nav_launch','LD_PRELOAD','/spawn/isoTX')))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
