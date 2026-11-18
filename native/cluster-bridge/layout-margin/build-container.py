"""Build in a private container tree; /src is mounted read-only."""
from pathlib import Path
import shutil,subprocess,os
src=Path('/src');out=Path('/out');root=Path('/tmp/layout-source');root.mkdir()
for p in (src/'native').rglob('*'):
 if not p.is_file() or p.suffix not in ('.c','.h','.S','.sh','.json') or any(x in ('build','qemu','release','layout-margin') for x in p.relative_to(src/'native').parts):continue
 q=root/p.relative_to(src);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
for p in (src/'scripts').glob('*'):
 if p.suffix in ('.py','.sh'):
  q=root/'scripts'/p.name;q.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(p,q)
(root/'native/cluster-bridge/live/build').mkdir(parents=True,exist_ok=True)
for name in ('.tools','delphi-dump','delphi-analysis'):os.symlink(str(src/name),str(root/name))
profile=root/'native/cluster-bridge/layout-margin';profile.mkdir(exist_ok=True,parents=True)
for name in ('wire-margin.c','margin-fixture.c','vectors.h'):shutil.copyfile(out/name,profile/name)
for p in root.rglob('*.sh'):
 if p.is_symlink():continue
 p.write_text(p.read_text().replace('/src',str(root)))
t=root/'native/secondary-display/test-qemu.sh'
v=subprocess.run(['sh',str(t)],capture_output=True,text=True);(out/'build.log').write_text(v.stdout+v.stderr)
log=root/'native/secondary-display/qemu/qemu.log'
if log.exists():shutil.copyfile(log,out/'qemu.log')
if v.returncode:raise RuntimeError((v.stdout+v.stderr)[-7000:])
assert 'CLUSTER_MARGIN_QNX_PASS' in log.read_text()
release=out/'release';release.mkdir(exist_ok=True);shutil.copyfile(root/'native/secondary-display/build/libdelphi_observer_keyframe.so',release/'libdelphi_observer.so')
print('Private QNX margin build and existing secondary/cleanup regressions passed.')
