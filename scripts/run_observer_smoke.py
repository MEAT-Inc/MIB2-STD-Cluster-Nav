"""RAM-only observer smoke test. Default is a plan; --run uploads and executes synthetic tests."""
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
import socket
import uuid
import delphi_inventory as d
from decode_delphi_observer import decode

ROOT=Path(__file__).resolve().parents[1]
NAMES=('observer_smoke','observer_smoke_guard','libautoreceiver.so','libdelphi_observer.so')
REMOTE_PREFIX='/ramdisk/delphi-observer-smoke_'
RESULTS=('stock-before.txt','baseline.txt','observed.txt','stock-after.txt','observer.bin',
         'procman.captured','libc.so.3.captured')

def validate_remote(path):
    if not re.fullmatch(re.escape(REMOTE_PREFIX)+r'[0-9a-f]{32}',path):
        raise ValueError('Refusing a path outside the unique RAM test namespace')
    return path

def sha(data): return hashlib.sha256(data).hexdigest()

def retrieve(ftp,remote,limit=16*1024*1024):
    progress('Retrieving '+remote.rsplit('/',1)[-1], key='retrieve:'+remote)
    data=bytearray()
    def save(block):
        if len(data)+len(block)>limit: raise ValueError('Transfer exceeds fixed limit')
        data.extend(block)
    ftp.retrbinary('RETR '+remote,save)
    if not data: raise ValueError('Zero-byte transfer: '+remote)
    return bytes(data)

class Shell:
    def __init__(self,a,run):
        self.sock=None; self.broken=False; self.actions=[]
        self.transcript=(run/'telnet-actions.txt').open('x',encoding='utf-8')
        try:
            status('Connecting to the head unit command shell.')
            self.sock=socket.create_connection((a.host,a.telnet_port),timeout=a.timeout)
            self.reader=d.TelnetReader(self.sock,a.timeout)
            prompts=[('login',re.compile(rb'(?i)(?:login|username):\s*$')),
                     ('password',re.compile(rb'(?i)password:\s*$')),('shell',d.TelnetReader.PROMPT)]
            label,_=self.reader.read_until(prompts)
            if label=='login':
                self.reader.send(a.telnet_user); label,_=self.reader.read_until(prompts)
            if label=='password':
                self.reader.send(getpass.getpass('Telnet password (Enter if blank): '))
                label,_=self.reader.read_until(prompts)
            if label!='shell': raise ValueError('Authentication did not reach a shell')
        except BaseException:
            self.close(); raise
    def command(self,command,required=True):
        if self.broken: raise RuntimeError('Failed session cannot be reused')
        if command.rstrip().endswith('&'):raise ValueError('A background command must end with a following statement before the completion marker')
        marker='OS'+uuid.uuid4().hex[:10]
        done=re.compile(marker.encode()+rb':([0-9]+):END')
        self.transcript.write('COMMAND '+command+'\n'); self.transcript.flush()
        def save(block):
            self.transcript.write('RECV '+repr(block)+'\n'); self.transcript.flush()
        try:
            self.reader.send(command+'; echo '+marker+':$?:END')
            label,response=self.reader.read_until([('done',done),('syntax',re.compile(rb'(?:^|[\r\n])(?:ksh|sh):[^\r\n]*syntax error'))],on_data=save)
            if label=='syntax':
                self.actions.append(dict(command=command,exit_code=None,error='shell_syntax_error'))
                raise RuntimeError('Remote shell syntax error; session stopped')
        except BaseException:
            self.broken=True
            raise
        self.last_response=response
        code=int(done.search(response).group(1))
        self.actions.append(dict(command=command,exit_code=code))
        if required and code: raise RuntimeError('Remote test step returned '+str(code)+': '+command)
        return code
    def close(self):
        if self.sock: self.sock.close(); self.sock=None
        self.transcript.close()

def package_files(directory):
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('kind')!='isolated_observer_smoke' or set(manifest['files'])!=set(NAMES):
        raise ValueError('Wrong smoke package manifest')
    files={name:(directory/name).read_bytes() for name in NAMES}
    for name,data in files.items():
        if len(data)>128*1024 or sha(data)!=manifest['files'][name]['sha256']:
            raise ValueError('Package hash/size check failed: '+name)
    return files

def stock_processes(data):
    found={}
    for line in data.replace(b'\r',b'\n').splitlines():
        m=re.match(rb'^\s*(\d+)\s+(\S+)(.*)$',line)
        if m and m[2].rsplit(b'/',1)[-1]==b'AndroidAuto':
            found[int(m[1])]=(m[2]+m[3]).decode('utf-8',errors='replace')
    return found

