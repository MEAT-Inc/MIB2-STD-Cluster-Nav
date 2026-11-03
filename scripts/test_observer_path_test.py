"""Offline smoke-runner checks: no vehicle/network access."""
from project_console import console_session
import contextlib,ftplib,io,json,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_observer_path_test as m
from run_observer_smoke import decode
TOOLS=(Path(__file__).resolve().parents[1]/'.tools').resolve()

def trace(pid=100):
    data=bytearray(128+1024*32)
    header=[decode.__globals__['MAGIC'],1,128,32,1024,4,pid,0x78000100,0x78000000,1,9,0,0,0]+[0]*18
    struct.pack_into('<32I',data,0,*header)
    for i in range(9): struct.pack_into('<8I',data,128+i*32,i+1,1,i+1,0x1000+i,0x2000+i,0x104abc,0,i+1)
    return bytes(data)

def native_report():
    words=[0x31545044,1,208,1,0,1,1,6,1,105,99,1,0,0,0,0]
    for i in range(6):words.extend([i+1,100+i if i!=1 else 200,99,int(i==1),9 if i==1 else 0,1])
    return struct.pack('<52I',*words)

def blobs():
    return {'stock-before.txt':b' 42 AndroidAuto -t\n','stock-after.txt':b' 42 AndroidAuto -t\n',
            'path-test.txt':('\n'.join(m.MARKERS)+'\n').encode(),
            'report.bin':native_report(),'observer.bin':trace(pid=200)}

class DataTests(unittest.TestCase):
    def test_success_and_changed_stock_rejected(self):
        self.assertTrue(m.assess(blobs())['stock_processes_unchanged'])
        data=blobs();data['stock-after.txt']=b' 43 AndroidAuto -t\n'
        with self.assertRaises(ValueError): m.assess(data)
    def test_wrong_trace_and_factory_pid_rejected(self):
        data=blobs();data['observer.bin']=trace(pid=42)
        with self.assertRaises(ValueError):m.assess(data)
        data=blobs();data['observer.bin']=b'truncated'
        with self.assertRaises(ValueError):m.assess(data)
    def test_accounted_log_drop_is_accepted_but_zero_capture_is_not(self):
        data=blobs();capture=bytearray(trace(pid=200))
        struct.pack_into('<II',capture,40,8,1)
        capture[128+8*32:128+9*32]=bytes(32)
        data['observer.bin']=bytes(capture)
        report=bytearray(native_report());struct.pack_into('<I',report,26*4,8);data['report.bin']=bytes(report)
        self.assertEqual(m.assess(data)['decoded_log']['count'],8)
        struct.pack_into('<II',capture,40,0,9)
        data['observer.bin']=bytes(capture)
        with self.assertRaises(ValueError):m.assess(data)
    def test_remote_namespace_is_exact(self):
        self.assertEqual(m.validate_remote(m.REMOTE_PREFIX+'a'*32),m.REMOTE_PREFIX+'a'*32)
        for value in ('/extbin/apps/lib','/ramdisk/other',m.REMOTE_PREFIX+'a'*32+'/../bad'):
            with self.assertRaises(ValueError):m.validate_remote(value)

