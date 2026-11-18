"""Package an isolated secondary-display margin variant of the completed v8 trial."""
from pathlib import Path
import sys,hashlib,json,zipfile,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
from project_console import console_session,status,log as print
from decode_androidauto_display import fields
from package_cluster_replay import elf_gate
sha=lambda b:hashlib.sha256(b).hexdigest()
def var(v):
 b=bytearray()
 while v>127:b.append((v&127)|128);v>>=7
 return bytes(b+bytes([v]))
def encode(rows):
 b=bytearray()
 for n,w,v in rows:
  b+=var((n<<3)|w)
  if w==0:b+=var(v)
  elif w==2:b+=var(len(v))+v
  else:b+=v
 return bytes(b)
def modify(packet,config_change):
 top=[]
 for n,w,v in fields(packet[2:]):
  if n==1 and w==2:
   service=fields(v);ids=[q for a,t,q in service if a==1 and t==0]
   if ids==[9]:
    updated=[]
    for a,t,q in service:
     if a==3 and t==2:q=encode([(x,y,encode(config_change(fields(z))) if x==4 and y==2 else z) for x,y,z in fields(q)])
     updated.append((a,t,q))
    v=encode(updated)
  top.append((n,w,v))
 return packet[:2]+encode(top)
def main():
 base=ROOT/'native/cluster-bridge/live-output/live-cluster-v8-laptop.zip';base_sha=sha(base.read_bytes())
 with zipfile.ZipFile(base) as z:entries={n:z.read(n) for n in z.namelist()}
 ap='native/cluster-bridge/keyframe-probe/release/manifest.json';np='native/cluster-bridge/live-output/release/manifest.json';am=json.loads(entries[ap]);nm=json.loads(entries[np]);original_sources=dict(am['source_sha256']); historical_build_hash=original_sources['native/cluster-bridge/build.sh']; original_sources['native/cluster-bridge/build.sh']=sha((ROOT/'native/cluster-bridge/build.sh').read_bytes())
 for n,h in original_sources.items():
  if sha((ROOT/n).read_bytes())!=h:raise ValueError('Main source changed after v8: '+n)
 raw=(ROOT/'delphi-dump/_disconnect_observer_20261118_140131_df3a9762/discovery.bin').read_bytes();magic,pid,ni,no,flags,committed=struct.unpack_from('<6I',raw);assert magic==0x32534344 and flags==0 and committed==1
 source=raw[24:24+ni];baseline=raw[8216:8216+no];assert encode(fields(baseline[2:]))==baseline[2:]
 patch=lambda rows:[(n,w,160 if n==3 else v) for n,w,v in rows]
 expected=modify(baseline,patch);extra=lambda rows:rows+[(31,0,123)]
 vectors=dict(input=source,baseline=baseline,expected=expected,extra_input=modify(source,extra),extra_expected=modify(modify(baseline,extra),patch),bad_wire=modify(source,lambda rows:[(n,2,b'') if n==3 else (n,w,v) for n,w,v in rows]),nonzero_width=modify(source,lambda rows:[(n,w,2 if n==3 else v) for n,w,v in rows]),duplicate_width=modify(source,lambda rows:rows+[(3,0,0)]),missing_width=modify(source,lambda rows:[r for r in rows if r[0]!=3]))
 (BASE/'vectors.h').write_text('\n'.join('static const unsigned char '+n+'[]={'+','.join(str(v) for v in b)+'};' for n,b in vectors.items()))
 status('Building the margin variant in a private tree; main workspace mounted read-only.')
 v=subprocess.run(['docker','run','--rm','--network','none','-v',str(ROOT)+':/src:ro','-v',str(BASE)+':/out','delphi-qnx65:qemu','python3','/out/build-container.py'],capture_output=True,text=True)
 if v.returncode:raise RuntimeError(v.stdout+v.stderr)
 print(v.stdout.strip());lib,meta=elf_gate(BASE/'release/libdelphi_observer.so');(BASE/'baseline-observer.so').write_bytes(entries[ap.rsplit('/',1)[0]+'/libdelphi_observer.so']);_,oldmeta=elf_gate(BASE/'baseline-observer.so')
 for key in ('imports','exports','needed'):
  if set(meta[key])!=set(oldmeta[key]):raise ValueError('Unexpected ABI change '+key)
 for n,h in original_sources.items():
  if sha((ROOT/n).read_bytes())!=h:raise ValueError('Main source changed during isolated build: '+n)
 if sha(base.read_bytes())!=base_sha:raise ValueError('Baseline v8 ZIP changed')
 lp=ap.rsplit('/',1)[0]+'/libdelphi_observer.so';entries[lp]=lib;am['files']['libdelphi_observer.so']=dict(bytes=len(lib),sha256=sha(lib));am.update(imports=meta['imports'],exports=meta['exports'],needed=meta['needed'])
 layout=dict(video_service_id=9,width_margin_total=160,height_margin_total=0,left_right_pixels=80,content_rectangle=[80,0,720,480],coded_dimensions=[800,480],density=160,phone_rendering_test_needed=True,primary_configuration_unchanged=True,baseline_bundle_sha256=base_sha)
 layout['historical_manifest_build_hash']=historical_build_hash;layout['current_prerequisite_build_hash']=original_sources['native/cluster-bridge/build.sh'];am['layout_trial']=layout;nm['layout_trial']=layout;am['source_sha256']['native/cluster-bridge/build.sh']=original_sources['native/cluster-bridge/build.sh']
 for name in ('wire-margin.c','margin-fixture.c','build-container.py','package.py'):
  rel=(BASE/name).relative_to(ROOT).as_posix();h=sha((BASE/name).read_bytes());am['source_sha256'][rel]=h;nm['source_sha256'][rel]=h
 entries[ap]=json.dumps(am,indent=2).encode();entries[np]=json.dumps(nm,indent=2).encode()
 readme='''V8 SECONDARY DISPLAY MARGIN TRIAL (160 TOTAL HORIZONTAL PIXELS)
=============================================================
This separate variant retains the completed v8 disconnect fix and proven video core.
It advertises 160 total horizontal margin pixels on video service9 only:80 per side,
requesting a centered640x480 content area inside the unchanged800x480 coded frame.
Height margin remains0 and density160. Primary display configuration is unchanged.
The phone must honor the secondary-display margin; physical positioning needs testing.

Keep the original v8 bundle for its baseline restoration check. Extract THIS entire
ZIP into a separate folder. Ignition on, phone unplugged, Ethernet connected,
factory map visible in the cluster. Run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
At CAPTURE READY connect the phone and start a route promptly. Observe the directions
bubble for about12 seconds, unplug the phone and follow the v8 cleanup prompts.
Return the complete result folder and a cluster photo if any part remains clipped.
Margins require a fresh phone session. This trial does not re-encode or scale video.
'''
 entries['README.txt']=readme.encode();entries['LAYOUT-PROFILE.json']=json.dumps(layout,indent=2).encode();bundle=BASE/'live-cluster-v8-margin160-laptop.zip'
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for name,b in sorted(entries.items()):z.writestr(name,b)
 with tempfile.TemporaryDirectory() as td:
  root=Path(td)
  with zipfile.ZipFile(bundle) as z:
   assert z.testzip() is None;z.extractall(root)
  v=subprocess.run([sys.executable,'-S','-B',str(root/'scripts/run_disconnected_observer.py'),'--live-cluster'],cwd=root,capture_output=True,text=True)
  if v.returncode or 'Plan only' not in v.stdout:raise ValueError('Portable plan failed '+v.stderr)
  for path in (ap,np):
   m=json.loads((root/path).read_text())
   for n,e in m['files'].items():
    b=(root/Path(path).parent/n).read_bytes();assert len(b)==e['bytes'] and sha(b)==e['sha256'],n
   for n,h in m['scripts_sha256'].items():assert sha((root/'scripts'/n).read_bytes())==h,n
  with zipfile.ZipFile(base) as z:
   for name,b in entries.items():
    if name not in (ap,np,lp,'README.txt','LAYOUT-PROFILE.json'):assert z.read(name)==b,name
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),sha256=sha(bundle.read_bytes()),bytes=bundle.stat().st_size,baseline_bundle_unchanged=sha(base.read_bytes())==base_sha,main_sources_unchanged=True,private_qnx_passed=True,existing_cleanup_regressions_passed=True,portable_plan_passed=True,all_nonlayout_payloads_and_scripts_unchanged=True,layout=layout)
 (BASE/'release-review.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
 with console_session(__file__,__doc__):main()
