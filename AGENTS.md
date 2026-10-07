# AGENTS.md — VASP 计算顾问（跨 agent 通用入口）

> 本文件是**唯一真源**。任何 AI 编码助手（Claude Code / Cursor / Cline /
> CodeBuddy / Gemini CLI / Copilot / Aider / Zed …）读到这里，就掌握了使用
> 本 skill 所需的全部信息。
>
> 其它入口文件（`CLAUDE.md` / `.cursorrules` / `GEMINI.md` /
> `.github/copilot-instructions.md`）都只是指向本文件的**极简指针**，
> 不重复内容，避免多份说明互相漂移。

---

## 1. 这是什么

一套**VASP 计算顾问**的知识库 + 工具链。它**不替用户跑计算**，而是：

- 在**每个阶段**告诉用户该考虑什么、有哪些取舍、坑在哪、该盯哪些指标；
- 提供**可调用的命令行工具**（参数推荐 / 生成输入 / 校验 / 解析 / 诊断 / 后处理）；
- 按 **11 个主线阶段 + 1 个续算分支**陪跑项目。

**设计原则：顾问，而非自动驾驶。**
工具都是"给用户、由用户决定执行"，没有一个接口是"读完需求自动跑完流水线"。

> ⚠️ **本 skill 的核心价值主张是「可回溯」与「错了能被发现」**，
> 不是"内容多"。所以你会看到大量"这条我没核实""这项本次未检查"的标注 ——
> **那是特性，不是缺陷。**

## 2. 零依赖，直接可用

核心脚本**只用 Python 标准库**（≥3.8），无需 pip 安装任何东西：

```bash
python scripts/doctor.py        # 环境自检（新手第一步跑它）
python scripts/wizard.py        # 交互式向导：一问一答生成一套自洽输入
python scripts/validate.py  <算例目录>   # 校验输入（语法/归属/值域/跨文件）
python scripts/parse_output.py <算例目录> # 抽取数值（TSV/JSON，供脚本接）
python scripts/compare.py   <算例目录>   # 物理不变量与一致性（判"自洽"）
python scripts/diagnose.py  <算例目录>   # 症状 → 诊断 → 处方
python scripts/guide.py     scan <目录>  # **我在哪个阶段？下一步做什么？**
python scripts/recommend.py --goal <目标> --elements "<元素>"   # 参数推荐
```

仅 `scripts/postprocess.py --plot`（出图）需要 `matplotlib`；缺了会友好提示 + `exit 3`，**数值照样打出来**。

**第一步永远先跑自检**：

```bash
python scripts/doctor.py
```

看到 `结论：核心功能可用 ✓` 即可开始。

## 3. 新手从这里开始

```bash
python scripts/doctor.py                    # 1. 环境自检
python scripts/wizard.py                    # 2. 生成一套输入（含 README 解释每个参数）
python scripts/validate.py <输出目录> --potcar <你本地的 POTCAR>
```

**示例**在 `examples/`，每个都有已校验的输入 + README。

## 4. 按需求取用

| 用户想做什么 | 用什么 |
|---|---|
| 不知道环境行不行 | `python scripts/doctor.py` |
| 想生成输入但不想记参数 | `python scripts/wizard.py` |
| 生成了输入要检查 | `python scripts/validate.py <目录>` |
| 跑完要看数值 | `python scripts/parse_output.py <目录>` |
| **怀疑"算错了"但语法没问题** | `python scripts/compare.py <目录>` —— 查能量自洽、原子数一致、`ENCUT` 一致、**力平衡**（孤立体系应为 0） |
| 跑出问题了要诊断 | `python scripts/diagnose.py <目录>` |
| 不知道参数怎么选 | `python scripts/recommend.py` |
| 要出图/算物性 | `python scripts/postprocess.py <子命令> …` |

### ⚠️ 关于"检验算得对不对"，必须说清楚的事

**没有任何离线工具能证明"算得对"。** 分工是：

