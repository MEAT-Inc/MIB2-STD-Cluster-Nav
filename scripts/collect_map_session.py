"""Read-only map-session diagnostics; no service restart or video transport access."""
from project_console import console_session, log as print, progress
import argparse, datetime as dt, ftplib, getpass, hashlib, json, re, time, uuid
from pathlib import Path
import delphi_inventory as d
from run_observer_smoke import Shell
ROOT=Path(__file__).resolve().parents[1]
# Utility query behavior: https://www.qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/p/pidin.html
# sloginfo -t reads retained messages and exits; no -c clearing or -w follow.
# https://qnx.com/developers/docs/6.5.0SP1.update/com.qnx.doc.neutrino_utilities/s/sloginfo.html
TARGETS=('NavigationServer','NavServices','DisplayManagement','screen-cda','Most','TransportServer','MediaHandler')

def processes(data):
 result={}
 for line in data.decode(errors='replace').splitlines():
  m=re.match(r'\s*(\d+)\s+(\S+)',line)
  if m and m[2].rsplit('/',1)[-1] in TARGETS:
   name=m[2].rsplit('/',1)[-1]
   if name in result:raise ValueError('Ambiguous process '+name)
   pid=int(m[1])
   if not 0<pid<=0x7fffffff:raise ValueError('Invalid process identity')
   result[name]=pid
 return result

def register_snapshot(data,pid):
 """Parse only this numeric PID's ARM register blocks; reject ambiguous headers."""
 result={};current=None
 for line in data.decode('ascii',errors='replace').splitlines():
  header=re.match(r'^\s*(\d+)\s+(\d+)\s+\S',line)
  if header:
   current=None
   if int(header[1])==pid:
    tid=int(header[2])
    if tid in result:raise ValueError('Duplicate register thread')
    result[tid]={};current=result[tid]
  elif current is not None:
   for name,value in re.findall(r'\b(r(?:1[0-2]|[0-9])|sp|lr|pc|fp|ip):([0-9a-fA-F]{8})\b',line):
    if name in current:raise ValueError('Duplicate register '+name)
    current[name]=int(value,16)
 return result

def raw_stack_pages(data,pid):
 """Bounded pages containing the captured NavMain/timer stacks, not an unwind."""
 regs=register_snapshot(data,pid);pages=[];seen=set()
 for tid in (2,11):
  sp=regs.get(tid,{}).get('sp')
  if sp is None:continue
  # ARM userspace only, naturally aligned, one readable page per selected thread.
  if not 4096<=sp<0xc0000000 or sp&3:raise ValueError('Invalid userspace stack pointer')
  page=sp&~4095
  if page not in seen:pages.append((tid,sp,page));seen.add(page)
 if not pages:raise ValueError('No NavMain/timer ARM stack pointers found')
 return pages


def libc_mapping(data):
 values=re.findall(rb'^\s*libc\.so\.3\s+@\s*([0-9a-fA-F]+)\b',data,re.M)
 if len(values)!=1:raise ValueError('Ambiguous/missing libc mapping')
 base=int(values[0],16)
 if base&4095 or not 4096<=base<0xbff00000:raise ValueError('Invalid libc mapping')
 return base

