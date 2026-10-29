"""Real loopback tests of the same C source; only bounds shortened in test binary."""
import hashlib,json,os,re,shutil,signal,socket,subprocess,tempfile,threading,time
from pathlib import Path
ROOT=Path('/src');BASE=ROOT/'native/trace-reader'
os.environ['PATH']='/usr/bin:/bin'
work=Path(tempfile.mkdtemp(prefix='trace-reader-host-'));source=work/'reader.c';source.write_bytes((BASE/'reader.c').read_bytes())
for name,defines in (('production',[]),('short',['-DTRACE_SECONDS=2','-DTRACE_BYTES=32768'])):
 subprocess.run(['gcc','-std=gnu99','-O2','-Wall','-Wextra','-Werror',*defines,str(source),'-o',str(work/name)],check=True)
Path('/ramdisk').mkdir(exist_ok=True);results=[]
def case(name,executable,mode,leader=False):
 root=Path('/ramdisk/delphi-trace-reader_'+hashlib.sha256(name.encode()).hexdigest()[:32]);root.mkdir()
 ready=threading.Event();sent=bytearray();errors=[]
 def server():
  try:
   with socket.socket() as listener:
    listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);listener.bind(('127.0.0.1',15361));listener.listen(1);listener.settimeout(8);ready.set()
    with listener.accept()[0] as client:
     if mode=='duration':client.sendall(b'hello\x00trace');time.sleep(3)
     elif mode=='empty':pass
     elif mode=='eof':client.sendall(b'raw\x00\xff');sent.extend(b'raw\x00\xff')
     else:
      block=bytes(range(256))*256
      for i in range(260):
       try:client.sendall(block);sent.extend(block)
       except (BrokenPipeError,ConnectionResetError):break
  except Exception as exc:errors.append(repr(exc));ready.set()
 if mode!='refused':
  t=threading.Thread(target=server);t.start();assert ready.wait(3)
 p=subprocess.Popen([str(executable),str(root)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=leader)
 if mode=='duration':
  line=p.stdout.readline();assert b'TRACE_READER_READY' in line;reader_pid=int(re.search(rb'pid=(\d+)',line).group(1));os.kill(reader_pid,signal.SIGHUP)
  if leader:assert reader_pid!=p.pid
 out,err=p.communicate(timeout=10)
 if mode!='refused':t.join(6);assert not t.is_alive(),name
 assert not errors,(name,errors)
 text=(root/'trace-report.txt').read_text();raw=(root/'trace.bin').read_bytes()
 assert 'bytes='+str(len(raw))+' ' in text,(name,text)
 if mode=='duration':assert p.returncode==0 and 'reason=duration' in text and raw==b'hello\x00trace'
 if mode=='cap':
  expected=16777216 if executable.name=='production' else 32768
  assert p.returncode==0 and len(raw)==expected and 'reason=byte_limit' in text
  assert raw==(bytes(range(256))*(len(raw)//256))
 if mode=='eof':assert p.returncode==2 and raw==sent and 'reason=peer_closed' in text
 if mode=='empty':assert p.returncode==2 and not raw and 'reason=peer_closed' in text
 if mode=='refused':assert p.returncode==2 and 'reason=error' in text and not raw
 # Existing output files cannot be overwritten.
 original=(root/'trace-report.txt').read_bytes();retry=subprocess.run([str(executable),str(root)],capture_output=True,timeout=4)
 assert retry.returncode==5 and (root/'trace-report.txt').read_bytes()==original
 results.append(dict(case=name,passed=True,exit_code=p.returncode,bytes=len(raw),report=text.strip()))
for name,exe,mode in (('duration-hangup',work/'short','duration'),('short-cap',work/'short','cap'),('production-cap',work/'production','cap'),('short-eof',work/'short','eof'),('short-empty',work/'short','empty'),('refused',work/'short','refused')):case(name,exe,mode)
case('process-group-leader',work/'short','duration',True)
r=subprocess.run([str(work/'short'),'/ramdisk/bad'],capture_output=True);assert r.returncode==3
report=dict(scope='Linux real loopback of same C source; bounds shortened only for duration tests; no QNX network execution claim',cases=results,invalid_root_rejected=True,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),qnx_binary_sha256=hashlib.sha256((BASE/'build/trace_reader').read_bytes()).hexdigest())
(BASE/'host-tests.json').write_text(json.dumps(report,indent=2));print('TRACE_READER_HOST_PASS: seven real-loopback cases, SIGHUP survival, exact production 16MiB cap, binary preservation, overwrite/root refusal.')
