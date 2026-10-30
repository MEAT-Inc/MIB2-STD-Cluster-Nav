"""Package the read-only display observer after QNX and unit-ABI checks; no network."""
from pathlib import Path
import copy,hashlib,io,json,re,shutil,struct,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
from decode_androidauto_display import decode,HEADER,RECORD,CAPACITY
from run_androidauto_observer import NAMES,REFERENCES,package_files
BASE=ROOT/'native/observer/display'
SYMBOLS={'_ZN9VideoSink25addSupportedConfigurationEiiiiiii':0x8df74,'_ZN9VideoSink13setVideoFocusEib':0x8db50,'_ZN13MessageRouter13queueOutgoingEhPvj':0x7f5d8}
def sha(blob):return hashlib.sha256(blob).hexdigest()
def tested(path):return {r.split()[1]:r.split()[0] for r in path.read_text().splitlines()}
def main():
    q=BASE/'qemu';log=(q/'qemu.log').read_text(errors='replace');lines=log.splitlines()
    markers=['DISPLAY_QNX_SUITE_PASS','DISPLAY_ZERO_TAILS_OK','DISPLAY_QNX_END']+['DISPLAY_FIXTURE_PASS mode='+x for x in ('baseline','observed','disabled','full')]
    if any(x not in lines for x in markers) or not re.search(r'Process \d+ \(display_qemu_runner\) exited status=0[.]',log):raise ValueError('Incomplete native display tests')
    if any(x in log for x in ('DISPLAY_CASE_FAILED','SIGSEGV','SIGABRT','terminated signo=')):raise ValueError('Failed native display test')
    if not re.search(r'Process \d+ \(display_fixture\) exited status=125[.]',log) or 'DISPLAY_LOG count=32 dropped=7' not in lines:raise ValueError('Missing rejection/overflow control')
    checked=tested(q/'tested.sha256')
    for name in ('libdelphi_observer.so','libautoreceiver.so','display_fixture'):
        if sha((BASE/'build'/name).read_bytes())!=checked.get(name):raise ValueError('Untested display artifact: '+name)
    headers=re.findall(r'^DISPLAY_HEADER ([0-9a-f]+)\r?$',log,re.M)
    rows=re.findall(r'^DISPLAY_RECORD ([0-9a-f]+)\r?$',log,re.M)
    if len(headers)!=1 or len(rows)!=4:raise ValueError('Missing compact native evidence')
    header=bytes.fromhex(headers[0]);raw=bytearray(header)
    if len(header)!=HEADER:raise ValueError('Wrong native header size')
    for row in rows:
        blob=bytes.fromhex(row)
        if len(blob)<64 or len(blob)!=64+struct.unpack_from('<I',blob,52)[0] or len(blob)>RECORD:raise ValueError('Malformed compact native record')
        raw+=blob+bytes(RECORD-len(blob))
    raw+=bytes((CAPACITY-len(rows))*RECORD)
    evidence=decode(raw)
    if evidence['count']!=4 or evidence['dropped'] or [r['kind'] for r in evidence['records']]!=['video_configuration','video_focus','service_discovery','oversized_control_candidate']:raise ValueError('Native record classes incorrect')
    if evidence['records'][0]['integer_parameters']!=[0x11111111,0x22222222,0x33333333,0x44444444,0x55555555,0x66666666,0x87654321-0x100000000] or evidence['records'][1]['integer_parameters']!=[-2,1] or evidence['records'][2]['discovery']['advertised_service_ids']!=[1]:raise ValueError('Native arguments/wire data changed')
    (q/'display.bin').write_bytes(raw);(q/'display-decoded.json').write_text(json.dumps(evidence,indent=2))
    launch=ROOT/'native/observer/launch';release0=launch/'release';files=package_files(release0)
    launch_log=(launch/'qemu/qemu.log').read_text(errors='replace')
    for marker in ('LAUNCH_MANAGED_CAPTURE_RESTORE_PASS','LAUNCH_ORPHAN_RESTORE_PASS','LAUNCH_HANGUP_GROUP_RESTORE_PASS','LAUNCH_PHONE_WINDOW_PASS','LAUNCH_QNX_SUITE_PASS'):
        if marker not in launch_log.splitlines():raise ValueError('Missing controller control: '+marker)
    if sha(files['observer_launch'])!=tested(launch/'qemu/tested.sha256').get('observer_launch'):raise ValueError('Controller differs from tested launch')
    if sha(files['libdelphi_observer.so'])!='cc425ccdc1a889caa2b4128a0a55f07cc8b26679065d7e293b274b80e83ad70c':raise ValueError('Base observer release changed')
    receiver=(ROOT/'delphi-dump/extbin/apps/lib/libautoreceiver.so.1').read_bytes()
    if sha(receiver)!=REFERENCES['receiver.reference'][2]:raise ValueError('Wrong receiver profile')
    e=ELFFile(io.BytesIO(receiver));symbols={s.name:s['st_value'] for s in e.get_section_by_name('.dynsym').iter_symbols()}
    if any(symbols.get(n)!=v for n,v in SYMBOLS.items()):raise ValueError('Display symbol offsets differ from unit')
    libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
    blob=(BASE/'build/libdelphi_observer.so').read_bytes();e=ELFFile(io.BytesIO(blob));needed=[];imports=[];exports=[]
    if not blob or len(blob)>128*1024 or e['e_machine']!='EM_ARM' or e.elfclass!=32 or not e.little_endian or e['e_flags']>>24!=5 or e['e_flags']&0x400:raise ValueError('Wrong display ARM ABI')
    for seg in e.iter_segments():
        if seg['p_type']=='PT_GNU_STACK' and seg['p_flags']&1:raise ValueError('Executable stack')
        if seg['p_type']=='PT_DYNAMIC':needed=[t.needed for t in seg.iter_tags() if t.entry.d_tag=='DT_NEEDED']
    for s in e.get_section_by_name('.dynsym').iter_symbols():
        if s['st_info']['bind']!='STB_GLOBAL':continue
        (imports if s['st_shndx']=='SHN_UNDEF' else exports).append(s.name)
    if needed!=['libc.so.3'] or set(imports)-libc:raise ValueError('Missing unit runtime imports: '+repr(set(imports)-libc))
    if not set(SYMBOLS).issubset(exports) or '_ZN11GalReceiver15registerServiceEP20ProtocolEndpointBase' not in exports:raise ValueError('Missing interposed methods')
    manifest=copy.deepcopy(json.loads((release0/'manifest.json').read_text()))
    manifest.update(kind='managed_androidauto_display_observer',display_capture_version=1,display_capacity=CAPACITY,display_payload_limit=4096,display_native_offsets={n:hex(v) for n,v in SYMBOLS.items()},display_qnx_log_sha256=sha((q/'qemu.log').read_bytes()),display_interposition_tested_on_car=False,mutates_packets=False,creates_endpoints=False)
    manifest['files']['libdelphi_observer.so']=dict(bytes=len(blob),sha256=sha(blob),needed=needed,required_unit_libc_imports=sorted(imports))
    release=BASE/'release';release.mkdir(exist_ok=True)
    (release/'observer_launch').write_bytes(files['observer_launch']);(release/'libdelphi_observer.so').write_bytes(blob)
    (release/'manifest.json').write_text(json.dumps(manifest,indent=2));shutil.copy2(BASE/'README.txt',release/'README.txt')
    package_files(release,'managed_androidauto_display_observer')
    paths=[ROOT/'scripts'/n for n in ('run_androidauto_observer.py','run_observer_smoke.py','delphi_inventory.py','decode_delphi_observer.py','decode_androidauto_display.py')]+[release/n for n in (*NAMES,'manifest.json','README.txt')]
    bundle=BASE/'androidauto-display-capture-laptop.zip'
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for path in paths:z.write(path,path.relative_to(ROOT).as_posix())
    print('PASS: QNX forwarding, stack arguments, errno, payload preservation, disabled log, overflow, missing originals.')
    print('PASS: unchanged tested controller; ARM ABI, receiver symbols and actual unit libc imports.')
    print('Bundle:',bundle);print('SHA256:',sha(bundle.read_bytes()))
if __name__=='__main__':main()
