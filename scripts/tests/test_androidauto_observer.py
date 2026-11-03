"""Offline tests; no vehicle access."""
from pathlib import Path as _TestPath
import sys as _test_sys
_test_sys.path.insert(0, str(_TestPath(__file__).resolve().parents[1]))
from project_console import console_session
import contextlib,ftplib,io,json,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import run_androidauto_observer as m

class RunnerTests(unittest.TestCase):
    def simulate(self,mode='',run=True,phone=False,display=False):
        state=dict(data={},commands=[],connections=0)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);release=root/'native/observer/launch/release';release.mkdir(parents=True);(release/'manifest.json').write_text(json.dumps({'capture_profiles':[20,60]}));uploads={name:name.encode() for name in m.NAMES}
            display_release=root/'native/observer/display/release';display_release.mkdir(parents=True);(display_release/'manifest.json').write_text(json.dumps({'capture_profiles':[20,60]}))
            refs={name:('ref '+name).encode() for name in m.REFERENCES}
            refs['procman-core.cfg']=b'-f AndroidAuto -n"androidauto" -l20 -x10 -r -c15 -a"-t"\n'
            contract={name:(spec[0],len(refs[name]),m.sha(refs[name])) for name,spec in m.REFERENCES.items()}
            class FTP:
                def __init__(self,**kw):state['connections']+=1
                def __enter__(self):return self
                def __exit__(self,*args):pass
                def connect(self,*args):pass
                def login(self,*args):pass
                def voidcmd(self,*args):pass
                def mkd(self,path):state['remote']=m.validate_remote(path)
                def storbinary(self,cmd,source):state['data'][cmd[5:]]=source.read()
                def retrbinary(self,cmd,save):
                    path=cmd[5:]
                    if path not in state['data']:raise ftplib.error_perm('550 absent')
                    data=state['data'][path]
                    if mode=='upload' and path.endswith('/observer_launch'):data+=b'bad'
                    save(data)
            class Shell:
                def __init__(self,a,folder):
                    self.broken=False;self.closed=False;self.actions=[]
                    state.setdefault('shells',[]).append(self)
                def close(self):self.closed=True
                def command(self,cmd,required=True):
                    if self.broken or self.closed:raise AssertionError('reused broken/closed shell')
                    state['commands'].append(cmd);self.actions.append(dict(command=cmd,exit_code=0))
                    if cmd.startswith('cd ') and (mode=='cd' or mode=='collect_cd' and len(state['shells'])==2):raise RuntimeError('failed cd')
                    if cmd.startswith('cp '):
                        name=cmd.split()[-1];state['data'][state['remote']+'/'+name]=refs[name]+(b'bad' if mode=='reference' else b'')
                    if '> stock-' in cmd:
                        name=cmd.split('> ')[1].split()[0]
                        state['data'][state['remote']+'/'+name]=(b'44 /extbin/apps/bin/AndroidAuto -t\n' if phone and 'stock-after' in name else b'42 /extbin/apps/bin/AndroidAuto -t\n')+(b'43 /extbin/apps/bin/AndroidAuto -t\n' if mode=='ambiguous' else b'')
                    if './observer_launch ' in cmd:
                        if mode=='timeout':self.broken=True;raise TimeoutError('offline timeout')
                        state['data'][state['remote']+'/controller.bin']=b'unknown result'
                        if phone:
                            evidence,oldroot,_=AssessmentTests().fixture(count=1)
                            evidence.update(refs)
                            if display and mode!='missing_display':
                                from test_androidauto_display import DisplayTests,HEADER,RECORD
                                extra=DisplayTests().sample();struct.pack_into('<I',extra,24,43);struct.pack_into('<I',extra,HEADER+20,0x2000);struct.pack_into('<I',extra,HEADER+2*RECORD+16,0x780761f0)
                                if mode=='partial_display':struct.pack_into('<I',extra,HEADER+2*RECORD+16,0x780761f4)
                                evidence['display.bin']=bytes(extra)
                            controller=bytearray(evidence['controller.bin'].replace(oldroot.encode(),state['remote'].encode()))
                            struct.pack_into('<I',controller,4,2);struct.pack_into('<I',controller,256,60)
                            evidence['controller.bin']=bytes(controller)
                            evidence['launch.txt']=evidence['launch.txt'].replace(oldroot.encode(),state['remote'].encode())+b'LAUNCH_READY capture_seconds=60\n'
                            for name,data in evidence.items():state['data'][state['remote']+'/'+name]=data
            with patch.object(m,'ROOT',root),patch.object(m,'package_files',return_value=uploads),patch.object(m,'REFERENCES',contract),patch.object(m.ftplib,'FTP',FTP),patch.object(m,'Shell',Shell),patch.object(m,'wait_for_phone_ready',side_effect=RuntimeError('not ready') if mode=='readyfail' else None,return_value=b'LAUNCH_READY capture_seconds=60\n'),patch('builtins.input',side_effect=lambda prompt: state['shells'][-1].closed or (_ for _ in ()).throw(AssertionError('phone prompt before close'))),contextlib.redirect_stdout(io.StringIO()):
                code=m.main((['--run'] if run else [])+(['--phone-capture'] if phone else [])+(['--display-capture'] if display else []))
            summary=json.loads(next(root.glob('delphi-dump/*/androidauto-summary.json')).read_text()) if run else None
        return code,state,summary
    def test_plan_has_no_network(self):
        code,s,_=self.simulate(run=False);self.assertEqual(code,0);self.assertEqual(s['connections'],0)
    def test_upload_tamper_prevents_shell(self):
        _,s,r=self.simulate('upload');self.assertEqual(s['commands'],[]);self.assertFalse(r['passed'])
    def test_cd_failure_does_not_collect_or_write_relative(self):
        _,s,r=self.simulate('cd');self.assertEqual(len(s['commands']),1);self.assertEqual(r['artifacts'],[])
    def test_reference_mismatch_prevents_launch(self):
        _,s,_=self.simulate('reference');self.assertFalse(any('./observer_launch ' in x for x in s['commands']))
    def test_stock_ambiguity_prevents_launch(self):
        _,s,_=self.simulate('ambiguous');self.assertFalse(any('./observer_launch ' in x for x in s['commands']))
    def test_timeout_is_not_reused_but_ftp_collects(self):
        _,s,r=self.simulate('timeout');self.assertIn('./observer_launch ',s['commands'][-1]);self.assertFalse(r['passed']);self.assertGreater(s['connections'],5)
    def test_unknown_result_cannot_pass(self):
        code,s,r=self.simulate();self.assertEqual(code,1);self.assertFalse(r['passed']);self.assertIn('validation_error',r)
        launch=next(x for x in s['commands'] if './observer_launch ' in x)
        self.assertEqual(launch,'LD_PRELOAD= ./observer_launch '+s['remote']+' 42 > launch.txt 2>&1')
    def test_real_short_name_and_manager_arguments(self):
        self.assertEqual(m.fresh_stock_pid(b'42 AndroidAuto -t\n'),42)
        self.assertEqual(m.fresh_stock_pid(b'42 AndroidAuto -t -X2\n'),42)
        for data in (b'42 AndroidAuto -wrong',b'42 AndroidAuto -t -Xbad',b'42 AndroidAuto -t extra'):
            with self.assertRaises(ValueError):m.fresh_stock_pid(data)
    def test_phone_handoff_uses_new_verified_session(self):
        code,state,summary=self.simulate(phone=True)
        self.assertEqual(code,0);self.assertTrue(summary['passed'])
        self.assertEqual(len(state['shells']),2)
        self.assertTrue(all(s.closed for s in state['shells']))
        self.assertTrue(summary['phone_handoff_ready']);self.assertEqual(summary['capture_seconds'],60)
        self.assertEqual(sum(c.startswith('cd ') for c in state['commands']),2)
        self.assertTrue(any(c.endswith('phone > launch.txt 2>&1 & delphi_aa_job=$!') for c in state['commands']))
        background=next(i for i,c in enumerate(state['commands']) if c.endswith('phone > launch.txt 2>&1 & delphi_aa_job=$!'))
        self.assertIn('chmod 644 launch.txt',state['commands'][:background])
    def test_display_capture_collects_and_correlates(self):
        code,state,r=self.simulate(phone=True,display=True)
        self.assertEqual(code,0);self.assertTrue(r['passed']);self.assertTrue(r['display_capture_validated'])
        self.assertEqual(r['video_configuration_records'],1);self.assertEqual(r['discovery_records'],1)
        self.assertTrue(any('delphi-display-' in c and 'cp ' in c for c in state['commands']))
        self.assertTrue(any(c=='if test -f display.bin; then chmod 644 display.bin; fi' for c in state['commands']))
    def test_missing_or_partial_display_retains_restoration_evidence(self):
        for mode in ('missing_display','partial_display'):
            with self.subTest(mode=mode):
                code,state,r=self.simulate(mode=mode,phone=True,display=True)
                self.assertEqual(code,1);self.assertFalse(r['passed']);self.assertTrue(r['completed_restored'])
                self.assertTrue(r['actual_androidauto_interposition_tested'])
    def test_display_plan_without_network(self):
        code,state,_=self.simulate(run=False,phone=True,display=True)
        self.assertEqual(code,0);self.assertEqual(state['connections'],0)
    def test_failed_phone_readiness_waits_without_handoff(self):
        code,state,summary=self.simulate(mode='readyfail',phone=True)
        self.assertEqual(code,1);self.assertFalse(summary.get('phone_handoff_ready',False))
        self.assertEqual(len(state['shells']),1)
        self.assertIn('wait "$delphi_aa_job"',state['commands'])
    def test_collection_cd_failure_does_not_write_in_wrong_directory(self):
        code,state,summary=self.simulate(mode='collect_cd',phone=True)
        self.assertEqual(code,1)
        last_cd=max(i for i,c in enumerate(state['commands']) if c.startswith('cd '))
        self.assertEqual(last_cd,len(state['commands'])-1)
    def test_exact_stock_path_required(self):
        for data in (b'42 AndroidAuto\n',b'42 /ramdisk/AndroidAuto\n',b''):
            with self.assertRaises(ValueError):m.fresh_stock_pid(data)
    def test_package_size_and_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder);files={n:n.encode() for n in m.NAMES}
            for n,data in files.items():(path/n).write_bytes(data)
            manifest=dict(kind='managed_androidauto_observer',files={n:dict(bytes=len(data),sha256=m.sha(data)) for n,data in files.items()})
            (path/'manifest.json').write_text(json.dumps(manifest));self.assertEqual(m.package_files(path),files)
            (path/m.NAMES[0]).write_bytes(b'tamper')
            with self.assertRaises(ValueError):m.package_files(path)
