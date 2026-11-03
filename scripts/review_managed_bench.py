"""Audit the emulated real-manager integration evidence; never connect to a car."""
from project_console import console_session, log as print
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
MARKERS=("MANAGED_EXIT_STATUS_ENCODING_PASS encoded=1792",
 "MANAGED_REAL_OBSERVER_CAPTURE_PASS","MANAGED_REAL_STOCK_RESTORE_PASS",
 "MANAGED_REAL_PROCMAN_RESTART_AND_CLEAN_EXIT_PASS","MANAGED_QNX_END",
 "Process 3 (managed_runner) exited status=0.")
def assess(log):
 for marker in MARKERS:
  if marker not in log:raise ValueError("Missing evidence: "+marker)
 if "MANAGED_SUITE_FAIL" in log or "MANAGED_MANAGER_EARLY_EXIT" in log:
  raise ValueError("Guest reported failure")
 rows=re.findall(r"MANAGED_CHILD count=(\d+) pid=(\d+) ppid=(\d+) argc=(\d+) arg0=(\S+) arg1=(\S+) extra=([^\r\n]*)",log)
 if len(rows)!=4:raise ValueError("Expected exactly four managed launches")
 manager=int(rows[0][2]);pids=[]
 for i,row in enumerate(rows,1):
  count,pid,ppid,argc,path,arg,extra=row
  if int(count)!=i or int(ppid)!=manager or path!="/proc/boot/managed_child" or arg!="-t":
   raise ValueError("Process parent, executable or argument mismatch")
  if int(argc)!=(2 if i==1 else 3) or extra!=("" if i==1 else "-X1792" if i==2 else "-X2"):
   raise ValueError("Manager restart argument was not preserved")
  pids.append(int(pid))
 if len(set(pids))!=4 or manager in pids:raise ValueError("Unexpected process identities")
 observed=re.findall(r"MANAGED_OBSERVER observed=(\d+) records=(\d+)",log)
 if len(observed)!=4 or [int(x[0]) for x in observed]!=[0,0,1,0] or not 1<=int(observed[2][1])<=9:
  raise ValueError("Observer injection/restoration was not demonstrated")
 if any(int(observed[i][1]) for i in (0,1,3)):raise ValueError("Stock launch reported observer records")
 expected={(pids[1],"managed_child","SIGINT"),(pids[2],"managed_original","SIGINT"),(manager,"procman.captured","SIGTERM")}
 signals=re.findall(r"Process (\d+) \(([^)]+)\) terminated (SIG\w+) code=(\d+) by process (\d+) value=(\d+)\.",log)
 if len(signals)!=3 or {(int(p),n,s) for p,n,s,c,by,v in signals}!=expected:
  raise ValueError("Unexpected signal termination")
 if any(c!="0" or by!="3" or v!="0" for p,n,s,c,by,v in signals):raise ValueError("Unexpected signal sender")
 if len(re.findall("terminated SIG",log))!=3:raise ValueError("Unparsed fatal signal")
 if "MANAGED_SIGNAL_RESTART count=3 code=2 expected=2" not in log:raise ValueError("Signal restart not verified")
 if f"Process {pids[0]} (managed_child) exited status=7." not in log or f"Process {pids[3]} (managed_child) exited status=0." not in log:
  raise ValueError("Child exit status evidence missing")
 return dict(passed=True,manager_pid=manager,child_pids=pids,observed_records=int(observed[2][1]),
  raw_status_after_exit_7=1792,raw_status_after_sigint=2,
  scope="Captured procman plus synthetic apps in QNX emulation only",
  actual_androidauto_interposition_tested=False,vehicle_deployment_ready=False)
def main():
 base=ROOT/"native/observer/managed-bench";q=base/"qemu"
 result=assess((q/"qemu.log").read_text(errors="replace"));bound={}
 for line in (q/"tested.sha256").read_text().splitlines():
  digest,name=line.split()
  if name=="procman.captured":p=ROOT/"delphi-dump/_observer_smoke_20261029_005129_a1ecf3ce"/name
  elif name=="libdelphi_observer.so":p=ROOT/"native/observer/release"/name
  elif name=="libautoreceiver.so":p=ROOT/"native/observer/smoke/build"/name
  elif name=="libsocket.so.3":continue # sysroot artifact; container SHA is retained as evidence.
  else:p=base/"build"/name
  if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError("Stale tested artifact: "+name)
  bound[name]=digest
 result["artifacts"]=bound
 result["log_sha256"]=hashlib.sha256((q/"qemu.log").read_bytes()).hexdigest()
 result["source_hashes"]={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in base.iterdir() if p.is_file()}
 (q/"summary.json").write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
