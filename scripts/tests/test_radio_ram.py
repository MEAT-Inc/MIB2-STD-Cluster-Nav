"""Regression gates for full RAM disk and archived-file deletion boundaries."""
from pathlib import Path
import sys,unittest,json,hashlib,tempfile,types
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import radio_ram as m
class RamTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  p=Path(__file__).resolve().parents[2]/'delphi-dump/_disconnect_observer_20261110_140421_9fba06f2';s=json.loads((p/'disconnect-summary.json').read_text());cls.root=s['remote_directory'];cls.marker=(p/'controller.bin').read_bytes()
 def test_posix_free_space_and_echo(self):
  self.assertEqual(m.df_available(b'df -Pk /ramdisk; echo marker\r\nFilesystem 1024-blocks Used Available Capacity Mounted on\r\n/dev/ram0 65536 65536 0 100% /ramdisk\r\nmarker:0:END'),0)
  self.assertEqual(m.df_available(b'/dev/ram0 65536 1000 64536 2% /ramdisk\n'),64536*1024)
 def test_unknown_or_ambiguous_space_refused(self):
  for b in (b'',b'df: not found',b'/dev/ram0 1 0 1 0% /ramdisk\n/dev/ram1 1 0 1 0% /else'):
   with self.assertRaises(ValueError):m.df_available(b)
 def entry(self,data):
  return dict(root=self.root,marker=dict(name='controller.bin',bytes=512,sha256=hashlib.sha256(self.marker).hexdigest()),files=[dict(name='secondary.h264',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())])
 def test_namespace_and_traversal_refused(self):
  for key,value in (('root','/extbin/apps/bin'),('root',self.root+'/..')):
   e=self.entry(b'x');e[key]=value
   with self.assertRaises(ValueError):m.validate_entry(e)
  e=self.entry(b'x');e['files'][0]['name']='../NavigationServer'
  with self.assertRaises(ValueError):m.validate_entry(e)
 def run_case(self,wrong_file=False,wrong_marker=False,active=False,enough=False):
  entry=self.entry(b'archived content');state=dict(deleted=[]);owner=self
  class FTP:
   def __init__(self,**kw):pass
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def connect(self,*a):pass
   def login(self,*a):pass
   def voidcmd(self,*a):pass
   def size(self,path):return 512 if path.endswith('controller.bin') else len(b'archived content')
   def retrbinary(self,cmd,callback):callback((bytes(512) if wrong_marker else owner.marker) if cmd.endswith('controller.bin') else b'CORRUPT! content' if wrong_file else b'archived content')
   def delete(self,path):state['deleted'].append(path)
  class Shell:
   def command(self,c,required=True):
    if c.startswith('test !'):return int(active)
    free=40000 if enough or state['deleted'] else 0;self.last_response=('/dev/ram0 65536 65536 '+str(free)+' 100% /ramdisk\n').encode() if c.startswith('df ') else b'AndroidAuto NavigationServer';return 0
  a=types.SimpleNamespace(timeout=90,host='host',port=21,username='user')
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'plan.json';p.write_text(json.dumps(dict(entries=[entry])))
   with patch.object(m.ftplib,'FTP',FTP):
    try:state['report']=m.prepare_space(Shell(),a,'pw',p)
    except RuntimeError as e:state['error']=str(e)
  return state
 def test_only_matching_archived_file_deleted(self):
  s=self.run_case();self.assertEqual(s['deleted'],[self.root+'/secondary.h264']);self.assertGreaterEqual(s['report']['free_after'],m.MIN_FREE)
 def test_changed_data_preserved(self):self.assertFalse(self.run_case(wrong_file=True)['deleted'])
 def test_bad_restoration_marker_preserved(self):self.assertFalse(self.run_case(wrong_marker=True)['deleted'])
 def test_active_controller_blocks_deletion(self):
  s=self.run_case(active=True);self.assertFalse(s['deleted']);self.assertIn('active',s['error'])
 def test_enough_space_needs_no_deletion(self):self.assertFalse(self.run_case(enough=True)['deleted'])
if __name__=='__main__':
 from project_console import console_session
 with console_session(__file__,__doc__):unittest.main()