class PhoneReadinessTests(unittest.TestCase):
    def test_ready_and_stale_markers(self):
        with patch.object(m.time,'monotonic',return_value=1):
            self.assertIn(b'LAUNCH_READY',m.wait_for_phone_ready(lambda:b'LAUNCH_READY capture_seconds=60\n',0))
            with self.assertRaises(RuntimeError):m.wait_for_phone_ready(lambda:b'LAUNCH_READY capture_seconds=60\nLAUNCH_COMPLETE\n',0)
        with patch.object(m.time,'monotonic',side_effect=[1,26]),self.assertRaises(RuntimeError):
            m.wait_for_phone_ready(lambda:b'LAUNCH_READY capture_seconds=60\n',0)
    def test_missing_readiness_is_bounded(self):
        with patch.object(m.time,'monotonic',side_effect=[1,26]),patch.object(m.time,'sleep'),self.assertRaises(RuntimeError):
            m.wait_for_phone_ready(lambda:b'',0)
class ConfigTests(unittest.TestCase):
    def test_restart_flag_required(self):
        good=b'-f AndroidAuto -n"androidauto" -l20 -x10 -r -c15 -a"-t"\n'
        self.assertIn('-r',m.verify_manager_config(good))
        for bad in (good.replace(b'-r ',b''),good+good,good.replace(b'-c15',b'-c0')):
            with self.assertRaises(ValueError):m.verify_manager_config(bad)
