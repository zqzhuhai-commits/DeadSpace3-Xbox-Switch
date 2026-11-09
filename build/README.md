# test1 完整构建记录

本目录记录生成已上传 `1.0.1-dlc-test1` 的实际过程、脚本、日志和校验结果。`../source/` 是上游 v1.0.1 的完整项目文件快照及本次修改；SDK 和第三方依赖由固定提交获取，不包含游戏 XEX、XEXP、游戏资源或生成的游戏 C++。

**验证范围：**本次 NRO 已编译、链接、校验通过，未在 Switch 实机验证。下面的 Dockerfile 和便携入口是根据实际执行步骤整理的，从全新环境执行这套入口尚未完整重跑，因此不承诺逐字节一致的重建。

## 目录

| 路径 | 内容 |
| --- | --- |
| `evidence/` | 上游提交、工具链、输入 SHA-256、模块数量和 NRO 校验结果 |
| `logs/` | 主机工具构建、依赖准备、代码生成、CPU 优化、Switch 编译与链接日志 |
| `session-scripts/` | 本次会话实际使用的恢复、分析、校验和打包脚本；保留原绝对路径，供审计，不能直接当作通用入口 |
| `manifests/` | 本体和 Awakened 分开运行的代码生成配置 |
| `analysis/` | 排查记录、钩子匹配、缺失函数和当时工具故障的调用栈 |
| `../debug/` | 与已上传 NRO 精确对应的 ELF 和链接映射压缩包 |

日志包含失败、人工中断及恢复步骤，不应将每个日志的结束状态都当作最终构建结果。早期部分日志已被同名重试覆盖；这里保存现存的全部构建日志，不是逐条终端录屏。

## 实际经过

1. 解压用户提供的 TU 与 DLC，解析 XEX 元数据、记录哈希；检查两个 NRO、着色器库和缓存。
2. 固定上游 `717ae41deaf9c22059d6f27a0376d18cb443ca43`、Switch SDK `f961303fe3c6e3a90905b379ff4bf3de9a35a757`。该上游版本与原版日志提交 `06670fdd2f...` 仅文档不同。
3. 构建 ReXGlue v0.10.0，应用 Hell's Gate 固定提交 `3ce3993b0f03c77353f8f10fdcd982160c9a2d18` 的 SDK 补丁和项目的 dump-image 补丁。Linux 编译用 Clang 19、`-mssse3`。
4. 初次联合加载本体和 DLC 进行生成，因它们的 Xbox 映像均位于 `0x88000000`，发生映像覆盖和工具异常。最终实现改为两个独立进程生成，再合并模块注册表。临时的异常表边界检查没有保留到最终主机工具。
5. 本体沿用原来的函数提示；DLC 通过函数体比对适配 15 个钩子、setjmp/longjmp、日志中的 8 个缺失入口及生成检查发现的额外分支。修正 DLC 专用分辨率变量地址；加载及卸载按 DLC 入口点选择独立模块。
6. 本体代码生成后完成分支修复、栈访问、同文件调用内联和寄存器局部化。DLC 曾补充目标后单独重试，最后运行 `finish_codegen.py --dlc-only`；没有重新执行已优化的本体。
7. Switch SDK 先构建，本体编译与 DLC 优化部分并行，最后统一运行 CMake 构建目标 `ds3 -j 4`。最终完整链接日志为 `logs/final-build.log`，529/529 项成功。
8. 校验 ARM64 ELF、NRO 段、版本、两个模块符号、DLC 入口及 8 个缺失函数注册；压缩包 CRC 和 GitHub 下载后的 SHA-256 相同。结果见 `evidence/build-verification.json`。

原版不能进入 DLC 的直接证据来自未标记修改的 `ds3_003.log`：加载器将 DLC 匹配成本体，因映像范围 `88000000-89200000` 与 DLC 的 `88000000-89220000` 不一致而拒绝，随后回退本体。修改版的画面异常和章节存档闪退是另一组证据，不能归为原版故障；本次未修改游戏存档格式，也未用忽略非法访问的方式掩盖闪退。

## 从零重建入口（Linux x86_64 / Docker）

本仓库所在路径必须以相同绝对路径挂载到两个容器，生成的链接才可在二者间复用。输入目录也应放在这个挂载路径内，例如 `inputs/tu/` 和 `inputs/dlc/deadspace_game_f.xex`；它们不应提交到 Git。当前云任务已经隔离，使用现有 checkout 即可，不需要创建 Git worktree。

构建镜像：

```sh
docker build -f build/Dockerfile.host -t ds3-build-host .
docker build -f build/Dockerfile.switch -t ds3-build-switch .
```

在使用 HTTPS 检查代理的环境中，镜像构建应加 `--secret id=proxy_ca,src="$CODEX_PROXY_CERT"`。运行容器时以只读方式挂载环境提供的合并 CA bundle，并设置相应的 `SSL_CERT_FILE`、`GIT_SSL_CAINFO`；保留平台提供的代理设置和 TLS 校验。不要把凭据或 CA 私密文件复制进镜像。

以下命令假定普通系统 CA 已足够；托管代理环境应按上一段加入 CA 挂载：

```sh
# 主机代码生成工具需要较大的共享内存，使用 2 GiB，避免中断留下的 shm 文件耗尽默认 64 MiB。
docker run --rm --shm-size=2g --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$PWD,dst=$PWD" -w "$PWD" ds3-build-host \
  bash build/prepare-source.sh "$PWD/work/ds3-nx"

docker run --rm --shm-size=2g --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$PWD,dst=$PWD" -w "$PWD" ds3-build-host \
  bash build/prepare-host.sh "$PWD/work/ds3-nx" "$PWD/work/host"

docker run --rm --shm-size=2g --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$PWD,dst=$PWD" -w "$PWD" ds3-build-host \
  bash build/generate.sh "$PWD/work/ds3-nx" "$PWD/inputs/tu" "$PWD/inputs/dlc/deadspace_game_f.xex"

docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$PWD,dst=$PWD" -w "$PWD" ds3-build-switch \
  bash build/compile-switch.sh "$PWD/work/ds3-nx"

docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$PWD,dst=$PWD" -w "$PWD" ds3-build-switch \
  python3 build/verify.py "$PWD/work/ds3-nx"
```

SDK 第三方依赖准备和代码生成会访问 GitHub。生成器必须使用带项目所需补丁的版本；官方未打补丁的可执行文件不能替代。构建镜像固定，APT 中的辅助软件包未全部固定版本，实际版本记录见 `evidence/host-packages.txt`。主机工具在 Debian 13 构建，Switch 编译镜像基于 Debian 12，因此不要在 Switch 镜像中运行 Debian 13 编译出的主机工具。

输出为 `work/ds3-nx/ds3/out/sw/ds3.nro`。不需要重新生成本次未修改的着色器文件。已发布测试 NRO 的 SHA-256 为 `d71cc10a4d91cb477acca893ec6be4820f7f76e296eef3a0d9740b738cb8e165`。

## 调试文件

下载 `../debug/ds3-test1-symbols.zip` 后解压，得到 `ds3-test1.elf` 和 `ds3-test1.map`。它们只对应本仓库当前 test1 NRO。可以使用 devkitA64 的 `aarch64-none-elf-addr2line -f -C -e ds3-test1.elf <image+偏移>` 查函数名；生成代码按原配置未保留完整行号信息，部分位置只能定位到符号。