| 工具 | 回答的问题 | `OK` 的真实含义 |
|---|---|---|
| `validate.py` | 输入写对了吗 | 只是"**我检查过的那些项**没发现问题" |
| `compare.py` | 结果自洽吗 | 只是"能量/原子数/参数在文件之间**一致**"、「力平衡」 |
| `diagnose.py` | 是哪一类问题 | 只是"**没找到我认识的那个模式**" |

**"语法全对但程序不接受"原理上要真程序才能抓** —— 见 `conformance/README.md`。
**"程序不报错但结果不对"**多数只有真程序 + 你的物理判断能抓。

## 5. 知识分层（需要深入时读）

按**权威性从高到低**：

| 层 | 文件 | 内容 |
|---|---|---|
| **G 官方权威层** | `references/official/` | 逐页采自 `vasp.at/wiki`（637 个页面）；来源 URL / 抓取日期 / `sha256` 统一登记在 `_sources.tsv`（659 行），**不写在各页文件头**；另有自动生成的**关键字归属表** `_keywords.tsv`（620 条） |
| **V 版本层** | `references/VERSIONS.md` + `official/_versions.tsv` + `official/_known_issues.tsv` | **版本门控**（这个标签你那个版本支持吗）与**官方缺陷登记簿**（110 条「不报错但结果错」的官方记录，带首现/修复版本）。⚠️ 官方语料是 **6.6 时代**，真实算例全是 **5.4.4** |
| **模板层** | `references/templates/` | **报告模板**（`report.md`）：方法学清单 + 「本次没检查的项」+ 结论置信度。⚠️ **只给结构、不给数值** —— 数值依体系/版本/集群而定，填错了比不填更糟 |
| **症状入口** | `references/_ENTRY.md` | **遇到问题时的第 0 步**：先分清三类 —— **A 没跑起来** / **B 跑完但结果不对** / **C 慢**。⚠️ 三类的**处方是冲突的**（对 C 类对的调法，对 A 类可能火上浇油）⇒ **没分类就调参等于赌博** |
| **阶段向导** | `references/workflow.md` + `scripts/guide.py` | **11 个主线阶段 + 1 个续算分支**：每阶段「该做 / 决策点 / 常见坑 / 该跑的命令 / 该读的条目」。`guide.py scan <目录>` 会推断「卡在哪、下一步做什么」（启发式，**会打印依据**）。⚠️ `workflow.md` 是**生成物**，由 `--export` 重生成 |
| **体系索引** | `references/_SYSTEMS.md` + `_system_types.py` | **工具书的第一层索引**：先问「你算的是哪类体系」+**规模轴**。画像由 98 个真实算例反推，可 `--check` 复核。⚠️ 这一层是为了解决「知识都在库里但查不到」 |
| **条件层** | `references/_GATES.md` + `_audit_gates.py` | **「适用条件」怎么标**：规定 vs 描述、后果四档（崩/静默错/慢贵/无）、**规模敏感标签清单**。⚠️ 本项目曾因缺这一层，让一条依赖规模的「无视即可」把使用者引向了反方向 |
| **A 决策库** | `references/decide.md` | 「遇到 X 该选 Y，因为 Z，代价是 W」（§0–§20 + 附录） |
| **F 实战手册** | `references/playbook.md` | 症状→处方 73 条、工作流 17 个、数值速查 14 张表、报错速查 28 行 |
| **B 课程综合** | `references/course_learned.md` | 讲义内化（主题式导航）+ **课程口径 vs 官方口径差异表** |
| **C 速查** | `references/course_notes.md` | 实战精华（供 grep 直击） |
| **E 原始素材** | `references/raw/` | 讲义分页抽取 `L1–L4.txt`、答疑 `D1–D4.txt`、精读报告 `learn_L*.md`、分段表 `seg_L*.tsv`（**原文只读，勿改**） |
| **E′ 外部教程** | `references/raw/lvthw/` | **《Learn VASP The Hard Way》第二版**（132 篇 / **22 881 行**）：`<ID>.txt` + `learn_G1–G8.md` 精读报告 + `seg_G*.tsv` 分段表。⚠️ **发布版是"行数骨架"**（每行 `(content withheld)`）—— GitHub 上那份**不含正文**；原文**只存在本仓库之外**（维护者自行保管，用 `_publish_prep.py --restore --src <目录>` 指回）——**既不在仓库里，也不在仓库内的任何忽略目录里**（CR-059）。⚠️ 因此**骨架是这一层的全部内容**；正文请回原站。见 `MAINTENANCE.md` §12 |
| **案例层** | `references/cases/` | 真实生产算例登记（**不含 `POTCAR`**） |

