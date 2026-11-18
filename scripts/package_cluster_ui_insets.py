"""Package the full-frame map / inset-controls trial from the proven v9 bundle."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,zipfile
from project_console import console_session,status,log as print
from package_cluster_replay import elf_gate
ROOT=Path(__file__).resolve().parents[1]
SHA=lambda b:hashlib.sha256(b).hexdigest()
SCHEMA='https://github.com/borconi/obd2aa/blob/5768e9399777b7d44e0874967f7bd4c47d6fced7/app/src/main/proto/protos.proto#L110-L136'

def main():
    base=ROOT/'native/cluster-bridge/live-output'
    original=base/'live-cluster-v9-margin200-density140-laptop.zip'
    original_hash=SHA(original.read_bytes())
    if original_hash!='f195a869d09dd5c81221abfc4740ae62faf5b02da7ce63f0915ba4d1ffc52485':
        raise ValueError('Proven compact v9 archive changed')
    native=ROOT/'native/secondary-display'
    log=(native/'qemu/qemu.log').read_text()
    for gate in ('CLUSTER_UI_INSETS_QNX_PASS','CLUSTER_MARGIN_QNX_PASS width_total=200 height_total=0 dpi=140','ROUTE_DISCONNECT_QNX_PASS','SECONDARY_DISCOVERY_TRANSACTION_QNX_PASS','SECONDARY_KEYFRAME_PROBE_PASS','DELPHI_SMOKE_QNX_SUITE_PASS'):
        if gate not in log:raise ValueError('Missing QNX gate: '+gate)
    checked={Path(row.split()[1]).name:row.split()[0] for row in (native/'qemu/ui-insets-tested.sha256').read_text().splitlines()}
    payload=native/'build/libdelphi_observer_keyframe_uiinsets.so'
    binary,abi=elf_gate(payload)
    if checked.get(payload.name)!=SHA(binary):raise ValueError('UI-insets native hash differs from QNX gate')
    if set(abi['imports'])&{'kill','ptrace','pwrite','pwrite64','system'}:raise ValueError('Forbidden imports')
    with zipfile.ZipFile(original) as z:
        if z.testzip() is not None:raise ValueError('Baseline ZIP CRC')
        entries={n:z.read(n) for n in z.namelist()}
    aa='native/cluster-bridge/keyframe-probe/release'
    nav='native/cluster-bridge/live-output/release'
    with tempfile.TemporaryDirectory() as td:
        old=Path(td)/'baseline.so';old.write_bytes(entries[aa+'/libdelphi_observer.so'])
        _,old_abi=elf_gate(old)
    for key in ('imports','exports','needed'):
        if set(abi[key])!=set(old_abi[key]):raise ValueError('Native ABI changed: '+key)
    changed={'native/secondary-display/build.sh','native/secondary-display/test-qemu.sh'}
    layout=ROOT/'native/cluster-bridge/layout-margin'
    changed|={p.relative_to(ROOT).as_posix() for p in layout.iterdir() if p.suffix in ('.c','.h')}
    changed.add('scripts/package_cluster_ui_insets.py')
    profile=dict(video_service_id=9,width_margin_total=0,height_margin_total=0,
        left_right_pixels=0,content_rectangle=[0,0,800,480],coded_dimensions=[800,480],density=140,
        ui_config_field=11,content_insets=dict(top=0,bottom=0,left=120,right=120),
        stable_content_insets=dict(top=0,bottom=0,left=120,right=120),ui_content_rectangle=[120,0,680,480],
        full_frame_map_requested=True,phone_honors_ui_insets_unverified=True,
        phone_rendering_test_needed=True,primary_configuration_unchanged=True,
        reencoded=False,protocol_schema=SCHEMA,baseline_bundle_sha256=original_hash)
    for name in (aa+'/manifest.json',nav+'/manifest.json'):
        m=json.loads(entries[name])
        for path,h in m.get('source_sha256',{}).items():
            if path not in changed and SHA((ROOT/path).read_bytes())!=h:
                raise ValueError('Nonlayout source changed since v9: '+path)
        m['source_sha256'].update({p:SHA((ROOT/p).read_bytes()) for p in changed})
        m.update(release_version=10,on_car_tested=False,video_core_on_car_verified=True,
            baseline_on_car_collection='_disconnect_observer_20261118_185015_2cd7fa2a',layout_trial=profile)
        if name.startswith(aa+'/'):
            m['files']['libdelphi_observer.so']=dict(bytes=len(binary),sha256=SHA(binary))
        entries[name]=json.dumps(m,indent=2).encode()
    entries[aa+'/libdelphi_observer.so']=binary
    readme='''V10 FULL-FRAME MAP / INSET CONTROLS TRIAL
==========================================
Requests full800x480 map imagery with no encoded video border, density140 as in
the successful compact v9 trial, and120px left/right content+stable UI insets.
Inset metadata requests controls in the center560px; phone support on the
cluster stream has NOT been verified. This is not an image zoom or re-encode.
All playback, disconnect, recovery binaries and laptop scripts are exact v9 bytes.

Extract the ENTIRE ZIP into a fresh folder. Park, ignition on, phone unplugged,
Ethernet connected, factory map working. Run:
 python scripts/run_disconnected_observer.py --run --live-cluster --phone-unplugged
Follow the existing prompts. Only at CAPTURE READY connect phone, start a route
and watch live updates for about12 seconds. Check both map edges and the full
directions card. Unplug phone; do not toggle map location until answering the
automatic-return question. Reconnect Ethernet and finish the normal cleanup.

Return the full delphi-dump/_disconnect_observer_* folder and report:
1. Did map imagery fill both previously black side areas?
2. Was the complete directions card visible, including its right edge?
3. Did factory compass/map return automatically after disconnection?
If controls move behind a gauge, the phone may not honor this inset metadata.
Keep the proven v9 compact ZIP available for comparison.
'''
    entries['README.txt']=readme.encode();entries[nav+'/README.txt']=readme.encode()
    entries['LAYOUT-PROFILE.json']=json.dumps(profile,indent=2).encode()
    result=base/'live-cluster-v10-ui-insets120-density140-laptop.zip'
    with zipfile.ZipFile(result,'w',zipfile.ZIP_DEFLATED) as z:
        for name,b in sorted(entries.items()):z.writestr(name,b)
    with tempfile.TemporaryDirectory() as td:
        extracted=Path(td)
        with zipfile.ZipFile(result) as z:
            if z.testzip() is not None:raise ValueError('V10 ZIP CRC')
            z.extractall(extracted)
        for folder in (aa,nav):
            m=json.loads((extracted/folder/'manifest.json').read_text())
            for name,record in m['files'].items():
                b=(extracted/folder/name).read_bytes()
                if len(b)!=record['bytes'] or SHA(b)!=record['sha256']:raise ValueError('Payload hash '+name)
            for name,h in m['scripts_sha256'].items():
                if SHA((extracted/'scripts'/name).read_bytes())!=h:raise ValueError('Script hash '+name)
        status('Checking extracted stdlib-only laptop plan.')
        v=subprocess.run([sys.executable,'-S','-B',str(extracted/'scripts/run_disconnected_observer.py'),'--live-cluster'],cwd=extracted,capture_output=True,text=True)
        if v.returncode or 'Plan only' not in v.stdout or (extracted/'delphi-dump').exists():raise ValueError('Portable plan '+v.stderr)
        code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_disconnected_observer as m;print(len(m.package(Path(sys.argv[1])/'native/cluster-bridge/keyframe-probe/release',phone=True,factory=True,secondary=True,cluster=True,probe=True)))"
        v=subprocess.run([sys.executable,'-S','-B','-c',code,str(extracted)],cwd=extracted,capture_output=True,text=True)
        if v.returncode or v.stdout.strip()!='4':raise ValueError('Portable asset gate '+v.stderr)
    allowed={aa+'/libdelphi_observer.so',aa+'/manifest.json',nav+'/manifest.json','README.txt',nav+'/README.txt','LAYOUT-PROFILE.json'}
    with zipfile.ZipFile(original) as z:
        for name in z.namelist():
            if name not in allowed and z.read(name)!=entries[name]:raise ValueError('Nonlayout payload changed '+name)
    if SHA(original.read_bytes())!=original_hash:raise ValueError('Baseline archive changed during packaging')
    report=dict(bundle=result.relative_to(ROOT).as_posix(),bytes=result.stat().st_size,sha256=SHA(result.read_bytes()),
        qnx_ui_insets_passed=True,portable_plan_passed=True,portable_assets_passed=True,
        payload_and_script_hashes_passed=True,nonlayout_payloads_and_scripts_identical_to_v9=True,
        baseline_archive_unchanged=True,on_car_tested=False,layout=profile)
    (base/'ui-insets-release-review.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    with console_session(__file__,__doc__):main()
