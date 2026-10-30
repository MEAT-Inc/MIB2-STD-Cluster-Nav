"""Stage a bounded passive on-unit trace reader, swap USB to phone, then collect. Stdlib only."""
import argparse,datetime as dt,ftplib,getpass,hashlib,io,json,re,shlex,time,uuid
from pathlib import Path
import delphi_inventory as d
from run_observer_smoke import Shell,retrieve
from run_androidauto_observer import fresh_stock_pid
from collect_trace_tcp import port_state
ROOT=Path(__file__).resolve().parents[1]
PREFIX='/ramdisk/delphi-trace-reader_'
def sha(b):return hashlib.sha256(b).hexdigest()
def valid_remote(path):
    if not re.fullmatch(re.escape(PREFIX)+r'[0-9a-f]{32}',path):raise ValueError('Invalid trace RAM directory')
    return path
def launch_command(remote):
    return 'LD_PRELOAD= ./trace_reader '+shlex.quote(valid_remote(remote))+' > trace-job.txt 2>&1 & delphi_trace_job=$!'

def package(directory):
    manifest=json.loads((directory/'manifest.json').read_text());blob=(directory/'trace_reader').read_bytes()
    if manifest.get('kind')!='passive_loopback_trace_reader' or len(blob)!=manifest['bytes'] or sha(blob)!=manifest['sha256'] or len(blob)>131072:raise ValueError('Unverified trace reader package')
    return blob
def ready(read,started):
    while time.monotonic()-started<12:
        try:data=read()
        except (OSError,ValueError,ftplib.Error):data=b''
        if b'TRACE_READER_REPORT' in data:raise ValueError('Reader ended before phone handoff')
        m=re.search(rb'^TRACE_READER_READY pid=(\d+) seconds=180 max_bytes=16777216\r?$',data,re.M)
        if m:
            pid=int(m[1])
            if not 0<pid<=0x7fffffff:raise ValueError('Invalid reader PID')
            return pid,data
        time.sleep(.5)
    raise ValueError('No native reader readiness; no phone handoff')
def assess_report(data,raw,pid):
    match=re.fullmatch(rb'TRACE_READER_REPORT version=1 pid=(\d+) seconds=180 limit=16777216 bytes=(\d+) elapsed_ms=(\d+) reason=(duration|byte_limit|peer_closed|error) rc=(0|2) error=(\d+)\r?\n',data)
    if not match:raise ValueError('Reader final report missing/malformed')
    actual,size,elapsed,reason,rc,error=match.groups();size=int(size);elapsed=int(elapsed)
    if int(actual)!=pid or size!=len(raw) or size>16777216:raise ValueError('Reader PID or byte accounting mismatch')
    if reason==b'duration' and elapsed<180000:raise ValueError('Native duration report is too short')
    if reason==b'byte_limit' and size!=16777216:raise ValueError('Native byte-limit accounting is impossible')
    logger_completed=int(rc)==0 and int(error)==0 and size>0 and reason in (b'duration',b'byte_limit')
    complete=logger_completed and reason==b'duration'
    return dict(bytes=size,elapsed_ms=elapsed,reason=reason.decode(),native_error=int(error),logger_completed=logger_completed,capture_complete=complete)
