from pathlib import Path
import time,shutil,filecmp,subprocess
r=Path('/workspace/ds3-nx-upstream');cg=r/'ds3/out/codegen';log=Path('/workspace/ds3-analysis/finish-codegen.log')
while 'awakened patch_branch_traps' not in log.read_text():
 if 'Traceback' in log.read_text():raise RuntimeError('codegen failed')
 time.sleep(10)
for m in ['default','game']:
 src=cg/'staging/generated'/m;dest=cg/'generated'/m
 dest.mkdir(parents=True,exist_ok=True)
 for p in src.iterdir():
  d=dest/p.name
  if not d.exists() or not filecmp.cmp(p,d,shallow=False):shutil.copy2(p,d)
 for p in dest.iterdir():
  if not (src/p.name).exists():p.unlink()
with Path('/workspace/ds3-analysis/base-build.log').open('w') as f:
 subprocess.run(['docker','exec','--user','1000:1000','ds3-builder','sh','-c','cmake -S /workspace/ds3-nx-upstream/ds3 -B /workspace/ds3-nx-upstream/ds3/out/sw > /workspace/ds3-analysis/base-configure.log 2>&1 && cmake --build /workspace/ds3-nx-upstream/ds3/out/sw --target ds3_deadspace_game_f ds3_recomp -j 2'],stdout=f,stderr=subprocess.STDOUT,check=True)
