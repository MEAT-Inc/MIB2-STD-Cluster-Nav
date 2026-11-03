"""Targeted FTP collection; optional root-shell copies to a fresh RAM-disk directory."""
from project_console import console_session, log as print
import argparse, ftplib, getpass, json, re, shlex, socket, sys, uuid
import delphi_inventory as d

TARGETS = ('screen-cda', 'libscreen.so.1', 'libXSAL.so')
SEARCH_DIRS = ('/proc/boot', '/extbin/apps/bin', '/extbin/apps/lib',
               '/extbin/apps/usr/bin', '/extbin/apps/usr/lib', '/ifs2', '/lib', '/usr/lib',
               '/extbin/apps/usr/lib/graphics', '/extbin/apps/usr/lib/graphics/jacinto6',
               '/usr/lib/graphics')

def select_targets(directory, entries):
    if directory not in SEARCH_DIRS:
        raise ValueError('Directory is outside fixed search scope')
    return [(directory+'/'+name,size) for name,kind,size in entries
            if name in TARGETS and kind in ('file','link')]

def copy_command(source, stage_dir, index):
    parent, name = source.rsplit('/',1)
    if parent not in SEARCH_DIRS or name not in TARGETS:
        raise ValueError('Source is not an allowlisted target')
    if not re.fullmatch(r'/ramdisk/delphi-stage_[0-9a-f]{32}',stage_dir):
        raise ValueError('Invalid temporary RAM-disk directory')
    if not 0 <= index < 100:
        raise ValueError('Invalid staging index')
    destination=stage_dir+'/'+str(index).zfill(2)+'_'+name
    return 'cp '+shlex.quote(source)+' '+shlex.quote(destination),destination

def completion_command(command, marker):
    if not re.fullmatch(r'DS[0-9a-f]{8}', marker):
        raise ValueError('Invalid completion marker')
    # The echoed input contains literal $?; only executed output has digits.
    return command+'; echo '+marker+':$?:END'

def target_availability(transfers, records):
    good={r.get('remote_path'):r for r in records
          if r.get('status') in ('downloaded','existing_not_downloaded') and r.get('bytes',0)>0}
    ready=set()
    for transfer in transfers:
        row=good.get(transfer['ftp_remote_path'])
        if row and (transfer['expected_bytes'] is None or row['bytes']==transfer['expected_bytes']):
            ready.add(transfer['source_remote_path'].rsplit('/',1)[1])
    return {name: ('available_locally' if name in ready else 'not_collected') for name in TARGETS}

