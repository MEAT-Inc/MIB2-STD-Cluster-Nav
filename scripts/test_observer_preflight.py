"""Offline preflight regressions. No vehicle or network connection is made."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch
import collect_observer_preflight as p

ROOT = Path(__file__).resolve().parents[1]
TOOLS = (ROOT / '.tools').resolve()
ARGS = b' 684110 /extbin/apps/bin/AndroidAuto -t\r\n'
MAPS = b'             bautoreceiver.so.1 @78100000 1112K 28K\r\n'

class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        TOOLS.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='preflight-tests-', dir=TOOLS)
        self.root = Path(self.temp.name).resolve()
        self.addCleanup(self.cleanup)
    def cleanup(self):
        # Verify the exact absolute target before TemporaryDirectory removes it.
        if self.root.parent != TOOLS or not self.root.name.startswith('preflight-tests-'):
            raise RuntimeError('Unexpected test workspace')
        self.temp.cleanup()

class ParserTests(unittest.TestCase):
    def test_actual_name_and_truncated_mapping(self):
        self.assertTrue(p.has_android_process(ARGS))
        self.assertTrue(p.receiver_mapping(MAPS)['name_truncated'])
        self.assertEqual(p.receiver_mapping(MAPS)['mapping_start'], '0x78100000')
    def test_unrelated_arguments_are_not_a_process_match(self):
        for data in (b'pidin -p AndroidAuto arguments\n',
                     b' 12 pidin -p AndroidAuto arguments\n',
                     b' 12 OtherProcess --watch AndroidAuto\n',
                     b' 12 AndroidAutoServices -t\n'):
            self.assertFalse(p.has_android_process(data), data)
    def test_ambiguous_and_short_library_names_are_rejected(self):
        self.assertIsNone(p.receiver_mapping(b'so.1 @78100000\n'))
        self.assertIsNone(p.receiver_mapping(b'fakeautoreceiver.so.1 @78100000\n'))
        self.assertIsNone(p.receiver_mapping(MAPS + MAPS))
        self.assertIsNotNone(p.receiver_mapping(b'libautoreceiver.so.1 @78100000\n'))

class MainTests(WorkspaceTest):
    def manifest(self):
        file = self.root / 'native/observer/release/manifest.json'
        file.parent.mkdir(parents=True)
        file.write_text(json.dumps({'expected_target_sha256': {
            'AndroidAuto': 'a'*64, 'libautoreceiver.so': 'b'*64}}))
    def run_main(self, argv, failed_telnet=False, mismatch=False):
        def inventory(a, run, commands):
            if failed_telnet: return [{'stage':'telnet', 'error':'offline timeout'}], {}
            return ([{'command':cmd,'file':name+'.txt','exit_code':0} for name,cmd in commands],
                    {'android-arguments': ARGS, 'android-maps': MAPS})
        def download(a, password, remote, run, expected):
            return {'remote':remote, 'expected_sha256':expected,
                    'matches_expected': not (mismatch and remote.endswith('/AndroidAuto'))}
        with patch.object(p, '__file__', str(self.root/'scripts/collect_observer_preflight.py')), \
             patch.object(p, 'inventory', side_effect=inventory) as inv, \
             patch.object(p, 'download', side_effect=download) as down, \
             patch.object(p.getpass, 'getpass') as password, \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = p.main(argv)
        report = json.loads(next((self.root/'delphi-dump').glob('*/preflight-summary.json')).read_text())
        return code, report, inv, down, password
    def test_supervisor_needs_no_manifest_or_ftp_or_ftp_password(self):
        code, report, inv, down, password = self.run_main(['--supervisor-only', '--ask-password'])
        self.assertEqual(code, 0)
        self.assertEqual(len(inv.call_args.args[2]), 7)
        down.assert_not_called(); password.assert_not_called()
        self.assertEqual(report['files'], [])
        self.assertFalse(report['fresh_hashes_verified'])
        self.assertEqual(report['mode'], 'supervisor')
    def test_default_includes_supervisor_and_three_fresh_files(self):
        self.manifest()
        code, report, inv, down, _ = self.run_main([])
        self.assertEqual(code, 0)
        self.assertEqual(len(inv.call_args.args[2]), 14)
        self.assertIn(('procman-core','cat /etc/procman_core.cfg'), inv.call_args.args[2])
        self.assertEqual(down.call_count, 3)
        self.assertTrue(report['fresh_hashes_verified'])
        self.assertTrue(report['supervisor_capture_included'])
    def test_full_mode_missing_manifest_stops_before_network(self):
        with patch.object(p, '__file__', str(self.root/'scripts/collect_observer_preflight.py')), \
             patch.object(p, 'inventory') as inv, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught: p.main([])
        self.assertEqual(caught.exception.code, 2)
        inv.assert_not_called()
        self.assertFalse((self.root/'delphi-dump').exists())
    def test_hash_mismatch_is_incomplete(self):
        self.manifest()
        code, report, _, _, _ = self.run_main([], mismatch=True)
        self.assertEqual(code, 1)
        self.assertFalse(report['ready_for_review'])
    def test_telnet_failure_preserves_independent_ftp_collection(self):
        self.manifest()
        code, report, _, down, _ = self.run_main([], failed_telnet=True)
        self.assertEqual(code, 1)
        self.assertEqual(down.call_count, 3)
        self.assertTrue(report['fresh_hashes_verified'])
        self.assertFalse(report['all_commands_ok'])

class FakeSocket:
    def __init__(self, chunks): self.chunks=list(chunks); self.sent=[]; self.closed=False
    def __enter__(self): return self
    def __exit__(self,*args): self.closed=True
    def settimeout(self,value): pass
    def sendall(self,value): self.sent.append(value)
    def recv(self,limit):
        if not self.chunks: raise TimeoutError('offline timeout')
        return self.chunks.pop(0)

class TelnetTests(WorkspaceTest):
    def run_inventory(self, chunks, commands=(('system','uname -a'),)):
        sock=FakeSocket(chunks)
        a=SimpleNamespace(host='test',telnet_port=23,timeout=1,telnet_user='root')
        with patch.object(p.socket,'create_connection',return_value=sock), \
             patch.object(p.uuid,'uuid4',return_value=SimpleNamespace(hex='a'*32)), \
             contextlib.redirect_stdout(io.StringIO()):
            rows,responses=p.inventory(a,self.root,commands)
        return sock,rows,responses
    def test_echo_fragmentation_and_utf8_boundary(self):
        sock,rows,_=self.run_inventory([b'# ', b'uname -a; echo OPaaaaaaaaaaaa:$?:END\r\n',
            b'caf\xc3', b'\xa9\r\x00OPaaaa', b'aaaaaaaa:0:END\r\n# '])
        self.assertEqual(rows[0]['exit_code'],0)
        self.assertIn('caf'+chr(233),(self.root/'system.txt').read_text(encoding='utf-8'))
        self.assertEqual(len(sock.sent),1)
    def test_partial_timeout_closes_and_never_sends_next_command(self):
        sock,rows,_=self.run_inventory([b'# ', b'partial response'],
            (('system','uname -a'),('kernel','pidin info')))
        self.assertTrue(sock.closed)
        self.assertEqual(len(sock.sent),1)
        self.assertEqual(rows[-1]['stage'],'telnet')
        self.assertIn('partial response',(self.root/'system.txt').read_text())
    def test_authentication_is_not_in_transcript(self):
        with patch.object(p.getpass,'getpass',return_value='secret'):
            sock,rows,_=self.run_inventory([b'login: ',b'Password: ',b'# ',b'OPaaaaaaaaaaaa:0:END\n'])
        self.assertIn(b'secret\r\n',sock.sent)
        self.assertNotIn('secret',(self.root/'system.txt').read_text())
        self.assertEqual(rows[0]['exit_code'],0)
    def test_nonzero_remote_exit_is_recorded(self):
        _,rows,_=self.run_inventory([b'# ',b'OPaaaaaaaaaaaa:1:END\n'])
        self.assertEqual(rows[0]['exit_code'],1)

class DownloadTests(WorkspaceTest):
    def run_download(self, payload=b'fresh payload', fail_first=False):
        instances=[]
        class FTP:
            def __init__(self, **kw): self.index=len(instances); self.commands=[]; instances.append(self)
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def connect(self,*args): pass
            def login(self,*args): pass
            def voidcmd(self,cmd): self.commands.append(cmd)
            def retrbinary(self,cmd,callback):
                self.commands.append(cmd)
                if fail_first and self.index==0:
                    callback(b'old partial'); raise EOFError('offline drop')
                if payload: callback(payload)
        a=SimpleNamespace(timeout=1,host='test',port=21,username='test')
        with patch.object(p.ftplib,'FTP',FTP):
            row=p.download(a,'secret','/extbin/apps/bin/AndroidAuto',self.root,hashlib.sha256(payload).hexdigest())
        return row,instances
    def test_retry_is_fresh_and_binary_hash_is_checked(self):
        row,instances=self.run_download(fail_first=True)
        self.assertEqual(len(instances),2)
        self.assertEqual((self.root/'extbin/apps/bin/AndroidAuto').read_bytes(),b'fresh payload')
        self.assertTrue(row['matches_expected'])
        self.assertTrue(all(i.commands==['TYPE I','RETR /extbin/apps/bin/AndroidAuto'] for i in instances))
    def test_zero_bytes_never_passes(self):
        row,_=self.run_download(payload=b'')
        self.assertFalse(row['matches_expected'])
        self.assertFalse((self.root/'extbin/apps/bin/AndroidAuto').exists())
    def test_existing_file_is_not_overwritten(self):
        target=self.root/'extbin/apps/bin/AndroidAuto'
        target.parent.mkdir(parents=True); target.write_bytes(b'existing')
        row,instances=self.run_download()
        self.assertEqual(instances,[])
        self.assertFalse(row['matches_expected'])
        self.assertEqual(target.read_bytes(),b'existing')

if __name__=='__main__': unittest.main()
