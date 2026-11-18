"""Capture the pinned failed live Nav state. Read-only; no shutdown, restart or video."""
from project_console import console_session,status,log as print
from pathlib import Path
import argparse,datetime as dt,ftplib,hashlib,json,struct,uuid
from run_observer_smoke import Shell
from collect_replay_wait import validate_pin
from collect_map_session import register_snapshot,libc_mapping
ROOT=Path(__file__).resolve().parents[1]
def load_session_identity(root,session=None):
 root=Path(root)
 if session is None:
  candidates=sorted(p for p in (root/'delphi-dump').glob('_disconnect_observer_*') if p.is_dir() and (p/'live-bridge-summary.json').is_file())
  if not candidates:raise ValueError('No previous live-output session found under delphi-dump; use --session PATH')
  # Never silently target an older process after a newer live run/restoration.
  session=candidates[-1]
 else:
  session=Path(session)
  if not session.is_absolute():session=root/session
 session=session.resolve();state=json.loads((session/'live-bridge-summary.json').read_text());summary=json.loads((session/'disconnect-summary.json').read_text())
 if not summary.get('live_cluster_requested') or not state.get('started') or state.get('restoration_verified') or not state.get('cleanup_pending'):raise ValueError('Selected live session is not a pending failed Nav run: '+str(session))
 name='nav-controller-final.bin' if (session/'nav-controller-final.bin').exists() else 'nav-controller-pending.bin'
 b=(session/name).read_bytes();entries=[a for a in summary.get('artifacts',[]) if a.get('file')==name]
 if len(entries)!=1 or len(b)!=entries[0].get('bytes') or hashlib.sha256(b).hexdigest()!=entries[0].get('sha256'):raise ValueError('Saved controller artifact differs: '+name)
 if len(b)!=512:raise ValueError('Saved controller report size')
 w=struct.unpack('<128I',b);times=struct.unpack_from('<4Q',b,64);raw=b[96:224]
 if b'\0' not in raw:raise ValueError('Saved Nav namespace is unterminated')
 address,padding=raw.split(b'\0',1);remote=address.decode('ascii')
 if w[:3]!=(0x314e4c44,1,512) or w[3]!=4 or w[9] or any(padding) or remote!=state['remote'] or summary['remote_directory']!='/ramdisk/delphi-aa-observer_'+remote.rsplit('_',1)[1]:raise ValueError('Saved failed Nav identity/profile differs')
 saved=session/'live-release-manifest.json';manifest_file=saved if saved.exists() else root/'native/cluster-bridge/live-output/release/manifest.json';manifest_bytes=manifest_file.read_bytes()
 if hashlib.sha256(manifest_bytes).hexdigest()!=state.get('manifest_sha256'):raise ValueError('Release manifest differs from selected session; use its original live-release-manifest.json or original test bundle')
 manifest=json.loads(manifest_bytes)
 if manifest.get('kind')!='native_cluster_live_output':raise ValueError('Selected session is not a live-output release')
 pin=dict(remote=remote,pid=w[10],start_time=times[2],manager_pid=w[13],manager_start=times[1],helper_sha256=manifest['files']['nav_cycle']['sha256'])
 return validate_pin(pin),session,manifest_bytes

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--session',type=Path,help='Previous live-output result folder; default is latest session in delphi-dump');p.add_argument('--phone-unplugged',action='store_true');p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=90);a=p.parse_args(argv)
 if not a.run:print('Plan only. Reads pinned existing helper/logs and bounded Nav stack pages. No upload, signal, shutdown, restart or video.');return 0
 if not a.phone_unplugged:p.error('Keep phone unplugged and Ethernet connected; add --phone-unplugged')
 if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 10<=a.timeout<=120:p.error('Invalid connection options')
 try:pin,session_source,_=load_session_identity(ROOT,a.session)
 except (OSError,ValueError,KeyError,TypeError,struct.error) as e:p.error(str(e))
 status('Using previous live session: '+str(session_source))
 remote=pin['remote'];token=remote.rsplit('_',1)[1];tag=uuid.uuid4().hex[:8];folder=ROOT/'delphi-dump'/('_live_failure_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+tag);folder.mkdir(parents=True);summary=dict(kind='readonly_live_failure',pin=pin,session_source=str(session_source),signals=False,service_restarts=False,video=False,artifacts=[],errors=[]);shell=None
 def persist():(folder/'failure-summary.json').write_text(json.dumps(summary,indent=2))
 def get(path,limit=1048576):
  data=bytearray()
  with ftplib.FTP(timeout=a.timeout) as ftp:
   ftp.connect(a.host,a.port);ftp.login(a.username,'ftpuser');ftp.voidcmd('TYPE I')
   def take(b):
    if len(data)+len(b)>limit:raise ValueError('Bounded diagnostic transfer exceeded')
    data.extend(b)
   ftp.retrbinary('RETR '+path,take)
  return bytes(data)
 def save(name,b):
  (folder/name).write_bytes(b);summary['artifacts'].append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));return b
 def query(name,command):
  dest='lf-'+tag+'-'+name;rc=shell.command(command+' > '+dest+' 2>&1',required=False);shell.command('chmod 644 '+dest);return rc,save(name,get(remote+'/'+dest))
 def copy(source,name):
  dest='lf-'+tag+'-'+name
  if shell.command('test -r '+source,required=False):return
  shell.command('cp '+source+' '+dest);shell.command('chmod 644 '+dest);save(name,get(remote+'/'+dest))
 persist()
 try:
  if hashlib.sha256(get(remote+'/nav_cycle',131072)).hexdigest()!=pin['helper_sha256']:raise ValueError('Existing helper hash differs; no helper executed')
  shell=Shell(a,folder);shell.command('cd '+remote)
  for name in ('start.txt','nav-startup.txt','cleanup.txt','libc-preflight.json'):copy(remote+'/'+name,name)
  for phase in ('start-cycle','start-recover','cleanup-cycle','cleanup-recover'):copy('/dev/shmem/delphi-nav-lifecycle-'+token+'-'+phase+'.txt','lifecycle-'+phase+'.txt')
  for source,name in (('delphi-nav-report-','live-nav.bin'),('delphi-nav-launch-report-','controller-pending.bin'),('delphi-nav-launch-final-','controller-final.bin')):copy('/dev/shmem/'+source+token+'.bin',name)
  query('processes.txt','pidin arguments')
  fields=('pid','start_time','manager_pid','manager_start');args=' '.join(str(pin[k]) for k in fields)
  for sample in (1,2):
   status('Reading pinned Nav failure: sample '+str(sample)+' of 2')
   prefix='sample-'+str(sample);rc,b=query(prefix+'-identity.json','LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle inspect '+str(pin['pid']))
   if rc:raise ValueError('Pinned Nav inspect refused; logs retained')
   identity=json.loads(b)
   if any(identity.get(k)!=pin[k] for k in fields):raise ValueError('Nav/manager identity changed; memory queries cancelled')
   for view in ('threads','backtrace'):query(prefix+'-'+view+'.txt','pidin -p '+str(pin['pid'])+' '+view)
   _,raw=query(prefix+'-regs.txt','pidin -p '+str(pin['pid'])+' regs');regs=register_snapshot(raw,pin['pid']);_,raw=query(prefix+'-mem.txt','pidin -p '+str(pin['pid'])+' mem');pages=[]
   try:pages.append((libc_mapping(raw)+0x76ee8)&~4095)
   except ValueError as e:summary['errors'].append(str(e))
   for tid,v in sorted(regs.items())[:24]:
    sp=v.get('sp',0)
    if 4096<=sp<0xbfffefff and not sp&3:
     for address in (sp&~4095,(sp+1023)&~4095):
      if address not in pages:pages.append(address)
   for address in pages[:49]:
    name=prefix+'-page-'+format(address,'08x')+'.bin';err=name+'.errors.txt';dest='lf-'+tag+'-'+name;edest=dest+'.errors.txt'
    rc=shell.command('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle page '+args+' '+str(address)+' > '+dest+' 2> '+edest,required=False);shell.command('chmod 644 '+dest+' '+edest);data=save(name,get(remote+'/'+dest));save(err,get(remote+'/'+edest))
    if rc or len(data)!=4096:summary['errors'].append('Page unavailable: '+name)
   persist()
  for name in ('NavServices','DisplayManagement','Most','TransportServer','screen-cda'):query(name+'-threads.txt','pidin -p '+name+' threads')
  query('slog.txt','sloginfo -t');summary['complete']=True
 except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:summary['errors'].append(str(e));status(str(e),'ERROR')
 finally:
  if shell:summary['actions']=shell.actions;shell.close()
  persist()
 print('Saved:',folder);print('Read-only capture finished. Return the entire _live_failure_* folder; no recovery or playback was attempted.');return 0 if summary.get('complete') else 2
if __name__=='__main__':
 with console_session(__file__,__doc__):raise SystemExit(main())
