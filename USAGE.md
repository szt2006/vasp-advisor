# USAGE —— VASP 计算顾问 使用说明（面向人）

> 面向 AI 的入口是 `AGENTS.md` / `SKILL.md`；本文件面向**用它的人**。
> 项目结构见 `README.md`；改动规范见 `CONTRIBUTING.md`。

---

## 0. 30 秒上手

```bash
python scripts/doctor.py        # ① 环境自检（**永远先跑这个**）
python scripts/wizard.py        # ② 一问一答生成一套自洽输入
#   → 自己拼 POTCAR（受许可保护，本 skill 不生成）
python scripts/validate.py <输出目录> --potcar <你的 POTCAR>
#   → 上机跑
python scripts/parse_output.py <输出目录>   # ③ 看数值
python scripts/compare.py      <输出目录>   # ④ 看结果自不自洽
python scripts/diagnose.py     <输出目录>   # ⑤ 出问题了：症状 → 处方
```

**⭐ 出了问题？先做第 0 步分类** → `references/_ENTRY.md`
（**A 没跑起来** / **B 跑完但结果不对** / **C 慢** —— 三类的处方是冲突的，**没分类就调参等于赌博**）

**⭐ 不知道现在该干什么？先跑这个**（它替你判断阶段）：

```bash
python scripts/guide.py list          # 看 11 个主线阶段 + 1 个续算分支
python scripts/guide.py scan <目录>    # 推断「你卡在哪、下一步做什么」
python scripts/guide.py show params   # 展开某个阶段的完整指引
```

⚠️ `scan` 是**启发式**（按你目录里有哪些文件判断），
**它会打印推断依据**，你可以直接推翻它。它**只读、不改、不提交作业**。

**零依赖**：核心脚本只用 Python 标准库（≥3.8）。唯一例外是
`postprocess.py --plot`（出图）需要 `matplotlib`，缺了会友好提示 + `exit 3`，
**数值照样打出来**。

---

## 1. 先接受三件事，再往下读

### 1.1 `OK` 不等于"算得对"

| 工具 | 它回答 | `OK` 的真实含义 |
|---|---|---|
| `validate.py` | 输入写对了吗 | 只是"**我检查过的那些项**没发现问题" |
| `compare.py` | 结果自洽吗 | 只是"文件之间**一致**" + "力平衡" |
| `diagnose.py` | 是哪一类问题 | 只是"**没找到我认识的那个模式**" |

**每个工具都会打印"本次未检查的项"。** 那不是"通过了"，是"没查"。

**为什么这么强调**：本 skill 的实测教训是 —— 有人拿生成的输入看到 `OK`、
据此上了集群、**白跑一趟**，因为 `OK` 只覆盖了语法与拼写那一层。

### 1.2 本 skill 不生成 `POTCAR`

`POTCAR` 受 VASP 许可保护，**不得再分发**。所以 `wizard.py` 只写一份
`POTCAR.README` 教你怎么拼；`validate.py --potcar` **只读头部几个数字**
（`TITEL`/`ENMAX`/`ZVAL`），**不复制、不缓存、不写出正文**。

### 1.3 大部分阈值**没在真机上标定过**

构建环境没有 VASP。所以力判据默认报 `WARN` 而非 `ERROR`，
诊断规则只有"官方明文 / 算例实证"的才是 `确定` 级。
标定方法见 `conformance/README.md` —— **需要你（有真程序的人）来补**。

---

### 1.4 ⚠️ **你的 VASP 版本会影响上面每一条建议**

这是实测出来的一个风险，不是"注意事项"：

| 来源 | 实测版本 |
|---|---|
| 本 skill 抓的官方 wiki 语料 | **VASP 6.6 时代** |
| `things to study/` 的 98 个真实算例 | **全部 `vasp.5.4.4`** |

**为什么要紧**：VASP 对 `INCAR` 里**不认识的标签**常常**静默忽略** ——
你以为设了，其实没生效，而且**不会有任何报错**。

**怎么做（三步）**：

```bash
# ① 看你的版本（最可靠）
head -1 OUTCAR       # → vasp.5.4.4.18Apr17-… complex

# ② 让校验器知道（它会检查"这个标签你的版本支持吗"）
python scripts/validate.py <算例目录> --vasp-version 5.4.4

# ③ 查你那个版本的官方已知缺陷
python references/official/_extract_known_issues.py --for-version 5.4.4
```

