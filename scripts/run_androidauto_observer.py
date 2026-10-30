"""Actual AndroidAuto observer diagnostic. Defaults to an offline plan."""
import argparse, datetime as dt, ftplib, getpass, hashlib, io, json, re, shlex, struct, uuid, time
from pathlib import Path
import delphi_inventory as d
from run_observer_smoke import Shell, retrieve, stock_processes
from decode_delphi_observer import decode
ROOT=Path(__file__).resolve().parents[1]
NAMES=('observer_launch','libdelphi_observer.so')
REMOTE_PREFIX='/ramdisk/delphi-aa-observer_'
KNOWN_REGISTRATION_CALLERS={0x124e54,0x127390,0x128764,0x12b95c,0x12ed44,0x12fa08,0x130b90,0x132a3c}
REFERENCES={
 'AndroidAuto.original':('/extbin/apps/bin/AndroidAuto',482967,'da1fd5776f6b85962b84ad77c6f564d3f09dd8079652229cda57b4138060c271'),
 'receiver.reference':('/extbin/apps/lib/libautoreceiver.so.1',1621327,'e14aa58d7867955d968d291fd43b941223fb5072ca7184d8885ef40f2323c92d'),
 'procman.reference':('/proc/boot/procman',196184,'c32c018b515396bd0b322fb2014b45f2fba37d6000b2d178e9dc402c6845f05d')}
RESULTS=('stock-before.txt','stock-before-maps.txt','stock-fresh.txt','stock-after.txt','stock-after-maps.txt','launch.txt','controller.bin','observer.bin')
def sha(data):return hashlib.sha256(data).hexdigest()
def validate_remote(path):
    if not re.fullmatch(re.escape(REMOTE_PREFIX)+r'[0-9a-f]{32}',path):raise ValueError('Invalid unique RAM experiment path')
    return path