class AssessmentTests(unittest.TestCase):
    def fixture(self,count=1):
        root=m.REMOTE_PREFIX+'a'*32
        controller=bytearray(512)
        struct.pack_into('<16I',controller,0,0x314c4144,1,512,6,0,1,1,0,0,1,43,44,45,46,42,1)
        struct.pack_into('<4Q',controller,64,100,200,300,400)
        controller[96:96+len(root)]=root.encode()
        struct.pack_into('<8I',controller,224,1,count,0,0,0,0,0,0)
        trace=bytearray(128+1024*32)
        struct.pack_into('<32I',trace,0,0x314f4c44,1,128,32,1024,4,43,0x78076fac,0x78000000,1,count,0,0,0,*([0]*18))
        for i in range(count):struct.pack_into('<8I',trace,128+i*32,i+1,1,i+1,0x1000,0x2000,0x124e54,0,i+1)
        refs={name:name.encode() for name in m.REFERENCES}
        contract={name:(spec[0],len(refs[name]),m.sha(refs[name])) for name,spec in m.REFERENCES.items()}
        refs['procman-core.cfg']=b'-f AndroidAuto -n"androidauto" -l20 -x10 -r -c15 -a"-t"\n'
        blobs=dict(refs,**{'controller.bin':bytes(controller),'observer.bin':bytes(trace),
          'stock-before.txt':b'42 /extbin/apps/bin/AndroidAuto -t',
          'stock-fresh.txt':b'42 /extbin/apps/bin/AndroidAuto -t',
          'stock-after.txt':b'44 /extbin/apps/bin/AndroidAuto -t',
          'launch.txt':('LAUNCH_OBSERVED pid=43 parent=46 base=100000 start=300 exec='+root+'/AndroidAuto.original\nLAUNCH_RESTORED\nLAUNCH_COMPLETE\n').encode()})
        return blobs,root,contract
    def test_captured_and_zero_count(self):
        for count in (0,1,1024):
            blobs,root,refs=self.fixture(count)
            with patch.object(m,'REFERENCES',refs):r=m.assess(blobs,root)
            self.assertTrue(r['completed_restored']);self.assertEqual(r['captured_registration'],bool(count))
    def test_version_two_capture_profile(self):
        blobs,root,refs=self.fixture()
        data=bytearray(blobs['controller.bin']);struct.pack_into('<I',data,4,2);struct.pack_into('<I',data,256,60);blobs['controller.bin']=bytes(data)
        with patch.object(m,'REFERENCES',refs):self.assertEqual(m.assess(blobs,root)['capture_seconds'],60)
        struct.pack_into('<I',data,256,120);blobs['controller.bin']=bytes(data)
        with patch.object(m,'REFERENCES',refs),self.assertRaises(ValueError):m.assess(blobs,root)
    def test_unknown_caller_and_wrong_load_identity_rejected(self):
        blobs,root,refs=self.fixture()
        bad=bytearray(blobs['observer.bin']);struct.pack_into('<I',bad,128+20,0x111111);blobs['observer.bin']=bytes(bad)
        with patch.object(m,'REFERENCES',refs),self.assertRaises(ValueError):m.assess(blobs,root)
        blobs,root,refs=self.fixture();blobs['launch.txt']=blobs['launch.txt'].replace(b'parent=46',b'parent=47')
        with patch.object(m,'REFERENCES',refs),self.assertRaises(ValueError):m.assess(blobs,root)
    def test_controller_mutations_fail_closed(self):
        for offset in (0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60,64,72,80,88,96,224,228,232,236,240,244,248,252,256,511):
            blobs,root,refs=self.fixture();raw=bytearray(blobs['controller.bin']);raw[offset]^=0xff
            if offset in (48,52):raw[offset:offset+4]=bytes(4)
            if offset in (64,72,80,88):raw[offset:offset+8]=bytes(8)
            blobs['controller.bin']=bytes(raw)
            with patch.object(m,'REFERENCES',refs),self.subTest(offset=offset),self.assertRaises(ValueError):m.assess(blobs,root)
    def test_mismatched_trace_and_results_rejected(self):
        for name in ('observer.bin','controller.bin','launch.txt','stock-after.txt','receiver.reference'):
            blobs,root,refs=self.fixture();blobs[name]=b'unknown'
            with patch.object(m,'REFERENCES',refs),self.subTest(name=name),self.assertRaises(ValueError):m.assess(blobs,root)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        unittest.main()

