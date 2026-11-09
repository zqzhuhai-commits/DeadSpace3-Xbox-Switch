# Dead Space 3 Switch — DLC 测试版

基于 [VasilkovND/ds3-nx v1.0.1](https://github.com/VasilkovND/ds3-nx/tree/v1.0.1) 稳定源码构建的非官方测试版，版本号 `1.0.1-dlc-test1`。

## 下载

- [NRO 测试包（约 53 MB）](https://github.com/zqzhuhai-commits/DeadSpace3-Xbox-Switch/raw/refs/heads/main/ds3-nx-1.0.1-dlc-test1.zip)
- [源码改动包](https://github.com/zqzhuhai-commits/DeadSpace3-Xbox-Switch/raw/refs/heads/main/ds3-nx-1.0.1-dlc-source-changes.zip)
- [SHA-256 校验值](SHA256SUMS.txt)

## 使用

先备份原 NRO 和存档，再将测试包中的 `ds3-nx.nro` 替换到原游戏目录。游戏数据、TU、DLC 数据、`ds3_shaders.dslib` 和 `shadercache_dksh.bin` 保持原样，不要重命名 DLC 内的 `deadspace_game_f.xex`。使用原有的完整内存启动方式。

## 改动与验证

加入独立的 Awakened 重编译模块，修正同名游戏可执行文件的模块选择（加载及卸载），补充日志中的缺失函数和分支入口，并适配 DLC 专用的钩子及分辨率变量地址。本体渲染实现沿用稳定版。

编译、链接、NRO 结构、模块注册及压缩包完整性检查已通过。尚未完成 Switch 实机验证，不能保证显示异常和章节存档闪退已全部消除。请重点测试 DLC 入口、第一章画面和存档选择；详细说明在测试包内。

适配本次提供的 TU（Media ID `7139B889`，更新版本 `0.0.1.8`）及 Awakened（Media ID `20AF2ACB`，版本 `1.2.0.1`）。

源码改动包应覆盖到上游 v1.0.1 源码，并按其中的 `ds3/DLC_TEST.md` 构建；不包含游戏可执行文件或生成的游戏源码。测试包内保留许可证与第三方说明。
