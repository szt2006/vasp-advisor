# workflow —— **项目阶段向导**：我在哪个阶段？下一步做什么？

> ⚠️ **本文件由 `python scripts/guide.py --export` 生成，请不要手改。**
> 要改内容请改 `scripts/guide.py` 的 `STAGES`。

> **这不是一个「自动跑命令的工作流」。** 它在**每个阶段**告诉你：
> 现在该做什么、有哪些决策点、坑在哪、该跑哪条已有命令、该读哪个条目。
>
> ⚠️ **它不替你决定**，也不提交作业 —— 定位是「顾问，而非自动驾驶」。

## 怎么用

```bash
python scripts/guide.py list                  # 列全部阶段
python scripts/guide.py show <阶段>           # 展开某阶段
python scripts/guide.py scan <你的项目目录>    # 推断「卡在哪、下一步做什么」
python scripts/guide.py next <你的项目目录>    # 只要下一步
```

⚠️ `scan` 是**启发式**（按文件存在性判断），它会**打印依据**，你可以直接推翻它。

---

## 11 个主线阶段 + 1 个续算分支

| # | 阶段 | 一句话 |
|---|---|---|
| 1 | [立项与问题定义](#1-define) | 把科学问题翻译成可计算的任务，并估清规模。 |
| 2 | [建模与初始结构](#2-model) | 拿到一个**物理上站得住**的初始结构（`POSCAR`）。 |
| 3 | [参数设定（INCAR / KPOINTS）](#3-params) | 一套**自洽**的输入。 |
| 4 | [收敛测试](#4-converge) | 证明**你的数值设置够用**（`ENCUT` / k 点 / `SIGMA`）。 |
| 5 | [几何优化 / 晶胞优化](#5-optimize) | 找到**力收敛**的驻点结构。 |
| 6 | [电子结构分析](#6-electronic) | 拿到 DOS / PDOS / 电荷 / 势 / 功函数这类**可观测量**。 |
| 7 | [分子动力学（AIMD）](#7-dynamics) | 有限温下的轨迹与统计量。 |
| 8 | [反应路径 / 过渡态](#8-path) | 找到**一阶鞍点**并验证它。 |
| 9 | [后处理与物性](#9-post) | 从输出里抽出**可用的数值**，并核对自洽性。 |
| 10 | [诊断（出问题时）](#10-diagnose) | 从**症状**定位到**原因**，并给出**改哪一处**。 |
| 11 | [结论与报告](#11-report) | 把结果写成**别人能复核**的形式。 |
| ↻ | [↻ 续算（旁路分支）](#resume) | 计算被中断（墙钟 / 被 kill / 崩溃）后接着跑，而不是从头。 |

---

## 1 立项与问题定义

**目标**：把科学问题翻译成可计算的任务，并估清规模。

**⭐ 第一件事**：先跑 `python _system_types.py --lookup <目录>` 确认体系类型与**规模** —— 规模决定并行配置，而并行配置决定作业能不能起来。

**该做的**：

- 明确要算的量（吸附能 / 反应能垒 / DOS / 频率 / 扩散系数…）
- 判断体系类型与维度（体相 / slab / 分子 / 线状）
- 粗估原子数与核数 ⇒ **决定并行配置**

**决策点**：

- 静态 vs 有限温（表面反应、扩散必须有限温）
- 是否需要反应路径（NEB / Dimer）

**常见坑**：

- 任务类型选错 ⇒ 整套白算
- ⚠️ **不定规模就开始写 INCAR** —— 这正是那次事故的来源：179 原子 + 16 rank 却没写 `NCORE`

**该跑的命令**：

```bash
python _system_types.py --lookup <目录>   # 先确认「你是哪类体系 + 规模轴」
python scripts/recommend.py --goal <目标> --elements "<元素>"
python scripts/doctor.py
```

**该读的条目**：

- `references/_SYSTEMS.md`（体系类型索引 + 规模轴）
- `references/decide.md`（决策总览）

---

## 2 建模与初始结构

**目标**：拿到一个**物理上站得住**的初始结构（`POSCAR`）。

**⭐ 第一件事**：先量**真空层够不够**（该方向有没有 ≥10 Å 真空）—— 不够会被镜像作用污染，而**程序不报错**。

**该做的**：

- 按实验数据（配位环境、键长、电镜、元素组成）搭模型
- 定晶胞与真空层厚度
- 定元素顺序 —— 它决定 `POTCAR` 的拼接顺序

**决策点**：

- 表面切哪个晶面、几层、固定几层
- 真空层多厚

**常见坑**：

- ⚠️ **真空层不够** ⇒ slab 与自己的镜像作用，**而程序不报错**
- ⚠️ **`POSCAR` 元素顺序与 `POTCAR` 不一致** ⇒ 静默错
- ⚠️ **某方向设 1 个 k 点**只对**真有真空**的方向成立（3D 体相照做会静默算错）

**该跑的命令**：

```bash
python scripts/validate.py <目录>   # 会查真空方向与 k 点的关系
```

**该读的条目**：

- `references/playbook.md` §1 的 S30（真空层不够）
- `references/playbook.md` §0.3（真空层、slab 层数、固定层数）
- `references/_GATES.md` §3（规模敏感标签）

---

## 3 参数设定（INCAR / KPOINTS）

**目标**：一套**自洽**的输入。

**⭐ 第一件事**：先跑 `python scripts/validate.py <目录> --ncores <你的核数>` —— 它会在**提交之前**查并行分解。

**该做的**：

- 选泛函与 `ENCUT`
- 选展宽 `ISMEAR` / `SIGMA`（按金属性）
- 选 k 点密度
- **定并行配置**（`NCORE` / `KPAR`）

**决策点**：

- 要不要 +U / 杂化 / vdW / 隐式溶剂
- 金属 vs 绝缘体的展宽口径
- **k 点密度 vs 机时**

**常见坑**：

- ⚠️ **`NCORE` 不写就走默认 1** ⇒ 大体系 + 多 rank 会**第一次 SCF 就崩**
- ⚠️ **`NCORE` 与 `NPAR` 同时写** ⇒ `NPAR` 优先、`NCORE` 被**静默忽略**
- ⚠️ `ISMEAR=-5`（四面体法）在 k 点 < 4 时失败

**该跑的命令**：

```bash
python scripts/wizard.py   # 生成一套自洽输入 + 逐参数 README
python scripts/recommend.py --goal <目标> --elements "<元素>"
python scripts/validate.py <目录> --ncores <你的核数>
```

**该读的条目**：

- `references/decide.md`（遇到 X 该选 Y，因为 Z，代价是 W）
- `references/_SYSTEMS.md`（该类体系的参数画像）
- `references/_GATES.md` §3（规模敏感标签清单）

---

## 4 收敛测试

**目标**：证明**你的数值设置够用**（`ENCUT` / k 点 / `SIGMA`）。

**⭐ 第一件事**：先只扫**一个**参数（`ENCUT` 或 k 点），固定其余 —— 一次只动一个才能归因。

**该做的**：

- 固定其它参数，只扫一个；看目标物理量随它变化
- 画收敛曲线，取「变化小于你的精度要求」的那个值

**决策点**：

- 收敛判据取多少（能量 1 meV/atom？力 0.01 eV/Å？）
- ⚠️ **收敛测试要按「要算的量」来定** —— 算能量差和算力，要求不同

**常见坑**：

- ⚠️ **跳过收敛测试** ⇒ 后面所有结论都建立在一个没验证的基组上
- ⚠️ 只测了 `ENCUT` 没测 k 点（或反过来）
- ⚠️ **变胞优化（`ISIF=3`）要重测 `ENCUT`** —— 胞变了基组也变了

**该跑的命令**：

```bash
python scripts/compare.py <目录>   # 跨算例一致性
python scripts/parse_output.py <目录>
```

**该读的条目**：

- `references/decide.md`（`ENCUT` / k 点 / `SIGMA` 的条目）
- `references/playbook.md` §0（数值速查表，每张都带「适用范围」列）

---

## 5 几何优化 / 晶胞优化

**目标**：找到**力收敛**的驻点结构。

**⭐ 第一件事**：先确认 `OUTCAR` 里**力真的到了 `EDIFFG`**，而不是只看"跑完了"。

**该做的**：

- 选 `IBRION` / `ISIF` / `NSW` / `EDIFFG`
- 看 `OUTCAR` 的力是否到 `EDIFFG`
- 收敛后确认**没有跑偏**（对比初末结构）

**决策点**：

- `ISIF=2`（冻胞）vs `ISIF=3`（变胞）
- slab 要不要固定底层原子

**常见坑**：

- ⚠️ **`IBRION=5`（频率）配 `ISIF=3`** ⇒ 晶胞在动，Hessian 不是你要的
- ⚠️ **`POTIM` 给 0 但 `IBRION` 不是 3** ⇒ 离子不动**而程序不报错**（「没报错但白干」）
- ⚠️ 只看到 `reached required accuracy` 就以为一定对 —— 要确认**收敛到的是你要的那个结构**

**该跑的命令**：

```bash
python scripts/diagnose.py <目录>   # 查 GEO.not_converged
python scripts/compare.py <目录>     # 查力平衡
```

**该读的条目**：

- `references/playbook.md` §1（几何优化相关 S 条目）
- `references/decide.md`（`ISIF` / `EDIFFG` 条目）

---

## 6 电子结构分析

**目标**：拿到 DOS / PDOS / 电荷 / 势 / 功函数这类**可观测量**。

**⭐ 第一件事**：先确认**这一步的 k 点比优化时更密**（DOS 的毛刺根因是 k 点，不是 `NEDOS`）。

**该做的**：

- 先做**自洽**单点，再算目标量
- DOS 用比优化更密的 k 点；能带用 line 模式
- 电荷分析选对方法（Bader / DDEC / Löwdin…）

**决策点**：

- `ISMEAR` 用哪个（DOS 要 `-5` 还是 `0`）
- 电荷分析用哪种布居

**常见坑**：

- ⚠️ **拿优化用的粗 k 点去算 DOS** ⇒ 曲线有毛刺（根因是 k 点，**不是** `NEDOS`）
- ⚠️ **`LORBIT` 输出的 `total charge` 不能定量**（那是半径球内的布居）
- ⚠️ `ISMEAR=-5` 要求 k 点 ≥ 4

**该跑的命令**：

```bash
python scripts/diagnose.py <目录>
python scripts/postprocess.py <子命令>   # DOS / 功函数 / 电荷
```

**该读的条目**：

- `references/playbook.md` §4（后处理判读经验）
- `references/course_learned.md` §4（电子结构分析）

---

## 7 分子动力学（AIMD）

**目标**：有限温下的轨迹与统计量。

**⭐ 第一件事**：先跑**很短**的一段确认能量不漂，再上生产段。

**该做的**：

- 定系综与温控（`MDALGO` / `TEBEG` / `TEEND`）
- 定时间步与步数；先跑短的确认稳定
- 丢平衡段，只用生产段做统计

**决策点**：

- 时间步长（含 H 要更小）
- 系综选择

**常见坑**：

- ⚠️ **把平衡段也算进统计** ⇒ 统计量有系统偏差
- ⚠️ 时间步太大 ⇒ 能量漂移，**不一定报错**

**该跑的命令**：

```bash
python scripts/parse_output.py <目录>
python scripts/postprocess.py <子命令>
```

**该读的条目**：

- `references/decide.md`（MD 相关条目）
- `references/playbook.md` §2（工作流）

---

## 8 反应路径 / 过渡态

**目标**：找到**一阶鞍点**并验证它。

**⭐ 第一件事**：先确认**插点数能被核数整除**（NEB 的硬约束），再提交。

**该做的**：

- NEB / CI-NEB 或 Dimer
- 用频率确认**恰好一个虚频**
- 做 IRC 或至少两端点确认连接的是你要的两个态

**决策点**：

- NEB vs Dimer（知道大致路径 vs 只知初末态）
- 插点数量（**必须能被核数整除**）

**常见坑**：

- ⚠️ **过渡态必须恰好 1 个虚频**；0 个是极小点、≥2 个没爬到鞍点
- ⚠️ **NEB 的核数必须整除插点数**，否则并行出错
- ⚠️ 频率计算里「最小 6 个频率出虚频可无视」**只对孤立分子成立**

**该跑的命令**：

```bash
python scripts/diagnose.py <目录>
python scripts/parse_output.py <目录>   # 读 DYNMAT 判虚频
```

**该读的条目**：

- `references/playbook.md` §1（频率 / 虚频相关 S 条目）
- `references/_SYSTEMS.md`（孤立分子那一节）

---

## 9 后处理与物性

**目标**：从输出里抽出**可用的数值**，并核对自洽性。

**⭐ 第一件事**：先跑 `python scripts/compare.py <目录>` 做**自洽性检查** —— 这是最值钱的一个动作。

**该做的**：

- 抽数值（能量 / 力 / 频率 / DOS / 功函数）
- **做自洽性检查**（能量闭合、力平衡、原子数一致）
- 把口径（`ENCUT` / k 点 / 版本）记下来

**决策点**：

- 要不要做自由能校正（ZPE / 熵）
- 参考态怎么选

**常见坑**：

- ⚠️ **不做闭合性检查** ⇒ 一个常数偏移能悄悄进到结论里
- ⚠️ 不同算例的 `ENCUT` / k 点不一致 ⇒ 能量差**不可比**

**该跑的命令**：

```bash
python scripts/parse_output.py <目录>
python scripts/compare.py <目录>
python scripts/postprocess.py <子命令>
```

**该读的条目**：

- `references/playbook.md` §4（后处理判读）
- `references/course_learned.md`（自由能校正）

---

## 10 诊断（出问题时）

**目标**：从**症状**定位到**原因**，并给出**改哪一处**。

**⭐ 第一件事**：**先分类**：`grep -cE "^(DAV|RMM):" OSZICAR` —— 0 就是「没跑起来」（A 类），否则是「结果不对」（B 类）。**三类的处方是冲突的。**

**该做的**：

- 先分清三类：**没跑起来** / **跑完但结果不对** / **慢**
- 按症状查 `diagnose.py`，对不上再查 `playbook.md` §1

**决策点**：

- ⚠️ **不要在没分清「哪一类」之前就开始调参**

**常见坑**：

- ⚠️ **把「某个取值没救回来」当成「该变量无关」**
- ⚠️ **把日志里「总会出现的行」当根因**（红鲱鱼）
- ⚠️ **在动系统 / 队列配置之前没试并行分解**

**该跑的命令**：

```bash
python scripts/diagnose.py <目录>
python scripts/validate.py <目录> --ncores <核数>
python scripts/compare.py <目录>
```

**该读的条目**：

- `references/playbook.md` §4b（**诊断反模式**，先读这个）
- `references/playbook.md` §1（症状 → 处方 73 条）
- `references/playbook.md` §5（报错原文速查）

---

## 11 结论与报告

**目标**：把结果写成**别人能复核**的形式。

**⭐ 第一件事**：先把**每个数的来源**记下来（哪个目录、哪个文件）—— 事后补不回来。

**该做的**：

- 记清每个数的来源（哪个目录、哪个文件、哪一行）
- 写清方法学参数（泛函 / `ENCUT` / k 点 / 版本 / 展宽）
- **列出本次没检查的项**

**决策点**：

- 结论的置信度怎么表述

**常见坑**：

- ⚠️ 不写 `ENCUT` / k 点 ⇒ 别人无法复现也无法判断可比性
- ⚠️ 把「程序没报错」当成「结果对」

**该跑的命令**：

```bash
python scripts/compare.py <目录>
python scripts/doctor.py   # 报告环境
```

**该读的条目**：

- `references/templates/report.md`（**报告模板**：只给结构不给数值）
- `references/VERSIONS.md`（写清版本）
- `references/_WRITING_CONTRACT.md`（证据分级）

---

<a id="resume"></a>

## ↻ ↻ 续算（旁路分支）

**目标**：计算被中断（墙钟 / 被 kill / 崩溃）后接着跑，而不是从头。

**⭐ 第一件事**：先判断**已经算到哪**（离子步 / 电子步），再决定从 `CONTCAR` 还是 `WAVECAR` 续。

**该做的**：

- 判断**已经算到哪**（离子步 / 电子步）
- 决定从 `CONTCAR` 还是 `WAVECAR` / `CHGCAR` 续
- 改 `ISTART` / `ICHARG`

**决策点**：

- 要几何结构还是要波函数 / 电荷密度

**常见坑**：

- ⚠️ **`ISTART=1` 但没有 `WAVECAR`** ⇒ 程序忽略它、从头算（**不报错**）
- ⚠️ 续算时**改了 `ENCUT` / k 点** ⇒ 与前面的结果不可比

**该跑的命令**：

```bash
python scripts/diagnose.py <目录>   # 先看 RUN.not_finished
python scripts/wizard.py --goal resume
```

**该读的条目**：

- `references/playbook.md` §1（续算相关 S 条目）
- `references/decide.md`（`ISTART` / `ICHARG` 条目）

---

## 相关页

- **体系索引**：`references/_SYSTEMS.md`（先问「你算的是哪类」）
- **条件与规模**：`references/_GATES.md`
- **症状 → 处方**：`references/playbook.md` §1
- **诊断反模式**：`references/playbook.md` §4b
