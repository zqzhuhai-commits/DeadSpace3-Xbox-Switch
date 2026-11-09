from pathlib import Path
import struct,hashlib,json,re,subprocess
root=Path('/workspace/ds3-nx-upstream');build=root/'ds3/out/sw';cg=root/'ds3/out/codegen/generated'
elf=(build/'ds3').read_bytes();assert elf[:4]==b'\x7fELF' and struct.unpack_from('<H',elf,18)[0]==183
nro=build/'ds3.nro';b=nro.read_bytes();u=lambda o:struct.unpack_from('<I',b,o)[0]
assert b[16:20]==b'NRO0'
size=u(24);assert 128<size<=len(b)
segs=[struct.unpack_from('<II',b,o) for o in [32,40,48]]
assert segs[0][0]==0
for (off,n),(nextoff,_) in zip(segs,segs[1:]):assert off+n<=nextoff
assert segs[-1][0]+segs[-1][1]<=size
asset=b[size:];assert asset[:4]==b'ASET'
o,n=struct.unpack_from('<QQ',asset,24);assert o+n<=len(asset) and n==0x4000
nacp=asset[o:o+n];version=nacp[0x3060:0x3070].split(b'\0')[0].decode();assert version=='1.0.1-dlc-test1',version
counts={m:len(re.findall(r'SetFunction\(', (cg/m/'ds3_register.cpp').read_text())) for m in ['default','game','awakened']}
assert counts['game']==54996
missing=json.loads(Path('/workspace/ds3-analysis/missing-functions.json').read_text())
s=(cg/'awakened/ds3_register.cpp').read_text()
for addr in [*missing,'0x88C9B260']:assert 'SetFunction('+addr+',' in s
symbols=subprocess.check_output(['/opt/devkitpro/devkitA64/bin/aarch64-none-elf-nm','--defined-only',str(build/'ds3')],text=True)
for symbol in ['ReXModule_Register_ds3_deadspace_game_f','ReXModule_Register_ds3_awakened','ReXModule_GetImageInfo_ds3_awakened']:assert symbol in symbols,symbol
r={'nro_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'version':version,'segments':segs,'registered_function_counts':counts,'all_8_logged_missing_functions_registered':True,'both_guest_modules_linked':True,'console_test':'not run'}
Path('/workspace/ds3-analysis/build-verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