> ⚠️ **「官方没标版本」≠「所有版本都支持」。**
> 官方只对**新加的**标签标 `{{Available}}`，绝大多数标签根本没标。
> 正确措辞是「**官方未标注版本门槛**」。

总纲见 `references/VERSIONS.md`（含 **5.4.4 用户最该知道的 5 条官方已知缺陷**）。

---

## 2. 工具详解

### 2.1 `doctor.py` —— 环境与脚本自检

```bash
python scripts/doctor.py
python scripts/doctor.py --dir <算例目录>    # 顺便体检一个算例
python scripts/doctor.py --json
```

检查：Python 版本、**每个脚本能否编译**、知识库文件是否齐全、
关键字表在不在（不在 ⇒ 归属校验不生效，会明说）、
顺手看一个算例目录里有什么。

**退出码**：`0` 核心可用 · `1` 有文件缺失但部分可用 · `3` Python 太旧。

### 2.2 `wizard.py` —— 输入向导

```bash
python scripts/wizard.py                     # 交互式
python scripts/wizard.py --list-goals        # 看 12 个目标
python scripts/wizard.py --non-interactive \
    --goal slab-adsorption --poscar POSCAR --out ./calc \
    --elements "Pt O" --metal --potcar ./POTCAR
```

**12 个目标**：`bulk-static` `bulk-relax` `slab-relax` `slab-adsorption`
`dos` `freq` `band` `molecule` `neb` `dimer` `aimd` `resume`。

生成物：

```
<输出目录>/
├── INCAR          # 每个参数带注释，注明理由与陷阱
├── KPOINTS        # **一律 Γ 居中**（理由见下）
├── POSCAR         # 从你给的结构复制（归一成 LF、去 BOM）
├── POTCAR.README  # 说明为什么这里没有 POTCAR，以及怎么拼
├── README.md      # **逐参数解释 + 收敛测试怎么做 + 下一步**
└── submit.sh      # 提交脚本骨架，**所有站点相关的都是 <<<请填写>>> 占位符**
```

**为什么 `KPOINTS` 一律 Γ 居中**（官方明文，三条）：
①规则网格是生产计算首选；②四面体方法（`ISMEAR=-5`）**必须** Γ 居中；
③**fcc / hexagonal 晶格只能**用 Γ 居中 —— Monkhorst-Pack 在偶数细分时
会破坏对称性，可能直接报 `IBZKPT` 与 `generating k-lattice` 的错误。

**它不做**：不生成 `POTCAR`、不提交作业、不做收敛测试。
生成物**未经真机验证**。

### 2.3 `recommend.py` —— 参数推荐

```bash
python scripts/recommend.py --list-goals
python scripts/recommend.py --goal slab-adsorption --elements "Pt O" --metal
python scripts/recommend.py --goal dos --elements "Co N C" --potcar ./POTCAR
```

给**文字**（推荐 + 理由 + 代价 + 出处），不是文件。想直接开算用 `wizard.py`。
两者共用**同一份**目标定义，避免"两份逻辑给出不同答案"。

它会根据元素清单**提醒**你要不要 `ISPIN=2` / 考虑 DFT+U ——
⚠️ 那些清单是**经验**的，作用是提醒，不是判定。

### 2.4 `validate.py` —— 输入校验

```bash
python scripts/validate.py <算例目录>
python scripts/validate.py <目录> --potcar <POTCAR 路径>
python scripts/validate.py <目录> --strict      # WARNING 也判失败
python scripts/validate.py --list-checks        # 看它会查什么、不查什么
```

**查 25 项**，按层分：

| 层 | 查什么 |
|---|---|
| 语法 | `tag = value` 形式、`;` 分隔、续行、引号跨行、字段数 |
| **归属** | 关键字**是否真的存在**、**是否属于该文件**（依赖官方关键字表） |
| 值域 | 已收录 tag 的取值域（**覆盖率有限，会明说**） |
| 跨文件 | 元素顺序、`ENCUT` vs `ENMAX`、`MAGMOM` 个数、`LDAU` 列表长度、维度 vs k 点 |

**几个它真的抓到过的真问题**（都在真实算例里）：

