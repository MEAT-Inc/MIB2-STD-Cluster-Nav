from pathlib import Path
import sys,json,struct,tempfile,unittest,contextlib,io
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import collect_replay_wait as m

class Tests(unittest.TestCase):
 def session(self,root,name='_cluster_replay_20261104_190458_test',pending=False):
  p=root/'delphi-dump'/name;p.mkdir(parents=True)
  remote='/ramdisk/delphi-nav-bridge_'+'a'*32
  b=bytearray(512);struct.pack_into('<3I',b,0,0x314e4c44,1,512);struct.pack_into('<I',b,40,123);struct.pack_into('<I',b,52,456);struct.pack_into('<4Q',b,64,10,20,30,0);b[96:96+len(remote)]=remote.encode()
  manifest=json.dumps(dict(files=dict(nav_launch=dict(sha256='b'*64),nav_cycle=dict(sha256='c'*64)))).encode()
  file='controller-pending.bin' if pending else 'controller.bin'
  (p/file).write_bytes(b);(p/'release-manifest.json').write_bytes(manifest)
  summary=dict(remote=remote,controller_sha256='b'*64,release_manifest_sha256=m.sha(manifest),artifacts=[dict(file=file,bytes=len(b),sha256=m.sha(b))])
  (p/'replay-summary.json').write_text(json.dumps(summary))
  return p
 def test_missing_pin_uses_latest_verified_collection(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.session(root,'_cluster_replay_20261103_old');latest=self.session(root)
   pin,source=m.load_pin(root);self.assertEqual(source,str(latest));self.assertEqual((pin['pid'],pin['start_time'],pin['manager_pid'],pin['manager_start']),(123,30,456,20))
 def test_explicit_session_and_pending_controller(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);chosen=self.session(root,pending=True)
   self.assertEqual(m.load_pin(root,chosen)[0]['helper_sha256'],'c'*64)
 def test_existing_pin_takes_precedence(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);session=self.session(root);pin,_=m.load_pin(root,session);pin['pid']=789
   (root/'replay-wait-pin.json').write_text(json.dumps(pin))
   self.assertEqual(m.load_pin(root)[0]['pid'],789)
 def test_invalid_latest_does_not_silently_use_older_collection(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);self.session(root,'_cluster_replay_20261103_old');p=self.session(root)
   (p/'controller.bin').write_bytes(bytes(512))
   with self.assertRaisesRegex(ValueError,'artifact hash'):m.load_pin(root)
 def test_manifest_tampering_refused(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);p=self.session(root);(p/'release-manifest.json').write_text('{}')
   with self.assertRaisesRegex(ValueError,'manifest hash'):m.load_pin(root)
 def test_no_sources_gives_actionable_error(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(ValueError,'--session'):m.load_pin(Path(d))
 def test_invalid_pin_namespace_refused(self):
  with self.assertRaises(ValueError):m.validate_pin(dict(remote='/tmp/anything'))
 def test_plan_needs_no_pin_or_network(self):
  with tempfile.TemporaryDirectory() as d,patch.object(m,'ROOT',Path(d)),patch.object(m.ftplib,'FTP') as ftp,patch.object(m,'Shell') as shell,contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(m.main([]),0);ftp.assert_not_called();shell.assert_not_called();self.assertFalse((Path(d)/'delphi-dump').exists())

if __name__=='__main__':unittest.main()
