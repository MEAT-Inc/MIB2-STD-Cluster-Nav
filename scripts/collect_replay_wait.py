"""Read-only raw stacks for the pinned v8 replay wait; never signals or restarts."""
from project_console import console_session, log as print, status, progress
import argparse,datetime as dt,ftplib,hashlib,json,struct,uuid,re
from pathlib import Path
from run_observer_smoke import Shell
from collect_map_session import register_snapshot,libc_mapping
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def validate_pin(pin):
 if not isinstance(pin,dict) or not re.fullmatch(r'/ramdisk/delphi-nav-bridge_[0-9a-f]{32}',str(pin.get('remote',''))):
  raise ValueError('Invalid replay namespace in pin')
 for field in ('pid','start_time','manager_pid','manager_start'):
  limit=0x7fffffff if field in ('pid','manager_pid') else 0xffffffffffffffff
  if type(pin.get(field)) is not int or not 0<pin[field]<=limit:
   raise ValueError('Invalid pinned identity: '+field)
 if pin['pid']==pin['manager_pid'] or not re.fullmatch(r'[0-9a-f]{64}',str(pin.get('helper_sha256',''))):
  raise ValueError('Invalid pinned helper/process identity')
 return pin

def load_pin(root,session=None):
 pinfile=root/'replay-wait-pin.json'
 if session is None and pinfile.is_file():
  return validate_pin(json.loads(pinfile.read_text())),str(pinfile)
 if session is None:
  sessions=sorted(p for p in (root/'delphi-dump').glob('_cluster_replay_*') if p.is_dir() and (p/'replay-summary.json').is_file())
  if not sessions:
   raise ValueError('No replay-wait-pin.json or local replay collection found. Copy the replay results into delphi-dump, or use --session PATH.')
  session=sessions[-1]
 session=Path(session)
 summary=json.loads((session/'replay-summary.json').read_text())
 manifest_bytes=(session/'release-manifest.json').read_bytes()
 if sha(manifest_bytes)!=summary.get('release_manifest_sha256'):
  raise ValueError('Replay release manifest hash differs: '+str(session))
 manifest=json.loads(manifest_bytes)
 if manifest['files']['nav_launch']['sha256']!=summary.get('controller_sha256'):
  raise ValueError('Replay controller provenance differs: '+str(session))
 name='controller.bin' if (session/'controller.bin').is_file() else 'controller-pending.bin'
 blob=(session/name).read_bytes()
 entries=[a for a in summary['artifacts'] if a['file']==name]
 if len(entries)!=1 or entries[0]['bytes']!=len(blob) or entries[0]['sha256']!=sha(blob):
  raise ValueError('Replay controller artifact hash differs: '+str(session/name))
 if len(blob)!=512 or struct.unpack_from('<3I',blob)!=(0x314e4c44,1,512):
  raise ValueError('Invalid replay controller report')
 raw=blob[96:224]
 if b'\0' not in raw or raw.split(b'\0',1)[0].decode()!=summary['remote']:
  raise ValueError('Replay controller namespace differs')
 w=struct.unpack_from('<16I',blob);times=struct.unpack_from('<4Q',blob,64)
 pin=dict(remote=summary['remote'],pid=w[10],start_time=times[2],manager_pid=w[13],manager_start=times[1],helper_sha256=manifest['files']['nav_cycle']['sha256'])
 return validate_pin(pin),str(session)

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=60);p.add_argument('--session',type=Path,help='Derive the pin from this local replay collection instead of the pin file/latest collection');a=p.parse_args(argv)
 if not a.run:print('Plan only: read existing pinned replay helper, process identity and bounded raw stack pages. No upload, shutdown, signal or video. Use --run.');return 0
 try:pin,pin_source=load_pin(ROOT,a.session)
 except (OSError,ValueError,KeyError,TypeError,struct.error) as e:p.error(str(e))
 status('Using replay pin from '+pin_source)
 if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 10<=a.timeout<=120 or any(ord(c)<32 or ord(c)==127 for v in (a.host,a.username,a.telnet_user) for c in v):p.error('Invalid connection arguments')
 folder=ROOT/'delphi-dump'/('_replay_wait_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);folder.mkdir(parents=True)
 s=dict(kind='readonly_pinned_replay_wait',pin=pin,pin_source=pin_source,signals=False,service_restarts=False,artifacts=[],errors=[]);shell=None;remote=pin['remote']
 def save(name,b):
  (folder/name).write_bytes(b);s['artifacts'].append(dict(file=name,bytes=len(b),sha256=sha(b)));return b
 def persist():(folder/'wait-summary.json').write_text(json.dumps(s,indent=2))
 def fetch(name):
  data=bytearray()
  with ftplib.FTP(timeout=a.timeout) as f:
   f.connect(a.host,a.port);f.login(a.username,'ftpuser');f.voidcmd('TYPE I')
   def take(b):
    if len(data)+len(b)>1048576:raise ValueError('Bounded transfer exceeded')
    data.extend(b)
   f.retrbinary('RETR '+remote+'/'+name,take)
  return bytes(data)
 def capture(name,c):
  rc=shell.command(c+' > '+name+' 2>&1',required=False);shell.command('chmod 644 '+name);b=save(name,fetch(name))
  if rc:raise ValueError('Read-only query refused '+name+' exit '+str(rc))
  return b
 persist()
 try:
  status('Verifying the existing pinned replay helper.')
  if sha(fetch('nav_cycle'))!=pin['helper_sha256']:raise ValueError('Pinned helper differs; no helper execution attempted')
  shell=Shell(a,folder);shell.command('cd '+remote);identity=None
  fields=('pid','start_time','manager_pid','manager_start');args=' '.join(str(pin[k]) for k in fields)
  for sample in (1,2):
   status('Reading pinned navigation wait: pass '+str(sample)+' of 2.')
   label='wait-'+str(sample);identity=json.loads(capture(label+'-identity.json','LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle inspect '+str(pin['pid'])))
   if any(identity.get(k)!=pin[k] for k in fields):raise ValueError('Pinned process changed; do not reproduce the fault')
   pid=str(pin['pid']);capture(label+'-threads.txt','pidin -p '+pid+' threads');capture(label+'-backtrace.txt','pidin -p '+pid+' backtrace')
   regs=register_snapshot(capture(label+'-regs.txt','pidin -p '+pid+' regs'),pin['pid']);base=libc_mapping(capture(label+'-mem.txt','pidin -p '+pid+' mem'));pages={(base+0x76ee8)&~4095}
   candidates=[]
   for tid,r in regs.items():
    if r.get('pc') in (base+0x38714,base+0x38710) and r.get('lr')==base+0x28088:
     sp=r.get('sp',0)
     if not 4096<=sp<0xbffff000 or sp&3:raise ValueError('Unexpected stack pointer')
     candidates.append(dict(tid=tid,sp=sp))
     pages.update((sp&~4095,(sp+193*4-1)&~4095))
   if not 1<=len(candidates)<=4 or len(pages)>9:raise ValueError('Allocator-wait candidates unavailable or ambiguous; snapshot retained')
   s.setdefault('candidates',[]).append(dict(sample=sample,threads=candidates,libc_base=base))
   for address in sorted(pages):
    progress('Reading stack/mutex page 0x'+format(address,'08x')+'.',key='wait-page:'+str(sample)+':'+str(address))
    name=label+'-page-'+format(address,'08x')+'.bin';err=name+'.errors.txt'
    rc=shell.command('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle page '+args+' '+str(address)+' > '+name+' 2> '+err,required=False)
    shell.command('chmod 644 '+name+' '+err);save(err,fetch(err));b=save(name,fetch(name))
    if rc or len(b)!=4096:raise ValueError('Raw reader refused '+name)
   persist()
  s['complete']=True
 except (OSError,EOFError,ValueError,RuntimeError,KeyboardInterrupt,ftplib.Error) as e:
  s['errors'].append(str(e));status(str(e),'ERROR')
 finally:
  if shell:s['actions']=shell.actions;shell.close()
  persist()
 status('Wait capture '+('complete.' if s.get('complete') else 'partial; return the saved results.'),'OK' if s.get('complete') else 'WARN')
 print('Saved:',folder);print('No shutdown, signals or video sent. Return the entire _replay_wait_* folder.');return 0 if s.get('complete') else 2
if __name__=='__main__':
 with console_session(__file__, __doc__):
  raise SystemExit(main())