def door_step(report,started):
    answer=input('With the phone connected, is Android Auto displaying normally now? [y/n/u]: ').strip().lower()
    report['phone_normal_before_door']=answer
    if answer!='y':report['door_action_skipped']='phone_view_not_confirmed_normal';return
    if time.monotonic()-started>90:report['door_action_skipped']='not_enough_capture_time';return
    print('Keep the vehicle parked and ignition on. Waiting 30 seconds before the door action.',flush=True)
    time.sleep(30)
    if time.monotonic()-started>120:report['door_action_skipped']='not_enough_capture_time';return
    input('Now open and close the driver door ONCE, then press Enter immediately: ')
    elapsed=round(time.monotonic()-started,3)
    report['door_action_host_elapsed_seconds']=elapsed
    report['door_action_host_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    report['door_action_within_planned_window']=elapsed<=120
    print('Observe whether Android Auto goes black and returns. Keep the phone connected until collection time; do not reboot just to restore the view before collecting.',flush=True)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--scenario',choices=('baseline','door'),default='baseline');p.add_argument('--ignition',choices=('on','off','unknown'),default='unknown');p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--ask-password',action='store_true');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=20);a=p.parse_args(argv)
    if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 0<a.timeout<=60:p.error('Invalid port or timeout')
    if a.scenario=='door' and a.ignition!='on':p.error('Door scenario requires --ignition on; keep the vehicle parked')
    print('Passive loopback logger only: 180 seconds / 16 MiB. No AndroidAuto restart, observer or logging configuration change.')
    if not a.run:print('Plan only. Add --run; Ethernet stage -> phone for 210 seconds -> Ethernet collection.');return 0
    blob=package(ROOT/'native/trace-reader/release');base=ROOT/'delphi-dump'
    for parent in (base,*base.parents):d.reject_link(parent)
    base.mkdir(exist_ok=True);token=uuid.uuid4().hex;remote=valid_remote(PREFIX+token);folder=base/('_phone_trace_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8]);folder.mkdir()
    password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    report=dict(kind='passive_phone_trace',scenario=a.scenario,ignition=a.ignition,remote_directory=remote,reader_sha256=sha(blob),capture_complete=False,phone_interval_verified=False,phone_interval_coverage='unverified_manual_usb_handoff',display_recovery_verified=False,actions=[],artifacts=[])
    shell=None;cwd=False;namespace=False;history=[];blobs={};reader_pid=None
    def persist():(folder/'phone-trace-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    def fetch(name,limit=16777216):
        # Stream locally so a dropped connection preserves received bytes.
        part=folder/(name+'.partial');deadline=time.monotonic()+120;data=bytearray()
        try:
            with part.open('xb') as out:
                with ftplib.FTP(timeout=a.timeout) as ftp:
                    ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
                    def save(block):
                        if time.monotonic()>deadline:raise TimeoutError('Host transfer exceeded 120-second budget')
                        if len(data)+len(block)>limit:raise ValueError('Transfer exceeds fixed byte limit')
                        out.write(block);out.flush();data.extend(block)
                    ftp.retrbinary('RETR '+remote+'/'+name,save)
                if not data:raise ValueError('Empty transfer')
        except BaseException:
            if part.exists():report['artifacts'].append(dict(file=part.name,bytes=len(data),sha256=sha(data),status='partial'))
            raise
        part.replace(folder/name);blobs[name]=bytes(data);report['artifacts'].append(dict(file=name,bytes=len(data),sha256=sha(data)));return blobs[name]
    persist()
    try:
        with ftplib.FTP(timeout=a.timeout) as ftp:
            ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I');ftp.mkd(remote);namespace=True;ftp.storbinary('STOR '+remote+'/trace_reader',io.BytesIO(blob))
            if retrieve(ftp,remote+'/trace_reader',131072)!=blob:raise ValueError('Reader upload verification failed')
        shell=Shell(a,folder);shell.command('cd '+shlex.quote(remote));cwd=True
        shell.command('pidin -p AndroidAuto arguments > stock-before.txt 2>&1');shell.command('pidin -p TraceServer fds > trace-before.txt 2>&1');shell.command('pidin -p AndroidAuto mapinfo > maps-before.txt 2>&1')
        for name in ('stock-before.txt','trace-before.txt','maps-before.txt'):shell.command('chmod 644 '+name)
        before=fresh_stock_pid(fetch('stock-before.txt'));fds=fetch('trace-before.txt');maps=fetch('maps-before.txt')
        if b'observer' in maps.lower() or port_state(fds,'ESTABLISHED') or not port_state(fds,'LISTEN'):raise ValueError('Observer mapping/trace client present, or trace listener unverified; logger not started')
        report['stock_pid_before']=before
        shell.command('chmod 500 trace_reader');shell.command(': > trace-job.txt');shell.command('chmod 644 trace-job.txt')
        started=time.monotonic();shell.command(launch_command(remote))
        def read_ready():
            with ftplib.FTP(timeout=a.timeout) as ftp:
                ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I');return retrieve(ftp,remote+'/trace-job.txt',4096)
        reader_pid,first=ready(read_ready,started)
        if reader_pid==before:raise ValueError('Reader PID aliases AndroidAuto')
        report.update(reader_pid=reader_pid,phone_handoff_ready=True,logger_ready_host_utc=dt.datetime.now(dt.timezone.utc).isoformat())
        (folder/'reader-ready.txt').write_bytes(first);report['artifacts'].append(dict(file='reader-ready.txt',bytes=len(first),sha256=sha(first)))
        history.extend(shell.actions);report['actions']=history.copy();persist();shell.close();shell=None;cwd=False
        print('LOGGER READY: swap Ethernet for the phone now. Open Android Auto navigation.',flush=True)
        if a.scenario=='baseline':print('Keep the driver door CLOSED for this baseline.',flush=True)
        print('Leave the phone connected for 210 seconds. The logger stops itself; AndroidAuto is never restarted.',flush=True)
        handoff_started=time.monotonic()
        if a.scenario=='door':door_step(report,handoff_started);persist()
        input('After at least 210 seconds TOTAL since LOGGER READY, reconnect Ethernet, wait for its link, and press Enter: ')
        report['host_handoff_elapsed_seconds']=round(time.monotonic()-handoff_started,3)
        answer=input('Before unplugging the phone, was Android Auto displaying normally? [y/n/u]: ').strip().lower()
        report['phone_view_observation']={'y':'normal','n':'black','u':'unknown'}.get(answer,'unknown')
        report['door_opened']=input('Did the driver door open during that interval? [y/n/u]: ').strip().lower()
        if a.scenario=='door':
            report['black_after_door']=input('Did Android Auto go black after the door action? [y/n/u]: ').strip().lower()
            report['recovered_without_reboot']=input('If it went black, did it return without a head-unit reboot? [y/n/u]: ').strip().lower()
        collection=folder/'collection-session';collection.mkdir();shell=Shell(a,collection);shell.command('cd '+shlex.quote(remote));cwd=True
    except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:report['error']=(type(exc).__name__+': '+str(exc)).replace(password,'[redacted]') if password else str(exc)
    finally:
        if shell and cwd and not shell.broken:
            for cmd in ('pidin -p AndroidAuto arguments > stock-after.txt 2>&1','pidin -p AndroidAuto mapinfo > maps-after.txt 2>&1','pidin -p TraceServer fds > trace-after.txt 2>&1','chmod 644 stock-after.txt maps-after.txt trace-after.txt','if test -f trace.bin; then chmod 644 trace.bin; fi','if test -f trace-report.txt; then chmod 644 trace-report.txt; fi'):
                try:shell.command(cmd,required=False)
                except (OSError,EOFError,RuntimeError,ValueError):break
        report['actions']=history+(shell.actions if shell else [])
        if shell:shell.close()
        if namespace:
            for name in ('trace-job.txt','trace-report.txt','trace.bin','stock-after.txt','maps-after.txt','trace-after.txt'):
                try:fetch(name)
                except (OSError,EOFError,ValueError,ftplib.Error) as exc:report['artifacts'].append(dict(file=name,error=type(exc).__name__))
        try:
            report['stock_pid_after']=fresh_stock_pid(blobs['stock-after.txt']);report['stock_pid_unchanged']=report['stock_pid_after']==report['stock_pid_before']
            if reader_pid is not None:report.update(assess_report(blobs['trace-report.txt'],blobs['trace.bin'],reader_pid))
            if report.get('host_handoff_elapsed_seconds',0)<180:report['capture_complete']=False;report['handoff_wait_too_short']=True
            if not report['stock_pid_unchanged'] or 'error' in report or any(x['exit_code']!=0 for x in report['actions']):report['capture_complete']=False
        except (ValueError,KeyError) as exc:report['validation_error']=str(exc)
        persist()
    print('Saved: '+str(folder));print('Return the whole folder. Capture completion is not proof of display recovery or a cluster map.')
    return 0 if report['capture_complete'] else 2
if __name__=='__main__':raise SystemExit(main())
