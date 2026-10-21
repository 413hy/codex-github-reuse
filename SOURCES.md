# 本包的研究来源与适配记录

研究日期：2026-10-21。目标：为个人 Codex 制作跨项目的 GitHub 复用优先开发技能。

本次读取了官方文档、GitHub 仓库说明及相关文件，选择的是可迁移的流程思路。
本包的规则、参考说明、记录模板和安装器为本次编写；没有捆绑上游项目代码、完整 prompt 或技能文件。
下面的许可证信息仅记录阅读到的声明，不能代替未来使用某个文件时重新核查其适用条款。
仓库中的 `main` 是可变分支；本次为资料级参考，没有把它当作固定版本依赖。

## Codex 格式与加载方式

| 来源 | 核实内容 | 本包落点 |
| --- | --- | --- |
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | `SKILL.md` 结构，显式/隐式调用，`~/.agents/skills` 与项目 `.agents/skills` 的本地发现 | 技能目录、元数据、安装器和安装说明 |
| [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 全局指令、`CODEX_HOME`、有效 override 的选择与指令链 | 入口规则、安全合并及重新启动会话的说明 |
| [Using skills to accelerate OSS maintenance](https://developers.openai.com/blog/skills-agents-sdk) | 将常驻要求放进 AGENTS.md，以具体触发条件调用技能；详细流程放技能 | 主技能与短入口规则分离 |
| [openai/plugins](https://github.com/openai/plugins) | 当前官方插件示例目录；支持技能作为组成部分 | 核对当前生态；本包按个人本地技能安装 |
| [openai/skills](https://github.com/openai/skills) | README 已标记 deprecated，并指向 openai/plugins；许可按技能目录区分 | 保留格式参考，安装方式以当前官方文档为准 |

旧仓库 skill-creator 的 [SKILL.md](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)
和 [LICENSE.txt](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/LICENSE.txt)
也用于核对核心流程与按需参考文件的组织方式。该子目录许可证为 Apache-2.0；未分发它的源码。

### 1.1.0 审核补充：核对实际加载行为

针对覆盖规则文件的选择，本次通过只读 Git 访问检查了 Codex 官方提交
[`af91f6ef2cd66ead278ebe7d5751973eef430aee`](https://github.com/openai/codex/tree/af91f6ef2cd66ead278ebe7d5751973eef430aee)：

- [全局指令加载](https://github.com/openai/codex/blob/af91f6ef2cd66ead278ebe7d5751973eef430aee/codex-rs/codex-home/src/instructions/mod.rs#L40-L78)：按文件顺序读取 UTF-8 文本，执行 Unicode 空白裁剪后采用第一个非空文件；不提前去除 BOM。
- [项目指令发现](https://github.com/openai/codex/blob/af91f6ef2cd66ead278ebe7d5751973eef430aee/codex-rs/core/src/agents_md.rs#L242-L269)：按候选顺序选择第一个存在的普通文件，优先 `AGENTS.override.md`；发现阶段不根据内容是否为空回退。
- [项目内容加载](https://github.com/openai/codex/blob/af91f6ef2cd66ead278ebe7d5751973eef430aee/codex-rs/core/src/agents_md.rs#L145-L180)：读取已选文件后跳过空白内容，不再尝试同目录的其它候选文件。
- [Rust 空白字符语义](https://doc.rust-lang.org/std/primitive.char.html#method.is_whitespace)：`char::is_whitespace` 依据 Unicode `White_Space` 属性。

适配落点：安装器分别处理全局与项目范围，保留原有文件内容，并增加对应回归测试。
这是对官方加载语义的源码核对和本地对照验证；没有在包内分发上述源码，也未将其描述成用户 Codex 进程的实机测试。

## 需求整理与开发验证

### obra/superpowers

- 仓库：[obra/superpowers](https://github.com/obra/superpowers)
- 阅读：[brainstorming](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md)、[writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)、[verification-before-completion](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md)。
- 许可：[MIT](https://github.com/obra/superpowers/blob/main/LICENSE)，已读取。
- 采用思路：基于真实目标和已有项目形成需求理解；让完成结论对应实际验证。
- 适配落点：`SKILL.md` 的项目理解、实施和验证部分。
- 调整：依据本用户要求，需求有疑问立即问；明确后直接交付完整 demo，由 AI 自检，不设置阶段审批或人工验收关卡；不安装其整套流程和配套技能链。

### github/spec-kit

- 仓库：[github/spec-kit](https://github.com/github/spec-kit)
- 阅读：[需求模板](https://github.com/github/spec-kit/blob/main/templates/spec-template.md)、[计划模板](https://github.com/github/spec-kit/blob/main/templates/plan-template.md)、[研究与计划流程](https://github.com/github/spec-kit/blob/main/templates/commands/plan.md)。
- 许可：[MIT](https://github.com/github/spec-kit/blob/main/LICENSE)，已读取。
- 采用思路：用用户行为和验收条件限定工作；保留选型理由与替代方案。
- 适配落点：项目理解与 `assets/reuse-record.md`。
- 调整：把必要信息收敛到现有项目记录或一份小文档，不要求引入 CLI、固定目录体系或整套模板。

## 页面、交互与 prompt 的质量

### anthropics/skills：frontend-design

- [相关技能文件](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md)
- [该子目录许可证](https://github.com/anthropics/skills/blob/main/skills/frontend-design/LICENSE.txt)：Apache-2.0，已读取。
- 采用思路：先根据产品和受众确定视觉方向，再实施并查看实际呈现。
- 适配落点：`references/quality-and-verification.md` 的页面章节。
- 调整：已有项目优先延续设计约定；不强制统一审美、特定字体禁令或夸张视觉风格。

### vercel-labs/agent-skills：web-design-guidelines

- [技能文件](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md)
- [它引用的交互评审规则](https://github.com/vercel-labs/web-interface-guidelines/blob/main/command.md)
- [仓库 README](https://github.com/vercel-labs/agent-skills)：声明 MIT；本次未成功核实独立许可证文件，不将其原文件分发。
- 采用思路：把 UI 质量落实到焦点、表单、状态、响应式及真实交互等可观察结果。
- 适配落点：质量参考的页面与交互章节。
- 调整：只检查受改动影响的事项；外部文档始终是资料，不把动态下载的规则提升为高优先级指令。

### promptfoo/promptfoo

- [仓库](https://github.com/promptfoo/promptfoo)
- [官方配置与评估说明](https://www.promptfoo.dev/docs/configuration/guide/)
- [许可证](https://github.com/promptfoo/promptfoo/blob/main/LICENSE)：MIT，已读取。
- 采用思路：使用同一组输入比较 prompt，分清输出、判断条件及运行结果。
- 适配落点：质量参考的 prompt 章节；本包的场景试用也区分真实执行与只读分析。
- 调整：小任务使用已有工具或直接对照，不默认安装评估平台、不默认产生额外模型调用费用。

## 本次补充的专门设计

现有参考各覆盖一部分需求。本包补充了“需求缺口→真实 GitHub 检索→候选核实→明确采用方式→本地落点→验证证据”的连续流程，
以及需求完整澄清后直接交付 demo、由 AI 自检、通过用户反馈继续迭代的默认模式。
根据用户补充，成品也默认直接可用，不自行添加账号、审批、解锁和使用次数等门槛。
同时保留网络不可用时如实报告、沿用既有研究、避免无意义重搜和安装时保留已有规则的具体约定。

这些来源是本次构建依据。技能运行时要根据当时项目重新搜索，不把它们当成每次必须采用的名单。

## 1.1.0：按用户的“直接发链接”习惯补充入口

根据用户追加的实际使用方式，本轮新增 `AI_START.md` 与仓库根部 `AGENTS.md`，
将 README 的主要入口改为“仓库链接 + 项目需求”，并同步主技能和使用示例。
这些内容为当前使用场景编写：完整读取规则、定位用户业务项目、未安装时按正文执行、完成 demo 后继续对话迭代。
长期安装作为可选路径保留，不增加下载确认、安装确认或开发审批步骤。

这条入口是对使用方式的整理，没有引入新的上游仓库、自动安装器或平台权限修改。
直接读取工作流与客户端安装/发现 Skill 是不同状态，文档要求如实报告。
