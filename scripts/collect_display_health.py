"""Read-only display-failure snapshot. No observer, uploads, signals or restart. Stdlib only."""
import argparse,datetime as dt,hashlib,json,re,uuid
from pathlib import Path
from collect_observer_preflight import inventory
import delphi_inventory as d
ROOT=Path(__file__).resolve().parents[1]
PROCESSES=('AndroidAuto','AndroidAutoServices','AppConnect','DisplayManagement','screen-cda','j9','procman')
COMMANDS=(('system','uname -a'),('kernel','pidin info'),('slog','sloginfo -t'),('processes','pidin arguments'),('family','pidin family'))+tuple(('threads-'+n,'pidin -p '+n) for n in PROCESSES)+tuple(('maps-'+n,'pidin -p '+n+' mapinfo') for n in ('AndroidAuto','DisplayManagement','screen-cda','j9'))+(
 ('observer-markers','ls -l /dev/shmem/delphi-aa-observer-active.bin /dev/shmem/delphi-aa-report-*.bin /dev/shmem/delphi-display-*.bin'),
 ('display-nodes','ls -ld /dev/screen /dev/graphics'),
 ('error-files','ls -lt /extbin/apps/hmi/errlog'),
 ('processes-end','pidin arguments'))
COMMANDS=COMMANDS[:-1]+tuple(('fds-'+n,'pidin -p '+n+' fds') for n in ('AndroidAuto','AndroidAutoServices','AppConnect','DisplayManagement','screen-cda'))+(
 ('trace-memory-files','ls -l /dev/shmem'),
 ('boot-tools','ls -l /proc/boot'),
 ('app-tools','ls -l /extbin/apps/bin'),
 ('log-directories','ls -ld /var/log /var/logs'),
 COMMANDS[-1])
def process_ids(data):
    found={n:[] for n in PROCESSES}
    for line in data.replace(b'\r',b'\n').splitlines():
        m=re.match(rb'^\s*(\d+)\s+(\S+)',line)
        if not m:continue
        name=m[2].rsplit(b'/',1)[-1].decode('ascii',errors='replace')
        if name in found and int(m[1]) not in found[name]:found[name].append(int(m[1]))
    return found
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',action='store_true',help='Collect fixed read-only diagnostics over Telnet')
    p.add_argument('--state',choices=('black','normal','after-reboot','unknown'),help='What the display looks like during this snapshot')
    p.add_argument('--menu-response',choices=('works','black','unknown'),default='unknown')
    p.add_argument('--seconds-after-ready',type=int)
    p.add_argument('--door-opened',action='store_true',help='Record that opening the driver door preceded this fault; does not operate the vehicle')
    p.add_argument('--ignition',choices=('on','off','unknown'),default='unknown')
    p.add_argument('--host',default='192.168.1.4');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=20)
    a=p.parse_args(argv)
    if not 1<=a.telnet_port<=65535 or not 0<a.timeout<=60 or a.seconds_after_ready is not None and not 0<=a.seconds_after_ready<=86400:p.error('Invalid port, timeout or elapsed time')
    if a.run and a.state is None:p.error('--run requires --state black, normal, after-reboot, or unknown')
    print('Read-only display snapshot. No process restarts, observer installation or USB handoff.')
    if not a.run:print('Plan only. Add --run --state <black|normal|after-reboot|unknown> to collect.');return 0
    base=ROOT/'delphi-dump'
    for parent in (base,*base.parents):d.reject_link(parent)
    base.mkdir(exist_ok=True);folder=base/('_display_health_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);folder.mkdir()
    report=dict(kind='read_only_display_health',state=a.state,menu_response=a.menu_response,seconds_after_ready=a.seconds_after_ready,door_opened=a.door_opened,ignition=a.ignition,display_recovery_verified=False,ui_fault_reported=a.state=='black',collection_complete=False,actions=[],artifacts=[])
    target=folder/'display-health-summary.json'
    def persist():target.write_text(json.dumps(report,indent=2),encoding='utf-8')
    persist()
    try:
        actions,responses=inventory(a,folder,commands=COMMANDS);report['actions']=actions
        report['process_ids_before']=process_ids(responses.get('processes',b''));report['process_ids_after']=process_ids(responses.get('processes-end',b''))
        report['missing_processes']=[n for n,ids in report['process_ids_after'].items() if not ids]
        report['changed_processes']=[n for n in PROCESSES if report['process_ids_before'][n]!=report['process_ids_after'][n]]
        core={'uname -a','pidin info','pidin arguments'}
        report['collection_complete']=len(actions)==len(COMMANDS) and not any('error' in x or x.get('command') in core and x.get('exit_code')!=0 for x in actions)
        report['nonzero_commands']=[x['command'] for x in actions if x.get('exit_code',0)!=0]
        for file in sorted(folder.glob('*.txt')):
            data=file.read_bytes();report['artifacts'].append(dict(file=file.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    finally:persist()
    print('Saved: '+str(folder));print('Snapshot collected; this is not a display-health PASS. Live restart experiments remain on hold.')
    return 0 if report['collection_complete'] else 1
if __name__=='__main__':raise SystemExit(main())
