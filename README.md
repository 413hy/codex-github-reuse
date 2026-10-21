# GitHub 复用优先开发 · Codex Skill

> 把本仓库链接和项目需求发给 AI，让它先理解项目、研究合适的 GitHub 方案，再适配并完成完整可运行 demo。

版本：1.1.0

**主要用法：直接发链接使用。** AI 读取本仓库的完整工作流后，就在你的目标项目中继续开发。
本轮使用无需先安装 Skill；也提供可选的全局安装，让 Codex 在以后多个项目中更容易复用这套工作方式。

## 给收到本仓库链接的 AI

用户要求“根据这个仓库里的 Skill 开发我的项目”时，立即按以下入口处理：

1. 阅读 [AI_START.md](AI_START.md)，明确如何读取规则、定位业务项目和开始执行。
2. 完整阅读 [主技能 SKILL.md](skills/github-reuse-first/SKILL.md)，按任务读取其中引用的检索、质量与记录文件。
3. 读取用户目标项目，理解全部需求；需求有疑问就及时提问，明确后直接完成研究、适配、完整 demo、自检与修复。

本仓库是开发方法的来源。用户要开发的业务项目才是本次交付对象。
只读了首页或摘要不等于读过主技能；具体获取方式、直接使用与已安装模式的处理见 [AI_START.md](AI_START.md)。

用户要求介绍、审核、安装或修改本 Skill 时，按对应请求处理。入口按当前用户意图选择。

## 你只需要这样发给 AI

在准备开发的项目对话或工作区中发送：

```text
https://github.com/413hy/codex-github-reuse

请按照这个仓库里的 skill 开发我的项目。
我的需求：【写下你想实现的功能、页面、交互和偏好】
```

已有项目可以继续补充相关文件或项目路径；当前对话和工作区已经明确的信息，AI 应直接沿用。
你无需再逐条解释检索顺序、如何选库、怎样适配、自检方式或默认交付标准，这些已经写在仓库中。

你也可以只说“按照这个仓库里的 Skill，继续完善当前项目”，AI 应结合已有需求和研究记录继续工作。
同一对话中的后续修改直接提出即可。

## AI 接下来应自动完成什么

| 阶段 | 具体行为 |
| --- | --- |
| 理解需求 | 阅读目标项目的说明、已有代码、依赖、设计与当前改动，梳理全部需求。对需求本身有疑问立即停下受影响工作并提问。 |
| 研究 GitHub | 优先利用项目已有能力，再围绕缺口搜索成熟方案，实际读取相关源文件、文档、示例和使用条件。 |
| 判断并适配 | 说明借鉴哪部分、解决什么需求、怎样接入当前技术栈与设计。可采用成熟依赖、局部代码、设计/逻辑思路或改写后的 prompt。 |
| 完成 demo | 覆盖全部已明确需求，准备可运行入口、关键交互、必要状态、示例数据和运行说明。 |
| 自检与修复 | 由 AI 执行与改动相关的运行、构建、交互或 prompt 检查，修复问题并报告真实结果。 |
| 交付与迭代 | 说明如何体验、借鉴了什么及验证结果；用户要求压缩包时完成实际打包，之后沿用本项目继续优化。 |

需求明确后，常规技术选择由 AI 自行处理，不增加方案审批、选库确认、逐项授权、人工验收或“是否继续”的关卡。
小范围文案修改、纯解释和根因明确的局部修复，不自动启动完整调研；用户当次明确要求调研、只读或逐步指导时，按对应范围执行。

## 核心原则：理解后适配

**本 Skill 的文件围绕用户需求组织和编写。** 参考仓库提供可借鉴的设计思路，每个采用项都应能解释实际用途和适配方式。

- 保持目标项目已有技术栈、接口、代码结构和统一视觉。
- 只引入当前需求需要的部分，控制整合与维护成本。
- 页面与交互形成一致的使用体验，避免多个模板外观直接拼接。
- Prompt 和 Skill 按实际角色、工具、输入输出及目标行为重新组织。
- 研究来源不构成固定必选仓库名单；未来项目按自身需求重新判断。
- 真实读取、真实实现、真实验证；无法核实的信息如实说明。

本包没有捆绑上游项目源码或完整第三方 Skill。研究来源、借鉴点和本地调整见 [SOURCES.md](SOURCES.md)。

## 完整 demo 与默认使用体验

首轮交付应覆盖全部已明确需求并可以实际运行体验。页面项目包含主要页面与关键交互；
CLI 提供可运行入口和代表性输入；prompt 提供可直接使用的完整内容与样例。

成品默认打开即可用，不自行添加登录注册、授权申请、激活码、验证码、审批、权限等级、功能解锁、付费墙、次数或试用限制。
用户明确要求这些产品机制时，再按实际需求实现；必要的数据和错误检查由程序自动完成。

外部服务暂不可用时，先完成标注清楚、可替换的本地模拟流程。真实集成尚未完成的部分如实说明。
项目实现、自检和修复由 AI 完成，用户反馈用于后续优化。

## 两种使用方式

