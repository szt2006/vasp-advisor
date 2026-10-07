# vasp-advisor

**VASP 计算顾问** —— 一套「帮你写对输入、判断结果可不可信」的**顾问型**知识库
+ **零依赖**工具链（只用 Python 标准库）。

它**不替你跑计算**，也**不承诺一键出结果**。

> ### 📖 这是一个**学习者的个人学习项目**
>
> 起因是作者自己学 VASP 时踩了坑（一个 179 原子体系因为没写 `NCORE`，
> 第一次 SCF 就崩），于是把「踩过的坑 + 读过的资料 + 学到的判断」
> 整理成一套**能被核对**的笔记与工具。
>
> - **非商业、非官方**，与 VASP 官方、与任何课程机构**无隶属关系**；
> - 目的只有一个：**让下一个人少踩一次同样的坑**；
> - 所以它**欢迎被指出错误** —— `CHANGELOG` 里已经记了 57 条
>   「我原先写错了什么」，那是这个仓库最值得看的部分。
>
> ⚠️ 学习用途的项目**不等于权威**。请把它当**线索**，不是结论 ——
> 每条结论都应回到 `references/official/` 或你自己的算例上验证。

---

## 这个仓库凭什么可信

同类 VASP 资料很多。**这个仓库不一样的地方只有一个：每条结论都能被核对。**

