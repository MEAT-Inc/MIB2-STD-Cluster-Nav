"""Package only QNX-tested private-path fixtures; no vehicle connection."""
from project_console import console_session, log as print
from pathlib import Path
import hashlib,json,re,shutil,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/".tools/python"))
from elftools.elf.elffile import ELFFile
from run_observer_path_test import assess,NAMES,MARKERS
BASE=ROOT/"native/observer/path-test"
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 q=BASE/"qemu";log=(q/"qemu.log").read_text(errors="replace")
 for marker in (*MARKERS,"PATH_QNX_SUITE_PASS","PATH_INVALID_FACTORY_TARGET_REJECTED","PATH_QNX_END"):
  if marker not in log.splitlines():raise ValueError("QNX evidence missing: "+marker)
 if not re.search(r"Process \d+ \(path_qemu_runner\) exited status=0[.]",log):raise ValueError("Emulator runner failed")
 if "terminated SIG" in log or "PATH_CHECK_FAILED" in log:raise ValueError("Fatal QNX test result")
 blobs={"path-test.txt":log.encode(),"stock-before.txt":b"99999999 AndroidAuto -t\n","stock-after.txt":b"99999999 AndroidAuto -t\n"}
 for label,name in (("PATH_REPORT_HEX","report.bin"),("PATH_TRACE_HEX","observer.bin")):
  matches=re.findall(r"^"+label+r" ([0-9a-f]+)\r?$",log,re.M)
  if len(matches)!=1:raise ValueError("Missing/ambiguous QNX evidence: "+label)
  blobs[name]=bytes.fromhex(matches[0]);(q/name).write_bytes(blobs[name])
 reviewed=assess(blobs);reviewed.pop("decoded_log")
 reviewed.update(scope="Private-path QNX emulation; stock snapshots above are offline fixtures",qnx_log_sha256=sha((q/"qemu.log").read_bytes()))
 (q/"summary.json").write_text(json.dumps(reviewed,indent=2))
 tested={line.split()[1]:line.split()[0] for line in (q/"tested.sha256").read_text().splitlines()}
 sources={name:BASE/"build"/name for name in NAMES}
 sources["libdelphi_observer.so"]=ROOT/"native/observer/release/libdelphi_observer.so"
 sources["libautoreceiver.so"]=ROOT/"native/observer/smoke/build/libautoreceiver.so"
 original=json.loads((ROOT/"native/observer/release/manifest.json").read_text())["sha256"]
 if sha(sources["libdelphi_observer.so"].read_bytes())!=original:raise ValueError("Observer candidate changed")
 records={}
 for name,p in sources.items():
  data=p.read_bytes()
  if not data or len(data)>128*1024 or sha(data)!=tested.get(name):raise ValueError("Stale/invalid tested file: "+name)
  with p.open("rb") as stream:
   e=ELFFile(stream);needs=[]
   if e["e_machine"]!="EM_ARM" or e.elfclass!=32 or not e.little_endian or e["e_flags"]>>24!=5 or e["e_flags"]&0x400:raise ValueError("Wrong ARM ABI")
   for seg in e.iter_segments():
    if seg["p_type"]=="PT_GNU_STACK" and seg["p_flags"]&1:raise ValueError("Executable stack")
    if seg["p_type"]=="PT_DYNAMIC":needs += [t.needed for t in seg.iter_tags() if t.entry.d_tag=="DT_NEEDED"]
   expected={"libc.so.3","libautoreceiver.so"} if name in ("path_child","path_original") else {"libc.so.3"}
   if set(needs)!=expected:raise ValueError("Unexpected dependencies: "+name+repr(needs))
  records[name]=dict(bytes=len(data),sha256=sha(data),needed=needs)
 if records["path_child"]["sha256"]!=records["path_original"]["sha256"]:raise ValueError("Original copy differs")
 release=BASE/"release";release.mkdir(exist_ok=True)
 for name,p in sources.items():shutil.copy2(p,release/name)
 manifest=dict(kind="isolated_observer_path_test",files=records,qnx_emulation_passed=True,
  vehicle_validated=False,no_stock_app_control=True,qnx_log_sha256=reviewed["qnx_log_sha256"])
 (release/"manifest.json").write_text(json.dumps(manifest,indent=2))
 shutil.copy2(BASE/"README.txt",release/"README.txt")
 files=[ROOT/"scripts"/name for name in ("run_observer_path_test.py","run_observer_smoke.py","delphi_inventory.py","project_console.py","decode_delphi_observer.py")]
 files += [release/name for name in (*NAMES,"manifest.json","README.txt")]
 bundle=BASE/"observer-path-test-laptop.zip"
 with zipfile.ZipFile(bundle,"w",zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,p.relative_to(ROOT).as_posix())
 print("PASS: exact five native files passed QNX emulation and Python evidence assessment.")
 print("Portable bundle:",bundle)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
