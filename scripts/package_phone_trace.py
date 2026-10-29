"""Release the passive reader after source/hash, native-loader and loopback gates."""
import hashlib,io,json,shutil,subprocess,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
BASE=ROOT/'native/trace-reader'
def sha(blob):return hashlib.sha256(blob).hexdigest()
def main():
    blob=(BASE/'build/trace_reader').read_bytes();host=json.loads((BASE/'host-tests.json').read_text());source=(BASE/'reader.c').read_bytes();q=(BASE/'qemu/qemu.log').read_text(errors='replace')
    expected=(BASE/'qemu/tested.sha256').read_text().split()[0]
    if sha(blob)!=expected or sha(blob)!=host['qnx_binary_sha256'] or sha(source)!=host['source_sha256'] or len(host['cases'])!=7 or not all(c['passed'] for c in host['cases']):raise ValueError('Reader differs from checked source/artifact')
    if 'TRACE_READER_QNX_LOADER_ROOT_REFUSAL_PASS' not in q or 'trace_qemu_runner) exited status=0' not in q or 'TRACE_READER_QNX_END' not in q:raise ValueError('QNX loader checks incomplete')
    for marker in ('TRACE_READER_QNX_KSH_GOOD_WIRE_PASS','TRACE_READER_QNX_KSH_BAD_WIRE_REJECTED'):
        if marker not in q:raise ValueError('QNX shell syntax regression not checked')
    sources=json.loads((BASE/'qemu/shell-source-hashes.json').read_text())
    for name,digest in sources.items():
        if sha((ROOT/'scripts'/name).read_bytes())!=digest:raise ValueError('Python shell launcher changed after syntax check')
    tested={row.split()[1]:row.split()[0] for row in (BASE/'qemu/tested.sha256').read_text().splitlines()}
    for name in ('launch-good.sh','launch-bad.sh'):
        if sha((BASE/'qemu'/name).read_bytes())!=tested.get(name):raise ValueError('Shell fixture differs from QNX-tested wire')
    e=ELFFile(io.BytesIO(blob));needs=[];imports=[]
    if e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400 or len(blob)>131072:raise ValueError('Wrong reader ARM ABI/size')
    for seg in e.iter_segments():
        if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1:raise ValueError('Executable stack')
        if seg['p_type']=='PT_DYNAMIC':needs=[t.needed for t in seg.iter_tags() if t.entry.d_tag=='DT_NEEDED']
    if needs!=['libsocket.so.3','libc.so.3']:raise ValueError('Unexpected runtime dependencies')
    for s in e.get_section_by_name('.dynsym').iter_symbols():
        if s['st_shndx']=='SHN_UNDEF' and s['st_info']['bind']=='STB_GLOBAL':imports.append(s.name)
    libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
    if set(imports)-libc-{'socket','connect','getsockopt','recv','select'}:raise ValueError('Unexpected imports: '+repr(set(imports)-libc))
    if any(n in imports for n in ('kill','pathmgr_symlink','pathmgr_unlink','dlsym','send','sendto','system','execv')):raise ValueError('Unwanted process/control/network-write import')
    release=BASE/'release';release.mkdir(exist_ok=True);(release/'trace_reader').write_bytes(blob)
    manifest=dict(kind='passive_loopback_trace_reader',bytes=len(blob),sha256=sha(blob),seconds=180,byte_limit=16777216,network_peer='127.0.0.1:15361',needed=needs,imports=sorted(imports),source_sha256=sha(source),host_loopback_tested=True,qnx_loader_root_refusal_tested=True,qnx_network_runtime_tested=False,actual_unit_reader_tested=False,androidauto_restart=False)
    (release/'manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(BASE/'README.txt',release/'README.txt')
    names=('run_phone_trace.py','run_observer_smoke.py','delphi_inventory.py','decode_delphi_observer.py','run_androidauto_observer.py','collect_trace_tcp.py','collect_observer_preflight.py')
    if b'LIVE_EXPERIMENT_HOLD=True' not in (ROOT/'scripts/run_androidauto_observer.py').read_bytes():raise ValueError('Disruptive observer hold missing')
    bundle=BASE/'passive-phone-trace-laptop.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n in names:z.write(ROOT/'scripts'/n,'scripts/'+n)
        for n in ('trace_reader','manifest.json','README.txt'):z.write(release/n,(release/n).relative_to(ROOT).as_posix())
    with tempfile.TemporaryDirectory(prefix='phone-trace-package-') as t:
        folder=Path(t)
        with zipfile.ZipFile(bundle) as z:z.extractall(folder)
        result=subprocess.run([sys.executable,'-S','-B',str(folder/'scripts/run_phone_trace.py')],cwd=folder,capture_output=True,text=True)
        if result.returncode or 'Plan only' not in result.stdout or (folder/'delphi-dump').exists():raise ValueError('Portable plan failed: '+result.stderr)
        code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));from run_phone_trace import package;print(len(package(Path(sys.argv[1])/'native/trace-reader/release')))"
        result=subprocess.run([sys.executable,'-S','-B','-c',code,str(folder)],cwd=folder,capture_output=True,text=True)
        if result.returncode or int(result.stdout)!=len(blob):raise ValueError('Portable reader asset verification failed')
    report=dict(bundle=str(bundle.relative_to(ROOT)),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),portable_plan_passed=True,manifest=manifest)
    (ROOT/'delphi-analysis/control-runtime/passive-phone-trace-release.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))
if __name__=='__main__':main()
