# Skill the Spire

[English](#english) | [简体中文](#简体中文)

## English

**Describe a Slay the Spire 2 mod in your own words, and get a mod you can play.**

You don't need to know how to code. Tell Claude Code or Codex something like "a relic that
gives 5 Block every third turn" and Skill the Spire designs it, writes it, builds it, tests it
inside the real game, and tells you whether it worked.

<!-- TODO: replace with the demo video (YouTube/Bilibili thumbnail link or an embedded MP4). -->
> 🎬 **Demo video: coming soon**

### How It Works

1. **Say what you want.** One sentence is enough. Write in English or Chinese.
2. **Answer a few questions.** It only asks when your answer really changes the mod, for
   example "should this card be an Attack or a Skill?". If your idea is already clear, it
   asks nothing.
3. **Wait.** It writes the mod, builds it, and opens the game by itself to test it in a real
   fight.
4. **Play.** The mod is already in your game's `mods` folder. Start the game and try it.

At the end you get a short, honest report: what was checked, what passed, and anything it
couldn't check and you should look at yourself.

### What You Can Make

| You want... | Examples |
|---|---|
| **Cards** | Attacks, Skills, Powers, upgrades, cards that cost Stars, cards whose damage grows |
| **Relics and potions** | "Every 3 turns, gain 5 Block", "Heal 10 HP and draw 2 cards" |
| **Buffs, debuffs, and keywords** | New statuses like Poison or Strength, new card keywords |
| **Enchantments, Afflictions, Orbs** | Effects stuck on cards, new Orbs that fire every turn |
| **A whole new character** | Starting deck, relic, HP, card colors, portrait, energy orb, even a second resource |
| **Monsters and fights** | New enemies with their own move patterns, new encounters |
| **Events and Ancients** | Map events with choices and rewards, new Ancients with dialogue |
| **New Acts** | A full new chapter with its own map, fights, and boss |
| **Run-wide rules** | Custom run modifiers, new Rest Site options, new reward types |
| **Changes to the base game** | Rebalance an existing card or relic, change its text or art, move cards between pools |
| **Small UI additions** | Top-bar buttons, pop-up notices, hotkeys, card glow, small badges on relics |

All player-facing text is written in **both English and Chinese**, in the same style as the
base game's own text.

<!-- TODO: add 2–3 screenshots of generated content (a card, a relic, a character). -->
> 🖼️ **Screenshots: coming soon**

### Example Ideas

Copy one of these to try it out:

- "Make a 1-cost Attack that deals 9 damage. Upgraded, it deals 13."
- "Make a relic: at the start of every third turn, gain 5 Block."
- "Make a potion that gives 3 Strength but loses 1 HP each turn for the rest of the fight."
- "Design a playable character who stores cards in a second hand."
- "Make an event where the player can trade 50 Gold for a random rare card."
- "Make Strike deal 7 damage instead of 6."

<!-- TODO: link each example to a short clip or a finished example mod. -->

### Before You Start

You need these once:

1. **Slay the Spire 2** on Steam, version **0.107.1**.
2. **RitsuLib**, the mod framework every generated mod uses. The easiest way is to
   [subscribe on the Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3747602295).
3. **[.NET SDK 9](https://dotnet.microsoft.com/download/dotnet/9.0)** and
   **[Python 3](https://www.python.org/downloads/)**. These are free tools that build the mod.
   Just install them; you won't need to open them.
4. **[Claude Code](https://claude.com/claude-code)** or **Codex**. This is the AI that does
   the work.

Windows is the main tested platform.

### Install

**Claude Code:** run these two lines in a terminal, then start a new Claude Code session.

```bash
claude plugin marketplace add WhiteTowerAI/skill-the-spire
```

```bash
claude plugin install skill-the-spire@skill-the-spire
```

**Codex:** run these two lines in a terminal, then start a new Codex task.

```bash
codex plugin marketplace add https://github.com/WhiteTowerAI/skill-the-spire
```

```bash
codex plugin add skill-the-spire@skill-the-spire
```

**Other agents that support Agent Skills:**

```bash
npx skills add WhiteTowerAI/skill-the-spire
```

### Make Your First Mod

Type `/modmaker` in Claude Code (or `$modmaker` in Codex), then describe your idea:

> /modmaker Make a relic: at the start of every third turn, gain 5 Block.

While it works it tells you what is happening in plain words. Some things to know:

- **The game opens and closes by itself** a few times while it tests. Let it run, and don't
  play during that time.
- **Your mod project lives in its own folder**, apart from the game. Only the finished mod is
  copied into the game's `mods` folder. Tell it if you want the project somewhere specific.
- **Want to change something?** Just say so in the same session: "make it 6 Block instead",
  "also give it a Chinese name", and so on. It updates the mod and checks it again.

### Art

By default, new cards, relics, and characters get **placeholder art**, which is the fastest way
to a playable mod. You can add real art at the start or later:

- **Use your own images.** Give it the files and it resizes and places them for you.
- **Use the AI's image tool**, if your agent has one (Codex does).
- **Use your own image service** (OpenAI, Gemini, OpenRouter, or a local tool such as
  ComfyUI). This spends your own credit, so it always tells you how many images it will make
  and asks before it starts.

<!-- TODO: add a before/after picture: placeholder art vs. generated art. -->

### What It Can't Do Yet

- Multiplayer content.
- Mod settings menus, achievements or unlock progression, and telemetry.
- Complex animation (Spine), custom shaders, or brand-new scenes and music systems.
- Publishing to the Steam Workshop in one click. You can still share the finished mod folder
  by hand. Players also need RitsuLib.
- Game versions other than **0.107.1**. If Steam updates the game, a newer Skill the Spire
  release may be needed.

If a request needs something the game doesn't allow mods to do safely, it tells you plainly
instead of faking it.

### FAQ

**Do I need to know programming?** No. You describe the idea; the AI writes and checks the code.

**Is it free?** Skill the Spire is free and open source. You need your own Claude Code or Codex
access, and an image service only if you choose one.

**How do I know the mod really works?** It doesn't just build the mod. It opens the real game,
runs your content in an automatic test, and reports only what actually passed. Things a program
can't judge, such as whether the art looks good, are left for you to check, and it says so.

**Can I edit the mod myself afterwards?** Yes. It's a normal C# project on your computer.

### For Developers

Contributor rules live in [`AGENTS.md`](AGENTS.md). The exact list of supported features and
known limits is in
[`games/sts2/tests/content-capability-graph.md`](games/sts2/tests/content-capability-graph.md).
Bug reports and focused pull requests are welcome at
[`WhiteTowerAI/skill-the-spire`](https://github.com/WhiteTowerAI/skill-the-spire).

Current version `0.2.0` targets Slay the Spire 2 `0.107.1` and RitsuLib `0.6.7`.

### License

[MIT License](LICENSE). Slay the Spire 2 art samples included for reference belong to Mega Crit;
see their bundled `ATTRIBUTION.md`.

## 简体中文

**用自己的话描述一个《杀戮尖塔 2》Mod，就能得到一个能玩的 Mod。**

不需要会编程。对 Claude Code 或 Codex 说一句"做一个遗物：每三回合获得 5 点格挡"，Skill the
Spire 会帮你设计、编写、构建，在真实游戏里测试，再告诉你结果。

<!-- TODO: 替换为演示视频（B 站 / YouTube 封面链接或内嵌 MP4）。 -->
> 🎬 **演示视频：待补充**

### 怎么用

1. **说出你的想法。** 一句话就够，中文英文都行。
2. **回答几个问题。** 只有答案真的会影响 Mod 时它才会问，比如"这张牌是攻击牌还是技能牌？"。
   如果你的描述已经很清楚，它一个问题都不问。
3. **等它做完。** 它会写代码、构建 Mod，并自动打开游戏，在真实战斗里测试。
4. **开玩。** Mod 已经放进游戏的 `mods` 文件夹，启动游戏就能玩。

最后你会收到一份简短、如实的报告：检查了什么、哪些通过了，以及哪些它没法检查、需要你自己看一眼。

### 能做什么

| 你想做…… | 例子 |
|---|---|
| **卡牌** | 攻击、技能、能力牌，升级效果，消耗辉星的牌，伤害会成长的牌 |
| **遗物和药水** | "每 3 回合获得 5 点格挡"、"回复 10 点生命并抽 2 张牌" |
| **增益、减益和关键词** | 类似中毒、力量的新状态，新的卡牌关键词 |
| **附魔、词缀、充能球** | 附着在卡牌上的效果，每回合触发的新充能球 |
| **全新角色** | 初始卡组、初始遗物、生命值、卡牌配色、立绘、能量球，甚至第二种资源 |
| **怪物和战斗** | 有自己行动模式的新敌人，新的遭遇战 |
| **事件和远古** | 带选项和奖励的地图事件，带对话的新远古 |
| **新章节** | 一整个新章节，有自己的地图、战斗和 Boss |
| **整局规则** | 自定义修正项、新的休息点选项、新的奖励类型 |
| **修改原版内容** | 调整现有卡牌或遗物的数值、文字或美术，在卡池之间移动卡牌 |
| **小型界面** | 顶栏按钮、弹出提示、快捷键、卡牌发光、遗物角标 |

所有玩家能看到的文字都会**同时生成中文和英文**，风格和原版游戏一致。

<!-- TODO: 放 2–3 张生成内容的截图（一张卡牌、一个遗物、一个角色）。 -->
> 🖼️ **截图：待补充**

### 试试这些想法

直接复制一条试试：

- "做一张 1 费攻击牌，造成 9 点伤害，升级后造成 13 点。"
- "做一个遗物：每三个回合开始时获得 5 点格挡。"
- "做一瓶药水：获得 3 点力量，但本场战斗每回合失去 1 点生命。"
- "设计一个可玩角色，能把牌存进第二手牌区。"
- "做一个事件：玩家可以花 50 金币换一张随机稀有牌。"
- "把打击的伤害从 6 改成 7。"

<!-- TODO: 给每个例子链接一段短视频或一个做好的示例 Mod。 -->

### 准备工作

以下只需准备一次：

1. Steam 上的**《杀戮尖塔 2》**，版本 **0.107.1**。
2. **RitsuLib**，所有生成的 Mod 都依赖这个 Mod 框架。最简单的方法是
   [在创意工坊订阅](https://steamcommunity.com/sharedfiles/filedetails/?id=3747602295)。
3. **[.NET SDK 9](https://dotnet.microsoft.com/download/dotnet/9.0)** 和
   **[Python 3](https://www.python.org/downloads/)**。这两个是构建 Mod 用的免费工具，装好即可，不用打开。
4. **[Claude Code](https://claude.com/claude-code)** 或 **Codex**，也就是实际干活的 AI。

目前主要在 Windows 上测试。

### 安装

**Claude Code：** 在终端里运行下面两行，然后新开一个 Claude Code 会话。

```bash
claude plugin marketplace add WhiteTowerAI/skill-the-spire
```

```bash
claude plugin install skill-the-spire@skill-the-spire
```

**Codex：** 在终端里运行下面两行，然后新建一个 Codex 任务。

```bash
codex plugin marketplace add https://github.com/WhiteTowerAI/skill-the-spire
```

```bash
codex plugin add skill-the-spire@skill-the-spire
```

**其他支持 Agent Skills 的 AI 工具：**

```bash
npx skills add WhiteTowerAI/skill-the-spire
```

### 做你的第一个 Mod

在 Claude Code 里输入 `/modmaker`（Codex 里是 `$modmaker`），然后描述你的想法：

> /modmaker 做一个遗物：每三个回合开始时获得 5 点格挡。

它会一边做一边用大白话告诉你进度。需要知道的几件事：

- **游戏会自己打开、关闭几次**，这是在测试。让它跑完，这段时间别去玩。
- **Mod 项目放在单独的文件夹里**，和游戏分开。只有做好的 Mod 会被复制到游戏的 `mods` 文件夹。想放在指定位置的话，告诉它就行。
- **想改？直接说。** 在同一个会话里说"改成 6 点格挡"、"名字再起得霸气点"之类的就行，它会修改并重新检查。

### 美术

默认情况下，新卡牌、遗物和角色使用**占位图**，这是最快能玩上的方式。你可以一开始就加真美术，也可以以后再加：

- **用你自己的图。** 把图片文件给它，它会帮你裁剪、缩放并放到正确位置。
- **用 AI 自带的画图工具**，如果你的 AI 工具有的话（Codex 有）。
- **用你自己的画图服务**（OpenAI、Gemini、OpenRouter，或 ComfyUI 等本地工具）。这会花你自己的额度，所以它开始前一定会告诉你要生成几张图，并征得你同意。

<!-- TODO: 放一张对比图：占位图 vs 生成的美术。 -->

### 暂时做不到的

- 多人联机内容。
- Mod 设置菜单、成就或解锁进度、数据统计。
- 复杂动画（Spine）、自定义着色器，或全新的场景和音乐系统。
- 一键发布到创意工坊。你仍然可以手动分享做好的 Mod 文件夹，对方也需要安装 RitsuLib。
- **0.107.1** 以外的游戏版本。如果 Steam 更新了游戏，可能需要等 Skill the Spire 出新版本。

如果某个需求需要游戏不允许 Mod 安全做到的事，它会直接告诉你，而不是糊弄过去。

### 常见问题

**需要会编程吗？** 不需要。你负责描述想法，AI 负责写代码和检查。

**收费吗？** Skill the Spire 免费开源。你需要自己的 Claude Code 或 Codex，选择画图服务时才会产生画图费用。

**怎么知道 Mod 真的能用？** 它不只是把 Mod 编译出来，还会打开真实游戏、自动测试你的内容，并且只报告真正通过的部分。美术好不好看这类程序判断不了的事，会留给你看，并明确告诉你。

**做完之后我能自己改吗？** 可以。它就是你电脑上的一个普通 C# 项目。

### 开发者

贡献规则见 [`AGENTS.md`](AGENTS.md)。完整的支持功能和已知限制见
[`games/sts2/tests/content-capability-graph.md`](games/sts2/tests/content-capability-graph.md)。
欢迎在 [`WhiteTowerAI/skill-the-spire`](https://github.com/WhiteTowerAI/skill-the-spire)
提交问题和范围明确的 Pull Request。

当前版本 `0.2.0` 面向《杀戮尖塔 2》`0.107.1` 和 RitsuLib `0.6.7`。

### 许可证

[MIT License](LICENSE)。随附的《杀戮尖塔 2》美术参考样本版权归 Mega Crit，详见同目录的 `ATTRIBUTION.md`。
