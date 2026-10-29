"""Generate exact actual-Shell.command wire for QNX ksh parse-only regression tests."""
import hashlib,io,json
from pathlib import Path
from run_phone_trace import launch_command,PREFIX
from run_observer_smoke import Shell
ROOT=Path(__file__).resolve().parents[1]
def main():
 class Reader:
  def send(self,wire):self.wire=wire
  def read_until(self,patterns,on_data=None):
   marker=patterns[0][1].pattern.split(b':')[0]
   return 'done',marker+b':0:END'
 shell=Shell.__new__(Shell);shell.broken=False;shell.actions=[];shell.transcript=io.StringIO();shell.reader=Reader()
 shell.command(launch_command(PREFIX+'a'*32));good=shell.reader.wire+'\n'
 bad=good.replace(' & delphi_trace_job=$!;', ' &;')
 assert good!=bad and '&;' not in good and '&;' in bad
 q=ROOT/'native/trace-reader/qemu';q.mkdir(exist_ok=True)
 (q/'launch-good.sh').write_bytes(good.encode());(q/'launch-bad.sh').write_bytes(bad.encode())
 record={n:hashlib.sha256((ROOT/'scripts'/n).read_bytes()).hexdigest() for n in ('run_phone_trace.py','run_observer_smoke.py')}
 (q/'shell-source-hashes.json').write_text(json.dumps(record,indent=2))
 print('Generated actual Shell.command wire; valid & assignment and invalid &; control.')
if __name__=='__main__':main()