- `1-fundamental/hse/INCAR:62`：
  `ALGO = ALL (Electronic Minimisation Algorithm; ALGO=58)`
  —— **圆括号不是注释，`;` 是语句分隔符**，这行会被切成两句。
- `partialCharge/INCAR`：从 wiki 抄示例时把 `#` 丢了，
  值变成 `1    job   : 0-new  1-cont  2-samecut`。
- `ex8-NaHe2`：`ENCUT = 520` 而 He 的 `ENMAX = 2135 eV` ——
  **这条工具只报 WARN**，因为 `ENMAX` 是孤立原子的推荐值，
  闭壳层 He 几百 eV 可能就够（**这是经验判断，不是官方规则**）。

**并行分解预检（`XPAR.*` / `XNCORE.*`）—— 提交作业之前该看的**

```bash
python scripts/validate.py <目录> --ncores <你实际提交的核数>
```

⚠️ **这一组检查回答的是"作业会不会根本起不来"**，而其它检查回答"输入写对没有"。
背景：一个 179 原子体系、16 rank、**没写 `NPAR`/`NCORE`**（走默认 `NCORE=1`）
⇒ 每个 rank 独占一个 band、独自完成整块 FFT ⇒ **第一次 SCF 就 `SIGSEGV`**。
只加一行 `NPAR = 2` 就好了。**当时 `validate.py` 一项都没查并行标签。**

| 检查 | 判据 | 级别 |
|---|---|---|
| `XPAR.both_set` | `NCORE` 与 `NPAR` **同时出现** ⇒ `NPAR` 优先、`NCORE` 被**静默忽略**（官方明文） | WARN |
| `XNCORE.missing_with_rank` | 没写 `NCORE`/`NPAR`，而体系**≥100 原子**且核数 ≥8 ⇒ 默认 `NCORE=1` 是危险区 | WARN（小体系为 INFO） |
| `XNCORE.inconsistent` | 写的值与可用 rank 数**除不尽**（程序会自己改，不报错） | **INFO**（⚠️ 见下） |

⚠️ **核数的来源有优先级**：**`LOG` 横幅里的实际核数**（一手事实）
优先于 `--ncores`（你的记忆）。

⚠️ **`XNCORE.inconsistent` 为什么是 INFO 而不是 WARN**：用**真实核数**
跑 98 个真实算例，这条命中 **46 个（47%）**。它们**不是假阳性**
（写的与生效的确实不同），但**不影响正确性** —— VASP 照样算、照样收敛。
⇒ **47% 的 WARNING 会把人训练成忽略整个报告**；47% 的 INFO 才是诚实的。

⚠️ **本组只查"标签之间的关系"，不判断某个取值会不会栈溢出/内存不足**
（那取决于每 rank 的内存上限、FFT 网格、赝势、编译器 —— 本工具看不到），
也**不替你选 `NCORE`**（官方给的是"跑一个简短的 `NCORE` 扫描"）。
**它是预检，不是保证。**

**退出码**：`0` 无 ERROR · `4` 有 ERROR · `5` 仅有 WARNING。

### 2.5 `parse_output.py` —— 数值抽取

```bash
python scripts/parse_output.py <算例目录>
python scripts/parse_output.py <目录> --json
python scripts/parse_output.py <目录> --csv energies.csv
python scripts/parse_output.py <目录1> <目录2> ... --summary
python scripts/parse_output.py <目录> --param ENCUT
```

**只读数，不做判断**（判断交给 `compare.py`/`diagnose.py`）——
这样"抽取"与"判断"各只有一份实现。

给：版本号、每个离子步的 `energy(sigma->0)` / `TOTEN` / `E-fermi` /
最大力 / RMS 力 / `total drift` / 是否收敛、以及**从 `OUTCAR` 回显读到的实际参数**。

⚠️ **默认给 `energy(sigma->0)`，不是 `free energy TOTEN`** ——
后者含展宽熵项 `−TS`，**不同展宽参数之间不可比**。要 `TOTEN` 加 `--toten`。

### 2.5b ⚠️ 作业起不来时，先看这两件事（**别急着找管理员**）

```bash
grep -E "running on|distrk:|distr:" LOG    # 并行分解：每 rank 干多少活
grep -E "forrtl|SIGSEGV|BAD TERMINATION" LOG  # 崩在哪一行
grep -cE "^(DAV|RMM):" OSZICAR             # 0 = 一次 SCF 都没走
```

