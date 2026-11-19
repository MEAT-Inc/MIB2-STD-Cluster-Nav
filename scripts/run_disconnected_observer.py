"""Observer capture with a phone-disconnected start and explicit disconnected cleanup. Stdlib only."""
from project_console import console_session, log as print, prompt as input, status, progress
import argparse,datetime as dt,ftplib,getpass,hashlib,io,json,re,shlex,struct,time,uuid
from pathlib import Path
import delphi_inventory as d
import run_androidauto_observer as old
from run_observer_smoke import Shell,retrieve
ROOT=Path(__file__).resolve().parents[1]

def wait_for_capture_ready(read_log,started,seconds,limit=25):
    expected=f'LAUNCH_READY capture_seconds={seconds}'.encode()
    while time.monotonic()-started<limit:
        try:data=read_log()
        except (ValueError,ftplib.error_perm):data=b''
        lines=data.replace(b'\r',b'').splitlines()
        if any(x in data for x in (b'LAUNCH_FAILED',b'LAUNCH_REFUSED',b'LAUNCH_COMPLETE',b'LAUNCH_RESTORED')):raise RuntimeError('Native experiment ended before phone handoff')
        if expected in lines:return data
        time.sleep(1)
    raise RuntimeError('No timely native phone-capture readiness; no phone handoff performed')

def package(path,phone=False,factory=False,secondary=False,cluster=False,probe=False):
    m=json.loads((path/'manifest.json').read_text());files={n:(path/n).read_bytes() for n in old.NAMES+ (('nav_snapshot',) if cluster else ())+ (('live_capture',) if probe else ())}
    if m.get('kind')!='disconnected_observer_control_trial':raise ValueError('Wrong disconnected controller package')
    if phone and (m.get('phone_trial_enabled') is not True or (20 if factory else 60) not in m.get('capture_profiles',[])):raise ValueError('Package has not cleared the phone-profile gate')
    if bool(m.get('keyframe_probe_enabled',False))!=probe:raise ValueError('Keyframe-probe package selection differs')
    expected='secondary_endpoint_negotiation' if secondary else 'isolated_endpoint_factory_probe'
    if factory and (m.get('experiment')!=expected or m.get('factory_report_version')!=2 or m.get('factory_contract_revision',0)<4):raise ValueError('Use the current endpoint bundle: configuration-index contract revision4 is required')
    if secondary and not m.get('secondary_stream_enabled'):raise ValueError('Secondary-stream package is not enabled')
    if cluster and (m.get('timing_capture_version')!=1 or not m.get('native_geometry_readonly') or m.get('factory_contract_revision',0)<5):raise ValueError('Use the current cluster preflight bundle')
    for n,b in files.items():
        if len(b)!=m['files'][n]['bytes'] or hashlib.sha256(b).hexdigest()!=m['files'][n]['sha256'] or len(b)>131072:raise ValueError('Package mismatch: '+n)
    return files

def validate_report(data,remote,pending,seconds=20):
    if seconds not in (20,60):raise ValueError('Invalid capture profile')
    if len(data)!=512:raise ValueError('Wrong disconnected-controller report size')
    h=struct.unpack_from('<16I',data);capture,done,authorized,started=struct.unpack_from('<4I',data,256)
    raw=data[96:224]
    if b'\0' not in raw:raise ValueError('Unterminated report root')
    name,padding=raw.split(b'\0',1)
    if name.decode('ascii')!=remote or any(padding) or h[:3]!=(0x314c4144,3,512) or h[15]!=1 or capture!=seconds or done!=1 or any(data[272:]):raise ValueError('Invalid version/root/capture flags')
    if pending:
        if h[3:10]!=(4,0,1,1,0,0,0) or h[11]!=0 or authorized or started:raise ValueError('Capture is not safely pending cleanup')
    elif h[3]!=6 or h[4]!=0 or h[9]!=1 or (authorized,started)!=(1,1):raise ValueError('Explicit cleanup was not verified')
    return dict(version=3,phase=h[3],observed_pid=h[10],restored_pid=h[11],capture_done=done,cleanup_authorized=authorized,cleanup_started=started)

def assess_final(blobs,remote,seconds=20):
    flags=validate_report(blobs['controller.bin'],remote,False,seconds)
    normalized=bytearray(blobs['controller.bin']);struct.pack_into('<I',normalized,4,2);normalized[260:]=bytes(252)
    evidence=dict(blobs);evidence['controller.bin']=bytes(normalized)
    result=old.assess(evidence,remote)
    result.update(disconnected_control_flags=flags,controller_trial_passed=True)
    return result

