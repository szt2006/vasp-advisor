# decide.md —— VASP 决策库（A 层）

> **这份文件回答的是「遇到 X 该选 Y，因为 Z，代价是 W」。**
> 它**不是**百科，不解释"`ISMEAR` 是什么"；它只说"你该写哪个值、为什么、什么时候别这么写"。
>
> | 你想知道的 | 去哪 |
> |---|---|
> | 该选什么参数、为什么、代价是什么 | **本文件** |
> | 出错了怎么修（症状→处方） | `playbook.md` |
> | 这门课讲了什么 | `course_learned.md` |
> | 官方原文 | `references/official/`（627 个 wiki 页面，抓取日期见 `_sources.tsv`） |
> | 讲义原文 | `references/raw/L1–L4.txt` + `learn_L1–L4.md` |
>
> **权威序（冲突时照此裁定）**：
> `references/official/`（官方）> 真实算例文件 > 讲义 `L*` > 答疑 `D*` > 本文件里的 `[经验]`。
>
> **证据标记**（每条结论都带一个，见 `_WRITING_CONTRACT.md`）：
> `[官方]` 官方明文 · `[算例]` 真实文件里的事实 · `[讲义]` · `[答疑]` ·
> `[实测]` 本项目构建时真跑出来的 · `[经验]` 有适用范围的经验判据 · `[待核对]` 单一来源或推论
>
> ⚠️ **本文件里凡是标 `[经验]` 或 `[待核对]` 的，都不是官方规则**，是"在特定条件下成立"的判断。
> 用之前先看它的**适用范围**与**反例**。

---

## 目录