class StagingSession:
    def __init__(self,c):
        self.c=c;self.sock=None;self.transcript=None;self.root='/ramdisk/delphi-stage_'+uuid.uuid4().hex
    def start(self):
        a=self.c.a
        self.c.log('Telnet staging: connecting to root shell on port '+str(a.telnet_port))
        self.sock=socket.create_connection((a.host,a.telnet_port),timeout=a.telnet_timeout)
        self.reader=d.TelnetReader(self.sock,a.telnet_timeout)
        prompts=[('login',re.compile(rb'(?i)(?:login|username):\s*$')),
                 ('password',re.compile(rb'(?i)password:\s*$')),('shell',self.reader.PROMPT)]
        label,_=self.reader.read_until(prompts)
        if label=='login':
            self.c.log('Telnet staging: sending login name')
            self.reader.send(a.telnet_user);label,_=self.reader.read_until(prompts)
        if label=='password':
            password=a.telnet_password
            if password is None:password=getpass.getpass('Telnet password (Enter if blank): ')
            self.reader.send(password);label,_=self.reader.read_until(prompts)
        if label!='shell':raise ValueError('Telnet authentication did not reach a shell')
        self.c.log('Telnet staging: root shell ready')
        self.transcript=(self.c.run/'staging-actions.txt').open('x',encoding='utf-8')
        self.run('mkdir '+self.root)
        self.c.log('Temporary copies only in '+self.root+'; originals remain unchanged.')
    def run(self,command):
        marker='DS'+uuid.uuid4().hex[:8]
        wire=completion_command(command,marker)
        self.c.log('Telnet staging command: '+command)
        self.transcript.write('COMMAND '+wire+'\n');self.transcript.flush()
        done=re.compile(marker.encode()+rb':([0-9]+):END')
        def save(data):
            # Store escaped bytes so CR/NUL/negotiation-related formatting is visible.
            self.transcript.write('RECV '+repr(data)+'\n');self.transcript.flush()
        try:
            self.reader.send(wire)
            _,response=self.reader.read_until([('done',done)],on_data=save)
        except (OSError,EOFError,ValueError) as exc:
            raise OSError('No command completion received; session stopped. Inspect staging-actions.txt. '+str(exc)) from exc
        code=int(done.search(response).group(1))
        self.c.log('Telnet staging command completed: exit '+str(code))
        if code:raise OSError('Temporary-copy command failed with exit '+str(code))
    def close(self):
        if self.transcript:self.transcript.close()
        if self.sock:self.sock.close()

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',default='192.168.1.4');p.add_argument('--port',type=int,default=21)
    p.add_argument('--username',default='ftpuser');p.add_argument('--ask-password',action='store_true')
    p.add_argument('--output',default=d.DEFAULT_OUTPUT,help='Shared project delphi-dump folder')
    p.add_argument('--timeout',type=float,default=30);p.add_argument('--retries',type=int,default=2)
    p.add_argument('--encoding',default='utf-8')
    p.add_argument('--stage-boot-files',action='store_true',help='Use root Telnet to copy /proc/boot targets into a fresh /ramdisk directory before FTP download; leaves temporary copies until reboot')
    p.add_argument('--telnet-port',type=int,default=23);p.add_argument('--telnet-user',default='root')
    p.add_argument('--ask-telnet-password',action='store_true')
    p.add_argument('--telnet-timeout',type=float,default=10,help='Timeout for each Telnet phase/command, separate from FTP')
    supplied=p.parse_args(argv)
    if not 1<=supplied.port<=65535 or not 1<=supplied.telnet_port<=65535 or supplied.timeout<=0 or supplied.retries<0 or supplied.telnet_timeout<=0:
        p.error('Invalid port, timeout or retries')
    if any(ord(x)<32 or ord(x)==127 for v in (supplied.host,supplied.username,supplied.telnet_user) for x in v):
        p.error('Control characters in connection arguments')
    a=d.parser().parse_args([]);vars(a).update(vars(supplied))
    a.password=getpass.getpass('FTP password: ') if a.ask_password else 'ftpuser'
    a.telnet_password=getpass.getpass('Telnet password (Enter if blank): ') if a.ask_telnet_password else None
    d.FILES=();d.ROOTS=()
    try:c=d.Collector(a)
    except (OSError,ValueError) as exc:
        print('Cannot initialize output:',exc,file=sys.stderr);return 1
    interrupted=False;found=[];unavailable=[];staging=None;transfers=[];staged_bytes=0;staging_failed=False
    try:
        c.log('Targeted collection. Boot-file staging '+('enabled' if a.stage_boot_files else 'disabled')+'.')
        c.retry('Initial FTP connection',lambda:None)
        for directory in SEARCH_DIRS:
            retries=a.retries;a.retries=0
            c.log('Searching '+directory)
            try:entries=c.listing(directory)
            except (OSError,EOFError,ftplib.Error,ValueError) as exc:
                unavailable.append({'directory':directory,'error':c.clean(exc)})
                c.log('Candidate directory unavailable: '+directory);continue
            finally:a.retries=retries
            chosen=select_targets(directory,entries)
            c.record(directory,'listed',selected_paths=[path for path,size in chosen]);found.extend(chosen)
        d.FILES=tuple(path for path,size in found)
        for index,(path,size) in enumerate(found):
            transfer_path=path
            if a.stage_boot_files and path.startswith('/proc/boot/'):
                if staging_failed:
                    c.record(path,'failed',stage='ramdisk_copy',error='Skipped: prior staging session failed; see staging-actions.txt')
                    continue
                try:
                    if size is None or size<=0 or staged_bytes+size>8*1024*1024:
                        raise ValueError('Boot staging requires a positive listed size and at most 8 MiB total')
                    if staging is None:
                        staging=StagingSession(c);staging.start()
                    command,transfer_path=copy_command(path,staging.root,index)
                    staging.run(command);staged_bytes+=size
                except (OSError,EOFError,ValueError) as exc:
                    staging_failed=True
                    c.log('RAM-disk staging failed: '+c.clean(exc)+'. Remaining boot files will be skipped; other FTP downloads continue.')
                    c.record(path,'failed',stage='ramdisk_copy',error=c.clean(exc));continue
            transfers.append({'source_remote_path':path,'ftp_remote_path':transfer_path,'expected_bytes':size})
            c.download(transfer_path,size)
        missing=[name for name in TARGETS if not any(path.rsplit('/',1)[1]==name for path,size in found)]
        for name in missing:
            c.record(None,'failed',stage='locate_target',target_basename=name,error='Not found in successful fixed directory listings')
        availability=target_availability(transfers,c.records)
        c.log('Target availability: '+', '.join(name+'='+state for name,state in availability.items()))
        report={'target_availability':availability,'all_targets_available':all(v=='available_locally' for v in availability.values()),'targets':TARGETS,'found_paths':d.FILES,'missing_basenames':missing,'transfers':transfers,
                'temporary_ramdisk_directory':staging.root if staging else None,
                'unavailable_candidate_directories':unavailable,
                'note':'Located copies do not prove loaded paths. Original files unchanged; staging, if enabled, creates only new temporary RAM-disk files.'}
        with (c.run/'runtime-targets.json').open('x',encoding='utf-8') as f:json.dump(report,f,indent=2)
    except KeyboardInterrupt:
        interrupted=True;c.log('Interrupted; partial downloads are not complete binaries.')
    except Exception as exc:
        interrupted=True;c.record(None,'failed',stage='runtime_collection',error=c.clean(exc))
    finally:
        if staging:staging.close()
    return c.finish(interrupted)

if __name__ == '__main__':
    with console_session(__file__, __doc__):
        sys.exit(main())