def assess_factory(data,observed,bias,trace):
    if len(data)!=256:raise ValueError('Incorrect factory report size')
    h=struct.unpack('<64I',data)
    if h[:8]!=(0x31504645,2,256,observed,1,1,1,0) or h[8]!=bias or h[9]!=int(trace['module_base'],16):raise ValueError('Factory profile/process/status failed validation')
    primary=[r for r in trace['records'] if int(r['caller'],16)==bias+0x124e54]
    if len(primary)!=1 or h[10]!=int(primary[0]['receiver'],16) or h[11]!=int(primary[0]['endpoint'],16):raise ValueError('Factory/main registration identities differ')
    if not h[10] or not h[11] or h[10]==h[11] or h[10]%4 or h[11]%4:raise ValueError('Invalid factory object identities')
    if h[12:14]!=h[14:16] or h[16:18]!=(1,1):raise ValueError('Main endpoint/router table changed during isolated construction')
    if h[18:30]!=(0,1,1,1,1,1,1,1,1,1,0,0) or h[30:37]!=(1,1,1,1,1,1,10) or h[37]!=trace['count']+trace['dropped'] or h[38]!=bias+0x124e54 or any(h[39:]):raise ValueError('Factory ownership/configuration/destruction failed validation')
    return dict(isolated_factory_passed=True,native_callback_abi_checked=True,callback_sample_bytes=h[36],trigger_caller=hex(h[38]),video_constructed=True,input_constructed=True,independent_callback_destroyed_once=True,configuration_count=1,primary_unchanged=True,router_table_unchanged=True,candidate_slots_empty_at_probe=h[12:14]==(0,0),slots_reserved=False,secondary_endpoints_registered=False,secondary_stream_received=False)

def assess_secondary(data,raw,observed,factory_router,probe=False):
    if len(data)!=512:raise ValueError('Incorrect secondary report size')
    h=struct.unpack('<128I',data)
    if h[:4]!=(0x31505253,1,512,observed) or h[4]>5 or h[39]!=8388608 or h[42]>2 or ((h[43]!=1 or h[44]>3 or h[45]>h[26] or h[46]>h[26] or h[48]>1 or h[50]>h[26] or h[51]>h[26] or h[52]>h[26] or h[56]>1 or h[53]>1 or any(h[57:])) if probe else any(h[43:])):raise ValueError('Secondary report format/process/limit mismatch')
    if h[8] not in (0,factory_router) or h[16] not in (0,2) or len(raw)>h[39] or h[28]>h[39] or h[29]>h[28]:raise ValueError('Secondary identity/registration/byte accounting invalid')
    if h[16]==2 and (h[12:16]!=(9,10,0,0) or not all(h[9:12]) or len(set(h[9:12]))!=3 or h[40] not in (0,1) or h[42]!=2):raise ValueError('Paired secondary endpoint identities invalid')
    nal_types=sorted({m[1][0]&31 for m in re.finditer(rb'\x00\x00(?:\x00)?\x01(.)',raw,re.S)})
    advertised=h[16]==2 and h[18]>0
    received=bool(advertised and h[20] and h[21] and h[26] and raw)
    accounting=len(raw)==h[28]
    flow=bool(h[26] and h[31]>=h[26] and 0<h[33]<255)
    passed=bool(received and accounting and flow and not h[5] and not h[34])
    state='video_received' if received else 'setup_no_frames' if h[20] else 'awaiting_phone_setup' if advertised else 'not_advertised'
    return dict(secondary_attempt_completed=advertised,secondary_video_received=received,secondary_trial_passed=passed,state=state,native_error=h[5],registered_endpoints=h[16],discovery_calls=h[17],discovery_rewrites=h[18],fallbacks=h[19],setup_calls=h[20],codec_calls=h[21],playback_starts=h[22],playback_stops=h[23],frames=h[26],frame_bytes=h[27],saved_bytes=h[28],codec_saved_bytes=h[29],dropped=h[30],ack_requests=h[31],session=h[32],channel=h[33],io_error=h[34],wire_error=h[35],primary_backup_bytes=h[36],raw_accounting_matches=accounting,private_flow_control_observed=flow,keyframe_probe=dict(refresh_disabled=bool(h[53]),requests=h[44],idr_frames=h[45],last_request_frame=h[46],clock_error=h[47],ipc_attached=bool(h[48]),ipc_error=h[49],ipc_frames=h[50],ipc_dropped=h[51],ipc_malformed=h[52],ipc_consumer_pid=h[55],ipc_closed=bool(h[56])) if probe else None,annexb_nal_types=nal_types,supported_cluster_keys=[23,65536] if h[42]==2 else [],cluster_transport_connected=False)