def package_files(directory,kind="managed_androidauto_observer"):
    manifest=json.loads((directory/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('kind')!=kind or set(manifest['files'])!=set(NAMES):raise ValueError('Wrong managed observer package')
    files={name:(directory/name).read_bytes() for name in NAMES}
    for name,data in files.items():
        entry=manifest['files'][name]
        if not data or len(data)>128*1024 or len(data)!=entry['bytes'] or sha(data)!=entry['sha256']:raise ValueError('Package hash/size mismatch: '+name)
    return files
def verify_reference(name,data):
    _,size,digest=REFERENCES[name]
    if len(data)!=size or sha(data)!=digest:raise ValueError('Stock reference hash/size mismatch: '+name)
def verify_manager_config(data):
    if not data or len(data)>65536:raise ValueError('Invalid manager configuration size')
    entries=[]
    for line in data.decode('utf-8',errors='strict').splitlines():
        words=shlex.split(line,comments=True)
        if not words:continue
        executable=words[words.index('-f')+1] if '-f' in words and words.index('-f')+1<len(words) else ''
        if executable.rsplit('/',1)[-1]=='AndroidAuto' or '-nandroidauto' in words:entries.append((executable,words))
    if len(entries)!=1:raise ValueError('Expected one AndroidAuto manager entry')
    executable,words=entries[0]
    if executable not in ('AndroidAuto','/extbin/apps/bin/AndroidAuto') or '-nandroidauto' not in words or '-r' not in words or '-a-t' not in words or '-c15' not in words:
        raise ValueError('AndroidAuto supervised restart configuration differs from reviewed unit')
    return words

def fresh_stock_pid(data):
    found=stock_processes(data)
    if len(found)!=1:raise ValueError('Expected exactly one fresh stock AndroidAuto PID')
    pid,args=next(iter(found.items()))
    parts=args.split()
    if not 0<pid<=0x7fffffff or parts[0] not in ('AndroidAuto','/extbin/apps/bin/AndroidAuto') or len(parts) not in (2,3) or parts[1]!='-t' or (len(parts)==3 and not re.fullmatch(r'-X[0-9]{1,20}',parts[2])):
        raise ValueError('Unexpected stock path/arguments/PID')
    return pid
def assess(blobs,remote=None):
    data=blobs['controller.bin']
    if len(data)!=512:raise ValueError('Incorrect controller result length')
    h=struct.unpack_from('<16I',data)
    starts=struct.unpack_from('<4Q',data,64)
    if h[0]!=0x314c4144 or h[1] not in (1,2) or h[2]!=512 or h[3:10]!=(6,0,1,1,0,0,1) or h[15]!=1:
        raise ValueError('Controller final state failed validation')
    capture_seconds=20 if h[1]==1 else struct.unpack_from('<I',data,256)[0]
    if capture_seconds not in (20,60) or any(data[256:] if h[1]==1 else data[260:]):raise ValueError('Invalid capture profile/reserved data')
    rawroot=data[96:224]
    if b'\0' not in rawroot:raise ValueError('Unterminated controller root')
    root,padding=rawroot.split(b'\0',1)
    if any(padding):raise ValueError('Nonzero controller root padding')
    root=validate_remote(root.decode('ascii'))
    if remote is not None and root!=remote:raise ValueError('Controller root differs from run directory')
    observed,restored,controller,manager,baseline=h[10:15]
    if any(not 0<pid<=0x7fffffff for pid in h[10:15]) or len(set(h[10:15]))!=5 or not all(starts):
        raise ValueError('Controller process identities failed validation')
    if fresh_stock_pid(blobs['stock-before.txt'])!=baseline or fresh_stock_pid(blobs['stock-fresh.txt'])!=baseline or fresh_stock_pid(blobs['stock-after.txt'])!=restored:
        raise ValueError('Controller and stock snapshots disagree')
    lines=blobs['launch.txt'].replace(b'\r',b'').splitlines()
    if b'LAUNCH_RESTORED' not in lines or b'LAUNCH_COMPLETE' not in lines or re.search(rb'(fatal\s+signal|LAUNCH_FAILED)',blobs['launch.txt'],re.I):
        raise ValueError('Native completion markers missing or failed')
    for name in REFERENCES:verify_reference(name,blobs[name])
    verify_manager_config(blobs['procman-core.cfg'])
    trace=decode(blobs['observer.bin']);th=struct.unpack_from('<32I',blobs['observer.bin'])
    status,count,dropped,slot,value,expected,got_valid,observer_base=struct.unpack_from('<8I',data,224)
    if trace['pointer_bytes']!=4 or trace['pid']!=observed or status!=1 or th[9]!=1 or th[12] not in (0,1) or any(th[14:]) or trace['writer_active'] or trace['incomplete_records'] or (count,dropped)!=(trace['count'],trace['dropped']):
        raise ValueError('Observer trace identity/state failed validation')
    if not int(trace['module_base'],16) or int(trace['native_address'],16)-int(trace['module_base'],16)!=0x76fac:
        raise ValueError('Unexpected native receiver symbol address')
    if any((slot,value,expected,got_valid,observer_base)):raise ValueError('Unexpected unused binding fields')
    observed_line=re.findall(rb'^LAUNCH_OBSERVED pid=(\d+) parent=(\d+) base=([0-9a-f]+) start=(\d+) exec=(\S+)\r?$',blobs['launch.txt'],re.M)
    if len(observed_line)!=1:raise ValueError('Missing observed executable identity')
    op,mp,base,started,executable=observed_line[0]
    if (int(op),int(mp),int(started))!=(observed,manager,starts[2]) or executable.decode('ascii')!=root+'/AndroidAuto.original':
        raise ValueError('Observed executable identity differs from controller')
    bias=int(base,16)-0x100000
    if bias<0 or bias>0x7fffffff:raise ValueError('Unexpected executable load bias')
    known_callers=KNOWN_REGISTRATION_CALLERS
    callers={int(r['caller'],16)-bias for r in trace['records']}
    captured=count>0
    if captured and not callers.intersection(known_callers):raise ValueError('No captured caller matches the verified AndroidAuto binary')
    return dict(completed_restored=True,process_restoration_verified=True,restoration_scope='process_identity_and_stock_files_only',captured_registration=captured,decoded_log=trace,
                capture_validated=captured,capture_seconds=capture_seconds,observed_pid=observed,restored_pid=restored,
                baseline_pid=baseline,manager_pid=manager,controller_pid=controller,
                executable_load_bias=bias,known_registration_callers=[hex(x) for x in sorted(callers.intersection(known_callers))],
                video_registration_seen=0x124e54 in callers)


def wait_for_phone_ready(read_log,started,limit=25):
    while time.monotonic()-started<limit:
        try:data=read_log()
        except (ValueError,ftplib.error_perm):data=b''
        lines=data.replace(b'\r',b'').splitlines()
        if any(x in data for x in (b'LAUNCH_FAILED',b'LAUNCH_REFUSED',b'LAUNCH_COMPLETE',b'LAUNCH_RESTORED')):
            raise RuntimeError('Native experiment ended before phone handoff')
        if b'LAUNCH_READY capture_seconds=60' in lines:
            if time.monotonic()-started>=limit:break
            return data
        time.sleep(1)
    raise RuntimeError('No timely native phone-capture readiness; no phone handoff performed')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phone-capture',action='store_true',help='Stage over Ethernet, capture for 60 seconds while the phone occupies USB, then reconnect to collect')
    p.add_argument('--display-capture',action='store_true',help='Read-only video configuration/focus and service-discovery capture; requires --phone-capture')
    p.add_argument('--run',action='store_true',help='Interrupt/restart actual AndroidAuto twice using the bounded native guard')
    p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21)
    p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--username',default='ftpuser')
    p.add_argument('--telnet-user',default='root');p.add_argument('--ask-password',action='store_true')
    p.add_argument('--timeout',type=float,default=90);a=p.parse_args(argv)
    if not 60<=a.timeout<=180 or not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535:p.error('Timeout must be 60..180 seconds; ports must be 1..65535')
    if a.display_capture and not a.phone_capture:p.error('--display-capture requires --phone-capture')
    print('Plan: upload two verified files to a fresh /ramdisk/delphi-aa-observer_<uuid32>; verify three RAM stock references.')
    print('Native guard interrupts/restarts actual AndroidAuto twice and verifies stock restoration.')
    print('Phone mode: Ethernet stage -> phone for 90 seconds -> reconnect Ethernet to collect.' if a.phone_capture else 'Default mode: 20-second capture, up to about 45 seconds including startup/restoration.')
    if a.display_capture:print('Display capture: observe configuration, focus and discovery bytes without changing endpoints or packets.')
    if not a.run:print('Plan only. Add --run to perform the actual experiment.');return 0
    kind='managed_androidauto_display_observer' if a.display_capture else 'managed_androidauto_observer'
    directory=ROOT/('native/observer/display/release' if a.display_capture else 'native/observer/launch/release')
    files=package_files(directory,kind)
    results=RESULTS+(('display.bin',) if a.display_capture else ())
    if a.phone_capture and 60 not in json.loads((directory/'manifest.json').read_text()).get('capture_profiles',[]):raise ValueError('This package does not support the phone-capture profile; extract the new bundle')
    base=ROOT/'delphi-dump';d.reject_link(base);base.mkdir(exist_ok=True)
    token=uuid.uuid4().hex;remote=validate_remote(REMOTE_PREFIX+token)
    run=base/('_androidauto_observer_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8]);run.mkdir()
    password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    shell=None;cwd_verified=False;namespace_verified=False;blobs={};launched=False;history=[]
    report=dict(kind=kind,display_capture_requested=a.display_capture,remote_directory=remote,passed=False,actions=[],artifacts=[],actual_androidauto_interposition_tested=False,phone_capture_requested=a.phone_capture)
    if a.display_capture:report['display_capture_validated']=False
    def persist():(run/'androidauto-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    def fetch(name,source=None):
        with ftplib.FTP(timeout=a.timeout) as ftp:
            ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I');data=retrieve(ftp,source or remote+'/'+name)
        (run/name).write_bytes(data);blobs[name]=data
        report['artifacts'].append(dict(file=name,bytes=len(data),sha256=sha(data)));return data
    persist()
    try:
        with ftplib.FTP(timeout=a.timeout) as ftp:
            ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I');ftp.mkd(remote)
            for name,data in files.items():
                ftp.storbinary('STOR '+remote+'/'+name,io.BytesIO(data))
                if retrieve(ftp,remote+'/'+name,128*1024)!=data:raise ValueError('Upload readback differs: '+name)
        shell=Shell(a,run);shell.command('cd '+shlex.quote(remote));cwd_verified=True;namespace_verified=True
        for name in NAMES:shell.command('chmod 500 '+name)
        shell.command('pidin -p AndroidAuto arguments > stock-before.txt 2>&1')
        shell.command('pidin -p AndroidAuto mapinfo > stock-before-maps.txt 2>&1')
        for name,(source,_,_) in REFERENCES.items():shell.command('cp '+source+' '+name)
        for name in REFERENCES:shell.command('chmod 644 '+name)
        for name in REFERENCES:verify_reference(name,fetch(name))
        shell.command('cp /etc/procman_core.cfg procman-core.cfg')
        shell.command('chmod 644 procman-core.cfg')
        verify_manager_config(fetch('procman-core.cfg'))
        shell.command('chmod 644 stock-before.txt')
        before_pid=fresh_stock_pid(fetch('stock-before.txt'))
        shell.command('pidin -p AndroidAuto arguments > stock-fresh.txt 2>&1')
        shell.command('chmod 644 stock-fresh.txt')
        pid=fresh_stock_pid(fetch('stock-fresh.txt'))
        if pid!=before_pid:raise ValueError('Stock AndroidAuto changed during preparation')
        shell.command('chmod 500 AndroidAuto.original');launched=True
        command='LD_PRELOAD= ./observer_launch '+shlex.quote(remote)+' '+str(pid)
        if a.phone_capture:
            shell.command(': > launch.txt')
            shell.command('chmod 644 launch.txt')
            started=time.monotonic()
            shell.command(command+' phone > launch.txt 2>&1 & delphi_aa_job=$!')
            def read_ready():
                with ftplib.FTP(timeout=a.timeout) as ftp:
                    ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
                    return retrieve(ftp,remote+'/launch.txt',65536)
            try:ready=wait_for_phone_ready(read_ready,started)
            except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error):
                if not shell.broken:shell.command('wait "$delphi_aa_job"',required=False)
                raise
            (run/'launch-ready.txt').write_bytes(ready)
            report['artifacts'].append(dict(file='launch-ready.txt',bytes=len(ready),sha256=sha(ready)))
            report['phone_handoff_ready']=True
            history.extend(shell.actions);report['actions']=list(history);persist()
            shell.close();shell=None;cwd_verified=False
            print('CAPTURE READY: unplug Ethernet and connect the phone to the car now.',flush=True)
            print('Open your navigation app in Android Auto; wait 90 seconds. Then reconnect Ethernet.',flush=True)
            input('After Ethernet has reconnected, press Enter to collect results: ')
            collect=run/'collection-session';collect.mkdir()
            shell=Shell(a,collect);shell.command('cd '+shlex.quote(remote));cwd_verified=True
        else:shell.command(command+' > launch.txt 2>&1')
    except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:
        report['error']=(type(exc).__name__+': '+str(exc)).replace(password,'[redacted]') if password else str(exc)
    finally:
        if shell and cwd_verified and not shell.broken:
            commands=('pidin -p AndroidAuto arguments > stock-after.txt 2>&1','pidin -p AndroidAuto mapinfo > stock-after-maps.txt 2>&1',
                        'if test -r /dev/shmem/delphi-aa-report-'+token+'.bin; then cp /dev/shmem/delphi-aa-report-'+token+'.bin controller.bin; fi',
                        'if test -r /dev/shmem/delphi-observer-aa-'+token+'.bin; then cp /dev/shmem/delphi-observer-aa-'+token+'.bin observer.bin; fi')
            if a.display_capture:commands+=('if test -r /dev/shmem/delphi-display-'+token+'.bin; then cp /dev/shmem/delphi-display-'+token+'.bin display.bin; fi',)
            for cmd in commands:
                try:shell.command(cmd,required=False)
                except (OSError,EOFError,RuntimeError,ValueError):break
            if not shell.broken:
                for name in results:
                    try:shell.command('if test -f '+name+'; then chmod 644 '+name+'; fi',required=False)
                    except (OSError,EOFError,RuntimeError,ValueError):break
        report['actions']=history+(shell.actions if shell else [])
        if shell:shell.close()
        for name in (tuple(REFERENCES)+('procman-core.cfg',)+results if namespace_verified else ()):
            if name in blobs:continue
            try:
                source=None
                if shell and shell.broken and name in ('controller.bin','observer.bin','display.bin'):
                    source='/dev/shmem/'+{'controller.bin':'delphi-aa-report-','observer.bin':'delphi-observer-aa-','display.bin':'delphi-display-'}[name]+token+'.bin'
                fetch(name,source)
            except (OSError,EOFError) as exc:report['collection_error']=type(exc).__name__;break
            except (ValueError,ftplib.Error) as exc:report['artifacts'].append(dict(file=name,error=type(exc).__name__))
        try:
            report.update(assess(blobs,remote))
            if report['capture_seconds']!=(60 if a.phone_capture else 20):raise ValueError('Controller capture profile differs from requested experiment')
            report['passed']=report['capture_validated'] and 'error' not in report and all(x['exit_code']==0 for x in report['actions'])
            report['actual_androidauto_interposition_tested']=bool(report['passed'] and launched)
            if a.display_capture:
                report['passed']=False
                from decode_androidauto_display import assess as assess_display
                display=assess_display(blobs['display.bin'],report)
                (run/'display-decoded.json').write_text(json.dumps(display,indent=2),encoding='utf-8')
                report.update(display_capture_validated=display['display_capture_validated'],video_configuration_records=display['video_configuration_records'],discovery_records=display['discovery_records'],display_records=display['count'],display_dropped=display['dropped'])
                report['passed']=report['actual_androidauto_interposition_tested'] and display['display_capture_validated']
            if 'decoded_log' in report:(run/'observer-decoded.json').write_text(json.dumps(report.pop('decoded_log'),indent=2))
        except (KeyError,ValueError) as exc:report['validation_error']=str(exc)
        if 'decoded_log' in report:(run/'observer-decoded.json').write_text(json.dumps(report.pop('decoded_log'),indent=2))
        persist()
    print('Saved: '+str(run))
    no_calls=report.get('completed_restored') and not report.get('captured_registration') and 'error' not in report and all(x['exit_code']==0 for x in report['actions'])
    partial_display=a.display_capture and report.get('completed_restored') and report.get('actual_androidauto_interposition_tested')
    print('Result: '+(('DISPLAY CONFIGURATION / DISCOVERY CAPTURE PASS' if a.display_capture else 'ACTUAL ANDROIDAUTO OBSERVER PASS') if report['passed'] else 'RESTORED - DISPLAY CAPTURE PARTIAL; preserve this folder for review' if partial_display else 'RESTORED - NO REGISTRATION CALLS; preserve this folder for review' if no_calls else 'INCOMPLETE / FAILED - preserve this folder for review'))
    return 0 if report['passed'] else 2 if no_calls else 1
if __name__=='__main__':raise SystemExit(main())
