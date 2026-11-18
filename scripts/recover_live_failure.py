"""Recover the saved failed Nav session using exact fault guards; no video trial."""
from project_console import console_session,status,log as print,prompt as input
from pathlib import Path
import argparse,datetime as dt,ftplib,hashlib,io,json,struct,uuid
from run_observer_smoke import Shell,retrieve
from collect_live_failure import load_session_identity
from run_cluster_replay import assess_controller
ROOT=Path(__file__).resolve().parents[1]

def json_record(raw):
 rows=[]
 for line in raw.splitlines():
  if line.startswith(b'{'):
   try:rows.append(json.loads(line))
   except ValueError:pass
 if len(rows)!=1:raise ValueError('Expected exactly one native result record')
 return rows[0]

def failed_controller(raw,pin):
 if len(raw)!=512:raise ValueError('Pending controller size')
 w=struct.unpack('<128I',raw);times=struct.unpack_from('<4Q',raw,64);root=raw[96:224].split(b'\0')[0].decode()
 if w[:4]!=(0x314e4c44,1,512,4) or w[4] not in (1005,1006) or w[6]!=1 or w[7] or w[8]!=3 or w[9] or w[10]!=pin['pid'] or w[13]!=pin['manager_pid'] or w[15]!=1 or tuple(w[64:68])!=(20,1,1,1) or times[1]!=pin['manager_start'] or times[2]!=pin['start_time'] or root!=pin['remote']:raise ValueError('Radio is not in the saved failed-cleanup state; recovery cancelled')
 if not all(0<x<=0x7fffffff for x in (w[10],w[12],w[13],w[14])) or len({w[10],w[12],w[13],w[14]})!=4:raise ValueError('Invalid failed controller identities')
 return w

