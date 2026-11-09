import re,pathlib,collections,hashlib,json
F=re.compile(r'^DEFINE_REX_FUNC\((\w+)\) \{',re.M);I=re.compile(r'^\t// ([a-z][\w.+-]*)(?: (.*))?$',re.M)
def scan(root):
 d={}
 for p in pathlib.Path(root).glob('*.cpp'):
  s=p.read_text();ms=list(F.finditer(s))
  for j,m in enumerate(ms):d[m[1]]=I.findall(s[m.end():ms[j+1].start() if j+1<len(ms) else len(s)])
 return d
def norm(ins):
 out=[]
 for op,args in ins:
  if op.startswith('b') and op not in ['blr','bctr','blrl','bctrl']:
   args=re.sub(r'0x[0-9a-fA-F]+','T',args)
  if op in ['lis','addis']:args=re.sub(r',-?\d+$',',H',args)
  # Address low halves can move between executable versions.
  args=re.sub(r'-?\d{4,}','N',args)
  out.append(op+' '+args)
 return tuple(out)
a=scan('/workspace/ds3-analysis/base-probe/generated/game');b=scan('/workspace/ds3-analysis/diagnostic-codegen/generated')
by=collections.defaultdict(list)
for n,i in b.items():by[norm(i)].append(n)
result={}
for name,ins in a.items():
 if not(name.startswith('ds3_') or name.startswith('rw__') or name in ['sub_88C99620','sub_88C991F0']):continue
 c=by[norm(ins)];print(name,c)
 if len(c)==1:result[name]=c[0]
 if name=='ds3_D3DDevice_SetGammaRamp':
  for n in c:
   diffs=[(x,y) for x,y in zip(ins,b[n]) if x!=y];print(n,'diffs',diffs[:15])
pathlib.Path('/workspace/ds3-analysis/hook-map.json').write_text(json.dumps(result,indent=2))
for name in ['sub_88A275C0','sub_88C96B30']:
 print('gamma dependency',name,by[norm(a[name])])
for key,ins in [('base resolution',a['ds3_ConfigureDisplay']),('dlc resolution',b['sub_889606B0'])]:
 print(key,[(op,args) for op,args in ins if op in ['lis','sth','stfs','stw','addi']])