### 怎么引用 LVTHW（E′）那一层

写法 **`<篇 ID>:<行号>`**，例如 `EX80:42`、`M_02:68`、`EX01_V3:30`。
篇 ID = 原文件名主干**大写化**（`ex80.md` → `EX80`）。

- **行号口径 = 物理行数**（`\n` 的个数，等价于 `wc -l`），
  **不是** `text.split("\n")` 的长度（那会多 1）。见 `CHANGELOG.md` CR-025。
- `_audit_citations.py` **会核对这些引用**（篇必须存在、行号必须在范围内）。
- 覆盖性由 `_check_coverage.py` 保证（每篇行区间连续、无重叠、无空档）。

⚠️ **该层的已知短板**：大量关键内容（报错原文、`INCAR` 全文、脚本源码）
**只存在于截图里**，文本层取不到。引用这些时必须标注
"原文为截图，文本层未核实"。清单见 `references/raw/lvthw/README.md` §8。

⚠️ **该层含站点信息**（它是网站导出，`SITEINFO.tsv` 记着 **673 条**）。
**本地原文逐字保留**（供引用核对），但**发布版是行数骨架、正文为空** ——
因为站点信息**不能进仓库**（第 6/8 条）。**消费层更不得复制** ——
一律写 `<你的集群>` / `<账号>@<主机>` / `~/…`。
⚠️ **不要试图用正则脱敏**（实测只清掉约 30%，会给出 false 的信心）——
用 `python _publish_prep.py --make --out <目录>`。见 `MAINTENANCE.md` §12。

**冲突裁决原则：与 `references/official/` 冲突时，一律以官方为准**，
并回修 A–F，在改动处留一条更正记录（见 `CHANGELOG.md`）。

**写作规范**见 `references/_WRITING_CONTRACT.md`（证据分级 `[官方]`/`[算例]`/
`[讲义]`/`[答疑]`/`[实测]`/`[经验]`/`[待核对]`、引用格式、四要素、红线）。

## 6. 硬性约束（做任何改动前必读）

1. **工作流是「本地改好 → 校验跑绿 → 再交付」**，不要绕过校验。
2. **改完必须串行重跑全部护栏**（**不要并行**）：
   ```bash
   python _audit_citations.py        # 引用审计（引用必须指向真实页/段/文件）
   python _inject_test.py            # 注入测试（证明护栏真的会红）
   python _doc_consistency.py        # 文档口径一致（数字不许漂移）
   python _validate_all_suites.py    # 串行总跑
   ```
   **红了先弄明白再改，不要为了让灯变绿而放宽判据。**
3. **健壮性基线**：无参数 → usage + `exit 2`；`--help` → `exit 0`；
   缺依赖 → 友好中文 + `exit 3`；文件不存在 → 友好中文 + `exit 1`，**不抛 traceback**。
   > ⚠️ **"没有选项"不等于可以忽略 `--help`** —— 不写参数解析时，`--help`
   > 会被当成"无参数"，直接跑起全套再按结果非 0 退出，
   > 而"跑一遍所有入口"那类护栏会因此**稳定判红**。
