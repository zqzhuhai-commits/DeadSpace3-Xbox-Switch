from pathlib import Path
import subprocess,re,json
r=Path('/workspace/ds3-nx-upstream');cg=r/'ds3/out/codegen';st=cg/'staging';names=r/'ds3/codegen/names_awakened.toml'
s=(cg/'ds3_awakened_manifest.toml').read_text();prefix=s.split('[[modules]]',1)[0];module='[[modules]]\nfile_path="game/awakened.xex"\nout_directory_path="generated/awakened"\nguest_path="pdlc/awakened.xex"\nincludes=[]\n'
for attempt in range(6):
 hints=names.read_text();(st/'ds3_awakened_manifest.toml').write_text(prefix+module+re.sub(r'^\[entrypoint\.functions\.', '[modules.functions.',hints,flags=re.M))
 log=Path('/workspace/ds3-analysis')/f'dlc-regenerate-{attempt}.log'
 with log.open('w') as f:
  subprocess.run(['/workspace/ds3-analysis/host-src/out/linux-amd64/rexglue','--force','codegen','ds3_awakened_manifest.toml'],cwd=st,stdout=f,stderr=subprocess.STDOUT,check=True)
 text=log.read_text();a=set(re.findall(r'Unresolved (?:b target|function|conditional branch to) 0x([0-9A-Fa-f]{8})',text));new=sorted(x.upper() for x in a if x.upper().startswith('88') and f'[entrypoint.functions.0x{x.upper()}]' not in hints)
 print('DLC attempt',attempt,'new targets',new,flush=True)
 if not new:break
 for x in new:hints+=f'\n[entrypoint.functions.0x{x}]\nname = "dlc_discovered_{x}"\n'
 names.write_text(hints)
else:raise RuntimeError('DLC branch discovery did not converge')
# Update the reproducible manifest after convergence.
(cg/'ds3_awakened_manifest.toml').write_text((st/'ds3_awakened_manifest.toml').read_text())
