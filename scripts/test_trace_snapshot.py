import contextlib,ftplib,io,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import collect_trace_snapshot as m
class TraceTests(unittest.TestCase):
 def test_plan_no_network_or_dump(self):
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory') as inv,patch.object(m.ftplib,'FTP') as ftp,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main([]),0);inv.assert_not_called();ftp.assert_not_called();self.assertFalse((Path(t)/'delphi-dump').exists())
 def test_config_paths(self):
  self.assertEqual(m.config_from_environment(b' TRACE_CONFIG_PATH=/etc/dts/\r\n'),'/etc/dts/trace_config.json')
  self.assertEqual(m.config_from_environment(b'TRACE_CONFIG_PATH=/etc/trace_config.json'),'/etc/trace_config.json')
  for value in (b'/dev/ser3',b'/etc/../dev/ser3',b'/etc/a;kill',b'relative'):
   self.assertIsNone(m.config_from_environment(b'TRACE_CONFIG_PATH='+value))
  self.assertIsNone(m.config_from_environment(b'TRACE_CONFIG_PATH=/etc/a TRACE_CONFIG_PATH=/etc/b'))
 def test_transfer_limit_and_no_device_reads(self):
  a=SimpleNamespace(timeout=1,host='unit',port=21,username='ftpuser')
  class FTP:
   def __init__(self,**kw):pass
   def __enter__(self):return self
   def __exit__(self,*args):pass
   def connect(self,*args):pass
   def login(self,*args):pass
   def voidcmd(self,*args):pass
   def retrbinary(self,cmd,save):save(b'1234');save(b'5')
  with patch.object(m.ftplib,'FTP',FTP):
   with self.assertRaises(ValueError):m.fetch(a,'x',m.MEMORY[0],4)
   self.assertEqual(m.fetch(a,'x',m.MEMORY[0],5),b'12345')
   for remote in ('/dev/ser3','/dev/DbTrace','/proc/1/as'):
    with self.assertRaises(ValueError):m.fetch(a,'x',remote,5)
 def test_partial_copy_retains_evidence(self):
  def fetch(a,p,remote,limit):
   if remote==m.MEMORY[1]:raise ftplib.error_perm('550')
   return b'config' if remote.endswith('.json') else b'data'
  with tempfile.TemporaryDirectory() as t,patch.object(m,'ROOT',Path(t)),patch.object(m,'inventory',return_value=([dict(command=c,exit_code=0) for n,c in m.COMMANDS],{})),patch.object(m,'fetch',side_effect=fetch),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main(['--run']),2)
   r=json.loads(next(Path(t).glob('delphi-dump/*/trace-summary.json')).read_text());self.assertEqual(r['dts_objects_copied'],3);self.assertFalse(r['atomic_snapshot']);self.assertFalse(r['display_recovery_verified'])
 def test_commands_only_read_inventory(self):
  for n,c in m.COMMANDS:self.assertTrue(c.startswith(('pidin ','ls ')));self.assertFalse(any(x in c for x in (';','>','kill','reboot')))
if __name__=='__main__':unittest.main()