def capture_allocator_pages(shell,capture,fetch,pid,label,identity):
 """Read at most three live 4096-byte pages; caller verifies exact libc first."""
 if type(pid) is not int or not 0<pid<=0x7fffffff or not re.fullmatch('[a-z0-9-]{1,32}',label):
  raise ValueError('Invalid allocator capture identity/label')
 fields=('pid','start_time','manager_pid','manager_start')
 if not isinstance(identity,dict) or identity.get('pid')!=pid or any(type(identity.get(k)) is not int or not 0<identity[k]<=0xffffffffffffffff for k in fields):
  raise ValueError('Missing native page-reader identity')
 if identity['manager_pid']>0x7fffffff:raise ValueError('Invalid page-reader manager identity')
 arguments=' '.join(str(identity[k]) for k in fields)
 regsdata=capture(label+'-regs.txt','pidin -p '+str(pid)+' regs')
 memdata=capture(label+'-mem.txt','pidin -p '+str(pid)+' mem')
 regs=register_snapshot(regsdata,pid);pages=raw_stack_pages(regsdata,pid)
 base=libc_mapping(memdata);requests=[]
 for tid,sp,page in pages:
  requests.append(('tid'+str(tid),page,dict(tid=tid,sp=hex(sp),pc=hex(regs[tid].get('pc',0)),lr=hex(regs[tid].get('lr',0)))))
 requests.append(('allocator',(base+0x76ee8)&~4095,dict(libc_base=hex(base),mutex=hex(base+0x76ee8))))
 result=[]
 for kind,address,context in requests:
  name=label+'-'+kind+'.bin'
  errors=name+'.errors.txt'
  code=shell.command('LD_PRELOAD= LD_LIBRARY_PATH=/proc/boot ./nav_cycle page '+arguments+' '+str(address)+' > '+name+' 2> '+errors,required=False)
  shell.command('chmod 644 '+name+' '+errors)
  fetch(errors);blob=fetch(name)
  if code:raise ValueError('Native page reader exit '+str(code)+' for '+name+'; see '+errors)
  if len(blob)!=4096:raise ValueError('Incomplete raw page '+name+': '+str(len(blob))+' bytes')
  result.append(dict(file=name,address=hex(address),bytes=len(blob),context=context,non_atomic=True))
 return result

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--shutdown-stack',action='store_true',help='Short read-only Nav backtraces/registers/mappings and peer waits; never requests shutdown');p.add_argument('--state',choices=('broken','healthy'));p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--ask-password',action='store_true');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=60);a=p.parse_args(argv)
 if not 1<=a.port<=65535 or not 1<=a.telnet_port<=65535 or not 10<=a.timeout<=120:p.error('Invalid ports/timeout')
 if any(ord(c)<32 or ord(c)==127 for v in (a.host,a.username,a.telnet_user) for c in v):p.error('Control characters in connection arguments')
 if not a.run:print('Plan only. Read-only threads/fds/memory/times for map services. Use --run --state broken or --run --state healthy. No restart, preload, video writes, or replay.');return 0
 if not a.state:p.error('--state broken or --state healthy is required; this is your observed screen state')
 token=uuid.uuid4().hex;remote='/ramdisk/delphi-map-state_'+token;base=ROOT/'delphi-dump'
 for parent in (base,*base.parents):d.reject_link(parent)
 base.mkdir(exist_ok=True);folder=base/('_map_session_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+token[:8]);folder.mkdir();summary=dict(kind='readonly_map_session_snapshot',user_reported_state=a.state,remote=remote,service_restarts=False,preload=False,video_writes=False,shutdown_stack=a.shutdown_stack,artifacts=[],errors=[],commands=[]);shell=None;password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser';total=0
 def persist():(folder/'map-session-summary.json').write_text(json.dumps(summary,indent=2))
 def fetch(name):
  nonlocal total
  blob=bytearray()
  def receive(block):
   if len(blob)+len(block)>2*1024*1024 or total+len(blob)+len(block)>32*1024*1024:raise ValueError('Snapshot transfer exceeds bound')
   blob.extend(block)
  with ftplib.FTP(timeout=a.timeout) as ftp:
   progress('Connecting to the head unit over FTP.', key='ftp', interval=10)
   ftp.connect(a.host,a.port);ftp.login(a.username,password);ftp.voidcmd('TYPE I');ftp.retrbinary('RETR '+remote+'/'+name,receive)
  b=bytes(blob);total+=len(b);(folder/name).write_bytes(b);summary['artifacts'].append(dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));persist();return b
 def capture(name,command):
  code=shell.command(command+' > '+name+' 2>&1',required=False);summary['commands'].append(dict(file=name,command=command,exit_code=code));shell.command('chmod 644 '+name);b=fetch(name)
  if code:summary['errors'].append(dict(file=name,error='command exit '+str(code)))
  return b
 persist()
 try:
  shell=Shell(a,folder);shell.command('mkdir '+remote);shell.command('cd '+remote)
  before=processes(capture('processes-before.txt','pidin arguments'));summary['processes_before']=before
  if not all(n in before for n in ('NavigationServer','Most','TransportServer','DisplayManagement','screen-cda')):raise ValueError('Required map services are absent; process inventory retained')
  selected={n:before[n] for n in ('NavigationServer','Most','screen-cda')} if a.shutdown_stack else before
  for passno in (1,2):
   print('Read-only snapshot',passno,'of 2:',a.state,flush=True)
   for name,pid in selected.items():
    print(' ',name,pid,flush=True)
    views=(('threads','backtrace','regs','mem') if name=='NavigationServer' else ('threads',)) if a.shutdown_stack else ('threads','fds','mem','times')
    for view in views:capture(name+'-'+str(passno)+'-'+view+'.txt','pidin -p '+str(pid)+' '+view)
   if passno==1:time.sleep(2)
  after=processes(capture('processes-after.txt','pidin arguments'));summary['processes_after']=after;summary['same_process_ids']=before==after
  capture('system-log.txt','sloginfo -t')
  capture('nav-coredump-metadata.txt','ls -lt /sdc1/coredumps /sdc2/coredumps')
  summary['collection_complete']=True
 except (OSError,EOFError,ValueError,RuntimeError,KeyboardInterrupt,ftplib.Error) as e:summary['errors'].append(dict(error=(type(e).__name__+': '+str(e)).replace(password,'[redacted]')))
 finally:
  if shell:summary['actions']=shell.actions;shell.close()
  persist()
 print('Saved:',folder);print('No services restarted; no video was sent. Return the entire folder.');return 0 if summary.get('collection_complete') else 2
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        raise SystemExit(main())