| § | 主题 | 一句话 |
|---|---|---|
| [§0](#0-怎么用这份决策库) | 怎么用这份决策库 | 三条使用原则 |
| [§1](#1-输入文件的结构性事实vasp-与-cp2k-最根本的不同) | 输入文件的结构性事实 | 四件套怎么协同 |
| [§2](#2-开工前必须确定的三件事) | 开工前必须确定的三件事 | 目标 / 维度 / 元素 |
| [§3](#3-收敛测试总纲) | 收敛测试总纲 | 先测什么、判据是什么 |
| [§4](#4-encut 怎么定) | `ENCUT` 怎么定 | 与 POTCAR 的 `ENMAX` 关系 |
| [§5](#5-k-点怎么定) | k 点怎么定 | 网格、中心、密度 |
| [§6](#6-展宽-ismearsigma-怎么选) | 展宽 `ISMEAR`/`SIGMA` | 金属 vs 绝缘体 |
| [§7](#7-自旋ispin--magmom) | 自旋 `ISPIN` / `MAGMOM` | 初值决定收敛到哪个态 |
| [§8](#8-dftu-怎么设) | DFT+U | 两套写法差 1 eV |
| [§9](#9-几何优化参数) | 几何优化 | `IBRION`/`ISIF`/`EDIFFG` |
| [§10](#10-二维材料与-vdw) | 二维与 vdW | `OPTCELL`、`IVDW`/`LUSE_VDW` |
| [§11](#11-slab-建模) | slab 建模 | 真空层、固定、钝化 |
| [§12](#12-过渡态搜索) | 过渡态 | NEB / CI-NEB / Dimer |
| [§13](#13-频率计算与虚频) | 频率与虚频 | 判据与自由度语义 |
| [§14](#14-能量与力的读法) | 能量与力的读法 | 读哪个数、怎么判 |
| [§15](#15-带电体系与偶极修正) | 带电体系与偶极修正 | `NELECT`/`LDIPOL` |
| [§16](#16-气相分子与参考态) | 气相分子与参考态 | O₂ 必须反推 |
| [§17](#17-自由能校正zpe--熵) | 自由能校正 | ZPE 只算吸附物 |
| [§18](#18-溶剂模型) | 溶剂模型 | 显式 vs 隐式 / VASPsol |
| [§19](#19-性能与并行) | 性能与并行 | `NCORE`/`KPAR`/`LREAL` |
| [§20](#20-常见硬规则汇总可抄) | 硬规则汇总 | 一张表 |
| [§A](#附录-a本文件里的数值速查) | 数值速查 | 数值 + 适用范围 + 出处 |
| [§B](#附录-b本文件明确不覆盖的范围) | 不覆盖的范围 | 诚实的能力边界 |

---

## §0 怎么用这份决策库

### 原则一：**"代价"比"推荐值"重要**

每一条都写了"这么选的代价"。原因很直接：**你一定会遇到我没覆盖的情形**，
而那时"推荐 Y"这句话对你毫无帮助；有用的只有"Y 在什么条件下不成立"。

### 原则二：**先问"我要什么"，再问"参数写什么"**

VASP 的参数本身不难写，难的是**知道自己在追什么量**。
追总能量、追能量差、追力、追态密度 —— 对同一套参数的要求完全不同。
所以 §2 要求你先回答三个问题，之后每一节都会引用它们。

### 原则三：**`[经验]` 与 `[待核对]` 不是"弱化版的官方"**

它们是**性质不同**的东西：官方规则是"不这么做就错"，
经验判据是"在这些体系上这么做通常对，但我知道反例"。
把 `[经验]` 当硬规则用，就会在反例上翻车。

---

## §1 输入文件的结构性事实（VASP 与 CP2K 最根本的不同）

### 1.1 四个文件**互相耦合**，而且耦合是**按位置**而不是按名字

| 文件 | 角色 | 谁决定它 |
|---|---|---|
| `INCAR` | **做什么、怎么做**（算法与参数） | 你 |
| `KPOINTS` | k 点采样 | 你（或 `KSPACING`） |
| `POSCAR` | 结构（晶格 + 元素顺序 + 坐标） | 你 |
| `POTCAR` | 每个元素的赝势 | 你，**但受许可约束** |

**跨文件硬约束（`[官方]`）**：

1. **`POTCAR` 的数据集顺序必须与 `POSCAR` 的元素顺序完全一致** ——
   官方原文：`It contains the pseudopotential for each atomic species
   in the same order as in the POSCAR`（`references/official/pages/POTCAR.md`）。
   VASP **按位置**配对，不按元素名匹配。**顺序错了程序不报错**，只是每个原子的赝势都是错的。
   → 本 skill 的 `validate.py` 会核对这一条（`XSPECIES.elements`）。

2. **`POTCAR` 是只读的** —— 官方原文：`The settings in the POTCAR file are
   read-only and must not be edited.` 选泛函要改 `INCAR` 里的 `XC`/`GGA`/`METAGGA`，
   **不要去改 `POTCAR` 的 `LEXCH`**。`[官方]`

3. **`POTCAR` 自带 `ENMAX`/`ENMIN`，会决定 `ENCUT` 的默认值**（见 §4）。

4. **`KPOINTS` 缺省时由 `INCAR` 的 `KSPACING` 决定**（见 §5）。`[官方]`

### 1.2 **VASP 没有 CP2K 那样的官方机器可读 schema**

这一条决定了本 skill 的校验架构，必须写清楚：

- 官方**没有** `vasp_input.xml` 这类 schema 文件。
- 但官方 wiki 是 MediaWiki，`Category:INCAR_tag` **可以机器枚举**（613 个标签）。
- 于是本 skill 的做法是：用 `references/official/_fetch_wiki.py` 抓这个分类页，
  自动生成关键字归属表 `references/official/_keywords.tsv`（620 行），
  再做**归属校验**（"这个 tag 到底存不存在、属不属于这个文件"）。

**⚠️ 这张表的覆盖率必须如实传播**：它**不完整**。实测（2026-11，逐页查证）：

| 标签 | 在 `Category:INCAR_tag` | wiki 有独立页面 | 结论 |
|---|---|---|---|
| `LUSE_VDW` `ZAB_VDW` `AMIX_MAG` `BMIX_MAG` `NKRED` `HFSCREEN` | ❌ 不在 | ✅ 有 | **是真标签，别误判成拼错** |
| `ICHAIN` `IOPT` `LCLIMB` | ❌ 不在 | ❌ 没有 | 核心标签，但 wiki 没建页 |
| `LSOL` `LRHOB` | ❌ 不在 | ❌ 没有 | VASPsol **插件**标签 |

所以 `validate.py` 对"不在表里"的标签**分三档报**（见该脚本 `_unknown_tag_finding`），
并且在报告里显式列出"本次未检查的项"。**它的 `OK` 从来不等于"算得对"。**

### 1.3 `INCAR` 的格式陷阱（三个真实踩过的坑）

| 坑 | 官方原文依据 | 真实案例 |
|---|---|---|
| **`;` 是语句分隔符，括号不是注释** | `it is possible to combine multiple statements on a single line, separating them by a semicolon ;`；`VASP ignores any text after a hashtag # or exclamation mark !` | `1-fundamental/hse/INCAR:62` 写 `ALGO = ALL (Electronic Minimisation Algorithm; ALGO=58)` → 被切成两句，第二句是 `58)` |
| **反斜杠后续行时，反斜杠后不能有空格** | `Avoid blanks after the backslash because some versions of VASP cannot parse those.` | — |
| **自由文字里不能含 `= ; "`** | `do not use any syntax relevant character (=;") because it may break the parsing` | `partialCharge/INCAR` 把 wiki 的 `#` 丢了，值变成 `1    job   : 0-new  1-cont  2-samecut` |

`[官方]` 全部来自 `references/official/pages/INCAR.md`。
`[算例]` 来自上表所列的真实文件。→ 处方见 `playbook.md`。

### 1.4 `KPOINTS` 有五种模式，靠**第 3 行第一个非空字符**区分

| 第 2 行 `nk` | 第 3 行首字符 | 模式 | 用途 |
|---|---|---|---|
| > 0 | 任意 | **显式列表** | 特定 k 点、能带（非 line 模式） |
| 0 | `G`/`g` | 规则网格 Γ 居中 | **生产计算首选** |
| 0 | `M`/`m` | 规则网格 Monkhorst-Pack | 可能收敛更快，但见 §5.3 的对称性陷阱 |
| 0 | `C`/`c`/`K`/`k`/`R`/`r` | **广义规则网格** | 需与倒格矢 commensurate，否则程序报错退出 |
| 0 | `L`/`l` | **line 模式** | 能带。**必须配 `ICHARG=11`**（官方 Warning） |
| 0 | `A`/`a` | 全自动（`R_k`） | 官方标 **Deprecated**，优先用 `KSPACING` |

`[官方]` `references/official/pages/KPOINTS.md`。

> 💡 **line 模式最容易被误用**：官方 Warning 写明
> `The mesh generated by this mode is not suitable for self-consistent calculations.
> Please set ICHARG = 11 to avoid updating the density.`
> 即：**先用规则网格算收敛的电荷密度，再用 line 模式 + `ICHARG=11` 做非自洽**。
> 反例：直接拿 line 模式的 KPOINTS 跑自洽，得到的密度不可信。

---

## §2 开工前必须确定的三件事

**不要跳过这一节。** 后面每一节的判据都依赖这三个答案。

### 2.1 你追的是哪个量？（决定收敛判据的严格程度）

| 你追的量 | 收敛判据的严格程度 | 理由 |
|---|---|---|
| 总能量的**绝对值** | 宽松（`ENCUT` 到 1 meV/atom 即可） | 常数偏移会在作差时消掉 |
| 能量**差**（吸附能、反应能、表面能） | **最严** | 误差直接进结论，且常常是 meV 量级的差 |
| **力** / 几何优化 | `ENCUT` 可以略松，但 `EDIFFG` 必须严 | 力对截断的敏感度低于能量差 |
| **态密度** / d 带中心 | 需要更密的 k 点 + 四面体方法（`ISMEAR=-5`） | 谱函数需要精细采样 |
| 过渡态**能垒** | 最严：`EDIFF = 1E-7` 量级 | 能垒是两步能量之差，误差叠加 |
| 频率 / ZPE | 强依赖几何收敛质量 | 频率是能量的二阶导，几何不收敛就没有意义 |

`[经验]` 这张表的每一行都是"追什么量 → 参数严到什么程度"的映射，
不是官方规定。**把它当起点，用 §3 的收敛测试定你自己的数值。**

### 2.2 体系是**几维**的？（决定 k 点与真空层）

判据（可自查）：`validate.py` 会用"某方向晶格长度 − 该方向原子跨度"估计真空尺度，
输出 `XDIM.kpoints` 提示。**这个判据是启发式的**：

- `[经验]` 差 > 6 Å → 该方向像真空 → 该方向 k 点取 1。
- **反例**：倾斜晶胞、层间有真实相互作用的体系会误报。
  **必须自己确认该方向确实只有真空。**

### 2.3 体系含哪些元素？（决定赝势、`ENCUT`、`MAGMOM`、DFT+U）

三个直接后果：

1. **`ENCUT` 默认值 = 本套 `POTCAR` 里最大的 `ENMAX`**（见 §4）。
2. **有磁性元素 → 必须想清楚 `ISPIN`/`MAGMOM`**（见 §7）。
3. **有 3d/4f/5f 局域电子 → 要考虑 DFT+U**（见 §8）。

---

## §3 收敛测试总纲

### 3.1 必须做收敛测试的量，按优先级

| 优先级 | 量 | 典型判据 | 为什么 |
|---|---|---|---|
| **1** | `ENCUT` | 相邻截断能的总能量差 < **1 meV/atom** | 基组不完备会污染一切 |
| **2** | k 点密度 | 相邻网格的能量差 < **1 meV/atom** | 同上 |
| **3** | 真空层厚度（slab） | 再增加时**表面能/吸附能**变化 < 0.01 eV/Å² 或 < 10 meV | 周期性镜像相互作用 |
| **4** | slab 层数 | 再增加时**吸附能**变化 < 0.05 eV | 体相 vs 表面电子结构差异 |
| **5** | `SIGMA` | 只对金属/近简并体系重要 | 见 §6.3 |

`[经验]` "1 meV/atom" 是本 skill 采用的通用门槛，**不是官方数字**。
官方只在 `LREAL` 页提过 `an acceptable accuracy, e.g. 1 meV/atom`（那是关于 `ROPT` 的）。
`[官方]` `references/official/pages/LREAL.md`。

> ⚠️ **真实教训（本项目的）**：`validate.py` 早期版本把"`ENCUT` 低于 `ENMAX`"
> 一律报 ERROR，结果在真实算例 `ex8-NaHe2`（`ENCUT=520`，而 He 的 `ENMAX=2135 eV`）
> 上产生假阳性。原因是 **`ENMAX` 是孤立原子的推荐值**，对闭壳层 He 这类元素
> 几百 eV 往往就够。现在这条判据**分三档**报，并要求用户自己做测试。
> 详见 §4.3 与 `CHANGELOG.md` 的更正记录。

### 3.2 收敛测试怎么做（操作序列）

**单变量差分**：一次只动一个量，其余固定。

```
对 ENCUT ∈ {300, 350, 400, 450, 500, 550, 600}：
    用同一个 POSCAR/KPOINTS/POTCAR 跑单点（NSW=0, IBRION=-1）
    记下每个 OUTCAR 里的 energy(sigma->0)（见 §14.1）
    取 E(ENCUT)/N_atom，看相邻差值何时 < 1 meV/atom
```

**关键细节（不做会白跑）**：

1. **必须是单点**：`NSW=0`、`IBRION=-1`。做弛豫再比能量是无效的 ——
   几何变了，能量差里混进了结构弛豫的贡献。`[官方]` `NSW=0` 表示只做单点。
2. **同一套 `POTCAR`**：换赝势等于换了基组，`ENCUT` 的收敛值不可比。
3. **读 `energy(sigma->0)`，不要读 `free energy TOTEN`**（见 §14.1）。
4. **k 点与 `ENCUT` 要交替收敛**：先用粗 k 点定 `ENCUT`，再用定好的 `ENCUT` 定 k 点，
   必要时再回头复核 `ENCUT`。一次定死一个通常够用。
5. **`[经验]` 别只扫一个区间就下结论**：能量差**不是单调下降**的（平面波基组随
   `ENCUT` 离散变化）。要在目标值**两侧**各取一两个点确认已经进入平台。

---

## §4 `ENCUT` 怎么定

### 4.1 默认值从哪来（**硬规则**）

`[官方]` `references/official/pages/POTCAR.md`：

> `These two tags are default plane-wave cutoffs for the pseudopotential in
> electron Volt (eV). ENMIN is the minimum viable, end ENMAX the recommended cutoff.
> For POTCAR files with more than one species, the maximum cutoffs (ENMAX or ENMIN)
> are used for the calculation. Note that the INCAR tag ENCUT overwrites the
> default from the POTCAR.`

⇒ **`ENCUT` 不给时，VASP 自动取本套 `POTCAR` 里所有元素的 `ENMAX` 的最大值。**

官方同时建议：`We recommend setting the ENCUT tag in the INCAR file.`（`[官方]`）

### 4.2 决策条目

> **遇到**「任何生产计算」→ **选「显式写 `ENCUT`，并自己做收敛测试」，
> 而不要照搬某个"倍数规则"**
>
> **因为**（这一条是**官方明文**，比任何倍数都重要）：
> `references/official/pages/PREC.md` 原文：
>
> > `We strongly recommend specifying the energy cutoff ENCUT always manually
> > in the INCAR file to ensure the same accuracy between calculations.
> > Otherwise, the default ENCUT may differ among the different calculations
> > (e.g., for the calculation of the cohesive energy), with the consequence
> > that the total energies, for instance, can not be compared.`
> >
> > `Setting PREC=Accurate does not necessarily mean that the results are
> > converged. The convergence of the results with respect to the energy cutoff
> > ENCUT has to be checked separately.`
>
> 也就是说：**官方要求"显式写 + 单独测收敛"** —— 这是**唯一**的普遍要求。
> 但**官方在特定场景下确实给过倍数**，见下一段（本项目为此返工过一次）。

> **⚠️⚠️ 一个本项目自己写错过、又订正回来的说法（CR-002 → CR-026）**
>
> **先说结论（三句话）**：
> 1. **`ENCUT = 1.3 × max(ENMAX)` 确实是官方明文写过的值** ——
>    写在 `[官方]` **`references/official/pages/ISIF.md` 第 38 行**，
>    语境是"**做体积变化/变胞计算**"；
> 2. 它**不是**"所有计算的通用推荐值"；
> 3. 被官方标为 `deprecated` 的是 **`PREC=High` 这个开关**，
>    **不是** 1.3 这个倍数。
>
> **官方 `ISIF` 页原文**（`[官方]` `pages/ISIF.md:38`，本仓库已镜像、可 grep）：
>
> > `The PAW basis for the electronic minimization is not adjusted when the
> > structure is varied during a calculation. Therefore, carefully consider
> > effects such as Pulay stress and choose generous settings for the electronic
> > minimization. Generally, volume changes should be done only with an increased
> > energy cutoff, e.g., ENCUT = 1.3×max(ENMAX), and PREC=High.`
>
> 注意它的**逻辑链**：变胞时 PAW 基组**不跟着变** ⇒ 有 **Pulay 应力** ⇒
> 所以官方要你**保守地把截断能抬高**。这**才是 1.3 倍的由来** ——
> 它是**针对 Pulay 应力的对策**，不是"精度越高越好"的意思。
>
> **`PREC` 页怎么说 1.3 倍**（`[官方]` `pages/PREC.md`）：
> 默认值表里 `High` 那一行确实对应 `1.3×max(ENMAX)`，
> 而且同页有一段解释它**其实等价于"手工把 `ENCUT` 提高 30%"**：
> `Essentially, PREC=High only increases the energy cutoff by 30 %, which can
> also be achieved by just manually increasing ENCUT.`
> ⇒ 所以现在推荐的做法是：**别用 `PREC=High`（它已弃用），
> 直接手工把 `ENCUT` 写成 1.3×`max(ENMAX)`。**
> 两件事**效果相同**，但后者**显式、可复现、不依赖弃用开关**。
>
> **⚠️ 本项目在此处的两次错误（如实记录）**：
>
> | 版本 | 当时写的 | 错在哪 |
> |---|---|---|
> | 最初 | "`1.3×` 是官方建议的常用做法"（**归因给讲义**） | 归因错了：它不是讲义的说法，是**官方 `ISIF` 页**的说法 |
> | CR-002 之后 | "官方**从来没有说过**取 `ENMAX` 的多少倍；`1.3×` 只是已弃用 `PREC=High` 的行为" | **断言过强** —— 当时只检索了 `ENCUT.md` / `PREC.md`，**漏了 `ISIF.md`** |
> | **现在** | 见上：官方**在变胞语境下明文给过** 1.3×；被弃用的是 `PREC=High` 开关 | —— |
>
> **这次错误的教训**（已进 `MAINTENANCE.md` §6"搜不到 ≠ 不存在"）：
> > **"官方没说过 X"是一个很强的断言，它要求你检索过整个官方层。**
> > 只查了两三个"看起来相关"的页面就下这个结论，是把"我没找到"
> > 说成了"它不存在" —— 而本项目为此**把一个正确的做法改成了错误的**。
> > 正确写法是：「在 `ENCUT.md`/`PREC.md` 里**未见到**倍数推荐
> > （检索式：…，范围：…）」，而不是「官方**从来没有**说过」。
>
> **代价与正确的做法**：
> - 变胞（`ISIF=3`/`7`/`8`，或 `PSTRESS`）⇒ **按官方抬高 `ENCUT`**
>   （`1.3×max(ENMAX)` 是官方给的例子），**并显式写**；
> - 定胞计算（`ISIF=2`、单点、slab 弛豫）⇒ **用 `max(ENMAX)` 就够**，
>   没有必要一律乘 1.3（乘了只是多花机时，不会错）；
> - **无论哪种，`ENCUT` 收敛都必须按 §3.2 单独测** —— 官方对这点没有例外。
> - 真实算例佐证（`[算例]`）：`day1/fe2o3` 是 **`ISIF=3`** 的变胞优化，
>   `ENCUT = 520` 恰为 O 的 `ENMAX = 400.000` 的 **1.3 倍** ——
>   **现在这条终于有了正确的解释**（它是在做变胞）；
>   而 `day2/Ag`（定胞）用 400、`day1/mos2` 用 500，都不乘 1.3。
>
> **证据**：`[官方]` `references/official/pages/ISIF.md:38`（1.3× + `PREC=High`
> 的原文与 Pulay 应力语境）；`[官方]` `references/official/pages/PREC.md`
> （默认值表 + `deprecated` 提示 + "等价于手工提高 30%"）；
> `[官方]` `references/official/pages/ENCUT.md:16-17`
> （`The convergence … should always be checked` + 强建议显式写）；
> `[官方]` `references/official/pages/PSTRESS.md:16-17`
> （Pulay 应力怎么算、怎么用 `PSTRESS` 补）；
> `[LVTHW]` `EX36:99`（转录了同一句官方原文 —— 独立佐证）；
> `[算例]` `day1/fe2o3`（1.3 倍 + `ISIF=3`）。
> **订正记录**：CR-002（第一次改）与 **CR-026**（第二次改 —— 把过强的断言改回来）。

### 4.3 ⚠️ 反例与例外（**这条比上面的推荐值重要**）

> **遇到**「`POTCAR` 里有 `ENMAX` 异常高的元素（> 1000 eV）」→ **不要机械照搬 `ENMAX`**
>
> **因为**：`ENMAX` 是**孤立原子**的推荐值。实测反例：真实算例
> `3-electronicStructure/ex8-NaHe2` 用 `ENCUT = 520`，而 Na₂He 的 `POTCAR` 里
> He 的 `ENMAX = 2135.871 eV`（`[算例]`）。若按"必须 ≥ `ENMAX`"执行，
> 这个算例会需要 2000+ eV —— 实际上 He 是闭壳层、几乎不参与成键，
> **几百 eV 就够了**。这类元素还包括 Ne、以及某些带半芯态的 `_pv`/`_d` 赝势。
>
> **代价 / 怎么判**：本 skill **没有**一条"哪些元素的 `ENMAX` 可以打折"的规则，
> 因为这依赖具体赝势与体系。**唯一可靠的办法是自己做 §3.2 的收敛测试。**
> 本 skill 的 `validate.py` 对这种情况只报 `WARN` 并明确写出"这是经验设定，不是官方判据"。
>
> **证据**：`[算例]` `ex8-NaHe2`；`[官方]` POTCAR 页的 `ENMAX`/`ENMIN` 定义；
> ⚠️ 分档阈值 1000 eV 是 `[经验]` 设定，非官方。

> **遇到**「`INCAR` 里没写 `ENCUT`」→ **`validate.py` 会报 `WARN`，请照它说的做**
>
> **因为**：不写虽然合法（用 `POTCAR` 默认），但**可复现性挂在"你没动过 POTCAR"上**。
> `validate.py` 会从你的 `POTCAR` 读出实际的 `max(ENMAX)` 并显示出来。
>
> **代价**：写出来要多维护一个数字（换赝势时要同步改）。这是值得的。
>
> **证据**：`[官方]` POTCAR 页的 Tip。

---

## §5 k 点怎么定

### 5.1 网格数之间的比例（**硬规则**）

`[官方]` `references/official/pages/KPOINTS.md`：

> `N₁ : N₂ : N₃ ≈ |b₁| : |b₂| : |b₃|`

即**沿每个倒格矢方向的细分数与该方向倒格矢长度成正比**。
对（近）正交晶胞，这等价于 `N₁ : N₂ : N₃ ≈ 1/|a₁| : 1/|a₂| : 1/|a₃|`。

⚠️ **官方特别指出**：`the reciprocal lattice vectors do not in general align
with lattice vectors`，且 `1/|a|` 与 `|b|` 这两种取法**在某些 Bravais 格上不兼容**。

### 5.2 决策条目

> **遇到**「生产计算的规则网格」→ **选 Γ 居中（第 3 行写 `Gamma`），网格按 §5.1 的比例**
>
> **因为**：官方把规则网格列为
> `It offers sufficient flexibility and stability and should be preferred for
> most production calculations.` 而 Γ 居中在**所有** Bravais 格上都安全（见 §5.3）。
>
> **代价**：官方指出 `Monkhorst-Pack meshes may converge faster than the
> Γ-centered ones.` —— 即 MP 可能用更少的点达到同样精度。
> 但 MP 有对称性陷阱（§5.3），**省下的机时通常不值得冒那个风险**。
>
> **证据**：`[官方]` KPOINTS 页。

### 5.3 ⚠️ **Monkhorst-Pack 的对称性陷阱**（很重要，容易被忽略）

`[官方]` KPOINTS 页原文：

> `To enable an efficient symmetry reduction, the (shifted) regular mesh of
> k points should conserve the point-group symmetry of the reciprocal lattice.
> Specifically, the generating lattice (g_i = k_i/N_i) should belong to the same
> class of Bravais lattice as the reciprocal lattice.`
>
> `Consequently, refrain from using a shifted regular mesh for some Bravais
> lattices, see table. Importantly, this includes the **default Monkhorst-Pack
> mesh for even numbers of subdivisions**.`

**官方给出的结论（直接可抄）**：

- **fcc、hexagonal、fcc-orthorhombic 晶格：只用 Γ 居中。**
- body-centered tetragonal / body-centered orthorhombic：
  用 `N₁:N₂:N₃ = 1/|a₁| : 1/|a₂| : 1/|a₃|`，
  ⚠️ **`KSPACING` 用的是倒格矢，对这些对称性可能不适用**。
- face-centered orthorhombic：用 `N₁:N₂:N₃ = |b₁| : |b₂| : |b₃|`。
- 其他对称性：各种组合都行，但换个细分数或网格可能解决报错。

**报错形态**：`VASP issues an error when it detects an incompatible k-point mesh.
... includes the name of the routine IBZKPT, some warning about the generating
k-lattice, and some suggestions to overcome the problem.` `[官方]`

> ⇒ **判据**：看到报错里出现 `IBZKPT` 与 `generating k-lattice`，
> **先怀疑网格中心选错了**，而不是先怀疑结构或赝势。

### 5.4 密度定多少

官方给的**自动模式的量级**（`[官方]` KPOINTS 页）：

> `Useful values for the length vary between R_k = 10 (large gap insulators)
> and R_k = 100 (d metals).`

⇒ 从大能隙绝缘体到 d 金属，**采样密度可以差 10 倍**。这与 §6 的展宽选择是同一件事的两面：
**金属需要更密的 k 点**。

**真实算例里用的值**（`[算例]`，可作为起步参考，**不是判据**）：

| 体系 | `KPOINTS` 网格 | `KP-Resolved Value` |
|---|---|---|
| `day1/fe2o3`（Fe₄O₆ 胞） | Γ `6 6 6` | 0.040 |
| `day1/mos2`、`day1/vdw-df2`（二维） | Γ `9 9 1` | 0.040 |
| `day2/Ag`、`day2/au111-opt`（Au/Ag slab） | Γ `5 5 1` | 0.040 |
| `day2/al2o3`（Al₂O₃ 胞） | Γ `9 9 5` | 0.040 |
| `day2/c`（石墨烯条带） | Γ `1 5 1` | 0.040 |
| `day2/mos2ws2`（异质结，96 原子） | Γ `1 4 1` | 0.040 |
| `day2/ni-co`（Ni slab + CO） | Γ `3 3 1` | 0.040 |
| `6-electronic/oer/slab`（CoN₄） | Γ `2 2 1` | — |

**观察到的规律**：这些 `KPOINTS` 都由工具生成，第一行注释是
`KPT-Resolved Value to Generate K-Mesh: <R>`，且**真空方向的网格数一律是 1**。

> ⚠️ **`KP-Resolved Value` 的单位是 `[待核对]`。**
> 我们检索到 vaspkit 手册称其单位为 `2π/Å`，但**按该单位反推这些算例的网格并不自洽**，
> 所以本文件**不采信、也不给换算公式**，只如实报告"这些算例写的是 0.040/0.050"这个事实。
> **要自己定密度，请用 §3.2 的收敛测试**，不要依赖这个数的单位。

---

## §6 展宽 `ISMEAR`/`SIGMA` 怎么选

### 6.1 官方取值（**硬规则**）

`[官方]` `references/official/pages/ISMEAR.md`，默认值 `ISMEAR = 1`：

| 取值 | 含义 |
|---|---|
| `>0` | Methfessel-Paxton，阶数 = `ISMEAR`，宽度 `SIGMA` |
| `0` | Gaussian 展宽，宽度 `SIGMA` |
| `-1` | Fermi 展宽，宽度 `SIGMA` |
| `-2` | 从 `WAVECAR` 读部分占据并固定（或用 `FERWE`/`FERDO` 指定） |
| `-3` | 对 `INCAR` 里 `SMEARINGS` 给的参数做循环 |
| `-4` | 四面体方法，**无展宽** |
| `-5` | 四面体方法 + Blöchl 修正，**无展宽** |
| `-14` | 四面体方法 + Fermi-Dirac 展宽（`SIGMA`） |
| `-15` | 四面体方法 + Blöchl 修正 + Fermi-Dirac 展宽（`SIGMA`） |

**两条官方注意事项（必须遵守）**：

1. `ISMEAR > 0`（Methfessel-Paxton）：
   `can yield erroneous results for insulators because the partial occupancies
   can be unphysical.` ⇒ **绝缘体不要用 MP**。
2. 四面体方法（`-4`/`-5`/`-14`/`-15`）：
   `Use a Γ-centered k-mesh for the tetrahedron methods.` ⇒ **必须 Γ 居中**。

`SIGMA` 默认值 `0.2` eV（`[官方]` `pages/SIGMA.md`）。

### 6.1b ⭐ 官方有一张专门的 how-to 页 —— **它是本节最权威的来源**

`[官方]` `references/official/pages/Smearing_technique.md`
（标题 *Smearing technique*，官方 `Howto` 分类）。
**它给出了 `ISMEAR` 标签页里没有的判据**，本 skill 早期版本漏了它
（抓取时按分类枚举，而这页不在标签分类里 —— 见 `_fetch_named.py` 的说明）。

**按体系类型的官方建议（原文可核）**：

| 体系 | 官方建议 |
|---|---|
| **不知道是什么体系 / 高通量** | `ISMEAR = 0`（Gaussian）+ `SIGMA = 0.03–0.1`；可再把 `EFERMI = MIDGAP` |
| **半导体 / 绝缘体** | 可用四面体 `ISMEAR = -5`，**前提是有 ≥ 4 个 k 点构成四面体**；这样**不必**收敛 `SIGMA` |
| **金属（做弛豫）** | `ISMEAR = 1` 或 `2`，`SIGMA` 取到**熵项 `T×S` < 1 meV/atom**；官方说默认的 `0.2` **通常**是合理选择 |
| **金属（DOS / 极精确总能量，不弛豫）** | 四面体 `ISMEAR = -5` |

> ⇒ **`SIGMA` 终于有了官方给出的可执行判据**（本 skill 之前只有 `[经验]`）：
> **金属看 `OUTCAR` 里的熵项 `T×S`（`entropy T*S`），要求 < 1 meV/atom。**
> 这比"把 `SIGMA` 减半看能量差变多少"更直接 —— 它**已经在输出里**。

**三条容易忽略、但官方明文写着的**：

1. ⚠️ **力与应力是与"自由能"一致的，不是与 `energy(σ→0)` 一致的。**
   原文：`The forces and stress are consistent with the free energy and not with
   the extrapolated energy SIGMA→0 so make sure that forces and stress are
   converged with respect to SIGMA`。
   ⇒ 这解释了两件事：
   - 为什么 §14.1 说"报能量用 `energy(sigma->0)`"（**对能量是对的**）；
   - 但**做几何优化/算力时，要盯的是 `SIGMA` 本身收敛**，不能只看那个外推值。

2. ⚠️ **四面体方法的力可能错 5–10%（对金属）。**
   原文：`the calculated forces and the stress tensor can be wrong by up to 5 to
   10% for metals. Only for semiconductors and insulators, the forces are correct
   because the partial occupancies do not vary and are either zero or one.`
   ⇒ 这是 §6.2「四面体不适合金属弛豫」那条的**官方依据**（之前只有课程口径）。

3. ⚠️ **`EFERMI`（费米能）在绝缘体/半导体里不唯一，而且依赖 `NEDOS`。**
   原文：`In insulators and semiconductors, this choice is not unique if SIGMA is
   much smaller than the gap`；以及 `This method is not deterministic, i.e.,
   changes to the number of points for the density of states NEDOS can lead to
   different values.`
   ⇒ 若你的结论依赖"绝对费米能级"，**必须显式设 `EFERMI`**，否则改 `NEDOS`
   就可能改数 —— 这是一条**无报错**的不确定性。

4. `[官方]` 还给了一个**效率工具**：`ISMEAR = -3` 会对 `INCAR` 里
   `SMEARINGS` 给定的多组参数**做一次循环扫描** ——
   用来扫 `SIGMA` 比手工建多个目录省事。

> ⚠️ **一个官方没写、只能靠报错原文确认的阈值：四面体方法的最少 k 点数。
> 现在它被官方页面解决了** ——
> 官方 *Smearing technique* 页明确写：**`at least 4 k points to form a
> tetrahedron`**。
>
> 于是之前那处"3 还是 4"的分歧**有了裁定依据**：
>
> | 出处 | 说的阈值 | 裁定 |
> |---|---|---|
> | `[官方]` *Smearing technique* 页 | **≥ 4** | ✅ **以它为准** |
> | `[讲义]` L2（报错速查行） | `NKPT < 4` | ✅ 与官方一致 |
> | `[LVTHW]` `EX01:148` | "小于 3 时罢工" | ⚠️ 与官方**不一致**，见下 |
>
> **但要注意"4 个 k 点"与"`NKPT<4`"说的可能不是同一件事**：
> 官方那句是在讲**能不能构成四面体**（4 个顶点 ⇒ 需要 4 个 k 点），
> 而程序报错里的 `NKPT` 指的是**不可约 k 点数**。
> ⇒ 实践上仍以**程序自己报的原文**为准（它会把实际阈值与你的 `NKPT` 一起打出来）。
>
> `[待核对]`：本 skill 现有资料**没有**任何一次可复现的真实报错记录
> （在 `things to study/` 的 98 个算例里搜不到这条报错），
> 所以**程序侧的精确阈值仍未经本项目实测**。要落实它，需要一次
> **带真实 `OUTCAR` 的复现** —— 见 `conformance/README.md` 的"你可以怎么帮忙"。

### 6.2 决策条目

> **遇到**「绝缘体 / 半导体 / 分子」→ **选 `ISMEAR = 0`，`SIGMA = 0.01–0.05`**
>
> **因为**：Gaussian 展宽对这些体系安全；MP 会产生**非物理的部分占据**（官方明说）。
> 真实算例里 `day1/fe2o3`（Fe₂O₃，带隙体系）用 `ISMEAR=0, SIGMA=0.05`；
> `vaspsol-H2O`（水分子）用 `ISMEAR=0, SIGMA=0.01`。`[算例]`
>
> **代价**：`SIGMA` 越小，SCF 收敛越难（尤其金属性体系）。
> 绝缘体通常没问题；一旦收敛困难，先查是不是其实有金属性。
>
> **证据**：`[官方]` ISMEAR/SIGMA；`[算例]` 上述两个目录。

> **遇到**「金属 / 需要弛豫的体系」→ **选 `ISMEAR = 1`（或 `0`），`SIGMA = 0.1–0.2`**
>
> **因为**：金属的 Fermi 面需要展宽来稳定占据数。真实算例的用法**很一致**：
> `day2/Ag`、`day2/au111-opt`、`day2/ni-co`、`day3/ts/dim`、
> `4-thermo/7-2-adsorptionO-Au/hollow` **全部是 `ISMEAR = 1, SIGMA = 0.2`**（`[算例]`）。
> 讲义口径与此一致（`[讲义]` L1/L2 关于金属体系的部分）。
>
> **代价**：`ISMEAR=1` 是 MP 展宽，对绝缘体不安全（所以不能一套参数走天下）；
> `SIGMA` 越大，能量外推误差越大 —— **做能量差时要把 `SIGMA` 也纳入收敛测试**。
> `[经验]`
>
> **证据**：`[官方]` ISMEAR 页；`[算例]` 上述多个目录。

> **遇到**「要算 DOS / 需要精确的态密度」→ **选 `ISMEAR = -5`（四面体 + Blöchl），且 k 点必须 Γ 居中**
>
> **因为**：四面体方法没有展宽带来的谱展宽，最适合 DOS。
>
> **代价与反例**：
> - **必须是 Γ 居中网格**（官方明说）。
> - 四面体方法**对力的计算可能不稳定**，不适合做金属的 MD/弛豫。
> - ⚠️ **真实算例里有一个反面教材**：`day2/ni-co` 的 DOS 实际出自
>   `NSW = 300` 的**弛豫**计算（其 `OUTCAR` 里 `E-fermi` 出现 8 次 ⇒ 有 8 个离子步），
>   而讲义 P62 明确要求 DOS 那一步用 `NSW=0`（`[讲义]` L2 P62；`[算例]` `day2/ni-co/`）。
>   **弛豫过程中的 DOS 不是最终结构的 DOS。**
>
> **证据**：`[官方]` ISMEAR 页；`[讲义]` L2 P62；`[算例]` `day2/ni-co`。

### 6.3 一个容易忽略的判据

> **判据（自查）**：把 `SIGMA` 减半，重跑单点，看**你关心的那个能量差**变了多少。
> 若变化 > 你的误差预算（例如 10 meV），说明展宽还没收敛。
>
> **证据**：`[经验]`。官方没有给"`SIGMA` 收敛判据"的数字。

---

## §7 自旋：`ISPIN` / `MAGMOM`

### 7.1 硬规则

`[官方]` `references/official/pages/MAGMOM.md`：

1. **默认值**：`ISPIN=2` 时 `MAGMOM = NIONS * 1.0`；
   非共线（`LNONCOLLINEAR=.TRUE.`）时 `3 * NIONS * 1.0`。
2. **`MAGMOM` 会降低对称性**：
   `If the MAGMOM line breaks a symmetry of the crystal, the corresponding
   symmetry operation is removed`。
3. **从 `WAVECAR`/`CHGCAR` 续算时，`MAGMOM` 只用来定对称性，不再设初值**：
   `if you remove the MAGMOM tag before restarting from a converged WAVECAR or
   CHGCAR, the magnetization is likely to be symmetrized away.`
4. **重要**：`The final magnetic state strongly depends on the initial values
   for MAGMOM. This is true even if no symmetry is used (ISYM=-1), because of
   the many local minima that most exchange-correlation functionals have within
   spin-density-functional theory.`
5. **官方给的操作建议**：
   `we recommend setting the magnetic moments slightly larger than the expected
   values, e.g., using the experimental magnetic moment multiplied by 1.2-1.5.`

### 7.2 决策条目

> **遇到**「任何含磁性元素的体系」→ **选 `ISPIN = 2` + 显式写 `MAGMOM`，并按磁序分组**
>
> **因为**：
> - 官方第 4 条说明**最终磁态强依赖初值** —— 不写 `MAGMOM` 等于把结果交给默认值 `1.0`，
>   **同一个输入换个核数可能收敛到不同磁态**。`[官方]`
> - 真实算例的写法可直接参考：
>   - **反铁磁**（Fe₂O₃）：`MAGMOM = 5.0 -5.0 5.0 -5.0 6*0.0`（`[算例]` `day1/fe2o3/INCAR`）
>   - **单原子磁性中心**（CoN₄ 上的 Co）：
>     `MAGMOM = 32*0.0 2.0 0.0` —— 前 32 个原子（slab）设为 0，
>     第 33 个（Co）设 2.0，第 34 个（吸附的 O）设 0（`[算例]` `6-electronic/oer/o/freq/INCAR`）
>
> **代价**：
> - `MAGMOM` **按原子顺序**逐个给，个数必须等于 `POSCAR` 的原子总数。
>   个数不符时 VASP 的行为不直观，磁态会失控 → `validate.py` 会报 `XMAGMOM.count`。
> - 写出磁序会**按需打破对称性**（官方第 2 条），计算量上升。
> - **`[经验]` 一个必须做的动作**：算完后去 `OUTCAR` 里核对**每个离子的最终磁矩**，
>   而不是只看总磁矩。收敛到错误的磁态时总磁矩可能看起来"差不多"。
>
> **证据**：`[官方]` MAGMOM 页（含 1.2–1.5 倍的 Tip）；`[算例]` 上述两个 `INCAR`。

> **遇到**「非磁性体系 / 已确认无未配对电子」→ **选 `ISPIN = 1`**
>
> **因为**：`ISPIN=2` 会把计算量翻倍左右，且对闭壳层体系没有收益。
> 真实算例里 `al2o3`、`mos2`、`mos2ws2`、`c`、`vaspsol-H2O`（`ISPIN=1`）都是这样。`[算例]`
>
> **代价**：**判错就要重跑**。若不确定某个体系有没有磁性，
> **`[经验]` 先跑一次 `ISPIN=2` 看最终磁矩是否为零**，比先跑 `ISPIN=1` 再返工便宜。
> 特别地：**过渡金属氧化物、含 Fe/Co/Ni/Mn/Cr 的体系默认按有磁性处理**。
>
> **证据**：`[官方]` ISPIN 页；`[算例]` 上述目录。

---

## §8 DFT+U 怎么设

### 8.1 ⚠️ 最重要的一条：**两套写法差 1.1 eV，引用 U 值必须注明写法**

真实算例与讲义给出了**两套数值**：

| 来源 | `LDAUU` | `LDAUJ` | 有效 U（`U_eff = U − J`，Dudarev 型） |
|---|---|---|---|
| 讲师模板 `things to study/INCAR` | 4.6 | 0.4 | **4.2 eV** |
| 讲义正文 & 真实算例 `day1/fe2o3` | 5.3 | 0.0 | **5.3 eV** |

（`[算例]` `things to study/INCAR` 的 `#### DFT +U ####` 段；`things to study/day1/fe2o3/INCAR`；
`[讲义]` L1 关于 DFT+U 的页。两份精读报告均把这一条列为冲突项。）

> **遇到**「要在论文/报告里写 U 值」→ **必须同时写 `LDAUTYPE` 与 `U`/`J` 的分解方式**
>
> **因为**：`LDAUTYPE=2` 是 Dudarev 型，起作用的是 `U − J`。
> 只写"我用了 U = 5.3 eV"而不写 `J`，读者无法判断你实际用的是 5.3 还是 4.2。
> 两者相差 **1.1 eV**，足以改变结论。
>
> **代价**：多写几个字。不写的代价是**别人复现不出你的结果**。
>
> **证据**：`[算例]` 两份 `INCAR` 的对比；`[官方]` `pages/LDAUTYPE.md` 与 `pages/LDAUU.md`。

### 8.2 必配的参数（**硬规则**）

`[官方]` `references/official/pages/LMAXMIX.md`，默认值 `2`：

> `DFT+U calculations require, in many cases, an increase of LMAXMIX to 4 for
> d-electrons (or 6 for f-elements) to obtain fast convergence to the ground state.`
>
> `For the calculation of band structures within the DFT+U approach, it is
> strictly required to increase LMAXMIX to 4 for d-elements and to 6 for f-elements.`

⇒ **`[官方]` 硬规则**：
- DFT+U 含 **d 电子 → `LMAXMIX = 4`**；
- 含 **f 电子 → `LMAXMIX = 6`**；
- **用 `ICHARG=11` 做 DFT+U 的能带计算时，这一条是 `strictly required`**。

⚠️ 官方同页还警告：`When the CHGCAR file is read and kept fixed ... the results
will not necessarily be identical to a self-consistent run. The deviations will
be large for DFT+U calculations.` —— 即 **DFT+U 的 `ICHARG=11` 非自洽结果与自洽结果差别大**。

**其他必配**：`LDAU = .TRUE.`、`LDAUTYPE = 2`、`LDAUL`/`LDAUU`/`LDAUJ` 的**列表长度必须等于元素种类数**，
且**顺序与 `POSCAR` 的元素顺序一致**。

> **判据（自查）**：`validate.py` 的 `XLDau.count` 会核对列表长度与元素种类数。
> 长度不符时 VASP 会按默认值补齐 —— **U 就加到了错误的元素上，且不报错**。

---

## §9 几何优化参数

### 9.1 `IBRION` / `ISIF` / `NSW` / `POTIM` / `EDIFFG`

`[官方]` `references/official/pages/EDIFFG.md`（默认 `EDIFF × 10`）：

> `When EDIFFG is positive, the relaxation is stopped when the change of the
> total energy is smaller than EDIFFG between two ionic steps.`
> `When EDIFFG is negative, the relaxation is stopped when the norms of all the
> forces are smaller than |EDIFFG|. This is usually a more convenient setting.`
> `If EDIFFG = 0, the ionic relaxation is stopped after NSW steps.`
> ⚠️ `EDIFFG does not apply to molecular-dynamics simulations.`（官方 Warning）

`[官方]` `references/official/pages/POTIM.md`（默认值随 `IBRION` 变）：

| `IBRION` | `POTIM` 默认 | 含义 |
|---|---|---|
| `0` | **无（必须给）** | MD 时间步（fs）；不给会 `crash immediately after having started` |
| `1`,`2`,`3` | `0.5` | 离子弛豫的步宽缩放因子 |
| `5`,`6` | `0.015`（VASP.5.1 起） | 有限差分频率的**位移量（Å）** |

官方对 `IBRION=1/2/3` 的提示：`The quasi-Newton algorithm is especially
sensitive to the choice of this parameter.`

`[官方]` `POTIM.md` 还有一条 Warning：
`For VASP.5.1 and newer releases, POTIM is automatically reset to 0.015 Å,
if the supplied value for POTIM is unreasonably large.`
⇒ **`POTIM` 写得过大时会被程序静默改写** —— 你以为写了 1.0，实际用了 0.015。

### 9.2 决策条目

> **遇到**「表面/分子/常规几何优化」→ **选 `IBRION = 2`（CG）、`ISIF = 2`、`POTIM = 0.2`、力判据 `EDIFFG = -0.01`**
>
> **因为**：这是**这门课与真实算例的一致口径**。真实算例里
> `day1/fe2o3`、`day1/mos2`、`day2/Ag`、`day2/au111-opt`、`day2/ni-co`、
> `day2/mos2ws2`、`6-electronic/oer/slab` **全部是 `IBRION=2` + `POTIM=0.2`**
> （`[算例]`）；`EDIFFG = -0.01` 也是多数算例的值。
>
> **代价**：
> - 官方页说 `IBRION=1 (RMM-DISS) is faster`（`[官方]` `pages/INCAR.md` 的示例注释），
>   即 **CG 不是最快的**；但 CG 更稳，是安全的起点。
> - `POTIM = 0.2` 偏保守。`[经验]` 结构离平衡很远时收敛慢，可先做几步
>   `IBRION=1`/`ISIF=2` 或调大 `POTIM`，但官方提醒准牛顿算法对 `POTIM` 特别敏感。
> - **`EDIFFG = -0.01 eV/Å` 对过渡态与频率不够严**，见 §12/§13。
>
> **证据**：`[官方]` POTIM/EDIFFG/INCAR 页；`[算例]` 上述目录。

> **遇到**「**二维材料**的面内晶胞优化」→ **选 `ISIF = 3` + 冻结真空方向**
>
> **因为**：`ISIF = 3` 会同时优化晶胞形状与体积。对 slab/二维材料，
> **真空方向也会被优化**，结果是真空层塌陷（层间出现虚假相互作用）。
> 真实算例 `day1/mos2`、`day1/vdw-df2`、`day2/mos2ws2` 用了一个 `OPTCELL` 文件
> 来控制哪些方向允许变化（`[算例]`）。
>
> **代价 / 陷阱**：
> - ⚠️ **`OPTCELL` 不在 `OUTCAR` 里回显**（`[实测]`：在真实算例的 `OUTCAR` 里搜不到它）。
>   也就是说 **程序不会告诉你它有没有生效**。唯一可核对的办法是
>   **比对优化前后的 `POSCAR` 与 `CONTCAR` 的晶格**：
>   允许变化的方向长度该变，被冻结的方向应该**逐位保持不变**。
>   （`[实测]` `day1/mos2`：面内 a 由 3.166 → 3.182，
>   而 c 严格保持 18.4099998474 不变。）
> - `OPTCELL` 是 **vaspkit 的工具约定**，不是 VASP 原生标签 → 它**不在**官方关键字表里。
>   若你用的是别的流程，等价做法是**手动从 `CONTCAR` 里把真空方向改回原值**再续算。
> - `[经验]` 若真空层足够厚（≥ 15 Å），真空方向的优化幅度通常很小，
>   有时不改也能接受 —— 但**这需要你自己验证**，不要假设。
>
> **证据**：`[算例]` `day1/mos2/OPTCELL`、`day1/vdw-df2/OPTCELL`、`day2/mos2ws2/OPTCELL`
> 与各自的 `POSCAR`/`CONTCAR` 对比；`[实测]` 上述比对结果。

---

## §10 二维材料与 vdW

### 10.1 vdW 修正：两条路线

| 路线 | 怎么写 | 真实算例 |
|---|---|---|
| **D3 类经验修正** | `IVDW = 11`（D3）或 `12`（D3-BJ） | 答疑里讲师说"两个差不多都可以用，11 是 D3（有时候低估 vdW），12 是 D3BJ（有时候高估 vdW）"（`[答疑]` D1-P6） |
| **非局域泛函** | `LUSE_VDW = .TRUE.` + `ZAB_VDW`（+`AGGAC`/`BPARAM`） | `day1/vdw-df2`：`GGA = ML` + `LUSE_VDW = .TRUE.` + `ZAB_VDW = -1.8867` + `AGGAC = 0.0000`（即 vdW-DF2）（`[算例]`） |

> **遇到**「层间/分子间以范德华为主，且你要报能量差」→ **选哪种取决于你要跟谁比**
>
> **因为**：
> - `IVDW` 是**经验修正**，便宜、易用，但绝对值取决于参数化。
> - vdW-DF 系列是**自洽的非局域泛函**，物理上更完整，但要额外指定核函数（`ZAB_VDW`）。
> - `[答疑]` 里讲师的口径很务实：**D3 与 D3-BJ 各有偏高偏低**，
>   没有"哪个更对"的绝对答案（D1-P6）。
>
> **代价**：
> - 换 vdW 方法会**系统性改变能量差**，因此**同一篇工作里必须固定一种**。
> - ⚠️ **本 skill 不替你选核函数**。`ZAB_VDW` 的取值含义、`AGGAC`/`BPARAM` 的物理意义，
>   本文件**没有**从官方资料中核实到完整的对应表 → 标 `[待核对]`。
>   **请以 `references/official/pages/` 下的页面与你自己的文献依据为准。**
> - `validate.py` 的 `INCAR.pair` 规则会提醒"开了 `LUSE_VDW` 但没给 `ZAB_VDW`"。
>
> **证据**：`[答疑]` D1-P6；`[算例]` `day1/vdw-df2/INCAR`。

### 10.2 二维材料的真空方向

见 §9.2 的 `OPTCELL` 条目。补充一条数值参考：

`[算例]` 里二维/表面体系的真空层厚度（由 `POSCAR` 与原子跨度反推）：
`day1/mos2` ≈ 15.24 Å · `day2/Ag` ≈ 15.0 Å · `day2/au111-opt` ≈ 13.5 Å ·
`day2/ni-co` ≈ **7.4 Å**（明显偏小）。

> **判据**：**没有"标准真空层厚度"这个数字。** 正确做法是 §3.1 的第 3 项 ——
> 逐步加厚真空层，直到你关心的量（表面能/吸附能/功函数）不再变化。
> `ni-co` 的 7.4 Å 是个提醒：**真实算例里也有偏小的值**，不要把它当基准抄。

---

## §11 slab 建模

### 11.1 固定策略（Selective dynamics）

**做法**：在 `POSCAR` 里加 `Selective dynamics` 行，然后每个原子后跟 3 个 `T`/`F`。

- `T` = 该方向放开，`F` = 冻结。
- 这是**仅影响弛豫/MD 的标志**；对静态单点计算没有影响。
- `[官方]` `pages/POSCAR.md`。

**真实算例的用法**（`[算例]`）：
- `day2/Ag`、`day2/au111-opt`、`4-thermo/7-2-adsorptionO-Au/hollow`：
  底层固定 `F F F`，表层与吸附物放开。
- `6-electronic/oer/{o,oh,ooh}/freq`：**31 个 slab 原子全部 `F F F`**，
  只让吸附物 `T T T` —— 这是为了 §13 的"只算吸附物的频率"。

> **遇到**「表面吸附能计算」→ **选"固定底部 2–3 层，放开表层 + 吸附物"**
>
> **因为**：全部放开会让 slab 整体弛豫（表面能贡献混进吸附能）；
> 全部固定则无法描述吸附引起的表面重构。
>
> **代价**：固定层数是一个**要收敛的量**（§3.1 第 4 项）。
> `[经验]` 常见做法是固定 2–3 层，但**层数够不够要自己测**：
> 加一层，看吸附能变多少。
>
> **证据**：`[官方]` POSCAR 页；`[算例]` 上述目录。

### 11.2 赝氢钝化（**有精确的可复查判据**）

> **遇到**「slab 底面有悬挂键，需要钝化」→ **选"把赝氢放在被删除原子的**键中点**，并固定它"**
>
> **因为**：这是本课程讲义的做法，而且**真实算例给出了可逐位核对的证据**：
> `day1/GaN` 的 `POSCAR` 里 H 到 N 的距离 = **0.9865 Å**，
> 而 Ga–N 键长 = **1.9742 Å** —— **H 恰好在中点**（与中点差 0.0006 Å），
> 且 H 标为 `F F F`（固定）。该算例真空层恰为 **15.0000 Å**。（`[实测]`）
>
> **代价**：
> - 赝氢的质量/电子数会影响总能量，**作差时要保证所有对比体系用了同样的钝化方案**。
> - `[答疑]` 里讲师提到：`Gamma-Al2O3` 要钝化，其他看相似文献可能不需要（D1-P16）。
>   ⇒ **是否需要钝化取决于体系与文献惯例**，不是一律要。
> - ⚠️ 真实算例 `day1/GaN` 用的赝势是 **`H.75`**（分数占据，`ZVAL = 0.75`，`[算例]`）。
>   这是一个**特殊的赝氢**，不是普通的 H。用它时 `ENCUT` 等参数要重新核对。
>
> **判据（自查）**：
> 1. 量 `H` 到"被它饱和的那个原子"的距离，应约等于**原键长的一半**；
> 2. 确认 `Selective dynamics` 里赝氢是 `F F F`；
> 3. 确认真空层没被钝化氢吃掉（加氢后真空层应基本不变）。
>
> **证据**：`[实测]` `day1/GaN/POSCAR` 的坐标与键长计算；`[讲义]` L1 关于钝化的页；
> `[答疑]` D1-P15/P16。

---

## §12 过渡态搜索

### 12.1 四种方法的定位

| 方法 | 关键标签 | 什么时候用 | 代价 |
|---|---|---|---|
| **NEB / CI-NEB** | `IMAGES`, `LCLIMB`, `SPRING`, `ICHAIN` | 知道初态与末态，要整条路径 | 计算量 ≈ `IMAGES` 倍单点（见下方更正） |
| **Dimer** | `ICHAIN = 2`, `IBRION = 3`, `POTIM = 0` | 只知道初态 + 一个粗略方向 | 便宜，但**只有一个鞍点**、易爬错 |
| **Improved Dimer** | `IBRION = 44`（**VASP 原生**）；老 VTST 口径 `ICHAIN = 3` + `IBRION = 3` | 同上，对曲率估计更稳 | 同上 |
| **约束优化 / 扫描** | — | 只要一个粗略的能垒 | 便宜，但**不是真鞍点** |

> ⚠️ **`ICHAIN`/`IOPT`/`LCLIMB` 不在官方 wiki 的 `Category:INCAR_tag` 里**
> （`[实测]`：用 wiki API 逐页查证，这三个标签**没有独立页面**）。
> 它们是 VASP 的核心过渡态标签，见 `references/official/` 里的相关页面与官方
> `Nudged elastic bands` how-to 页（`pages/Nudged_elastic_bands.md`）。
> **本文件里的用法来自真实算例，标 `[算例]`。**
>
> 真实算例用法（`[算例]`）：
> - **Dimer**：`day3/ts/dim/INCAR` 与 `5-ts/8-1-ex1-O-Au/ts-dimer/INCAR`：
>   `IBRION = 3`、`POTIM = 0`、`ICHAIN = 2`、`IOPT = 2`（CG 优化器），配 `MODECAR`。
> - **CI-NEB**：`5-ts/8-1-ex1-O-Au/ts-cineb/` 与
>   `5-ts/8-1-ex2c6h12ptgraphene/c6h12ptgraphene/`：
>   `ICHAIN`、`LCLIMB`、`IOPT` 三个标签一起出现。

> ✅ **更正：Improved Dimer 是 VASP 原生的 `IBRION = 44`，不需要编 VTST。**
>
> `[官方]` `references/official/pages/IBRION.md` 的取值表里有 `44`
> （Improved Dimer method）。`[LVTHW]` `A32` 整篇讲的就是这个：
> 用它算过渡态**不必**先编 VTST。
>
> 本项目早期只记了老 VTST 口径的 `ICHAIN = 3` + `IBRION = 3`。
> **两条路线并存**：
>
> | 路线 | 怎么写 | 前提 |
> |---|---|---|
> | **VASP 原生 IDM** | `IBRION = 44` | 无需额外编译（VASP 版本要够新） |
> | VTST 的 Dimer/IDM | `ICHAIN = 3` + `IBRION = 3` + `IOPT` | 需要 VTST 版 VASP |
>
> **怎么选**：能用 `IBRION = 44` 就用它（少一层依赖）。
> ⚠️ `[待核对]`：本项目**没有**在真机上比较过两条路线的差异，
> 也没有算例可核对（现有 98 个算例里 `IBRION = 44` **零出现**）。
>
> **订正记录**：`CHANGELOG.md` CR-033。

> ✅ **更正：NEB 的计算量是 `IMAGES` 倍单点，不是 `(IMAGES+2)` 倍。**
>
> `[官方]` `references/official/pages/Nudged_elastic_bands.md:10,18` 原文：
>
> > `For n IMAGES, create (n + 2) subdirectories and label them with their
> > index starting from 0.`
> > `Place the POSCAR file of the initial state in 00 and POSCAR file of the
> > final state in the last directory (04 in the example).`
>
> ⇒ **要建 `n+2` 个目录，但 `IMAGES = n` 才是实际并行运行的反应像数**；
> `00` 与末尾那个目录只放**端点 `POSCAR`**（它们由你事先优化好，不参与 NEB 弛豫）。
> 所以**运行开销 ≈ `IMAGES` 倍单点**。
>
> ⚠️ 但**总工作量**还要加上**两个端点的优化**（初态、末态各一次弛豫）。
> 本项目早期的 `(IMAGES+2)` 是把"目录数"当成了"计算量" —— 偏保守，
> 不算错，但**会让你误以为 NEB 比实际贵**。
>
> **订正记录**：`CHANGELOG.md` CR-033。
> （指出这条的是 G6 精读员；它当时归因给了 `VCAIMAGES.md`，
> 那条**归因不对** —— `VCAIMAGES` 讲的是热力学积分，与 NEB 无关。
> 官方依据在 `Nudged_elastic_bands.md`。**归因错与结论错是两件事**：
> 结论经核实**成立**，归因已改。）

### 12.2 决策条目

> **遇到**「能垒要进论文 / 要报过渡态结构」→ **选 CI-NEB（`LCLIMB = .TRUE.`）**
>
> **因为**：CI-NEB 让最高能量的像爬到鞍点（climbing image），
> 是**唯一能给出真实鞍点**的常用路线；Dimer 也能，但对初始方向敏感。
>
> **代价**：
> - 计算量是 `(IMAGES+2)` 倍单点，且要**所有像同时收敛**才结束。
> - ⚠️ `LCLIMB` 会改变最高像的受力方式，**必须在路径大致收敛后再打开**
>   （先用普通 NEB 插值收敛，再开 `LCLIMB` 精修）。
>   `[经验]` / `[待核对]` —— 这一条本 skill **没有**从官方资料核实到明文，
>   是按 CI-NEB 方法的通用做法写的。
>
> **证据**：`[算例]` `5-ts/` 目录；`[讲义]` L3 关于 CI-NEB 的页。

> **遇到**「插几个点？」→ **选"含端点 3–5 个点"，不要贪多**
>
> **因为**：课程讲义明确否定了"插点越多越好"（`[讲义]` L3）。
> 真实算例的 `c6h12ptgraphene` 用了 `00`–`05` 共 6 个目录（含两个端点 ⇒ 4 个像）。
>
> **代价**：点太少时，如果路径弯曲厉害，直线插值会给出很差的初始路径
> （见下一条）；点太多则计算量线性上升。
>
> **证据**：`[讲义]` L3；`[算例]` `5-ts/8-1-ex2c6h12ptgraphene/c6h12ptgraphene/00..05`。

> **遇到**「线性插值的初始路径太差」→ **选 IDPP 插值，而不是加更多点**
>
> **因为**：课程用了 IDPP（Image Dependent Pair Potential）改进初始猜测，
> 而且**讲义与真实算例给出了可逐位核对的证据**：
> 线性插值的第 `03` 像 C–H = **0.5916 Å**、IDPP 的 = **1.0879 Å**，
> 精确复现讲义里写的 0.59 / 1.09 Å（`[实测]`，两份精读报告都独立验过）。
>
> **代价**：
> - IDPP 需要额外的工具（课程用的是 `things to study/idpp.py`，依赖
>   `pymatgen` + `pymatgen_diffusion` —— 这**违反本 skill 的零依赖承诺**，
>   所以本 skill **不提供** IDPP 实现，只告诉你它是什么、去哪找）。
> - ⚠️ **真实算例的目录名不可信**（`[实测]`）：
>   `day3/idpp/` 下名为 `nebmake` 的目录装的其实是 **IDPP 结果**
>   （与 `c6h12-idpp` 的文件 MD5 逐字节相同），而 `c6h12-nebmake` 才是线性插值。
>   **不要按目录名判断算法。**
>
> **证据**：`[实测]` 两份精读报告对 `day3/idpp/*/POSCAR` 的比对；`[讲义]` L3。

### 12.3 过渡态的能量判据

> **遇到**「过渡态计算的 `EDIFFG` 该写多少」→ **选 `-0.01`；真正不能动的是 `EDIFF = 1E-7`**
>
> **因为**：这是一个**讲义模板与真实算例不一致**的地方，且证据方向很明确：
> 讲义模板（L3 P129/P131/P147）写 `EDIFFG = -0.03`，
> 但**三个真实 `INCAR` 与讲义自己 P153 的自述都是 `-0.01`**（`[实测]`）。
> 而 `EDIFF = 1E-7` 是过渡态算例里一致出现的更严的电子判据。
>
> **代价 / 裁定**：按权威序（`[算例]` > `[讲义]`），**取 `-0.01`**。
> 理由：真实的收敛算例能跑通而且更严；`-0.03` 只在讲义模板里出现。
> ⚠️ 但**本 skill 没有验证过 `-0.03` 是否会导致错误结果**，
> 所以这条的表述是"真实算例用 `-0.01`"，不是"`-0.03` 是错的"。
>
> **证据**：`[实测]` L3 精读报告的冲突日志 X 系列；`[算例]` `day3/ts/dim/INCAR` 等。

> ⭐ **补充（来自 `[LVTHW]`）：`EDIFFG` 其实是一个"阶梯"，不是一个值。**
>
> 这条是引入 LVTHW 之后**最重要的一个发现** ——
> 它解释了"为什么会有 `-0.03` 和 `-0.01` 两个答案"，而**两边都不是笔误**。
>
> `[LVTHW]` `EX75:133/135/148` 给的是 **`EDIFFG = -0.05`**，
> 而且作者明说：
> > 「前面的 `EDIFFG` **只是个形式**」「先让这个参数**占个坑**」
> > 「在粗算中就是个**摆设**」。
>
> ⇒ **它不是用来出结果的**。作者的意思是：NEB 的**粗算阶段**
> 只需要看出"路径形状对不对"，力判据放宽到 `-0.05` 能省大量机时。
> 另给一般体系 **`-0.02`**（`EX76:37`，与 `EDIFF = 1E-5` 同段）。
>
> **本项目的裁定 —— 把它写成阶梯**：
>
> | 档 | `EDIFFG` | 目的 | 能得出什么结论 |
> |---|---|---|---|
> | 粗算 | `-0.05` | **只看路径形状**（有没有走歪、最高像在哪） | ❌ **不能报能垒** |
> | 起步 | `-0.03` | 讲义模板值；路径基本成形后的中间档 | ⚠️ 谨慎 |
> | 出结果 | `-0.01` | 真实算例与讲义自述用的值 | ✅ 可以报 |
>
> ⇒ **判据不是"你用了哪个值"，而是"你报的那个过渡态是在哪一档下收敛的"。**
>
> ⚠️ **仍然诚实的部分**：本项目**没有**验证过 `-0.05` 是否会导致错误结果
> （作者既无反例也无正例），所以这条的表述是
> 「LVTHW 用它做粗算」，**不是**「`-0.05` 是错的」。
> 同理 `EX75:129` 的 `EDIFF = 1E-4` 也只用于粗算，
> 本项目**建议统一用 `1E-5`** 而不是 `1E-4`（`[待核对]`）。
>
> ⚠️ **`EDIFF = 1E-7` 那条不变**：过渡态出结果时电子判据要严。
>
> **证据**：`[LVTHW]` `EX75:129/133/135/148`、`EX76:37`；
> `[实测]` L3 精读报告的冲突日志 X 系列；`[算例]` `day3/ts/dim/INCAR` 等。
> 分析见 `references/raw/lvthw/learn_G6.md` §4 C-1。

---

## §13 频率计算与虚频

### 13.1 ⚠️ **自由度语义**：`OUTCAR` 里的 "Degree of freedom" 不是 3N

> **遇到**「读频率计算的 `OUTCAR`，看不懂自由度与离子步数」→ **记住这两条**
>
> **因为**（`[实测]`，两份精读报告独立核实）：
> - `IBRION = 5` 时，`OUTCAR` 里的 `Degree of freedom` = **3 × 放开的原子数**，
>   **不是**体系的 `3N`。
>   证据：21 个原子的体系只放开 1 个原子 → 回显 `3/3`；O₂ → `6/6`。
> - 离子步数 = `3 × 放开原子数 × NFREE + 1`。
> - ⚠️ **讲义 P31 把这个量写成了"体系中的自由度 3N"，这是错的。**
>   按权威序，`[实测]`（来自真实 `OUTCAR`）优先于 `[讲义]`。
>
> **代价 / 为什么重要**：这个数字决定了
> ①`OUTCAR` 里会出现几组位移；②你需要几个虚频才算"异常"。
> 用错基数会把"应有 3 个模"读成"应有 3N 个模"，从而误判计算没跑完。
>
> **证据**：`[实测]` L3 精读报告 §4 的 C 系列冲突项；对应真实算例
> `day4/oer/*/freq/`、`6-electronic/oer/{o,oh,ooh}/freq/` 的 `OUTCAR`/`DYNMAT`。

### 13.2 `IBRION` 怎么选

| `IBRION` | 含义 | 备注 |
|---|---|---|
| `5` | 有限差分，**不做对称性约化** | 实算例里最常见 |
| `6` | 有限差分，**做对称性约化** | 更快，但对称性高时可能漏模 |
| `7` | 从 `DYNMAT` 读动力学矩阵（**不重新算位移**） | 用于后处理/调 `POTIM` 重算 |
| `8` | 有限差分 + 部分对角化 | |

`[官方]` `pages/IBRION.md` / `pages/POTIM.md`。
⚠️ **诚实说明**：本 skill 的资料里，真实算例只用了 `IBRION = 5`；
`6`/`7`/`8` 的用法**没有真实算例可核对** → `[待核对]`。
讲义里 `DYNMAT` 出现 **0 次**（`[实测]`）。

> **遇到**「频率计算要不要固定原子」→ **选"看你要谁的频率"**
>
> **因为**：要求**整个体系**的振动 → 全部放开；
> 只要求**吸附物**的振动（做 ZPE 校正的常见做法）→
> 用 `Selective dynamics` 把 slab 原子全标 `F F F`、吸附物标 `T T T`。
>
> **代价**：
> - 全部放开时，低频声学模会带来很多**小的虚频/近零频**，
>   判读困难，且 `IBRION=5` 的计算量大。
> - 只放开吸附物时，**slab 自身的零点能贡献被忽略**。
>   `[实测]` 真实算例的做法就是"干净 slab 的校正取 0"
>   （`6-electronic/oer/*/freq/` 里 31 个 slab 原子全是 `F F F`）。
>   ⇒ **做能量差时，只要所有对比体系用了同一约定，slab 的 ZPE 会抵消。**
>
> **证据**：`[算例]` `6-electronic/oer/{o,oh,ooh}/freq/POSCAR`（Selective dynamics 标志）
> 与 `DYNMAT` 首行的模数（分别只有 3/6/9 个）；`[实测]` L4 精读报告。

### 13.3 虚频怎么判

| 体系 | 预期虚频数 | 说明 |
|---|---|---|
| 优化好的**极小点** | **0**（或仅有数值噪声级的小虚频） | |
| 优化好的**过渡态** | **恰好 1** | 且该模的位移应指向反应坐标 |
| 有虚频但不是 1 | 没收敛到鞍点 / 爬到别的鞍点 / 对称性用错 | |

> **判据（自查，三件都要做）**：
> 1. 看虚频的**数值**：`[经验]` 数量级在几到几十 `cm⁻¹` 的虚频常是数值噪声
>    （未充分收敛、`POTIM` 太小/太大）；上百 `cm⁻¹` 的才是真虚频。
>    ⚠️ **这个分界值是 `[经验]`，本 skill 没有官方依据** —— 别把它当硬阈值。
> 2. 看**振动模式的方向**：过渡态的那一个虚频，其位移必须沿着
>    "初态 → 末态"的路径。方向不对说明爬到了错误的鞍点。
> 3. **用 `IBRION=7` + `DYNMAT` 复核**：如果只是 `POTIM` 不合适，
>    改 `POTIM` 后用 `IBRION=7` 重算比重新做位移便宜得多。
>    （`[待核对]`：本 skill 没有真实算例验证过这条流程。）
>
> **证据**：`[官方]` IBRION/POTIM 页；`[讲义]` L3；`[经验]` 上述阈值分界。

#### 13.3b ⭐ 虚频怎么**消**（**这一条原来完全没有，是缺口**）

> **诚实交代**：本 skill 早期版本在 §13.3 只写了"**怎么判**"虚频，
> **没有写"怎么消"**。这是引入 LVTHW 后才补上的缺口
> （`[LVTHW]` `A29` 整篇 + `EX27` 一整篇）。

> **遇到**「优化好的结构还有虚频，怎么办」→ **按下面的顺序试，不要一上来就加严参数**
>
> **【最重要的是先说"什么不用做"】** `[LVTHW]` `EX27` 作者做了
> **五参数 × 三维度（ZPE / 虚频 / 耗时）的实测**，结论**反直觉**：
>
> | 他试过的 | 结果 |
> |---|---|
> | 加严 `EDIFF` | **完全消不掉虚频** |
> | 加严 `PREC` | **完全消不掉虚频** |
> | `ENCUT` 400 → 800 eV | 最大虚频 **65 → 26 cm⁻¹**，但作者判定"**没必要**" |
> | `POTIM` 调到很小（如 0.001） | **反而制造虚频** |
> | `POTIM` 调得很大（≥ 0.05） | **也制造虚频** |
>
> ⇒ **所以"用更严的优化再收一次"这条路，对虚频的作用被高估了。**
> 本项目早期处方里把它列为第一招 —— **这是需要修正的**。
>
> **【先判：这个虚频要不要管】** `[LVTHW]` 给了可执行的量级门槛（`[经验]`，非官方）：
>
> | 虚频大小 | 怎么处理 |
> |---|---|
> | **< 50 cm⁻¹** | **可忽略**（分子体系；数值噪声级） |
> | **50–100 cm⁻¹** | 一般也可忽略（`EX26:125` 给的宽松界是 100 cm⁻¹） |
> | **> 100 cm⁻¹** | **要小心** —— 除非你要的正是反应路径（`EX27:257`） |
>
> **为什么可以忽略（量级论证，这条很值钱）**：`EX26:139` 实测
> **3 个虚频合计 11.11 meV = ZPE（2.117 eV）的 0.5%**。
> ⇒ **它对 ZPE 的影响远小于你关心的能量差。**
>
> **【真要消，怎么做】** `[LVTHW]` `A29` 给的是**沿虚频方向位移**：
> 1. 从频率计算里找出虚频模的**位移方向矢量**（`OUTCAR` 的频率块里有）；
> 2. **沿该方向把坐标平移一点点**（`A29` 正文举例 `0.1`，脚本默认 `0.4`）；
> 3. 用**优化过的**输入重新做一次几何优化。
>
> ⚠️ **两个坑（`[LVTHW]` 原文自己带的）**：
> - `A29` 的脚本里 `dx,dy,dz` 是**单位方向矢量**（实测模长 = 1.00000），
>   所以"校正因子"在数值上**≈位移的 Å 数**；
> - **正文说 0.1、脚本默认 0.4** —— **同一篇两个值**，
>   ⇒ **不能把任何一个写成"推荐值"**，要按体系试。
> - 纯 Python 那一版有个静默坑：**把所有原子都写成了 `F F F`**
>   （本该保留原来的 `T/F`）⇒ 用之前**必须核对生成物的 `Selective dynamics` 列**。
>
> **【另一条更省事的路】** 用 `IBRION = 7` + `DYNMAT` 复核（见上）。
> `[待核对]`：本 skill 没有真实算例验证过这条流程。
>
> ⚠️ **本小节的门槛值（50 / 100 cm⁻¹）都是 `[经验]`，不是官方判据**，
> 而且作者**没有给出出处**。用它们时要结合体系判断。
>
> **证据**：`[LVTHW]` `EX26:125/139`、`EX27:51-61/188-331/257`、`A29:27/59/106/165/172`；
> 分析见 `references/raw/lvthw/learn_G5.md` §3.1 与 `learn_G7.md` §3.1。

---

## §14 能量与力的读法

### 14.1 读哪个能量（**这一条决定你的数字对不对**）

`OUTCAR` 里同一电子步附近会出现**多个能量**：

```
  free  energy   TOTEN  =      -41.69908757 eV
  energy  without entropy =      -41.69908757  energy(sigma->0) =      -41.70333685
```

> **遇到**「要报/要比总能量」→ **选 `energy(sigma->0)`，不要用 `free energy TOTEN`**
>
> **因为**：`free energy TOTEN` 是**含展宽熵项的自由能**
> `F = E − TS_smearing`。它依赖 `SIGMA` 与 `ISMEAR`，
> **两套不同展宽参数的 `TOTEN` 不可比**。
> `energy(sigma->0)` 是外推到 `SIGMA → 0` 的能量，才是你要的那个"DFT 总能量"。
>
> **代价**：
> - `energy(sigma->0)` 只在电子的 `FREE ENERGIE OF THE ION-ELECTRON SYSTEM` 块里
>   被打印，解析时要注意取**每个离子步的那一个**，而不是电子步中间的。
> - `[经验]` 对绝缘体（`ISMEAR=0`、`SIGMA` 小）两者差别很小；
>   对金属（`ISMEAR=1`、`SIGMA=0.2`）差别可达几十 meV —— **足以改变结论**。
>
> **证据**：`[实测]` `day2/Ag/OUTCAR` 里两种能量并存；
> `[官方]` ISMEAR/SIGMA 页（`SIGMA` 是展宽宽度）。

### 14.2 力平衡（**免费的物理不变量**）

`OUTCAR` 的 `TOTAL-FORCE` 块末尾有一行：

```
    total drift:                               -0.000037      0.003444      0.002516
```

> **判据（免费，零机时）**：**孤立体系**（分子、团簇、无固定原子的体系）里，
> 所有原子受力之和必须为零（牛顿第三定律）。
> `total drift` 就是 `ΣF`。它的量级应远小于单原子受力的量级。
>
> **因为**：`total drift` 明显偏大 ⇒ 力的计算或对称性处理有问题 ⇒
> **几何优化的收敛判据（`EDIFFG`）本身就是不可信的**。
> 这类缺陷**不会报错**，只会让优化停在一个错误的位置。
>
> **代价**：几乎为零 —— 这个数**已经在输出里**，不需要额外计算。
>
> **⚠️ 适用范围与反例（很重要）**：
> - 这个判据**只对孤立体系成立**。有固定原子的 slab、有外场、有约束的体系里
>   `ΣF ≠ 0` 是**正常的**（约束力不在 `TOTAL-FORCE` 里体现）。
> - `[经验]` 阈值怎么定：**不要用绝对阈值**。正确做法是拿 `total drift` 的模
>   与**该体系里最大的单原子受力**比，比值应在 `1e-3` 或更小。
>   `[实测]` `day2/Ag`（slab，有固定原子）的 `total drift ≈ (0.00004, 0.0034, 0.0025)` eV/Å，
>   而该体系的力在 `0.01` eV/Å 量级 ⇒ **比值约 0.3**。
>   ⇒ **这恰恰说明：对有固定的体系，这个判据不能直接用绝对大小判。**
>   `[待核对]`：本 skill **没有**在真实算例上标定过这条判据的可靠阈值。
>
> **证据**：`[实测]` `day2/Ag/OUTCAR:5152`；`[经验]` 阈值讨论。
> **→ 完整的不变量检查工具见 `scripts/compare.py`。**

---

## §15 带电体系与偶极修正

> **遇到**「要给体系加/减电荷」→ **选 `NELECT`，并同时考虑偶极修正与有限尺寸外推**
>
> **因为**：`[答疑]` 里讲师给的做法很具体：
> "改变 `NELECT`，默认的数值在 `grep NELECT OUTCAR` 里读取，重启计算把总电子数减一。
> 或者添加抗衡离子，在下表面加一个 OH"（`[答疑]` D1-P12）。
>
> **代价与必须做的配套**：
> - 改 `NELECT` 引入**背景电荷**。带电 slab 会产生**虚假的镜像相互作用**，
>   能量随真空层厚度**不收敛**（以 1/L 的形式）。
>   `[经验]` 必须做两件事：①加偶极修正（`LDIPOL`/`IDIPOL`）；
>   ②对**至少 3 个不同的真空层厚度**做外推到无限大。
> - ⚠️ 讲义 L2 有一个**自相矛盾**之处：P141 说"O/Au(111) 的 `INCAR` 和优化 Au 表面一样"，
>   但真实算例多出了 `LDIPOL = .TRUE.` / `IDIPOL = 3`，
>   而 P142 恰恰用"偶极矫正"解释结果（`[实测]`，见 L2 精读报告 §3.9）。
>   ⇒ **以真实算例为准**：做偶极修正。
>
> **判据（自查）**：
> 1. `grep NELECT OUTCAR` 拿到中性体系的电子数，确认你改的值与它差**整数个电子**；
> 2. 用两个不同真空层厚度算同一个带电体系，看能量差是否在误差预算内；
>    **不在 ⇒ 尺寸效应没收敛，结论不可用**。
>
> **证据**：`[答疑]` D1-P12；`[实测]` L2 精读报告的冲突项；`[算例]`
> `3-electronicStructure/ex6-electrostaticPotential/au111`。

---

## §16 气相分子与参考态

### 16.1 ⛔ **O₂ 的 DFT 能量必须反推，不能直接算**（电催化里最关键的一条）

> **遇到**「电催化自由能图里要 O₂ 的能量」→ **选"由实验热力学量反推"，绝不直接用 DFT 算的 O₂ 能量**
>
> **因为**：PBE 等半局域泛函**系统性高估 O₂ 的结合能**（O₂ 是著名的"DFT 失败案例"之一）。
> 课程给的做法是：由
> ```
> 2 G(H₂O) − 2 G(H₂) − G(O₂) = −4.92 eV
> ```
> 反推 `G(O₂)`。`[讲义]` L4 P9 + `[答疑]` D4-P20。
> **关键澄清**（`[实测]` L4 精读报告）：**错的是 O₂ 的 DFT 电子能，不是热力学校正项**
> —— 所以正确做法是替换**电子能**，而不是去调校正项。
>
> **代价**：
> - 这个做法引入了"与实验热力学量一致"的约束，代价是**放弃自洽性**：
>   你的自由能图里 O₂ 的能量不再是这个泛函算出来的。**必须在文中说明。**
> - **CO、N₂ 同理**（同样的 DFT 失败模式），见 `[讲义]` L4 P9。
> - `[实测]` L4 精读报告记录了讲义里 O₂ 的 G 值有 `−9.91` 与 `−9.92` 两个版本（C9），
>   说明连讲师自己的表里都有**取整差异** —— 报数时请统一到同一位小数。
>
> **证据**：`[讲义]` L4 P9；`[答疑]` D4-P20；`[实测]` L4 精读报告 §4。

### 16.2 水的参考态

`[讲义]` L4 P9：液态水取**饱和蒸气压（≈0.035 bar）下的水蒸气能量**代替，
用 `vaspkit-502-298.15-0.035-1` 计算。

> **代价 / 适用范围**：这是一种**近似**（把液态水的化学势等同于 0.035 bar 的水蒸气）。
> `[经验]` 它适用于常温常压附近；温度/压力离得远时误差会变大。
> ⚠️ **`vaspkit` 的 `502` 功能与 `-1` 开关的确切含义本 skill 未核实** → `[待核对]`。
> 本 skill **不提供**该功能，只登记"课程这么做"。

---

## §17 自由能校正（ZPE + 熵）

### 17.1 公式

```
ΔG = ΔE(DFT) + ΔZPE − TΔS
```

`[讲义]` L4；`[算例]` `6-electronic/oer.xlsx`（讲师自制的汇总表）。

### 17.2 决策条目

> **遇到**「给吸附物做 ZPE 校正」→ **选"只算吸附物的频率，slab 的校正取 0"**
>
> **因为**：真实算例的做法**完全一致**：`6-electronic/oer/{o,oh,ooh}/freq/` 里
> 把 31 个 slab 原子全标 `F F F`、只放开吸附物，
> 于是 `DYNMAT` 首行的模数分别只有 **3 / 6 / 9** 个（正好是 *O / *OH / *OOH 的原子数 × 3）。
> `[实测]`（L4 精读报告独立核实）。
>
> **代价**：slab 自身的 ZPE 被忽略。
> `[经验]` 只要**所有对比体系用了同一约定**，它在作差时会抵消 ——
> 所以这不影响"吸附能之差"，但**会影响绝对吸附自由能**。
>
> **真实校正值（可直接用作量级参考）**（`[算例]` `oer.xlsx`，`[实测]` L4 精读报告复算）：
>
> | 中间体 | ZPE + 熵校正 |
> |---|---|
> | `*O` | 0.027952 eV |
> | `*OH` | 0.272014 eV |
> | `*OOH` | 0.340296 eV |
>
> 用该表复算得到 OER 过电势 **η = 0.486 V**（讲义正文**没有**给这个数，
> 是精读时用算例数据算出来的 → `[实测]`）。
>
> **证据**：`[算例]` `6-electronic/oer.xlsx`、各 `freq/` 目录；`[实测]` L4 精读报告。

### 17.3 ⚠️ 一个**必须记下来的失败模式**

> **遇到**「要算 DOS 或吸收谱，却拿了一个弛豫计算的输出」→ **重跑单点**
>
> **真实案例**（`[实测]`）：`day2/ni-co` 的 `DOSCAR` 出自 `NSW = 300` 的**弛豫**计算
> （`OUTCAR` 里 `E-fermi` 出现 8 次 ⇒ 有 8 个离子步），
> 而讲义 P62 明确要求 DOS 步用 `NSW = 0`。
> ⇒ **弛豫过程中的 DOS 不是最终结构的 DOS**，两者不可混用。
>
> **判据（自查，一条命令）**：
> ```
> grep -c "E-fermi" OUTCAR      # 结果 > 1 ⇒ 这不是单点计算
> ```
> 或用本 skill 的 `python scripts/parse_output.py <目录>`，它会报出离子步数。
>
> **证据**：`[实测]` L2 精读报告；`[讲义]` L2 P62；`[算例]` `day2/ni-co/`。

---

## §18 溶剂模型

### 18.1 显式 vs 隐式

| | 显式溶剂 | 隐式溶剂（连续介质） |
|---|---|---|
| 做法 | 让溶剂分子真的出现在体系里 | 把溶剂当成介电常数为 ε 的连续介质 |
| 优点 | 能描述氢键等强相互作用 | 便宜、方便 |
| 缺点 | 计算量大幅增加，往往要做构象平均 | **无法描述氢键**等强相互作用 |

`[讲义]` L4 P39（显式）、P46（隐式）。

`[讲义]` L4 P44 还列了恒电势显式溶剂路线的**三个问题**：
①AIMD 模拟水/空气界面不能保持；②静电势依靠添加离子改变、不能连续调节；
③反应前后的静电势不等。对策是"通过扩包逼近 constant potential 状态"。

### 18.2 VASPsol（隐式溶剂的具体实现）

> **遇到**「要在 VASP 里加隐式溶剂」→ **选 VASPsol；最小改动 = 加 `LSOL` + 把 `NSW` 改成 0**
>
> **因为**：`[实测]` L4 精读报告对 `6-electronic/vaspsol-H2O/` 与 `vaspsol-GaN/` 里
> **普通 vs vaspsol 两套 `INCAR` 做了逐行 diff**，差异只有：
> - 加 `LSOL = .TRUE.`（默认水溶液）
> - `NSW` 改成 `0`（关掉离子步）
> - （`LRHOB = .TRUE.` 只用于打印 bound charge，不影响能量）
>
> ⚠️ **`EB_K`/`SIGMA_K`/`NC_K`/`TAU` 一个都没写** ⇒ 走默认值：
> 水 `EB_K = 78.4`、`SIGMA_K = 0.6`、`NC_K = 0.0025`、`TAU = 0.000525`
> （`[讲义]` L4 P54 给出了这些默认值的含义）。
>
> **代价**：
> - **要换溶剂就必须显式写 `EB_K`**。而讲义 P54 明说：
>   "其他参数不能直接查表需拟合，程序未公开其他溶剂参数，
>   目前只能**改介电常数**近似代表其他溶剂"（`[讲义]`）。
>   ⇒ **VASPsol 对其他溶剂的支持是有限的，别指望它精确描述甲醇/乙腈。**
> - `LSOL`/`LRHOB` **不在官方关键字表里**（`[实测]`：wiki API 查不到这两个页面）
>   —— 它们是**插件标签**。用它们的可执行文件必须**编译时编进了 VASPsol**，
>   否则会被静默忽略（`validate.py` 会因为 "OUTCAR 回显里没有它" 而报 ERROR）。
> - 讲义 P49 给了编译办法：
>   `makefile` 的 `CPP_OPTIONS` 加 `-Dsol_compat`，
>   把 VASPsol 的 `src/solvation.F` 复制到 `./src`（`[讲义]` L4 P49）。
>   ⚠️ **版本敏感**：讲义基于 VASP 5.4.4；新版本 VASP 的插件接口可能不同 → `[待核对]`。
> - `[讲义]` L4 P52：标准态校正还要 `+1.89 kcal/mol`。
>   ⚠️ 这个数的**适用范围与出处只有单一来源** → `[待核对]`。
>
> **实测数值（可作量级参考）**：H₂O 的溶剂化 ΔE = **−0.3128 eV**（`[实测]` L4 精读报告）。
> ⚠️ 但 `OSZICAR` 里 `SOL:` 行的四个数字含义**本 skill 未核实** → `[待核对]`。
>
> **证据**：`[实测]` L4 精读报告的逐行 diff；`[讲义]` L4 P49/P52/P54；
> `[算例]` `6-electronic/vaspsol-{H2O,GaN}/`。

---

## §19 性能与并行

> **遇到**「体系 > ~30 个原子」→ **选 `LREAL = Auto`**
>
> **因为**：`[官方]` `pages/LREAL.md` 原文：
> `We recommend using the real-space projection scheme for systems containing
> more than about 30 atoms. We also strongly recommend using only LREAL=Auto.`
>
> **代价**：官方明确警告 `.TRUE.` 与 `On` **都不推荐**：
> `LREAL=.TRUE. ... is potentially very inaccurate`；
> `For the outdated LREAL=On ...`。真正的精度控制要配 `ROPT`：
> `perform first reference calculations using LREAL=.False. and decrease ROPT
> until an acceptable accuracy, e.g. 1 meV/atom, is attained.`
>
> ⇒ **`[经验]`**：`LREAL = Auto` 在几何优化里是安全的；
> **做高精度能量差（< 10 meV）时，应当用 `LREAL = .FALSE.` 复核一次**。
> 真实算例里 `day1/fe2o3` 就是 `LREAL = .FALSE.`（`[算例]`）。

> **遇到**「`NCORE` 该写多少」→ **`NCORE` 与 `KPAR` 的乘积不应超过核数，且 `NCORE` 不宜超过约 8–16**
>
> **因为**：`[答疑]` 里学员问"自己的机器 24 核 48 线程，应该怎么设 `NCORE`"，
> 讲师答"**12 或 6**"（`[答疑]` D1-P13/P14）。
> ⇒ 讲师的取法对应"`NCORE` ≈ 物理核数 / 2"（24 → 12）或更保守（6）。
>
> **代价 / 注意事项**：
> - ⚠️ 真实算例里 `NCORE = 16`，配合 64 核（`[算例]` `day1/fe2o3/sub_vasp`）。
>   ⇒ **`NCORE` 没有普适最优值**，它取决于核数、内存带宽与体系大小。
> - `[经验]` **`NCORE` 与 `KPAR` 是两套并行层次**：`KPAR` 按 k 点分组、
>   `NCORE` 按轨道分组。**两个都调时要注意乘积**。
> - **不要**把"某台机器的最优 `NCORE`"当成通用规则（见 `MAINTENANCE.md` 的"机器细节不进"）。
>
> **证据**：`[答疑]` D1-P13/P14；`[算例]` `day1/fe2o3/INCAR` 与 `sub_vasp`；
> `[经验]` 并行层次的关系。

---

## §20 常见硬规则汇总（可抄）

| # | 规则 | 依据 |
|---|---|---|
| 1 | `POTCAR` 的数据集顺序**必须**与 `POSCAR` 元素顺序一致 | `[官方]` POTCAR 页 |
| 2 | `POTCAR` 只读，**不要编辑**它（选泛函改 `INCAR`） | `[官方]` POTCAR 页 |
| 3 | 绝缘体**不要**用 `ISMEAR > 0`（MP 会产生非物理占据） | `[官方]` ISMEAR 页 |
| 4 | 四面体方法（`-4`/`-5`/`-14`/`-15`）**必须** Γ 居中 k 点 | `[官方]` ISMEAR 页 |
| 5 | fcc / hexagonal 晶格**只用** Γ 居中网格 | `[官方]` KPOINTS 页 |
| 6 | line 模式 k 点**必须**配 `ICHARG = 11` | `[官方]` KPOINTS 页（Warning） |
| 7 | DFT+U 含 d 电子 → `LMAXMIX = 4`；含 f → `6`；DFT+U 能带计算**严格必须** | `[官方]` LMAXMIX 页 |
| 8 | `IBRION = 0`（MD）**必须**给 `POTIM`，否则程序立即崩 | `[官方]` POTIM 页 |
| 9 | `EDIFFG` **不适用于**分子动力学 | `[官方]` EDIFFG 页（Warning） |
| 10 | `IBRION=3`（Damped MD）下 `POTIM = 0` **是**官方默认值，合法 | `[官方]` POTIM 页 Default 表 |
| 11 | 从 `WAVECAR`/`CHGCAR` 续算时，删掉 `MAGMOM` 会让磁矩**被对称化掉** | `[官方]` MAGMOM 页 |
| 12 | `MAGMOM` 会按需**打破对称性** | `[官方]` MAGMOM 页 |
| 13 | `INCAR` 的注释只能用 `#` 或 `!`；**圆括号不是注释**；`;` 是语句分隔符 | `[官方]` INCAR 页 |
| 14 | `INCAR` 续行的反斜杠后**不能有空格** | `[官方]` INCAR 页 |
| 15 | `LREAL=.TRUE.` 与 `On` 官方**不推荐**，只用 `Auto` | `[官方]` LREAL 页 |
| 16 | `POTIM` 值不合理时程序会**静默改成 0.015 Å** | `[官方]` POTIM 页（Warning，VASP.5.1+） |
| 17 | DFT+U / `ICHARG=11` 的非自洽结果与自洽结果**差别大** | `[官方]` LMAXMIX 页 |
| 18 | 用 line 模式的 k 点做自洽是**错的**（官方 Warning） | `[官方]` KPOINTS 页 |

---

## 附录 A：本文件里的数值速查

> **只列本文件正文里出现过、且带出处的数值。** 更全的数值见 `playbook.md` §0。

| 量 | 值 | 适用范围 | 出处 |
|---|---|---|---|
| `ENCUT` | **显式写 + 自己做收敛测试** | 通用（官方**唯一**的要求） | `[官方]` PREC 页「strongly recommend」 |
| `ENCUT` 的 `1.3×max(ENMAX)` | **已弃用 `PREC=High` 的历史默认值**，可作起点 | 见 §4.2 的订正 | `[官方]` PREC 页默认值表 + `deprecated` 提示 |
| `PREC=Normal/Accurate` 的默认 `ENCUT` | `max(ENMAX)` | — | `[官方]` PREC 页默认值表 |
| `ENMAX` 高于 ~1000 eV 时 | **不要机械照搬** | He/Ne、半芯态赝势 | `[算例]` `ex8-NaHe2`；`[经验]` 阈值 |
| 收敛判据 | 相邻 `ENCUT`/k 点的能量差 < **1 meV/atom** | 通用 | `[经验]`；官方在 LREAL 页提过同名量级 |
| `ISMEAR` / `SIGMA`（绝缘体） | `0` / `0.01–0.05` | 绝缘体、半导体、分子 | `[算例]` `day1/fe2o3`、`vaspsol-H2O` |
| `ISMEAR` / `SIGMA`（金属） | `1` / `0.2` | 金属弛豫 | `[算例]` `day2/Ag` 等 5 例 |
| `ISMEAR`（DOS） | `-5`（+Γ 居中 k 点） | DOS/静态 | `[官方]` ISMEAR |
| `SIGMA` 默认 | `0.2` eV | — | `[官方]` SIGMA 页 |
| `LMAXMIX` | `4`（d）/ `6`（f）；默认 `2` | DFT+U、非共线 | `[官方]` LMAXMIX 页 |
| `POTIM` | `0.2` | 表面/分子 CG 优化 | `[算例]` 7 例 |
| `POTIM` 默认 | `0.5`（`IBRION=1,2,3`）/ `0.015`（`5,6`） | — | `[官方]` POTIM 页 |
| `EDIFFG` | `-0.01` eV/Å | 常规弛豫与过渡态 | `[算例]` 多例 |
| `EDIFFG` 默认 | `EDIFF × 10` | — | `[官方]` EDIFFG 页 |
| `EDIFF`（过渡态） | `1E-7` | 过渡态 | `[实测]` L3 精读报告 |
| `MAGMOM` 初值 | 实验磁矩 × **1.2–1.5** | 磁态收敛 | `[官方]` MAGMOM 页 Tip |
| DFT+U（Fe₂O₃） | `LDAUU = 5.3`, `LDAUJ = 0` → `U_eff = 5.3` | Fe 3d | `[算例]` `day1/fe2o3/INCAR` |
| DFT+U（模板） | `LDAUU = 4.6`, `LDAUJ = 0.4` → `U_eff = 4.2` | 同上，**不同写法** | `[算例]` `things to study/INCAR` |
| 真空层 | **无标准值**；真实算例 7.4–15.2 Å | slab/二维 | `[算例]` 反推 |
| 赝氢位置 | 被删原子的**键中点**；实测 H–N = 0.9865 Å ≈ Ga–N/2 | 钝化 | `[实测]` `day1/GaN`；`[答疑]` D1-P15/16 |
| CI-NEB 插点 | 含端点 **3–5 点** | 过渡态 | `[讲义]` L3 |
| 频率自由度（`IBRION=5`） | `OUTCAR` 里 = **3 × 放开原子数**，不是 3N | 频率计算 | `[实测]` L3 精读报告 |
| ZPE 校正 `*O`/`*OH`/`*OOH` | 0.027952 / 0.272014 / 0.340296 eV | CoN₄ OER | `[算例]` `oer.xlsx` |
| OER `η`（复算） | 0.486 V | CoN₄ OER，用上表 | `[实测]` L4 精读报告 |
| O₂ 参考态 | `2G(H₂O) − 2G(H₂) − G(O₂) = −4.92 eV` | 电催化 | `[讲义]` L4 P9；`[答疑]` D4-P20 |
| 液态水参考态 | 饱和蒸气压 ≈ 0.035 bar | 电催化 | `[讲义]` L4 P9 |
| VASPsol 默认 | `EB_K=78.4`, `SIGMA_K=0.6`, `NC_K=0.0025`, `TAU=0.000525` | 水 | `[讲义]` L4 P54 |
| VASPsol 最小改动 | 加 `LSOL` + `NSW=0` | 隐式溶剂 | `[实测]` L4 精读报告逐行 diff |
| 溶解自由能标准态校正 | `+1.89 kcal/mol` | `[待核对]` 单一来源 | `[讲义]` L4 P52 |
| vdW-DF2 | `GGA=ML` + `LUSE_VDW=.TRUE.` + `ZAB_VDW=-1.8867` + `AGGAC=0` | 非局域 vdW | `[算例]` `day1/vdw-df2/INCAR` |
| `IVDW` | `11`=D3，`12`=D3-BJ | 经验修正 | `[答疑]` D1-P6 |
| `NCORE` | 24 核 → 12 或 6 | **某一次问答，不是通用规则** | `[答疑]` D1-P13/P14 |

---

## 附录 B：本文件**明确不覆盖**的范围

诚实列出边界，比假装覆盖全部更有用：

1. **`ZAB_VDW` 的核函数取值表** —— 本 skill 没有从官方资料核实到完整对应关系 → `[待核对]`。
2. **`KP-Resolved Value`（vaspkit）的单位与换算** —— 检索到的说法与实测反推不自洽，
   本 skill **不采信、不给公式**（§5.4）。
3. **`ICHAIN`/`IOPT`/`LCLIMB` 的官方定义** —— wiki 上没有独立页面，
   本文件只登记真实算例的用法（§12）。
4. **`IBRION=6/7/8` 的实操** —— 没有任何真实算例可核对 → `[待核对]`（§13.2）。
5. **虚频大小的"噪声 vs 真虚频"分界值** —— 只有 `[经验]`，没有官方依据（§13.3）。
6. **赝势"选得对不对"**（该不该用 `_pv`/`_d`、该用 PBE 还是 PW91）——
   本 skill 只校验顺序与截断，**不评价选型**。
7. **`vaspkit` 各功能的开关含义** —— 只登记课程用过哪些，不解释其内部。
8. **编译与部署** —— 除 §18.2 里 VASPsol 的两步之外，本 skill 不覆盖编译。
9. **具体机器的并行最优参数** —— 按 `MAINTENANCE.md` 的"机器细节不进"，一律不写。
10. **`OPTCELL` 的官方语义** —— 它是工具约定不是 VASP 原生标签；
    本文件只写"实测到它会冻结某个方向、且不在 `OUTCAR` 回显"（§9.2）。
