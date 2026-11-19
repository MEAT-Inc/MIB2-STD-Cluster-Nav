"""Collect exact startup files and filesystem evidence without changing the radio."""
from pathlib import Path
import argparse,datetime as dt,ftplib,getpass,json,hashlib,uuid
from collect_observer_preflight import inventory
from project_console import console_session,log as print
import delphi_inventory as d
COMMANDS=(('system','uname -a'),('mounts','mount'),('space','df -h'),
 ('procman-arguments','pidin -p procman arguments'),('procman-fds','pidin -p procman fds'),
 ('paths','ls -ld /etc /etc/procman_core.cfg /extbin /extbin/apps/hmi/HMI /extbin/apps/hmi/HMI/runHMI.sh /persistence /extbin/.boot /ffs'),
 ('backing','ls -l /etc/procman_core.cfg /extbin/apps/hmi/HMI/runHMI.sh'),
 ('procman-config','cat /etc/procman_core.cfg'),('startup-script','cat /extbin/apps/hmi/HMI/runHMI.sh'),
 ('boot-directories','ls -la /extbin/.boot /etc/rc.d /etc/rcscripts /ffs'))
def collect(args,folder,password):
 out=Path(folder)/'deployment-preflight';out.mkdir(exist_ok=True)
 rows,responses=inventory(args,out,commands=COMMANDS)
 report=dict(read_only=True,commands=rows,files=[],persistent_write_performed=False)
 try:
  with ftplib.FTP(timeout=args.timeout) as ftp:
   ftp.connect(args.host,args.port);ftp.login(args.username,password)
   for remote,name in (('/extbin/apps/hmi/HMI/runHMI.sh','runHMI.sh'),('/etc/procman_core.cfg','procman_core.cfg')):
    chunks=[];size=0
    def save(b):
     nonlocal size
     size+=len(b)
     if size>1048576:raise ValueError('Startup evidence exceeds1MiB')
     chunks.append(b)
    try:
     ftp.retrbinary('RETR '+remote,save);b=b''.join(chunks);(out/name).write_bytes(b)
     report['files'].append(dict(path=remote,file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    except ftplib.error_perm as e:report['files'].append(dict(path=remote,error=str(e)))
 except (OSError,EOFError,ftplib.Error,ValueError) as exc:
  report['ftp_error']=type(exc).__name__+': '+str(exc)
 (out/'preflight-summary.json').write_text(json.dumps(report,indent=2));return report
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true')
 p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21);p.add_argument('--username',default='ftpuser');p.add_argument('--ask-password',action='store_true');p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root');p.add_argument('--timeout',type=float,default=90)
 a=p.parse_args(argv)
 if not(1<=a.port<=65535 and 1<=a.telnet_port<=65535 and 5<=a.timeout<=180):p.error('Invalid ports or timeout')
 if not a.run:print('Plan only. Read startup scripts, mounts and procman evidence. No remote writes. Add --run with Ethernet connected.');return 0
 base=Path(__file__).resolve().parents[1]/'delphi-dump'
 for parent in (base,*base.parents):d.reject_link(parent)
 base.mkdir(exist_ok=True)
 folder=base/('_deployment_preflight_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);folder.mkdir()
 password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
 report=collect(a,folder,password)
 print('Saved read-only startup evidence: '+str(folder))
 good=any(r.get('file')=='runHMI.sh' for r in report['files'])
 print('Startup script captured.' if good else 'Startup script unavailable; return this partial collection for review.')
 return 0 if good else 2
if __name__=='__main__':
 with console_session(__file__,__doc__):raise SystemExit(main())
