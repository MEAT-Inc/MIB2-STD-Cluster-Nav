"""Bounded receive-only capture of the configured TraceServer text port. Stdlib only."""
import argparse,datetime as dt,hashlib,json,re,socket,time,uuid
from pathlib import Path
import delphi_inventory as d
from collect_observer_preflight import inventory
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=(('kernel','pidin info'),('processes','pidin arguments'),('trace-fds','pidin -p TraceServer fds'),('android-threads','pidin -p AndroidAuto'))

def port_state(data,state):
    return any(re.search(rb'(?<![0-9])15361(?![0-9])',line) and state.encode() in line.upper() for line in data.replace(b'\r',b'\n').splitlines())

def receive(sock,output,seconds,limit):
    started=time.monotonic();total=0;reason='duration';digest=hashlib.sha256();chunks=0
    while total<limit:
        remaining=seconds-(time.monotonic()-started)
        if remaining<=0:break
        sock.settimeout(min(1,remaining))
        try:block=sock.recv(min(65536,limit-total))
        except socket.timeout:continue
        if not block:reason='peer_closed';break
        output.write(block);digest.update(block);total+=len(block);chunks+=1
    if total==limit:reason='byte_limit'
    output.flush()
    return dict(bytes=total,sha256=digest.hexdigest(),chunks=chunks,stop_reason=reason,elapsed_seconds=round(time.monotonic()-started,3))

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--host',default='192.168.1.4')
    p.add_argument('--seconds',type=int,default=30);p.add_argument('--max-bytes',type=int,default=8*1024*1024)
    p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=15)
    a=p.parse_args(argv)
    if not 1<=a.seconds<=120 or not 1<=a.max_bytes<=16*1024*1024 or not 1<=a.telnet_port<=65535 or not 0<a.timeout<=60:p.error('Invalid duration, byte limit, port or timeout')
    print('Receive-only TraceServer TCP 15361 capture. No filter commands, observer, process restart, or USB handoff.')
    if not a.run:print('Plan only. Add --run; keep Ethernet attached throughout.');return 0
    base=ROOT/'delphi-dump'
    for parent in (base,*base.parents):d.reject_link(parent)
    base.mkdir(exist_ok=True);folder=base/('_trace_tcp_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);folder.mkdir()
    report=dict(kind='receive_only_trace_tcp',host=a.host,port=15361,requested_seconds=a.seconds,byte_limit=a.max_bytes,application_bytes_sent=0,display_recovery_verified=False,capture_complete=False,actions=[])
    def persist():(folder/'trace-tcp-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    persist()
    try:
        before=folder/'before';before.mkdir();actions,responses=inventory(a,before,commands=COMMANDS);report['actions'].append(dict(stage='before',commands=actions));persist()
        fds=responses.get('trace-fds',b'')
        if port_state(fds,'ESTABLISHED') or not port_state(fds,'LISTEN'):
            report['error']='Existing trace client detected or listener could not be verified; no TCP connection attempted'
            print(report['error']);return 2
        print('Receiving existing trace output for up to '+str(a.seconds)+' seconds. Keep Ethernet connected.',flush=True)
        with (folder/'trace.bin').open('xb') as output:
            try:
                with socket.create_connection((a.host,15361),timeout=a.timeout) as sock:
                    report['connected']=True;report['capture']=receive(sock,output,a.seconds,a.max_bytes)
            except (OSError,EOFError) as exc:
                report['error']=type(exc).__name__+': '+str(exc)
            finally:
                output.flush()
        raw=(folder/'trace.bin').read_bytes();report['trace_artifact']=dict(file='trace.bin',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        # Convenience preview only: raw bytes stay authoritative; no timestamps or
        # complete protocol records are inferred from a partial UTF-8 decode.
        (folder/'trace-preview.txt').write_text(raw[:262144].decode('utf-8',errors='replace'),encoding='utf-8')
        report['preview_truncated']=len(raw)>262144
        after=folder/'after';after.mkdir();actions,_=inventory(a,after,commands=COMMANDS);report['actions'].append(dict(stage='after',commands=actions))
        report['trace_received']=report.get('capture',{}).get('bytes',0)>0
        report['capture_complete']='error' not in report and report['trace_received'] and report.get('capture',{}).get('stop_reason') in ('duration','byte_limit')
    finally:
        report['artifacts']=[dict(file=str(f.relative_to(folder)),bytes=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest()) for f in sorted(folder.rglob('*.txt'))]
        persist()
    print('Saved: '+str(folder));print('Trace receipt is not proof of Android Auto recovery. Return the entire folder even if empty or partial.')
    return 0 if report['capture_complete'] else 2
if __name__=='__main__':raise SystemExit(main())