def assess(blobs):
    before=stock_processes(blobs['stock-before.txt'])
    after=stock_processes(blobs['stock-after.txt'])
    if not before or before!=after: raise ValueError('Stock AndroidAuto identity changed or was not captured')
    if b'DELPHI_SMOKE_PASS mode=baseline calls=9' not in blobs['baseline.txt']:
        raise ValueError('Baseline did not pass')
    if b'DELPHI_SMOKE_PASS mode=observed calls=9' not in blobs['observed.txt']:
        raise ValueError('Observed child did not pass')
    log=decode(blobs['observer.bin'])
    if log['pointer_bytes']!=4 or log['logging_disabled'] or not 1<=log['count']<=9 or log['count']+log['dropped']>9 or \
       (not log['dropped_is_lower_bound'] and log['count']+log['dropped']!=9) or \
       log['incomplete_records'] or log['writer_active'] or log['pid'] in before:
        raise ValueError('Observer trace failed validation')
    previous=0xfff
    for r in log['records']:
        receiver=int(r['receiver'],16)
        if not previous<receiver<=0x1008 or int(r['endpoint'],16)!=receiver+0x1000 or not int(r['caller'],16):
            raise ValueError('Synthetic argument/caller check failed')
        previous=receiver
    return dict(stock_processes_unchanged=True,stock_pids=list(before),decoded_log=log)

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true',help='Upload four verified test files into a new RAM directory and run two isolated children')
    parser.add_argument('--host',default='192.168.1.4')
    parser.add_argument('--port',type=int,default=21)
    parser.add_argument('--telnet-port',type=int,default=23)
    parser.add_argument('--username',default='ftpuser')
    parser.add_argument('--telnet-user',default='root')
    parser.add_argument('--ask-password',action='store_true')
    parser.add_argument('--timeout',type=float,default=25)
    a=parser.parse_args(argv)
    if not 15<=a.timeout<=120 or not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535:
        parser.error('Timeout must be 15..120 seconds; ports must be 1..65535')
    files=package_files(ROOT/'native/observer/smoke/release')
    print('Plan: upload four small files into a new /ramdisk/delphi-observer-smoke_<uuid> directory.')
    print('Run baseline and preloaded synthetic children; each has an approximately 10-second watchdog.')
    print('Collect RAM trace, stock process snapshots, and RAM copies of procman/libc for offline analysis.')
    print('Stock AndroidAuto, its supervisor, factory libraries and startup configuration are not modified.')
    if not a.run:
        print('Plan only. Add --run on the connected laptop to perform this test.'); return 0
    base=ROOT/'delphi-dump'; d.reject_link(base); base.mkdir(exist_ok=True)
    token=uuid.uuid4().hex
    remote=validate_remote(REMOTE_PREFIX+token)
    run=base/('_observer_smoke_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8])
    run.mkdir()
    password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    shell=None; cwd_verified=False; blobs={}
    report=dict(kind='isolated_observer_smoke',remote_directory=remote,passed=False,actions=[],artifacts=[],
                actual_androidauto_interposition_tested=False)
    def persist(): (run/'smoke-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
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
        for mode in ('baseline','observed'):
            print('Running isolated '+mode+' test...',flush=True)
            shell.command('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./observer_smoke_guard '+
                shlex.quote(remote)+' '+mode+' > '+mode+'.txt 2>&1')
    except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:
        report['error']=(type(exc).__name__+': '+str(exc)).replace(password,'[redacted]') if password else str(exc)
    finally:
        if shell and cwd_verified and not shell.broken:
            final_steps=('pidin -p AndroidAuto arguments > stock-after.txt 2>&1',
                'if test -r /dev/shmem/delphi-observer-smoke-'+token+'.bin; then cp /dev/shmem/delphi-observer-smoke-'+token+'.bin observer.bin; fi',
                'cp /proc/boot/procman procman.captured',
                'cp /proc/boot/libc.so.3 libc.so.3.captured')
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
        for name in RESULTS:
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
            report['passed']='error' not in report
            (run/'observer-decoded.json').write_text(json.dumps(report.pop('decoded_log'),indent=2))
        except (KeyError,ValueError) as exc: report['validation_error']=str(exc)
        persist()
    print('Saved: '+str(run))
    print('Result: '+('ISOLATED SMOKE PASS' if report['passed'] else 'INCOMPLETE / FAILED - preserve this folder for review'))
    print('RAM artifacts are retained until explicitly removed or the unit restarts.')
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