4. **一律 LF 行尾、无 BOM**（由 `.gitattributes` 钉死）。
5. **提交信息以对外版本号开头**（形如 `V0.1: …`），详见 `CONTRIBUTING.md`。
6. **站点信息不进仓库** —— 见第 8 条与 `references/MAINTENANCE.md`。
7. **`POTCAR` 及其任何片段不进仓库** —— 见第 8 条。
8. **⛔ 许可分层：不要用一个 MIT 盖整个仓库。**
   `LICENSE` 的 MIT **只覆盖原创部分**；仓库里捆绑了第三方内容：
   `references/official/` 是 **VASP Wiki**（**GNU FDL 1.2**，copyleft）、
   `references/raw/` 的讲义层**版权归原机构**（未获再分发授权）、
   `references/raw/lvthw/` 是 BigBro(a)s 的站（发布版为行数骨架）。
   ⇒ **逐层清单与合规做法见 [`NOTICE.md`](NOTICE.md)。**
   新增任何第三方内容时，**必须同时更新 `NOTICE.md`**。

## 7. 知识是怎么保证可信的（护栏一览）

| 护栏 | 守住什么 | 怎么证明它有效 |
|---|---|---|
| `_audit_citations.py` | **可回溯**：引用必须指向真实存在的页/段/文件 | 有注入测试 KC1–KC4（越界必红）+ KC5（合法引用放行） |
| `_inject_test.py` | 上面每一条护栏**真的会红**，且合法输入放行 | 自身就是证明；**53 条用例** + 1 条仓库自审（`KREPO`） |
| `_doc_consistency.py` | 文档里的数字与代码/目录里的真值一致；扫描**泄漏**（`POTCAR` 内容 / 站点信息 / 凭据） | 有注入用例 |
| `_check_coverage.py` | **精读报告是否真的读完了**：分段表行区间连续、无重叠、无空档、完整覆盖 | 断言式核查，红/绿分明 |
| `_versions.tsv` + `validate.py` | **版本门控**：这个标签**你那个 VASP 版本**支持吗（官方语料是 6.6 时代，真实算例全是 5.4.4） | 有注入测试 KH1（版本不够必红）/ KH2（版本够必放行）/ KH3（无标注不得误报） |
| `validate.py` 的 `XPAR.*` / `XNCORE.*` | **并行分解预检**（提交前）：`NCORE` 与 `NPAR` 同时出现（静默失效）、大体系没写 `NCORE`、除不尽 | 有注入测试 KI1-KI5（含「正确写法必放行」与「级别不得升级」两条反例） |
| `diagnose.py` 的 `LAUNCH.*` | **作业起没起来**这一层：有崩溃特征 + `OSZICAR` 零迭代 ⇒ 查并行分解 | 见 `references/playbook.md` §1 与 §4b |
| `_doc_consistency.py` 的生成物检查 | **`references/workflow.md` 不许手改**（生成物）：重新生成后逐字比，不一致必红 | 已实测注入（手改一个字 ⇒ 红，并给修法） |
| `_doc_consistency.py` 的**路径存在性**检查 | **文档里引用的仓库内路径必须真的存在** —— 防"改了机制、漏改文档" | 有注入用例 KK1（注入假路径 ⇒ 必红） |
| `_known_issues.tsv` | **官方缺陷登记簿**：110 条「不报错但结果错」的官方记录，带首现/修复版本 | 可查 `--for-version 5.4.4` |
| `references/MAINTENANCE.md` | 维护规矩（**机器细节不进，结论进**） | — |
| `CHANGELOG.md` 的**更正记录** | 记录"我原先写错了什么" | **60 条**（CR-001…CR-060） |

## 8. 诚实的能力边界

**能**：
- 讲清 VASP 四件套怎么协同、参数怎么选、结果怎么读；
- 校验输入（语法 / 关键字归属 / 值域 / **跨文件硬约束**）；
- 抽取输出数值、查跨文件一致性、查力平衡；
- 从症状出发给诊断与处方（73 条）；
- 生成**除 `POTCAR` 之外**的三个输入文件 + 一份逐参数解释的 README。