| 机制 | 数量 |
|---|---|
| **更正记录** —— 记录"我原先写错了什么"（不是"我改了什么"） | **56 条** |
| **注入测试** —— 证明每条护栏**真的会红**，且合法输入放行 | **53 条** |
| **引用审计** —— 引用必须指向真实存在的页 / 段 / 文件 | **2400+ 条** |
| **护栏套件** —— 引用审计 / 注入测试 / 文档口径 / 覆盖性 / 环境自检 / 入口健壮性 | **6 个** |
| **官方语料** —— 采自 [VASP Wiki](https://www.vasp.at/wiki/) | **637 页** |
| **真实算例** —— 从它反推体系画像 | **98 个** |

⇒ 其中**更正记录**与**反模式**两节最值得看：它们记的是**"怎么把对的证据推成错的结论"**。

**⚠️ 也说清边界**：没有任何离线工具能证明"算得对"。
见下面的「诚实的能力边界」与 [`NOTICE.md`](NOTICE.md) 的许可分层。

---

## 30 秒上手

```bash
python scripts/doctor.py      # 1. 环境自检（新手第一步）
python scripts/wizard.py      # 2. 一问一答生成一套自洽输入 + 逐参数解释的 README
#    → 自己拼 POTCAR（受许可保护，本 skill 不生成，见下）
python scripts/validate.py <输出目录> --potcar <你的 POTCAR>
python scripts/compare.py  <输出目录>     # 跑完后：结果自不自洽
python scripts/diagnose.py <输出目录>     # 出问题了：症状 → 处方
```

**零依赖**：核心脚本只用 Python 标准库（≥3.8）。只有 `postprocess.py --plot` 需要
`matplotlib`，缺了会友好提示 + `exit 3`。

---

## ⚠️ 三件必须先说清楚的事

### 1. 本 skill **不生成、不分发 `POTCAR`**

`POTCAR` 受 VASP 许可保护，**不得再分发**（官方 wiki 的 POTCAR 页明说它自带版权声明）。
所以：

- `wizard.py` 生成 `INCAR` / `KPOINTS` / `POSCAR` + 一份 `POTCAR.README`，
  **故意不生成 `POTCAR`**；
- 本 skill **只能校验**你已经有的那个（只读头部几个数字：`TITEL`/`ENMAX`/`ZVAL`，
  **不复制、不缓存、不写出正文**）；
- 仓库里**没有任何 `POTCAR` 内容**（`.gitignore` 与 `_doc_consistency.py --scan-leaks` 双重把关）。

### 2. `OK` 不等于"算得对"

这是本 skill 存在的理由。一个真实教训：

> 有 agent 拿生成的输入看到校验器报 `OK`、据此上了集群、**白跑一趟** ——
> 因为那个 `OK` 的真实含义只是"语法与关键字拼写没问题"，而缺陷恰好在它**没检查**的那一层。

所以：

| 工具 | `OK` 的真实含义 |
|---|---|
| `validate.py` | 只是"**我检查过的那些项**没发现问题" |
| `compare.py` | 只是"文件之间**一致**"且"力平衡" |
| `diagnose.py` | 只是"**没找到我认识的那个模式**" |

**每个工具都会显式列出"本次未检查的项"。** 看到"未检查"时，
那不是"通过了"，是"没查"。

### 3. 大部分阈值**没有在真机上标定过**

构建环境里**没有 VASP**，所以：

- `compare.py` 的所有力判据（`F.` 开头）**默认报 WARN 而不是 ERROR**；
- `diagnose.py` 的 `确定` 级只给"官方明文"或"算例实证"的条目，
  其余一律降为"提示"；
- 标定方法写在 `conformance/README.md` —— **需要你（有真程序的用户）来补**。

---

## 目录结构

```
VASP-skill-V0.1/
├── AGENTS.md              # ★ 唯一真源（跨 agent 通用入口）
├── SKILL.md               # 面向 AI 的技能描述（description 塞满触发关键词）
├── USAGE.md               # 面向人的使用说明
├── README.md              # 本文件
├── CONTRIBUTING.md        # 改动硬性要求 + 提交规范
├── CHANGELOG.md           # 改动记录 + ★ 更正记录（23 条）
├── .gitattributes         # 钉死 LF（不依赖使用者本地的 git 设置）
├── .gitignore             # POTCAR / 站点信息 / 大文件 一律不入库
│
├── references/
│   ├── VERSIONS.md        # ★ 版本意识（门控表 + 官方缺陷登记簿的用法）
│   ├── MAINTENANCE.md     # ★ 维护规矩（机器细节不进，结论进）
│   ├── _WRITING_CONTRACT.md  # 写作契约（证据分级 / 引用格式 / 四要素 / 红线）
│   ├── decide.md          # ★ A 层决策库（§0–§20 + 附录）
│   ├── playbook.md        # ★ F 层实战手册（73 条症状→处方）
│   ├── course_learned.md  # B 层课程综合（含"课程 vs 官方"差异表）
│   ├── course_notes.md    # C 层速查
│   ├── official/          # G 层官方权威（★ 637 个 wiki 页面 + 620 条关键字表）
│   │   ├── _fetch_wiki.py / _discover_pages.py   # 抓取脚本
│   │   ├── _sources.tsv / _keywords.tsv / _keyword_aliases.tsv
│   │   ├── pages/         # 清洗后的正文（供 grep）
│   │   └── raw/           # 原始 wikitext（逐字保留）
│   ├── raw/               # E 层原始素材（★ 溯源用，逐字保留）
│   │   ├── L1–L4.txt      #   讲义分页抽取（491 页，每页带 PAGE 标记）
│   │   ├── D1–D4.txt      #   答疑分段抽取（257 段）
│   │   ├── learn_L1–L4.md #   精读报告（含冲突日志 + 待核对清单）
│   │   ├── seg_L1–L4.tsv  #   主题分段表（连续覆盖、无重叠无空档）
│   │   ├── extract_lectures.py / extract_qa.py
│   │   └── lvthw/         # E′ 层：★《Learn VASP The Hard Way》第二版
│   │       ├── <ID>.txt   #   132 篇逐字原文（引用形如 EX80:42）
│   │       ├── learn_G1–G8.md  # 8 份精读报告（约 8000 行）
│   │       ├── seg_G1–G8.tsv   # 分段表（132 篇逐行覆盖，机器可验）
│   │       ├── _MANIFEST.tsv / _GROUPS.tsv / SITEINFO.tsv / ASSETS.tsv
│   │       └── README.md  #   溯源 + 站点信息处理规矩 + 已知短板
│   └── cases/             # 真实生产算例登记（不含 POTCAR）
│
├── scripts/               # ★ 零依赖 CLI
│   ├── vasp_common.py     #    共用基础设施（唯一实现，不要另写一份）
│   ├── doctor.py          #    环境与脚本完整性自检
│   ├── wizard.py          #    输入向导（12 个目标）
│   ├── recommend.py       #    参数推荐（带理由 / 代价 / 出处）
│   ├── validate.py        #    输入校验（语法 / 归属 / 值域 / 跨文件）
│   ├── parse_output.py    #    数值抽取（TSV / JSON）
│   ├── compare.py         #    物理不变量与一致性
│   ├── diagnose.py        #    症状 → 诊断 → 处方
│   └── postprocess.py     #    后处理（DOS/带中心/功函数/带隙）
│
├── _audit_citations.py    # ★ 引用审计（守住"可回溯"）
├── _inject_test.py        # ★ 注入测试（证明护栏真的会红，53 条）
├── _doc_consistency.py    # ★ 文档口径一致（防数字漂移）
├── _validate_all_suites.py# ★ 串行总跑
│
├── examples/              # 开箱即用示例（每个含已校验输入 + README）
└── conformance/           # ★ 真机一致性套件（需要真 VASP）
```

---

## 知识分层与权威序

```
references/official/（G 官方权威，带来源 URL + 抓取日期）
        ↓ 官方没写
真实算例文件（references/cases/）
        ↓ 算例没覆盖
讲义正文（references/raw/L1–L4.txt）
        ↓
答疑稿（references/raw/D1–D4.txt）
        ↓
你自己推出来的
```

**冲突时一律以官方为准**，并回修上层且留一条更正记录。

### ⚠️ 但"权威"不等于"适用于你"—— 还有一层：**版本**

| 来源 | 实测版本 |
|---|---|
| 本项目抓的官方 wiki 语料 | **VASP 6.6 时代**（91 处版本门槛中 61×`6.5.0`、25×`6.6.0`） |
| `things to study/` 的 98 个真实算例 | **全部 `vasp.5.4.4`** |

⇒ 报参数前**先确认版本**。VASP 对不认识的标签常常**静默忽略**，
**不报错但也没生效**。

- 总纲：`references/VERSIONS.md`
- 版本门控表：`references/official/_versions.tsv`（420 条，可回原文）
- **官方缺陷登记簿**：`references/official/_known_issues.tsv`
  （110 条「不报错但结果错」的官方记录，带**首现/修复版本**）

**证据标记**（每条结论都带，见 `references/_WRITING_CONTRACT.md`）：

| 标记 | 含义 |
|---|---|
| `[官方]` | 官方明文，能给出 wiki 页面名 |
| `[算例]` | 真实输入/输出文件里的事实，能给出路径 |
| `[讲义]` / `[答疑]` | 课程资料原话，能给出 `L1 P28` / `D2-P14` |
| `[实测]` | **本项目构建过程中真的跑出来的结果** |
| `[经验]` | 有适用范围的经验判据（**必须**写清条件与反例） |
| `[待核对]` | 单一来源或自己推的 —— **默认状态** |

---

## 护栏：知识与工具凭什么可信

**先记住一句话**：

> **"看着在检查、其实没检查" 比 "不检查" 危险得多。**

| 护栏 | 守住什么 |
|---|---|
| `_audit_citations.py` | **可回溯**：`L1 P28`/`D2-P14`/`path:行号` 必须指向真实存在的页/段/文件 |
| `_inject_test.py` | 上面每条护栏**真的会红**，且合法输入**会放行**（31 条注入用例） |
| `_doc_consistency.py` | 文档里的数字与代码/目录里的**真值**一致 + 泄漏扫描 |
| `_check_coverage.py` | **精读报告真的读完了**：分段表连续覆盖、无重叠、无空档 |
| `CHANGELOG.md` 更正记录 | 记录"我原先写错了什么"（23 条） |

**跑全套**（**串行**，不要并行）：

```bash
python _validate_all_suites.py
```

### 这一层是怎么长出来的

构建过程中，护栏自己出过 23 次错（全部记在 `CHANGELOG.md` 的更正记录里），
其中几条**特别有代表性**：

- **一条规则在每一个算例上都误报**（`SCF.not_converged` 去错了文件 ——
  `aborting loop` 标记在 `OUTCAR` 里，不在 `OSZICAR` 里）。
  → "永远红的护栏"和"永远绿的护栏"一样坏。
- **真空层检查在 98 个算例上误报 76 次**（把面内层间距当成了真空）。
  → 78% 误报的规则等于噪声，还会让人不再相信其它规则。
- **`ISMEAR > 0` 一律提示，误报 48 次** —— 而金属用 MP 恰恰是**正确**做法。
  → 把"正确做法"报成问题，比不报更糟。
- **注入测试自己的夹具把要注入的缺陷抹掉了**（说明文字里含被检测的关键词）。
  → "注入失效"与"护栏失效"在输出上长得一模一样，
  所以运行器把这两种失败**分开报**。

---

## 诚实的能力边界

**能**：

- 讲清 VASP 四件套怎么协同、参数怎么选、结果怎么读；
- 校验输入（语法 / 关键字归属 / 值域 / **跨文件硬约束**）；
- 抽取输出数值、查跨文件一致性、查力平衡；
- 从症状出发给诊断与处方（**73 条**，见 `references/playbook.md` §1）；
- 生成**除 `POTCAR` 之外**的三个输入文件 + 一份逐参数解释的 README。

**不能**（设计边界，不是"还没做"）：

- ❌ 生成或分发 `POTCAR`；
- ❌ 替用户跑计算或提交作业；
- ❌ 保证生成的输入"一定能跑"（那要真程序，见 `conformance/`）；
- ❌ 判断"你的物理问题问得对不对"；
- ❌ 从零生成初始结构（切表面、建盒子需自备结构文件）；
- ❌ 保证解析在所有 VASP 版本上都对（输出格式会跨版本漂移）——
  因此**所有解析结果都带程序版本号**。

---

## 常见问题

**Q：为什么我的 `things to study/` 目录不在仓库里？**
A：讲义有明确版权声明、算例目录里有 `POTCAR` 与大文件。仓库只保留**抽取后的文本**
（`references/raw/*.txt`）与**登记清单**。见 `.gitignore`。

**Q：为什么不写我的集群的队列名和核数？**
A：`references/MAINTENANCE.md` §0.1「**机器细节不进，结论进**」。
把它写进通用文档，下一次换机器就会把人带沟里。给站点信息一个出口：`SITE.md`（永不入库）。

**Q：`validate.py` 报了 `INCAR.unknown_tag` 警告，但我的关键字明明是对的？**
A：官方 wiki 的 `Category:INCAR tag` **不完整**（实测至少缺 `LUSE_VDW`、`ZAB_VDW`、
`AMIX_MAG`、`BMIX_MAG`、`NKRED`、`HFSCREEN`，以及 `ICHAIN`、`IOPT`、`LCLIMB`）。
工具因此**分三档报**：`OUTCAR` 回显里有它 ⇒ INFO；`OUTCAR` 有但没有它 ⇒ ERROR；
没有 `OUTCAR` 可比 ⇒ WARN。见 `references/decide.md` §1.2。

**Q：`compare.py` 的力平衡判据说"阈值未标定"，那我怎么用？**
A：把它当**线索**而不是判据。它的价值在于"这个数**已经在你输出里**，零成本" ——
你只需要花一秒钟看它与最大单原子受力的**比值**。要把它变成硬判据，
需要你用真程序标定（`conformance/README.md`）。

**Q：我改了 skills 内容，怎么验证没改坏？**
A：见 `CONTRIBUTING.md`。核心是**串行**跑 `python _validate_all_suites.py`，
且**红了先弄明白再改，不要为了让灯变绿而放宽判据**。

---

## 引用与致谢

- **官方权威内容**采自 [VASP Wiki](https://www.vasp.at/wiki/)（**GNU FDL 1.2**），
  逐页抓取。⚠️ 来源 URL、抓取日期与 `sha256` **统一登记在**
  `references/official/_sources.tsv`（659 行）—— **不是写在各页文件头里**
  （本句早期版本说成"每个文件带"，与实际情况不符，已更正）。
- **课程讲义与答疑**来自用户提供的学习资料，版权归原机构所有。
  仓库只保留**抽取后的文本**用于内部溯源，`references/raw/README.md` 登记了
  原始文件名、页数/段数、行数与 sha256。
- 本 skill 的**结构**参照了同一作者的 `cp2k-aimd` skill。

## 许可

⚠️ **本仓库的许可是分层的，不是一个。**

| 部分 | 许可 |
|---|---|
| 原创代码 + 原创知识库（`scripts/`、`_*.py`、`references/*.md`、`examples/`、`vasp-calc/`） | **MIT**（[`LICENSE`](LICENSE)） |
| `references/official/`（VASP Wiki 采录，637 页） | **GNU FDL 1.2**（VASP Wiki 的许可） |
| `references/raw/` 的讲义与答疑抽取物 | **版权归原机构**，未获再分发授权 |
| `references/raw/lvthw/`（《Learn VASP The Hard Way》第二版） | 发布版为**行数骨架、不含正文** |

**⇒ 逐层来源、权利人、合规做法见 [`NOTICE.md`](NOTICE.md)。**
**把整个仓库当成 MIT 使用是错的。**

**没有**在本仓库里的：`POTCAR` 及其任何片段（受 VASP 许可保护，不得再分发）、
原始讲义 PDF、原始算例文件、任何**站点信息**。