**判据：`OSZICAR` 里有没有 `DAV:` / `RMM:` 行。**
⚠️ **不要用 `exit code` 判断** —— `mpirun` 下崩溃时它可能仍是 0 或 255。

**最常见的一类**：`distr: one band on 1 cores` ⇒ 每个 rank 独占一个 band、
独自完成整块 FFT ⇒ 大体系 + 多核下内存/栈爆 ⇒ 第一次 SCF 就崩。
**先试 `NCORE ≈ √(核数)`，再考虑系统配置。**

⚠️ 诊断时最容易犯的错，见 `references/playbook.md` §4b「**诊断反模式**」——
尤其：**报资源数字时必须同时报"在什么并行配置下测的"**。

### 2.6 `compare.py` —— 物理不变量与一致性

```bash
python scripts/compare.py <算例目录>
python scripts/compare.py <目录> --strict
python scripts/compare.py --list-checks
```

**这是唯一能查"算得不对"的离线工具**（`validate.py` 只查输入）。它查：

| 检查 | 抓什么 |
|---|---|
| `E.selfconsistent` | `OSZICAR` 与 `OUTCAR` 的能量是否一致 |
| `X.nions_consistent` | `POSCAR`/`OUTCAR`/`vasprun.xml` 的原子数是否一致 |
| `X.encut_consistent` | `INCAR` 写的 `ENCUT` 与程序**实际用的**是否一致 |
| **`F.balance_isolated`** | **力平衡 `|ΣF|`**（孤立体系应严格为 0）—— **零成本** |
| `F.drift_reported` | 报告 `OUTCAR` 自带的 `total drift` |
| `C.isif3_cell` | `ISIF=3` 时晶胞是否真的变了（核对 `OPTCELL` 是否生效） |
| `C.freq_dof` | `IBRION=5` 的自由度是否为 **3×放开原子数**（不是 3N） |

⚠️ **诚实说明**：`F.` 开头的力判据**阈值未在真机上标定**
（没有 VASP 就无法构造"已知错误的计算"来标定），所以默认报 `WARN`。
**把它当线索，不要当判据。**

⚠️ **力平衡只对孤立体系成立**。有固定原子/约束的体系里 `ΣF ≠ 0` 是正常的 ——
工具靠 `Selective dynamics` 判断，并用**相对比值**而不是绝对值。

### 2.7 `diagnose.py` —— 症状 → 诊断 → 处方

```bash
python scripts/diagnose.py <算例目录>
python scripts/diagnose.py --list-rules
python scripts/diagnose.py <目录> --verbose   # 连常见做法也列出来
```

**16 条规则**，每条给**四要素**：症状（含可 grep 的原文）/ 诊断 / 处方 /
判据。设计上分两档：

- **`确定`** —— 只给"官方明文"或"算例实证"的条目；
- **`提示`** —— 需要你自己判断的；
- **`仅详细模式`** —— 属于"常见做法"而非"问题"的（例如 `ISYM = 0`）。

**它承认自己不认识的东西**：找不到症状时明确说
"**没找到症状不等于算得对**，本工具只认它认识的模式"。
更多症状（73 条）见 `references/playbook.md` §1。

**⭐ `LAUNCH.*` 是「作业起没起来」这一层**（本项目后来补的，因为原来完全没有）：

原来的那些规则**全部假设「计算跑完了」** —— 它们读 `OUTCAR`/`OSZICAR` 的
**内容行**。所以对"第一次 SCF 就崩"的算例，它们要么不触发、
要么给出**不可能执行的处方**（"看 `OSZICAR` 最后一步的 `d E`" —— 可它没有最后一步）。

`LAUNCH` 层读 **`LOG` / 作业日志**，认这几件事：

| 规则 | 认什么 |
|---|---|
| `LAUNCH.crash_no_scf` | 有崩溃特征（`forrtl: severe (174) SIGSEGV` 等）**且** `OSZICAR` 一次迭代都没有 ⇒ **先查并行分解**（横幅 `one band on 1 cores` = 默认 `NCORE=1` 的签名），试 `NCORE ≈ √(可用 rank 数)` |
| `LAUNCH.ulimit_redherring` | `ulimit: stack size: cannot modify limit` —— ⚠️ **红鲱鱼**，成功作业里也会出现，**不能单独当证据** |
| `LAUNCH.par_tags_inconsistent` | `INCAR` 写的 `NCORE` 与横幅生效值不一致（**仅详细模式**，因为它误报率约 15%） |

