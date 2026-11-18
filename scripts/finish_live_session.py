"""Capture and finish a prior interrupted live session; never starts video."""
from project_console import console_session,status,log as print,prompt as input
from pathlib import Path
import argparse,datetime as dt,ftplib,hashlib,json,re,struct,time,types,uuid
from run_observer_smoke import Shell,retrieve
from run_disconnected_observer import validate_report
from run_androidauto_observer import fresh_stock_pid
from live_cluster_bridge import LiveBridge,confirm_factory_map_locations
ROOT=Path(__file__).resolve().parents[1]

def session_metadata(root,session=None):
 if session is None:
  candidates=sorted(p for p in (root/'delphi-dump').glob('_disconnect_observer_*') if (p/'live-bridge-summary.json').exists())
  if not candidates:raise ValueError('No previous live session found; use --session PATH')
  session=candidates[-1]
 else:
  session=Path(session)
  if not session.is_absolute():session=root/session
 s=json.loads((session/'disconnect-summary.json').read_text());state=json.loads((session/'live-bridge-summary.json').read_text());raw=(session/'live-release-manifest.json').read_bytes()
 if not s.get('live_cluster_requested') or not state.get('started') or not re.fullmatch(r'/ramdisk/delphi-aa-observer_[0-9a-f]{32}',s['remote_directory']) or state['remote']!='/ramdisk/delphi-nav-bridge_'+s['remote_directory'].rsplit('_',1)[1]:raise ValueError('Invalid previous live session')
 if hashlib.sha256(raw).hexdigest()!=state.get('manifest_sha256') or not re.fullmatch(r'[0-9a-f]{64}',s['native_sha256']):raise ValueError('Previous live session provenance differs')
 return session,s,state,raw

def cleanup_aa(cmd,copy,fetch,remote,seconds=20,timeout=60):
 if not re.fullmatch(r'/ramdisk/delphi-aa-observer_[0-9a-f]{32}',remote):raise ValueError('Invalid AA cleanup root')
 token=remote.rsplit('_',1)[1];final='/dev/shmem/delphi-aa-final-'+token+'.bin'
 if cmd('test -r '+final,required=False)!=0:
  pending='/dev/shmem/delphi-aa-report-'+token+'.bin';until=time.monotonic()+timeout
  while cmd('test -r '+pending,required=False)!=0:
   if time.monotonic()>=until:raise TimeoutError('AA cleanup checkpoint not ready; no cleanup command sent')
   time.sleep(.5)
  validate_report(copy(pending,'finish-aa-pending.bin'),remote,True,seconds)
  rc=cmd('LD_PRELOAD= ./observer_launch cleanup-disconnected '+remote+' > finish-aa-cleanup.txt 2>&1',required=False);cmd('chmod 644 finish-aa-cleanup.txt');fetch('finish-aa-cleanup.txt')
  if rc:raise RuntimeError('AA cleanup refused; Nav cleanup not attempted')
 state=validate_report(copy(final,'finish-aa-final.bin'),remote,False,seconds)
 cmd('pidin -p AndroidAuto arguments > finish-aa-stock.txt');cmd('chmod 644 finish-aa-stock.txt')
 if fresh_stock_pid(fetch('finish-aa-stock.txt'))!=state['restored_pid']:raise ValueError('Restored AA identity differs')
 return state

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--phone-unplugged',action='store_true');p.add_argument('--session',type=Path);p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=90);a=p.parse_args(argv)
 if not a.run:print('Plan only. Capture and finish the previous AA/Nav test with the phone disconnected. No replay or video.');return 0
 if not a.phone_unplugged:p.error('Physically unplug the phone, connect Ethernet, and add --phone-unplugged')
 if not 60<=a.timeout<=180 or not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535:p.error('Invalid connection options')
 try:source,original,state,manifest=session_metadata(ROOT,a.session)
 except (OSError,ValueError,KeyError,TypeError) as e:p.error(str(e))
 folder=ROOT/'delphi-dump'/('_live_finish_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);folder.mkdir(parents=True);summary=dict(kind='finish_interrupted_live_session',source=str(source),video=False,errors=[],artifacts=[]);shell=None;remote=original['remote_directory'];bridge=None
 def persist():(folder/'finish-summary.json').write_text(json.dumps(summary,indent=2))
 def ftp():
  f=ftplib.FTP(timeout=a.timeout);f.connect(a.host,a.port);f.login(a.username,'ftpuser');f.voidcmd('TYPE I');return f
 def fetch(name):
  with ftp() as f:b=retrieve(f,remote+'/'+name)
  (folder/name).write_bytes(b);summary['artifacts'].append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));return b
 def cmd(c,required=True):return shell.command(c,required=required)
 def copy(src,name):cmd('cp '+src+' '+name);cmd('chmod 644 '+name);return fetch(name)
 persist()
 try:
  shell=Shell(a,folder)
  inactive=[cmd('test ! -e '+p,False)==0 for p in ('/dev/shmem/delphi-aa-observer-active.bin','/dev/shmem/delphi-nav-launch-active.bin')]
  if all(inactive):
   summary['no_pending_controllers']=True;summary.update(confirm_factory_map_locations(input));summary['factory_maps_working']=summary['factory_maps_restored']
  else:
   (folder/'live-bridge-summary.json').write_text(json.dumps(state));(folder/'live-release-manifest.json').write_bytes(manifest);a.resume=source;bridge=LiveBridge(ROOT,a,folder,original,'ftpuser');cmd('cd '+remote)
   with ftp() as f:b=retrieve(f,remote+'/observer_launch',131072)
   if hashlib.sha256(b).hexdigest()!=original['native_sha256']:raise ValueError('Saved AA controller differs; no cleanup attempted')
   bridge.cmd=cmd;bridge.fetch_aa=fetch;bridge.copy=copy
   try:
    from live_cluster_bridge import assess_output
    v=assess_output(bridge.report('live-nav-before-finish.bin'),state['observed_pid']);summary['output_before_cleanup']=v;bridge.capture_output(v)
    from review_live_input import reader_report
    reader=copy('/dev/shmem/delphi-live-report-'+remote.rsplit('_',1)[1]+'.bin','reader-before-finish.bin');summary['reader_before_cleanup']=reader_report(reader,state['source_pid'],consumer_pid=state['observed_pid'],allow_unbound=True)
   except (OSError,ValueError,RuntimeError,ftplib.Error) as e:summary['diagnostic_error']=str(e)
   summary['aa_restoration']=cleanup_aa(cmd,copy,fetch,remote,original.get('capture_profile_seconds',20));summary['aa_restoration_verified']=True;persist()
   bridge.cleanup(cmd,fetch,copy);summary['nav']=bridge.state;summary['restoration_verified']=bool(bridge.state.get('restoration_verified') and bridge.state.get('factory_maps_restored'))
 except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:summary['errors'].append(str(e));status(str(e),'ERROR')
 finally:
  if bridge:summary['nav']=bridge.state;bridge.save()
  if shell:summary['actions']=shell.actions;shell.close()
  persist()
 print('Saved:',folder);print('Cleanup only; no live playback was started.');return 0 if summary.get('restoration_verified') or summary.get('no_pending_controllers') and summary.get('factory_maps_working') else 2
if __name__=='__main__':
 with console_session(__file__,__doc__):raise SystemExit(main())
