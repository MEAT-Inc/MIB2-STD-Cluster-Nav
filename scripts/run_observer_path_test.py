"""RAM-only isolated observer pathname test. Defaults to an offline plan."""
from project_console import console_session, log as print, status, progress
import argparse
import datetime as dt
import ftplib
import getpass
import hashlib
import json
from pathlib import Path
import re
import shlex
import struct
import uuid
import delphi_inventory as d
from run_observer_smoke import Shell, retrieve, stock_processes, assess as assess_smoke

ROOT=Path(__file__).resolve().parents[1]
NAMES=('path_test','path_child','path_original','libautoreceiver.so','libdelphi_observer.so')
REMOTE_PREFIX='/ramdisk/delphi-path-test_'
RESULTS=('stock-before.txt','stock-after.txt','path-test.txt','report.bin','observer.bin')
MARKERS=('PATH_SUITE_PASS','PATH_BASELINE_PASS','PATH_ONE_SHOT_RESTORE_PASS',
         'PATH_AFTER_DETACH_FAILURE_PASS','PATH_BEFORE_DETACH_FAILURE_PASS','PATH_ORPHAN_WATCHDOG_PASS')

def validate_remote(path):
    if not re.fullmatch(re.escape(REMOTE_PREFIX)+r'[0-9a-f]{32}',path):
        raise ValueError('Refusing a path outside the unique RAM test namespace')
    return path

def sha(data): return hashlib.sha256(data).hexdigest()

def package_files(directory):
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('kind')!='isolated_observer_path_test' or set(manifest['files'])!=set(NAMES):
        raise ValueError('Wrong path-test package manifest')
    files={name:(directory/name).read_bytes() for name in NAMES}
    for name,data in files.items():
        if not data or len(data)>128*1024 or len(data)!=manifest['files'][name]['bytes'] or sha(data)!=manifest['files'][name]['sha256']:
            raise ValueError('Package hash/size check failed: '+name)
    return files

def assess(blobs):
    output=blobs['path-test.txt']
    if b'PATH_CHECK_FAILED' in output or re.search(rb'fatal\s+signal',output,re.I):
        raise ValueError('Native suite reported a check failure or fatal signal')
    for marker in MARKERS:
        if marker.encode() not in blobs['path-test.txt'].splitlines():
            raise ValueError('Missing native suite marker: '+marker)
    # Reuse the trace/stock identity checks with the synthetic nine-call contract.
    fixtures=dict(blobs, **{'baseline.txt':b'DELPHI_SMOKE_PASS mode=baseline calls=9',
                           'observed.txt':b'DELPHI_SMOKE_PASS mode=observed calls=9'})
    result=assess_smoke(fixtures)
    native=assess_report(blobs['report.bin'])
    trace=result['decoded_log']
    if native['records'][1]['pid']!=trace['pid'] or native['records'][1]['records']!=trace['count']:
        raise ValueError('Native report and observer trace disagree')
    if any(r['pid'] in result['stock_pids'] or r['ppid'] in result['stock_pids'] for r in native['records']):
        raise ValueError('Native report references a stock process')
    result['native_report']=native
    return result

