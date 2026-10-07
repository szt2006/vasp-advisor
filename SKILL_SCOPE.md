# SKILL_SCOPE —— 什么属于这个 skill，什么不属于

> ⚠️ **本文件存在的唯一理由**：本项目**犯过一次错** ——
> 把"构建 skill 用的任务书"留在了 skill 目录里，并且**推上了公开仓库**。
> ⇒ 那条界限以前**只存在于脑子里**，现在写在文件里。
>
> **新增任何文件前，先在这里找到它的归属。找不到 ⇒ 先问，别放进来。**

---

## 一、四类东西，两个去处

| 类别 | 是什么 | 判定问题 | 该在哪 |
|---|---|---|---|
| **SKILL** | 使用者**拿来解决问题**的东西 | 「一个要用 VASP 的人，会打开它吗？」 | ✅ **skill 内** |
| **CONTRACT** | 使用者/维护者**判断"这 skill 可不可信"**所需要的东西 | 「它在证明**这个 skill 靠得住**吗？」 | ✅ **skill 内** |
| **BUILD / PROCESS** | **造**这个 skill 的过程产物 | 「它只在"建造期间"有用吗？」 | ❌ **skill 外** |
| **PRIVATE** | **站点信息 / 账号 / 远端仓库细节** | 「它描述的是**某一台机器或某一个账号**吗？」 | ❌ **skill 外** |

### 为什么 `CONTRACT` 要留在里面

这个 skill 的核心主张是「**可回溯、错了能被发现**」。
⇒ **`CHANGELOG` 的更正记录、护栏脚本、许可声明，不是"内部文档"** ——
**它们是这条主张的凭证。** 抽掉它们，主张就变成空话。

### 为什么 `BUILD` 必须出去

构建任务书（"你要建一个什么样的 skill"）描述的是**将来该有什么**，
不是**现在有什么**。它对使用者**零价值**，还会：

- 误导使用者以为它是 skill 内容；
- 把"未完成的设计意图"当成"已实现的功能"读。

### 为什么 `PRIVATE` 必须出去

- **站点信息**（集群名/账号/IP/路径）是 `AGENTS.md` 第 6 条的红线；
- **远端仓库细节**（用户名、仓库地址、发布步骤）与 skill 的**能力**无关，
  但会**标识出具体的人与账号**。

⇒ 两者都放在 skill 之外的**独立区域**。

---

## 二、逐个文件的归属（当前状态）

### ✅ SKILL —— 使用者直接拿来用的

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 面向 AI 的技能描述（触发词） |
| `USAGE.md` | 面向人的使用说明 |
| `scripts/*.py`（10 个） | 命令行工具（校验/解析/诊断/后处理/向导…） |
| `references/official/` | G 层官方权威（VASP Wiki 637 页） |
| `references/decide.md` | A 决策库 |
| `references/playbook.md` | F 实战手册（症状→处方） |
| `references/course_learned.md` | B 课程综合 |
| `references/course_notes.md` | C 速查 |
| `references/_ENTRY.md` | **症状入口**（遇到问题从哪进） |
| `references/_SYSTEMS.md` | **体系索引**（工具书第一层） |
| `references/workflow.md` | **阶段向导**（生成物） |
| `references/templates/` | 报告模板 |
| `references/raw/` | E 原始素材（讲义/答疑抽取 + 外部教程骨架） |
| `references/cases/` | 案例层 |
| `examples/` | 已校验的示例 |
| `vasp-calc/` | 编译参考 |

### ✅ CONTRACT —— 证明"这个 skill 靠得住"