def recovered_result(v,pin):
 if v.get('version')!=1 or v.get('process_cycle_verified') is not True or v.get('signals_to_nav') is not True or v.get('termination_signal')!=9 or v.get('stage')!='recover_restart' or v.get('old_pid')!=pin['pid'] or type(v.get('new_pid')) is not int or not 0<v['new_pid']<=0x7fffffff or v['new_pid'] in (pin['pid'],pin['manager_pid']) or type(v.get('new_start')) is not int or not 0<v['new_start']<=0xffffffffffffffff or v['new_start']==pin['start_time']:raise ValueError('Guarded restart was not verified; finalization cancelled')
 return v

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--phone-unplugged',action='store_true');p.add_argument('--session',type=Path);p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=90);a=p.parse_args(argv)
 if not a.run:print('Plan only. Recover only the saved, twice-matched Nav allocator crash, then finalize verified factory restart. No video or full replay.');return 0
 if not a.phone_unplugged:p.error('Keep phone unplugged and Ethernet connected; add --phone-unplugged')
 if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 60<=a.timeout<=180:p.error('Invalid ports/timeout')
 try:pin,source,_=load_session_identity(ROOT,a.session)
 except (OSError,ValueError,KeyError,TypeError,struct.error) as e:p.error(str(e))
 release=ROOT/'native/cluster-bridge/recovery/release';manifest=json.loads((release/'manifest.json').read_text());files={n:(release/n).read_bytes() for n in manifest['files']}
 if manifest.get('kind')!='exact_crash_nav_recovery' or set(files)!={'nav_cycle','nav_finalize'}:raise ValueError('Wrong recovery package')
 for n,b in files.items():
  e=manifest['files'][n]
  if len(b)!=e['bytes'] or not 0<len(b)<=131072 or hashlib.sha256(b).hexdigest()!=e['sha256']:raise ValueError('Recovery payload changed '+n)
 tag=uuid.uuid4().hex;remote='/ramdisk/delphi-nav-recovery_'+tag;folder=ROOT/'delphi-dump'/('_live_recovery_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+tag[:8]);folder.mkdir(parents=True);s=dict(kind='exact_crash_nav_recovery',session_source=str(source),pin=pin,remote=remote,recovery_attempted=False,video=False,artifacts=[],errors=[]);shell=None
 def persist():(folder/'recovery-summary.json').write_text(json.dumps(s,indent=2))
 def ftp():
  f=ftplib.FTP(timeout=a.timeout);f.connect(a.host,a.port);f.login(a.username,'ftpuser');f.voidcmd('TYPE I');return f
 def get(path,limit=1048576):
  data=bytearray()
  with ftp() as f:
   def take(b):
    if len(data)+len(b)>limit:raise ValueError('Recovery transfer limit')
    data.extend(b)
   f.retrbinary('RETR '+path,take)
  return bytes(data)
 def save(name,b):
  (folder/name).write_bytes(b);s['artifacts'].append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));return b
 def query(scope,name,command):
  shell.command('cd '+scope);dest='recovery-'+tag[:8]+'-'+name;rc=shell.command(command+' > '+dest+' 2>&1',required=False);shell.command('chmod 644 '+dest);return rc,save(name,get(scope+'/'+dest))
 def copy(scope,source,name):
  shell.command('cd '+scope);dest='recovery-'+tag[:8]+'-'+name;shell.command('cp '+source+' '+dest);shell.command('chmod 644 '+dest);return save(name,get(scope+'/'+dest))
 def identity(scope,pid,name,start):
  rc,b=query(scope,name,'LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle inspect '+str(pid))
  if rc:raise ValueError('Pinned Nav inspection refused; no further action')
  v=json_record(b)
  if v.get('version')!=1 or v.get('readonly') is not True or v.get('app_id')!=29 or v.get('state')!=3 or any(v.get(k)!=val for k,val in dict(pid=pid,start_time=start,manager_pid=pin['manager_pid'],manager_start=pin['manager_start']).items()):raise ValueError('Nav or manager identity changed; no further action')
  return v
 persist()
 try:
  if hashlib.sha256(get(pin['remote']+'/nav_cycle',131072)).hexdigest()!=pin['helper_sha256']:raise ValueError('Original staged helper changed')
  shell=Shell(a,folder);identity(pin['remote'],pin['pid'],'identity-before.json',pin['start_time']);failed_controller(copy(pin['remote'],'/dev/shmem/delphi-nav-launch-active.bin','controller-before.bin'),pin)
  with ftp() as f:
   f.mkd(remote)
   for name,b in files.items():
    f.storbinary('STOR '+remote+'/'+name,io.BytesIO(b))
    if retrieve(f,remote+'/'+name,131072)!=b:raise ValueError('Recovery upload mismatch '+name)
  for name in files:shell.command('chmod 500 '+remote+'/'+name)
  identity(remote,pin['pid'],'identity-checked.json',pin['start_time'])
  args=' '.join(str(pin[k]) for k in ('pid','start_time','manager_pid','manager_start'));s['recovery_attempted']=True;persist();status('Applying the exact captured-crash guard; healthy or changed states are refused.')
  rc,b=query(remote,'recover.txt','LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle recover '+args);s['recovery_exit']=rc
  if rc:raise RuntimeError('Exact-crash recovery refused; no generic termination fallback was used')
  v=recovered_result(json_record(b),pin);s['restart']=v;persist();identity(remote,v['new_pid'],'identity-restored.json',v['new_start'])
  rc,b=query(remote,'finalize.txt','LD_PRELOAD= ./nav_finalize finalize-recovery '+pin['remote']);s['finalize_exit']=rc
  if rc:raise RuntimeError('Factory process restarted, but failed-cleanup reconciliation was refused')
  token=pin['remote'].rsplit('_',1)[1];final=copy(remote,'/dev/shmem/delphi-nav-launch-recovered-'+token+'.bin','controller-recovered.bin');state=assess_controller(final,pin['remote'],True)
  if state['restored_pid']!=v['new_pid'] or struct.unpack_from('<Q',final,88)[0]!=v['new_start']:raise ValueError('Factory process changed during finalization')
  if shell.command('test ! -e /dev/shmem/delphi-nav-launch-active.bin',required=False):raise ValueError('Nav controller still active')
  s.update(restoration_verified=True,restored_pid=v['new_pid']);persist();s['factory_maps_restored']=input('Wait for navigation to start. Using the location toggle, do factory maps work on the radio and then in the cluster? [y/n/unknown]: ').strip().lower() in ('y','yes')
 except (OSError,EOFError,ValueError,RuntimeError,ftplib.Error) as e:s['errors'].append(str(e));status(str(e),'ERROR')
 finally:
  if shell:s['actions']=shell.actions;shell.close()
  persist()
 print('Saved:',folder);print('Return the entire _live_recovery_* folder. No live playback test was run.');return 0 if s.get('restoration_verified') and s.get('factory_maps_restored') else 2
if __name__=='__main__':
 with console_session(__file__,__doc__):raise SystemExit(main())
