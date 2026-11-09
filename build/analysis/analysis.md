# DS3 NRO 初步分析

基准源码：VasilkovND/ds3-nx v1.0.1，提交 717ae41deaf9c22059d6f27a0376d18cb443ca43。

## 实测
- ZIP CRC 检查通过，共两个 NRO，没有配置、日志、着色器库、游戏文件或修改源码。
- original.nro：55,511,237 字节；代码段 49,111,040 字节。
- dlc.nro：109,992,133 字节；代码段 94,683,136 字节。
- 两者 NACP 版本均为 0.0.1 (TU1)，不能据此确认对应上游版本。
- 两者 ASET 均无 RomFS；增加的体积主要在程序段，并非内嵌着色器包。
- DLC 版独有字符串包括 ds3_awakened、pdlc/awakened.xex，以及 generated_nx/awakened/ds3_pch.h 构建路径，强烈表明加入独立 Awakened 重编译模块。
- 两者构建路径不同，不能认为 DLC 版仅有单一功能改动，也不能据体积断定故障原因。

## 源码证据与判断
- ds3/src/ds3_gpu.cpp 从外部读取 ds3_shaders.dslib；缺少 VS/PS 会进入缺失着色器处理路径。当前压缩包不足以检查库和 DKSH 缓存是否匹配或覆盖 DLC。
- ds3/PORTING.md 记录 CPU 蒙皮与几何缓存信任机制相关的旧姿态风险，0029 补丁默认 nfsmw_dk_geometria_confianza=1；值得对照故障版配置与源码，尚未证明这是上半身消失的根因。
- PORTING.md 还记录深度、渲染目标、着色器转换引起的历史黑屏/暗场问题；仅凭症状不能确定具体回归。
- SDK 已有 Marketplace 内容枚举与挂载基础，因此 DLC 支持不是从零实现；但 Awakened 的额外可执行模块仍需生成代码、注册并验证，不能仅修改一个标志。

## 推荐路线
优先取得 DLC 版对应修改源码/补丁，保留其 DLC 模块，对照稳定版修复渲染差异；若拿不到修改源码，以上游稳定源码加入 DLC 支持比盲改 NRO 更可维护。现有二进制不足以保证重建精确版本或安全移植机器码。

## 下一步所需材料
故障版对应源码或构建仓库；SD 目录 ds3.toml、ds3_shaders.dslib、shadercache_dksh.bin、logs/；能复现的章节/场景及存档（先备份）。重建还需本人游戏的两张盘和 TU1，Awakened 模块需对应 DLC 文件。尚未编译或在 Switch 上复现，未修改 NRO，未交付修复。

## Implementation findings
The 1.0.1 and 06670fdd2f baseline differ only in README/INSTALL text. The supplied TU is Media ID 7139B889, patched version 0.0.1.8; the supplied DLC is Media ID 20AF2ACB, version 1.2.0.1. Both guest game images start at 0x88000000, so codegen must run in separate processes. A combined manifest overwrites the base snapshot before analysis and is rejected for overlapping modules; the implementation uses separate manifests and merges only the registry. This is a build-tool constraint, not proof that the previously supplied NRO was built incorrectly.

The old NRO crash instruction at image+0x4ef3444 matches a read of r31+420 (0x1A4), followed by comparison to 207, in DLC guest function 0x88A5D4D0. The caller/object-lifetime cause remains unproven. No null-read suppression was added.

Original-build evidence: ds3_003.log starts with commit 06670fdd2f without +changes. Line 65 rejects the DLC using the base recompiled module: DLL image 88000000-89200000 versus loaded XEX 88000000-89220000; lines 71-73 subsequently register the base module. This directly supports the content-enumeration-success / DLC-entry-disabled report. Later modified-build crashes are separate evidence and are not attributed to the original build.