| 路径 | 守什么 |
|---|---|
| `AGENTS.md` | **唯一真源**（跨 agent 入口） |
| `CLAUDE.md` / `.cursorrules` / `GEMINI.md` / `.github/copilot-instructions.md` | 指向 `AGENTS.md` 的极简指针 |
| `README.md` | 结构 + 可信度声称 |
| `CONTRIBUTING.md` | 改动硬性要求 + 提交规范 |
| `CHANGELOG.md` | **改动 + 更正记录**（最重要的凭证） |
| `NOTICE.md` + `LICENSE` | 许可分层与第三方归属 |
| `references/MAINTENANCE.md` | 知识库维护 SOP（含发布前体检流程） |
| `references/VERSIONS.md` | 版本门控用法 |
| `references/_GATES.md` | 「适用条件」怎么标 |
| `references/_WRITING_CONTRACT.md` | 写作规范（证据分级等） |
| `_audit_citations.py` | 护栏：引用可回溯 |
| `_inject_test.py` | 护栏：证明上面每条**真的会红** |
| `_doc_consistency.py` | 护栏：数字不漂 + 无泄漏 + 生成物不手改 + 路径存在 |
| `_check_coverage.py` | 护栏：精读报告真的读完了 |
| `_validate_all_suites.py` | 护栏串行总跑 |
| `_audit_gates.py` | 适用条件审计 |
| `_system_types.py` | 体系索引生成器 |
| `_publish_prep.py` | 发布前预处理（原始素材 ↔ 安全占位版） |
| `.gitignore` / `.gitattributes` | 红线与行尾 |
| `SKILL_SCOPE.md` | **本文件**（分类规矩） |

### ❌ BUILD / PROCESS —— **不在 skill 里**

| 文件名 | 是什么 | 为什么不在里面 |
|---|---|---|
| `构建VASP-skill-提示词.md` | **构建本 skill 的任务书**（写给另一个 agent） | 描述"将来该有什么" |
| `_USABILITY.md` | 7 场景可用性**自测记录**（出题人是我自己） | 是"我做过什么"，不是"skill 能给什么" |
| `_GATE_AUDIT.md` | 52 条适用条件的**裁定底稿** | 同上（结论已落进 `_GATES.md`） |
| `_scrub_siteinfo.py` | 第一版脱敏工具（**实测只清 30%，已弃用**） | 已废弃 |

### ❌ PRIVATE —— **也不在 skill 里**

| 文件名 | 是什么 | 为什么不在里面 |
|---|---|---|
| `PUBLISH-github.md` | 远端仓库地址、owner、About 文案、发布步骤 | **含账号与仓库标识** |
| `HANDOFF-*.md` | 交接文档 | **含本机目录布局与远端策略** |

---

## 三、判别口诀

| 它在说什么 | 归属 |
|---|---|
| 「**将来该有什么**」 | BUILD |
| 「**我测试时发现什么**」 | PROCESS |
| 「**某一台机器 / 某一个账号**」 | PRIVATE |
| 「**这个 skill 现在怎么用**」 | SKILL |
| 「**这个 skill 凭什么可信**」 | CONTRACT |

> ⚠️ **`_USABILITY.md` 与 `_GATE_AUDIT.md` 是边界案例，说明为什么这么判**：
> 它们**确实**有价值（可用性测试、逐条裁定），但它们是
> **「我做过什么工作」的记录**，不是**「skill 能给你什么」的内容**。
> 使用者要的是**结论**（已落进 `_ENTRY.md` / `_SYSTEMS.md` / `_GATES.md`），
> 不是**过程**。⇒ **结论留下，过程出去。**

---

## 四、红线

1. **构建/过程/隐私产物一律放在 skill 目录之外，不放在 skill 目录内。**
   ⚠️ **不要靠 `.gitignore` 兜底** ——
   那次那个任务书**根本没被忽略**，它就那样被推上去了。
   **`.gitignore` 是安全网，不是分类标准。**

2. **新增根目录文件时，必须在 §二 找到它的归属。**
   找不到 ⇒ **停下来问用户**，别自己决定。

3. **"我构建时用的" ≠ "使用者需要的"。**
   每次想往里放文件时问一遍：
   **「一个明天要用 VASP 的人，会打开它吗？不会的话，它凭什么占这个位置？」**

4. **skill 内不许出现"只有本机才成立"的东西** ——
   绝对路径、站点信息、账号、远端地址。
   ⇒ **克隆下来必须能独立跑通**
   （可复现检查见 `references/MAINTENANCE.md` §12）。
