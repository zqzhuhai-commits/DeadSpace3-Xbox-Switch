from pathlib import Path
import shutil,zipfile,hashlib,json,subprocess
r=Path('/workspace/ds3-nx-upstream');a=Path('/workspace/ds3-analysis');dist=a/'dist';dist.mkdir(exist_ok=True)
verification=json.loads((a/'build-verification.json').read_text())
assert verification['version']=='1.0.1-dlc-test1'
nro=r/'ds3/out/sw/ds3.nro';assert hashlib.sha256(nro.read_bytes()).hexdigest()==verification['sha256']
shutil.copy2(nro,dist/'ds3-nx-1.0.1-dlc-test1.nro')
readme='''死亡空间3：1.0.1 稳定源码 + Awakened DLC 测试版（test1）

本版针对原版“识别到 DLC 但加载器把 DLC 匹配成本体、因映像大小不同而拒绝加载”的路径，加入独立的 DLC 模块和正确选择逻辑；补充编译版日志中缺失的函数及分支入口，适配 DLC 的钩子和分辨率变量地址。本体渲染实现沿用稳定版。

使用方法：
1. 先备份现有 NRO 和存档。
2. 将包内 ds3-nx.nro 替换到 SD 卡原游戏目录。
3. 保留原有 tu、disc1、disc2、DLC 数据、ds3_shaders.dslib 和 shadercache_dksh.bin，不要重命名 DLC 内的 deadspace_game_f.xex。
4. 使用已有的完整内存启动方式（按住 R 启动游戏，进入 Homebrew Menu）。

测试顺序：检查启动日志版本为 1.0.1-dlc-test1；确认本体正常；检查 Awakened 入口、第一章画面、新存档保存/读取，以及此前选择章节存档时闪退的操作。建议先用新存档槽测试。

已完成：代码生成、分支检查、目标平台编译/链接、NRO 结构和模块注册静态校验。
尚未完成：Switch 实机运行验证。因此这是测试版，不代表黑屏、人物消失或存档闪退已全部消除。
如需回退，恢复备份的 NRO；存档备份单独保留。若测试异常，请保留这次运行产生的 logs。

适配输入：本次提供的 TU（Media ID 7139B889，更新版本 0.0.1.8）及 Awakened（Media ID 20AF2ACB，版本 1.2.0.1）。
'''
(dist/'测试说明.txt').write_text(readme)
with zipfile.ZipFile(dist/'ds3-nx-1.0.1-dlc-test1.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.write(nro,'ds3-nx.nro');z.writestr('测试说明.txt',readme);z.write(a/'build-verification.json','build-verification.json');z.write(r/'LICENSE','LICENSE');z.write(r/'THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES.md')
changed=subprocess.check_output(['git','-C',str(r),'diff','--name-only'],text=True).splitlines()
untracked=subprocess.check_output(['git','-C',str(r),'ls-files','--others','--exclude-standard'],text=True).splitlines()
files=sorted(set(changed+untracked+['LICENSE','THIRD_PARTY_NOTICES.md']))
with zipfile.ZipFile(dist/'ds3-nx-1.0.1-dlc-source-changes.zip','w',zipfile.ZIP_DEFLATED) as z:
 for rel in files:
  p=r/rel
  if p.is_file():z.write(p,rel)
 z.writestr('APPLY.txt','Apply these changed files over VasilkovND/ds3-nx tag v1.0.1 (717ae41deaf9c22059d6f27a0376d18cb443ca43), with its sdk submodule initialized. The new SDK patch is applied by the existing build script. See ds3/DLC_TEST.md. Game executables and generated game sources are not included.\n')
elf=dist/'debug';elf.mkdir(exist_ok=True);shutil.copy2(r/'ds3/out/sw/ds3',elf/'ds3-test1.elf');shutil.copy2(r/'ds3/out/sw/ds3.map',elf/'ds3-test1.map')
with (dist/'SHA256SUMS.txt').open('w') as f:
 for p in sorted(dist.iterdir()):
  if p.is_file() and p.name!='SHA256SUMS.txt':f.write(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n')
for p in sorted(dist.iterdir()):
 if p.is_file():print(p.name,p.stat().st_size)
