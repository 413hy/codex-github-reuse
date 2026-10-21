# Codex：GitHub 复用优先开发

版本：1.0.0 · 文档核验日期：2026-10-21

这套配置让 Codex 在新项目和重要功能开发前，先完整理解需求，有疑问立即提问；明确后真实查找 GitHub 中合适的实现，直接完成完整可运行 demo，并自行检查和修复。
它适用于页面、交互、功能模块、架构、prompt 和 agent 工作流。

需求澄清完成后，默认一路做到完整演示交付，再通过对话修改优化。流程中不额外要求方案审批、逐项授权、用户手动测试或验收后才能继续。

成品也默认打开即可用：不额外添加登录注册、授权申请、激活码、验证码、审批、功能解锁、付费墙、次数限制或反复确认弹窗。
必要的数据检查由程序自动完成。若外部服务暂不可用，先完成明确标注的本地模拟流程；模拟不会被描述成真实服务已接通。

## 推荐用法：让 Codex 安装到当前用户

先解压压缩包，再用你实际开发时使用的 Codex 打开本目录，把下面这段发给它：

> 请阅读这个目录的 INSTALL.zh-CN.md，把 github-reuse-first 安装为当前用户的全局 Codex Skill，并将 rules/AGENTS.github-reuse.md 的管理区块合并到实际生效的全局指令文件。优先使用包内 install.py；已有规则必须保留，改动前备份。如果没有合适的 Python，按文档手动安装。安装后告诉我真实写入路径，并验证 Skill 和入口规则能否被发现。不要修改模型、代理、账号或安全设置。

安装在运行 Codex 的那台机器、那个操作系统和那个用户下。
Windows 原生 Codex、WSL 中的 Codex、VPS 上的 Codex 各有自己的用户目录，需要分别安装。

## 手动执行安装器

安装器要求 **Python 3.9 或更高版本**，只使用标准库。以下命令均在解压后的本目录运行。

Windows：

```powershell
py -3 install.py --global
```

Linux / macOS / WSL：

```bash
python3 install.py --global
```

不带范围参数时也默认为全局安装。可先使用 `--dry-run` 查看计划，不会写入文件。

安装位置遵循当前 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills) 与
[AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)：

| 内容 | 全局位置 |
| --- | --- |
| 技能目录 | 当前用户的 `~/.agents/skills/github-reuse-first/` |
| 常驻规则 | `CODEX_HOME` 下的 `AGENTS.md`；未设置时为 `~/.codex/AGENTS.md` |
| 有效覆盖文件 | 对应目录若有非空 `AGENTS.override.md`，安装器合并到这个实际生效的文件 |

这里的 `~` 指执行安装器的用户主目录；Windows 下通常在用户配置目录。
自定义 `CODEX_HOME` 影响全局指令位置；本包仍按官方本地技能文档把用户技能放在 `~/.agents/skills/`。

### 安装器如何保留已有配置

- 只维护 `github-reuse-first:start` 与 `github-reuse-first:end` 之间的管理区块。
- 保留其它规则、UTF-8 BOM 和已有换行风格。
- 改动已有规则前在同目录生成带时间标记的 `.bak-...` 备份。
- 已存在相同内容时不重复写入，也不产生多余备份。
- 同名技能内容不同时自动备份并更新，无需额外确认；`--update` 保留为兼容选项。
- 技能备份放在 `.agents/skill-backups/`，避免被当成另一个已安装技能。
- 遇到损坏/重复的管理标记、非 UTF-8 规则、符号链接或路径重叠时停止，并说明原因。

本包不会下载其它仓库、安装 MCP、设置 token、改变联网权限或修改 Codex 的模型与安全配置。
联网搜索能力来自你原有的 Codex 环境；本技能只规定如何使用已有能力。

## 安装后确认生效

重新启动 Codex 会话，使新常驻规则被加载。用 `/skills` 查看是否有 `github-reuse-first`，
或在输入框中输入 `$github-reuse-first` 选择技能。可以让 Codex 只检查配置：

