"""Package the guarded real-app experiment after native emulation; no network."""
from project_console import console_session, log as print, status
from pathlib import Path
import hashlib,io,json,re,shutil,struct,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/".tools/python"))
from elftools.elf.elffile import ELFFile
from decode_delphi_observer import decode
from run_androidauto_observer import NAMES,REFERENCES,KNOWN_REGISTRATION_CALLERS
BASE=ROOT/"native/observer/launch"
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 q=BASE/"qemu";log=(q/"qemu.log").read_text(errors="replace")
 markers=("LAUNCH_IDENTITY_MISMATCH_REJECTED","LAUNCH_MANAGED_CAPTURE_RESTORE_PASS","LAUNCH_ORPHAN_RESTORE_PASS","LAUNCH_HANGUP_GROUP_RESTORE_PASS","LAUNCH_PHONE_WINDOW_PASS","LAUNCH_TRACE_ZERO_TAIL_OK","LAUNCH_QNX_SUITE_PASS","LAUNCH_QNX_END")
 if any(m not in log.splitlines() for m in markers) or not re.search(r"Process \d+ \(launch_qemu_runner\) exited status=0[.]",log):raise ValueError("Native launch controls have not all passed")
 if any(m in log for m in ("LAUNCH_FAILED","LAUNCH_REFUSED","SIGSEGV","SIGABRT","terminated signo=")):raise ValueError("Failed/fatal native run")
 reports=[]
 for label in ("LAUNCH_REPORT_HEX","LAUNCH_ORPHAN_REPORT_HEX"):
  matches=re.findall(r"^"+label+r" ([0-9a-f]+)\r?$",log,re.M)
  if len(matches)!=1:raise ValueError("Missing report: "+label)
  raw=bytes.fromhex(matches[0]);h=struct.unpack_from("<16I",raw)
  if len(raw)!=512 or h[:10]!=(0x314c4144,2,512,6,0,1,1,0,0,1) or h[15]!=1 or any(raw[236:256]) or any(raw[260:]):raise ValueError("Bad native final state")
  if len(set(h[10:15]))!=5 or not all(h[10:15]) or not all(struct.unpack_from("<4Q",raw,64)):raise ValueError("Bad native identities")
  status,count,dropped=struct.unpack_from("<3I",raw,224)
  if status!=1 or not count or count+dropped!=9:raise ValueError("Synthetic trace accounting failed")
  (q/("normal-controller.bin" if label=="LAUNCH_REPORT_HEX" else "orphan-controller.bin")).write_bytes(raw)
  capture=struct.unpack_from('<I',raw,256)[0]
  if capture!=(20 if label=='LAUNCH_REPORT_HEX' else 60):raise ValueError('Wrong native capture profile')
  reports.append(dict(capture_seconds=capture,observed_pid=h[10],restored_pid=h[11],controller_pid=h[12],manager_pid=h[13],baseline_pid=h[14],records=count,dropped=dropped))
 rows=re.findall(r"^LAUNCH_TRACE_HEX ([0-9a-f]+)\r?$",log,re.M)
 if len(rows)!=1:raise ValueError("Missing trace")
 prefix=bytes.fromhex(rows[0]);raw=prefix+bytes(32896-len(prefix));trace=decode(raw)
 if len(prefix)!=416 or trace["pid"]!=reports[0]["observed_pid"] or trace["count"]!=reports[0]["records"] or trace["dropped"]!=reports[0]["dropped"] or trace["writer_active"] or trace["incomplete_records"]:raise ValueError("Native trace identity/state mismatch")
 (q/"observer.bin").write_bytes(raw)
 tested={r.split()[1]:r.split()[0] for r in (q/"tested.sha256").read_text().splitlines()}
 sources={"observer_launch":BASE/"build/observer_launch","libdelphi_observer.so":ROOT/"native/observer/release/libdelphi_observer.so"}
 original=json.loads((ROOT/"native/observer/release/manifest.json").read_text())["sha256"]
 if sha(sources["libdelphi_observer.so"].read_bytes())!=original:raise ValueError("Observer candidate changed")
 libc={s["name"] for s in json.loads((ROOT/"delphi-analysis/control-runtime/libc.so.3.index.json").read_text())["symbols"] if s["defined"]}
 records={}
 for name,p in sources.items():
  blob=p.read_bytes();e=ELFFile(io.BytesIO(blob));needs=[];imports=[]
  if sha(blob)!=tested.get(name) or not blob or len(blob)>128*1024:raise ValueError("Untested or oversized file: "+name)
  if e["e_machine"]!="EM_ARM" or e.elfclass!=32 or not e.little_endian or e["e_flags"]>>24!=5 or e["e_flags"]&0x400:raise ValueError("Wrong ARM ABI")
  for seg in e.iter_segments():
   if seg["p_type"]=="PT_GNU_STACK" and seg["p_flags"]&1:raise ValueError("Executable stack")
   if seg["p_type"]=="PT_DYNAMIC":needs=[t.needed for t in seg.iter_tags() if t.entry.d_tag=="DT_NEEDED"]
  for sec in e.iter_sections():
   if sec["sh_type"]=="SHT_DYNSYM":imports=[s.name for s in sec.iter_symbols() if s["st_shndx"]=="SHN_UNDEF" and s["st_info"]["bind"]=="STB_GLOBAL"]
  if needs!=["libc.so.3"] or set(imports)-libc:raise ValueError("Runtime dependencies/imports not present on unit: "+name+repr(set(imports)-libc))
  records[name]=dict(bytes=len(blob),sha256=sha(blob),needed=needs,required_unit_libc_imports=sorted(imports))
 app=(ROOT/"delphi-dump/extbin/apps/bin/AndroidAuto").read_bytes()
 if sha(app)!=REFERENCES["AndroidAuto.original"][2]:raise ValueError("Wrong app profile")
 e=ELFFile(io.BytesIO(app));text=e.get_section_by_name(".text");data=text.data();callers=set()
 for offset in range(0,len(data)-3,4):
  word=struct.unpack_from("<I",data,offset)[0]
  if word&0x0f000000!=0x0b000000:continue
  delta=word&0xffffff
  if delta&0x800000:delta-=0x1000000
  address=text["sh_addr"]+offset
  if address+8+delta*4==0x104df4:callers.add(address+4)
 if callers!=KNOWN_REGISTRATION_CALLERS:raise ValueError("Caller profile differs from verified app: "+repr(sorted(callers)))
 result=dict(scope="Captured procman with synthetic app in QNX; factory AndroidAuto not executed",passed=True,controls=list(markers),experiments=reports,qnx_log_sha256=sha((q/"qemu.log").read_bytes()),actual_androidauto_interposition_tested=False)
 (q/"summary.json").write_text(json.dumps(result,indent=2))
 release=BASE/"release";release.mkdir(exist_ok=True)
 for name,p in sources.items():shutil.copy2(p,release/name)
 manifest=dict(kind="managed_androidauto_observer",files=records,expected_stock=REFERENCES,known_registration_callers=[hex(x) for x in sorted(callers)],qnx_emulation_passed=True,actual_androidauto_interposition_tested=False,requires_explicit_run=True,capture_profiles=[20,60],qnx_log_sha256=result["qnx_log_sha256"])
 (release/"manifest.json").write_text(json.dumps(manifest,indent=2));shutil.copy2(BASE/"README.txt",release/"README.txt")
 paths=[ROOT/"scripts"/n for n in ("run_androidauto_observer.py","run_observer_smoke.py","delphi_inventory.py","project_console.py","decode_delphi_observer.py")]+[release/n for n in (*NAMES,"manifest.json","README.txt")]
 bundle=BASE/"androidauto-phone-capture-laptop.zip"
 with zipfile.ZipFile(bundle,"w",zipfile.ZIP_DEFLATED) as z:
  for p in paths:z.write(p,p.relative_to(ROOT).as_posix())
 print("PASS: normal capture/restoration, identity rejection and group-hangup recovery.")
 print("PASS: required native imports present in actual unit libc; app callers match verified binary.")
 print("Bundle:",bundle)
if __name__ == '__main__':
    with console_session(__file__, __doc__):
        main()
