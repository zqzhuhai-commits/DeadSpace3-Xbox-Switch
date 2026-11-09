from pathlib import Path
import subprocess,os,shutil,filecmp,re,json,sys
r=Path('/workspace/ds3-nx-upstream');cg=r/'ds3/out/codegen';st=cg/'staging';tools=r/'ds3/tools'
# Preserve the clean generator output before applying CPU transforms.
modules = ['awakened'] if '--dlc-only' in sys.argv else ['default','game','awakened']
for m in modules:
 shutil.copytree(st/'generated'/m,cg/'raw/generated'/m,dirs_exist_ok=True)
for m in modules:
 root=st/'generated'/m
 cpp=[str(x) for x in sorted(root.glob('*.cpp'))]
 recomp=[str(x) for x in sorted(root.glob('ds3_recomp.*.cpp'))]
 assert cpp and recomp
 srcs=[str(r/'ds3/src'),str(r/'sdk/src'),str(r/'sdk/include')]
 commands=[('patch_branch_traps',[*cpp]),('patch_stack_access',[*cpp]),('patch_inline_calls',[*srcs,'--',*recomp]),('patch_local_regs',[str(root/'ds3_inline_helpers.h'),*srcs,'--',*recomp])]
 for step,args in commands:
  log=cg/(step+'.'+m+'.log');env=os.environ.copy();env['PLR_MAP']=str(cg/('patch_local_regs.'+m+'.check.map'))
  print(m,step,flush=True)
  with log.open('w') as f:subprocess.run(['python3',str(tools/(step+'.py')),*args],stdout=f,stderr=subprocess.STDOUT,env=env,check=True)
  print(log.read_text()[-500:],flush=True)
for m in ['default','game','awakened']:
 src=st/'generated'/m;dest=cg/'generated'/m;dest.mkdir(parents=True,exist_ok=True)
 for f in src.iterdir():
  d=dest/f.name
  if not d.exists() or not filecmp.cmp(f,d,shallow=False):shutil.copy2(f,d)
 for f in dest.iterdir():
  if not (src/f.name).exists():f.unlink()
# Static registration checks against every address observed missing at runtime.
a=(cg/'generated/awakened/ds3_register.cpp').read_text()
missing=json.loads(Path('/workspace/ds3-analysis/missing-functions.json').read_text())
for addr in missing:assert 'SetFunction('+addr+',' in a,addr
registry=(cg/'generated/default/module_registry.cpp').read_text()
assert registry.count('"pdlc/awakened.xex"')==1 and registry.count('"deadspace_game_f.xex"')==2
for m in ['default','game','awakened']:
 for f in (cg/'generated'/m).glob('*.cpp'):
  assert not re.search(r'REX_FATAL\("Unresolved (?:branch|call)',f.read_text()),str(f)
print('All logged missing functions registered; no unresolved branch traps remain.',flush=True)
