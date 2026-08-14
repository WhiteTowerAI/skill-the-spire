# Skill the Spire

[English](#english) | [简体中文](#简体中文)

## English

Skill the Spire is a free Codex plugin that turns a plain-language idea into a Slay the
Spire 2 mod: it helps settle the design, writes the implementation, builds the project, and
reports the verification that actually ran.

Version `0.1.0` is the first public release. Generated mods target Slay the Spire 2
`0.107.1` and the RitsuLib `0.5.11` authoring/API baseline.

### Requirements

- Slay the Spire 2 stable `0.107.1`, installed through Steam.
- RitsuLib `>= 0.5.11` with its `0.107.1` Compat variant. The official Workshop item is
  `3747602295`.
- .NET SDK 9 and Python 3.
- Codex with plugin support, or another agent that supports portable Agent Skills.

Generated projects resolve the checked local game and RitsuLib assemblies. They do not use a
framework `PackageReference` and do not depend on BaseLib.

### Install The Codex Plugin

```text
codex plugin marketplace add https://github.com/WhiteTowerAI/skill-the-spire
codex plugin add skill-the-spire@skill-the-spire
```

Start a new Codex task after installation so the `modmaker` and `sts2api` skills are loaded.

### Install Portable Skills

```text
npx skills add WhiteTowerAI/skill-the-spire
```

The portable distribution contains the same two skills and bundled Python tools as the Codex
plugin.

### Quick Start

Invoke `$modmaker`, then describe the mod in ordinary language:

> Create a relic that gives 5 Block at the start of every third turn.

The skill keeps complete narrow requests on a zero-question path. It asks only when a decision
would materially change the behavior, scope, presentation, or verification.

### Examples

- "Make a 1-cost Attack that deals 9 damage and upgrades to 13."
- "Design and build a playable character around storing cards in a second hand."
- "Change an existing relic through the maintained vanilla-override routes."
- "Create an event with bilingual choices and a structured in-game self-test."

### Workflow

```text
idea -> DESIGN.md -> SPEC.md -> capability preflight -> scaffold and author
     -> Build -> Tier 1 -> Tier 2 / SelfTest -> headed review when needed
     -> direct report from actual results
```

`DESIGN.md` preserves intent and accepted scope. `SPEC.md` is the concrete work order. The
preflight checks shipped-route existence and raw model-hook reachability. Build owns compilation
and static packaging. The real game owns runtime behavior, and a person owns visual or subjective
judgment.

### Supported Scope

Skill the Spire supports new Cards, Relics, Potions, Powers, Keywords, Enchantments, Orbs,
Monsters, Encounters, Events, Characters, Acts, Ancients, Rewards, Card Piles, Afflictions,
Modifiers, Global Effects, Rest Site actions, and bounded Runtime UI. It also covers maintained
computed values, targeting, state, resources, presentation, model hooks, ordinary effect
primitives, and selected vanilla Card, visual, Ancient, availability, and non-Card overrides.

The exact support and limitation inventory is in
[`games/sts2/tests/content-capability-graph.md`](games/sts2/tests/content-capability-graph.md).

### What Verification Means

- **Build:** compilation, manifests, resources, localization, and packaging passed under the
  pinned local profile.
- **Tier 1:** the exact load marker and framework/host/Compat identity were observed with no fresh
  error block.
- **Tier 2:** `SelfTest.cs` drove the behavior in the real game, asserted structured post-state,
  and emitted `selftest done`.
- **Headed review:** a person checked the selected image, UI, input, animation, audio, or
  subjective result.

Source tests and payload validation are not gameplay proof. Reports state failed and unrun checks
directly; `played`, `fired`, and `used` logs are diagnostics only.

### Known Boundaries

- The target is pinned to STS2 `0.107.1` and the RitsuLib `0.5.11` API baseline.
- Many supported shapes still require their own generated-mod Build and real-host verification.
- Multiplayer, Settings, Telemetry, Update Check, broad custom scene/material/audio systems, and
  one-click Workshop publishing are not general authoring surfaces in `0.1.0`.
- Generated code does not invent prompt-derived Harmony, reflection, Publicizer, or IL. A missing
  maintained public/fixed route blocks authoring instead of receiving a silent approximation.
- Included STS2 art samples remain Mega Crit property and are reference-only; see their bundled
  `ATTRIBUTION.md`.

### Contributing

Bug reports and focused pull requests are welcome at
[`WhiteTowerAI/skill-the-spire`](https://github.com/WhiteTowerAI/skill-the-spire). Keep changes in
authoritative source under `games/sts2/`, preserve unrelated work, and regenerate both payloads
through `publish.sh`.

### License

Skill the Spire source is available under the [MIT License](LICENSE). Third-party game art and
other attributed material retain their original ownership and terms.

## 简体中文

Skill the Spire 是一个免费的 Codex 插件。用户只需用自然语言描述创意，它就能协助确定
设计、编写《杀戮尖塔 2》Mod、构建项目，并如实报告实际完成的验证。

`0.1.0` 是第一个正式公开版本。生成的 Mod 面向《杀戮尖塔 2》`0.107.1`，并使用
RitsuLib `0.5.11` 的创作/API 基线。

### 环境要求

- 通过 Steam 安装的《杀戮尖塔 2》稳定版 `0.107.1`。
- 带 `0.107.1` Compat 变体的 RitsuLib `>= 0.5.11`。官方创意工坊条目为
  `3747602295`。
- .NET SDK 9 和 Python 3。
- 支持插件的 Codex，或支持 portable Agent Skills 的其他 Agent。

生成项目会读取经过检查的本地游戏与 RitsuLib 程序集，不使用框架
`PackageReference`，也不依赖 BaseLib。

### 安装 Codex 插件

```text
codex plugin marketplace add https://github.com/WhiteTowerAI/skill-the-spire
codex plugin add skill-the-spire@skill-the-spire
```

安装后请新建 Codex 任务，使 `modmaker` 和 `sts2api` 两个 skill 被加载。

### 安装 Portable Skills

```text
npx skills add WhiteTowerAI/skill-the-spire
```

Portable 版本包含与 Codex 插件相同的两个 skill 和 Python 工具。

### 快速开始

调用 `$modmaker`，然后直接描述 Mod：

> 制作一个遗物：每三个回合开始时获得 5 点格挡。

如果需求已经完整且范围明确，skill 不会额外提问；只有会实际改变行为、范围、表现或
验证方式的决定才需要确认。

### 示例

- “制作一张 1 费攻击牌，造成 9 点伤害，升级后造成 13 点伤害。”
- “围绕第二手牌区设计并制作一名可玩角色。”
- “通过维护中的原版覆盖路径修改一个现有遗物。”
- “制作一个带中英文本选项和结构化真机自测的事件。”

### 工作流程

```text
创意 -> DESIGN.md -> SPEC.md -> 能力预检 -> 脚手架与实现
     -> Build -> Tier 1 -> Tier 2 / SelfTest -> 必要时人工有界面检查
     -> 按实际结果直接报告
```

`DESIGN.md` 保存意图和已接受范围；`SPEC.md` 是具体实施工单。预检只检查已发布路径和
原始模型 hook 的可达性。Build 负责编译和静态打包；真实游戏负责运行时行为；画面、
交互和主观体验由人工检查。

### 支持范围

Skill the Spire 支持新卡牌、遗物、药水、能力、关键词、附魔、充能球、怪物、遭遇、
事件、角色、章节、远古事件、奖励、卡牌堆、词缀、修正项、全局效果、休息点操作和有界
运行时 UI。它还维护计算值、目标选择、状态、资源、表现、模型 hook、普通效果原语，
以及部分原版卡牌、视觉、远古事件、可用性和非卡牌覆盖路径。

精确的支持项与限制见
[`games/sts2/tests/content-capability-graph.md`](games/sts2/tests/content-capability-graph.md)。

### 验证含义

- **Build：** 在固定本地配置下通过编译、manifest、资源、本地化和打包检查。
- **Tier 1：** 在真实游戏中观察到精确加载标记、框架/宿主/Compat 身份，且没有新的
  错误块。
- **Tier 2：** `SelfTest.cs` 在真实游戏中驱动行为、断言结构化结果，并输出
  `selftest done`。
- **有界面人工检查：** 人工观察选定的图片、UI、输入、动画、音频或主观结果。

源码测试和 payload 验证不是玩法证明。报告会直接写明失败和未运行项；`played`、
`fired`、`used` 日志只能用于诊断。

### 已知边界

- 目标固定为 STS2 `0.107.1` 和 RitsuLib `0.5.11` API 基线。
- 许多已支持形态仍需要对应生成 Mod 的 Build 和真机验证。
- `0.1.0` 不把多人、设置、遥测、更新检查、广义自定义场景/材质/音频系统或一键发布到
  创意工坊作为通用创作能力。
- 生成代码不会临时发明 Harmony、反射、Publicizer 或 IL 路径。缺少维护中的公开/固定
  路径时会停止创作，而不是静默近似。
- 随附的 STS2 美术样本仅作参考，版权仍归 Mega Crit；详见同目录
  `ATTRIBUTION.md`。

### 参与贡献

欢迎在 [`WhiteTowerAI/skill-the-spire`](https://github.com/WhiteTowerAI/skill-the-spire)
提交错误报告和范围明确的 Pull Request。请修改 `games/sts2/` 下的权威源码，保留无关
工作，并始终通过 `publish.sh` 重新生成两种 payload。

### 许可证

Skill the Spire 源码采用 [MIT License](LICENSE)。第三方游戏美术和其他署名材料继续
遵循其原有权属与条款。
