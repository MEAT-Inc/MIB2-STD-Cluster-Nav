"""Regression coverage for Telnet marker handling; no vehicle connection."""
import io,re,unittest
from types import SimpleNamespace
from unittest.mock import patch
import delphi_inventory as d
from collect_delphi_runtime import StagingSession,completion_command,target_availability,main

class FakeSocket:
    def __init__(self,chunks):self.chunks=list(chunks);self.sent=[]
    def recv(self,_):return self.chunks.pop(0) if self.chunks else b''
    def sendall(self,data):self.sent.append(data)
    def settimeout(self,_):pass
class TelnetTests(unittest.TestCase):
    def session(self,chunks):
        sock=FakeSocket(chunks);logs=[]
        c=SimpleNamespace(log=logs.append)
        s=StagingSession(c);s.sock=sock;s.reader=d.TelnetReader(sock,1);s.transcript=io.StringIO()
        return s,sock,logs
    def test_echo_is_not_completion(self):
        command=completion_command('mkdir /ramdisk/example','DS12345678')
        self.assertNotRegex(command,re.compile(r'DS12345678:([0-9]+):END'))
    def test_normal_and_nvt_line_endings(self):
        for ending in (b'\r\n',b'\r\x00\n',b'\r\r\n',b'\n'):
            with self.subTest(ending=ending),patch('collect_delphi_runtime.uuid.uuid4',return_value=SimpleNamespace(hex='12345678'+'a'*24)):
                s,sock,logs=self.session([b'echo DS12345678:$?:END'+ending,b'DS1234',b'5678:0:END'+ending+b'# '])
                s.run('mkdir /ramdisk/example')
                self.assertIn('exit 0',logs[-1]);self.assertIn('RECV',s.transcript.getvalue())
    def test_nonzero_status_detected(self):
        with patch('collect_delphi_runtime.uuid.uuid4',return_value=SimpleNamespace(hex='12345678'+'a'*24)):
            s,_,_=self.session([b'DS12345678:1:END\r\n'])
            with self.assertRaisesRegex(OSError,'exit 1'):s.run('mkdir /ramdisk/example')
    def test_incomplete_reply_saved_before_failure(self):
        s,_,_=self.session([b'command output without completion\r\x00'])
        with self.assertRaisesRegex(OSError,'session stopped'):s.run('mkdir /ramdisk/example')
        self.assertIn('command output',s.transcript.getvalue())
        self.assertIn('COMMAND',s.transcript.getvalue())
    def test_telnet_negotiation_separate_from_completion(self):
        sock=FakeSocket([b'\xff\xfb\x01hello ',b'DS12345678:0:END\r\n']);reader=d.TelnetReader(sock,1);saved=[]
        label,data=reader.read_until([('done',re.compile(rb'DS12345678:([0-9]+):END'))],on_data=saved.append)
        self.assertEqual(label,'done');self.assertEqual(sock.sent,[b'\xff\xfe\x01'])
        self.assertEqual(b''.join(saved),data)
    def test_existing_reader_api_unchanged(self):
        reader=d.TelnetReader(FakeSocket([b'login: ']),1)
        self.assertEqual(reader.read_until([('login',re.compile(rb'login: $'))])[0],'login')
class CollectionRegressionTests(unittest.TestCase):
    def test_failed_staging_session_is_not_reused_and_ftp_continues(self):
        from unittest.mock import MagicMock
        collectors=[]
        class Collector:
            def __init__(self,args):
                self.a=args;self.records=[];self.run=MagicMock();collectors.append(self)
            def log(self,_):pass
            def clean(self,value):return str(value)
            def retry(self,_,action):return action()
            def listing(self,directory):
                if directory=='/proc/boot':return [('screen-cda','file',206772),('libXSAL.so','file',130364)]
                if directory=='/extbin/apps/usr/lib/graphics':return [('libscreen.so.1','file',110740)]
                return []
            def record(self,path,status,**extra):self.records.append({'remote_path':path,'status':status,**extra})
            def download(self,path,size):self.record(path,'downloaded',bytes=size)
            def finish(self,interrupted=False):return 2 if any(r['status']=='failed' for r in self.records) else 0
        stage=MagicMock();stage.root='/ramdisk/delphi-stage_'+'a'*32;stage.start.side_effect=TimeoutError('fake timeout')
        with patch('collect_delphi_runtime.d.Collector',Collector),patch('collect_delphi_runtime.StagingSession',return_value=stage):
            self.assertEqual(main(['--stage-boot-files']),2)
        stage.start.assert_called_once();stage.run.assert_not_called();stage.close.assert_called_once()
        records=collectors[0].records
        self.assertEqual(sum(r['status']=='failed' for r in records),2)
        self.assertTrue(any(r['status']=='downloaded' and r['remote_path'].endswith('libscreen.so.1') for r in records))
    def test_found_path_or_zero_byte_file_is_not_ready(self):
        transfers=[{'source_remote_path':'/proc/boot/screen-cda','ftp_remote_path':'/ramdisk/staged','expected_bytes':206772}]
        self.assertEqual(target_availability(transfers,[])['screen-cda'],'not_collected')
        self.assertEqual(target_availability(transfers,[{'remote_path':'/ramdisk/staged','status':'existing_not_downloaded','bytes':0}])['screen-cda'],'not_collected')
    def test_preexisting_nonempty_matching_size_file_is_available(self):
        transfers=[{'source_remote_path':'/extbin/apps/usr/lib/graphics/libscreen.so.1','ftp_remote_path':'/lib-copy','expected_bytes':110740}]
        result=target_availability(transfers,[{'remote_path':'/lib-copy','status':'existing_not_downloaded','bytes':110740}])
        self.assertEqual(result['libscreen.so.1'],'available_locally')
        self.assertEqual(result['screen-cda'],'not_collected')

if __name__=='__main__':unittest.main()

