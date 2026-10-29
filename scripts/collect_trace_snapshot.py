"""Copy bounded DTS trace snapshots/configuration for offboard analysis. Stdlib only.
No streams are consumed, logging settings changed, or head-unit processes restarted.
"""
import argparse,datetime as dt,ftplib,getpass,hashlib,json,re,uuid
from pathlib import Path
from collect_observer_preflight import inventory
import delphi_inventory as d
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=(('kernel','pidin info'),('processes','pidin arguments'),('trace-arguments','pidin -p TraceServer arguments'),('trace-environment','pidin -p TraceServer environment'),('trace-fds','pidin -p TraceServer fds'),('trace-maps','pidin -p TraceServer mapinfo'),('trace-memory','ls -l /dev/shmem'),('processes-end','pidin arguments'))
MEMORY=tuple('/dev/shmem/DTS_Shm_'+str(i) for i in range(1,5))
LIBRARY='/proc/boot/libDebugTrace.so'
CONFIGS=('/etc/trace_config.json','/extbin/apps/cfg/trace_config.json','/persistence/trace_config.json')
MAX_FILE=4*1024*1024;MAX_TOTAL=8*1024*1024

def config_from_environment(data):
    values=re.findall(rb'(?:^|\s)TRACE_CONFIG_PATH=([^\s\x00]+)',data)
    if len(values)!=1:return None
    try:path=values[0].decode('ascii')
    except UnicodeDecodeError:return None
    if not path.startswith(('/etc/','/extbin/apps/cfg/','/persistence/','/ramdisk/','/ifs1/','/ifs2/')):return None
    if not re.fullmatch(r'/[A-Za-z0-9_./-]+',path) or any(p in ('.','..') for p in path.split('/')):return None
    return path if path.endswith('/trace_config.json') else path.rstrip('/')+'/trace_config.json'

def fetch(a,password,remote,limit):
    if remote not in (*MEMORY,LIBRARY,*CONFIGS) and config_from_environment(('TRACE_CONFIG_PATH='+remote).encode())!=remote:raise ValueError('Target outside fixed trace scope')
    data=bytearray()
    with ftplib.FTP(timeout=a.timeout) as ftp:
        ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I')
        def save(block):
            if len(data)+len(block)>limit:raise ValueError('Fixed trace transfer limit exceeded')
            data.extend(block)
        ftp.retrbinary('RETR '+remote,save)
    if not data:raise ValueError('Empty trace response')
    return bytes(data)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true')
    p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--telnet-port',type=int,default=23)
    p.add_argument('--username',default='ftpuser');p.add_argument('--telnet-user',default='root');p.add_argument('--ask-password',action='store_true');p.add_argument('--timeout',type=float,default=20)
    a=p.parse_args(argv)
    if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 0<a.timeout<=60:p.error('Invalid port or timeout')
    print('Read-only trace inventory, four bounded DTS copies, configuration and trace-library acquisition. No serial/pipe reads or logging controls.')
    if not a.run:print('Plan only. Add --run to collect.');return 0
    base=ROOT/'delphi-dump'
    for parent in (base,*base.parents):d.reject_link(parent)
    base.mkdir(exist_ok=True);folder=base/('_trace_snapshot_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);folder.mkdir()
    report=dict(kind='read_only_trace_snapshot',started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),atomic_snapshot=False,display_recovery_verified=False,artifacts=[],actions=[],copied_bytes=0)
    def persist():(folder/'trace-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    persist();password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    try:
        actions,responses=inventory(a,folder,commands=COMMANDS);report['actions']=actions
        found=config_from_environment(responses.get('trace-environment',b''));report['environment_config_path']=found
        targets=list(dict.fromkeys((*MEMORY,LIBRARY,*((found,) if found else ()),*CONFIGS)))
        for remote in targets:
            print('Copy read-only: '+remote,flush=True)
            row=dict(remote=remote);report['artifacts'].append(row)
            try:
                remaining=MAX_TOTAL-report['copied_bytes']
                if remaining<=0:raise ValueError('Aggregate trace limit reached')
                limit=min(remaining,65536 if remote.endswith('/trace_config.json') else MAX_FILE)
                blob=fetch(a,password,remote,limit);path=d.local_path(folder,remote);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(blob)
                row.update(file=str(path.relative_to(folder)),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),status='copied_live_unlocked' if remote in MEMORY else 'copied')
                report['copied_bytes']+=len(blob)
            except (OSError,EOFError,ValueError,ftplib.Error) as exc:row.update(status='unavailable',error=type(exc).__name__,error_detail=str(exc).replace(password,'[redacted]')[:256] if password else str(exc)[:256])
            persist()
        report['inventory_complete']=len(actions)==len(COMMANDS) and all(x.get('exit_code')==0 for x in actions)
        report['dts_objects_copied']=sum(x.get('status')=='copied_live_unlocked' for x in report['artifacts'])
        report['trace_library_copied']=any(x['remote']==LIBRARY and x.get('status')=='copied' for x in report['artifacts'])
        report['collection_complete']=report['inventory_complete'] and report['dts_objects_copied']==4 and report['trace_library_copied']
    finally:
        report['inventory_artifacts']=[dict(file=f.name,bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(folder.glob('*.txt'))]
        report['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat();persist()
    print('Saved: '+str(folder));print('Live copies may change during transfer. This is not a decoded trace or a display-health PASS.')
    return 0 if report.get('collection_complete') else 2
if __name__=='__main__':raise SystemExit(main())