⚠️ **判据不是 `exit code`** —— `mpirun` 下崩溃时它可能仍是 0 或 255。
判据是 `OSZICAR` 里出现 `DAV:` / `RMM:` 行。

### 2.8 `postprocess.py` —— 后处理

```bash
python scripts/postprocess.py --list
python scripts/postprocess.py dos      <目录> --band-center
python scripts/postprocess.py dos      <目录> --window -10 5 --out dos.tsv
python scripts/postprocess.py workfunc <目录> --efermi <值>
python scripts/postprocess.py efermi   <目录>
python scripts/postprocess.py gap      <目录>
```

| 子命令 | 算什么 | 已知局限 |
|---|---|---|
| `dos` | 态密度、积分电子数、带中心 | 算的是**整个 DOSCAR**；某元素的 d 带中心需要读分段（工具不做） |
| `workfunc` | 功函数（`LOCPOT` 平面平均） | **只沿 c 轴**平均；势的口径要自己确认 |
| `efermi` | 费米能级 | 同一输出里可能出现多次（每个离子步一次） |
| `gap` | 带隙（**粗估**） | 只按已有 k 点判 → 间接带隙会**高估** |

**两个实测踩过的坑（工具已修，但你该知道）**：

1. **`DOSCAR` 的列语义依赖 `ISPIN`**：
   `ISPIN=1` 是 `E DOS intDOS`；`ISPIN=2` 是
   `E DOS(up) DOS(dn) intDOS(up) intDOS(dn)` ⇒ **积分值在第 4、5 列**。
   （课程答疑说"看第三列"，那只对 `ISPIN=1` 成立。）
2. **报带中心必须同时报积分窗口**：实测同一份 PDOS，仅把积分上限定成
   20 eV 而不是 `EMAX−EFERMI`，结果就差 **0.027 eV** —— 足以改变结论。
   工具会自动把窗口打出来。

---

## 3. 按需求找东西（grep 直击）

| 你想知道 | 去哪 |
|---|---|
| 某参数该填多少、为什么、代价是什么 | `references/decide.md` |
| 出错了怎么修 | `references/playbook.md` §1（症状→处方 73 条） |
| 某个报错原文是什么意思 | `references/playbook.md` §5 报错速查 |
| 官方**原话**怎么说 | `references/official/pages/<页面>.md` |
| 这门课怎么讲的 | `references/course_learned.md` |
| 讲义原文第 N 页 | `references/raw/L1.txt`（搜 `PAGE N`） |
| 快速查一个常用数值 | `references/course_notes.md` · `decide.md` 附录 A |
| 某条经验有多可信 | 看它的证据标记（`[官方]`/`[算例]`/`[经验]`/`[待核对]`） |

**可 grep 性 > 可读性**：有经验的用法是**按问题 grep 命中**，不是顺序读。
每个主题都应该能回答"该去哪一层找"。

---

## 4. 任务剧本（照着做）

### 剧本 A：从一个结构开始做表面吸附能

```bash
# 1. 先体检
python scripts/doctor.py

# 2. 生成输入（假设 slab 已建好，含 Selective dynamics）
python scripts/wizard.py --goal slab-adsorption \
    --poscar slab_O.vasp --out ./oads --elements "Pt O" --metal

# 3. 拼 POTCAR（顺序必须与 POSCAR 第 6 行一致！）
cat ~/pot/Pt/POTCAR ~/pot/O/POTCAR > ./oads/POTCAR

# 4. 校验
python scripts/validate.py ./oads --potcar ./oads/POTCAR

# 5. 改 submit.sh 里的 <<<请填写>>>，先跑一个极小算例（NSW=2, NELM=20）

# 6. 正式跑，跑完
python scripts/parse_output.py ./oads --summary
python scripts/compare.py      ./oads
python scripts/diagnose.py     ./oads
```

⚠️ **算吸附能必须把「干净 slab」和「孤立吸附物」用同一套参数各算一次**，
否则系统误差不抵消。