class RunnerTests(unittest.TestCase):
    def setUp(self):
        TOOLS.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='path-tests-',dir=TOOLS)
        self.root=Path(self.temp.name).resolve();self.addCleanup(self.cleanup)
    def cleanup(self):
        if self.root.parent!=TOOLS or not self.root.name.startswith('path-tests-'):raise RuntimeError('Bad test path')
        self.temp.cleanup()
    def simulate(self,run=True,fail_cd=False,timeout=False,tamper=False,nonzero=False):
        state={'data':{},'commands':[],'shells':0}
        uploaded={name:('test '+name).encode() for name in m.NAMES}
        class FTP:
            def __init__(self,**kwargs): pass
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def connect(self,*args):pass
            def login(self,*args):pass
            def voidcmd(self,cmd):self.assert_binary=cmd
            def mkd(self,path):state['remote']=m.validate_remote(path)
            def storbinary(self,cmd,source):
                path=cmd[5:]
                if path.rsplit('/',1)[-1] not in m.NAMES:raise AssertionError('Bad upload')
                state['data'][path]=source.read()
            def retrbinary(self,cmd,save):
                path=cmd[5:]
                if path not in state['data']:raise ftplib.error_perm('550 missing')
                value=state['data'][path]
                save(value+b'bad' if tamper and path.endswith('/path_test') else value)
        class Shell:
            def __init__(self,a,run):self.broken=False;self.actions=[];state['shells']+=1
            def close(self):pass
            def command(self,cmd,required=True):
                state['commands'].append(cmd);self.actions.append({'command':cmd,'exit_code':0})
                if cmd.startswith('cd ') and fail_cd:raise RuntimeError('cd failed')
                if './path_test ' in cmd:
                    if timeout:self.broken=True;raise TimeoutError('offline timeout')
                    for name in ('path-test.txt',):
                        state['data'][state['remote']+'/'+name]=blobs()[name]
                    if nonzero:self.actions[-1]['exit_code']=1
                for name in ('stock-before.txt','stock-after.txt'):
                    if '> '+name in cmd:state['data'][state['remote']+'/'+name]=blobs()[name]
                if cmd.startswith('if test -r /dev/shmem/delphi-observer-path-'):state['data'][state['remote']+'/observer.bin']=trace(pid=200)
                if cmd.startswith('if test -r /dev/shmem/delphi-path-report-'):state['data'][state['remote']+'/report.bin']=native_report()
                return 0
        with patch.object(m,'ROOT',self.root),patch.object(m,'package_files',return_value=uploaded), \
             patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),contextlib.redirect_stdout(io.StringIO()):
            result=m.main(['--run'] if run else [])
        summary=None
        if run:summary=json.loads(next((self.root/'delphi-dump').glob('*/path-summary.json')).read_text())
        return result,state,summary
    def test_default_is_plan_without_connections_or_output_folder(self):
        result,state,_=self.simulate(run=False)
        self.assertEqual(result,0);self.assertEqual(state['shells'],0)
        self.assertNotIn('remote',state);self.assertFalse((self.root/'delphi-dump').exists())
    def test_success_verifies_capture_and_stock_identity(self):
        result,state,summary=self.simulate()
        self.assertEqual(result,0);self.assertTrue(summary['passed'])
        self.assertEqual(summary['stock_pids'],[42])
        self.assertFalse(summary['actual_androidauto_interposition_tested'])
        self.assertEqual(len(summary['artifacts']),5)
    def test_cd_failure_never_writes_relative_results(self):
        result,state,summary=self.simulate(fail_cd=True)
        self.assertEqual(result,1);self.assertEqual(len(state['commands']),1)
        self.assertTrue(state['commands'][0].startswith('cd '))
        self.assertFalse(summary['passed'])
    def test_tampered_upload_never_launches_shell(self):
        result,state,summary=self.simulate(tamper=True)
        self.assertEqual(result,1);self.assertEqual(state['shells'],0)
        self.assertFalse(summary['passed'])
    def test_timeout_session_is_not_reused(self):
        result,state,summary=self.simulate(timeout=True)
        self.assertEqual(result,1)
        self.assertFalse(any('stock-after.txt' in c for c in state['commands']))
        self.assertFalse(summary['passed'])
    def test_nonzero_action_cannot_pass_with_success_artifacts(self):
        result,state,summary=self.simulate(nonzero=True)
        self.assertEqual(result,1);self.assertFalse(summary['passed'])
    def test_command_scope_and_artifacts(self):
        result,state,summary=self.simulate()
        command=next(c for c in state['commands'] if './path_test ' in c)
        self.assertEqual(command,'LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./path_test '+state['remote']+' suite > path-test.txt 2>&1')
        self.assertFalse(any('procman' in c or 'slay ' in c or 'on ' in c for c in state['commands']))
        self.assertEqual(set(a['file'] for a in summary['artifacts']),set(m.RESULTS))
        token=state['remote'].removeprefix(m.REMOTE_PREFIX)
        report_path='/dev/shmem/delphi-path-report-'+token+'.bin'
        self.assertIn('if test -r '+report_path+'; then cp '+report_path+' report.bin; fi',state['commands'])

class ReportTests(unittest.TestCase):
    def test_failure_text_overrides_success_markers(self):
        for message in (b'PATH_CHECK_FAILED line=90 errno=1',b'Fatal signal 11',b'fatal SIGNAL 9'):
            data=blobs();data['path-test.txt']+=message+b'\n'
            with self.subTest(message=message),self.assertRaises(ValueError):m.assess(data)
    def test_report_mutations_rejected(self):
        for index in (0,1,2,3,5,6,7,8,11,12,16,17,18,19,20,21,23,25,26,27,51):
            data=bytearray(native_report());struct.pack_into('<I',data,index*4,0xffffffff)
            with self.subTest(index=index),self.assertRaises(ValueError):m.assess_report(data)
        with self.assertRaises(ValueError):m.assess_report(native_report()[:-1])
    def test_trace_pid_report_pid_and_markers_must_match(self):
        data=blobs();data['observer.bin']=trace(pid=201)
        with self.assertRaises(ValueError):m.assess(data)
        for marker in m.MARKERS:
            data=blobs();data['path-test.txt']=data['path-test.txt'].replace(marker.encode(),b'')
            with self.subTest(marker=marker),self.assertRaises(ValueError):m.assess(data)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()
