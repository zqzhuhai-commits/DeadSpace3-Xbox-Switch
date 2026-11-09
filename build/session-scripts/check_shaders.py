import pathlib,struct,ctypes,json,collections,re
lib=ctypes.CDLL('libxxhash.so.0');lib.XXH3_64bits.argtypes=[ctypes.c_void_p,ctypes.c_size_t];lib.XXH3_64bits.restype=ctypes.c_uint64
def h(b):return lib.XXH3_64bits(b,len(b))
def u(b,o=0):return struct.unpack_from('<I',b,o)[0]
def q(b,o=0):return struct.unpack_from('<Q',b,o)[0]
root=pathlib.Path('/workspace/attachments');b=next(root.rglob('ds3_shaders.dslib')).read_bytes();c=next(root.rglob('shadercache_dksh.bin')).read_bytes()
assert b[:8]==b'DS2SPV\0\0' and u(b,8)==1 and h(b[24:])==q(b,16)
p=24; hashes=set();stages=collections.Counter();prev=None
for i in range(u(b,12)):
 n,w,hh=struct.unpack_from('<IIQ',b,p);p+=16
 original=b[p:p+n];p+=n;spv=b[p:p+w*4];p+=w*4
 assert len(original)==n and len(spv)==w*4 and h(original)==hh
 sig,v,phys=struct.unpack_from('>III',original);assert sig&~1==0x102a1100 and v+phys==n and phys%4==0
 assert u(spv)==0x07230203 and u(spv,16)==0
 key=(hh,original);assert prev is None or prev<key;prev=key
 pos=5;entries=0
 while pos<w:
  inst=u(spv,pos*4);wc=inst>>16;op=inst&65535;assert wc and pos+wc<=w
  if op==15:
   assert wc>=5 and u(spv,(pos+1)*4)==(0 if sig&1 else 4) and spv[(pos+3)*4:(pos+5)*4]==b'main\0\0\0\0';entries+=1
  pos+=wc
 assert entries==1
 hashes.add(h(spv));stages['VS' if sig&1 else 'PS']+=1
assert p==len(b)
assert c[:4]==b'NFDK' and u(c,4)==2 and h(c[32:])==q(c,24)
n=u(c,16);p=32+24*n;cached=set();keys=set();badmagic=0;empty=0
for i in range(n):
 hh,spec,var,size,res=struct.unpack_from('<QIIII',c,32+24*i);key=(hh,spec,var);assert key not in keys;keys.add(key)
 assert size<=1<<20 and p+size<=len(c)
 payload=c[p:p+size];p=(p+size+3)&~3
 if size:badmagic+=payload[:4]!=b'DKSH'
 else:empty+=1
 cached.add(hh)
assert p==len(c)
id='uam 1.1.0 + SwitchWakerHD 2d147aa (patches 1-7); SPIRV-Cross vulkan-sdk-1.4.363.0; GLSL revision 1'
r={'library_bytes':len(b),'library_entries':sum(stages.values()),'stages':dict(stages),'library_hash_and_structure':'passed','cache_bytes':len(c),'cache_entries':n,'cache_hash_and_structure':'passed','cache_compiler_matches_upstream':h(id.encode())==q(c,8),'unique_library_spirv':len(hashes),'unique_cached_spirv':len(cached),'library_spirv_without_any_cache_variant':len(hashes-cached),'cache_spirv_not_in_library':len(cached-hashes),'empty_cache_entries':empty,'bad_DKSH_magic':badmagic}
for f in ['original.nro','dlc.nro']:
 data=(pathlib.Path('/workspace/ds3-analysis')/f).read_bytes();r[f+'_has_expected_compiler_id']=id.encode() in data
print(json.dumps(r,indent=2));pathlib.Path('/workspace/ds3-analysis/shader-validation.json').write_text(json.dumps(r,indent=2))