> 请列出当前有效的全局和项目指令来源，确认 github-reuse-first 技能的位置，并说明什么任务会触发它。这次只检查，不修改项目。

第一次实际使用可明确点名：

> 使用 $github-reuse-first 开发这个项目。先把我的需求全部理解好，有任何疑问立即问；明确后去 GitHub 搜索并适配可用实现，直接交付完整可运行 demo，自检和修复由你完成，之后再按我的反馈优化。

之后正常描述开发需求即可。常驻入口要求适用任务先调用技能；Skill 的描述也允许隐式匹配。
这是对 AI 行为的明确指导，不能保证每次推理都完全遵守；项目级指令、禁用技能配置、上下文长度和联网能力仍会影响执行。
如果没有触发，先明确点名技能，并检查更近的项目指令或覆盖文件。

官方依据：技能支持显式/隐式调用和本地发现；AGENTS.md 在会话启动时构建指令链。
参见上方两份官方文档；无需为此关闭沙箱或审批机制。

## 只安装到一个项目

你希望跨项目使用时选全局安装。仅让一个项目采用规则时，可运行：

```bash
python3 install.py --project "/absolute/path/to/project"
```

Windows 将 `python3` 换成 `py -3`，并提供实际项目路径。
目标项目必须已经存在；安装器不会创建新的业务项目。

这会使用项目中的 `.agents/skills/github-reuse-first/` 和 `AGENTS.md`，
存在有效 `AGENTS.override.md` 时使用后者。安装器不会自动提交、推送项目文件。
不要同时安装多份同名技能，除非你明确需要并理解 Codex 对重复名称的发现行为。

## 没有 Python 时

手动完成两个文件操作即可，也可以交给 Codex：

1. 把 `skills/github-reuse-first/` 整个目录复制到当前用户的 `~/.agents/skills/`，保留目录名。
2. 备份实际生效的全局指令文件，将 `rules/AGENTS.github-reuse.md` 中完整管理区块合并进去；保留其它内容，不要用它覆盖整个文件。

如果此前已有本包管理区块，只更新这一块。发现多个或不完整区块，先查看文件，不要猜测合并位置。
然后重新启动 Codex 会话并确认技能可见。

## 更新与移除

更新本包时使用：

```bash
python3 install.py --global --update
```

Windows 同样可使用 `py -3`。项目安装时使用原来的 `--project` 范围再加 `--update`。

移除时，只删除对应的 `github-reuse-first` 技能目录，以及有效指令文件中本包的管理区块。
不要删除整个 `.agents/skills/`、`AGENTS.md` 或 `AGENTS.override.md`。
若安装后你另有修改，不要直接恢复整个旧备份覆盖后续工作；先对照差异。

## 包内内容

| 文件/目录 | 用途 |
| --- | --- |
| `skills/github-reuse-first/SKILL.md` | 主开发流程与触发范围 |
| `skills/github-reuse-first/agents/openai.yaml` | 名称、入口示例与隐式调用配置 |
| `skills/github-reuse-first/references/` | 检索、筛选和按任务验证的细则 |
| `skills/github-reuse-first/assets/reuse-record.md` | 项目研究与实际整合记录模板 |
| `rules/AGENTS.github-reuse.md` | 常驻入口规则 |
| `install.py` | 保留已有配置的安装器 |
| `EXAMPLES.zh-CN.md` | 常见使用请求与预期行为 |
| `SOURCES.md` | 本次 GitHub 研究来源、采用方式与限制 |
| `VALIDATION.md` | 实际验证结果和未覆盖范围 |
| `tests/test_install.py` | 安装器的隔离测试 |
| `source-history.bundle` | 可选的离线 Git 源码版本记录，不参与安装 |

## 调整你的偏好

希望改变默认搜索范围、输出记录或 demo 要求时，修改技能中的对应规则。
如果修改常驻入口模板，要重新安装使它合并到有效指令文件。
不要把某次项目的技术栈或一份固定“热门仓库清单”写成所有未来项目的强制依赖。