def assess_discovery_capture(data,observed):
    if len(data)!=24600:raise ValueError('Incorrect discovery capture size')
    magic,pid,original,sent,flags,committed=struct.unpack_from('<6I',data)
    if (magic,pid)!=(0x32534344,observed) or original>8192 or sent>16384 or flags>3 or committed not in (0,1):raise ValueError('Discovery capture identity/bounds invalid')
    if committed and (original<2 or sent<2 or data[24:26]!=b'\x00\x06' or data[8216:8218]!=b'\x00\x06'):raise ValueError('Discovery capture packet header invalid')
    return dict(captured=bool(committed),original_bytes=original,sent_bytes=sent,input_truncated=bool(flags&1),fallback=bool(flags&2))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group();g.add_argument('--run',action='store_true');g.add_argument('--resume',type=Path)
    from live_run_options import add_live_arguments
    add_live_arguments(p)
    p.add_argument('--live-cluster',action='store_true',help='First live maps trial through the owned Nav descriptor; requires factory cluster maps before arm')
    p.add_argument('--live-input','--keyframe-probe',dest='keyframe_probe',action='store_true',help='Validate live secondary frames; waits for phone before capture timer starts')
    p.add_argument('--cluster-preflight',action='store_true',help='Read native geometry and preserve secondary frame boundaries/timestamps')
    p.add_argument('--secondary-stream',action='store_true',help='Register paired endpoints, advertise cluster display and capture secondary video; self-check gated')
    p.add_argument('--factory-probe',action='store_true',help='Isolated native endpoint construction/destruction; no registration or advertisement')
    p.add_argument('--phone-capture',action='store_true',help='Native phone capture: Ethernet -> phone -> Ethernet, explicit disconnected cleanup only')
    p.add_argument('--phone-unplugged',action='store_true',help='Attest phone is physically unplugged before initial launch or resume')
    p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--ask-password',action='store_true');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=90);a=p.parse_args(argv)
    if a.live_seconds is not None and not a.live_cluster:p.error('Live duration options require --live-cluster')
    if a.live_cluster:a.keyframe_probe=True
    if a.keyframe_probe:a.cluster_preflight=True
    if a.cluster_preflight:a.secondary_stream=True
    if a.secondary_stream:
        a.factory_probe=True
        if not a.resume:a.phone_capture=True
    if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 60<=a.timeout<=180:p.error('Invalid ports/timeout')
    if a.factory_probe and a.run and not a.phone_capture:p.error('--factory-probe requires --phone-capture to reach native endpoint initialization')
    if a.phone_capture and a.resume:p.error('Resume uses the profile saved in its summary; omit --phone-capture')
    if (a.run or a.resume) and not a.phone_unplugged:p.error('Requires --phone-unplugged before initial launch or resume')
    print('Capture ends pending; only explicit disconnected cleanup restarts the observed app.')
    if a.live_cluster:print('Live video: '+('until phone disconnect; diagnostic captures stay bounded.' if a.live_seconds==0 else '30-second bounded trial.'))
    if a.phone_capture:print('Phone capture: start unplugged; swap only at CAPTURE READY; remove phone and reconnect Ethernet before cleanup.')
    else:print('Default control trial: phone remains unplugged throughout.')
    if not a.run and not a.resume:print('Plan only. Add --run --phone-unplugged; keep --phone-capture for the phone profile.');return 0
    files=package(ROOT/('native/cluster-bridge/keyframe-probe/release' if a.keyframe_probe else 'native/cluster-bridge/release' if a.cluster_preflight else 'native/secondary-display/release' if a.secondary_stream else 'native/endpoint-factory/release' if a.factory_probe else 'native/observer/disconnect-launch/release'),phone=a.phone_capture,factory=a.factory_probe,secondary=a.secondary_stream,cluster=a.cluster_preflight,probe=a.keyframe_probe);base=ROOT/'delphi-dump'
    for parent in (base,*base.parents):d.reject_link(parent)
    base.mkdir(parents=True,exist_ok=True)
    if a.resume:
        folder=a.resume.resolve()
        if folder.parent!=base.resolve() or not re.fullmatch(r'_disconnect_observer_[0-9_]+_[0-9a-f]{8}',folder.name):raise ValueError('Resume folder is outside this project trial scope')
        report=json.loads((folder/'disconnect-summary.json').read_text());remote=old.validate_remote(report['remote_directory'])
        if report['native_sha256']!=old.sha(files['observer_launch']):raise ValueError('Saved run and native controller differ')
        if bool(report.get('cluster_preflight_requested',False))!=a.cluster_preflight:raise ValueError('Resume requires the saved cluster-preflight selection')
        if bool(report.get('factory_probe_requested',False))!=a.factory_probe:raise ValueError('Resume requires the saved factory-probe selection')
        if bool(report.get('live_cluster_requested',False))!=a.live_cluster:raise ValueError('Resume requires the saved live-cluster selection')
        if bool(report.get('keyframe_probe_requested',False))!=a.keyframe_probe:raise ValueError('Resume requires the saved keyframe-probe selection')
        if bool(report.get('secondary_stream_requested',False))!=a.secondary_stream:raise ValueError('Resume requires the saved secondary-stream selection')
        report['secondary_video_received']=False
        report['secondary_trial_passed']=False
        report['factory_probe_passed']=False
        report['controller_trial_passed']=False
        report['phone_capture_completed']=False
        seconds=report.get('capture_profile_seconds',20)
        if seconds not in (20,60):raise ValueError('Invalid saved capture profile')
        report.setdefault('previous_errors',[]).extend([report.pop(n) for n in ('error','validation_error') if n in report])
        session=folder/('resume-'+uuid.uuid4().hex[:8]);session.mkdir()
    else:
        token=uuid.uuid4().hex;remote=old.validate_remote(old.REMOTE_PREFIX+token);folder=base/('_disconnect_observer_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8]);folder.mkdir();session=folder
        seconds=20 if a.factory_probe else (60 if a.phone_capture else 20)
        report=dict(physical_swap_started=False,live_cluster_requested=a.live_cluster,keyframe_probe_requested=a.keyframe_probe,cluster_preflight_requested=a.cluster_preflight,secondary_stream_requested=a.secondary_stream,secondary_video_received=False,secondary_trial_passed=False,observer_sha256=old.sha(files['libdelphi_observer.so']),factory_probe_requested=a.factory_probe,factory_probe_passed=False,capture_profile_seconds=seconds,phone_capture_requested=a.phone_capture,phone_capture_completed=False,kind='disconnected_observer_control_trial',remote_directory=remote,native_sha256=old.sha(files['observer_launch']),controller_trial_passed=False,cleanup_pending=False,actions=[],artifacts=[])
    token=remote.rsplit('_',1)[1];blobs={f.name:f.read_bytes() for f in folder.iterdir() if f.is_file() and f.suffix in ('.txt','.bin','.reference','.original','.cfg')}
    shell=None;cwd=False;authorized=False;history=[];password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    bridge=None
    if a.live_cluster:
        from live_cluster_bridge import LiveBridge
        bridge=LiveBridge(ROOT,a,folder,report,password)
        report['live_seconds']=bridge.state['live_seconds']
    def persist():(folder/'disconnect-summary.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    def fetch(name):
        with ftplib.FTP(timeout=a.timeout) as ftp:
            progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
            ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
            if name in ('secondary.h264','live-copy.h264','nav-live-snapshot.jsonl','nav-live-errors.txt'):
                data=bytearray()
                def save_video(block):
                    if len(data)+len(block)>8388608:raise ValueError('Secondary capture exceeds8MiB')
                    data.extend(block)
                ftp.retrbinary('RETR '+remote+'/'+name,save_video);b=bytes(data)
            else:b=retrieve(ftp,remote+'/'+name)
        (folder/name).write_bytes(b);blobs[name]=b;report['artifacts']=[x for x in report['artifacts'] if x.get('file')!=name]
        report['artifacts'].append(dict(file=name,bytes=len(b),sha256=old.sha(b)));return b
    def command(cmd,required=True):return shell.command(cmd,required=required)
    def snapshot_native(label,pid):
        import cluster_preflight as cp
        dest='nav-'+label+'.json'
        code=command('LD_PRELOAD= ./nav_snapshot '+str(pid)+' > '+dest+' 2> nav-'+label+'-errors.txt',required=False)
        if code:
            try:fetch('nav-'+label+'-errors.txt')
            except (OSError,ValueError,ftplib.Error):pass
            raise ValueError('Read-only native geometry snapshot refused: '+str(code))
        command('chmod 644 '+dest);return cp.assess_nav(fetch(dest),pid)
    def copy_report(source,dest):
        command('cp '+source+' '+dest);command('chmod 644 '+dest);return fetch(dest)
    persist()
    try:
        if bridge and not a.resume:
            shell=Shell(a,session)
            from radio_ram import prepare_space
            report['ram_preflight']=prepare_space(shell,a,password,ROOT/'native/cluster-bridge/live-output/release/cleanup-plan.json',folder/'ram-preflight.json',expected_sha=bridge.manifest['cleanup_plan_sha256']);persist()
        with ftplib.FTP(timeout=a.timeout) as ftp:
            progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
            ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
            if not a.resume:
                ftp.mkd(remote)
                for name,b in files.items():
                    status('Uploading and verifying payload: '+name)
                    ftp.storbinary('STOR '+remote+'/'+name,io.BytesIO(b))
                    if retrieve(ftp,remote+'/'+name)!=b:raise ValueError('Upload readback mismatch: '+name)
            elif retrieve(ftp,remote+'/observer_launch')!=files['observer_launch']:raise ValueError('Staged controller changed; cleanup not attempted')
        if shell is None:shell=Shell(a,session)
        command('cd '+shlex.quote(remote));cwd=True
        if not a.resume:
            for name in old.NAMES:command('chmod 500 '+name)
            command('pidin -p AndroidAuto arguments > stock-before.txt 2>&1');command('chmod 644 stock-before.txt');before=old.fresh_stock_pid(fetch('stock-before.txt'))
            for name,(src,_,_) in old.REFERENCES.items():command('cp '+src+' '+name);command('chmod 644 '+name);old.verify_reference(name,fetch(name))
            command('cp /etc/procman_core.cfg procman-core.cfg');command('chmod 644 procman-core.cfg');old.verify_manager_config(fetch('procman-core.cfg'))
            command('pidin -p AndroidAuto arguments > stock-fresh.txt 2>&1');command('chmod 644 stock-fresh.txt');pid=old.fresh_stock_pid(fetch('stock-fresh.txt'))
            if pid!=before:raise ValueError('Stock PID changed before staging')
            if bridge:bridge.prepare(command,fetch,copy_report)
            if a.cluster_preflight:
                import cluster_preflight as cp
                print('Before the phone test, display the VW factory navigation map in the instrument cluster.',flush=True)
                if not bridge:input('Keep the phone unplugged and Ethernet connected. Press Enter when the native cluster map is visible (or if unavailable): ')
                command('pidin -p NavigationServer arguments > nav-before-arguments.txt');command('chmod 644 nav-before-arguments.txt')
                native_pid=cp.nav_pid(fetch('nav-before-arguments.txt'))
                if bridge:cp.verify_navigation(bridge.navigation_image())
                else:
                    command('cp /extbin/apps/bin/NavigationServer NavigationServer.reference');command('chmod 644 NavigationServer.reference');cp.verify_navigation(fetch('NavigationServer.reference'))
                command('chmod 500 nav_snapshot');report['native_before']=snapshot_native('before',native_pid);persist()
                if not report['native_before']['active_geometry_observed']:print('Native encoder geometry is inactive; preserving that result and continuing timing capture.',flush=True)
            command('chmod 500 AndroidAuto.original')
            launch='LD_PRELOAD= ./observer_launch start-disconnected '+shlex.quote(remote)+' '+str(pid)
            report['native_launch_requested']=True;persist()
            if report.get('phone_capture_requested'):
                command(': > start.txt');command('chmod 644 start.txt');started=time.monotonic()
                command(launch+(' phone' if seconds==60 else '')+' > start.txt 2>&1 & delphi_aa_job=$!')
                def read_ready():
                    with ftplib.FTP(timeout=min(a.timeout,10)) as ftp:
                        progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
                        ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I');return retrieve(ftp,remote+'/start.txt',65536)
                ready=wait_for_capture_ready(read_ready,started,seconds)
                (folder/'launch-ready.txt').write_bytes(ready)
                report['phone_handoff_ready']=True
                report['artifacts'].append(dict(file='launch-ready.txt',bytes=len(ready),sha256=old.sha(ready)))
                if a.keyframe_probe:
                    candidates=set(re.findall(rb'LAUNCH_OBSERVED pid=(\d+)',ready))
                    if len(candidates)!=1:raise ValueError('Live source process identity is ambiguous')
                    source_pid=int(next(iter(candidates)))
                    if bridge:bridge.phone_ready(command,fetch,copy_report,source_pid)
                    else:
                        command('chmod 500 live_capture')
                        command('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./live_capture --detach '+token+' '+str(source_pid)+' 30 '+str(native_pid)+' > live-start.txt 2>&1')
                    from review_live_input import reader_report
                    until=time.monotonic()+10
                    while True:
                        source='/dev/shmem/delphi-live-report-'+token+'.bin'
                        if command('test -r '+source,required=False)==0:
                            reader_bytes=copy_report(source,'live-reader-ready.bin')
                            if len(reader_bytes)!=512:raise ValueError('Live reader ready size')
                            if struct.unpack_from('<I',reader_bytes,20)[0]==0:
                                if time.monotonic()>=until:raise TimeoutError('Live reader bootstrap not committed')
                                time.sleep(.2);continue
                            ready_reader=reader_report(reader_bytes,source_pid,consumer_pid=bridge.state['observed_pid'] if bridge else None,allow_unbound=bool(bridge))
                            if ready_reader['state']==4:
                                report['live_reader_failure']=ready_reader;persist()
                                if bridge:bridge.state['output_before_handoff_error']=__import__('live_cluster_bridge').assess_output(bridge.report('live-nav-handoff-error.bin'),bridge.state['observed_pid']);bridge.save()
                                raise RuntimeError('Live input stopped before handoff; native error '+str(ready_reader['error'])+' (32=EPIPE)')
                            if ready_reader['state'] in (1,2):break
                        if time.monotonic()>=until:raise TimeoutError('Live input reader not ready; phone handoff cancelled')
                        time.sleep(.2)
                    report['live_reader_ready']=ready_reader
                    report['native_live_sampler_requested']=not bool(bridge)
                history.extend(shell.actions);report['actions']=list(history);persist();shell.close();shell=None;cwd=False
                report['physical_swap_started']=True;persist()
                print('CAPTURE READY: swap Ethernet for the phone now and start Android Auto navigation.',flush=True)
                handoff_started=time.monotonic()
                input(('Extended live output has no elapsed-time cutoff. After your test, unplug the phone, reconnect Ethernet, wait for its link, then press Enter: ' if bridge and bridge.state.get('live_seconds')==0 else 'Once navigation starts'+(', start a route and run it about12 seconds' if a.keyframe_probe else ', start a route and run it about10 seconds' if a.secondary_stream else '')+', unplug the phone, reconnect Ethernet, wait for its link, then press Enter: '))
                report['host_handoff_elapsed_seconds']=round(time.monotonic()-handoff_started,3)
                persist();collection=folder/'collection-session';collection.mkdir()
                shell=Shell(a,collection);command('cd '+shlex.quote(remote));cwd=True
            else:
                code=command(launch+' > start.txt 2>&1',required=False)
                if code!=2:raise ValueError('Expected a pending-cleanup exit, got '+str(code))
        for name in old.REFERENCES:old.verify_reference(name,blobs[name])
        old.verify_manager_config(blobs['procman-core.cfg'])
        command('chmod 644 start.txt');fetch('start.txt')
        final_exists=command('test -f /dev/shmem/delphi-aa-final-'+token+'.bin',required=False)==0
        if not final_exists:
            pending_source='/dev/shmem/delphi-aa-report-'+token+'.bin'
            deadline=time.monotonic()+seconds+10
            while command('test -r '+pending_source,required=False)!=0:
                if time.monotonic()>=deadline:raise TimeoutError('Native pending checkpoint not ready; cleanup not attempted')
                time.sleep(1)
            pending=copy_report(pending_source,'controller-pending.bin')
            report['pending_state']=validate_report(pending,remote,True,seconds);report['cleanup_pending']=True;persist()
        print('Capture has not authorized any interruption. Keep Ethernet connected and the phone physically unplugged.',flush=True)
        if bridge:bridge.confirm_automatic_factory_return()
        if input('Type PHONE REMOVED to request the explicit disconnected-only cleanup (anything else leaves it pending): ').strip()!='PHONE REMOVED':
            print('Cleanup remains pending. Use --resume "'+str(folder)+'" --phone-unplugged'+(' --live-cluster' if a.live_cluster else ' --cluster-preflight' if a.cluster_preflight else ' --secondary-stream' if a.secondary_stream else ' --factory-probe' if a.factory_probe else '')+' later.');return 2
        authorized=True;report['cleanup_requested_host_utc']=dt.datetime.now(dt.timezone.utc).isoformat();persist()
        command('if test ! -f cleanup.txt; then : > cleanup.txt; fi');command('chmod 644 cleanup.txt')
        code=command('LD_PRELOAD= ./observer_launch cleanup-disconnected '+shlex.quote(remote)+' >> cleanup.txt 2>&1',required=False)
        fetch('cleanup.txt')
        if code:raise ValueError('Disconnected cleanup refused/incomplete: '+str(code))
        copy_report('/dev/shmem/delphi-aa-final-'+token+'.bin','controller.bin')
        copy_report('/dev/shmem/delphi-observer-aa-'+token+'.bin','observer.bin')
        command('pidin -p AndroidAuto arguments > stock-after.txt 2>&1');command('chmod 644 stock-after.txt');fetch('stock-after.txt')
        combined=blobs['start.txt']+b'\n'+blobs['cleanup.txt'];blobs['launch.txt']=combined;(folder/'launch.txt').write_bytes(combined)
        report.update(assess_final(blobs,remote,seconds));report['cleanup_pending']=False
        report['phone_capture_completed']=bool(report.get('phone_capture_requested') and report.get('captured_registration'))
        if a.factory_probe:
            copy_report('/dev/shmem/delphi-endpoint-factory-'+token+'.bin','factory.bin')
            report['factory_probe']=assess_factory(blobs['factory.bin'],report['observed_pid'],report['executable_load_bias'],report['decoded_log'])
            report['factory_probe_passed']=True
        if a.secondary_stream:
            copy_report('/dev/shmem/delphi-secondary-report-'+token+'.bin','secondary.bin')
            copy_report('/dev/shmem/delphi-secondary-video-'+token+'.h264','secondary.h264')
            copy_report('/dev/shmem/delphi-secondary-discovery-'+token+'.bin','discovery.bin')
            report['secondary_discovery']=assess_discovery_capture(blobs['discovery.bin'],report['observed_pid'])
            state=assess_secondary(blobs['secondary.bin'],blobs['secondary.h264'],report['observed_pid'],struct.unpack_from('<I',blobs['factory.bin'],40)[0],probe=a.keyframe_probe)
            report.update(secondary=state,secondary_video_received=state['secondary_video_received'],secondary_trial_passed=state['secondary_trial_passed'])
        if a.cluster_preflight:
            from secondary_timing import assess_timing
            import cluster_preflight as cp
            copy_report('/dev/shmem/delphi-secondary-timing-'+token+'.bin','timing.bin')
            report['timing']=assess_timing(blobs['timing.bin'],blobs['secondary.h264'],report['observed_pid'],report['secondary'],probe=a.keyframe_probe)
            if a.keyframe_probe:
                from review_secondary_keyframes import assess_probe
                from review_live_input import reader_report,assess_live,assess_native_geometry
                report['keyframe_control']=assess_probe(blobs['timing.bin'],blobs['secondary.h264'],report['observed_pid'],report['secondary'])
                until=time.monotonic()+(36 if bridge else 10)
                while True:
                    native_reader=reader_report(copy_report('/dev/shmem/delphi-live-report-'+token+'.bin','live-reader.bin'),report['observed_pid'])
                    if native_reader['state'] in (3,4):break
                    if time.monotonic()>=until:raise TimeoutError('Live input reader still pending')
                    time.sleep(.2)
                for source,dest in (('video-'+token+'.h264','live-copy.h264'),('timing-'+token+'.bin','live-copy-timing.bin'),*(() if bridge else (('nav-'+token+'.jsonl','nav-live-snapshot.jsonl'),('nav-'+token+'.errors.txt','nav-live-errors.txt')))):
                    copy_report('/dev/shmem/delphi-live-'+source,dest)
                report['live_input']=assess_live(blobs['live-reader.bin'],blobs['live-copy-timing.bin'],blobs['live-copy.h264'],blobs['timing.bin'],blobs['secondary.h264'],report['observed_pid'],report['secondary'])
                if bridge:
                    report['live_output']=bridge.collect(command,fetch,copy_report)
                    output=report['live_output'];reader=report['live_input']['reader']
                    if output.get('profile_version')==6 and (output['total_input_frames']!=reader.get('total_input_frames') or output['total_input_bytes']!=reader.get('total_input_bytes') or output['live_seconds']!=bridge.state['live_seconds'] or reader.get('live_seconds')!=bridge.state['live_seconds'] or output['diagnostic_prefix_truncated']!=reader.get('diagnostic_prefix_truncated')):raise ValueError('Native stream totals or requested run mode differ from reader report')
                    from live_cluster_bridge import output_delivered
                    connected=output_delivered(report['live_output'],report['observed_pid'],report['live_input']['frames'])
                    for item in ('live_input','secondary','keyframe_control'):
                        if item in report:report[item]['cluster_transport_connected']=connected
                    report['cluster_display_confirmed']=bool(bridge.state.get('live_maps_seen'))
                    from review_route_policy import assess_route_policy
                    report['route_policy']=assess_route_policy(copy_report('/dev/shmem/delphi-route-policy-'+token+'.bin','route-policy.bin'),report['observed_pid'],bridge.state['observed_pid'])
                else:report['live_native_geometry']=assess_native_geometry(blobs['nav-live-snapshot.jsonl'],report['native_before']['pid'],report['timing']['records_detail'])
                persist()
            command('pidin -p NavigationServer arguments > nav-after-arguments.txt');command('chmod 644 nav-after-arguments.txt');current_nav=cp.nav_pid(fetch('nav-after-arguments.txt'))
            before_nav=report['native_before']
            report['navigation_pid_unchanged']=current_nav==before_nav['pid']
            report['native_after']=snapshot_native('after',current_nav)
            report['navigation_identity_unchanged']=report['navigation_pid_unchanged'] and report['native_after']['start_time']==before_nav['start_time'] and report['native_after']['parent']==before_nav['parent']
            report['cluster_preflight_passed']=bool(report['timing']['complete'] and before_nav['active_geometry_observed'] and report['navigation_identity_unchanged'])
        (folder/'observer-decoded.json').write_text(json.dumps(report.pop('decoded_log'),indent=2))
    except (OSError,EOFError,ValueError,RuntimeError,KeyError,ftplib.Error) as exc:report['error']=(type(exc).__name__+': '+str(exc)).replace(password,'[redacted]') if password else str(exc)
    finally:
        # Always preserve available phase reports and current PID after errors;
        # these commands never authorize cleanup or signal an application.
        if shell and cwd and not shell.broken:
            for source,dest in (('/dev/shmem/delphi-aa-report-'+token+'.bin','controller-pending.bin'),('/dev/shmem/delphi-aa-final-'+token+'.bin','controller.bin'))+((('/dev/shmem/delphi-endpoint-factory-'+token+'.bin','factory.bin'),) if a.factory_probe else ())+((('/dev/shmem/delphi-secondary-report-'+token+'.bin','secondary.bin'),('/dev/shmem/delphi-secondary-video-'+token+'.h264','secondary.h264'),('/dev/shmem/delphi-secondary-discovery-'+token+'.bin','discovery.bin')) if a.secondary_stream else ())+((('/dev/shmem/delphi-secondary-timing-'+token+'.bin','timing.bin'),) if a.cluster_preflight else ()):
                try:
                    command('if test -r '+source+'; then cp '+source+' '+dest+'; chmod 644 '+dest+'; fi',required=False)
                    if dest not in blobs:fetch(dest)
                except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:report.setdefault('diagnostic_errors',[]).append(dict(file=dest,error=type(exc).__name__))
            try:
                command('pidin -p AndroidAuto arguments > stock-current.txt 2>&1',required=False);command('chmod 644 stock-current.txt',required=False);fetch('stock-current.txt')
            except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:report.setdefault('diagnostic_errors',[]).append(dict(file='stock-current.txt',error=type(exc).__name__))
        if bridge and shell and cwd and not shell.broken and not report.get('physical_swap_started',False) and a.phone_unplugged and report.get('native_launch_requested') and not report.get('controller_trial_passed'):
            try:
                from finish_live_session import cleanup_aa
                report['aa_restoration']=cleanup_aa(command,copy_report,fetch,remote,seconds);report['aa_restoration_verified']=True;report['cleanup_pending']=False;authorized=True;report['cleanup_authorization']='initial_phone_unplugged_before_any_handoff'
            except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:report['aa_cleanup_error']=str(exc);report['cleanup_pending']=True
        if bridge and shell and not shell.broken:
            from live_cluster_bridge import cleanup_allowed
            if cleanup_allowed(report.get('physical_swap_started',False),authorized,report.get('cleanup_pending',False)):
                try:bridge.cleanup(command,fetch,copy_report)
                except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as exc:report['live_bridge_cleanup_error']=str(exc)
            report['live_bridge']=bridge.state;bridge.save()
        if shell:
            report['actions']=history+shell.actions;shell.close()
        report['operator_cleanup_confirmed']=authorized;persist()
    ok=report['controller_trial_passed'] and (not report.get('phone_capture_requested') or report.get('phone_capture_completed',False)) and (not a.factory_probe or report.get('factory_probe_passed',False)) and (not a.secondary_stream or report.get('secondary_trial_passed',False))
    if a.cluster_preflight:ok=ok and report.get('cluster_preflight_passed',False)
    if a.keyframe_probe:
        ok=bool(ok and 'error' not in report and report.get('live_input',{}).get('owned_live_copy_verified',False))
        print('Live frame copy: '+('VERIFIED' if report.get('live_input',{}).get('owned_live_copy_verified') else 'NOT VERIFIED; return this collection for review.'))
    if bridge:
        from live_cluster_bridge import output_delivered
        v=report.get('live_output',{});ok=bool(ok and not report.get('route_policy',{}).get('release_errors',0) and bridge.state.get('restoration_verified') and bridge.state.get('factory_maps_restored') and bridge.state.get('live_maps_seen') and output_delivered(v,report.get('observed_pid'),report.get('live_input',{}).get('frames',0)))
        print('Live cluster output: '+str(v.get('total_input_frames',v.get('frames',0)))+' streamed frames; '+str(v.get('packets',0))+' packets; native error='+str(v.get('error',0))+'; active closes='+str(v.get('active_closes',0)))
        if v.get('profile_version',0)>=3:print('Video startup: '+str(v.get('bootstrap_frames',0))+' repeated keyframes; '+str(v.get('source_frames_emitted',0))+' original frames emitted; added delay='+str(v.get('startup_delay_ms',0))+'ms; buffer overflows='+str(v.get('startup_overflows',0)))
        if bridge.manifest.get('automatic_factory_return_required'):
            from live_cluster_bridge import native_factory_return_verified
            report['automatic_factory_return_verified']=bool(bridge.state.get('factory_automatic_return_observed') and bridge.state.get('factory_automatic_return_before_manual_toggle') and native_factory_return_verified(v));ok=bool(ok and report['automatic_factory_return_verified']);persist()
            print('Automatic factory compass/map return before manual toggle: '+str(report['automatic_factory_return_verified']))
        policy=report.get('route_policy',{})
        if policy:print('Route presentation trial: held='+str(policy.get('held',0))+'; released='+str(policy.get('released',0))+'; cancelled='+str(policy.get('cancelled',0))+'; release errors='+str(policy.get('release_errors',0)))
        request=policy.get('last_request',{})
        if request:print('Route request: native focus='+str(request['native_focus'])+'; decision='+request['decision']+'; target='+str(request['app'])+'/'+str(request['thread'])+'; Nav status='+str(request['nav_status']))
        if bridge.manifest.get('route_disconnect_restore'):
            from review_route_policy import disconnect_verified
            report['disconnect_restoration_verified']=disconnect_verified(policy);ok=bool(ok and report['disconnect_restoration_verified']);persist()
            disconnect_state=policy.get('disconnect',{});print('Phone disconnect: stopped events='+str(disconnect_state.get('stopped_events',0))+'; discarded pending='+str(disconnect_state.get('pending_discarded',0))+'; native resets='+str(disconnect_state.get('native_focus_resets',0))+'; late callbacks discarded='+str(disconnect_state.get('late_projected_discarded',0))+'; verified='+str(report['disconnect_restoration_verified']))
        if bridge.state.get('cleanup_pending'):print('Nav cleanup pending. Keep the phone unplugged; resume this SAME bundle: python scripts/run_disconnected_observer.py --resume "'+str(folder)+'" --live-cluster --phone-unplugged')
    if a.secondary_stream and 'secondary' in report:print('Secondary state: '+report['secondary']['state']+'; frames='+str(report['secondary']['frames']))
    if 'error' in report:print('Result: '+report['error'])
    print('Saved: '+str(folder))
    print(('Live maps confirmed in the cluster.' if bridge else 'Trial complete; the physical cluster transport is not connected.') if ok else 'Partial trial or pending cleanup: return this folder for review.')
    return 0 if ok else 2
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