def assess_report(data):
    if len(data)!=208: raise ValueError('Wrong native report length')
    words=struct.unpack('<52I',data)
    header=words[:16]
    if header[:3]!=(0x31545044,1,208) or header[3]!=1 or header[4] not in (0,1) or \
       header[5:9]!=(1,1,6,1) or header[11]!=1 or any(header[12:16]):
        raise ValueError('Native report header failed validation')
    records=[dict(zip(('sequence','pid','ppid','observed','records','args_ok'),words[i:i+6]))
             for i in range(16,52,6)]
    pids=[r['pid'] for r in records]
    parent=records[0]['ppid']
    if not 0<parent<=0x7fffffff or len(set(pids))!=6 or any(not 0<pid<=0x7fffffff or pid==parent for pid in pids):
        raise ValueError('Native report process identity failed validation')
    for i,r in enumerate(records):
        if r['sequence']!=i+1 or r['ppid']!=parent or r['observed']!=int(i==1) or r['args_ok']!=1 or \
           (not 1<=r['records']<=9 if i==1 else r['records']!=0):
            raise ValueError('Native report child failed validation')
    if (header[9],header[10])!=(records[-1]['pid'],parent):
        raise ValueError('Native report final identity failed validation')
    return dict(armed=header[3],done=header[4],watchdog_finished=header[5],
                watchdog_removed=header[6],app_runs=header[7],observed_runs=header[8],records=records)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='Upload five verified files to a fresh RAM directory and run the bounded synthetic suite')
    parser.add_argument('--host',default='192.168.1.4')
    parser.add_argument('--port',type=int,default=21)
    parser.add_argument('--telnet-port',type=int,default=23)
    parser.add_argument('--username',default='ftpuser')
    parser.add_argument('--telnet-user',default='root')
    parser.add_argument('--ask-password',action='store_true')
    parser.add_argument('--timeout',type=float,default=40)
    a=parser.parse_args(argv)
    if not 30<=a.timeout<=120 or not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535:
        parser.error('Timeout must be 30..120 seconds; ports must be 1..65535')
    files=package_files(ROOT/'native/observer/path-test/release')
    print('Plan: upload five verified files into a fresh /ramdisk/delphi-path-test_<uuid> directory.')
    print('Run the bounded synthetic pathname suite and collect five private RAM artifacts.')
    print('Only its private path_child pathname is redirected; stock AndroidAuto and procman are not stopped.')
    if not a.run:
        print('Plan only. Add --run on the connected laptop to perform this test.'); return 0
    base=ROOT/'delphi-dump'; d.reject_link(base); base.mkdir(exist_ok=True)
    token=uuid.uuid4().hex
    remote=validate_remote(REMOTE_PREFIX+token)
    run=base/('_observer_path_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8])
    run.mkdir()
    password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    shell=None; cwd_verified=False; blobs={}
    report=dict(kind='isolated_observer_path_test',remote_directory=remote,passed=False,actions=[],artifacts=[],
                actual_androidauto_interposition_tested=False)
    def persist(): (run/'path-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    persist()
    try:
        with ftplib.FTP(timeout=a.timeout) as ftp:
            progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
            ftp.connect(a.host,a.port); ftp.login(a.username,password); ftp.voidcmd('TYPE I')
            ftp.mkd(remote) # must be NEW; no reuse or replacement of another directory
            for name,data in files.items():
                import io
                status('Uploading and verifying payload: '+name)
                ftp.storbinary('STOR '+remote+'/'+name,io.BytesIO(data))
                if retrieve(ftp,remote+'/'+name,128*1024)!=data: raise ValueError('Upload readback differs: '+name)
        shell=Shell(a,run)
        shell.command('cd '+shlex.quote(remote))
        cwd_verified=True
        for name in NAMES: shell.command('chmod 500 '+name)
        shell.command('pidin -p AndroidAuto arguments > stock-before.txt 2>&1')
        print('Running isolated pathname suite...',flush=True)
        shell.command('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./path_test '+
                      shlex.quote(remote)+' suite > path-test.txt 2>&1')
    except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:
        report['error']=(type(exc).__name__+': '+str(exc)).replace(password,'[redacted]') if password else str(exc)
    finally:
        if shell and cwd_verified and not shell.broken:
            final_steps=('pidin -p AndroidAuto arguments > stock-after.txt 2>&1',
                'if test -r /dev/shmem/delphi-path-report-'+token+'.bin; then cp /dev/shmem/delphi-path-report-'+token+'.bin report.bin; fi',
                'if test -r /dev/shmem/delphi-observer-path-'+token+'.bin; then cp /dev/shmem/delphi-observer-path-'+token+'.bin observer.bin; fi')
            for command in final_steps:
                try: shell.command(command,required=False)
                except (OSError,EOFError,RuntimeError,ValueError): break
            if not shell.broken:
                for name in RESULTS:
                    try: shell.command('if test -f '+name+'; then chmod 644 '+name+'; fi',required=False)
                    except (OSError,EOFError,RuntimeError,ValueError): break
        if shell:
            report['actions']=shell.actions; shell.close()
        # Each artifact has a fresh FTP session; failed transfers cannot poison
        # the next command. A transport failure stops further connection attempts.
        for name in (RESULTS if cwd_verified else ()):
            try:
                with ftplib.FTP(timeout=a.timeout) as ftp:
                    progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
                    ftp.connect(a.host,a.port); ftp.login(a.username,password); ftp.voidcmd('TYPE I')
                    data=retrieve(ftp,remote+'/'+name)
                (run/name).write_bytes(data); blobs[name]=data
                report['artifacts'].append(dict(file=name,bytes=len(data),sha256=sha(data)))
            except (OSError,EOFError) as exc:
                report['artifacts'].append(dict(file=name,error=type(exc).__name__))
                report['collection_error']=type(exc).__name__
                break
            except (ValueError,ftplib.Error) as exc:
                report['artifacts'].append(dict(file=name,error=type(exc).__name__))
        try:
            report.update(assess(blobs))
            report['passed']='error' not in report and not any(action['exit_code'] for action in report['actions'])
            (run/'observer-decoded.json').write_text(json.dumps(report.pop('decoded_log'),indent=2))
        except (KeyError,ValueError) as exc: report['validation_error']=str(exc)
        persist()
    print('Saved: '+str(run))
    print('Result: '+('ISOLATED PATH TEST PASS' if report['passed'] else 'INCOMPLETE / FAILED - preserve this folder for review'))
    print('RAM artifacts are retained until explicitly removed or the unit restarts.')
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
