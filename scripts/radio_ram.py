"""Space preflight and hash-verified pruning of archived completed RAM tests only."""
import ftplib,hashlib,json,re,struct
from pathlib import Path
from project_console import status
ACTIVE=('/dev/shmem/delphi-aa-observer-active.bin','/dev/shmem/delphi-nav-launch-active.bin')
MIN_FREE=30*1024*1024
# QNX6.4 df -P is POSIX format; -k reports1024-byte units:
# https://www.qnx.net/developers/docs/6.4.0/neutrino/utilities/d/df.html

def df_available(response):
 rows=[]
 for line in response.replace(b'\r',b'\n').splitlines():
  m=re.fullmatch(rb'\s*(\S+)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+\d+%\s+(\S+)\s*',line)
  if m:rows.append(max(0,int(m[4]))*1024)
 if len(rows)!=1:raise ValueError('Cannot parse QNX RAM-disk free space; no applications were launched')
 return rows[0]

def validate_entry(e):
 if not re.fullmatch(r'/ramdisk/delphi-(?:aa-observer|nav-bridge)_[0-9a-f]{32}',e['root']):raise ValueError('Invalid archived RAM root')
 if e['marker'].get('name')!='controller.bin' or e['marker'].get('bytes')!=512:raise ValueError('Archived restoration proof missing')
 for x in [e['marker'],*e['files']]:
  if not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]*',x['name']) or not re.fullmatch(r'[0-9a-f]{64}',x['sha256']) or not 0<=x['bytes']<=16*1024*1024:raise ValueError('Unsafe archived file entry')
 return e

def matches(ftp,path,e):
 try:
  if ftp.size(path)!=e['bytes']:return False
  h=hashlib.sha256();n=0
  def chunk(b):
   nonlocal n
   n+=len(b)
   if n>e['bytes']:raise ValueError('Archived remote file grew')
   h.update(b)
  ftp.retrbinary('RETR '+path,chunk)
  return n==e['bytes'] and h.hexdigest()==e['sha256']
 except (ftplib.error_perm,ValueError):return False

def marker_valid(ftp,e):
 try:
  if ftp.size(e['root']+'/controller.bin')!=512:return False
  data=bytearray()
  def bounded(b):
   if len(data)+len(b)>512:raise ValueError('Controller proof grew')
   data.extend(b)
  ftp.retrbinary('RETR '+e['root']+'/controller.bin',bounded)
  if len(data)!=512 or hashlib.sha256(data).hexdigest()!=e['marker']['sha256']:return False
  if '/delphi-aa-observer_' in e['root']:
   from run_disconnected_observer import validate_report
   validate_report(bytes(data),e['root'],False,struct.unpack_from('<I',data,256)[0])
  else:
   from run_cluster_replay import assess_controller
   assess_controller(bytes(data),e['root'],True)
  return True
 except (ftplib.error_perm,ValueError):return False

def build_cleanup_plan(root):
 entries=[]
 for folder in sorted((root/'delphi-dump').iterdir(),reverse=True):
  if not folder.is_dir():continue
  aa=(folder/'disconnect-summary.json').exists();nav=(folder/'replay-summary.json').exists()
  if not aa and not nav:continue
  try:
   summary=json.loads((folder/('disconnect-summary.json' if aa else 'replay-summary.json')).read_text())
   if summary.get('cleanup_pending') or not summary.get('controller_trial_passed' if aa else 'restoration_verified'):continue
   target=summary.get('remote_directory' if aa else 'remote');marker=(folder/'controller.bin').read_bytes()
   if aa:
    from run_disconnected_observer import validate_report
    validate_report(marker,target,False,struct.unpack_from('<I',marker,256)[0])
   else:
    from run_cluster_replay import assess_controller
    assess_controller(marker,target,True)
   files={}
   for a in summary.get('artifacts',[]):
    if not isinstance(a,dict) or not a.get('file'):continue
    p=folder/a['file']
    if p.is_file() and p.name==a['file']:
     b=p.read_bytes()
     if len(b)==a.get('bytes') and hashlib.sha256(b).hexdigest()==a.get('sha256'):files[p.name]=dict(name=p.name,bytes=len(b),sha256=a['sha256'])
   if nav:
    manifest=json.loads((folder/'release-manifest.json').read_text())
    for name,v in {**manifest.get('files',{}),**manifest.get('references',{})}.items():files[name]=dict(name=name,bytes=v['bytes'],sha256=v['sha256'])
   entry=dict(root=target,marker=dict(name='controller.bin',bytes=512,sha256=hashlib.sha256(marker).hexdigest()),files=[x for x in files.values() if 65536<=x['bytes']<=16*1024*1024])
   validate_entry(entry);entries.append(entry)
  except (OSError,ValueError,KeyError,TypeError,struct.error):continue
 return dict(version=1,required_bytes=MIN_FREE,entries=entries)

def prepare_space(shell,args,password,plan_path,journal=None,expected_sha=None):
 raw=plan_path.read_bytes()
 if expected_sha is not None and hashlib.sha256(raw).hexdigest()!=expected_sha:raise ValueError('Archived cleanup plan differs from release')
 plan=json.loads(raw);entries=[validate_entry(e) for e in plan['entries']];report=dict(required_bytes=MIN_FREE,deleted=[],skipped_roots=[])
 def save():
  if journal:journal.write_text(json.dumps(report,indent=2))
 def free():
  shell.command('df -Pk /ramdisk');return df_available(shell.last_response)
 def inactive():
  for path in ACTIVE:
   if shell.command('test ! -e '+path,required=False):raise RuntimeError('An existing test controller is active; keep its bundle and complete its cleanup before retrying')
 report['free_before']=free();save();inactive()
 if report['free_before']>=MIN_FREE:report['free_after']=report['free_before'];return report
 inactive();shell.command('pidin arguments');processes=shell.last_response
 with ftplib.FTP(timeout=args.timeout) as ftp:
  ftp.connect(args.host,args.port);ftp.login(args.username,password);ftp.voidcmd('TYPE I')
  for e in entries:
   root=e['root'];inactive()
   if root.encode() in processes or not marker_valid(ftp,e):report['skipped_roots'].append(root);continue
   for f in sorted(e['files'],key=lambda x:x['bytes'],reverse=True):
    if f['name']=='controller.bin':continue
    path=root+'/'+f['name']
    if not matches(ftp,path,f):continue
    inactive();ftp.delete(path);report['deleted'].append(dict(path=path,bytes=f['bytes'],sha256=f['sha256']));save()
    status('Reclaimed archived test file: '+f['name'])
    if free()>=MIN_FREE:break
   if free()>=MIN_FREE:break
 report['free_after']=free();save()
 if report['free_after']<MIN_FREE:raise RuntimeError('RAM disk still has only '+str(report['free_after']//1048576)+'MiB free; this combined test needs30MiB. No apps were launched. Reboot the radio once to clear old RAM files, wait for factory maps, then rerun this same command.')
 return report