| 方式 | 适用情况 | AI 如何执行 |
| --- | --- | --- |
| **发仓库链接，直接使用** | 你在当前对话中要求按本 Skill 开发 | 实际读取仓库规则并遵循，在本轮对话中直接开展任务。 |
| **安装为 Codex Skill** | 你希望以后跨项目长期使用，并明确要求安装 | 使用安装器复制技能、合并常驻入口；新会话可显式或隐式调用。 |

直接阅读属于本轮工作方式，不代表客户端已经安装或自动发现了技能。
在新的独立对话中，可以再次发仓库链接；长期安装方式则让配置保留在使用 Codex 的环境中。

### 可选：让 Codex 安装

需要长期安装时，可以在包含 `install.py` 的目录中发送：

```text
请阅读 INSTALL.zh-CN.md，将 github-reuse-first 安装为当前用户的全局 Codex Skill。
优先使用 install.py；保留已有规则，改动时自动备份并更新。
安装后报告实际写入路径，并检查技能与常驻入口的配置。
```

安装器要求 Python 3.9 或更高版本，只使用标准库。也可自行运行：

| 环境 | 全局安装命令 |
| --- | --- |
| Windows | `py -3 install.py --global` |
| Linux / macOS / WSL | `python3 install.py --global` |

仅安装到一个已有项目：`python3 install.py --project "/absolute/path/to/project"`。
Windows 将 `python3` 换成 `py -3`。没有 Python 时可按完整安装说明完成文件复制与规则合并。

全局技能位于 `~/.agents/skills/github-reuse-first/`；常驻规则使用 `CODEX_HOME`，未设置时为 `~/.codex/`。
全局 override 按 Codex 的 Unicode 空白语义判定；项目只要已有普通文件 `AGENTS.override.md`，就合并到该文件，包括原本为空的情况。
备份、更新、生效检查与移除方式见 [INSTALL.zh-CN.md](INSTALL.zh-CN.md)。

安装后开启新 Codex 会话，使用 `$github-reuse-first` 点名技能，或由适用任务匹配触发。
安装发生在运行 Codex 的机器和用户环境中，Windows 原生、WSL 与 VPS 各自使用对应配置。

## 文件导航

| 文件 | 作用 |
| --- | --- |
| [AI_START.md](AI_START.md) | 给只收到仓库链接的 AI：读取规则、定位目标项目、直接开始任务 |
| [AGENTS.md](AGENTS.md) | 本仓库工作区的任务入口，区分使用、审核、安装与维护 |
| [SKILL.md](skills/github-reuse-first/SKILL.md) | 核心开发流程与默认行为，支持直接阅读和已安装使用 |
| [AGENTS.github-reuse.md](rules/AGENTS.github-reuse.md) | 长期安装时合并到有效指令文件的常驻入口 |
| [openai.yaml](skills/github-reuse-first/agents/openai.yaml) | 技能显示名称、默认调用与隐式调用配置 |
| [search-and-selection.md](skills/github-reuse-first/references/search-and-selection.md) | 按项目缺口检索、核实与选择参考方案 |
| [quality-and-verification.md](skills/github-reuse-first/references/quality-and-verification.md) | 页面、交互、功能与 prompt 的检查方法 |
| [reuse-record.md](skills/github-reuse-first/assets/reuse-record.md) | 需求、研究、适配与验证记录模板 |
| [install.py](install.py) | 可选的全局或项目安装，保留已有规则，自动备份与更新 |
| [INSTALL.zh-CN.md](INSTALL.zh-CN.md) | 长期安装、生效检查、更新和移除说明 |
| [EXAMPLES.zh-CN.md](EXAMPLES.zh-CN.md) | 直接发链接、已有项目和常见开发任务示例 |
| [SOURCES.md](SOURCES.md) | 构建依据、研究来源和适配说明 |
| [VALIDATION.md](VALIDATION.md) | 已完成的验证与实测范围 |
| [AUDIT.zh-CN.md](AUDIT.zh-CN.md) | 原版 14 个文件审核、问题复现与本次改进记录 |
| [test_install.py](tests/test_install.py) | 安装器的隔离集成测试 |

压缩包中的 `source-history.bundle` 是可选离线源码版本记录，不参与技能安装。
GitHub 使用仓库自身的源码和提交记录即可。

## 维护与验证

修改时保持 README、AI 入口、主技能、常驻规则与示例一致。直接使用入口应能在未安装时执行；
安装后的主技能只依赖自身目录内的文件，不依赖仓库根部的说明文件。

安装器有改动时，在仓库根目录运行：

```bash
python3 -m unittest discover -s tests -v
```

文档改动核对内容、路径与命令即可；本轮实际结果见 [VALIDATION.md](VALIDATION.md)。

## 运行条件与官方依据

读取 GitHub、修改文件、代码运行和页面预览使用 AI 当前环境提供的能力。
工具不足时如实说明具体缺失，完成仍可执行的部分，不声称已经联网、运行、安装或接通服务。

本仓库规定开发方式；实际执行受当前用户要求、有效项目指令和可用工具影响，平台与第三方原有的强制权限由对应平台管理。
Codex 安装格式依据 [Skills 文档](https://learn.chatgpt.com/docs/build-skills) 与
[AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。