**不能**（**这是设计边界，不是"还没做"**）：
- ❌ **不能生成或分发 `POTCAR`** —— 它受 VASP 许可保护，不得再分发。
  本 skill 只能**校验**你已经有的那个（只读头部几个数字，不复制不缓存）。
- ❌ **不能替用户跑计算或提交作业**。
- ❌ **不能保证生成的输入"一定能跑"** —— 那要真程序（见 `conformance/`）。
- ❌ **不能判断"你的物理问题问得对不对"** —— 那是人的判断。
- ❌ **不从零生成初始结构**（切表面、建盒子需用户自备结构文件）。
- ❌ **不能保证解析在所有 VASP 版本上都对** —— 输出格式会跨版本漂移。
  因此所有解析结果**都带程序版本号**；不带版本号的结论请谨慎使用。

---

## 给 AI 助手的行为指引

当用户提到 VASP 相关需求时：

1. **先判断用户处于哪个阶段**（立项 / 建模 / 参数 / 收敛 / 优化 / 电子结构 /
   动力学 / 反应路径 / 后处理 / 诊断 / 报告）。不确定就先问，或让用户跑
   `doctor.py` 与 `wizard.py`。
2. **不要一次性输出全部参数**，而是按阶段给"当前该做什么 + 为什么 + 可选命令"。
3. **不要假装能跑 VASP** —— 只生成输入、校验、解析、诊断；实际计算在用户机器上。
4. **引用知识时优先引 `references/official/`**，并给出文件名/页面名。
5. **不确定时查，不要编。** 查不到就写"来源待核对"——
   这句话不丢人，编造才丢人。
6. **⚠️ 报参数前先确认对方用的是哪一版 VASP。**
   本 skill 的官方语料是 **6.6 时代**的，而真实算例全是 **5.4.4** ——
   **权威性与适用性是两件事**。有 `OUTCAR` 就读第一行；没有就问。
   用户版本低于门槛时**必须说**「这个标签在你的版本上可能不存在，
   而且程序可能**静默忽略**它」。**不要把"官方没标版本"说成"所有版本都支持"**。
   查门槛：`python references/official/_extract_versions.py --gate <标签>`；
   查已知缺陷：`python references/official/_extract_known_issues.py --for-version <版本>`；
   提到"某个 bug 已修"时**必须同时给首现版本与修复版本**（只说"已修"会让
   还在老版本上的人以为没事）。见 `references/VERSIONS.md`。
7. **绝不要把站点信息（集群地址/队列/核数/账号/路径）写进任何交付文件。**
   需要站点参数时，写成 `<<<请填写>>>` 占位符。
8. **⚠️ 诊断时先看 `references/playbook.md` §4b「诊断反模式」。**
   最常犯的两条：① **报资源数字（栈/内存/耗时）时必须同时报
   "在什么并行配置下测的"**（不带配置的资源数字没有意义）；
   ② **"某个取值没救回来" ≠ "该变量无关"**。
   还有一条本项目的教训：**"是不是真的"与"该不该报红"是两个问题** ——
   一条真的发现若命中率过高，当 WARNING 就是噪声。
9. **用户报"出问题了"时，先读 `references/_ENTRY.md` 做第 0 步分类**：
   **A 没跑起来** / **B 跑完但结果不对** / **C 慢**。
   ⚠️ **三类的处方是冲突的** —— 没分类就调参等于赌博。
   分诊命令：`grep -cE "^(DAV|RMM):" OSZICAR`（0 ⇒ A 类）。
   **判据不是 `exit code`**（`mpirun` 下崩溃时它可能仍是 0 或 255）。
10. **用户说"算完了但结果不对"时**，按顺序建议：
   `validate.py` → `compare.py` → `diagnose.py` → 查 `playbook.md` §1。

完整用法见 `USAGE.md`；项目结构见 `README.md`；改动与更正记录见 `CHANGELOG.md`；
维护规矩见 `references/MAINTENANCE.md`；**版本问题见 `references/VERSIONS.md`**。