### 剧本 B：收敛测试

一次只动一个量，其余固定；每次都做**单点**（`NSW=0`、`IBRION=-1`）；
读 `energy(sigma->0)`（不是 `TOTEN`）。

| 优先级 | 量 | 判据 |
|---|---|---|
| 1 | `ENCUT` | 相邻截断能的总能量差 < **1 meV/atom** |
| 2 | k 点密度 | 相邻网格的能量差 < **1 meV/atom** |
| 3 | 真空层（slab） | 表面能/吸附能变化 < 0.01 eV/Å² |
| 4 | slab 层数 | 吸附能变化 < 0.05 eV |
| 5 | `SIGMA` | 只对金属/近简并体系重要 |

⚠️ 官方对 `ENCUT` 的**唯一**要求是"显式写 + 单独测收敛"。
常听说的"取 `ENMAX` 的 1.3 倍"其实是**已弃用的 `PREC=High`** 的行为，
**不是官方推荐值** —— 见 `references/decide.md` §4.2 的更正记录。

### 剧本 C：跑完了但结果不对

```bash
python scripts/validate.py <目录> --potcar <POTCAR>   # 输入层
python scripts/compare.py  <目录>                     # 自洽层
python scripts/diagnose.py <目录>                     # 症状层
grep -n "XXX" references/playbook.md                  # 手册层
```

**最值钱的一类问题没有任何报错**。本 skill 收了几条真实的：

| 症状 | 自查动作 |
|---|---|
| DOS 出自**弛豫**计算（不是单点） | `grep -c "E-fermi" OUTCAR` 应为 **1** |
| `OPTCELL` 没生效（程序不回显它） | 比对 `POSCAR` 与 `CONTCAR` 的晶格 |
| 改了 `MAGMOM` 但磁矩没变 | 检查 `ISTART`/`ICHARG` —— **续算时 `MAGMOM` 只定对称性、不设初值** |
| 报带中心换了窗口就变 | **报的时候必须同时报窗口** |

---

## 5. 常见问题

**Q：为什么 `validate.py` 报关键字未知，但我的写法明明是对的？**
A：官方 wiki 的关键字分类**不完整**。工具**分三档报**：
`OUTCAR` 回显里有它 ⇒ `INFO`；`OUTCAR` 有但没有它 ⇒ `ERROR`（**可证伪的静默失效**）；
没有 `OUTCAR` 可比 ⇒ `WARN`。见 `references/decide.md` §1.2 的完整说明。

**Q：`compare.py` 说我的 `|ΣF|` 偏大，是不是算错了？**
A：先看**有没有固定原子**。有固定/约束的体系里 `ΣF ≠ 0` 是正常的
（约束力不体现在 `TOTAL-FORCE` 里）。工具会用相对比值判，并明确标注阈值未标定。
**别把它当"算错了"的证据**，把它当"值得看一眼"的线索。

**Q：为什么我的集群参数要自己填？**
A：`references/MAINTENANCE.md` §0.1「**机器细节不进，结论进**」。
猜机器细节 = 换机器就废。给站点信息一个出口：`SITE.md`（永不入库）。

**Q：能不能让它自动跑完整个流程？**
A：**不能，这是设计选择。** 本 skill 是"顾问，而非自动驾驶" ——
所有工具都是"给建议 / 生成输入 / 校验 / 解析 / 诊断"，由**你**决定执行。
这条不是口号，它决定了 API 形状：**没有一个接口是"读完需求自动跑完流水线"**。

---

## 6. 退出码约定（全 skill 统一）

| 码 | 含义 |
|---|---|
| `0` | 成功（**校验类工具里表示"没发现问题"，不表示"算得对"**） |
| `1` | 用户输入/文件有问题 |
| `2` | 命令行用法错误 |
| `3` | 缺依赖，或缺少必要的外部信息（如没给 VASP 可执行文件路径） |
| `4` | 发现了**错误级**问题 |
| `5` | 发现了**警告级**问题（`--strict` 时提升为 `4`） |

**每个脚本 `--help` 都 `exit 0`** —— 这不是小事：本项目踩过
"没写参数解析 ⇒ `--help` 被当成无参数 ⇒ 直接跑起全套再按结果非 0 退出" 的坑，
而那会让人以为工具坏了。
