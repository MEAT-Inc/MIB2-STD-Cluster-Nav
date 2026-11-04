"""Gate and package a single stock-map orderly restart trial."""
from project_console import console_session, log as print
import argparse, hashlib, io, json, subprocess, sys, tempfile, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'native/cluster-bridge/nav-control'
sys.path.insert(0,str(ROOT/'.tools/python'))
from elftools.elf.elffile import ELFFile
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 from run_nav_graceful import CYCLE_HELD
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--diagnostic-shutdown',action='store_true');parser.add_argument('--recover-stalled',action='store_true');args=parser.parse_args();diagnostic=args.diagnostic_shutdown;recovery=args.recover_stalled
 if diagnostic and recovery:raise ValueError('Choose one package mode')
 if CYCLE_HELD and not (diagnostic or recovery):raise ValueError('Graceful-cycle distribution held after stock shutdown stalled; use package_map_session.py for read-only stack capture.')
 log=(BASE/'qemu/qemu.log').read_text()
 for marker in ('NAV_STALL_CAPTURE_GUARD_PASS','NAV_RECOVER_HEALTHY_REFUSAL_PASS','NAV_RECOVER_STALE_REFUSAL_PASS','NAV_RECOVER_FACTORY_AUTORESTART_PASS','NAV_PAGE_READ_QNX_PASS','NAV_PAGE_STALE_IDENTITY_REFUSAL_PASS','NAV_PAGE_BAD_ADDRESS_REFUSAL_PASS','SAL_GRACEFUL_CONTROL_QNX_PASS','NAV_CONTROL_GUARDED_CYCLE_PASS','NAV_CONTROL_IDENTITY_REFUSAL_PASS','NAV_CONTROL_QNX_END','Process 3 (sal_init_fixture) exited status=0.'):
  if marker not in log:raise ValueError('Missing QNX validation: '+marker)
 tested={Path(line.split()[1]).name:line.split()[0] for line in (BASE/'qemu/tested.sha256').read_text().splitlines()}
 for name,expected in tested.items():
  if sha((BASE/'build'/name).read_bytes())!=expected:raise ValueError('Changed tested binary: '+name)
 if not all(n in tested for n in ('nav_cycle','nav_cycle_test','sal_init_fixture','idle_fixture')):
  raise ValueError('Incomplete tested binary ledger')
 sources={p.name:p.read_bytes() for p in BASE.iterdir() if p.suffix in ('.c','.h')}
 for name in ('proc_guard.c','proc_guard.h'):
  sources[name]=(BASE.parent/'nav-launch'/name).read_bytes()
 sources['proc_readonly.c']=b''.join(sources['proc_guard.c'].split(b'int pg_interrupt(',1)[:1])
 for line in (BASE/'qemu/source.sha256').read_text().splitlines():
  expected,name=line.split()
  if name not in sources or sha(sources[name])!=expected:raise ValueError('Changed native source: '+name)
 payload=(BASE/'build/nav_cycle').read_bytes()
 e=ELFFile(io.BytesIO(payload))
 if e.elfclass!=32 or not e.little_endian or e['e_machine']!='EM_ARM' or e['e_type']!='ET_EXEC' or e['e_flags']>>24!=5 or e['e_flags']&0x400 or not 0<len(payload)<131072 or b'idle_fixture' in payload or b'recover-fixture' in payload:
  raise ValueError('Production helper ABI/fixture gate')
 needed=[];imports=[]
 for segment in e.iter_segments():
  if segment['p_type']=='PT_GNU_STACK' and segment['p_flags']&1:raise ValueError('Executable stack')
  if segment['p_type']=='PT_DYNAMIC':
   needed=[t.needed for t in segment.iter_tags() if t.entry.d_tag=='DT_NEEDED']
 for symbol in e.get_section_by_name('.dynsym').iter_symbols():
  if symbol['st_info']['bind']=='STB_GLOBAL' and symbol['st_shndx']=='SHN_UNDEF':imports.append(symbol.name)
 libc={s['name'] for s in json.loads((ROOT/'delphi-analysis/control-runtime/libc.so.3.index.json').read_text())['symbols'] if s['defined']}
 if needed!=['libc.so.3'] or set(imports)-libc or set(imports)&{'sigqueue','raise','pwrite','pwrite64'} or ('kill' in imports and not recovery):
  raise ValueError('Unverified helper imports')
 tests=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/tests/test_nav_graceful.py')],cwd=ROOT,capture_output=True,text=True)
 if tests.returncode:raise ValueError(tests.stdout+tests.stderr)
 scripts=('run_nav_graceful.py','collect_map_session.py','run_observer_smoke.py','delphi_inventory.py','decode_delphi_observer.py','project_console.py')
 manifest=dict(kind='nav_stalled_recovery' if recovery else 'nav_shutdown_allocator_diagnostic' if diagnostic else 'stock_nav_graceful_cycle',qnx_recovery_guard_passed=True,diagnostic_only=diagnostic,diagnostic_revision=2,qnx_page_reader_passed=True,page_reader='native_guarded_pread64',allocator_pages=diagnostic,preflight_revision=2,reference_method='shell_copy_to_ram_then_ftp',nav_app_id=29,qnx_guarded_cycle_passed=True,car_validated=False,video_writes=False,signals_to_nav=recovery,functional_maps_verified=False,files={'nav_cycle':dict(bytes=len(payload),sha256=sha(payload))},elf=dict(needed=needed,imports=imports),sources={n:sha(b) for n,b in sources.items()},scripts={n:sha((ROOT/'scripts'/n).read_bytes()) for n in scripts})
 if recovery:
  source=ROOT/'delphi-dump/_nav_shutdown_diag_20261104_144616_5cd1a4aa'
  summary_bytes=(source/'nav-graceful-summary.json').read_bytes();summary=json.loads(summary_bytes)
  for a in summary['artifacts']:
   data=(source/a['file']).read_bytes()
   if len(data)!=a['bytes'] or sha(data)!=a['sha256']:raise ValueError('Pinned recovery source artifact changed')
  if not summary['diagnostics_complete'] or summary['identity_before']['pid']!=704597:raise ValueError('Wrong pinned recovery session')
  manifest.update(recovery_identity=summary['identity_before'],recovery_source=source.name,recovery_summary_sha256=sha(summary_bytes),termination_signal=9,requires_exact_live_crash=True)
 release=BASE/('recovery-release' if recovery else 'release');release.mkdir(exist_ok=True)
 (release/'nav_cycle').write_bytes(payload)
 (release/'manifest.json').write_text(json.dumps(manifest,indent=2))
 (release/'README.txt').write_bytes((BASE/('RECOVERY-README.txt' if recovery else 'DIAGNOSTIC-README.txt' if diagnostic else 'README.txt')).read_bytes())
 files={'scripts/'+n:(ROOT/'scripts'/n).read_bytes() for n in scripts}
 for n in ('nav_cycle','manifest.json','README.txt'):
  files[(release/n).relative_to(ROOT).as_posix()]=(release/n).read_bytes()
 bundle=BASE/('nav-stalled-recovery-laptop.zip' if recovery else 'nav-shutdown-diagnostic-v2-laptop.zip' if diagnostic else 'nav-graceful-cycle-laptop.zip')
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in files.items():z.writestr(n,b)
 with tempfile.TemporaryDirectory() as tmp:
  p=Path(tmp)
  with zipfile.ZipFile(bundle) as z:z.extractall(p)
  for n,b in files.items():
   if (p/n).read_bytes()!=b:raise ValueError('Extracted file mismatch')
  result=subprocess.run([sys.executable,'-S','-B',str(p/'scripts/run_nav_graceful.py')],cwd=p,capture_output=True,text=True)
  if result.returncode or 'Plan only' not in result.stdout or (p/'delphi-dump').exists():raise ValueError('Portable plan: '+result.stderr)
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path(sys.argv[1])/'scripts'));import run_nav_graceful as r;print(len(r.package(Path(sys.argv[1]))))"
  code=code.replace('r.package(Path(sys.argv[1]))','r.package(Path(sys.argv[1]),diagnostic='+repr(diagnostic)+',recovery='+repr(recovery)+')')
  result=subprocess.run([sys.executable,'-S','-B','-c',code,str(p)],cwd=p,capture_output=True,text=True)
  if result.returncode or result.stdout.strip()!=str(len(payload)):raise ValueError('Portable native payload: '+result.stderr)
 report=dict(bundle=bundle.relative_to(ROOT).as_posix(),bytes=bundle.stat().st_size,sha256=sha(bundle.read_bytes()),portable_plan_passed=True,portable_assets_passed=True,workflow_tests=tests.stderr.strip(),manifest=manifest)
 (BASE/('recovery-release-review.json' if recovery else 'diagnostic-release-review.json' if diagnostic else 'release-review.json')).write_text(json.dumps(report,indent=2))
 print(json.dumps({k:v for k,v in report.items() if k!='manifest'},indent=2))

if __name__=='__main__':
 with console_session(__file__,__doc__):
  main()
