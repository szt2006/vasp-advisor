# VASP 实战手册（F 层 · 怎么做）

> **本文件是什么**：VASP 表面/催化计算的**操作手册**。只回答「改哪一处、改成什么、怎么知道改对了」。
> **本文件不写什么**：物理原理、泛函/方法学的选择理由、参数背后为什么成立 —— 那些归 `decide.md`。
> 本文件里凡出现「为什么选它」，一律用交叉引用 `→ decide.md §x` 指出去，不在此展开。
>
> **怎么用**：
> 1. 遇到报错/异常 → 先查 **§5 报错原文速查**（按输出原文 grep），拿到编号后回 **§1** 看四要素细节；
> 2. 要开一个新任务 → 查 **§2 任务工作流**，按步骤抄命令；
> 3. 要一个具体数值 → 查 **§0 数值速查表**，**必须同时读该行的「适用范围」列**；
> 4. 建模型 → **§3**；算完出数了不确定怎么读 → **§4**；
> 5. **上线前** → 跑 **§3.8 输入文件的句级自查**（纯文本 grep，不占机时，专抓"写了但没生效"）。
>
> **路径约定**：文中所有路径（`references/…`、`scripts/…`、`things to study/…`）都相对**本仓库根目录**（即 `VASP-skill-V0.1/`），
> 不是相对本文件所在的 `references/`。命令示例一律假设你在仓库根目录下执行。
>
> **证据标记**：`[官方]`（VASP wiki，指向 `references/official/pages/`）> `[算例]`（随课真实文件）> `[讲义]`（`L1 P28` 形式）> `[答疑]`（`D2-P14` 形式）> `[经验]`（有适用范围与反例）> `[待核对]`（单一来源或本文件推断）。分级与引用格式见 `_WRITING_CONTRACT.md`。
>
> **红线声明**：本文件不含任何集群地址、队列名、核数上限、账号、机器路径或 `POTCAR` 正文。
> 文中出现的 ENMAX 类数值均来自 `OUTCAR` 的运行期回显或随课精读报告的记录，**不是**从 `POTCAR` 抄录；
> 要拿你自己的截止能，请用本仓库的解析工具读**你自己本地的** `POTCAR`（例如在仓库根目录执行
> `python -c "import sys; sys.path.insert(0,'scripts'); import vasp_common as vc; print(vc.parse_potcar_header('POTCAR').titles)"`）。

---

## §0 数值速查表

> **读法**：任何一行都**不能只看「典型值」**。"适用范围"列写了这个数在什么体系上成立；
> "例外/反例"列写了什么时候它不成立。两列缺一，这条数值就不许用。
> 表中 `[算例]` 一律指本仓库 `things to study/` 下的随课真实文件（第 1 天到第 4 天四批）。

### 0.1 截断能 ENCUT

| 量 | 典型值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|---|
| `ENCUT` | 不写则取 `POTCAR` 中最大 `ENMAX` | 任意体系（VASP 默认行为） | **不推荐**依赖默认：多体系比较时不同计算的默认 `ENCUT` 可能不同，总能量不可比 | `[官方]` `references/official/pages/ENCUT.md` |
| `ENCUT` | **必须手动写死在 INCAR 里** | 任何要跨计算比较能量的场合（吸附能、表面能、形成能） | 单次、孤立、不与别算例比较的试算可以省 | `[官方]` `references/official/pages/ENCUT.md` |
| `ENCUT` | `= max(ENMAX)` | 常规结构优化（讲义口径，例给 400） | 讲义给的 "(400)" 实为 O 的 ENMAX 而非普适常数 | `[讲义]` L1 P28 |
| `ENCUT` | **> 1.3 × max(ENMAX)** | 晶胞优化 / 弹性常数（`ISIF=3`、`ISIF=4`） | 截断偏低会让应力与晶格常数系统性偏小 | `[讲义]` L1 P28；`[算例]` `day1/fe2o3/INCAR`（O 的 ENMAX = 400.000 eV，`ENCUT = 520.0` = **恰好 1.30×**） |
| `ENCUT` | 500 | 单层 MoS₂（3 原子，`ISIF=3` + OPTCELL 面内优化） | 该例 1.93×ENMAX，属"给足"而非"刚好" | `[算例]` `day1/mos2/INCAR`、`day1/vdw-df2/INCAR` |
| `ENCUT` | 400 | 表面/二维体系常规计算（Ag、Al₂O₃、Au(111)、石墨烯片、VASPsol 两组） | 这些算例**都没有做截断能收敛测试**的记录 | `[算例]` `day2/{Ag,al2o3,au111-opt,c,mos2ws2}`、`线上中级班-催化资料/6-electronic/vaspsol-*` |
| `ENCUT` | 520 | Ni(100)-CO 体系（`L2 P61` 模板与 `ni-co` 算例一致） | 这是模板照抄值，讲义**通篇没有给 ENCUT 选取判据** | `[讲义]` L2 P61；`[算例]` `day2/ni-co/INCAR` |
| `ENCUT` | 500 | CoN₄ 单层 OER 全套（slab / *O / *OH / *OOH + 三个 freq） | 同上，无收敛测试记录 | `[算例]` `线上中级班-催化资料/6-electronic/oer/*/INCAR` |
| `ENCUT` | 降低到 ENMAX 是提速手段；**不建议更低** | 体系太大、算力不足时 | 低于 ENMAX 会引入未定义误差 | `[讲义]` L1 P48 第 (7) 条 |
| `_h` 后缀赝势 | 需要约 700 eV | 第一、二周期双原子分子（H₂/N₂/CO/O₂）想更贴实验时 | **单一来源、无法核验**（本仓库不读 POTCAR，4 个算例都没用 `_h`）；一般仍用默认赝势，理由是贵且要保持赝势统一 | `[讲义]` L1 P27 `[待核对]` |

**收敛测试怎么做** → §2 W1。**这是唯一能替代上表所有 ENCUT 取值的动作。**

### 0.2 k 点密度 / 网格

| 量 | 典型值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|---|
| vaspkit 的 `KP-Resolved Value`（即 `R`） | **0.040** | 讲师 8/8 个结构优化算例统一取值（day1+day2 的结构/晶胞优化） | 二维异质结 `mos2ws2` 用 0.050 | `[算例]` `day1/*/KPOINTS` 第 1 行、`day2/*/KPOINTS` 第 1 行 |
| `R` | 0.04 一般；0.03 / 0.02 精确 | 通用 | 讲义两套刻度（`R` 与 `ka`）没有给出换算，容易误用 | `[讲义]` L1 P20 |
| `ka = |a_i| × N_i` | d 区金属 ≈ 30 Å；普通金属 ≈ 25 Å；半导体 ≈ 20 Å；绝缘体 ≈ 15 Å | 按晶格矢量长度定三方向密度比 | 讲义**明确要求**测试收敛性；且自己"松绑"说文献里更粗的也有 | `[讲义]` L1 P21 |
| `R` ↔ `ka` 换算 | `ka = 1/R`（故 R=0.04 ↔ ka=25 Å） | 正交/近正交体系 | **本文件推断**，讲义未写；由 4 个 `KPOINTS` 反推归纳 | `[待核对]` |
| 自动网格公式 | `N_i = int(max(1, R_k·|b_i| + 0.5))`，`R_k = 2π/KSPACING` | 官方给出的四舍五入取整实现 | 与 vaspkit 的 R 不是同一个量，不要互相代入 | `[官方]` `references/official/pages/KPOINTS.md` |
| 网格比例 | `N_1:N_2:N_3 = |a_1|^{-1} : |a_2|^{-1} : |a_3|^{-1}` | 体心四方 / 体心正交 | fcc、六方、fcc-正交**只用 Γ 居中**网格 | `[官方]` `references/official/pages/KPOINTS.md` |
| 真空方向 | 网格取 **1** | slab / 二维材料（c 方向是真空） | 个别算例取 5（fe2o3 体相是 6×6×6，不是 slab） | `[算例]` `day1/GaN`=9×9×**1**、`day1/mos2`=9×9×**1**、`day2/au111-opt`=5×5×**1** |
| 算 DOS 时的 k 点 | 「比结构优化更大」 | DOS 单点 | 讲义**只给定性说法，全文无数值**；实操只能靠 vaspkit 的 R 档位加严 | `[讲义]` L2 P46；缺口见 §4.2 |
| k 点 ≤ 3 时 | 不能配 `ISMEAR=-5` | 大胞 Γ 点计算 | 见 §1 S9 / §5 E4 | `[讲义]` L2 P46/P47；`[算例]` `day2/c`（NKPTS=3）、`day2/mos2ws2`（NKPTS=3）都改用了 `ISMEAR=0` |

### 0.3 真空层、slab 层数、固定层数

| 量 | 典型值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|---|
| 真空层厚度 | **≈15 Å** | 二维材料 / slab（反推自 4 个算例：GaN 14.9999958 Å、Ag ≈15.0 Å、MoS₂/WS₂ ≈15.3 Å、OER slab c=15 Å） | `au111-opt`（含 O）≈12.5 Å；`ni-co` 从 CO 顶到镜像底仅 ≈7.4 Å（**偏小**） | `[算例]` `day1/GaN/POSCAR`、`day2/{Ag,mos2ws2,au111-opt,ni-co}/POSCAR`；`[讲义]` L1 P76（异质结"c 增大 15 埃"） |
| 真空层厚度 | 「上下各保持一定的真空距离」 | 表面计算 | **讲义全文没有任何数值判据**；vaspkit 自己反而提示要检查真空能级对真空层厚度的收敛 | `[讲义]` L2 P62、L2 P137 |
| slab 总厚度 | **10–15 Å** | 层数不好数的体系 | **单一来源**，且是"够用"不是收敛测试结论 | `[答疑]` D4-P9/D4-P10 `[待核对]` |
| slab 层数 | Ni(100) 取 **6 个原子层** | Ni(100)-CO 态密度分析 | — | `[讲义]` L2 P59；`[算例]` `day2/ni-co/POSCAR` = 24 Ni（6 个 z 层 ×4）✓ |
| slab 层数 | Au(111) **5 层**、Ag(111) **4 层** | 对应算例 | 讲义**没给** Au/Ag 的层数依据 | `[算例]` `day2/au111-opt`、`day2/Ag`；判据缺失见 `[待核对]` |
| 固定层数 | **下两层** | 金属 slab 表面优化（Ni(100)、Au(111)、Ag(111) 三例一致） | Au(111) 5 层里固定最下 2 层=40%；Ni(100) 6 层里固定 2 层=33% | `[讲义]` L2 P61/P136/P141；`[算例]` `au111-opt`/`Ag`/`ni-co` 的 `Selective Dynamics` ✓ |
| 固定层数 | 「下两层或者三层；让可弛豫的原子等于或多于被固定的层数」 | slab 经验规律 | **"层"指原子层还是双层不明确**；GaN 算例固定了 4 个原子层（=2 个 GaN 双层）+ 赝氢，可弛豫 8 层，满足后半句 | `[讲义]` L1 P15 `[待核对]` |
| 固定层数 | 二维材料**不用固定** | 单层/少层二维材料 | 只有 slab 类材料才固定下面几层 | `[答疑]` D4-P23/D4-P24 |

### 0.4 电子步收敛 EDIFF

| 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| 默认 `1E-4` | VASP 默认 | **不要用于生产计算** | `[官方]` `references/official/pages/EDIFF.md` |
| **`1E-6`** | 官方给的"最佳折中"；结构优化/晶胞优化 | 大体系或 `METAGGA` 下 1E-7/1E-8 可能做不到 | `[官方]` `references/official/pages/EDIFF.md` |
| **`1E-7`** | 有限差分类计算（声子/频率）；过渡态；力精度不够时 | — | `[官方]` 同上；`[讲义]` L3 P26/P30（频率）、L3 P129/P146（过渡态） |
| `1E-5` | 过渡态"粗收敛"取初猜那一步；一般结构优化下限 | — | `[讲义]` L3 P129 注、L3 P165；L3 P26 |
| `1E-8` | GaN 算例实测值 | 该 INCAR **风格与其余三个算例明显不同**（无 ENCUT/NCORE/KPAR/SYSTEM，标题为别的工具链），**不宜当讲师推荐值** | `[算例]` `day1/GaN/INCAR`；判断见 `learn_L1.md` C2 |
| 结构/晶胞优化实测 | 4 个算例中 3 个写 `1E-6` | 无一个用 `1E-5` | `[算例]` `day1/{fe2o3,mos2,vdw-df2}/INCAR`；`[讲义]` L1 P28 的"结构优化/MD 1E-5"与全部算例冲突 |

> ⚠ **讲义 L1 P28 与算例、与讲师自己的模板三处不一致**（讲义 1E-5 / 模板 1E-6 / 算例 1E-6~1E-8）。裁定见 `learn_L1.md` §4 C1。本文件给出的操作默认是 **1E-6**。

### 0.5 离子步收敛 EDIFFG

| 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| 正值（如 `0.001`） | 按**能量变化**判停 | 不推荐用于优化 | `[官方]` `references/official/pages/EDIFFG.md` |
| **负值** | 按**所有原子受力范数 < |EDIFFG|** 判停；通常更方便 | — | `[官方]` `references/official/pages/EDIFFG.md` |
| `0` | 跑到 `NSW` 步就停 | 只用来强制固定步数 | `[官方]` 同上 |
| **`-0.02`** | 表面/结构优化（`ISIF=2`） | — | `[讲义]` L1 P29；`[算例]` `day1/GaN/INCAR` = `-2E-02` ✓ |
| **`-0.01`** | 晶胞优化（`ISIF=3`）；表面优化；OER 全套；VASPsol 两组 | 讲义 P31 自称"结构优化"模板却用 −0.01，与 P29 冲突 | `[算例]` `day1/fe2o3`、`day1/mos2`、`day2/ni-co`、`oer/*`、`vaspsol-*` |
| **`-0.03`** | 过渡态（CI-NEB / Dimer）模板值 | **难收敛可放宽到 −0.05**；但三个真实 TS 算例写的是 −0.01，只有环己烷那套写 −0.03 | `[讲义]` L3 P129/P147；`[算例]` `5-ts/8-1-ex1-O-Au/ts-{cineb,dimer}/INCAR` = −0.01 |
| `-0.01` | 频率计算 | 讲义同页说"NSW 和 EDIFFG 都不用设置或取任意值，NSW 不能取 0"，与示例自相矛盾 | `[讲义]` L3 P30 |
| −0.5 | 过渡态**粗收敛**拿初猜那一步 | 仅此一步，参数无严格要求 | `[讲义]` L3 P165 |
| 单位提醒 | `EDIFFG` 单位是 **eV/Å**（力）；`EDIFF` 单位是 **eV**（能量） | 两者默认相关：`EDIFFG` 默认 = `EDIFF×10` | `[官方]` `references/official/pages/EDIFFG.md` |

### 0.6 SIGMA / ISMEAR

| 组合 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| `ISMEAR=-5`（Blöchl 四面体） | DOS/PDOS 单点、态密度图 | **`NKPT<4` 直接报错**；**结构优化不能用**（费米面处占据处理不好→力有百分比误差）；此时程序**不读 `SIGMA`**；**必须用 Γ 居中网格** | `[官方]` `references/official/pages/ISMEAR.md`；`[讲义]` L2 P36/P46/P47；`[官方]` `references/official/pages/KPOINTS.md`（Γ 居中） |
| `ISMEAR=1` + `SIGMA=0.2` | 金属体系（讲义"金属(1, 0.2)"档） | `SIGMA` 官方默认就是 **0.2** | `[讲义]` L1 P28；`[官方]` `references/official/pages/SIGMA.md` |
| `ISMEAR=0` + `SIGMA=0.05` | 非金属（半导体/绝缘体/二维） | 讲义口径；4/4 个 day1 算例都照此执行 | `[讲义]` L1 P28；`[算例]` `day1/*/INCAR` |
| `ISMEAR=0` + `SIGMA=0.01` | 分子（放进大盒子里的孤立分子） | 讲义口径 | `[讲义]` L1 P28 |
| `ISMEAR=0/1` | **k 点 ≤ 3 或只有 Γ 时做 DOS** | 这是 `-5` 的替代，"定性上完全没有问题" | `[讲义]` L2 P47 |
| `ISMEAR>0`（Methfessel-Paxton） | 金属 | 官方警告：**绝缘体会给出非物理的部分占据** | `[官方]` `references/official/pages/ISMEAR.md` |
| `ISMEAR=-5` vs 算例 | 6 个 day2 算例里**只有 1 个**用了 −5（`al2o3`，NKPTS=115） | `Ag`(13)/`au111-opt`(13)/`ni-co`(5) 本可用 −5 却用了 1 —— 属"优化步 INCAR 直接复用" | `[算例]` `day2/*/INCAR` + `IBZKPT`/`OUTCAR` |

### 0.7 POTIM

| 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| `0.5` | 默认；`IBRION=1,2,3` 的通用档 | 答疑说"一般用默认 0.5 就可以" | `[官方]` `references/official/pages/POTIM.md`；`[答疑]` D1-P38 |
| **`0.2`** | 结构/晶胞优化实操值；"初始结构不好"档 | 讲师全部模板与 6 个真实优化算例都写 0.2；**答辩稿与算例在这一条上口径不同但不矛盾** | `[讲义]` L1 P29/P31/P35/P46；`[算例]` `day1/{fe2o3,mos2,vdw-df2}`、`day2/au111-opt`、`oer/*` |
| `0.1` | 个别算例（`day2/Ag`） | — | `[算例]` `day2/Ag/INCAR` |
| **`0.015`** | `IBRION=5` / `6` 频率计算的位移宽度 | VASP 5.1+ 会把不合理的 `POTIM` 自动重置为 0.015 Å | `[官方]` `references/official/pages/POTIM.md`；`[讲义]` L3 P30 |
| **`0`** | `IBRION=3` 过渡态（VTST 生效标志） | 必须配 `IBRION = 3` | `[讲义]` L3 P129/P131/P146；`[算例]` `ts-cineb`/`ts-dimer`/`day3/ts/dim` |
| `1`（fs） | `IBRION=0` MD 时间步长 | **`IBRION=0` 时不给 `POTIM` 会立刻崩** | `[官方]` `references/official/pages/POTIM.md`；`[答疑]` D2-P48 |

### 0.8 NELM / NELMIN / NELMDL

| 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| `NELM = 60`（默认） | 官方默认值 | 官方原话："**40 步内不收敛，很可能就根本不会收敛**"，此时应改 `ALGO`/`LSUBROT`/混合参数，而不是加步数 | `[官方]` `references/official/pages/NELM.md` |
| `NELM = 300`（或以上，500） | 讲义建议；3 个 day1 算例 + 全部 day2/day3/day4 算例 | `GaN` 只写 60（该算例属另一工具链） | `[讲义]` L1 P28；`[算例]` 批量 |
| `NELMIN = 5` | 最小 SCF 步数 | `GaN` 写 6 | `[讲义]` L1 P28 |
| `NELMDL` | 负值 = **只在第一个离子步做延迟**（通常推荐） | 默认值分三档：`ISTART=0/INIWAV=1/IALGO=48或50` → **−12**；有 `WAVECAR` → **0**；其他 → **−5** | `[官方]` `references/official/pages/NELMDL.md` |
| `NELMDL` | 表面、金属团簇、低维体系**强烈依赖这个延迟** | 官方原话："没有延迟，VASP 很可能不收敛，或至少收敛速度显著变慢" | `[官方]` `references/official/pages/NELMDL.md` |
| `NELMDL` | 讲义说"难收敛体系取 −20" | 3 个有 OUTCAR 的算例都回显 `NELMDL = 0`（均 `ICHARG=1`）；样本不足以确定一般规则 | `[讲义]` L1 P28 `[待核对]` |

### 0.9 LREAL

| 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| `.FALSE.`（默认） | 倒空间投影；小体系、材料计算 | — | `[官方]` `references/official/pages/LREAL.md` |
| **`Auto`（推荐用于实空间）** | 官方建议：**原子数 > ~30 的体系**用实空间投影 | 官方强调只用 `Auto`，不用 `On`/`.TRUE.` | `[官方]` `references/official/pages/LREAL.md` |
| 精度代价 | `PREC=Normal` 下实空间误差与 wrap-around 误差同量级；`PREC=Accurate` 下通常 < 1 meV/atom | 想算能量差时，**bulk 与 slab 必须用完全相同的 `ENCUT`/`PREC`/`LREAL`/`ROPT` 设置** | `[官方]` `references/official/pages/LREAL.md` |
| 误差处理 | 用 `LREAL=Auto` 弛豫，最后再用 `LREAL=.FALSE.` 做一次单点拿精确能量 | 官方明说的补救路径 | `[官方]` `references/official/pages/LREAL.md` |
| 讲义口径 | "材料计算 `.FALSE.`，表面计算 `Auto`" | **3 个 slab/2D 算例全用 `.FALSE.`**（MoS₂ 3 原子、GaN 13 原子都是小体系）；讲义的表述缺了"体系大小"这个前提 | `[讲义]` L1 P28；`[算例]` `day1/{mos2,vdw-df2,GaN}/INCAR` 均 `.FALSE.` |

### 0.10 PREC

| 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|
| `Normal`（默认） | 多数常规计算 | — | `[官方]` `references/official/pages/PREC.md` |
| `Accurate` | 高精度受力、声子/频率、应力张量、**任何要算二阶导数的场合**；`ELF` 计算；力不收敛时的处方 | 内存与耗时上升 | `[官方]` `references/official/pages/PREC.md`；`[讲义]` L2 P150（ELF）、L3 P151/P156 |
| `High` | 与 `Accurate` 并列可用于 ELF | — | `[讲义]` L2 P150 |
| `Low` | 只用于快速 MD 之类、算力真的紧张时 | 官方明确不建议常规使用 | `[官方]` `references/official/pages/LREAL.md` |
| 实操惯例 | **不写 `PREC`，出问题再上 `Accurate`** | 全部讲师模板与真实算例里 `PREC` 都是注释状态 | `[算例]` `ts-cineb/INCAR`、`ts-dimer/INCAR`（`# PREC = Normal` / `# PREC = Accurate`） |
| 附带 | `ADDGRID=.TRUE.` 有时能再改善力精度，但**用户反馈互相矛盾** | 讲义给"一般结构优化 `.FALSE.`、电子结构高精度 `.TRUE.`"，而 `GaN` 纯结构优化却开了 `.TRUE.` | `[官方]` `references/official/pages/PREC.md`；`[讲义]` L1 P28；`[算例]` `day1/GaN/INCAR` |

### 0.11 IVDW（色散校正）

| 值 | 含义 | 适用范围 | 证据 |
|---|---|---|---|
| `1` 或 `10` | DFT-D2 | — | `[官方]` `references/official/pages/IVDW.md` |
| **`11`** | DFT-D3 + zero damping | 物理吸附必须加；对 PBE/RPBE/revPBE/PBEsol 不需要额外参数 | `[官方]` 同上；`[讲义]` L1 P36 |
| **`12`** | DFT-D3 + Becke-Johnson 阻尼 | 同上 | `[官方]` 同上；`[讲义]` L1 P36 |
| `2` 或 `20` | Tkatchenko-Scheffler | 仅支持前六周期、**不含镧系**；**不支持 `ADDGRID=.TRUE.`**；强烈建议 `PREC=Accurate` | `[讲义]` L1 P39 `[待核对]`（纯讲义单来源） |
| `202` | MBD@rsSCS（多体色散） | 精度"基本是最好的" | `[讲义]` L1 P39 |
| `263` | MBD@rSC/FI | VASP 6.1.0 起 | `[官方]` `references/official/pages/IVDW.md` |
| `13` / `14` / `15` | DFT-D4 / libMBD / simple-DFT-D3 | 需要 VASP 6.2 / 6.4.3 / 6.6.0 与外部包 | `[官方]` 同上 |
| 11 vs 12 怎么选 | `11` 有时候**低估** vdW，`12` 有时候**高估** vdW | 两者都可用 | `[答疑]` D1-P6 |
| vdW-DF 系列（非 `IVDW`） | 用 `LUSE_VDW=.TRUE.` + `GGA=` 变体，需 `vdw_kernel.bindat` 文件 | 可体现弱相互作用对电子结构的影响；计算量大 | `[讲义]` L1 P37；`[算例]` `day1/vdw-df2/` 内有该文件 ✓ |
| vdW-DF2 实测配方 | `GGA = ML` + `LUSE_VDW=.TRUE.` + `Zab_vdW=-1.8867` + `AGGAC=0.0000` + `LASPH=.TRUE.` | 单层 MoS₂ | `[算例]` `day1/vdw-df2/INCAR`，逐条与 L1 P38 一致 ✓；`OUTCAR` 回显 `LUSE_VDW = T`、`LEXCH = 44` |

### 0.12 LDAUU / DFT+U 相关的具体数

| 量 | 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|---|
| `LDAUL` | `2  -1` | Fe₂O₃（Fe 加 d 轨道 U，O 不加） | 槽位顺序与 POSCAR 元素顺序对应（讲义未明写，被算例支持） | `[算例]` `day1/fe2o3/INCAR` + `OUTCAR` 回显 ✓ |
| `LDAUU` | **5.3**（配 `LDAUJ = 0.0`） | Fe₂O₃ 的 Fe 3d；**Ueff = U − J = 5.3 eV** | 引用 U 值**必须说明用的是哪一套写法** | `[讲义]` L1 P43/P46；`[算例]` `day1/fe2o3` |
| `LDAUU` / `LDAUJ` | **4.6 / 0.4**（Ueff = 4.2 eV） | 讲师模板 INCAR 的 DFT+U 段（注释态，5 个元素槽，`SYSTEM = H2O`，判定为通用占位符） | 与上一条**相差 1.1 eV**；`LDAUPRINT` 模板用 2、讲义与算例用 0 | `[算例]` `things to study/INCAR`；冲突见 `learn_L1.md` §3.8 |
| `LDAUTYPE` | `2` | Dudarev 方案（`Ueff = U − J`） | 官方警告：**U/J 不同的计算之间总能量不可比**；`LDAUTYPE=3` 时 `LDAUU`/`LDAUJ` 另有含义 | `[官方]` `references/official/pages/LDAUU.md` |
| `LMAXMIX` | **4** | d 轨道体系（Fe 3d） | **f 轨道体系要用 6** | `[算例]` `day1/fe2o3`；`[官方]` `references/official/pages/ALGO.md` |
| `LMAXMIX` | 加 U 时"一定要设" | DFT+U 计算 | — | `[讲义]` L1 P43 |
| 镧系（CeO₂ 等） | 基本必须加 U | f 轨道收缩、电子相关强 | — | `[答疑]` D1-P3/D1-P4 |
| +U 用不用 | CoN₄ OER 全套**没用** +U（`LDAU` 段整段注释） | 纯 PBE 结果 | 该套结果是纯 PBE 的，与文献含 U 结果不可直接比 | `[算例]` `oer/*/INCAR` |
| +U 的影响范围 | 主要改善电子结构与能量；**对原子几何、晶体结构影响有限** | — | 但真实算例确实在 +U 下做了 `ISIF=3` 晶胞优化 —— "影响有限"≠"不能一起做" | `[讲义]` L1 P42；`[算例]` `day1/fe2o3`（`LDAU=.TRUE.` + `ISIF=3`） |

### 0.13 NCORE / KPAR（并行）

| 量 | 值 | 适用范围 | 例外 / 反例 | 证据 |
|---|---|---|---|---|
| `NCORE` 默认 | `1` | **只适用于小胞、或通信带宽受限的机器**（官方条件句：*appropriate for small unit cells or machines with limited communication bandwidth*）。⚠️ 注意：**「≲8 核 / Gbit 以太网」是官方给"多慢算慢"举的例子，不是适用条件** —— 这句话以前被抄进了「适用范围」列，是个**错位**（见 CHANGELOG 的 CR-043）。 | ⚠️ **后果随规模放大**：`NCORE=1` 时「**投影函数必须完整存在每个 rank 上 ⇒ 高内存占用**」，且正交化要**全局 all-to-all 通信**（官方 `NCORE.md:19` 原句 `leading to high memory usage … heavy all-to-all communication between all ranks`）。**⚠️ 大体系（≳100 原子）+ 多 rank 下这会直接崩**：每 rank 独占一个 band、独自完成整块 FFT ⇒ 栈/内存爆 ⇒ 第一次 SCF `SIGSEGV`。**这不是性能问题，是能不能跑的问题**（见 §1 的 `LAUNCH.crash_no_scf`）。 | `[官方]` `references/official/pages/NCORE.md:19` |
| `NCORE ≈ √(可用核数)` | 官方推荐区制（现代多核机） | **现代多核集群**（官方条件句：*This is the recommended regime for modern multi-core machines*） | — | `[官方]` `references/official/pages/NCORE.md:17`（同句另注：**同时降低内存需求**（投影函数在组内共享）**与正交化成本**） |
| `NCORE = 2 ~ 每节点核数` | 现代多核集群（InfiniBand 等快互连） | 经验：`NCORE=4` 对 ~100 原子不错；**`12–16` 对 >400 原子的胞常更好**；应取每节点核数的因子 | 官方强调这只是粗guideline，正式计算前应做 `NCORE` 扫描 | `[官方]` `references/official/pages/NCORE.md` |
| 与 `NPAR` 的关系 | `NPAR = 可用核数 / NCORE`，二者严格互逆；**不要同时设**；同时出现时 `NPAR` 优先（历史原因） | — | 官方"强烈建议"用 `NCORE` 而非 `NPAR` | `[官方]` `references/official/pages/NCORE.md` |
| `KPAR` | 总核数 = `KPAR × NCORE × 能带组数` | 非 111 k 点计算可以测试最优 `KPAR` | **本文件由 2 个 LOG 归纳**，非官方页原文 | `[待核对]`（依据 `day1/fe2o3/LOG`、`day1/mos2/LOG`） |
| 讲义口径 | "懒得测试就直接用 `NCORE = 每节点核数/2`" | 提速技巧第 (1) 条 | 同一份讲义另给 `NCORE = 5`（幻灯片模板）与 `NCORE = 16`（真实算例/模板文件）**三个不同数字** | `[讲义]` L1 P48、L1 P31/P35/P46；`[算例]` 4 个 INCAR |
| 答疑口径 | 24 核机器取 **12 或 6** | 即 24/2 与 24/4 | 与讲义"核数/2"不矛盾 | `[答疑]` D1-P14 |
| `IMAGES` 同时激活时 | `可用核数 = 总 MPI 核数 / KPAR`（无其他算法相关并行时） | CI-NEB 并行约束 | CI-NEB 另有"核数必须整除插点数量"的硬约束 | `[官方]` `references/official/pages/NCORE.md`；`[讲义]` L3 P132 |
| GPU / OpenMP | `NCORE` 会被**自动重置为 1** | GPU 卸载路径或 OpenMP 线程时 | 想控制 FFT 并行度就调每 rank 的 OpenMP 线程数 | `[官方]` `references/official/pages/NCORE.md` |

> 站点纪律：本表只写"怎么选"，不写任何具体机器的核数上限、队列名或模块版本。

### 0.14 能量口径、电荷参考与几个易错默认值

| 量 | 怎么取 | 适用范围 | 证据 |
|---|---|---|---|
| 总能量（推荐） | `tail -1 OSZICAR` → 最后一个 **`E0`** | 一切要报数的场合；过渡态能量也取 DIMCAR 之外的 `E0` | `[讲义]` L1 P30、L3 P151 |
| 总能量（对照） | `OUTCAR` 的 `free energy TOTEN` 与 `energy(sigma->0)` | 讲师 OER 数据用的是 **`energy(sigma->0)`**，不是 `TOTEN` | `[算例]` `oer.xlsx` B 列与 `OUTCAR` 逐位吻合，**属数值推断** `[待核对]` |
| 离子步是否收敛 | `grep reached OUTCAR` → 找 `reached required accuracy - stopping structural energy minimisation` | slab/优化 | `[算例]` `day1/fe2o3/OUTCAR` 实测命中 ✓（与讲义逐字一致） |
| 每个离子步的 SCF 是否收敛 | 同一文件里的 `------------------------ aborting loop because EDIFF is reached ------------------------` | 每步 SCF 判据 | `[算例]` 同上，共 9 次 ✓ |
| 带电体系 | `grep NELECT OUTCAR` 读默认值，然后改 `NELECT`（吸附一个质子就减一） | 需要背景电荷的场合 | `[答疑]` D1-P12；`[答疑]` D3-P45/D3-P46（提醒可能引起背景电荷问题，或改用抗衡离子） |
| `NEDOS` | 默认 **301**；讲义建议 **1000**；模板里用过 2000 | DOS 单点 | `[算例]` `day2/Ag` 未设 → 实测 301；`day2/al2o3`=1000；`day2/ni-co`=2000 |
| `EMAX`/`EMIN` | **留默认，不要手填**；`OUTCAR` 实测会打印 `EMIN = 10.00; EMAX =-10.00`（注意符号顺序与讲义文字定义相反） | DOS 作图 | `[算例]` `day2/{Ag,ni-co,al2o3}/OUTCAR`；讲义 P34 与 P36 自相矛盾，见 `learn_L2.md` §4 C2 `[待核对]` |
| 费米能级 | `grep E-fermi OUTCAR`；**同一结构不同次计算会漂移约 0.01 eV**（实测 5.4270 / 5.4353 / 5.4412） | 跨计算比较前必须 `shift` 到 0 | `[算例]` `day2/al2o3/OUTCAR` vs `things to study/al2o3/DOSCAR` |
| 偶极校正 | `LDIPOL = .TRUE.` **必须**配 `IDIPOL`（slab 用法向，通常 3；孤立分子用 4） | 不对称 slab、带电分子 | `[官方]` `references/official/pages/LDIPOL.md`、`references/official/pages/IDIPOL.md`；`[答疑]` D1-P44 |
| 偶极校正的硬约束 | **带电体系 + 非立方超胞 + `LDIPOL=.TRUE.` → VASP 直接停** | 带电缺陷/带电 slab | `[官方]` `references/official/pages/LDIPOL.md` |
| 偶极校正的代价 | 电子基态收敛**可能显著变慢**（需要更多电子步） | 不对称 slab | `[官方]` `references/official/pages/LDIPOL.md` |
| 偶极校正什么时候加 | **结构优化的时候就加上**（不是只加到单点） | 不对称表面 | `[答疑]` D3-P3/D3-P4 |
| `ISYM` | `0` 表示完全不用对称（但假定 Ψ_k = Ψ_−k）；官方说 **MD（`IBRION=0`）应该设 0** | MD；对称性被吸附物/缺陷破坏时 | `[官方]` `references/official/pages/ISYM.md` |
| `ISYM` 实测冲突 | 随课 OER 全套 `#ISYM = 0` 被注释 → 实际 `ISYM = 2`；而讲师在 D4-P21 说"需要设 `ISYM = 0`" | 复现随课数值 → 保持 2；按讲师建议做 → 显式写 0 | `[算例]` `oer/*/OUTCAR` vs `[答疑]` D4-P21/D4-P22 |
| `LORBIT` + `ISYM` | VASP **< 6** 且 `LORBIT >= 11` 且 `ISYM = 2` 时有已知问题 | 老版本做 lm 分解 PDOS | `[官方]` `references/official/pages/LORBIT.md` |
| `LMAXMIX` 的反向坑 | 离子位移大、或 MLFF 跳步时用 `MAXMIX` 会导致电子步**发散或奇怪报错**；判据是看 `OSZICAR` 的 `RMS(c)` 列突然增大 | 结构弛豫/机器学习 | `[官方]` `references/official/pages/MAXMIX.md` |
| 混合参数参考 | `AMIN = 0.4` 通常收敛良好；`AMIX` 强依赖体系，**金属应取小，如 `AMIX = 0.02`** | 电子步难收敛时 | `[官方]` `references/official/pages/IMIX.md` |

---

## §1 症状 → 诊断 → 处方

> **每条四要素齐全**：症状（可 grep 的原文片段）／诊断（确认过的原因）／处方（改哪一处、改成什么）／判据（怎么知道改对了）。
> **凡本文件在现有资料里找不到报错原文或确认过的原因，一律不写**，只在 §1.9 的"资料没覆盖"清单里列名。
> 编号 `S<n>`；§5 的报错速查表用这些编号回指。

### 1.1 SCF 电子步不收敛

#### S1 · SCF 用尽 NELM 步数仍未收敛

- **症状**：`OUTCAR`/`stdout` 里 `DAV:` / `RMM:` 行数达到 `NELM`（如 60 或 300）后停住；`OSZICAR` 里 `dE` 在最后若干步仍在 1E-3 量级抖动，没有出现 `aborting loop because EDIFF is reached`。用 `grep -c "aborting loop because EDIFF is reached" OUTCAR` 计数，若某离子步缺这个字符串，那一步就是没收敛。
- **诊断**：`[官方]` 明确给了判据性结论：**如果 40 步内不收敛，很可能根本不会收敛**；此时要重考虑的是 `ALGO`/`LSUBROT` 与混合参数，而不是把 `NELM` 调大（`references/official/pages/NELM.md`）。另外低维/表面/金属团簇体系**强烈依赖初始非自洽延迟**（`references/official/pages/NELMDL.md` 原文：没有延迟时"VASP 很可能不收敛，或至少收敛速度显著变慢"）。
- **处方**（按顺序做，每步只改一处）：
  1. **先确认延迟开着**：检查 `INCAR` 有没有显式写 `NELMDL`。默认分档是 `ISTART=0 & INIWAV=1 & IALGO=48/50` → `-12`；有 `WAVECAR` → `0`；其他 → `-5`（`references/official/pages/NELMDL.md`）。**有 `WAVECAR` 时默认 0，等于把延迟关掉了** —— 这是表面/低维体系最常见的隐式坑。处方：显式写 `NELMDL = -5`（或 `-12`）。
  2. **换成对 slab/真空体系更合适的算法族**：`[官方]` 原话是"长条几何、含真空的体系、slab、表面：优先用 mixing（自洽循环）类算法（`Normal` 或 `Fast`）"，因为这些体系容易 **charge sloshing**；并指出可通过调 `AMIX`、`BMIX` 等混合标签缓解（`references/official/pages/ALGO.md`）。
  3. **改混合参数**：`AMIN = 0.4` 通常收敛良好；`AMIX` 强依赖体系，**金属要小，如 0.02**（`references/official/pages/IMIX.md`）。金属/磁性体系另有默认档：`IMIX=4, AMIX=0.4, AMIN=min(0.1,AMIX,AMIX_MAG), BMIX=1.0, AMIX_MAG=1.6, BMIX_MAG=1.0`（`references/official/pages/AMIX_MAG.md`）。
  4. **检查 `MAXMIX` 是否在害你**：`[官方]` 明确"当 `OSZICAR` 的 `RMS(c)` 列出现残差范数突然增大时，试着从 INCAR 里删掉 `MAXMIX`"（`references/official/pages/MAXMIX.md`）。
  5. **检查 `ALGO`**：`ALGO = Fast`/`VeryFast` 便宜但**更不稳**；`VeryFast` 需要好的初始轨道且**不支持杂化泛函**（`references/official/pages/ALGO.md`）。
  6. **最后才动 `NELM`**：从默认 60 提到 300 只是给你观察振荡的机会，不是解法。
- **判据**：`grep -c "aborting loop because EDIFF is reached" OUTCAR` 的次数 = 离子步数（每个离子步都命中）；且 `OSZICAR` 最后 5 行的 `dE` 单调掉到 1E-6 以下。

#### S2 · 能量在电子步之间来回振荡、`rms(c)` 不下降

- **症状**：`OSZICAR` 每行的最后一列（自洽循环算法下是 `rms(c)`）在 1E-1 ~ 1E0 之间来回跳，不单调下降。
- **诊断**：`[官方]` 给了这一列的语义与判读法：`rms(c)` 是"电荷密度在混合器中的均方根变化"；**「把 `rms(c)` 对电子步 N 作图，值大说明电荷密度还在变、可能在涨落（charge sloshing）」**（`references/official/pages/ALGO.md`）。
- **处方**：
  1. 打印足够细的电子步信息：`NWRITE = 2`（或 3）—— `[官方]` `EDIFF`/`EDIFFG` 页都提示用 `NWRITE=2,3` 拿每电子步信息（`references/official/pages/EDIFF.md`、`references/official/pages/EDIFFG.md`）。
  2. slab/表面/真空体系按 `[官方]` 建议走 **mixing 类算法 + 调 `AMIX`/`BMIX`**（`references/official/pages/ALGO.md`）。
  3. 金属体系把 `AMIX` 降到 0.02 量级（`references/official/pages/IMIX.md`）。
  4. 若体系有 f 电子，`LMAXMIX = 6`（`references/official/pages/ALGO.md`：`LMAXMIX` 设对才能让自洽循环快速收敛）；d 电子用 4。
- **判据**：`rms(c)` 在 10 步内单调下降 3 个数量级；`OSZICAR` 的 `dE` 同步单调。

#### S3 · 用 `IMIX=1` 的 Kerker 混合时直接崩（浮点异常）

- **症状**：程序在电子步早期异常退出，日志无明确物理报错。
- **诊断**：`[官方]` 警告：`BMIX = 0` **在某些平台会引起浮点异常**（`references/official/pages/IMIX.md`）。
- **处方**：`IMIX = 1` 时不要把 `BMIX` 设成 0；想要纯 straight mixing 就用 `BMIX = 0.0001`（`references/official/pages/IMIX.md`）。
- **判据**：任务能越过前几个电子步不崩。

#### S4 · 直接优化类算法（`ALGO = All/Conjugate`、`Damped`）下没有 `rms(c)` 列

- **症状**：`OSZICAR` 表头最后一列写成 `ort` 而不是 `rms(c)`。
- **诊断**：**这不是故障**。`[官方]`：直接最小化算法直接更新密度、不过混合器，因此最后一列是 `ort`，报告轨道的正交性误差（`references/official/pages/ALGO.md`）。
- **处方**：不要去找不存在的 `rms(c)`；改看 `dE` 与 `ort`：`ort` 应保持小。
- **判据**：`dE` 掉到 `EDIFF` 以下并出现收敛串。

#### S5 · 换了 `ALGO` 之后结果/力出现差别

- **症状**：同一结构、同一参数，只改 `ALGO`，力或总能末位有差别。
- **诊断**：`[官方]` 说明 `Fast`/`VeryFast` 下**空带与恰好占据的带优化得不那么充分**（`WEIMIN` 相关），因此轨道、力、应力精度**低于** `Normal` 或 `All`（`references/official/pages/ALGO.md`）。
- **处方**：需要精确力/应力/二阶导数的步骤（频率、过渡态、弹性）用 `Normal` 或 `All`；`Fast`/`VeryFast` 只用于拿初猜。
- **判据**：换回 `Normal` 后力的最大值稳定；过渡态/频率步骤能给出预期的虚频数（见 S13）。

#### S6 · `EDDDAV`/`ZHEGV` 之类线性代数报错

- **状态**：**本文件在现有资料里找不到该报错的原文与确认原因**，不写。见 §1.9。

### 1.2 几何优化不收敛 / 振荡 / 力不下降

#### S7 · 离子步跑满 `NSW` 仍没收敛（没出现收敛串）

- **症状**：`grep -c "reached required accuracy" OUTCAR` 返回 0；`OSZICAR` 的 `F=` 行数 = `NSW`。力列（`FORCES: max atom, RMS`）在最后若干步仍在 `|EDIFFG|` 之上打转。
- **诊断**：`[官方]` 给的第一顺位原因是**电子步精度不够**：`IBRION` 页明确提示"可能需要设 `EDIFF <= 1E-6`，因为默认（1E-4）常常导致不可接受的大误差"（`references/official/pages/IBRION.md`）。`[讲义]` 在过渡态一节给了同一结论的强表述：**"好多过渡态计算不收敛原因都是因为力的精度不够"**（L3 P129）。
- **处方**（按性价比排序）：
  1. `EDIFF = 1E-6`（若原本是默认 1E-4）；仍不行收到 `1E-7`。
  2. 加 `PREC = Accurate`（`[官方]`：`Accurate` 用于"精确受力、声子、应力张量，以及一般要算二阶导数的场合"；`references/official/pages/PREC.md`）。
  3. 算法：`IBRION = 2` → 试 `1` 或 `3`（`[讲义]` L1 P29）。
  4. 步长：`POTIM` 从 0.5 降到 0.2（讲师全部算例的实操值，`[算例]` 6/6）。
  5. 检查力收敛标准是否过严（`[讲义]` L3 P156 明确把"力的收敛标准过于严格"列为三个可能原因之一）。
- **判据**：`grep reached OUTCAR` 命中 `reached required accuracy - stopping structural energy minimisation`（`[算例]` `day1/fe2o3/OUTCAR` 实测该串存在）；且 `grep "FORCES: max atom, RMS" OUTCAR | tail -3` 的最后一行第一个数 < `|EDIFFG|`。

#### S8 · 几何优化能量来回振荡、结构反复

- **症状**：`OSZICAR` 的 `F=` 序列上下摆，`d E` 不单调变小；`CONTCAR` 与原结构比原子来回动。
- **诊断**：`[官方]` 指出 `IBRION=1/2/3` 下 `POTIM` 是步宽缩放常数，而**准牛顿算法（`IBRION=1`）对这个参数特别敏感**（`references/official/pages/POTIM.md`）。`IBRION=3` 是阻尼 MD 类型，步长过大也会来回摆。
- **处方**：先降 `POTIM`（0.5 → 0.2 → 0.1），再考虑换 `IBRION`（2 ↔ 1 ↔ 3）。不要同时改。
- **判据**：`OSZICAR` 的 `F=` 序列变为单调（允许小抖动）下降，`d E` 逐次变小。

#### S9 · 键长/力出现"毛刺"，或 DOS 曲线毛刺很多

- **症状**：DOS 曲线在能量轴上有很多尖刺。
- **诊断**：`[讲义]` 给的原因是 k 点取样不够（L2 P48 注意事项 (5)：`NEDOS`/`EMAX`/`EMIN` **只影响作图效果**、不影响实际计算 —— 所以调 `NEDOS` 治不了毛刺）。
- **处方**：**增大 k 点数目**，或改用 `ISMEAR = 0`（`[讲义]` L2 P33 原文）。
- **判据**：同一体系加密 k 点后毛刺减少；`NEDOS` 从 301 加到 1000 只让曲线更细，不改变毛刺性质。
- **例外/反例**：`[算例]` `day2/Ag` 是 DOS 步但**没设 `NEDOS`**（实测 301），说明"建议值"在实操中常被跳过 —— 但不影响定性结论。

#### S10 · 频率计算报错说离子步数不对

- **症状**：`OUTCAR` 里 `Finite differences progress:` 块的 `Degree of freedom: 1/ N` 与你预期的 3N 不符。
- **诊断**：这里的分母**不是整个体系的 3N**，而是 **3 ×（放开的原子数）**。讲义 P31 原文写"体系中的自由度 3N"，但同页输出是 `1/3`（21 原子体系），自相矛盾。已被两个真实算例证实：`4-thermo/7-4-Au-O-freq/ts/OUTCAR`（21 原子、只放开 1 个 O）显示 `3/3`；同目录 `o2/OUTCAR`（2 原子全放开）显示 `6/6`。
- **处方**：按 **实际离子步数 = 3 × 放开原子数 × `NFREE` + 1** 去核对（`NFREE=2` 时即讲义 P31 的"6×放开原子数 + 1"）。不要按 3N 期望。
- **判据**：`grep "F=" OSZICAR | wc -l` = 3 × 放开原子数 × `NFREE` + 1。实测：Au-O 体系放开 1 个 O、`NFREE=2` → 7 行 ✓；O₂ 全放开 2 个原子 → 13 行 ✓。

#### S11 · `OUTCAR` 里 `NSW` 回显与 INCAR 写的不一样

- **症状**：INCAR 写 `NSW = 300`，`OUTCAR` 回显 `NSW = 289`（21 原子体系）或 `NSW = 61`（2 原子体系）。
- **诊断**：**`IBRION = 5` 下 VASP 会改写 `NSW`**。讲义也自认这一点："`NSW` 和 `EDIFFG` 都不用设置或取任意值。`NSW` 不能取 0"（L3 P30）。**具体的改写公式在现有资料里没有依据**。
- **处方**：频率计算里 `EDIFFG`/`NSW` 取什么值都不影响结果，**但 `NSW` 不能取 0**；判断频率计算是否跑完，看 `Finite differences progress` 是否走到 `Total: N/N`，不要看 `NSW`。
- **判据**：`grep -3 Finite OUTCAR` 的 `Total:` 分母跑到满。
- **附带坑**：`OUTCAR` 里 `NFREE` 的回显文字是给 `IBRION=2` 用的（实测 `NFREE  =      2    steps in history (QN), initial steepest desc. (CG)`），**看回显文字会被误导**（`[算例]` `7-4-Au-O-freq/*/OUTCAR`）。

### 1.3 虚频问题

#### S12 · 极小点（IS/FS/吸附态）算出来有虚频

- **症状**：`grep cm OUTCAR` 出现 `f/i=` 行，且虚频不是"可忽略的小值"。
- **诊断**：优化只能保证结构是**驻点**（一阶导为零），不保证是极小点；需要用频率确认虚频个数。`[讲义]` L3 P25 原文："我们计算的结构优化和过渡态搜索任务只能保证得到的结构是驻点…还要进一步计算频率来确定虚频的个数。"
- **处方**：
  1. 确认**优化与频率在同一级别下做**（同一泛函、格点精度、溶剂模型、vdW 校正）；级别不同等于"振动分析不是在势能面的极小点位置进行的，结果没有意义"（`[讲义]` L3 P26）。
  2. 把 `EDIFF` 收到 `1E-7`（频率计算的讲义取值，`[讲义]` L3 P26/P30）。
  3. 加 `PREC = Accurate`。
  4. 若虚频很小且方向无物理意义，用更严的优化再收一次结构。
- **判据**：极小点**没有虚频**；`grep "f/i" OUTCAR` 返回空（对只放开吸附物的体系）。
- **例外**：**气态分子的最低 6 个频率里出现虚频可以直接无视** —— `[讲义]` L3 P36 原文："VASP 算出的分子的频率有 3N 个。实际上其中有 6 个是属于平动和转动在振动自由度上的投影，这最小的 6 个频率中可能出现虚频，这些频率可以直接无视。"这一条**只对孤立分子成立**，对表面过渡态不成立。

#### S13 · 过渡态收敛了，但频率没有虚频 / 有两个以上虚频

- **症状**：TS 结构收敛，`grep cm OUTCAR` 得到 0 个 `f/i`，或多个 `f/i`。
- **诊断**：`[讲义]` L3 P157 给出的诊断很直接：**没有虚频 → 计算肯定是错的，最可能还是力的精度不够；多个虚频 → 也可能是力精度不够**。
- **处方**：
  1. `EDIFF = 1E-7`（严格化）。
  2. `PREC = Accurate`。
  3. 多个虚频时**换用 Dimer 方法**（`[讲义]` L3 P157）。
  4. 检查初猜/插点结构是否合理（见 S19、S20）。
- **判据**：恰好 1 个虚频；且虚频值一般 **> ~100 cm⁻¹**（`[讲义]` L3 P33：虚频太小说明 TS 可能找得不对，要看振动方向）。实测锚点：`4-thermo/7-4-Au-O-freq/ts/OUTCAR` 的 `3 f/i= 3.964289 THz ... 132.234445 cm-1 16.394988 meV`。
- **例外/反例**：>100 cm⁻¹ 是**表面吸附体系的经验门槛，讲义没给出处**；同批资料里的**分子**（非过渡态）虚频可以只有 0.007 THz 量级，且按 P36 可以无视。所以这个门槛**不能套到分子上**。

#### S14 · 算频率的文件夹选错了（对非驻点算频率）

- **症状**：对 CI-NEB 路径上每个 image 都算频率，得到一堆没有意义的虚频。
- **诊断**：`[答疑]` D4-P7/D4-P8 原话："**其他的点不是驻点，算频率没有意义**"；`[答疑]` D3-P33/D3-P34 更明确："**频率只算能量最高的点即可**"。
- **处方**：只对 `nebef.pl` 给出的**能量最高的 image** 做频率验证；`[讲义]` L3 P162 同口径："实际上一般我们只关注能量最高的 image 能量（用 `nebef.pl` 获取）"。
- **判据**：只提交 1 个频率任务，得到恰好 1 个虚频。

#### S15 · ZPE 算出来跟别人不一样

- **症状**：同一批频率，你的 ZPE 比别人大。
- **诊断**：`[讲义]` L3 P61 的说法是"`grep cm OUTCAR`，取最后一排 meV 的能量和，再除以 2000"，但这条**只在"列出的所有频率都是真实振动模式"时才成立**。含虚频的体系（分子、含虚频的 TS）机械求和会把虚频也算进去。同一份讲义 P71 自己算 O₂ 时**只取了第一个频率**（"由于双原子分子有 3N−5 个振动自由度，所以只需要取第一个频率即可。ZPE = 194.29/2000 = 0.097145 eV"），而不是 6 行全加。
- **处方**：ZPE = ½ Σ hν，**只对真实的 3N−6（线性分子 3N−5）个实频求和，虚频不计入**。逐行看 `f/i` 标记，**不要数"前几行"**（`[讲义]` L3 P37 的"前 3N−6 个"依赖输出顺序，不能当通用规则）。
- **判据**：把 O₂ 的 6 行 meV 全加 = 216.711 → /2000 = 0.10836 eV ≠ 讲义给的 0.097145 eV；按只取第一行则复现 0.097145 ✓。用同一套规则复算你自己的体系能自洽。
- **来源标记**：`[待核对]`（"虚频不计入"是本文件由 P71 算例反推的结论，讲义 P61 字面并未这么写）。

### 1.4 过渡态搜错鞍点 / NEB 不收敛

#### S16 · CI-NEB 中间点能量比初态和末态都低

- **症状**：`nebef.dat` 的能量剖面里 image 1..N−1 有低于两端点的值；或能量剖面出现"下降"。
- **诊断**：`[讲义]` L3 P154 给了两种可能：① IS 与 FS 之间还存在至少一个极小点；② **初态和末态本就不是极小点**。`[答疑]` D3-P34 用一句话概括同一件事："**能量出现下降是不对的**"。
- **处方**：
  1. 先用**更严格的精度**重新优化 IS 和 FS（`EDIFF=1E-7`、`PREC=Accurate`、`EDIFFG` 收紧），确认两端都是真正的极小点（各自**无虚频**）。
  2. 若 IS/FS 之间确实还有中间极小点，把这一步拆成两个基元步骤分别做 NEB。
- **判据**：重算后 `nebef.dat` 的中间点能量都 ≥ 两端点的较小值；对每个新判定的极小点做频率，确认无虚频。

#### S17 · CI-NEB 一开始就出现极大原子受力

- **症状**：任务刚起步，`OUTCAR`/`OSZICAR` 的力列出现 **10 eV/Å 以上**的极大值。
- **诊断**：`[讲义]` L3 P155 原话："原因肯定是**初始结构不合理**"。线性插值（`nebmake.pl`）会在两结构差异大时造出过短键 —— 讲义给的实测例子是环己烷脱氢，`(03)` image 的 **C–H 键只有 0.59 Å**，一个离子步后就偏离正确路径；同一位置 IDPP 插值是 **1.09 Å**。
- **处方**：改用**非线性插点** `idpp.py`（`python3 ~/bin/idpp.py POSCARis POSCARfs 4`），或把不合理的 `POSCAR` 手工调整后再提交。
- **判据**：把每个 image 的最短键长（尤其是形成/断裂的那根键）打出来对比。实测基线：`day3/idpp/c6h12-nebmake/03/POSCAR` 最短 C–H = **0.5916 Å**；`day3/idpp/c6h12-idpp/03/POSCAR` = **1.0879 Å**。改用 IDPP 后最短键应回到合理化学键长区间（~1.09 Å）。

#### S18 · 已经接近收敛，但力很久到不了标准

- **症状**：`nebef.pl`/`nebefs.pl` 的最后两列（能量、相对初态能量）基本不动了，但第一列（最大原子受力）就是下不去。
- **诊断**：`[讲义]` L3 P156 给了三个原因：① **力的精度不够**；② **过渡态优化算法不合适**；③ **力的收敛标准过于严格**。
- **处方**（分别对应）：
  1. `PREC = Accurate` + `EDIFF = 1E-7`。
  2. 换优化器：`IOPT = 7`，或 `IOPT = 0`（用 VASP 自带算法）。
  3. 放宽 `EDIFFG`：`-0.03` 起步，非常复杂难收敛的可以到 `-0.05`（`[讲义]` L3 P129）。
- **判据**：`nebef.pl` 输出所有 image 的最大受力都 **< |EDIFFG|**（`[讲义]` L3 P133：插多个点时**所有点**都要满足）。实测基线：`5-ts/8-1-ex2.../nebef.dat` 6 行最大受力 0.009926 / 0.019729 / 0.028569 / 0.018706 / 0.018991 / 0.009783，全部 < 0.03 ✓。
- **附带确认**：`IOPT` 只管**能不能找到** TS，**不影响** TS 能量 —— `[答疑]` D4-P41/D4-P42："如果正常计算结束，没有影响。`IOPT` 只会影响过渡态结构是不是容易找到。只要找得到，用啥 `IOPT` 参数都没影响。"

#### S19 · `nebmake.pl` 插点结构非常混乱

- **症状**：插出来的中间结构有原子重叠、异常键长键角。
- **诊断**：`[讲义]` L3 P158 给的诊断是**初态和末态的原子顺序不是一一对应** —— "这个是新手的常见错误"。
- **处方**：检查 IS 与 FS 的原子编号是否一一对应；**在计算初末态的时候就要注意不要打乱原子顺序**。检查命令：`dist.pl ini/CONTCAR fin/CONTCAR`，返回值 < 5 Å 才往下走；**数值非常大就要回头查原子顺序**（`[讲义]` L3 P125）。同一诊断也适用于 `[答疑]` D4-P55/D4-P56："初态和末态的距离是 2.8 Å，但是用 `dist.pl` 显示就是 16 Å" → "检查一下原子编号是否是一一对应的。"
- **判据**：`dist.pl` 返回值与你在 VESTA 里量到的初末态位移量级一致（该例基线 1.73920306203566 Å）。
- **例外**：`dist.pl` 返回值大**不一定**是原子顺序问题，也可能是路径本身就长；先核对顺序，再决定插点数。

#### S20 · CI-NEB 步数与预期不符 / `nebef.dat` 的能量与 `OSZICAR` 的 `E0` 对不上

- **症状**：讲义说"此例算 14 步就收敛了"，`01/OSZICAR` 里 `F=` 只有 13 行；或 `neb.dat` 第 3 列相对能量与同算例 `OSZICAR` 的 `E0` 差几 meV。
- **诊断**：`[算例]` 实测：`5-ts/8-1-ex1-O-Au/ts-cineb/01/OSZICAR` 的 `F=` 行数 = **13**（讲义 P133 说 14，差 1，原因不明）；`neb.dat` 的 image 1 相对能量 = 0.498031，而用 `OSZICAR` 的 `E0` 反算 = 0.494218，讲义 P134 给的是 0.494200。image 2 三处一致（0.268400 vs 0.268417）。
- **处方**：**报 TS 能量时用 `OSZICAR` 最后一个 `E0`，不要用 `neb.dat` 的相对能量列**（`[讲义]` L3 P151 对 Dimer 的同类提醒："这个能量不是电子熵外推到 0 的能量，故不能用作最终的过渡态能量，过渡态能量取 OSZICAR 最后一个 E0"）。`neb.dat` 只用来画剖面、判断形状。
- **判据**：`tail -1 OSZICAR` 的 `E0`；与自己的其它路径一致地取同一个量。
- **来源标记**：`neb.dat` 第 2/3/4 列的**确切语义在现有资料里没有依据**，不要据此写断言。

#### S21 · Dimer 的 Torque 不下降 / Curvature 不是负值

- **症状**：`DIMCAR` 的 `Torque` 列不往下走；或 `Curvature` 一直是正的。
- **诊断**：`[讲义]` L3 P151：旋转 Dimer 总是朝扭矩减小的方向转，`Torque < 1` 才进入平移步；**接近过渡态的标志是 Force 逐渐变小并且 Curvature 是负值**；Curvature 不是负的说明**离过渡态还较远**。
- **处方**：
  - `Torque` 不降 → 提高力的精度（更小的 `EDIFF`、`PREC = Accurate`），**或者提高 `DdR = 0.01`**（`[讲义]` L3 P151；注意 P147 的注释里默认写的是 `5E-3`，两者语境不同）。
  - `Curvature` 为正 → 不是故障，耐心等；同时检查初猜（S22）。
- **判据**：`DIMCAR` 里 `Force` 逐渐变小 + `Curvature` 转负 + `Torque < 1` 后进入平移步；收敛后 `grep converged OUTCAR` 出现 `OPT: skip step - force has converged`（`[讲义]` L3 P153）。
- **不要用的判据**：`DIMCAR` 的 `Force` 列 **< |EDIFFG| 不是收敛标准**；判断收敛的标准是**最大原子受力 F < |EDIFFG|**（`[讲义]` L3 P149/P150）。讲义自述算例里"我们设置的 `EDIFFG=-0.01`，发现 `DIMCAR` 里的 `Force` 没有到 0.01 就收敛了，**这是正常的**"（L3 P153）。

#### S22 · Dimer 初猜不好导致经常失败 / 结构严重偏离

- **症状**：Dimer 跑着跑着结构崩掉、偏离反应路径。
- **诊断**：`[讲义]` L3 P164：**Dimer 在初猜好的情况下效率很高，但初猜不好就经常失败**（该算例实测 207 个离子步、9620 秒，而 CI-NEB 只用了 13 步）。
- **处方**：
  1. 初猜技巧的第一条：**保证没有过短的键** —— 过短键长会造成强排斥，让结构在前几个离子步就崩掉、远离过渡态（`[讲义]` L3 P143）。
  2. 组合流程：**先用 CINEB/NEB 粗搜**（`EDIFFG = -0.5`、`EDIFF = 1E-5`）拿到能量最高的结构 → 用它作为 Dimer 初猜 → `nebresults.pl` 后跑 `neb2dim.pl <image 号>` → 在 `dim/` 里改 INCAR → Dimer 精修（`[讲义]` L3 P164–P167）。
  3. 运行中发现严重不合理的结构偏离就**杀掉任务重新调整初始构型**（`[讲义]` L3 P148）。
- **判据**：Dimer 收敛到恰好 1 个虚频（S13）；且与 CI-NEB 给出的 TS 能量在几个 meV 内吻合（实测基线：`ts-cineb` 的 `E0 = -66.256661` vs `ts-dimer` 的 `E0 = -66.258695`，差 **2.0 meV**；这条比较是本文件算的，`[待核对]`）。

#### S23 · `neb2dim.pl` 报错

- **症状**：调用 `neb2dim.pl` 时出错。
- **诊断/处方**：`[答疑]` D4-P49/D4-P50 给的三步处方（**按顺序试**）：
  1. 检查算 NEB 时 `CONTCAR` 有没有正常产生；
  2. 手动把 `CONTCAR` 最后的 `0000` 速度信息都删掉；
  3. 还不行就用 `modemake.pl` 自己生成 `MODECAR`。
- **判据**：`dim/` 目录里出现可用的 `POSCAR` + `MODECAR`；Dimer 能正常起步。

#### S24 · `neb2dim.pl` 生成的 INCAR 里带着 CINEB 参数

- **症状**：`dim/INCAR` 里同时有 `ICHAIN = 0`、`LCLIMB`、`IMAGES`、`SPRING` 和 `ICHAIN = 2`。
- **诊断**：`[讲义]` L3 P166 那段"VTST 提示我们使用这些参数，同时要把 CINEB 的参数删除掉"列出的其实是 **CINEB 的参数**（`ICHAIN=0 / LCLIMB / IOPT=1 / IMAGES=1 / SPRING=-5`），与 P146/P147 的 Dimer 需求冲突。讲义的意思应是"记得手改"，但没写出来。`[算例]` 的 `ts-dimer/INCAR` 里 CINEB 段整块被 `#` 注释，生效的是 `ICHAIN = 2` + `IOPT = 2`，且**没有** `LCLIMB`/`IMAGES`/`SPRING`。
- **处方**：在 `dim/INCAR` 里**把 `ICHAIN=0`/`LCLIMB`/`IMAGES`/`SPRING` 整段注释或删除**，只保留 `ICHAIN = 2`、`IOPT = 2`（`[讲义]` L3 P146/P147）。同时按 §0.5/§0.7 配 `IBRION = 3`、`POTIM = 0`、`EDIFF = 1E-7`、`EDIFFG = -0.03`。
- **判据**：`grep -E "ICHAIN|LCLIMB|IMAGES|SPRING" dim/INCAR` 只剩生效的 `ICHAIN = 2`。

### 1.5 磁矩不收敛 / 收敛到错误磁态

#### S25 · 磁矩收敛到了非目标磁态（本想算 AFM，结果给出 FM 或磁矩归零）

- **症状**：`OSZICAR` 末行的 `mag=` 与你设定的初猜不符 —— 例如设了 `MAGMOM = 5.0 -5.0 5.0 -5.0 6*0.0`（Fe₂O₃ 的 AFM），结果 `mag=` 不是 ≈ 0；或者反过来。
- **诊断（本文件认定的首要机制）**：**`MAGMOM` 只在特定条件下才生效**。`[讲义]` L1 P45 原文："只有如下两种情况程序才会使用 `MAGMOM` 初猜：(1) 计算没有读取 `CHGCAR`，也没有从 `WAVECAR` 里计算初始电荷密度；(2) 读取了非自旋极化的 `CHGCAR`。"**如果你是从上一次自旋极化的 `CHGCAR`/`WAVECAR` 续算的，你写的新 `MAGMOM` 被忽略了** —— 这是"改了 MAGMOM 却没反应"最可能的原因。
- **处方**：
  1. 要真正从初猜重来：把 `ICHARG = 2`（从原子电荷密度起算）或删掉/改名 `CHGCAR`，并设 `ISTART = 0`；同时确认 `ISPIN = 2`。
  2. `MAGMOM` 的**个数必须与 POSCAR 的原子数一一对应**，顺序按 POSCAR。写错个数时不要靠猜，用 `grep -i "NIONS\|ions" OUTCAR` 核原子数后重写（`[答疑]` D1-P8 的实操：**先扩包，再在 VESTA 观察原子编号**，按目标磁性排列逐个写）。
  3. 官方给的取向建议：找自旋极化（铁磁/反铁磁）解时**通常最安全的做法是从较大的局域磁矩起步**（`[讲义]` L1 P45 引手册原话 "usually safest to start from larger local magnetic moments"）—— 所以初猜可以大胆设大（比如 5.0），程序会自己优化到合理的磁矩。
- **判据**：`tail -1 OSZICAR` 的 `mag=`：
  - AFM（Fe₂O₃，`5.0 -5.0 5.0 -5.0 6*0.0`）→ `mag=    -0.0000`；
  - FM（`5.0 5.0 5.0 5.0 6*0.0`）→ `mag=    20.0000`。
  两个数都与 4 个 Fe 的初猜自洽（`[讲义]` L1 P47）。收敛后的原子磁矩块（Fe 的 s/p/d/tot = `0.014 0.016 4.248 4.278` 与 `-0.014 -0.016 -4.249 -4.279`）在 `day1/fe2o3/OUTCAR` 中逐数字可核。
- **能量判据**：AFM 比 FM 低约 **0.83 eV**（由讲义两组 E0 相减：67.085632 − 66.254043 = 0.831589 eV；用真实收敛值 67.088977 则为 0.835 eV）→ Fe₂O₃ 基态为反铁磁。**该结论由本文件从数值推出，讲义未写**，且 FM 那组在容器里**没有对应算例**。`[待核对]`
- **实操补充**：不用每次成功后改初猜 —— `[答疑]` D2-P81/D2-P82："`CoO` 初始磁矩设置 Co5 O2，优化完显示 `mag=3.0`，那接下来该怎么设置磁矩呢？" → "**磁矩设置不用变，继续用同样的设置方式就行。**"

#### S26 · 以为自己算了磁性，其实没开自旋

- **症状**：`OUTCAR` 里搜不到 `magnetization (x)` 块；`OSZICAR` 行里没有 `mag=` 字段。
- **诊断**：`ISPIN = 1`（或该行被注释掉）。
- **处方**：`ISPIN = 2`，并给 `MAGMOM`。**不确定吸附物有无自旋时必须用 2**：`[讲义]` L2 P141 的口径是"在不确定吸附物自旋状态的情况下用 `ISPIN = 2`，这个体系我已经测试过没有磁性…所以为了节省时间用 `ISPIN = 1`" —— 也就是说 `ISPIN=1` 的前提是**你已经验证过**。
- **判据**：`grep -c "magnetization (x)" OUTCAR` ≥ 1；`OSZICAR` 每行有 `mag=`。

#### S27 · 把 `OUTCAR` 末尾的原子磁矩/电荷当定量结果引用

- **症状**：论文里写"该 Fe 原子电荷为 1.234 e"或"磁矩 4.415 μB"，来源是 `OUTCAR` 末尾的表。
- **诊断**：**这是半径球内的布居数，不能定量**。`[讲义]` L1 P47 原话："`OUTCAR` 文件最后部分的原子电荷和磁矩是**根据每个原子的半径内电荷计算出的，仅供参考**。"`[讲义]` L2 P50 对 `LORBIT` 附带的 `total charge` 说得更狠："这里的电荷是根据 `PROCAR` 算出来的原子半径球内的电荷布居，**不能定量，定性可以做参考，一般无视就行了**。"
- **处方**：
  - 要定量原子电荷：**用 Bader charge**；其他可选 `DDEC`、`NPA` 电荷；用 `lobster` 分析能得到 Löwdin 与 Mulliken 电荷（`[讲义]` L2 P50）。操作见 §2 W4。
  - 要自旋密度：**不是读 `OUTCAR` 的 `MAGMOM`**。`[答疑]` D1-P21/D1-P22："`ISPIN=2` 的任务，spin density 保存在 `CHGCAR` 文件里，可以用 **vaspkit 312** 功能提取。"
- **判据**：你报的电荷来自 `ACF.dat`（Bader）或 `CHGCAR_mag`（自旋密度），而不是 `OUTCAR` 的末尾表。

### 1.6 "算完了但结果不对"（**本节最重要：没有任何报错**）

> 这一类是本手册最值钱的部分：程序一切正常、`grep reached` 命中、`OSZICAR` 好看，但数字不可用于发表。
> 共同特征：**没有任何报错，只有跟别的算例对比、或做收敛测试时才会暴露。**

#### S28 · ENCUT 偏低，能量差被系统性污染

- **症状**：程序正常结束；但吸附能/表面能与文献差 0.1–0.5 eV；或同一体系换了 `ENCUT` 后结论翻转。
- **诊断**：`[官方]` 两条明文：①"**感兴趣的量的收敛性必须针对能量截断 `ENCUT` 检查**"；②"**强烈建议永远在 `INCAR` 里手动写明 `ENCUT`**，否则默认值在不同计算之间可能不同（例如算内聚能时），后果是总能量不可比"（`references/official/pages/ENCUT.md`）。`[讲义]` L1 P28 给的定量规则是晶胞优化要 `> 1.3 × max(ENMAX)`。
- **处方**：把 `ENCUT` 显式写进 `INCAR`；对**你要报的那个量**（不是总能）做 §2 W1 的收敛测试；晶胞优化/弹性用 1.3×ENMAX 起。
- **判据**：`ENCUT` 从测试值再往上加 100 eV，目标物理量变化 < 你要求的精度（能量类一般 ≤ 10 meV/atom，吸附能 ≤ 0.02 eV）。
- **交叉核对锚点**：`day1/fe2o3` 的 `ENCUT = 520.0` 与 O 的 `ENMAX = 400.000` 之比**精确等于 1.30**，且该算例正是 `ISIF=3` 晶胞优化 —— 讲义规则在这个真实算例上被定量验证。

#### S29 · k 点不足 / 网格比例错

- **症状**：程序正常结束；DOS 曲线毛刺多；能量随 k 点变化还没收敛；各向异性胞某一方向明显欠采样。
- **诊断**：`[官方]` 给了两条：①"每个方向上的点数应**大致与对应晶胞长度成反比**"（`references/official/pages/KPOINTS.md` 的 `NB|tip`）；②"**这只提供了各方向之间的比例指导；k 网格的实际密度必须加大到某个相关输出量收敛为止**"（同页）。
- **处方**：
  1. 先按比例定网格：Γ 居中（`G`/`g`），三方向比 = `1/|a_1| : 1/|a_2| : 1/|a_3|`。
  2. **然后用 §2 W1 加密到目标量收敛**。
  3. ⚠️ **真空方向取 1**（`[算例]` `day1/GaN`、`day1/mos2`、`day2/au111-opt` 都是 `N N 1`）
     —— **只对 slab / 二维材料成立**（该方向是真空）。
     ⚠️ **3D 体相千万不要照做**：把某个方向设成 1 ⇒ 该方向**只采 Γ 点**
     ⇒ 总能 / 力 / 应力 / DOS **全部偏移，而 VASP 不报错**、
     `grep reached` 照样命中。
     判据：先看 `POSCAR` 该方向有没有**真空**
     （`playbook.md:59` §0.2 表的「真空方向」行已写明适用条件是
     "slab / 二维材料"；§0.3「真空层、slab 层数」有进一步判据）。
     **成对的另一面**见 S70（低维体系的真空方向**不该** > 1）。
  4. `fcc`、六方、`fcc`-正交**只用 Γ 居中网格**（`references/official/pages/KPOINTS.md` 的"只用 Γ 居中"清单）。Monkhorst-Pack 可能收敛更快，但要小心对称性被破坏。
- **判据**：把目标方向的 k 点数翻倍，目标物理量变化 < 精度要求。
- **参照档位**：vaspkit `KPOINTS` 头自带的档位说明是 `Low=0.08~0.05, Medium=0.04~0.03, Fine=0.02~0.01`（`[算例]` `day2/au111-opt/KPOINTS`、`day2/c/KPOINTS`）。

#### S30 · 真空层不够，slab 与自己的镜像作用

- **症状**：**没有任何报错**。功函数/静电势曲线在真空区**不出现平台**；吸附能随 c 增大还在变；掺杂/带电体系的能量随 c 剧烈漂移。
- **诊断**：c 太小，周期性镜像之间还留有相互作用。`[讲义]` 只写了"上下各保持一定的真空距离"（L2 P62），**全文没有数值判据**；但 vaspkit 在功函数流程里自己会提示 `Check the Convergence of Vacuum-Level Versus Vacuum Thickness!`（`[讲义]` L2 P137 引用的回显）。
- **处方**：把 c 加大到**真空层 ≥ 15 Å**（`[算例]` 反推基线：GaN 14.9999958 Å、Ag ≈15.0 Å、MoS₂/WS₂ ≈15.3 Å、OER slab c = 15.00000 Å），然后按 W1 的方式**扫描 c**验证收敛。二维材料做面内优化时用 `OPTCELL` 冻结 c（§3.6），防止优化把真空压掉。
- **判据**（可自查）：把 LOCPOT 的 z 方向平均势画出来，**真空区必须有一段水平直线**；c 再加 3 Å，`Φ` 与能量变化 < 10 meV。
- **反例**：`day2/ni-co` 从 CO 顶端到镜像底只有 ≈7.4 Å —— 该算例偏小，但因为它只是做 DOS 对齐用途，讲义接受。**不要把 7.4 Å 当成推荐值。**

#### S31 · slab 太薄，表面能/吸附能随层数漂移

- **症状**：不报错。表面能或吸附能随层数还没饱和；层数再变结论也变。
- **诊断**：结构弛豫的深度有限，层数不足时底层还没"长成体相"。`[讲义]` 只给了 Ni(100) 的 "6 个原子层"（L2 P59）与答疑的"一般 10–15 Å 就够了"（D4-P9/D4-P10，`[待核对]`），**没有收敛测试的记录**。
- **处方**：以 W1 的方式扫层数；同时保证**固定层数 ≤ 可弛豫层数**（`[讲义]` L1 P15）。参照：Ni(100) 6 层、Au(111) 5 层、Ag(111) 4 层。
- **判据**：层数 +2 时表面能/吸附能变化 < 0.02 eV；同时检查被固定的底层原子受力不为零但结构没动（说明固定生效）。

#### S32 · 赝势顺序错 / `MAGMOM` 个数不符 / 元素顺序错

- **症状**：不报错或报错信息含糊。能量离谱、磁矩归零、PDOS 明显不对。
- **诊断**：`POSCAR` 的元素顺序必须与 `POTCAR` 的拼接顺序、`LDAUL/LDAUU/LDAUJ` 的槽位顺序、`MAGMOM` 的原子顺序全部一致。`[官方]` 明文："**给定的顺序应与 `POTCAR` 文件中出现的物种顺序一致**"（`references/official/pages/POSCAR.md`，物种名行与计数行两处都写了）。`[算例]` 佐证：`day1/mos2/LOG` 显示 `POSCAR found type information on POSCAR  S  Mo` / `POSCAR found :  2 types and  3 ions` —— VASP 会从 POSCAR 第 6 行读元素名并要求 POTCAR 顺序匹配。
- **处方**：
  1. 拼 `POTCAR` 时严格按 `POSCAR` 第 6 行的次序首尾相连（`[讲义]` L1 P24）。用 vaspkit 103 可以自动拼，**但要知道原理**。
  2. 同一元素可以被定义多次，以对应不同赝势；`day1/GaN/POSCAR` 的元素行是 `N  Ga  H`、计数 `6  6  1`，把赝氢单列为第三种类就是为了给它配赝氢赝势（`[算例]`）。
  3. `MAGMOM` 个数按 `POSCAR` 原子总数写；`LDAUL/LDAUU/LDAUJ` 按**元素种类数**写（Fe₂O₃：`LDAUL = 2 -1`、`LDAUU = 5.3 0.0`）。
- **判据**（三步自查，全部可 grep）：
  - `grep "found type information" LOG` 的元素名顺序 = `POSCAR` 第 6 行顺序；
  - `grep -A6 "LDA+U is selected" OUTCAR` 的 `LDAUL/LDAUU/LDAUJ` 回显与你写的一致（实测 `day1/fe2o3/OUTCAR` 逐行吻合 ✓）；
  - `grep NIONS OUTCAR` 的原子数 = `MAGMOM` 的元素个数。

#### S33 · `ISMEAR` 用错：结构优化用了 `-5`，或大胞 Γ 点用了 `-5`

- **症状 A**：优化出来的力有"一定百分比的误差"（不是硬报错，是精度损失）。
- **症状 B**：直接报错（见 §5 E4）。
- **诊断**：`[讲义]` L2 P46 原文："**结构优化的时候不能使用 `ISMEAR=-5`**，是因为四面体方法不能很好地处理费米能级处的电子占据情况，**导致算出来的力会有一定百分比的误差**。"（力不准 → 优化出来的结构不准，且不报错。）
- **处方**：结构优化用 `ISMEAR = 1`（金属，配 `SIGMA=0.2`）或 `0`（非金属，配 `SIGMA=0.05`）；**只在优化完成后的 DOS/PDOS 单点步**改成 `ISMEAR = -5`（`[讲义]` L2 P36：`NSW=0` / `ICHARG=1` 或 11 / `LORBIT=11` / `ISMEAR=-5` / `NEDOS=1000`）。
- **判据**：优化步的 `INCAR` 里没有 `ISMEAR=-5`；DOS 步是**新文件夹**里的 `NSW=0` 单点（§2 W3）。

#### S34 · DOS 出自弛豫计算，而不是单点

- **症状**：`DOSCAR` 存在、能画图，但图与文献对不上；`OUTCAR` 里 `E-fermi` 出现很多次。
- **诊断**：`NSW > 1` 时最终 `DOSCAR` 是**所有离子步的平均**。`[官方]` 原文（VASP Wiki `DOSCAR` 页，本仓库未镜像该页）："For relaxations, the DOSCAR is usually useless… Mind that for NSW>1 the final DOS is averaged of all ionic steps."（外链：`https://vasp.at/wiki/index.php/DOSCAR`）。`[讲义]` 同口径：**"结构优化得到的 DOS 不能直接用，因为是平均了结构优化过程中的所有结构的 DOS"**（L2 P35），并再次强调"不优化就计算 DOS 一般没有意义"（L2 P48 注意事项 (6)）。
- **处方**：**另起 `dos` 文件夹做单点**：
  ```
  mkdir dos
  cp CONTCAR dos/POSCAR
  cp INCAR KPOINTS POTCAR CHGCAR ./dos/
  ```
  然后按 §2 W3 改 `INCAR`（`NSW = 0`、`ICHARG = 1` 或 11、`LORBIT = 11`、`ISMEAR = -5`、`NEDOS = 1000`、加密 k 点）。
- **判据**：`grep -c "E-fermi" OUTCAR` 应为 **1**（单点只算一次）。反例锚点：`day2/ni-co/OUTCAR` 里 `E-fermi` 出现 **8** 次，即该目录的 `DOSCAR` 出自一次**含离子弛豫**的计算 —— 正是讲义 P62 点名要避免的做法。**工作区内没有该体系独立的 `NSW=0` DOS 目录**，无法确认是否另有一份正确输出。

#### S35 · d 带中心报了数，但没报积分窗口 → 数字不可复现

- **症状**：你报 Ag(111) 的 d 带中心 −3.75 eV，别人复算得到 −3.78 eV，两人对不上。
- **诊断**：**同一个 PDOS，只改积分能量窗口，d 带中心的绝对值就变了**。实测对照：讲义给 **−3.7502**（vaspkit 503 回显，窗口 `[-9.39 17.20]`；另有脚本法取能量上限 20 eV 得 `-3.7501883008710406`），而 `day2/Ag/D_BAND_CENTER` 文件给 **−3.7771(Average)**（窗口 `[-9.11 10.04]`）。差异 **0.027 eV** 主要来自积分上限不同（20 eV vs 10.04 eV）。
- **处方**：报 d 带中心时**同时报三样**：× 积分窗口（下限、上限）、× 是否分自旋（UP/DOWN/Average）、× 数据来源（vaspkit 503 还是 115+脚本）。设置能量上限的理由（`[讲义]` L2 P93）："**因为高能的轨道（空轨道）计算误差非常大，且不参与成键**，所以有的时候需要设置一个能量上限，比如 10 eV。"
- **判据**：拿你的 `D_BAND_CENTER` 文件里的窗口去和你的 `DOSCAR` 头核对：窗口应等于 `[EMIN − E_F, EMAX − E_F]`。实测复核：`Ag/DOSCAR` 头 `EMAX=11.00348932`、`EMIN=−8.15061128`、`E_F=0.96133580` → `−9.11` 与 `10.04` ✓ 完全吻合。
- **心态判据**：工具自己印的警告是 `d-Band Center is Sensitive to the Number of Unoccupied Band. Anyway, the Trends are More Important than the Absolute Energies.`（`[讲义]` L2 P92）。**只能比趋势，别硬比绝对值。**

#### S36 · `ISYM` 设错，结果悄悄变了

- **症状**：没有任何报错；但与别人（或与讲义数值）差在小数位上；PDOS 的 lm 分解看起来怪。
- **诊断**：两条独立事实：① `[官方]` 记录了一个已知问题：**VASP < 6 且 `LORBIT >= 11` 且 `ISYM = 2`** 时有 known issue（`references/official/pages/LORBIT.md`）；② `[算例]` + `[答疑]` 冲突：随课 OER 全套实际跑在 `ISYM = 2`（`INCAR` 里 `#ISYM = 0` 被注释），而讲师在 D4-P21/D4-P22 说"需要设置一下 `ISYM = 0`"。
- **处方**（按目的二选一，**不要混**）：
  - **要复现随课 OER 数值** → 保持 `ISYM = 2`；
  - **要按讲师建议做、或体系对称性已被吸附物/缺陷破坏** → 显式写 `ISYM = 0`；
  - **做 MD（`IBRION = 0`）** → `[官方]` 明确：`ISYM = 0` 应该设，因为它仍然假定 Ψ_k = Ψ_−k 并据此减少 BZ 采样（`references/official/pages/ISYM.md`）；
  - **做杂化泛函** → `ISYM = 3`（该值下 VASP 通过把对称操作作用到不可约 BZ 的 k 点轨道上来构造电荷密度）；`[讲义]` L1 P34 也给了 `ISYM = 3`。
- **判据**：`grep "^ *ISYM" OUTCAR` 的回显（`OUTCAR` 里打印形如 `ISYM = 2  0-nonsym 1-usesym 2-fastsym`）与你的意图一致；跨计算比较时所有算例的 `ISYM` 一致。

#### S37 · `EMAX`/`EMIN` 手填了，或把默认回显当设置

- **症状**：`OUTCAR` 打印 `EMIN = 10.00; EMAX =-10.00  energy-range for DOS`，看起来像"EMIN > EMAX"，与讲义 P34 的文字定义（`EMAX = 最高 KS 本征值 + 2 eV`、`EMIN = 最低 − 2 eV`）形式相反。
- **诊断**：这三个量**只影响作图效果，不对实际计算起作用**（`[讲义]` L2 P48 注意事项 (5)）。而讲义 P36 的模板写 `# EMAX = -20` / `# EMIN = 15`，与 P34 的文字定义字面矛盾 —— 但 `[算例]` 实测三个 OUTCAR 都打印同型的 `EMIN = 10.00; EMAX =-10.00`，说明 VASP 自身在这个输出里就是这么写的哨兵/默认写法，P36 大概率是照抄而非笔误。
- **处方**：**留默认，不要手填** `EMAX`/`EMIN`；要改 DOS 图的能量范围就用后处理改横坐标（`p4vasp`/`vaspkit`/`pymatgen` 出的数据都会自动把 `E_F` 移到 0）。
- **判据**：你的 `INCAR` 里没有生效的 `EMAX`/`EMIN` 行。
- **来源标记**：`[待核对]` —— "VASP 是否接受在 INCAR 中如此反写"在现有资料里没有依据。

#### S38 · 片段单点没收敛就做差分电荷

- **症状**：`CHGDIFF.vasp` 在 VESTA 里"非常难看"、等值面碎裂不闭合。
- **诊断**：`[答疑]` D2-P23/D2-P24 原文："**要求收敛，如果不收敛，减出来的电荷密度会非常难看，结果也不合理。**"而讲义 P103 只强调了"结构从 CO/Ni(100) 直接截取，不要再结构优化！计算参数保持不变！"，**没有说片段单点必须收敛** —— 这是答疑稿补上的硬性条件。
- **处方**：三个片段（吸附态 AB、片段 A、片段 B）的**电子步都必须收敛**；且三者的 `ENCUT`/`PREC`/`LREAL`/`ROPT`/k 点/`ISMEAR` **完全一致**（否则做差时误差不抵消，见 `[官方]` `references/official/pages/LREAL.md` 关于"要算能量差时所有计算设置必须一致"的警告）。
- **判据**：三个目录各自的 `grep reached OUTCAR` 都命中；且 `grep -c "aborting loop because EDIFF is reached"` 与离子步数一致（若片段是 `NSW=0` 单点，至少要有收敛串）。

#### S39 · 费米能级没对齐就跨体系比 DOS / 比带边

- **症状**：不报错。两个体系的 DOS 图叠在一起，峰位看起来移动了，但其实是费米能级漂移。
- **诊断**：`[算例]` 实测：**同一结构、同一赝势，不同次计算的 `E-fermi` 会漂移约 0.014 eV**（`XC(G=0)` 与 `alpha+bet` 完全相同，说明是同一体系；`E-fermi` 在 5.4270 / 5.4353 / 5.4412 之间）。讲义 P40 因此要求"把 `Ef` 移动到 0 eV 的位置"。
- **处方**（三条路线，按体系选）：
  1. **有真空层的体系（slab、二维、异质结）→ 对齐真空能级**。`[答疑]` D2-P71/D2-P72："一般不太会对齐费米能级，因为不同体系的费米能级位置不同的。**最简单的就是对齐真空能级**。"做法见 §2 W5。
  2. **没有真空层的体系（体相/界面）→ 对齐深能级**。`[答疑]` D2-P11/D2-P12："如果没有真空层的体系可以去对齐深能级，比如加了 `_sv` 赝势对齐最内层的能级。或者 Core level 对齐。"具体关键词：`ICORELEVEL = 1`（`[答疑]` D2-P67/D2-P68）。
  3. 只是画图看形状 → 用工具自带的自动 shift（`p4vasp`/`vaspkit`/`pymatgen` 都会把 `E_F` 移到 0；`vaspkit` 由 `~/.vaspkit` 的 `SET_FERMI_ENERGY_ZERO .TRUE.` 控制）。
- **判据**：对齐后两个体系的**同一个芯能级峰**（或真空能级）在能量轴上重合到 ≤ 0.05 eV。
- **来源标记**：`_sv` 对齐 + `ICORELEVEL` 这两条**只出现在答疑稿，L2 全 157 页未提**，标 `[待核对]`。

#### S40 · `LORBIT` 的 `total charge` 被当定量电荷用

- **症状**：论文里写了"Bader 电荷"实际抄的是 `OUTCAR` 末尾 `LORBIT` 输出的 `total charge` 表。
- **诊断**：`[讲义]` L2 P50 原话："这里的电荷是根据 `PROCAR` 算出来的原子半径球内的电荷布居，**不能定量，定性可以做参考，一般无视就行了**。"`[官方]` 也说明 `LORBIT>=10` 的投影用的是 PAW 投影子，"这仍然是定性方法，因为半径是某种方式定义的，不保证对该体系是最优选择"（`references/official/pages/LORBIT.md`）。
- **处方**：定量电荷走 Bader（§2 W4）。`LORBIT` 只用来拿 PDOS 与 lm 分解。
- **判据**：你报的每个原子的电荷数来自 `ACF.dat`，且和数 = 体系总价电子数（可用 `grep NELECT OUTCAR` 对照）。

#### S41 · 赝氢钝化之后还算表面能

- **症状**：不报错，但表面能的物理意义不对。
- **诊断**：`[答疑]` D2-P55/D2-P56："**赝氢钝化以后这样的没法算表面能。只能钝化前算，而且算出来的是上下表面的平均表面能，单独的可能没法算。**"`[答疑]` D3-P23/D3-P24 同口径："钝化了以后就不能算了"。`[答疑]` D4-P57/D4-P58 给了替代路径："算表面能干脆就不用赝 H，直接上下表面一起优化，得到的结果是上下表面的平均表面能。"
- **处方**：表面能任务**不要加赝氢**，上下表面一起优化；报数时明确写"这是平均表面能"。钝化只用于"下表面不是研究对象"的吸附/催化任务。
- **判据**：你的能量式子里只用了 slab 本体能量，没有含 H 的赝氢项；且论文里写明了"上下表面平均"。

#### S42 · 用弛豫能量直接上报，但目标量需要更高精度

- **症状**：不报错。同一体系两次优化给出的能量在小数位不同，与文献比也差一点。
- **诊断**：弛豫过程用的是为"跑得快"设的参数（`ISMEAR=1/0` 展宽、k 点较粗、有时 `LREAL=Auto` 的实空间误差）。这些对几何够用，对报能量不一定够。
- **处方**：
  - **一般不需要再补单点**：`[答疑]` D3-P11/D3-P12："结构优化的能量可以直接用吗？不用再做个单点吗？" → "**不用，除非有精度更高的要求比如加大 K 点和 ENCUT。**"`[答疑]` D4-P67 同口径："优化完不用再算单点了，直接取优化完的能量就行。"
  - **需要时补单点**：`NSW = 0` + `ICHARG = 1` + 加密 k 点 + （必要时）加 `ENCUT`；若用了 `LREAL=Auto`，官方给的补救是"最后再用 `LREAL=.FALSE.` 做一次总能计算拿精确能量"（`references/official/pages/LREAL.md`）。
  - **所有要相减的能量必须在同一设置下算**：`bulk` 的能量要用与 `slab` 完全相同的一组设置重算（`[官方]` `references/official/pages/LREAL.md` 明文）。
- **判据**：参与相减的所有算例的 `ENCUT`/`PREC`/`LREAL`/`ROPT`/`ISMEAR`/`SIGMA`/`KPOINTS` 逐项相同；把 k 点或 `ENCUT` 加一档后，能量差变化 < 你的精度要求。

#### S43 · 吸附能参考态取错：用"同一次计算里的片段能量"代替单独的单点

- **症状**：不报错。吸附能数值与文献差系统性的一截。
- **诊断/处方**：`[答疑]` D2-P65/D2-P66 直接回答了这个问题："可以利用 Ni-CO 这个整体算出来的能量替换计算吸附能中要分别减去 Ni 的能量和 CO 能量的值吗？比如 `E(NiCO)-E(Ni)-E(CO)` 替换为 `E(NiCO)-E(Ni-CO)`？" → "**虽然结果差不多，但是不建议这么做，CO 分子要单独放到一个大盒子里算。**"
- **处方**：吸附能 = `E(AB/slab) − E(slab) − E(A)`，其中 `E(A)` 是吸附物**单独放在大盒子里**（Γ 点、`ISMEAR=0` + `SIGMA=0.01`）的单点；三者设置必须一致（尤其 k 点：吸附物分子用 Γ 点，slab 用你自己的网格 —— 这一处的不一致是不可避免的，**必须在同一套方法内保持一致**，即所有体系的"分子参考能"都来自同一种盒子设置）。
- **判据**：把分子盒子从 15 Å 加到 20 Å，`E(A)` 变化 < 10 meV。

#### S44 · 差分电荷的三种减法是不同的物理量

- **症状**：图和文献形状不同；或问"为什么我的差分电荷看起来像电荷密度本身"。
- **诊断**：`[讲义]` L2 P102 明确给了两种定义，**它们是不同的量**：
  1. **片段差**：`Δρ = ρ_AB − ρ_A − ρ_B`（"减去两个片段"，用于分析吸附物与表面的成键）；
  2. **变形电荷密度**：`Δρ = ρ(AB_self-consistent) − ρ(AB_atomic)`（SCF 收敛密度减去各原子自由状态下的球对称密度）。
  `[答疑]` D2-P79/D2-P80 补充了第三种用法（三片段差）："有些特殊体系需要，比如：表面共吸附两个不同的分子，可能就用三个减"。
- **处方**：明确你要的是哪一种，并在图注里写出来。做片段差时按 §2 W4 的流程（结构直接截取、不优化、参数保持一致、电子步必须收敛）。
- **判据**：`CHGDIFF.vasp` 用 VESTA 打开，青色=电荷密度减小、黄色=增加（`[讲义]` L2 P104）；把 `CHGDIFF.vasp` 改名成 `CHGCAR` 后用 `vaspkit 316` 得 `CHGPAVG.dat`，导入 origin 后**把 X-Y 坐标反转一下**，就得到平面平均差分电荷随 z 的分布（同页）。
- **来源标记**：三片段的**具体式子**在现有资料里没有给出，`[待核对]`。

#### S45 · 功函数用了 `LVTOT` 而不是 `LVHAR`

- **症状**：不报错，但 `LOCPOT` 的曲线形状不对（不是纯静电势）。
- **诊断**：`[讲义]` L2 P135 原话："在 `INCAR` 里 `LVHAR = .TRUE.` 输出静电势文件 `LOCPOT`，和 `CHGCAR` 的格式是完全一样的。注：如果设置 `LVTOT = .TRUE.`，`LVHAR = .FALSE.` 则输出的 `LOCPOT` 文件是**包含静电势和交换相关势能的总势能**。"
- **处方**：算功函数/静电势**只开 `LVHAR = .TRUE.`**，把 `LVTOT` 关掉。
- **判据**：`grep -E "LVHAR|LVTOT" OUTCAR` 显示 `LVHAR = T`、`LVTOT = F`；真空区的势曲线是一段水平线。
- **数值锚点**：Au(111)-p(2×2)：`grep fermi OUTCAR` 得 `Efermi = 1.6561 eV`，`Φ = 6.673 − 1.6561 = 5.02 eV`；O/Au(111)-p(2×2)：`Evac = 7.196 eV`、`Efermi = 1.5863 eV`、`Work function = 5.6097 eV`（两处算术均已复核）。

#### S46 · 隐式溶剂（VASPsol）还在跑离子步 / 忘了写 `EB_K` 就换了溶剂

- **症状 A**：加了 `LSOL` 但程序还在做几何优化，结果与真空优化混在一起。
- **症状 B**：想算甲醇里的溶剂化，只写了 `LSOL = T`。
- **诊断/处方**：
  - `[讲义]` L4 P54 明文："VASPsol 计算需要打开：`LSOL = T`，默认水溶液。**把离子步关掉 `NSW = 0`**。"`[算例]` 两组 `vaspsol/INCAR` 相对普通 `INCAR` 的**全部差异**就是：`NSW` 从 300 → **0**，并新增 `LSOL` 与 `LRHOB`。
  - 「`EB_K` 为介电常数，查表可知其他溶剂的介电常数。其他参数不能直接查表得到，需要拟合，但是 VASPsol 程序并没公开其他溶剂的参数，所以目前只能改变介电常数近似代表其他溶剂。」（`L4 P54`）→ **要换溶剂必须显式写 `EB_K`**；只写 `LSOL=T` 得到的就是 **78.4 的水**（`[算例]` 两组都没写这四个参数，走的是默认值；`[待核对]`：本文件未读 VASPsol 源码/官方手册，无法确认默认值就是这四个数）。
  - 四个参数与含义（`L4 P54`）：`EB_K = 78.400000`（bulk solvent 相对介电常数）、`SIGMA_K = 0.600000`（dielectric cavity 宽度）、`NC_K = 0.002500`（cutoff charge density）、`TAU = 0.000525`（cavity surface tension）。
  - 想打印 bound charge（电子转移与溶剂极化产生的溶剂电荷密度）：`LRHOB = .TRUE.`（`L4 P54`）。注意它**不是**算溶剂化能量必需的开关。
- **判据**：`OSZICAR` 里出现 `SOL:` 开头的行（证明溶剂模型生效）；`NSW = 0` 在 `OUTCAR` 回显里为 0。实测量级锚点：H₂O 分子单点，真空 `E0 = -.14226768E+02`（−14.226768 eV）→ VASPsol `E0 = -.14539553E+02`（−14.539553 eV），**ΔE = −0.312785 eV（−7.213 kcal/mol）**。
- **溶剂化与频率校正的一致性**：`[答疑]` D4-P31/D4-P32："最好用 vaspsol 下做频率校正，如果算不动，可以用没有 vaspsol 情况算也行。"

#### S47 · 能量口径混乱（`E0` / `TOTEN` / `energy(sigma->0)` 混用）

- **症状**：不报错。同一体系的"能量"在不同人手里差 1E-4 ~ 1E-2 eV；自由能台阶图最后一步不闭合。
- **诊断**：`OUTCAR` 里至少有三个能量口径：`free energy TOTEN`、`energy(sigma->0)`、`OSZICAR` 的 `E0`。`[算例]` 实测：讲师 OER 数据用的是 **`energy(sigma->0)`** 而不是 `TOTEN`（slab：`TOTEN = −279.09288` vs `sigma->0 = −279.08405889`，差 8.8 meV；*OH/*OOH 两者相同，因为它们带隙大、展宽无影响）。
- **处方**：
  1. 全项目**统一取 `tail -1 OSZICAR` 的 `E0`**（`[讲义]` L1 P30、L3 P151 都推荐这个）。
  2. 若要用 `OUTCAR` 的字段，**在图注/表注里写明是哪一个**（`TOTEN` 还是 `sigma->0`）。
  3. **台阶图必须机器校验回归**：`[算例]` 内部实测存在 6×10⁻⁵ eV 的不闭合（`oer.xlsx` 的 G 列每个值都比用精确参考态算的**小 6×10⁻⁵ eV**，导致末行显示 4.91994 而不是 4.92）。**它不影响过电势**（相减时常数偏移抵消，η = 0.486208 V 两种算法一致），但说明"闭合性检查"必须写成脚本，不能靠手工取整。
- **判据**：你的自由能台阶图最后一步回到总反应能（OER 是 **4.920000 eV**），误差 < 1E-4 eV，且这个检查是脚本跑出来的。

### 1.7 报错类（有原文的）

> 本节只列**在现有资料里读到过原文**的报错。原文 + 含义 + 处方在 §5 汇总；这里给出四要素细节。
> **凡是本文件在资料里找不到原文的报错（如 `ZBRENT: fatal error`、`EDDDAV`、`WARNING: DENTET` 等），一律不写** —— 见 §1.9。

#### S48 · `VERY BAD NEWS! internal error in subroutine IBZKPT: Tetrahedron method fails for NKPT<4`

- **症状原文**：`VERY BAD NEWS! internal error in subroutine IBZKPT: Tetrahedron method fails for NKPT<4. NKPT = 1`（`[讲义]` L2 P46 给出的原文；`references/raw/L2.txt` 第 580 行可见）。
- **诊断**：`ISMEAR = -5`（Blöchl 修正四面体法）在不可约 k 点数 < 4 时无法构造四面体。`[官方]` 说明 `-5` 是"不带展宽的 Blöchl 修正四面体法"，并要求**用 Γ 居中网格**（`references/official/pages/ISMEAR.md`）。
- **处方**：把 `ISMEAR` 改成 **0** 或 **1**（`[讲义]` L2 P47："当 K 点小于 3 个时候，`ISMEAR` 可以取 0 或 1 来算 DOS。（手册上建议用 -5，其实用 0 或 1，定性上完全没有问题）"）。配 `SIGMA = 0.05`（非金属）。
- **判据**：任务越过 IBZKPT 阶段；`grep -c NKPTS OUTCAR` 与实际不可约点数一致。
- **实测佐证**：`day2/c`（KPOINTS `1 5 1`，NKPTS = **3**）与 `day2/mos2ws2`（`1 4 1`，NKPTS = **3**）都用 `ISMEAR = 0`；唯一用 `-5` 的 `day2/al2o3` 的 NKPTS = **115** —— 规则被严格遵守 ✓。

#### S49 · 带电体系 + 非立方超胞 + `LDIPOL=.TRUE.`

- **症状原文**：`[官方]` 警告原文："For charged systems, the potential correction is currently only implemented for cubic supercells. **VASP will stop** if the supercell is not cubic and `LDIPOL` is used."（`references/official/pages/LDIPOL.md`）
- **诊断**：带电体系的偶极/单极势修正在当前实现里只支持立方超胞。
- **处方**（三选一）：
  1. 把超胞做成**立方**（a = b = c）；
  2. 关掉 `LDIPOL`，改为用**中和背景电荷**的常规做法，并单独评估有限尺寸误差；
  3. 改用**抗衡离子**代替改总电荷 —— `[答疑]` D1-P12："改变 `NELECT`…**或者添加抗衡离子，在下表面加一个 OH**"；`[答疑]` D3-P45/D3-P46 也提醒"可以改 `NELECT`（**可能会引起背景电荷问题**）或者加额外抗衡离子"。
- **判据**：任务能跑起来（不再在启动时停）；且 `grep -E "LDIPOL|IDIPOL" OUTCAR` 与你的意图一致。
- **附带**：`[官方]` 还提醒**不要同时设 `LMONO`**，因为它会抑制偶极修正的输出（`references/official/pages/LDIPOL.md` 相关链）。

#### S50 · 找不到 `reached required accuracy`（结构优化"跑完但没收敛"）

- **症状**：任务正常结束、`OUTCAR` 完整，但 `grep reached OUTCAR` 里**只有**每个离子步的 `------------------------ aborting loop because EDIFF is reached ------------------------`，**没有** `reached required accuracy - stopping structural energy minimisation`。
- **诊断**：结构优化跑满了 `NSW` 而力没到 `|EDIFFG|`（**不是崩溃，是"没收敛地结束"**）。这两种串的语义不同：前者是**每个离子步内部的 SCF 收敛**，后者才是**离子步收敛**。实测 `day1/fe2o3/OUTCAR` 两者都有（前者 9 次 = 9 个离子步；后者 1 次）。
- **处方**：按 S7 的顺序处理（先 `EDIFF` 后 `PREC` 后算法/步长），或者明确接受"跑满 `NSW`"这个结果但**不要当成收敛结构**用（尤其不要拿去做频率，见 S14）。
- **判据**：`grep -c "reached required accuracy" OUTCAR` ≥ 1；或（若确实有意跑满 `NSW`）在图注里写明"未达到力收敛"。

#### S51 · 结构优化"收敛"了但只走了一步（续算假象）

- **症状**：`OSZICAR` 只有 1~2 个离子步，`d E` 极小（如 `-.128559E-10`），仿佛一步就收敛。
- **诊断**：读入了**已收敛的 `WAVECAR`/`CHGCAR`**，第一个离子步的 `dE` 天然接近 0。`[讲义]` L1 P47 引用的那行 AFM `OSZICAR`（`1 F= -.67085632E+02 ... d E =-.128559E-10`）正是这种痕迹：它与 `day1/fe2o3/OSZICAR` 的**全部 9 个离子步都不相等**，且真实第 1 步的 `dE` 是 −0.670 eV 而不是 ~0 —— 说明那一行来自另一次（续算）运行。
- **处方**：
  1. 判断是否收敛，看 `dE` 的**下降过程**而不只是最后一行；续算时先把 `ISTART`/`ICHARG` 想清楚。
  2. **报 Fe₂O₃ 能量时用容器里的文件**（`fe2o3/OUTCAR` 的 `free energy TOTEN = -67.08897674 eV`；`fe2o3/OSZICAR` 末行 `E0 = -.67088977E+02`），**不要用讲义那一行**。
- **判据**：`OSZICAR` 的离子步数 > 1 且 `dE` 序列体现收敛过程；或（若确实是从收敛态续算做单点）确认 `NSW = 0`。

#### S52 · `OUTCAR` 显示的体系名/晶格不是你以为的那个

- **症状**：拿 `DOSCAR`/`EIGENVAL` 头里的体系名判断算例身份，得出错误结论。
- **诊断**：`SYSTEM` 名是从模板照抄来的，**与实际体系经常不符**：`[算例]` `day2/Ag/INCAR` 写 `SYSTEM = GDY`；`day2/ni-co/INCAR` 写 `SYSTEM = Fe`；`day2/c/INCAR` 写 `SYSTEM = Au`；`day2/mos2ws2/INCAR` 写 `SYSTEM = MoS2`（这个是对的）。而讲义 L2 P61 的模板本身就是 `SYSTEM = Fe`，所以 `ni-co` 是照抄。
- **处方**：判断体系身份用 **`POSCAR` 的元素行 + 计数**，或 `LOG` 里的 `POSCAR found type information` / `POSCAR found : N types and M ions`；不要用 `SYSTEM`。
- **判据**：`head -7 POSCAR` 的元素与计数与你的预期一致。

#### S53 · 讲义引的 `CHGCAR`/`POSCAR` 示例与容器里的算例不是同一个胞

- **症状**：照抄讲义的晶格矢量却复现不出讲义的结果。
- **诊断**：`[讲义]` L2 P97 展示的 Al₂O₃ `CHGCAR` 头与 `day2/al2o3/POSCAR` **不是同一个胞**：第二行矢量数值与符号都不同（`5.434311 / 2.854620` vs `−5.384940 / 2.830390`），元素顺序也不同（`O Al` vs `Al O`）。该页示例来自另一次（更早的）`Al2O3 Cell opt`。
- **处方**：复现数值时**只以容器里的 `POSCAR`/`CONTCAR`/`OUTCAR` 为准**；讲义里的示例当"格式示意"看。
- **判据**：你的 `POSCAR` 前 7 行与 `day2/al2o3/POSCAR` 一致（或与你自己的原始胞一致）。

### 1.8 建模/工作流类的"没报错但白干"

#### S54 · 忘记 `OPTCELL`，二维材料面内优化时把真空压掉了

- **症状**：不报错。`ISIF = 3` 优化完，`CONTCAR` 的 c 变小了、真空层被压缩。
- **诊断**：`ISIF = 3` 是**9 个自由度全放开**（`[讲义]` L1 P32）。二维材料/含真空体系不冻结 c 方向时，真空会被优化掉。`[讲义]` L2 全 157 页**没有出现 `OPTCELL`**，但 `day3`/`day4` 的二维算例靠它实现面内优化（`mos2ws2/OPTCELL`、`oer/slab/OPTCELL` 内容都是 `100 / 110 / 000`）。
- **处方**：
  1. 在计算目录放一个三行的 `OPTCELL` 文件，**无空格、无分号、只有回车换行**：
     ```
     100
     110
     000
     ```
     （`1` = 优化该矩阵元，`0` = 不优化；对应 POSCAR 的 3×3 晶胞矢量矩阵。）
  2. 必须使用**改过 `constr_cell_relax.F` 的 VASP**（普通官方源码版无效）；讲师提供的是集成了 OPTCELL 的版本（`[讲义]` L1 P32/P50）。
  3. **不要这样写**：`OPTCELL(100; 000; 000)`（带空格和分号）—— `[答疑]` D4-P1/D4-P2 的实例：这样写导致"第一个和第三个晶胞矢量的 x 坐标发生了变化"；讲师答"**看我给的 OPTCELL 的例子，没有空格没有分号，只有回车换行。**"
- **判据**：比较 `POSCAR` 与 `CONTCAR` 的晶格矢量 —— **面内 a、b 变了，c 严格不变**。实测锚点：`day1/mos2` 的 a 由 3.1659999 → 3.1822493，而 **c 严格保持 18.4099998474 不变**；`oer/slab` 的 c 精确为 15.00000。
- **⚠ 关键坑**：**`OPTCELL` 不会在 `OUTCAR` 的参数区回显**（在 `mos2`/`vdw-df2` 两个 `OUTCAR` 里都 grep 不到）。**判断它是否生效只能比较 `POSCAR` 与 `CONTCAR` 的晶格矢量。**
- **反向验证**：`day1/fe2o3` 没有 `OPTCELL` 且 `ISIF=3`，其 `CONTCAR` 三个基矢全变并出现非对角分量（a 的 z 分量 0 → 0.0205958）✓ 与"9 个自由度全放开"一致。

#### S55 · 赝氢放在了错的位置 / 忘了固定

- **症状**：不报错。但表面态没消掉，或赝氢在优化中跑掉。
- **诊断**：`[讲义]` L1 P58/P60 的规则是"**赝氢一般添加在原有化学键的中点位置，计算过程中固定**"。`[答疑]` D1-P45/D1-P46 补充："赝氢**不用优化**，直接把下面几层固定住就可以了。"
- **处方**：
  1. 位置：放在**原有化学键的中点**，沿键方向。
  2. 固定：在 `POSCAR` 里给赝氢的坐标行标 `F F F`（配合第 7/8 行之间的 `Selective Dynamics`）。
  3. `POTCAR` 要给赝氢单独一个物种槽（它有自己的赝势，价电子数不同：`H1.25`、`H1.5`、`H.5`、`H.75` 等，`[答疑]` D1-P23/D1-P24 确认"这个赝势是 vasp 赝势库里自带的，有很多"）。
- **判据**（可精确复核的几何判据）：H 到被饱和原子的距离 ≈ 原化学键长的一半，且 H 的 z 落在键中点上。实测锚点（`day1/GaN/POSCAR_FIX`）：Ga–N 键长 1.9742314 Å；文件中 H 的实际 z = 2.0000985 Å，而键中点 z = 1.9995039 Å，**仅差 0.0006 Å**；H 到 N 的距离 = 0.9865210 Å ≈ 键长的一半（0.9871157 Å）✓✓。
- **固定判据**：赝氢那一行是 `F F F`（`day1/GaN/POSCAR_FIX` 第 13 个原子 ✓）。
- **什么时候不需要赝氢**：金属不用（`[答疑]` D2-P25/D2-P26："只有共价键半导体需要饱和，Ni 是金属键结合的"）；单层 MoS₂ 切 100 面也不用（`[答疑]` D1-P57/D1-P58："不用"）；氧化物氧终端一般也不需要（`[答疑]` D4-P5/D4-P6）。

#### S56 · 切面选错了终端 / 忘了上下两个表面

- **症状**：不报错。表面能/吸附能看起来"能用"，但模型在自然界不存在。
- **诊断**：`[讲义]` L1 P54 提醒：**移动表面 Top 时上/下表面会同时变化，slab 有两个表面，搭建模型时要时刻记得上/下两个表面**。讲义给的诊断实例是 `O/Al = 21/12`，不符合化学计量比 `O/Al = 18/12 = 2/3`。`[讲义]` L1 P56 还警告："**好多计算的文章里截取的表面模型都是有问题的，自然界根本不存在的表面做催化计算。**"
- **处方**：按讲义给的四条切面原则（`[讲义]` L1 P57）逐条自检：
  1. 尽量保证**化学计量比与 bulk 一样**（如 Al:O = 2:3）；
  2. 尽量让**表面能最小**、暴露的表面原子与实验一致（**氧化物优先让氧暴露**）；
  3. 是否加基团钝化不饱和原子，要参考前人文献与实验经验：过渡金属化合物一般不加；Al₂O₃、SiO₂ 可考虑 −OH 饱和；Si、GaN、InSe、ZnSe 等共价晶体/半导体用**赝 H** 饱和；
  4. 尽量让表面**对称**；不对称表面加 `IDIPOL` + `LDIPOL` 消偶极。
  并核化学计量比（数原子）、核上下表面的暴露原子种类。
- **判据**：数出来的原子比 = bulk 化学计量比（或明确写出你故意偏离了多少、为什么）；`IDIPOL`/`LDIPOL` 在不对称时已打开。
- **判据（文献锚点）**：`[讲义]` L1 P56 推荐 **R. Hoffmann, Angew. Chem. Int. Ed., 2013, 52, 93-103** 作为切面参考。

#### S57 · 异质结晶格失配没处理

- **症状**：不报错。界面应力巨大、优化后单层被拉断或皱起来。
- **诊断**：两个材料的晶格常数/夹角不匹配。`[答疑]` D1-P25/D1-P26 给的处方："通过求算**最小公倍数**，比如 A（a=2 埃）B（a=3 埃），就把 A 扩包 3 倍，B 扩包两倍。如果夹角不一样，先通过 `redefine lattice` 转基矢。**不是所有的两个材料都能建立异质结的。**"
- **处方**：
  1. 按最小公倍数扩包；
  2. 夹角不同先用 `redefine lattice` 转基矢（`[讲义]` L1 P62）；
  3. 在建模工具里查 mismatch：讲义给的实例是 g-C₃N₄/TiO₂(100) 的 "a 矢量 8.88%，b 矢量 4.21%，角度 4.60%"，并评价"这个值在异质结的构建里算是很大了，但是由于单层的二维材料可塑性往往很好，所以经过一定的变形 C₃N₄ 可以匹配 TiO₂(100) 的晶格常数"（`[讲义]` L1 P75）；
  4. 建完给 c 加大约 15 Å 真空（`[讲义]` L1 P76：`build – crystal – rebuild crystal`，把 c 增大 15 埃），并考虑对 a、b 做选择性优化（即 `OPTCELL` 的 `110/110/000`，见 §3.6）。
- **判据**：matching 里三个数（a、b、角度）都 < 5%，或明确记录你接受了多大的失配。

#### S58 · 功函数/静电势参考零点没统一

- **症状**：不报错。你报"某电极电势 −2.04 V (vs SHE)"，别人按另一套零点得到 −2.20 V。
- **诊断**：**SHE 相对真空的绝对电位没有唯一值**。`[讲义]` L4 P41 用 **4.44 V**（"标准氢电极 SHE 相对于真空的绝对电位是 4.44 V"），并给两个换算：`2.40 V(vs Vacuum) ↔ −2.04 V(vs SHE)`、`3.81 V ↔ −0.63 V`（两处算术都已复核：2.40−4.44 = −2.04 ✓；3.81−4.44 = −0.63 ✓）。而配套的 `VASPsol原理.pdf`（arXiv:1601.03346v1）自己拟合出的值是 **4.6 V**（"compares very well with the previously reported computed value of 4.7 V"）。
- **处方**：**报 vs SHE 的绝对电势前必须先声明 SHE 零点用的是哪一个**（4.44 V 还是 4.6 V）；同一篇文章里不要混用。若做 AIMD 平均功函（`[讲义]` L4 P42 的流程：预平衡 → 跑 20 ps → 每 1 ps 取一个结构算单点拿功函 → 20 个功函取平均），把零点约定写死在流程说明里。
- **判据**：同一功函值用你声明的那一个零点换算，能得到你报出的 vs SHE 值。
- **附注**：`L4 P42` 的图注写 −2.4 V (vs SHE)，与 `P41` 的 −2.04 V 不是同一次计算（P42/P43 引的是 PNAS 2017 的另一个体系），**不要把这两个数互换**。

### 1.9 资料没覆盖、本文件**故意不写**的症状

> 遵守契约红线 5：不写"某内容不存在"。下表列出**我检索过的范围**与**结果**，供后续补料。
> 检索范围：`references/raw/learn_L1.md`、`learn_L2.md`、`learn_L3.md`、`learn_L4.md`、`D1.txt`–`D4.txt`、
> `references/official/pages/*.md`（627 页）与 `references/official/_keywords.tsv`（620 行）。
> 检索式（`grep` 正则，大小写敏感）：`ZBRENT|DENTET|PRICEL|EDDDAV|LAPACK|internal error|VERY BAD NEWS|WARNING|BRMIX|ZPOTRF|not converged|Fatal|fatal`。

| 症状/报错 | 检索结果 | 处理 |
|---|---|---|
| `ZBRENT: fatal error`（离子步线性搜索失败） | 在上述范围内**未命中任何原文** | **不写**。不给含义、不给处方（否则就是编）。 |
| `WARNING: DENTET` / `DENTET` 相关 | 未命中 | **不写**。 |
| `EDDDAV` / `ZHEGV` / `ZPOTRF` 等线性代数报错 | 未命中 | **不写**。 |
| `PRICEL` 相关报错 | 仅在 `references/official/pages/EFOR.md` 出现一句 "Subroutine PRICEL returns:"，**不是报错原文** | **不写**该报错的含义与处方。 |
| `BRMIX` 相关报错 | 未命中 | **不写**。 |
| `VERY BAD NEWS! internal error in subroutine IBZKPT` 之外的 `VERY BAD NEWS` | 只命中 L2.txt 第 580 行的这一条 | 只写这一条（§1.7 S48）。 |
| `vaspkit 402` 的 Threshold 具体含义 | 讲义原话只有"Threshold 是 vaspkit 的总层数判断标准，在不同的标准下层数会判断的不太一样"（L1 P17/P18），**没有算法说明** | 只写"怎么用"（§3.3），不解释判定算法。 |
| `IBRION = 6 / 7 / 8` 与 `DYNMAT` 的用法 | `learn_L3.md` 明确核对：`IBRION=7`/`8` 在 L3 全文中**一次都没出现**，`DYNMAT` 出现 **0 次**；`IBRION=6` 只在"`IBRION=5` 或 6 时的默认值"这一句里被附带提到。`things to study/` 下全部 INCAR 里 `IBRION` 只出现 **2、3、5、7** 四个值 | 只写 `IBRION=5`（§2 W8）。**红外谱（`IBRION=7` + `LEPSILON=.TRUE.`）的完整流程不写**，只标注"仓库里有这套算例的 INCAR，但讲义正文没有讲"。 |
| `非自洽/磁性收敛到错误解` 的系统性诊断树 | `learn_L1.md` L1 P45 给了 `MAGMOM` 生效的两个条件，但**没有**"多磁态枚举"的完整流程 | 只写 S25 的条件与判据；**不编造**多初猜枚举的推荐做法。 |
| Bader 的 `ACF.dat` 输出列 | `[讲义]` L2 P100 以图注形式给了列语义（笛卡尔坐标 / 原子盆体积 / 原子核到原子盆边界的最小距离 / 价电子数），但工作区内**没有** `AECCAR0`/`AECCAR2`/`ACF.dat` 可核 | 写流程（§2 W4），列语义标 `[待核对]`。 |
| `vaspkit 111` 的产物名 `TDOS.dat`/`ITDOS.dat` | 工作区里只有 `113` 系产物（`PDOS_*.dat`/`IPDOS_*.dat`，与讲义 P42/P44 命名一致 ✓），**没有 111/112/114/115 的产物实例** | 写讲义原文的说法，标 `[待核对]`。 |
| ELF 的数值分级（如 0.5 对应自由电子气） | 讲义只给"定域程度高/低"的定性两极，无数值分级 | 只写定性判读（§4）。 |
| 双电层/平板电容/泊松-玻尔兹曼的具体公式 | `L4 P34/P36/P37/P50` 的公式本体**在文本抽取中丢失** | 不写公式。只写"这几页没有可直接写进 INCAR 的参数"。 |
| `oer/o2/` 目录为什么没有结果文件 | 只有 `INCAR`/`KPOINTS`/`POSCAR`/`POTCAR`，无 `OUTCAR`/`vasprun.xml`/`OSZICAR` | 只记录现象，不推测原因。 |

### 1.10 输入文件解析类的静默失效（**最阴的一类：不报错，设置根本没生效**）

> 这一节的共同特征：任务跑起来了、也没有报错，但**你写的某个设置从来没被程序读过**。
> 与 §1.6 的区别是：§1.6 是"读进去了但结果不对"，这里是"根本没读进去"。
> 本节第一手的官方依据是 `[官方]` `references/official/pages/INCAR.md` 开篇：
> "**Yet, the settings in the INCAR file are the main source of errors and false results, so we suggest carefully checking the meaning of the set INCAR tags.**"

#### S59 · `INCAR` 里用圆括号写说明，且说明里含分号 `;`

- **症状**：任务正常跑完，但某条 `INCAR` 语句似乎没生效；`OUTCAR` 回显里那一项是默认值。
- **诊断**：`[官方]` 的 `INCAR` 格式规定：**注释只能用 `#` 或 `!`**；圆括号**不是**注释，是普通文字；而 **`;` 是语句分隔符**，用来在一行里写多条 `tag = value`（`references/official/pages/INCAR.md` 的 Format 节）。于是下面这一行：
  ```text
  ALGO   =  ALL         (Electronic Minimisation Algorithm; ALGO=58)
  ```
  在 VASP 眼里是**两条语句**：`ALGO = ALL` 与 `58)`。第二段会被当成一条语句去解析（`58)` 不是合法整数字面量）。
  **本项目真实算例里就有这一行**：`线上中级班-催化资料/1-fundamental/hse/INCAR` 第 62 行逐字如此 —— 作者的意图显然是"用 `ALL` 并在括号里注解 `ALGO=58` 这个编号"。
- **处方**：把括号里的说明改成 `#` 或 `!` 开头的注释，或删掉其中的分号：
  ```text
  ALGO   =  ALL         # (Electronic Minimisation Algorithm; ALGO=58)
  ```
- **判据**：`grep -n ';' INCAR` 只在 `#`/`!` 之后出现分号；且 `grep -E "^\s*ALGO" OUTCAR` 的回显是你要的算法。
- **证据分级（重要，照抄 `scripts/validate.py` 的谨慎程度）**：① "注释符是 `#`/`!`、`;` 是分隔符"是**官方明文**；② "这一行几乎肯定不是作者本意"是**推论但很硬**（作者在别处一直用 `#` 写注释）；③ **"VASP 具体会怎么处理 `58)`"本文件没有验证** —— 该目录里只有 `INCAR`/`INCAR.bak`，**没有 `OUTCAR`** 可以实测。所以这条处方是"按官方格式写对"，而不是"照实测现象改"。

#### S60 · 值里混进了说明文字（从 wiki 抄 `INCAR` 时丢了 `#`）

- **症状**：不报错，但某个 tag 的值明显不是你要的；或者某个列表型 tag（`MAGMOM`、`LDAUU`、`FERWE`）的行为完全不对。
- **诊断**：从 wiki 抄`INCAR` 示例时，把行尾的 `#` 丢掉了。真实算例（`3-electronicStructure/ex4-co-wavefunction-partialcharge/partialCharge/INCAR` 第 1–2 行）逐字是：
  ```text
  ISTART =      1    job   : 0-new  1-cont  2-samecut
  ICHARG =      1   charge: 1-file 2-atom 10-const
  ```
  wiki 原文形如 `ISTART = 0 # job : 0-new 1-orbitals from WAVECAR`，抄的时候 `#` 没了。后果：值变成了 `1    job   : 0-new  1-cont  2-samecut`。**如果 VASP 用自由格式列表读取而不是报错，它会读到很多"数"** —— `ISTART` 只取第一个数所以恰好还是 1，**看起来一切正常**；但换一个列表型 tag 就是灾难。
- **处方**：给这些行补回 `#`：
  ```text
  ISTART = 1   # job   : 0-new  1-cont  2-samecut
  ICHARG = 1   # charge: 1-file 2-atom 10-const
  ```
- **判据**：`grep -nE '=\s*[0-9.+-]+\s+[A-Za-z]' INCAR` **没有输出**（即没有任何"数值后面直接跟字母"的行）。这一条是能一条命令查完的自查式。
- **来源**：`scripts/validate.py` 的 `INCAR.annotation_in_value` 检查项与它记录的上述真实算例。

#### S61 · 关键字发到了不属于它的文件里（`INCAR` / `KPOINTS` / `POSCAR` 弄混）

- **症状**：语法完全合法，离线看没问题，真机上直接中止。
- **诊断**：把本该写到别的文件里的关键字写进了 `INCAR`（或反过来）。`scripts/validate.py` 的 `INCAR.unknown_tag` 检查项专门抓这一类，并明确记录这是"**CP2K skill 上真实翻过车的那一类缺陷**"。
- **处方**：用官方关键字表的"归属"列核对：`references/official/_keywords.tsv` 每行给出 `关键字 \t 所属文件 \t 分类 \t 描述`。跑一次离线校验：`python scripts/validate.py <算例目录>`。
- **判据**：`validate.py` 不再报 `INCAR.unknown_tag` 的 ERROR 档。

#### S62 · 分段小标题被误当成语法错误（**反向提醒：这是合法的**）

- **症状**：`INCAR` 里有 `Electronic Relaxation:`、`-------- DFT+U --------` 这类行，你担心它们会破坏解析。
- **诊断**：**它们无害**。`[官方]` `INCAR` 格式页明文："VASP ignores all text that does not fit the statement format"（只要这类文字里**不含 `= ; "` 三个语法字符**）。本手册 §2 W0 的模板里就大量使用了这种分段小标题。
- **处方**：**不用改**。想更保险就别在标题里写 `;` 或 `=`。
- **判据**：`grep -nE '^[^#!]*[=;"]' INCAR` 之外的分段标题都安全。
- **来源**：`scripts/validate.py` 的 `_looks_like_section_header()`（其中记录：早期版本要求标题必须以 `:` 结尾，把 `Global Parameters` 误报成 WARN，是一个已更正的假阳性）。

#### S63 · 同一关键字在 `INCAR` 里出现两次

- **症状**：不报错，但哪个值生效"取决于解析顺序"，可复现性很差。
- **诊断**：同一个 tag 出现两次时，**VASP 用哪个值不一定是后者**。本手册 §0.11 给的一个真实算例正是这个形态：`day1/vdw-df2/INCAR` 把 `#GGA = PE` 注释掉、**另起一行**写 `GGA = ML` —— 它之所以"避免了重复指定 GGA"，是因为先注释再新写，而不是靠"后者覆盖前者"。
- **处方**：改值就**注释掉旧行**再写新行（照 `vdw-df2` 的做法）；不要留两行生效的同一个 tag。
- **判据**：`grep -cE "^\s*GGA\s*=" INCAR` = 1（对每个 tag 都做一次这个计数）。
- **来源**：`scripts/validate.py` 的 `INCAR.duplicate` 检查项；算例依据 `[算例]` `day1/vdw-df2/INCAR`。

#### S64 · 等号后面直接跟注释、值写空了

- **症状**：不报错，但那个 tag 用了默认值（**静默失效**）。
- **诊断**：`TAG =   # 说明` 这种写法里，`#` 之后确实会被 VASP 忽略，所以**这一行的值成了空**。空值对多数 tag 等于用默认值。
- **处方**：把值补上，或删掉这一行。
- **判据**：`grep -nE '=\s*(#|!)' INCAR` **没有输出**。
- **来源**：`scripts/validate.py` 的 `INCAR.semicolon_comment` 第二条分支。

#### S65 · 设了 `ICHARG = 11` 却没配 `NELM = 1`

- **症状**：任务能跑完、结果也对，但**白跑了若干步 SCF**，而且容易让人误以为做了自洽。
- **诊断**：`ICHARG = 11` 是"固定电荷密度做非自洽"，**不需要迭代 SCF**。留着默认 `NELM` 会白跑若干电子步。
- **处方**：非自洽步骤配 `NELM = 1`。
- **判据**：非自洽目录的 `grep -c "DAV:\|RMM:" OSZICAR` 很小（1 步量级），而不是几十步。
- **来源**：`scripts/validate.py` 的 `INCAR.mutual_exclusion` 第三条（标注为 `[官方]` VASP wiki `ICHARG`）。
- **⚠ 与本手册 §2 W3 的关系**：W3 的 DOS 单点写 `ICHARG = 1`（自洽单点）—— `[讲义]` L2 P45 明说"可以用之前的 `CHGCAR` 做非自洽计算（`ICHARG = 11`）；也可以直接开始一个自洽单点计算（`ICHARG = 1`），只要收敛到同样的电子态上，结果是一样的"。**走 11 就配 `NELM = 1`；走 1 就正常设 `NELM`。**

#### S66 · 频率计算用 `ISIF = 3`

- **症状**：不报错，但 Hessian 不是你要的那个（晶胞在动）。
- **诊断**：**频率计算要求固定几何**；`ISIF = 3` 会让晶胞也参与弛豫。
- **处方**：频率计算用 `ISIF = 2`（或 `0`）冻结晶胞。本手册 §2 W6.1 与 W7.8 的模板都是 `ISIF = 2`。
- **判据**：`grep -E "ISIF" freq/OUTCAR` 与你的意图一致。
- **来源**：`scripts/validate.py` 的 `INCAR.mutual_exclusion` 第二条（标注为"经验判据 + VASP wiki: IBRION 的 Warning 与 phonon 页面"）。

#### S67 · `IBRION = 5/6` 下 `POTIM` 被自动重置

- **症状**：你在频率计算的 `INCAR` 里写了 `POTIM = 0.015`（或写了别的值），`OUTCAR` 回显似乎不同。
- **诊断**：`[官方]` 明文："**对 VASP.5.1 及更新的版本，如果提供的 `POTIM` 值不合理地大，它会被自动重置为 0.015 Å。**"（`references/official/pages/POTIM.md`）
- **处方**：不用管它。`IBRION=5/6` 下就写 `POTIM = 0.015`（这本来就是官方默认值）；写大了程序会自己重置。
- **判据**：`grep -E "POTIM" freq/OUTCAR` 显示 0.0150。
- **相关**：`POTIM = 0` **只在 `IBRION = 3`（Damped MD / 过渡态）下是官方默认值、完全合法**；在其他 `IBRION` 下给 0 会让步长缩放因子为 0 —— **离子不动，而程序不一定报错**。这是"没报错但白干"的又一例，也是 `validate.py` 里一条曾经误报真算例（`day3/ts/dim`，`IBRION=3` + `POTIM=0`）的假阳性，值得记住判据要看上下文。

#### S68 · `MAGMOM` 个数与 `POSCAR` 原子数不符

- **症状**：不报错（或报错信息含糊）；磁矩结果与预期完全不符。
- **诊断**：`MAGMOM` 是**逐原子**数组，个数必须等于 `POSCAR` 的原子总数（可用 `N*x` 简写）。个数不符时程序会自己补/截断，你的磁性设定就废了。
- **处方**：先数原子再写：
  ```bash
  # POSCAR 第 7 行的计数之和 = 原子总数
  awk 'NR==7{s=0; for(i=1;i<=NF;i++) s+=$i; print s}' POSCAR
  ```
  再核对 `OUTCAR` 的 `NIONS`，最后确认 `MAGMOM` 展开后的个数。
- **判据**：`grep NIONS OUTCAR` 的数 = `MAGMOM` 展开后的元素个数。`[算例]` 锚点：`day1/fe2o3` 的 `MAGMOM = 5.0 -5.0 5.0 -5.0 6*0.0` 展开为 4 + 6 = **10**；其 `POSCAR` 第 1 行是 `Fe4 O6`、计数为 `4 6` ✓。
- **来源**：`scripts/validate.py` 的 `XMAGMOM.count` 检查项。

#### S69 · `LDAUL/LDAUU/LDAUJ` 列表长度与元素种类数不符

- **症状**：不报错，但 U 加到了错误的元素上。
- **诊断**：这三个 tag **每个物种一个值**，长度必须 = `POSCAR` 的元素种类数（不是原子数），且**顺序与 `POSCAR` 元素顺序一致**。`[官方]` `LDAUU` 页："It must hold one value for each atomic species."（`references/official/pages/LDAUU.md`）
- **处方**：按 `POSCAR` 第 6 行的元素顺序逐个写。`[算例]` 锚点：`day1/fe2o3/POSCAR` 第 6 行是 `Fe    O`（Fe 在前），`INCAR` 就是 `LDAUL = 2 -1`、`LDAUU = 5.3 0.0`、`LDAUJ = 0.0 0.0` ✓（`OUTCAR` 回显逐项吻合）。
- **判据**：`grep -A6 "LDA+U is selected" OUTCAR` 的三行列表与你写的一致；长度 = 元素种类数。
- **来源**：`scripts/validate.py` 的 `XLDau.count` 检查项；算例依据 `[算例]` `day1/fe2o3`。

#### S70 · 低维体系的真空方向 k 点不为 1

- **症状**：不报错。计算量白涨；极端情况下真空方向采样引入无意义的分立。
- **诊断**：c 方向是真空时，该方向的能带完全色散平坦，`N_3 = 1` 就够。`[算例]` 三个 slab/2D 算例都取 `N N 1`。
- **处方**：`KPOINTS` 第 4 行第三个网格数写 1。
- **判据**：`awk 'NR==4{print $3}' KPOINTS` = 1（对真空方向的体系）；且 `grep NKPTS OUTCAR` 的数目与 Γ 居中网格相符。
- **来源**：`scripts/validate.py` 的 `XDIM.kpoints` 检查项。

#### S71 · `ENCUT` 低于 `POTCAR` 的 `ENMAX`

- **症状**：不报错。**这是"欠收敛最常见的来源"**（`scripts/validate.py` 对 `XENCUT.enmax` 检查项的原话）。
- **诊断**：`[官方]` `ENCUT` 页：不写 `ENCUT` 时取 `POTCAR` 里的最大 `ENMAX`；多个物种时用最大的那个。写小了等于主动欠收敛。
- **处方**：**显式写 `ENCUT`**，且 ≥ max(ENMAX)；晶胞优化/弹性 > 1.3×（见 §0.1 与 W1.1）。用你自己的 `POTCAR` 读它：
  ```bash
  # 用本仓库提供的解析工具读你自己的 POTCAR 头部（不要手抄 POTCAR 正文）
  python -c "from scripts import vasp_common as vc; h=vc.parse_potcar_header('POTCAR'); print(h.titles)"
  ```
  （`scripts/vasp_common.py` 提供 `parse_potcar_header`；本手册不引用 `POTCAR` 正文数字。）
- **判据**：`grep -E "ENMAX" OUTCAR` 的每个值都 ≤ 你的 `ENCUT`；`grep -E "^ *ENCUT" OUTCAR` 回显是你写的值。
- **来源**：`scripts/validate.py` 的 `XENCUT.enmax` 检查项；`[官方]` `references/official/pages/ENCUT.md`。

#### S72 · `POSCAR` 缺 `Direct`/`Cartesian` 行

- **症状**：不报错，但坐标被整体错位解释。
- **诊断**：这一行缺失时，VASP 会把它当成坐标行的第一行去解析。`[官方]` 说明坐标模式行只认第一个字符，**`C`/`c`/`K`/`k` 才算 Cartesian，其他一切都被解释为 Direct**（`references/official/pages/POSCAR.md`）。若你的文件是老格式（本来就没有这一行）那没问题；若是误删，坐标含义全变。
- **处方**：显式补一行 `Direct` 或 `Cartesian`。
- **判据**：`sed -n '8p;9p' POSCAR`（无 `Selective Dynamics` 时是第 8 行）能看到 `Direct` 或 `Cartesian`。
- **来源**：`scripts/validate.py` 的 `POSCAR.syntax`（`mode_line_missing`）。

#### S73 · `POSCAR` 第二行的 scale 是负数

- **症状**：晶格常数与你预期差一个数量级。
- **诊断**：**负的缩放因子是 VASP 支持的写法**：|scale| 被解释为**目标体积**，`s` 会被自动算出来（`references/official/pages/POSCAR.md`）。所以它**不是错误**，但如果你是从别处复制的文件，很容易误以为它是普通缩放。
- **处方**：确认这就是你的本意；否则改成正的缩放因子。
- **判据**：`sed -n '2p' POSCAR`；核对 `grep "volume of cell" OUTCAR` 的体积是不是你要的。
- **来源**：`scripts/validate.py` 的 `POSCAR.scale`（INFO 档）。

---

## §2 任务工作流

> 每个工作流给**可执行命令或文件操作**，不给方向性描述。
> 约定：`$WD` = 当前任务目录；所有 INCAR 片段只写与"通用模板"不同的行。
> 通用模板（表面/二维体系，金属改 `ISMEAR=1` + `SIGMA=0.2`）见 §2 W0。

### W0 · 通用 INCAR 模板（先抄这一份，再按各工作流改）

```text
#### initial I/O ####
SYSTEM  = <你的体系名>          # 注意：名字必须自己改，不要沿用模板
ISTART  = 0                     # 从头开始（要从 WAVECAR 续算才设 1）
ICHARG  = 2                     # 从原子电荷密度起算
LWAVE   = .TRUE.
LCHARG  = .TRUE.
LVTOT   = .FALSE.
LVHAR   = .FALSE.
LELF    = .FALSE.

#### Electronic Relaxation ####
ENCUT   = <查 §0.1，写死>
PREC    = Normal                # 力不收敛时改 Accurate
EDIFF   = 1E-6
NELM    = 300
NELMIN  = 5
NELMDL  = -5                    # 表面/低维体系显式写（有 WAVECAR 时默认是 0！）
GGA     = PE
ISMEAR  = 0                     # 金属改 1
SIGMA   = 0.05                  # 金属改 0.2
LREAL   = .FALSE.               # 原子数 > 30 再考虑 Auto
ISYM    = 0                     # 见 S36 的三选一

#### Ionic Relaxation ####
EDIFFG  = -0.02                 # 晶胞优化改 -0.01
IBRION  = 2
POTIM   = 0.2
NSW     = 300
ISIF    = 2                     # 晶胞优化改 3（二维材料 + OPTCELL，见 §3.6）

#### 并行（按你的机器自己定，不要抄） ####
NCORE   = <见 §0.13>
```

**上线前自查（三条命令）**：
```bash
grep -E "^ *ENCUT" OUTCAR          # 确认 ENCUT 是你要的值，不是默认
grep -E "^ *ISMEAR|^ *SIGMA|^ *ISYM|^ *LREAL|^ *NELMDL" OUTCAR   # 确认关键开关生效
head -7 POSCAR && head -1 POTCAR   # 确认元素顺序 = POTCAR 顺序（S32）
```

### W1 · 收敛测试（ENCUT / k 点 / 真空层 / slab 厚度）

**通用做法**：把"要报的那个物理量"作为判据，不要拿总能当判据。

**W1.1 ENCUT 收敛**
```bash
# 1) 取一个已经优化好的结构
cp CONTCAR POSCAR
# 2) 扫 ENCUT：从 max(ENMAX) 起，每次 +50~100 eV，写 4~5 个目录
for e in 400 450 500 550 600; do
  mkdir -p enc_$e && cp POSCAR KPOINTS POTCAR enc_$e/
  sed -e "s/^ENCUT.*/ENCUT = $e/" -e "s/^NSW.*/NSW = 0/" INCAR > enc_$e/INCAR
done
# 3) 跑完后取能量，算相邻差
for e in 400 450 500 550 600; do
  printf "%s  " $e; tail -1 enc_$e/OSZICAR
done
```
- **判据**：相邻两档之间的目标物理量变化 < 你要的精度（总能收敛一般看 ≤ 1 meV/atom；吸附能 ≤ 0.02 eV）。
- **取证**：`[官方]` "感兴趣的量的收敛性必须针对 `ENCUT` 检查"（`references/official/pages/ENCUT.md`）。
- **起点参考**：晶胞优化用 > 1.3 × max(ENMAX)（`[讲义]` L1 P28 + `[算例]` `day1/fe2o3` 的 520/400 = 1.30）。

**W1.2 k 点收敛**
```bash
# 先用 vaspkit 生成基准 KPOINTS（交互：1 → 102 → 2(Γ 中心 MP) → R 值）
vaspkit
#   1        <- 生成 VASP 输入文件
#   102      <- 产生自洽计算用的 KPOINTS
#   2        <- Gamma 中心的 MP 方法
#   0.04     <- 倒格子中 k 点间距 R
# 然后手工加密：把 KPOINTS 第 4 行的网格逐个方向 +2 扫
for g in "5 5 1" "7 7 1" "9 9 1" "11 11 1"; do
  d=$(echo $g | tr -d ' '); mkdir -p k_$d
  cp POSCAR POTCAR INCAR k_$d/
  printf "k-conv\n0\nGamma\n$g\n0.0 0.0 0.0\n" > k_$d/KPOINTS
done
```
- **判据**：网格再加密一档，能量变化 < 1 meV/atom。
- **比例规则**：`N_1:N_2:N_3 = |a_1|^{-1} : |a_2|^{-1} : |a_3|^{-1}`（`[官方]` `references/official/pages/KPOINTS.md`）。讲义给的等价说法是"三个基矢取模再取倒数，比值即三方向 k 点密度比"（`[讲义]` L1 P22）。
- **档位参考**：vaspkit 的 `R`：0.04 = Medium（讲师 8/8 个结构优化算例的取值），0.03/0.02 = Fine。
- **真空方向**：`N_3 = 1`（`[算例]` `day1/GaN`、`day1/mos2`、`day2/au111-opt`）。

**W1.3 真空层厚度收敛**
```bash
# 固定面内，只改 c；结构先优化好
for c in 15 18 21 24; do
  mkdir -p vac_$c
  # 把 POSCAR 第 3 个晶格矢量的 z 分量改成 $c（Direct 坐标下原子分数坐标不变即可）
  cp KPOINTS POTCAR INCAR vac_$c/
  awk -v c=$c 'NR==1{print} NR>=2&&NR<=4{ if(NR==4){$3=c} print } NR>4{print}' POSCAR > vac_$c/POSCAR
  # INCAR 里 NSW=0
  sed 's/^NSW.*/NSW = 0/' INCAR > vac_$c/INCAR
done
```
- **判据 A**（功函数/静电势）：`LVHAR=.TRUE.` 跑单点 → 取 z 方向平均势 → **真空区必须有一段水平平台**；c 再加 3 Å，Φ 变化 < 10 meV。
- **判据 B**（吸附能）：c 再加 3 Å，吸附能变化 < 0.02 eV。
- **起点参考**：**真空层 ≥ 15 Å**（`[算例]` 反推 15.0–15.3 Å 是这批算例的事实标准）。

**W1.4 slab 层数收敛**
```bash
for n in 4 5 6 7; do
  # 用建模工具切出 n 层的 slab（§3.1），固定最下 2 层（§3.3）
  mkdir -p slab_$n && ...
done
```
- **判据**：层数 +2，表面能/吸附能变化 < 0.02 eV。
- **起始参考**：Ni(100) = 6 层（`[讲义]` L2 P59）；Au(111) = 5 层、Ag(111) = 4 层（`[算例]`）；总厚度 10–15 Å（`[答疑]` D4-P9/D4-P10 `[待核对]`）。
- **同时检查**：固定层数 ≤ 可弛豫层数（`[讲义]` L1 P15）。

### W2 · 表面吸附能

**步骤**
1. **优化体相**（晶胞优化）：`ISIF = 3`，`EDIFFG = -0.01`，`ENCUT > 1.3×ENMAX`。判据：`grep reached OUTCAR` 命中。
2. **切表面 + 加真空 + 固定底层**：见 §3.1–§3.3。真空 ≥ 15 Å；固定下 2 层（金属）或按 §0.3。
3. **优化干净 slab**：`ISIF = 2`，`EDIFFG = -0.02`，`NSW = 300`。判据：`grep reached OUTCAR` 命中；`grep "FORCES: max atom, RMS" OUTCAR | tail -1` 的第一个数 < 0.02。
4. **建模吸附构型**（§3.5），**一次建多个位点**：`[答疑]` D2-P51/D2-P52："多摆几个可能的构型再优化，**取能量最低的构型**。也可以做个 AIMD 模拟退火看看，不过一般没必要。"
5. **优化吸附构型**：同第 3 步参数。**初始吸附距离**：异质结/分子-表面距离先给 ~3 Å 再优化（`[答疑]` D2-P65/D2-P66："距离保持个 3 Å 左右，再优化，优化的时候要加 vdW 校正"）。
6. **算孤立吸附物**：**单独放到一个大盒子里**（`[答疑]` D2-P65/D2-P66 明确"不建议"用同一次计算里的片段能量代替）。Γ 点、`ISMEAR=0`、`SIGMA=0.01`。
7. **算吸附能**：`E_ads = E(AB/slab) − E(slab) − E(A)`。

**判据/自查**
- 三个能量都在**同一设置**下算（`ENCUT`/`PREC`/`LREAL`/`ROPT`/`ISMEAR`/`SIGMA` 逐项一致）—— `[官方]` `references/official/pages/LREAL.md` 明文要求。
- 分子盒子从 15 Å 加到 20 Å，`E(A)` 变化 < 10 meV。
- 多构型里最低的那个与次低差 < 0.05 eV 时，要在正文里说明"两个位点能量接近"。

**物理吸附**：必须加色散校正。`[讲义]` L2 P57："**DFT 计算物理吸附吸附的时候需要 DFT-D3 方法才能算出物理吸附的状态。**" `INCAR` 加 `IVDW = 11`（或 12，见 §0.11）。

**例外/坑**
- 金属表面用 PBE 会**高估吸附能**，RPBE 有很大改善（`[讲义]` L1 P41）。同一个项目内不要混泛函。
- `[答疑]` D2-P73/D2-P74：上下对称的 slab 上算吸附能，**不需要在上下两面都放吸附分子** —— "不用，下表面固定"。

### W3 · DOS 与 d 带中心

**W3.1 DOS 单点**
```bash
# 必须在优化之后，另起目录（S34）
mkdir -p dos && cd dos
cp ../CONTCAR POSCAR
cp ../KPOINTS ../POTCAR ../CHGCAR .
```
`INCAR` 相对优化步要改的行：
```text
NSW     = 0                # 纯单点
ICHARG  = 1                # 或 11（读 CHGCAR 做非自洽）。两者收敛到同一电子态时结果相同
LORBIT  = 11               # lm 分解；只要 s/p/d/f 用 10
ISMEAR  = -5               # 四面体法；NKPT<4 或只有 Γ 时改 0/1（见 S48）
NEDOS   = 1000             # 默认 301；模板里也用过 2000
```
**k 点要加密**：`[讲义]` L2 P46："K 点数目要适当取得更大…K 点越多，画出来的 DOS 图质量越高，曲线也会更平滑。"
**判据**：`grep -c "E-fermi" OUTCAR` = **1**；`head -6 DOSCAR` 的第 6 行第 3 个数 = 你的 `NEDOS`。
**注意**：`ISMEAR=-5` 时程序**不读 `SIGMA`**（`[讲义]` L2 P36）。

**W3.2 提取 DOS / PDOS（vaspkit）**

| 功能号 | 输入 | 产物 | 用途 |
|---|---|---|---|
| `111` | — | `ITDOS.dat` / `TDOS.dat` | 总 DOS 与**积分** DOS（积分 DOS 用来判断电子占据数） |
| `112` | 指定原子序号 | `PDOS_A<n>.dat` / `IPDOS_A<n>.dat` | 单原子 PDOS |
| `113` | 元素符号 | `PDOS_<El>.dat` / `IPDOS_<El>.dat` | 每元素 PDOS（d 带中心最常用） |
| `114` | 多原子序号 | `PDOS_SUM.dat` / `IPDOS_SUM.dat` | 多原子加和（**原子编号用 POSCAR 的整体编号**，可在 Jmol 里看整体编号） |
| `115` | 依次输入 `元素` ↵ `轨道` ↵ … | `PDOS_USER.dat` | 指定元素+轨道 |

（来源：`[讲义]` L2 P41–P44；`[答疑]` D2-P7/D2-P8 补充 114 的编号规则。产物命名在 `things to study/al2o3` 里被证实：`PDOS_Al.dat`、`PDOS_O.dat`、`IPDOS_Al.dat`、`IPDOS_O.dat` ✓。`111`/`112`/`114`/`115` 的产物实例**工作区里没有**，命名按讲义照录 `[待核对]`。）

**`E_F` 移位**：`p4vasp`/`vaspkit`/`pymatgen` 出的数据都会自动把 `E_F` 移到 0；`vaspkit` 由 `~/.vaspkit` 的 `SET_FERMI_ENERGY_ZERO .TRUE.` 控制。费米能级用 `grep E-fermi OUTCAR` 取。（`[讲义]` L2 P40）

**W3.3 d 带中心**
```bash
# 方法一：vaspkit 503（直接输出所有原子与总的 d 带中心）
vaspkit   # 主功能 5（电子结构）-> 503
# 会问：The default energy window of integration is [-9.39 17.20], Do you want to change (Y/N)?
# 输入 y 可以指定积分权重平均的能量范围
# 产物：D_BAND_CENTER
#   表头：# Atom ID  d-Band-Center (UP)  d-Band-Center (DOWN)  d-Band-Center (Average) (in eV)

# 方法二：vaspkit 115 + 自备脚本（可算 s/p/d/f 中心、可指定某几个原子）
vaspkit   # 115 -> 输入元素 -> 输入轨道（如 d）-> 0
python3 ~/bin/d-bandC.py PDOS_USER.dat 20    # 第 3 个参数 20 = 能量上限（eV）
```
（来源：`[讲义]` L2 P92、L2 P93。方法二的三个优点原文：可算 s/p/d/f 中心；可指定某几个原子；"因为高能的轨道(空轨道)计算误差非常大，且不参与成键，所以有的时候需要设置一个能量上限，比如 10 eV"。）

**⚠ 报告纪律**：报 d 带中心**必须同时报**积分窗口、是否分自旋、数据来源（503 还是 115+脚本）。理由与实测差 0.027 eV 的对照见 S35。
**⚠ 适用边界**：单原子/过渡金属氧化物/单原子 FeN₄ 也能算，但"规律没有纯金属那么好。决定单原子催化吸附能的除了 d-band center 还有一些价态、配位环境等因素"（`[答疑]` D2-P15/D2-P16、D2-P17/D2-P18、D2-P19/D2-P20）。

**流程骨架（讲师版）**：优化金属最密堆积表面（先晶胞优化 `ISIF=3`，再表面优化 `ISIF=2`）→ 每个体系新建 `dos` 文件夹算单点 → 适当提高 k 点 → `vaspkit 113` 生成 `PDOS_M_UP.dat` → 导入 origin，**对 5 个 d 轨道求和**（`[讲义]` L2 P89/P90）。

### W4 · Bader 电荷 与 差分电荷

**W4.1 Bader**
```text
INCAR 加：
LAECHG = .TRUE.        # 显式重构全电子电荷密度并写文件
# 注意：LAECHG 会把 AECCAR0/AECCAR2 写到"fine"FFT 网格（NGXF/NGYF/NGZF）
```
```bash
# 1) 自洽计算（必须收敛，见 S38）
# 2) 三件套
chgsum.pl AECCAR0 AECCAR2       # 生成 CHGCAR_sum
bader CHGCAR -ref CHGCAR_sum    # 生成 ACF.dat / BCF.dat
# 3) 把原子电荷画成着色图
vaspkit   # 508
```
（来源：`[讲义]` L2 P100、L2 P101；格点说明见 L2 P97/P98：`grep NGXF OUTCAR` 可查格点数，"这个数值可以在 INCAR 中指定，但是不建议这么做，一般用 `PREC=Accurate` 产生的格点数量就足够了"。）
**判据**：所有原子电荷之和 = 体系总价电子数（`grep NELECT OUTCAR` 对照）；`ACF.dat` 的列语义（笛卡尔坐标 / 原子盆体积 / 原子核到原子盆边界的最小距离 / 价电子数）按讲义图注 `[待核对]` —— 工作区里没有 `AECCAR*`/`ACF.dat` 可核。
**⚠ 不要**用 `OUTCAR` 末尾 `LORBIT` 的 `total charge` 当定量电荷（S40/S27）。

**W4.2 差分电荷（片段差）**
```bash
# 目录结构：ads（吸附态） / slab / mol（吸附物）
# 三个片段的 POSCAR 都从吸附态结构直接截取，不要再优化！
# 三个片段的 INCAR 参数必须完全一致！
cp ads/CONTCAR slab/POSCAR   # 删掉吸附物原子
cp ads/CONTCAR mol/POSCAR    # 只留吸附物，放进大盒子
# 三个都必须收敛（S38）
cd ads && vaspkit   # 314 -> 依次输入三个片段：./CHGCAR ./mol/CHGCAR ./slab/CHGCAR
# 产物：CHGDIFF.vasp
```
- **读图**：VESTA 打开 `CHGDIFF.vasp`，**青色 = 电荷密度减小，黄色 = 电荷密度增加**（`[讲义]` L2 P104）。
- **平面平均**：把 `CHGDIFF.vasp` 改名成 `CHGCAR` → `vaspkit 316` → `CHGPAVG.dat` → 导入 origin 后**把 X-Y 坐标反转一下**（同页）。
- **三片段差分**：表面**共吸附两个不同分子**时可能需要（`[答疑]` D2-P79/D2-P80）；**具体式子在资料里没有**，`[待核对]`。
- **判据**：三个片段各自的电子步都收敛；等值面闭合、不碎裂。

**W4.3 partial charge（band decomposed charge density）**
```text
# 第 1 步：先做自洽，得到收敛的 WAVECAR
# 第 2 步：新建一次运算，直接从 WAVECAR 提取（相当于把 VASP 当脚本跑，不做新 SCF）
```
| 关键词 | 默认 | 用法 |
|---|---|---|
| `LPARD` | `.FALSE.` | `.TRUE.` 时读入自洽收敛的 `WAVECAR` 做 band decomposed charge density |
| `IBAND` | 无 | 按 **EIGENVAL 的顺序**指定能带，如 `IBAND = 20 21 22 23` |
| `NBMOD` | `-1` | `>0`：`IBAND` 中的能带数量（设了 `IBAND` 会自动调整）；`0`：所有轨道（含非占据）；`-1`：正常算 `CHGCAR`；`-2`：算 `EINT` 能量范围内的 partial charge；`-3`：同 −2，但能量范围以**费米能级为 0 参考** |
| `KPUSE` | 无（所有 k 点） | 指定算哪些 k 点，取值是这些 k 点在 `KPOINTS` 里的**序号**；算 Γ 点就 `KPUSE = 1` |
| `EINT` | 无 | 两个实数 → `NBMOD=-2`，能量参考 **EIGENVAL 文件**（如 `EINT = 4.00 5.00`）；只给一个数 → "从 `EINT` 到费米能级"，`NBMOD=-3`，参考**费米能级**（如 `EINT = -2.00` 表示 −2.0 ~ 0 eV） |
| `LSEPB`/`LSEPK` | `.FALSE.`（合并） | `.TRUE.` 时按每个能带/每个 k 点分别写到 `PARCHG.$.$`；`.FALSE.` 时合并写到 `PARCHG.ALLB.*` 或 `PARCHG` |

（来源：`[讲义]` L2 P115–P119。三个模板见 L2 P120–P121：指定能带+指定 k 点；只指定能量范围；指定相对费米能级的范围。）

**三种用法模板**
```text
# 1) 指定能带 + 指定 k 点（研究 VBM/CBM 常用）
ISTART = 1
LPARD  = .TRUE.
IBAND  = 20 21 22 23
KPUSE  = 1
LSEPB  = .TRUE.
LSEPK  = .TRUE.
# 输出 PARCHG.0020.0001.vasp 等；手动添加 .vasp 后缀（VESTA 不识别 .0001 后缀）

# 2) 只指定能量范围 [-10.0, -5.0]、不指定 k 点
NBMOD = -2
EINT  = -10.0 -5.0
LSEPB = .FALSE.
LSEPK = .FALSE.

# 3) 指定相对费米能级的范围 [Efermi-1.0, Efermi]
NBMOD = -3
EINT  = -1.0
```

**⚠ 最重要的判读经验**：**简并轨道必须合并输出**。讲义原例：288 号单独输出"电荷不完整，对称性不好"，**287+288（VBM）、289+290（CBM）才正确**（`[讲义]` L2 P124）。实测佐证：`mos2ws2/EIGENVAL` 第 3 个 k 点块给出 `287 −2.799036 occ=1.000000`、`288 −2.799017 occ=1.000000`、`289 −0.201564 occ=0.000000`、`290 −0.201561 occ=0.000000`，**到 1E-5 eV 级别与讲义 P122 一致** ✓。
**检查窗口是否合理**：`[讲义]` L2 P127：`OUTCAR` 最后会列出 partial charge 包含了哪些能带（每个 k 点一段）。

**STM 模拟（同一条路）**：`NBMOD = -3` + `EINT = 2.0` 表示显示费米能级以上 2 eV 的态；`EINT` 取负显示费米能级以下的态。**⚠ `EINT` 不是实验偏压**："`EINT` 和实验上所施加的偏压绝对数值并不直接对应，需要自己测试对比图像。"（`[讲义]` L2 P126）

### W5 · 功函数与静电势

**步骤**
```text
INCAR 关键行：
LVHAR = .TRUE.        # 输出纯静电势到 LOCPOT
LVTOT = .FALSE.       # 不要同时开（开了 LOCPOT 会变成含交换相关势的总势，见 S45）
NSW   = 0             # 单点（结构先优化好）
```
```bash
grep -i fermi OUTCAR              # 取 Efermi
# 路线 A：vaspkit 对 z 方向积分（自动判断真空能级位置，输出 POTPAVG.dat）
vaspkit   # 426 -> 3
# 回显形如：Vacuum-Level (eV): 6.673
# 还会提示：Check the Convergence of Vacuum-Level Versus Vacuum Thickness!
# 路线 B：p4vasp —— File-Load System 导入 LOCPOT -> Electronic / Local potential
#         -> Show, Z-direction -> 出现三条线，用中间那条 average 的线 -> Graph-Export
```
**计算**：`Φ = E_vac − E_F`。

**判据/锚点**
- 真空区必须有一段水平平台（否则 c 不够，见 S30）。
- 实测锚点：Au(111)-p(2×2)：`Efermi = 1.6561 eV`，`Φ = 6.673 − 1.6561 = 5.02 eV`；O/Au(111)-p(2×2)：`Evac = 7.196 eV`、`Efermi = 1.5863 eV`、`Φ = 5.6097 eV`。
- **趋势判据（`[讲义]` L2 P142）**：吸附带负电物种（如 O）→ 功函数**增大**；吸附带正电物种（如 K）→ 功函数**减小**。实测：O/Au(111) 比干净 Au(111) 的 Φ 大 ✓。
- **不对称表面的坑**：真空层里会有明显偶极，**上下表面所对应的真空能级位置不同** —— 所以取平台时要分清是哪一侧（同页）。

**用功函数预测电子流向（异质结/负载团簇）**：电子由**功函较低的一侧流向较高的一侧**。`[讲义]` L2 P143/P144 给的实例是 `Φ = 5.22 eV` 与 `6.43 eV`，结论"部分电子会从 g-C₃N₄ 转移到 TiO₂ 上"，故 **g-C₃N₄ 侧功函较低**。（5.22/6.43 分别属于哪个材料，讲义文本无法确定 `[待核对]`。）
**⚠ `[答疑]` D3-P37/D3-P38**：判断异质结电子流向**不要用 HOMO/LUMO** —— "homo 跟 lumo 和激发态有关系，异质结电子流动是**基态**的性质。算电荷密度差分和 bader 电荷，功函数就行了。"

### W6 · 自由能校正（ZPE + 熵）

**W6.1 表面吸附中间体（vaspkit 501）**
```bash
# 在频率计算完成的目录里运行
vaspkit
#   5        <- 主功能
#   501      <- 热力学量校正
#   298.15   <- 输入温度
# 输出：
#   Zero-point energy E_ZPE   :    1.515 kcal/mol    0.065715 eV
#   Thermal correction to U(T):    2.189 kcal/mol    0.094915 eV
#   Thermal correction to H(T):    2.189 kcal/mol    0.094915 eV
#   Thermal correction to G(T):    1.158 kcal/mol    0.050237 eV
#   Entropy S                 :   14.459 J/(mol*K)   0.000150 eV
```
（来源：`[讲义]` L3 P63/P64。这个功能**只适合计算表面吸附分子的自由能校正** —— 因为转动和平动的贡献在表面吸附以后被大大削弱，可以认为它们转化成了振动模式。）

**关键设置**：**表面吸附体系只放吸附物振动**。做法（`[讲义]` L3 P29）：
```bash
mkdir freq && cp <TS或IS的CONTCAR> freq/POSCAR && cd freq
vaspkit
#   403      <- 按 z 坐标固定原子
#   1
#   0 0.48   <- 固定 z 分数坐标 < 0.48 的原子（阈值按你的体系定）
cp POSCAR_fix POSCAR
```
**阈值怎么定**：找到要固定的原子中 z 分数坐标最大的那个，读它的 z；固定所有 z 小于 "该值 + 一点余量" 的原子。实测锚点：`day3/ts/dim/POSCAR` 里 O 的分数 z = **0.48812**，20 个 Au 的最大分数 z = **0.43488**，用 **0.48** 作阈值刚好只放开 O ✓。
**机制说明**：VASP 的有限差分（`IBRION=5`）**遵守选择性动力学、只位移标 T 的原子**（`[算例]` `freq/OUTCAR` 打印 `using selective dynamics as specified on POSCAR`）。所以 `DYNMAT` 第一行的自由度数 = 3 × 放开原子数（`4 32 3` / `5 33 6` / `5 34 9` = 元素种类数 / 总原子数 / 被位移的自由度数）。
**结果**：ZPE/熵里**只有吸附物的贡献**，slab 的声子被排除；这就是"干净 slab 的校正取 0"的物理原因。

`INCAR` 关键行（`[讲义]` L3 P30）：
```text
EDIFF  = 1E-7      # "和过渡态计算一样频率计算也需要很高的力精度"
IBRION = 5         # 计算 Hessian 矩阵、能量对坐标的二阶导数和频率
NFREE  = 2         # 每个方向位移次数（2 或 4）
POTIM  = 0.015     # IBRION=5/6 时的默认位移宽度
NSW    = 300       # 讲义说"NSW 和 EDIFFG 都不用设置或取任意值。NSW 不能取 0"
EDIFFG = -0.01     # 同上，取任意值
ISIF   = 2
```

**W6.2 气相分子（vaspkit 502）**
```bash
vaspkit
#   5
#   502
#   298.15     <- 温度
#   1          <- 压力（bar）
#   ...
# 产物：Thermal correction to G(T): ... eV
```
- `[讲义]` L3 P67/P68 也给了另外两条路：查 **JANAF-NIST** 实验热力学表（`https://janaf.nist.gov/`），或用 **Gaussian** 做频率算；三条路 `[答疑]` D3-P35/D3-P36 说"一样的"。
- **O₂ 必须反推**（见 W7）。
- `[答疑]` D3-P41/D3-P42：vaspkit 对其他常见分子（CO、CO₂、CH₄、NH₃ 等）的热力学校正"应该没问题"。
- **`[答疑]` D3-P47/D3-P48**：vaspkit **不输出**谐振近似下的配分函数 q。

**W6.3 低频截断**
- `[讲义]` L3 P55/P64：做表面吸附分子的自由能校正时，平动转动的 6 个自由度被限制转为振动，很可能出现小的振动频率使校正出的自由能异常低，所以"**把频率在 50 cm⁻¹ 以下的贡献都算成是 50 cm⁻¹**"（P64 说 50 或 60 cm⁻¹）。
- vaspkit 501 的输出里自己会打印：`frequencies less than 50 cm-1 are set to 50 cm-1.` 与 `Neglect PV contribution to translation for adsorbed molecules.`
- **适用范围**：**只用于表面吸附分子**，不要套到气相分子上。

**W6.4 频率的选取规则**
- `grep cm OUTCAR` 取频率。`f` 是实频，**`f/i` 代表虚频**（`[讲义]` L3 P33）。
- VASP 5.4.4 的打印顺序是**实频由大到小在前，虚频由小到大排在最后**（本文件由讲义内三个实例归纳：Au–O 的 12.609 → 12.052 → f/i 3.964；H₂O 的 6 个实频后跟 3 个 f/i；O₂ 的 3 个实频后跟 3 个 f/i）`[待核对]`。**稳妥做法是逐行看 `f/i` 标记，不要数前几行。**
- ZPE = ½ Σ hν：讲义 P32 的说法是"最后这个 52.148981 meV 是 hν 的值，`hν/2` 是零点振动能 ZPE，**求 zpe 可以直接读这个能量除以 2**"。**虚频不计入**（见 S15）。
- 吸附物模数 = 吸附原子数 × 3（实测：1/2/3 个吸附原子 → 3/6/9 个模）。这也是"频率只覆盖吸附物"的直接证据。

### W7 · 过渡态：CI-NEB

**W7.1 前置**
```bash
# 步骤一：分别优化初态 IS 与末态 FS
#   注意：原子顺序必须一一对应（S19）
# 步骤二：检查两结构相似程度
dist.pl ini/CONTCAR fin/CONTCAR
#   返回值 < 5 Å 一般可进行下一步；数值很大要检查原子顺序
#   基线：1.73920306203566
```

**W7.2 插点**
```bash
# 线性插值
nebmake.pl ../is/CONTCAR ../fs/CONTCAR 1
#   成功提示：OK, ALL SETUP HERE / FOR LATER ANALYSIS, PUT OUTCARs IN FOLDERS 00 and 02 !!!
#   自动生成 ./00 ./01 ./02；00 = IS，02 = FS，中间为插点；每个文件夹里的文件名都是 POSCAR

# 检查插点合理性（可跳过）
nebmovie.pl 0        # 用 POSCAR 生成 xyz；参数 1 用 CONTCAR
```
**插点数目**：`[讲义]` L3 P126 的经验规则是"≈ `dist.pl` 返回值 / 0.8"，**但这只是量级经验、不是硬约束**（该例 1.7392/0.8 = 2.17，实际只插 1 个点）。`[讲义]` L3 P124 的明确态度："**CI-NEB 插点越多越好，这是错误的结论！**…大多数时候插 3 到 4 个点已经完全能应付正常的过渡态计算需要"，"包含初、末态总共 **5 个甚至 3 个点**就能准确定位过渡态"。
**插点方法选择**
- `nebmake.pl`（线性）：**对近乎直线的原子扩散问题比较适用**；缺点是初始结构可能远离真实反应路径，甚至出现原子重叠。
- `idpp.py`（Image Dependent Pair Potential）：避免插值结构里某些原子相距太近。
```bash
python3 ~/bin/idpp.py POSCARis POSCARfs 4     # 得到 00 ~ 05 共 6 个文件夹
# 疑难体系：python3 ~/bin/idpp.py POSCARis POSCARfs 1
# 安装：pip install pymatgen pymatgen-diffusion（或 conda）；自测 import pymatgen / import pymatgen_diffusion
```
**判据**：把每个 image 的最短键长打出来。实测对照：线性插值 `c6h12-nebmake/03` 的 C–H = **0.5916 Å**（不合理），IDPP 同位置 = **1.0879 Å**（合理）。

**W7.3 抄 OUTCAR 供后处理**
```bash
cp ../is/OUTCAR ./00/
cp ../fs/OUTCAR ./02/
```

**W7.4 改 INCAR**
```text
#### Geo opt ####
EDIFFG = -0.03          # 难收敛可放宽到 -0.05
IBRION = 3              # VTST 识别并启动 VTST 优化算法的标志
POTIM  = 0              # 必须为 0
NSW    = 300
ISIF   = 2

#### VTST ####
ICHAIN = 0              # 开启 NEB 方法
LCLIMB = .TRUE.         # 爬坡即 CI-NEB
IOPT   = 1              # 1/2 适合精收敛；7 适合粗收敛
IMAGES = 1              # 插点个数
SPRING = -5             # 弹簧力常数，默认值即可

#### 电子步 ####
EDIFF  = 1E-7           # "这个参数非常关键！…好多过渡态计算不收敛原因都是因为力的精度不够"
```
**⚠ 关键**：`IBRION = 3` + `POTIM = 0` 是 **VTST 生效的标志**；必须用**编译了 VTST 的 VASP**，否则用的是 VASP 自带 NEB，"非常糟糕"（`[讲义]` L3 P125）。
**怎么判断管理员有没有编译 VTST**（`[答疑]` D4-P59/D4-P60）："用 `grep RMS OUTCAR` 看有没有信息。" （VTST 会在 `OUTCAR` 里补写相关的 RMS 信息。）

**W7.5 提交**
```bash
# POTCAR 与 KPOINTS 直接复制结构优化的
# 核数必须整除插点数量；为最大并行效率，节点数最好等于插点个数
```

**W7.6 跟踪收敛**
```bash
nebef.pl            # 或 nebefs.pl（不带参数）
# 后三列为 [最大原子受力] [能量] [相对初态的能量]
```
**收敛判据**：**所有插点的最大原子受力都 < |EDIFFG|**；插多个点时**所有点都要满足**（`[讲义]` L3 P133）。
**实测基线**：`5-ts/8-1-ex2.../nebef.dat` 6 行最大受力全部 < 0.03 ✓。

**W7.7 后处理**
```bash
nebresults.pl
# 依次做：nebbarrier.pl / nebspline.pl / nebef.pl / nebmovie.pl / nebjmovie.pl / nebconverge.pl
# 并把各文件夹 OUTCAR 打包压缩（不想被压缩：gunzip 0*/OUTCAR.gz）
# 产物：mep.eps（横坐标 = dist.pl 距离、纵坐标 = 能量）、vaspgr/ 下各插点收敛图、movie.xyz（Jmol 可看）
# nebspline.pl 单独跑会输出 spline.dat / exts.dat / mep.eps
```
**⚠ 判读纪律**：`mep.eps` 里**拟合出来的极值点不一定是真实存在的**，需要自己判断并做频率计算验证；"实际上一般我们只关注能量最高的 image 能量（用 `nebef.pl` 获取）"（`[讲义]` L3 P162）。`exts.dat` 的极值点要区分三类：可能存在的过渡态（需进一步验证）、我们要找的过渡态位置（进行频率验证）、需重新优化以确定极小值是否真实存在（L3 P163）。

**W7.8 频率验证**
```bash
# 只对能量最高的 image 做（S14）
mkdir freq && cp <能量最高的 image>/CONTCAR freq/POSCAR
cd freq
vaspkit   # 403 -> 1 -> <z 阈值>
cp POSCAR_fix POSCAR
# INCAR 见 W6.1（EDIFF=1E-7, IBRION=5, NFREE=2, POTIM=0.015）
grep cm OUTCAR        # 找 f/i
```
**判据**：**恰好 1 个虚频**，且一般 > ~100 cm⁻¹（表面体系经验门槛）。

### W8 · 过渡态：Dimer

**W8.1 初猜**
- 可以不需要 IS/FS，但"这个早晚要算的"，先算 IS/FS 有助于初猜与理解反应（`[讲义]` L3 P142）。
- 初猜来源：① 在建模软件里从 IS/FS 手动调到"可能的过渡态"；② 用 `nebmake.pl` 产生几个中间点，**选能量最高的那个**作为 Dimer 初始结构。

**W8.2 MODECAR**
```bash
modemake.pl ../is/CONTCAR ../fs/CONTCAR
# 或者：modemake.pl ../is/CONTCAR ./POSCAR
#   第二种要把 is/CONTCAR 后面的原子速度部分都删掉，以保持和 POSCAR 行数一样
```
- `MODECAR` **定义初始的 dimer 方向**；**没有这个文件程序会自己随机猜一个方向——强烈建议设置 `MODECAR`**（`[讲义]` L3 P144）。
- 格式：每个原子一行、每行 3 个数（dx dy dz），逐原子排列。示例里前若干行是 ~1E-14 量级（几乎为零），**最后一行是主分量** `2.4199310346E-01 9.3308559935E-01 1.6190951779E-01`。
- "`MODECAR` 就是 dimer 的方向，也就是我们期待的虚频的振动的方向；开始 DIMER 计算以后每一 Dimer 旋转步都会更新 `NEWMODECAR` 为新的 dimer 方向"（L3 P145）。

**W8.3 INCAR**
```text
#### Geo opt ####
EDIFFG = -0.03
IBRION = 3
POTIM  = 0
NSW    = 300
ISIF   = 2

#### VTST ####
ICHAIN = 2              # 开启 VTST 中 DIMER 的算法
IOPT   = 2              # 为保证稳定收敛，推荐 7、2、1
# DdR = 5E-3            # The dimer separation（默认注释态）
# DRotMax = 1           # 每个平移步最多旋转次数
# DFNMin = 0.01
# DFNMax = 1.0

#### 电子步 ####
EDIFF  = 1E-7           # "由于 Dimer 的两个点间距很小，要求力计算精度极高"
```
**⚠ 把 CINEB 的段落注释掉**（见 S24）。

**W8.4 跟踪 `DIMCAR`**

| 列 | 含义 | 判读 |
|---|---|---|
| `Step` | 平移 Dimer 的步数（每个平移步里可以包含数个旋转步） | — |
| `Force` | Dimer 在任意自由度上的最大受力 | **这个 Force < \|EDIFFG\| 不是收敛标准**；收敛标准是**最大原子受力 F < \|EDIFFG\|** |
| `Torque` | Dimer 扭矩 | 旋转总是朝扭矩减小方向；**`Torque < 1` 时进入平移 Dimer 步** |
| `Energy` | Dimer 中点的能量 | **不是电子熵外推到 0 的能量，不能用作最终 TS 能量**；TS 能量取 `OSZICAR` 最后一个 `E0` |
| `Curvature` | Dimer 曲率 | 每个平移步里应逐渐下降；**在 TS 位置 Dimer 方向就是反应方向** |
| `Angle` | 旋转角度 | 每个平移步里也应逐渐下降 |

（来源：`[讲义]` L3 P149/P150/P151）
**最关键的是 Force、Torque、Curvature 三个量**：接近过渡态的标志是 **Force 逐渐变小、并且 Curvature 是负值**；Curvature 不是负的说明离过渡态还较远。

**W8.5 收敛确认三条命令**
```bash
grep converged OUTCAR     # 出现：OPT: skip step - force has converged
grep RMS OUTCAR           # 看 FORCES: max atom, RMS 行，最后一个受力 < |EDIFFG| 即正常收敛
tail -1 OSZICAR           # 取最后一个 E0 作为过渡态能量
```
（来源：`[讲义]` L3 P153。讲义示例：`F= -.66261570E+02 E0= -.66258695E+02  d E =-.705902E-05`；实测该算例 **207 个离子步、9620 秒**。）

**W8.6 看虚频方向**
```bash
dimmode.pl CENTCAR NEWMODECAR 32 0.5
# 生成 dimmode.xyz（以 CENTCAR 为中心、NEWMODECAR 为振动方向做动画），用 Jmol / VMD 打开
#   Jmol 里：Tools - Animate - Loop
# ⚠ 该脚本必须保证 CENTCAR 第一行是元素组成
```

**W8.7 与 CI-NEB 互相验证**
- 两种方法给出的 TS 能量应接近。实测基线：`ts-cineb` 的 `E0 = -66.256661` vs `ts-dimer` 的 `E0 = -66.258695` → **差 2.0 meV**（此比较是本文件算的 `[待核对]`）。
- **选型参考**（`[讲义]` L3 P164/P165）：简单扩散、路径近似直线 → CI-NEB 效率高（该例 13 步收敛）；初猜好 → Dimer 效率很高；初猜不好 → Dimer 经常失败；**复杂催化反应（两种方法单独都低效）→ 先用 CINEB/NEB 粗搜拿能量最高的结构作为 Dimer 初猜，再用 Dimer 精修**。

### W9 · 隐式溶剂（VASPsol）

**编译前提**（`[讲义]` L4 P49，基于 VASP 5.4.4）：
1. 在 makefile 的 `CPP_OPTIONS` 里加入 `-Dsol_compat`；
2. 把 `VASPsol/src/solvation.F` 复制到 `./src`。
（官方站点 `http://vaspsol.mse.cornell.edu/`；模型是 linearPCM，GLSSA13。）

**用法：相对真空计算只改三处**
```text
NSW    = 0              # 把离子步关掉
LSOL   = .TRUE.         # 打开溶剂（默认水溶液；算例里也写成 LSOL = T）
LRHOB  = .TRUE.         # 想打印 bound charge 才需要
```
（`[讲义]` L4 P54；`[算例]` 两组 `vaspsol/INCAR` 与普通 `INCAR` 的**全部差异**就是这三项 + `NSW` 从 300 改 0。）

**换溶剂要显式写介电常数**
```text
EB_K    = 78.400000     # relative permittivity of the bulk solvent（水 = 78.4）
SIGMA_K =  0.600000     # width of the dielectric cavity
NC_K    =  0.002500     # cutoff charge density
TAU     =  0.000525     # cavity surface tension
```
- `[讲义]` L4 P54：`EB_K` 查表可知其他溶剂的介电常数；**其他三个参数不能直接查表得到、需要拟合，而 VASPsol 程序并没公开其他溶剂的参数，所以目前只能改变介电常数近似代表其他溶剂。**
- **⚠ 两组算例一个都没写这四个参数** → 走的是程序默认值。**要换溶剂必须显式写 `EB_K`**；只写 `LSOL=T` 得到的就是 78.4 的水。

**判据**：`OSZICAR` 里出现 `SOL:` 行。
**量级锚点**：H₂O 分子 12×12×12 Å 盒、Γ 点、`ENCUT=400`、`GGA=PE`、`ISPIN=1` —— 真空 `E0 = -14.226768 eV` → VASPsol `E0 = -14.539553 eV`，**ΔE = −0.312785 eV（−7.213 kcal/mol）**。
**⚠ 未核对**：同一次运行 `OSZICAR` 里还打印 `SOL: 6 -0.44079E+00 0.31696E-01 -0.40909E+00 63`，其第一项 −0.4408 eV 与总能差 −0.3128 eV **不等价**；这两个数分别代表什么、差从哪来，该目录**没有 `OUTCAR`** 可以分解，`[待核对]`。

**什么时候必须上溶剂化**（`[讲义]` L4 P32/P44/P24/P21）
- 需要**能垒**时：Nørskov 04 方法不能算能垒，"这时候可能需要引入一些溶剂分子"；
- 需要**静电势/双电层/电极电势的连续调节**时（恒电势显式溶剂路线当前有三个已知问题：AIMD 模拟水/空气界面不能保持；静电势依靠添加离子改变、不能连续调节；反应前后静电势不等）；
- 碱性下考虑 **Volmer（H₂O 解离）**步骤的过渡态；
- **纯热力学台阶图 + CHE 不需要溶剂化**（讲义 P3 自己就声明忽略了静电势与溶剂化）。

**溶解自由能的标准态校正**：`[讲义]` L4 P52 给 **+1.89 kcal/mol**（= 0.08196 eV）；`[答疑]` D4-P51/D4-P52 只给了一个外部博客链接，**没说清加在哪个量上、气相和溶液相各加几次**，`[待核对]`。

**显式溶剂下的自由能校正**：`[答疑]` D4-P39/D4-P40："显示溶剂模型，就**把所有溶剂和 slab 都固定住算频率**，再用 vaspkit 计算自由能校正。"
**显式溶剂 + 频率的一致性**：`[答疑]` D4-P31/D4-P32："最好用 vaspsol 下做频率校正，如果算不动，可以用没有 vaspsol 情况算也行。"
**显式溶剂盒子的高度**：`[答疑]` D1-P9/D1-P10："由水分子的个数决定，我们上课的例子是 **20 个分子**，可以自己调节。"
**加真空层的目的**：`[答疑]` D1-P47/D1-P48："可以加，也可以不加，**加真空层的目的是为了得到真空能级的，并不是为了避免和下表面的作用**。"

### W10 · 二维材料面内优化（OPTCELL）

```text
#### INCAR ####
ISIF = 3                     # 晶胞优化
NSW  = 300
EDIFFG = -0.01
# 面内两个方向放开、c（含真空）完全冻结
```
```text
#### OPTCELL 文件（放在计算目录里，三行，无空格、无分号、只有回车换行）####
100
110
000
```
（`1` = 优化该矩阵元，`0` = 不优化；对应 POSCAR 的 3×3 晶胞矢量矩阵。）

**前提**：必须用**改过 `constr_cell_relax.F` 的 VASP**（`[讲义]` L1 P32）。普通官方源码版没有效果。
**判据**：比较 `POSCAR` 与 `CONTCAR` 的晶格矢量 —— **a、b 变了，c 严格不变**。
**实测锚点**：
- `day1/mos2`：a 由 3.1659999 → **3.1822493**；**c 严格保持 18.4099998474 不变** ✓
- `day1/vdw-df2`：a 由 3.1659999 → **3.2806599**（比 PBE 大 +3.09%）；c 同样不变 ✓
- `oer/slab`：弛豫后 a = 9.73274 Å、b 变为 (−4.61207, 8.57073)、**c 仍精确为 15.00000 Å** ✓
**反向验证**：`day1/fe2o3` 没有 `OPTCELL` 且 `ISIF=3` → `CONTCAR` 三个基矢全变并出现非对角分量（a 的 z 分量 0 → 0.0205958）✓
**⚠ 坑**：`OPTCELL` **不会在 `OUTCAR` 的参数区回显**（`mos2`/`vdw-df2` 的 `OUTCAR` 里都 grep 不到）。**判断是否生效只能比较 `POSCAR` 与 `CONTCAR`。**
**⚠ 写法坑**：不要写 `OPTCELL(100; 000; 000)`（带空格和分号）—— `[答疑]` D4-P1/D4-P2 的实例显示这样写会让"第一个和第三个晶胞矢量的 x 坐标发生变化"。

### W11 · 表面能 与 化学势相图

**W11.1 表面能（**先确认你没有赝氢**）**

```
γ = [ E(slab) − N × E(bulk) ] / (2 × A)
```
- `N` = slab 里的化学式单元数，`E(bulk)` = **用与 slab 完全相同的设置**算出的体相每单元能量（`[官方]` `references/official/pages/LREAL.md` 明文要求参与相减的计算设置一致）；
- `A` = 一个表面的面积；**除以 2A** 是因为 slab 有上下两个表面。
- **⚠ 前提**：`[答疑]` D2-P55/D2-P56 与 `[答疑]` D3-P23/D3-P24 都明确："**赝氢钝化以后这样的没法算表面能。只能钝化前算，而且算出来的是上下表面的平均表面能，单独的可能没法算。**"`[答疑]` D4-P57/D4-P58 给的替代路径："算表面能干脆就不用赝 H，直接上下表面一起优化。"
- **非对称表面也能算**：`[答疑]` D4-P17/D4-P18："非对称表面可以算，就按照我们讲的方法算就行了，算出来是上下表面的**平均**表面能。"
- **该考虑几个面**：`[答疑]` D3-P25/D3-P26："更稳定的暴露，一般只考虑最稳定表面，**特殊情况可能不稳定表面起到主要作用**。"
- **判据**：层数 +2 时 γ 变化 < 0.02 eV/Å²。

**W11.2 不同元素相同元素的化学势（定义参考基准）**

- `[答疑]` D3-P19/D3-P20 给的处方（原文）："**定义参考基准，比如 `Mu(O)` 是自变量，可以把一定温度压力的 H₂O 和 Al₂O₃ 作为参考基准，`Mu(Al) = 1/3(G(Al₂O₃) − Mu(O))`。**"
- 实操顺序：
  1. 选定一个**自变量**（通常是 O 的化学势 `μ_O`，因为它随温度和 O₂ 分压变）；
  2. 用别的稳定相作参考基准，把其余元素的化学势**反解**出来（如上式的 `μ_Al`）；
  3. 扫 `μ_O` 画相图。
- `[答疑]` D3-P27/D3-P28 补充了覆盖度那条线："先看一个 P(1×1) 的表面能最多吸附几个分子，然后根据扩包的大小，和最终吸附的数量相除就行了。**氧气分子的自由能/2 就是化学势。**"
- **化学势与实验条件的联系**：`[答疑]` D1-P39/D1-P40（问：稳定表面与气氛/氧分压有关，实际模拟怎么选？）→ "**第三天讲，这个可以算。如果实验能给出结论就用实验的结论。**"
- **缺陷形成能的边界条件**（`[答疑]` D4-P47/D4-P48，唐刚老师的答复）：算缺陷形成能的化学势边界条件比催化更复杂，要构建化学势的相图（固体的行话叫**化学窗口**），选取 poor / rich 的代表性化学势点再代入；自变量是 `Ef`，范围一般是 `0 ~ Eg`；难点是能量的修正 `ΔV`（含三个修正）；可参考 Su-Huai Wei / Zewen Xiao 的文献；也可用自动化软件（回复里给了一个自动化校正脚本的链接）。**⚠ 这条属于"另一位讲师的口头答复"，本手册只转述方法框架，不写具体公式**（公式在文本里没有完整给出）。

**W11.3 氧空位形成能**
- `[答疑]` D3-P39/D3-P40 给的式子（原文）："氧空位形成能直接按照吸附脱附能的计算形式算就行了 `Ev = G(MO1-x) + 1/2 G(O2) − G(MO)`。"
- **⚠ `G(O2)` 必须用反推值**（见 W12），不要用 O₂ 单点的 DFT 电子能。

### W12 · O₂ / CO / N₂ 的自由能反推 与 电催化台阶图

**W12.1 参考态约定（`[讲义]` L4 P9）**

```text
1) 在 pH = 0, U = 0 V (SHE) 条件下：G(H2)/2 = G(H+) + G(e-)
   —— 即把 (H+ + e-) 整体替换成 ½G(H2)
2) G(H2O) 是液态水的能量 = 饱和蒸气压下的水蒸气能量（常温下 ~0.035 bar）
   用 vaspkit-502-298.15-0.035-1 计算
```

**W12.2 O₂ 必须反推（**本手册认定的最值钱的一条处方**）**

```text
2 G(H2O) - 2 G(H2) - G(O2) = -4.92 eV     （先算 G(H2O) 与 G(H2)，再解出 G(O2)）
同理 CO、N2 也需要能量反推
```
- **为什么**：`[答疑]` D4-P19/D4-P20 已经把误区点破 —— 学员问"通过 vaspkit 进行热力学校正之后氧气分子的吉布斯自由能和文献值吻合得很好了，还是不能用计算出来的吉布斯自由能吗？" → 讲师答："**ΔG 校正值吻合的很好。但是 O₂ 的 DFT 计算出来的电子能量不准确，所以才要用热力学数据减。**"**错的不是热力学校正项，是 DFT 电子能本身。**
- **参考数值表（`[讲义]` L4 P9 原文照抄）**

| 物种 | Pressure/bar | Temperature/K | E(DFT)/eV | ΔG/eV | G/eV |
|---|---|---|---|---|---|
| O₂(g) | 1 | 298.15 | （未给） | （未给） | **−9.91** |
| H₂(g) | 1 | 298.15 | −6.76 | −0.045 | **−6.80** |
| H₂O(l) | 0.035 | 298.15 | −14.22 | −0.001 | **−14.22** |

- **读法**：`G = E(DFT) + ΔG`，其中 ΔG 列就是 **ΔZPE − TΔS 的热力学校正**。O₂ 行的 `E(DFT)` 与 `ΔG` 两格为空、只有一个 G，正是因为它不能直接算。
- **⚠ 该表是"手填 + 取整/截断"的汇总表**：`[算例]` 实测非溶剂化 H₂O 的 `OSZICAR` 末行是 `E0 = -.14226768E+02`（**−14.226768 eV**），四舍五入到两位应是 −14.23，而表里是 −14.22（是**截断**）。同一表里 H₂ 的 `G = E+ΔG = −6.805`，G 列却填 −6.80。**误差量级 0.001–0.007 eV，可用于量级与流程，不可作为高精度数据源**（化学精度通常按 0.05 eV 计）。
- **`oer.xlsx` 与讲义差 0.01 eV 的原因**：反解可知若用 `G(H2) = −6.805`（未取整）则得 G(O2) = −9.91；若用表里填的 −6.80 则得 **−9.92**。

**W12.3 表面中间体的校正量从哪来**

`[算例]` `oer.xlsx` 里表面中间体的校正列（表头写 `DG /eV`，数值关系恒为 `D 列 = B 列 + C 列`）：

| 中间体 | E(DFT)/eV | 热力学校正/eV | G/eV |
|---|---|---|---|
| slab（干净表面） | −279.08406 | **0** | −279.08406 |
| *OH | −289.20002 | **+0.272014** | −288.928006 |
| *O | −283.83975 | **+0.027952** | −283.811798 |
| *OOH | −293.6715 | **+0.340296** | −293.331204 |

- 干净 slab 的校正取 **0**（吸附前后抵消的假设）；三个中间体的校正量级 **0.03–0.34 eV**，**远大于**气相分子的 0.001–0.045 eV。
- **本文件从 `freq/OUTCAR` 的频率反推**（`[待核对]`）：按 `ZPE = ½Σhν` 复算得 *O 的 Σhν = 118.248286 meV → ZPE = 0.059124 eV，与校正列 0.027952 相减 ⇒ `TΔS ≈ 0.031172 eV`；*OH 的 Σhν = 676.106484 meV → ZPE = 0.338053 eV ⇒ `TΔS ≈ 0.066039 eV`；*OOH 的 Σhν = 878.900013 meV → ZPE = 0.439450 eV ⇒ `TΔS ≈ 0.099154 eV`。**结论：算例的"校正列" = ΔZPE − TΔS，且 ΔZPE 就是按吸附物自身振动模的 ½Σhν 算的** —— 这一条讲义正文完全没写。

**W12.4 台阶图（CHE）与过电势**

```text
ΔG1 = G(*OH) + ½G(H2) + eU − G(*)   − G(H2O)
ΔG2 = G(*O)  + ½G(H2) + eU − G(*OH)
ΔG3 = G(*OOH)+ ½G(H2) + eU − G(*O)  − G(H2O)
ΔG4 = G(O2)  + G(*)   + ½G(H2) + eU − G(*OOH)
其中 e = -1，U 是外加电极电势(SHE)；U = 1.23 V 时 eU = -1.23 eV
```
（`[讲义]` L4 P8；原文把下标与 `*` 打散成 `G ∗ OH` 这类形式，此处已按化学语义还原。）
- **决速步判据**：`G_OER = Max(ΔG1, ΔG2, ΔG3, ΔG4)`（`[讲义]` L4 P11）。
- **过电势**：`η = Max(ΔG) − 1.23`。实测锚点：CoN₄ 单层 OER 的 **η = 0.486 V**，决速步是第 2 步（*OH → *O，ΔG = 1.716 eV）—— 讲义 P13/P26 只给了台阶能量，**没给体系名与过电势**，这两个数是 `oer.xlsx` 补齐的。
- **ORR 方向相反**：`U = 能量下降最小的一步的能量 / e`（`[讲义]` L4 P14）。
- **必须做闭合性检查**：用同一张表的数字逐步复算，末步必须回到总反应能（OER 是 **4.920000 eV**）。实测 `oer.xlsx` 的 G 列每个值都比用精确参考态算的**小 6×10⁻⁵ eV**（因为它是用取整到 3 位小数的 −307.524 作参考态减出来的），导致末行显示 **4.91994** 而不是 4.92。**它不影响过电势**（相减时常数偏移抵消：η = 0.486208 V 两种算法完全一致），但**说明闭合性检查必须写成脚本，不能靠手工取整**。

**W12.5 pH 与电势进入公式的位置**

```text
pH 只通过 H+/OH- 的化学势进入：
  G(H+) + G(e-) = ½G(H2) − 0.0592 · pH
  E(H+) = ½E(H2) − 0.0592 pH             （由 H2 ↔ 2H+ + 2e- 得）
ΔG = 2G(H2O) − 4G(H+) + 4G(e-) + G(O2)
   = 2G(H2O) − 4(½G(H2) − 0.0592·pH) + G(O2)
pH = 0  → ΔG = −4.92 eV
pH = 14 → ΔG = −1.605 eV
```
（`[讲义]` L4 P15/P17；本文件复核：−4.92 + 4 × 0.0592 × 14 = **−1.6048** ≈ −1.605 ✓）
- 酸性（pH = 0）标准电极电势 **1.23 V**（P16 表格写 **+1.229 V**）；碱性（pH = 14）**0.401 V**（本文件复核 1.229 − 0.0592×14 = 0.4002）。
- **酸碱可以互换**：`H+ + OH− ⇌ H2O`，可以直接把 OH⁻ 换成 H⁺ 计算，"酸性和碱性条件下计算方式是一样的"（`[讲义]` L4 P16）。`[答疑]` D4-P25/D4-P26："如果**只考虑热力学，没有区别**，但是反应过程参与的物种可能不同。H₃O⁺，H₂O。"
- **电势以 `eU` 的形式逐项加在每个电化学基元步骤上**：4 步各含一个 `eU`，所以把 U 从 0 抬到 1.23 V 会让第 n 步的累积自由能整体下移 n × 1.23 eV（`[讲义]` L4 P8；本文件推论，与 `oer.xlsx` 的两列换算一致）。

**W12.6 判"这一步算不算电化学基元步骤"（一条极实用的判据）**

- **判据**：**这一步里有没有 `H+ + e−` 参与；没有就说明它不含 `eU` 项、不随 U 平移。**
- 两条原文依据：
  - `[答疑]` D4-P45/D4-P46：`O2 + * → *O2` 这一步"**不是电化学基元步骤，不涉及 `H+ + e` 产生的过程，可以加到台阶图里，但是这一步不会随着 U 的变化而变化**"。
  - `[答疑]` D4-P15/D4-P16：NRR 里"**N₂ 解离或者 H₂ 解离这种步骤不是电化学基元步骤，在电化学计算里没有 `eU` 这一项，不会受电势 U 的影响改变台阶的能量**"。
- **推论（可操作）**：台阶图里出现步骤能量不随 U 平移时，先按这条判据检查，而不是怀疑算错。

**W12.7 什么时候必须加能垒/溶剂化**

- 需要**能垒**时：`[讲义]` L4 P24："用 Norskov 04 年的方法不能计算反应的能垒，一些电催化过程反应能垒很重要，这时候可能需要引入一些溶剂分子。"
- 碱性下的 **Volmer（H₂O 解离）**：`[讲义]` L4 P21："如果多一步考虑，要计算 Volmer（即 H₂O 的解离）过程的过渡态，这多在碱性条件下需要考虑。"也可以同时考虑第二步 Tafel 或 Heyrovsky 的过渡态，"通过对比两个步骤哪个是决速步，来对比设计催化剂"。
- **双分子表面反应的建模顺序**（`[答疑]` D4-P43/D4-P44）："算过渡态之前，**要两个分子都放到表面同时优化的**。H₂ 可以直接用吸附 H 往后算，就是把 H₂ 的解离过程忽略掉。"并且"**要先把中间态一步一步都算出来，然后再算能垒**"。
  - 给出的分解示范：`CO2 + H -> H2O + CO` 可能包含好几个基元步骤 —— "H₂ 先解离吸附，然后 CO₂ 吸附，再发生 `CO2+H -> COOH` 中间体，然后 `COOH+H -> CO + H2O`"。
- **Heyrovsky 第二个 H 的初始位置**（`[答疑]` D4-P11/D4-P12）："第二个 H 需要用显示（显式）溶剂模型，用 **H₃O⁺ 的形式**摆在第一个吸附 H 的附近。"（单一来源，`[待核对]`）
- **火山图用吸附能还是结合能**：`[答疑]` D4-P65/D4-P66："**没有本质区别，都行**，吸附能和结合能不是差不多嘛，就是有没有校正的区别。最后得到火山曲线趋势都一样。"
- **不要用上一步的放热去"抵消"下一步的势垒**：`[答疑]` D4-P33/D4-P34："这个说法可能本来就有点问题，有些文献解释说前一步强放热会引发局部过热，有利于下一步翻高能垒，**这种说法很定性，不好说**。"

### W13 · AIMD 与显式溶剂界面

**W13.1 AIMD 的最小 INCAR（把结构优化的离子步换掉即可）**

```text
IBRION = 0
NSW    = 20000        # maxcycle
POTIM  = 1            # timestep of ionic movement（fs）
SMASS  = 0            # >= 0, NVT ensemble，值决定与热浴耦合的频率
MDALGO = 2
TEBEG  = 300
TEEND  = 300
```
（`[答疑]` D2-P47/D2-P48 原文："AIMD 输入文件很简单，就是把结构优化的离子步换成下面就行了。**其他不用变**。"）
- **⚠ `IBRION = 0` 时 `POTIM` 必须给**，否则程序启动后立刻崩（`[官方]` `references/official/pages/POTIM.md`）。
- **`ISYM = 0`**：`[官方]` 明确 MD 应该设 0（`references/official/pages/ISYM.md`）。
- **升温/恒温两套模板的差别**（`[算例]` `things to study/INCAR` 与 `INCAR(1)` 只差 MD 段）：`NSW` 2000 vs 20000、`SMASS` −1 vs 0、`MDALGO` 注释 vs 2、`TEBEG/TEEND` 100→300 vs 300/300、`NBLOCK` 20 vs 无。**推论**：前者是 100→300 K 的升温退火（`SMASS=-1` → NVE），后者是 300 K 恒温（`SMASS=0` + `MDALGO=2` → NVT Nosé-Hoover）`[待核对]`。
- **AIMD 的用途之一**是取构象平均，而不是替代优化：`[答疑]` D2-P51/D2-P52 在问"吸附物的初始位置怎么放"时给的答复是"多摆几个可能的构型再优化，取能量最低的构型。**也可以做个 AIMD 模拟退火看看，不过一般没必要。**"

**W13.2 显式溶剂 + 恒电势路线的平均功函流程**

```text
第一步：建模，优化结构，AIMD 预平衡
第二步：跑 20 ps 的 AIMD，每 1 ps 取出一个结构计算单点，拿到功函；
        把 20 个功函做平均，即得到当前组分的平均功函
```
（`[讲义]` L4 P42。）
- **零点换算**：`[讲义]` L4 P41 用 **SHE 相对真空的绝对电位 = 4.44 V**；示例：`2.40 V(vs Vacuum) ↔ −2.04 V(vs SHE)`、`3.81 V ↔ −0.63 V`（本文件复核：2.40 − 4.44 = −2.04 ✓；3.81 − 4.44 = −0.63 ✓）。
- **⚠ 必须先声明零点**：配套 `VASPsol原理.pdf`（arXiv:1601.03346v1）用 PZC 拟合出的是 **4.6 V**。同一功函 2.40 V(vs Vacuum) 用 4.44 V 得 −2.04 V，用 4.6 V 得 **−2.20 V**。→ 见 S58。
- **⚠ `L4 P42` 图注的 −2.4 V (vs SHE) 与 `P41` 的 −2.04 V 不是同一次计算**，不可互换。
- **这条路线的三个已知问题**（`[讲义]` L4 P44）：AIMD 模拟水/空气界面不能保持；静电势依靠添加离子改变、不能连续调节；反应前后的静电势（电极电势）不等。对策是"通过扩包逼近 constant potential 状态"。

**W13.3 深能级对齐（没有真空层时）**
- `[答疑]` D2-P11/D2-P12："如果没有真空层的体系可以去对齐深能级，比如加了 `_sv` 赝势对齐最内层的能级。或者 Core level 对齐。"具体关键词 `ICORELEVEL = 1`（`[答疑]` D2-P67/D2-P68）。
- **用途举例**（同一个答疑）："从固体中提取一个分子，原固体和新分子的 DOS 放在一起比较，它们的费米能级是否需要对齐调整？" → "**需要对齐**。"
- **单一来源，L2 全 157 页未提**，`[待核对]`。

### W14 · 频率之外的振动/光谱计算（**资料覆盖有限，只列已核实的部分**）

**IR 光谱（红外）**
- 讲义 L3 **只覆盖 `IBRION = 5` 的有限位移频率计算**。核对结论：`IBRION = 7`、`IBRION = 8` 在 L3 全文中**一次都没出现**；`DYNMAT` 出现 **0 次**；`IBRION = 6` 只在"`IBRION = 5` 或 6 时的默认值"这一句里被附带提到。
- `things to study/` 下全部 `INCAR`/`INCAR.bak` 里 `IBRION` 只出现 **2、3、5、7** 四个取值。
- **仓库里确有一套 IR 流程的输入**：`线上中级班-催化资料/4-thermo/7-5-IRspectrum/INCAR` 用 `IBRION = 7`、`NFREE = 2`、`POTIM = 0.015`、`NSW = 1`、`LEPSILON = .TRUE.`、`NWRITE = 3`，`SYSTEM = ethanol`，配套有 `spectra.dat`、`ir.sh`、`ir_6.sh`、`spectra.exe`。
- **⚠ 本手册不给 `IBRION = 7/8` 与 `DYNMAT` 的用法** —— 讲义没讲，本文件也没有实验证据，按契约不编。（如果你要从这套算例推流程，请把它当成 `[待核对]` 的一手素材，并回到 VASP 官方文档核对 `IBRION` 页。）

**声子谱 / 热力学量（体相）**
- `[答疑]` D3-P21/D3-P22（问块体自由能、熵怎么算）→ "这不属于表面甲酸（催化）的东西了，**一般我们直接忽略**，要算的话用 **phonopy**"，并给了 phonopy 的 thermal properties 相关文档链接。
- 有限位移法本身**只能算 Γ 点**：`[讲义]` L3 P28 原话"单独 VASP 只计算 Γ 点的振动频率，**必须结合 phonopy 才能计算声子谱**"。

**单一来源、未核实的空频路径**：`[算例]` `4-thermo/*/INCAR` 里出现的 `IBRION = 7` 是唯一证据，`L3` 正文没有配套说明，`[待核对]`。

### W15 · 单原子/团簇催化剂的建模与计算要点（汇总散落条目）

- **团簇构型**：全局极小值搜索（模拟退火、ase、ssw、calypso、uspex 都可以做）；"如果粗糙点，多优化几个构型看能量最低的"（`[答疑]` D1-P19/D1-P20）。
- **建团簇**：① `ase.cluster` 模块（可方便构建一些经典纳米颗粒）；② 在建模软件里先建一个比较大的 bulk 晶胞、`unbuild crystal` 去掉边界，然后不断手动删除部分原子，或直接用铅笔功能拉出想要的团簇形状再优化（`[答疑]` D1-P1/D1-P2）。
- **V₂O₇ 这类小团簇**："直接用铅笔功能一点一点拉出来就行"（`[答疑]` D1-P15/D1-P16）。
- **团簇大小与吸附物**：想用 Pt₇/TiO₂ 模拟苯或甲醇的吸附，答复是"可以，不过对于含有苯这样大分子的表面模型要建立的大一些"（`[答疑]` D2-P37/D2-P38）。
- **单原子体系能不能用 d 带中心**：能，但"规律没有纯金属那么好"；决定单原子催化吸附能的除了 d 带中心还有**价态、配位环境**等因素（`[答疑]` D2-P15/D2-P16 等，见 §4.1）。
- **吸附能强弱比较时可用的分析手段清单**（`[答疑]` D2-P39/D2-P40）："算吸附能。然后我们讲过的好多电子结构分析手段都能用。**DOS、d-band center、电荷密度差分、原子电荷、ELF、COHP、NBO 等等都能用。**"
- **判断"哪个原子与表面接触"**：`[答疑]` D2-P53/D2-P54："多试几个构型，取能量低的。"
- **覆盖度**：`[答疑]` D2-P57/D2-P58 关于 OH⁻ 应该在哪、个数怎么定 → "应该在什么位置，还是多优化几个可能的位置。**要看覆盖度的。**"

### W16 · 带电/质子化中间体

- **改总电子数**：`[答疑]` D1-P11/D1-P12："改变 `NELECT`，默认的数值在 `grep NELECT OUTCAR` 里读取，重启计算把总电子数减一。"（"氢质子吸附"就减一。）
- **或者加抗衡离子**：`[答疑]` D1-P11/D1-P12："或者添加抗衡离子，在下表面加一个 OH。"
- **⚠ 背景电荷风险**：`[答疑]` D3-P45/D3-P46 明确提醒"可以改 `NELECT`（**可能会引起背景电荷问题**）或者加额外抗衡离子"。带电体系还要注意：**非立方超胞 + `LDIPOL=.TRUE.` 会让 VASP 直接停**（见 S49）。
- **标准态校正（溶解自由能）**：`[讲义]` L4 P52 给 **+1.89 kcal/mol**（本文件换算 = 0.08196 eV）；数值上等于 `RT·ln(24.46) ≈ 0.5922 × 3.197 = 1.893 kcal/mol`（1 atm 理想气体 → 1 mol/L 溶液的标准态换算）—— **这个出处解释是本文件算的，讲义与答疑都没给**，`[待核对]`。
- **判据**：`grep NELECT OUTCAR` 回显的电子数 = 你的设定值；电荷密度/静电势的真空平台仍然平（说明没被背景电荷毁掉）。

---

## §3 建模实操

> 目标：把"正确的表面模型"做出来。物理上为什么这么切 → `decide.md`。

### 3.1 切表面（cleave surface）

**建模工具里**
- `Build - Surface - Cleave surface`；**用 `0 0 1` 切出来的就是 (0001) 面**；厚度先给 1.0 再调（`[讲义]` L1 P52）。
- 调整 `Top` 可以改变终端（O-terminated / Al-terminated）。
- **⚠ 移动 `Top` 时上/下表面会同时变化** —— slab 有两个表面，搭模型时要时刻记得两个表面（`[讲义]` L1 P54）。
- 切面厚度：`[讲义]` L2 P59 给的实例是 Ni(100) "取 **6 个原子层**厚度即可"。

**切面四条原则（逐条自检，`[讲义]` L1 P57）**
1. 尽量保证**化学计量比与 bulk 一样**（如 Al:O = 2:3）。自检：数原子，写成分数比对 bulk。
2. 尽量保证**表面能最小**，即暴露的表面原子与实验一致；**氧化物优先让氧暴露**。
   - 补充（`[答疑]` D1-P33/D1-P34）：硫化物/硒化物/磷化物**基本也是**选 S/Se/P 暴露，"但是也有很多特例，暴露金属表面都有可能"。
3. 是否添加基团给不饱和原子，参考前人文献与实验经验：
   - **一般过渡金属化合物都不需要加额外的基团**；
   - Al₂O₃、SiO₂ 等可考虑用 **−OH** 饱和；
   - Si、GaN、InSe、ZnSe 等共价晶体/半导体用**赝 H** 饱和。
   - 补充（`[答疑]` D1-P15/D1-P16）：γ-Al₂O₃ **要**钝化，其他看相似文献可能不需要。
   - 补充（`[答疑]` D2-P37/D2-P38）：α-Al₂O₃ **需要**饱和，γ-Al₂O₃ **应该不需要**饱和。
   - 补充（`[答疑]` D4-P5/D4-P6）：**氧化物氧为表面终端时一般不需要钝化**。
4. 尽量保证表面**对称**；不对称表面加 `IDIPOL` + `LDIPOL` 消偶极。

**文献告诫**：`[讲义]` L1 P56 推荐 **R. Hoffmann, Angew. Chem. Int. Ed., 2013, 52, 93-103**；并提醒"好多计算的文章里截取的表面模型都是有问题的，自然界根本不存在的表面做催化计算"。

**下表面怎么处理**（`[答疑]` D4-P61/D4-P62，一条很实用的组合方案）
- "可以不用太关注下表面的状态…**如果把下表面金属都固定住，且不会引起其他电子结构问题的话，可以不用悬挂键。如果电子结构有问题，比如出现不正常的自旋电荷密度等，可能考虑用啥东西给他饱和一下。**
- **或者还有一种办法，先把 slab 所有原子都优化一次，然后后续算的时候再固定下两层。**"

### 3.2 加真空层

- 目标：**真空层 ≥ 15 Å**（`[算例]` 事实标准 15.0–15.3 Å；见 §0.3）。
- 建模工具做法（异质结/多层）：`build - crystal - rebuild crystal`，把 **c 矢量的长度增大 15 埃**（`[讲义]` L1 P76）。
- **⚠ 不要靠"删掉最上面一层"来造真空** —— 讲义 P76 那句"删掉最上面一层 C₃N₄ 建立真空层"与 P75 的 `Layer 1 用 TiO₂ / Layer 2 用 C₃N₄` 层次顺序矛盾（若 C₃N₄ 是上层，删掉就只剩 TiO₂，构不成异质结）。**该疑点在资料里无解**，`[待核对]`。
- **自查**：`awk 'NR==4{print $3}' POSCAR` 得到 c；把 slab 里最高原子的 z 与最低原子的 z 相减得到跨度；`c − 跨度` 就是真空层厚度。实测锚点：GaN slab 含 H 的 z 跨度 = 14.7324042 Å，`29.7324 − 14.7324042 = 14.9999958 Å` ✓。

### 3.3 固定底层

**方法 A：vaspkit 402（按层数固定）**
```bash
vaspkit
#   402      <- 按原子层数固定
#   1        <- 选择 POSCAR
# 程序先自动判断层数并列出候选阈值：
#   Threshold:  0.3 layers:   5
#   Threshold:  0.6 layers:   5
#   ...
#   Please choose a threshold to separate layers->
#   1.0      <- 输入阈值
#   Found 5 layers
#   2        <- 输入要固定的层数
#   -->> (2) Written POSCAR_fix File!
diff POSCAR POSCAR_fix     # 检查一下
cp POSCAR_fix POSCAR
```
- **限制（讲义明确写出）**：**"此方法只限于法矢量在 z 方向的 slab 模型。"**（`[讲义]` L1 P17/P18）
- `Threshold` 的含义讲义只说了"是 vaspkit 的总层数判断标准，在不同的标准下层数会判断的不太一样"，**没有算法说明**。

**方法 B：vaspkit 403（按 z 坐标一刀切）**
```bash
# 1) 找出要固定的原子中 z 坐标最大的那个，读它的 z 值
# 2) 固定所有 z 小于 (该值 + 余量) 的原子
vaspkit
#   403
#   1
#   0 0.48        <- 若用分数坐标判定
cp POSCAR_fix POSCAR
```
- 与 402 的分工：402 用于"层状清晰、沿 z 分层"的 slab；403 用于"按一个 z 阈值一刀切"的场合，不受层判断阈值影响（`[讲义]` L1 P19）。
- **实测用法锚点**：`day3/ts/dim/POSCAR` 里 O 的分数 z = 0.48812，20 个 Au 的最大分数 z = 0.43488，用 **0.48** 作阈值刚好只放开 O。

**方法 C：手改 `POSCAR`**
```text
第 7 行与第 8 行之间插入一行（只认第一个字母，S 必须大写）：
Selective Dynamics
```
然后在坐标模式行写 `Cartesian`（或 `Direct`），之后**每行坐标尾部加 3 个 T/F**，分别对应 x、y、z（`[讲义]` L1 P16；`[官方]` `references/official/pages/POSCAR.md`）。
- `[官方]` 三条要点：①"只认第一个字符且必须是 `S` 或 `s`"；②"**这些标志指的是**离子的**直接坐标位置，无论位置是以 Cartesian 还是 Direct 模式输入的**"；③"如果 `Selective dynamics` 行被删掉，这些标志会被忽略（内部设为 T）"。
- **实测格式锚点**（`day1/GaN/POSCAR_FIX`）：第 7 行 = `6 6 1`（计数），第 8 行 = `Selective Dynamics`，第 9 行 = `Cartesian` —— 插入位置与讲义完全一致；共 5 个原子标 `F F F`（序号 1、4、7、10、13）。
- **⚠ 固定的是"直接坐标"方向**：`[官方]` 原文 "The flags refer to the positions of the ions in direct coordinates, no matter whether the positions are entered in 'Cartesian' or 'Direct' coordinate modes."（`references/official/pages/POSCAR.md`）

**固定几层**：金属 slab 固定下 2 层（`[讲义]` L2 P61/P136/P141；三个算例一致）；保证**可弛豫层数 ≥ 固定层数**（`[讲义]` L1 P15）；二维材料**不用固定**（`[答疑]` D4-P23/D4-P24）。

### 3.4 赝氢钝化（**键中点 + 固定**）

**什么时候用**：共价晶体/半导体（Si、GaN、InSe、ZnSe）切面后，上下表面最表层原子配位不饱和、有多余 sp³ 轨道没成键、产生表面态；下表面不是研究对象，就用赝氢饱和来还原体相性质（`[讲义]` L1 P58）。
**不用的情况**：金属（`[答疑]` D2-P25/D2-P26）；单层 MoS₂ 切 100 面（`[答疑]` D1-P57/D1-P58）；氧化物氧终端一般不用（`[答疑]` D4-P5/D4-P6）。

**做法（三步）**
1. **在原有化学键的中点位置添加 H**（`[讲义]` L1 P58/P60）。
2. **把 H 固定**（坐标行标 `F F F`）+ 固定下面几层。`[答疑]` D1-P45/D1-P46："赝氢**不用优化**，直接把下面几层固定住就可以了。"
3. **给赝氢单独一个元素槽**，并给它配赝氢赝势。`[算例]` `day1/GaN/POSCAR` 的元素行 = `N  Ga  H`、计数 `6  6  1`。

**几何自查（可精确到 0.001 Å）**
- 取同一 (x,y) 柱内相邻的两个成键原子，算键长 d；
- 被饱和原子在键方向的另一侧 d/2 处 = 赝氢位置；
- 实测锚点（`day1/GaN/POSCAR_FIX`）：Ga–N 键长 = 1.9742314 Å；H 到 N 的距离 = 0.9865210 Å ≈ d/2（0.9871157 Å）；H 的 z = 2.0000985 Å，而键中点 z = 1.9995039 Å → **仅差 0.0006 Å** ✓
- H 那一行是 `F F F`（第 13 个原子）✓

**赝氢赝势的家族**：`H1.25`、`H1.5`、`H.5`（`[讲义]` L1 P25）之外还有 `0.75H`（`[答疑]` D1-P23/D1-P24："这个赝势是 vasp 赝势库里自带的，有很多。价电子数不同，带有 0.75 个电子"）。

**⚠ 用赝氢就不能算表面能**（见 S41）。

### 3.5 超胞、吸附位点

**超胞**
- 异质结：**求最小公倍数**扩包（A 的 a=2 Å、B 的 a=3 Å → A 扩 3 倍、B 扩 2 倍）；夹角不一样先用 `redefine lattice` 转基矢（`[答疑]` D1-P25/D1-P26）。
- 扭转/手性超胞：`[讲义]` L1 P66–P68 给了 (11,1) 扭转石墨烯的完整步骤（导入石墨 → 去对称性 → 去一层 → `redefine lattice`，矩阵 `(11 1 0; −1 10 0; 0 0 1)` → 另导入一层建 **11×11×1** 超胞 → `Build Layers`）。**晶格失配率 4.2%**；若第二步用 **10×10×1** 超胞则 **5.1%**。
- 扭转角脚本（`[讲义]` L1 P69 给的源码）：`python3 magicAngle.py 11 1`。`(m,1)` 族的值：m=5 → 10.89339°、m=10 → 5.208719°、m=15 → 3.417981°、m=45 → 1.114906°、m=50 → 1.002314°、m=105 → 0.474818°。（**⚠ 讲义表里的"魔角"标注位置疑为浮动标注错位**，`[待核对]`：(11,1) 复算得 θ = 4.7145°。）
- **根号表面**：`Au(111)-(√3×√3)R30°` 的变换矩阵是 **A = a − b，B = 2a + b**，即 `(1 −1 0; 2 1 0; 0 0 1)·(a,b,c)`（`[讲义]` L1 P64/P65，矩阵已复算无误）。`c(2×2)` 与 `(√2×√2)R45°` 是同一个东西（`[讲义]` L1 P61）。

**吸附位点**
- **多摆几个可能的构型再优化，取能量最低的**（`[答疑]` D2-P51/D2-P52）。
- 初始距离：**~3 Å**，再优化；优化时物理吸附要加 vdW 校正（`[答疑]` D2-P65/D2-P66）。
- 覆盖度：先算一个 p(1×1) 表面最多能吸附几个分子，再按扩包大小与最终吸附数量相除（`[答疑]` D3-P27/D3-P28）。
- 合金表面（规则排列的金属间化合物，如 NiCo(111)）：在 bulk 模型里从 Ni 出发把部分 Ni 换成 Co，**再切面**（`[答疑]` D1-P51/D1-P52）。
- 团簇/负载型催化剂：`ase.cluster` 模块，或在 MS 里先建较大的 bulk 晶胞、`unbuild crystal` 去掉边界、再手动删原子或用铅笔功能拉形状（`[答疑]` D1-P1/D1-P2）。团簇构型用**全局极小值搜索**（模拟退火、ase、ssw、calypso、uspex），粗糙点就多优化几个构型取能量最低的（`[答疑]` D1-P19/D1-P20）。
- 显式溶剂盒子：把一个水分子替换成目标物种（如 HCO₃⁻）即可；接触原子"多试几个构型，取能量低的"（`[答疑]` D2-P53/D2-P54）。
- 含大分子的表面模型要建得大一些（`[答疑]` D2-P37/D2-P38：Pt₇/TiO₂ 上模拟苯或甲醇"可以，不过对于含有苯这样大分子的表面模型要建立的大一些"）。

### 3.6 二维材料：建模与面内优化

1. 建单层（`[讲义]` L1 P33 给的 MoS₂ 单层 POSCAR：a = (3.1659998894, 0, 0)、b = (−1.5829999447, 2.7418363326, 0)、c = (0, 0, 18.4099998474)；元素行 `S Mo`；计数 `2 1`；`Direct`；分数坐标 0.413899988 / 0.586099982 / 0.500000000）。
2. 加真空（c 方向，总长约 15–18 Å，见 §3.2）。
3. **用 `OPTCELL` 做面内优化**（§2 W10；`100/110/000`）。
4. 吸附/掺杂后：**不要固定任何原子**（`[答疑]` D4-P23/D4-P24）。
5. **不用加赝氢**（单层 MoS₂ 切 100 面，`[答疑]` D1-P57/D1-P58）。
6. **不用偶极校正**（中心对称单层）：`[算例]` OER 全套的 `#LDIPOL = .TRUE.` / `#IDIPOL = 3` 都被注释掉。
7. 面内晶格矢量若需要选择性优化，就 `OPTCELL` 写 `110 / 110 / 000`（讲义/算例里也见过 `100/110/000`；**具体某个方向放不放开要看你的胞的矢量定义**，判据永远是"比较 `POSCAR` 与 `CONTCAR` 的晶格矢量"）。

### 3.7 建模完成前的自查清单（五条）

```bash
# 1) 元素顺序 = POTCAR 顺序（S32）
head -7 POSCAR ; head -1 POTCAR
# 2) 原子数 = POSCAR 计数之和 = INCAR 里 MAGMOM 的个数
grep -E "NIONS|ions" OUTCAR | head -3
# 3) 真空层 ≥ 15 Å
awk 'NR==4{print "c =",$3}' POSCAR
# 4) Selective Dynamics 的位置与 T/F 个数（§3.3）
sed -n '7,12p' POSCAR
# 5) 对称性/偶极：不对称 slab 是否开了 LDIPOL + IDIPOL（§0.14）
grep -E "LDIPOL|IDIPOL" OUTCAR
```

### 3.8 输入文件的句级自查（**上线前跑这一组，专抓"没报错但没生效"**）

> 这一组命令对应 §1.10 的 S59–S65。它们全部是**纯文本检查**，不需要跑 VASP。
> 目的只有一个：在你排队等机时之前，把"写了但程序不读"的行先揪出来。

```bash
INCAR=INCAR

# ① 行内说明用了圆括号且含分号 —— VASP 会把它当语句分隔符（S59）
grep -nE '\([^)]*;[^)]*\)' "$INCAR"

# ② 值里混进了说明文字（从 wiki 抄 INCAR 时丢了 #）（S60）
grep -nE '=\s*[0-9.+-]+\s+[A-Za-z]' "$INCAR"

# ③ 等号后面直接是注释、值写空了（S64）
grep -nE '=\s*(#|!)' "$INCAR"

# ④ 同一关键字出现两次（改值要注释旧行再写新行）（S63）
for t in ENCUT EDIFF EDIFFG ISMEAR SIGMA ISIF IBRION NSW POTIM ISPIN MAGMOM \
         LREAL ISYM NCORE KPAR LDAU LDAUL LDAUU LDAUJ LMAXMIX IVDW NELM NELMDL; do
  n=$(grep -cE "^[[:space:]]*$t[[:space:]]*=" "$INCAR")
  [ "$n" -gt 1 ] && echo "重复 $n 次: $t"
done

# ⑤ 非自洽（ICHARG=11）是否配了 NELM=1（S65）
grep -qE '^\s*ICHARG\s*=\s*11' "$INCAR" && ! grep -qE '^\s*NELM\s*=\s*1\b' "$INCAR" \
  && echo "ICHARG=11 但没设 NELM=1"

# ⑥ 频率计算是否误用了 ISIF=3（S66）
grep -qE '^\s*IBRION\s*=\s*5' "$INCAR" && grep -qE '^\s*ISIF\s*=\s*3' "$INCAR" \
  && echo "IBRION=5 配了 ISIF=3：晶胞会动，Hessian 不是你要的"

# ⑦ POTIM=0 是否配了 IBRION=3（只在 IBRION=3 下合法）（S67）
grep -qE '^\s*POTIM\s*=\s*0(\.0*)?\s*$' "$INCAR" \
  && ! grep -qE '^\s*IBRION\s*=\s*3' "$INCAR" \
  && echo "POTIM=0 但 IBRION 不是 3：离子不会动"
```

**POSCAR / KPOINTS 侧**
```bash
# ⑧ POSCAR 计数之和 vs 元素种类数（供 MAGMOM/LDAU* 用）（S68/S69）
awk 'NR==6{print "元素:",$0} NR==7{s=0;for(i=1;i<=NF;i++)s+=$i;print "原子总数:",s," 种类数:",NF}' POSCAR

# ⑨ 坐标模式行是否存在（S72）
sed -n '8p;9p' POSCAR | grep -qiE '^(s|selective)' && sed -n '9p' POSCAR || sed -n '8p' POSCAR

# ⑩ 真空方向 k 点是否为 1（S70）
awk 'NR==4{print "k 网格:",$0}' KPOINTS

# ⑪ 是否用了 Γ 居中网格（`ISMEAR=-5` 的硬要求）
awk 'NR==3{print "k 中心:",$0}' KPOINTS
```

**若你的算例目录里有 `OUTCAR`**，再加一条最强的检查：**回显里有没有你写的每一个开关**。
`[官方]` `INCAR` 页说明 VASP 会把自己对 `INCAR` 的理解写进 `OUTCAR`；出现即证明程序认了它。
**"有 `OUTCAR` 但回显里没有这个 tag" = 它被静默忽略了**（拼错了，或它属于你没编译进去的插件，如 VASPsol 的 `LSOL`/`LRHOB`）。
```bash
for t in ENCUT EDIFF EDIFFG ISMEAR SIGMA ISIF IBRION NSW POTIM ISPIN LREAL ISYM NCORE LMAXMIX; do
  grep -qE "^[[:space:]]*$t[[:space:]]*=" OUTCAR || echo "OUTCAR 回显里没有: $t"
done
```
（这一组检查的第 ①–⑦ 项与上面"有 `OUTCAR` 但没回显"的分档逻辑，取自本仓库的 `scripts/validate.py`；它的检查项清单可用 `python scripts/validate.py --list-checks` 查看，整目录校验用 `python scripts/validate.py <算例目录>`。**⚠ `validate.py` 的 `OK` 只表示"它检查过的那些项没问题"，不表示"算得对"** —— 见该脚本文件头的分层说明。）

---

## §4 后处理判读经验

### 4.1 d 带中心

- **必须同时报积分窗口**，否则数字不可复现。同一 PDOS、只改上限：讲义 **−3.7502**（窗口 `[-9.39 17.20]`）/ 脚本法上限 20 eV 得 `-3.7501883008710406`；`day2/Ag/D_BAND_CENTER` 给 **−3.7771(Average)**（窗口 `[-9.11 10.04]`）—— 差 **0.027 eV**（`[算例]` + `[讲义]` L2 P92/P93）。
- **窗口的来源**：默认窗口 = `[EMIN − E_F, EMAX − E_F]`（本文件复核：`Ag/DOSCAR` 的 `EMAX=11.00348932`、`EMIN=−8.15061128`、`E_F=0.96133580` → `−9.11` / `10.04` ✓）。
- **上限可以自己定**：设能量上限的理由是"高能的轨道（空轨道）计算误差非常大，且不参与成键"，讲义举例 **10 eV**，脚本法用了 **20 eV**（`[讲义]` L2 P93）。
- **只能比趋势**：工具自带警告 `d-Band Center is Sensitive to the Number of Unoccupied Band. Anyway, the Trends are More Important than the Absolute Energies.`（`[讲义]` L2 P92）。
- **自旋**：`ISPIN=2` 时文件会分 UP / DOWN / Average 三列。判据是看数值是否相等 —— 相等的说明那次是非自旋极化（讲义 P92 的回显 UP=DOWN=Average），不等才是 `ISPIN=2`（算例 −3.7792 / −3.7750 / −3.7771）。
- **别拿 bulk 代替表面**：`[讲义]` L2 P88 自己提醒"我们这里用的 bulk 的模型，算出来和表面体系会有一点差别"。
- **适用边界**：单原子、过渡金属氧化物、单原子 FeN₄ 都能算，但"**规律没有纯金属那么好**"（`[答疑]` D2-P15/P16、P17/P18、P19/P20）。
- **算法本身**：d 轨道的 PDOS 对能量做权重平均；必做的一步是**对 5 个 d 轨道求和**（`[讲义]` L2 P89/P90）。

### 4.2 DOSCAR 列语义（**最常见的读错**）

| 情形 | 每行的列 | 积分值在第几列 |
|---|---|---|
| `ISPIN = 1`（非自旋极化） | 能量 / DOS / **积分 DOS** | **第 3 列** |
| `ISPIN = 2`（自旋极化） | 能量 / DOS(up) / DOS(down) / **积分 DOS(up)** / **积分 DOS(down)** | **第 4、5 列** |

- **答疑稿 D2-P1/D2-P2 的答复"看第三列的数值是积分值"只在 `ISPIN=1` 时成立**（学员问"为什么 `DOSCAR` 算出来的电子数量是 0.68 不到 1"）。对自旋极化体系会把积分值读错列。
- **实测核对**：`things to study/al2o3`（`ISPIN=1`）每行 **3** 个数值；`day2/Ag`（`ISPIN=2`）每行 **5** 个数值（如 `-8.151 0.0000E+00 0.0000E+00 0.0000E+00 0.0000E+00`）。
- **官方依据**：VASP Wiki `DOSCAR` 页给出了两种列的排列（外链 `https://vasp.at/wiki/index.php/DOSCAR`）。**本仓库未镜像该页**，所以这一条的 `[官方]` 只能给外链，不能给本地文件路径。
- **讲义本身的缺口**：L2 P43 只说"积分的 DOS 可以用来判断电子占据的具体数值"，**没有讲列位置**。
- **操作**：拿不准就数一行有几个数 —— 3 个 → `ISPIN=1`；5 个 → `ISPIN=2`。
  ```bash
  awk 'NR==7{print NF}' DOSCAR     # 第 7 行是第一个数据行（第 6 行是 NEDOS EMAX EMIN E_F 那行）
  ```

### 4.3 PDOS / LORBIT 的读法边界

- **PDOS 的和 < 总 DOS**，且**不能**用它积分为"某个原子轨道的占据数"。`[讲义]` L2 P48 的英文解释："To obtain PDOS, a projection on spherical harmonics is done. In this procedure, you lose part of the information. So, the sum of the parts is lower than the whole DOS…"；P49 更直接："PDOS 的加和不重合总 DOS。所以对 PDOS 的占据轨道积分不能讨论某个原子轨道的占据数。"
  - **⚠ 归因在讲义里前后不一致**：L2 P24 归给"区域根据原子半径（`RWIGS`）划分"，L2 P48 归给"球谐投影丢信息"。`[官方]` 说位点投影 DOS 由 `RWIGS` **或** `LORBIT` 决定（`references/official/pages/LORBIT.md`）。三处不互相排斥，但**不要把它当成一个精确的归一化关系用**。
- **`LORBIT` 的分工**：`10` 只区分 s/p/d/f 角量子数；`11` 再做 lm 分解（`[讲义]` L2 P36）。`[官方]` 的更准确说法是 `LORBIT=11` 写 **lm-decomposed** `PROCAR`（`references/official/pages/LORBIT.md`）；讲义用"磁量子数"指代是**不精确**的（严格说这里是轨道磁量子数 m_l，与自旋磁量子数无关）。
- **`LORBIT>=10` 时 `RWIGS` 被忽略**；`LORBIT<10` 时才需要 `RWIGS`（`references/official/pages/LORBIT.md`）。
- **`LORBIT` 附带的 `total charge` 不能定量**（`[讲义]` L2 P50；见 S40/S27）。
- **`LORBIT` 可以后加**：`[官方]` 提示这是后处理步骤，可在重启时改 —— 设 `ALGO=None` 加上想要的 `LORBIT`，从 `WAVECAR` 重启（`references/official/pages/LORBIT.md`）。
- **`LORBIT=12/13` 不要用于定量**；`LORBIT=14` 是 vasp.6 起改进的方案（`references/official/pages/LORBIT.md`）。
- **DOSCAR 是不是弛豫算出来的**：见 S34。判据 `grep -c "E-fermi" OUTCAR`。

### 4.4 电荷分析方法的可信度排序与适用场景

**按"能不能定量"排（本文件给出的排序，依据 `[讲义]` L2 P50 与 `[官方]` `LORBIT.md`）**：

| 档次 | 方法 | 怎么得到 | 能用来说什么 |
|---|---|---|---|
| **可定量** | **Bader charge** | `LAECHG=.TRUE.` → `chgsum.pl AECCAR0 AECCAR2` → `bader CHGCAR -ref CHGCAR_sum` | 原子净电荷、电荷转移量 |
| 可定量 | DDEC、NPA | 讲义列为"分析原子电荷方法很多"里的选项，**具体工具链讲义未给** | 同上（`[待核对]` 流程） |
| 可定量 | Löwdin、Mulliken | 用 **lobster** 分析得到 | 同上（`[待核对]` 流程） |
| **不能定量、只能定性** | `LORBIT` 的 `total charge`（`OUTCAR` 末尾） | 自动输出 | "一般无视就行了" |
| **不能定量、只能定性** | `OUTCAR` 末尾的原子电荷与磁矩 | 自动输出 | "根据每个原子的半径内电荷计算出的，**仅供参考**"（`[讲义]` L1 P47） |
| **不能定量** | PDOS 的积分值当占据数 | `vaspkit 113/115` 等 | 明确禁止（`[讲义]` L2 P49） |

**电荷转移量的量级锚点（帮你判断自己的数是否离谱）**
- Fe₃ 活性中心"low charge state (**0.59 |e|**)"（`[讲义]` L2 P31）；
- N₂ 吸附后"Bader 电荷从 0 降低到 **−1.13 |e|**"（`[讲义]` L2 P77）。

**差分电荷可信度的前提**：片段单点**必须收敛**（`[答疑]` D2-P24）；三个片段**设置完全一致**；结构**直接截取、不再优化**（`[讲义]` L2 P103）。三条缺一，图就是废的。

**电子流向的判据顺序**：静电势/功函数 → 电荷差分 → Bader 电荷。**不要用 HOMO/LUMO**（`[答疑]` D3-P37/D3-P38）。

### 4.5 频率 → ZPE / 熵 / 自由能的对应关系

| 量 | 关系 | 实操取法 | 来源 |
|---|---|---|---|
| 频率 | `1 f = 12.609563 THz  79.228223 2PiTHz  420.609746 cm-1  52.148981 meV` | 一般用 cm⁻¹；**最后一个 `meV` 是 hν** | `[讲义]` L3 P32 |
| ZPE | `ZPE = ½ Σ hν` | "**求 zpe 可以直接读这个能量除以 2**"；**虚频不计入**（见 S15） | `[讲义]` L3 P32/P61；`[待核对]`（"虚频不计入"为本文件推断） |
| `U(T) = H(T)` | `ZPE + ΔU(0→T)` | vaspkit 501 直接给 | `[讲义]` L3 P64 的输出块 |
| `G(T)` | `H(T) − T·S = ZPE + ΔU(0→T) − T·S` | vaspkit 501 的 `Thermal correction to G(T)` | 同上 |
| 熵的柱 | 讲义同页给 `Entropy S : 14.459 J/(mol*K)  0.000150 eV`；**第二个数其实是"每 K 的熵"**（14.459/96485 ≈ 1.499E-4 eV/K） | 不要把它当 TS；TS = ΔH − ΔG = 0.094915 − 0.050237 = 0.044678 eV | `[讲义]` L3 P64 + 本文件核算 `[待核对]` |
| 频率与 ZPE 的关系 | 频率越大对 ZPE 贡献越大（H₂ 伸缩 4395 cm⁻¹ → H₂ 参与的反应 ZPE 校正非常大） | — | `[讲义]` L3 P53 |
| 频率与熵的关系 | 频率越小对 ZPE 贡献越小，但对 q_vib 贡献越大、对升温造成的熵增贡献越大 | 所以低频要截断（50 cm⁻¹） | `[讲义]` L3 P54/P55 |
| 表面吸附分子的自由度处理 | "难以计算平动能和转动能，所以可以近似的认为分子平动转动的贡献耦合到了这 6 个振动中，故可以按照 3N 计算分子的振动能量" | 所以表面体系用 3N，不是 3N−6 | `[讲义]` L3 P24 |
| 自由能的温度效应量级 | 298.15 K 下 O 原子迁移的自由能对能垒影响只有 ~0.01 eV；800 K 下有 ~0.05 eV 的差别 | 低温算能垒可以不加校正，高温必须加 | `[讲义]` L3 P65/P66 |
| vaspkit 输出 vs 手工算 | 实测锚点：`7-4-Au-O-freq/ts/OUTCAR` 给出 `ZPE = 0.065715 eV`（1.515 kcal/mol）；`ΔH = 0.094915 eV`；`ΔG = 0.050237 eV` | 与讲义 P65 的 298.15 K 表**对不上**（ZPE 0.065715 vs 0.0672；ΔH 0.094915 vs 0.0285）—— **不确定这两页是否来自同一次计算**，用你自己体系的输出为准 | `[讲义]` L3 P64 vs P65；差异见 `learn_L3.md` §4 C-4 `[待核对]` |

### 4.5b ⭐ `SIGMA` 与 `NEDOS` 的三个**可执行自检**（都零额外机时）

> 这三条来自 `[官方]` `references/official/pages/Smearing_technique.md`
> 与 `[LVTHW]` `EX01`/`EX37`。它们的好处是：**数字已经在你的输出里，不用重算。**

| 自检 | 怎么做 | 判据 | 来源 |
|---|---|---|---|
| **金属的 `SIGMA` 够不够** | `grep "entropy T" OUTCAR` 取 `entropy T*S`，**除以原子数** | **< 1 meV/atom** | `[官方]` Smearing technique 页（原文：`the entropy term should be less than 1 meV per atom`）；`[LVTHW]` `EX01:167-179` |
| **DOS 的 `NEDOS` 够不够** | 看 `DOSCAR` 表头的 `NEDOS` | 经验值 **≈ 3000**（配合足够密的 k 点） | `[LVTHW]` `EX37:53`（`[经验]`） |
| **k 点密度够不够** | `K × a ≈ 45`（`K` = 各方向 k 点数，`a` = 对应晶格常数 Å） | 经验起手式 | `[LVTHW]` `EX37:45`（`[经验]`；⚠️ 同篇还提到 `k·a ≈ 30` 的出处是 **GPAW 教程**，**不是 VASP 官方** ⇒ 别当官方判据） |

**为什么"熵项 < 1 meV/atom"这条特别有用**：
它是**官方给出的、对金属 `SIGMA` 的定量判据**，
比"把 `SIGMA` 减半看能量差变多少"**省一整套计算**
—— 因为 `entropy T*S` 那一行**每次 SCF 都会打出来**。

> ⚠️ **一个容易搞错的读法**：`OUTCAR` 里那行原文形如
> `  entropy T*S    EENTRO =        -0.00633891`
> （`[实测]`：`day2/Ag/OUTCAR` 里出现 27 次、`day1/fe2o3/OUTCAR` 里 77 次
> —— 即**每个离子步都会打**，所以这个自检是零成本的）。
> 注意 `T*S` 已经**含温度**（它就是 `TS`），**不要再乘温度**，
> 除以原子数后与 1 meV 比。
>
> ⚠️ **单位没有在本项目里被独立验证过**：官方那页只写了
> "the entropy term should be less than 1 meV per atom"，
> **没写读哪一列、什么单位**。本项目按"它是 eV"理解
> （`day2/Ag` 末值 `−0.00633891` ÷ 16 原子 ≈ **0.40 meV/atom**；
> `day1/fe2o3` 末值 `−0.00000000`）。**量级自洽**，但这条判据的
> **具体口径标 `[待核对]`** —— 用之前先确认量级合理
> （`SIGMA` 减半时它应当近似减半）。
>
> **证据**：`[官方]` `pages/Smearing_technique.md:81`；
> `[LVTHW]` `EX01:167-179`、`EX37:45/53`；`[实测]` 上述两个 `OUTCAR`。

### 4.6 几个"看着像结果其实不是结果"的量

| 量 | 为什么不能直接用 | 该用什么 |
|---|---|---|
| `OUTCAR` 末尾的原子电荷/磁矩 | 半径球内布居，仅供参考（`[讲义]` L1 P47） | Bader / 自旋密度（`CHGCAR` 或 `vaspkit 312`） |
| `LORBIT` 的 `total charge` | 定性（`[讲义]` L2 P50） | Bader |
| `DIMCAR` 的 `Energy` 列 | 不是电子熵外推到 0 的能量（`[讲义]` L3 P151） | `OSZICAR` 最后一个 `E0` |
| `neb.dat` 的相对能量列（image 1） | 与同算例 `OSZICAR` 差 3.8 meV，与讲义也差（`[算例]`） | `OSZICAR` 的 `E0` |
| `neb.dat` 距离列 | 反映的是**弛豫后**的实际构型，不是插值距离（末段 24.8 Å vs 前四段 ~5.30 Å） | 只用来画剖面形状 |
| `mep.eps` 里拟合出的极值点 | "拟合出来的极值点不一定是真实存在的"（`[讲义]` L3 P162） | `nebef.pl` 的能量最高 image + 频率验证 |
| `SYSTEM` 名 / `DOSCAR` 头的体系名 | 常是模板残留（`Ag` 写 `GDY`、`ni-co` 写 `Fe`、`c` 写 `Au`） | `POSCAR` 元素行 + 计数；`LOG` 的 `POSCAR found` |
| `EMAX`/`EMIN` 的 `OUTCAR` 回显 | 是哨兵写法，不是你的设置 | 看你的 `INCAR` 有没有写；一般留默认 |
| `d 带中心` 的单个数字 | 依赖积分窗口 | 数字 + 窗口 + 自旋 + 来源，四件一起报 |

---

## §4b 诊断时的**反模式**（怎么把对的证据推成错的结论）

> **这一节的定位**：前面各节讲"**知识**"，这一节讲"**行为**"。
> 它的来源不是教材，而是**真实的失败过程**：一位使用者（有经验的算力用户）
> 花了几小时诊断一个"作业第一次 SCF 就崩"的问题，
> **中途得出了至少四个错误结论**，最后自己发现了正确的那一个。
>
> ⇒ **知识会过时，反模式不会。** 换代码、换体系、换集群，
> 下面每一条都会**以新的面孔**再出现一次。
>
> ⚠️ **本节不讲"你该知道什么"，讲"你怎么会想错"。**
> 每条都配一个**可执行的自查动作** —— 不然它只是道德说教。

### AM-1 · 把"我测到的"当成"体系固有的"

**症状**：测出一个"资源需求量"（栈/内存/耗时），就拿它去支撑
"必须改系统/改配置"的结论。

**为什么错**：**那些测量是在某一个并行配置下做的。**
例：在一个 `NCORE=1`（最恶劣）的配置下测出"这个体系要 >32 MB 栈"，
然后断言"体系需要 32 MB" —— 而**换一个并行分解，需求就掉下来了**。

> ✅ **自查**：报任何资源数字时，**必须同时报"在什么并行配置下测的"**。
> **不带并行配置的资源数字没有意义。**
> `grep -E "running on|distrk:|distr:" LOG` 就是那个配置。

### AM-2 · 把"某个取值没救回来"当成"该变量无关"

**症状**：单变量对照里试了一两个取值，都失败，于是写"**与 X 无关**"。

**为什么错**：`NCORE=4` 不行，**只说明"4 这个取值不行"**，
**推不出"并行分解这个维度无关"**。而正确的那一档（`NPAR=2`）
可能就在你没试的地方。

> ✅ **自查**：措辞必须是「**在该取值下无效**」，
> **不是**「**与该变量无关**」。
> 下"无关"结论前，至少要覆盖该参数的一个**"应该明显不同"的档位**
> （例如从"每 rank 一个 band"换到"多 rank 一个 band"）。

### AM-3 · 把"我改不了"当成"客观不可解"

**症状**：验证了 `sudo` 不可用 / 配置读不到，就下结论"这是站点级问题、
要找管理员"。

**为什么错**：**"我权限不够"与"这个问题只能靠权限解决"是两件事。**

> ✅ **自查（给出"需要外部介入"之前，强制执行这个顺序）**：
>
> | 层 | 问什么 |
> |---|---|
> | ① 输入文件层 | 有没有**该改没改**的参数？ |
> | ② 程序层 | 有没有别的二进制 / 算法选项？ |
> | ③ **并行层** | **`NCORE`/`NPAR`/`KPAR`/核数**？ |
> | ④ 环境层 | 环境变量、库、模块？ |
> | ⑤ 才轮到 | 系统 / 队列配置 |
>
> **并且先问一句**：「**如果我不能改系统，有没有办法让它在这个限制下跑起来？**」

### AM-4 · 忽略了**程序自己给出的提示**

**症状**：程序在输出里**明确建议了**一个参数，而它被归类成"性能建议"跳过。

**实例**：VASP 在启动横幅里自己打印

```
|     For optimal performance we recommend to set          |
|       NCORE = 4 - approx SQRT(number of cores).          |
```

而那个参数（`NCORE`）**正是能让作业跑起来的旋钮**。

> ✅ **自查**：把下面这几行登记为**必须读的诊断信号**（不是"性能提示"）：
> - `NCORE = 4 - approx SQRT(number of cores)`（VASP 自己给的并行建议）
> - `running on N total cores`
> - `distrk: each k-point on ... groups`
> - **`distr: one band on N cores, M groups`** ← 决定"每 rank 干多少活"
>
> 一般化：**程序主动建议的参数，优先于我自己想出来的假设。**

### AM-5 · 红鲱鱼（把"总是出现的一行"当成根因证据）

**症状**：日志里有 `ulimit: stack size: cannot modify limit`，
就认定"栈不够"。

**为什么错**：当队列的栈硬限由调度器设死时，
作业脚本里的 `ulimit -s unlimited` **必然**失败并打印这行 ——
**在成功的作业里也会出现**。它只是"这个队列不允许改栈"的**事实陈述**。

> ✅ **自查**：在把某行日志当证据之前，先问
> 「**这行在成功的运行里会不会也出现？**」

### AM-6 · 修完"参数交互"类问题，**立刻又制造一个同类问题**

**症状**：诊断出"`NPAR`/`NCORE` 的取值能决定作业生死"之后，
在同一次修复里**同时写下了 `NPAR = 2` 和"建议 `NCORE = 8`"** ——
而官方明文禁止两者并存（`NPAR` 优先，`NCORE` 被静默忽略）。

> ✅ **自查**：修"参数取值/交互"类问题时，收尾**必须**做一次
> **该参数的语义与互斥检查**：
> ① 有没有**别名 / 逆参数**？② 能不能**同时出现**？③ 同时出现时**谁优先**？
>
> **不要只把"能让它跑起来的那个值"填进去。**
> 工具侧已机器化：`validate.py` 的 `XPAR.both_set`。

### AM-7 · 把"知识库怎么写"当成"计算怎么做"（**本项目自己的反模式**）

**症状**：一条**文档维护规矩**（"本文的指针一律按主题名给"、
"机器细节一律不写"）被当成**计算建议**去审、去改。

**为什么错**：它的**宾语是文档，不是 `INCAR`**。问它"适用条件是什么"
是**问错了问题** —— 该问的是"这条规矩的前提现在还成立吗 / 边界划清了吗"。
（本项目就有实例：一条"本文的指针一律……"的规矩，
其前提**已被它自己的下一句推翻** —— `decide.md`/`playbook.md` 早已落盘带 § 号。）

> ✅ **自查**：下结论前先问「**这句话的宾语是"本文件"还是"我的计算"？**」

### AM-8 · 把"真的发现"当成"该报红"（**本项目自己的反模式**）

**症状**：一条检查命中了 47% 的算例，而且**逐条核对都是真的** ——
于是保留成 `WARNING`。

**为什么错**：**"是不是真的"与"该不该报红"是两个问题。**
一条**真**的发现，如果命中率高达 47%，它当 WARNING 就是**噪声**，
**会把人训练成忽略整个报告**。

> ✅ **自查**：新增任何会报红的检查前，**先量命中率**。
> 如果它**不影响正确性**（能跑完、算得对），就降为 `INFO`
> （"仅供参考"），并在说明里写清**为什么不升级**。
>
> 本项目已三次应用这条规矩：真空层检查误报 76/98（`CR-009`）、
> `par_tags` 误报 15%（`CR-041`）、`NCORE` 除不尽命中 47%（`CR-044`）。

### AM-9 · 用一个"意图"去校验一批"事实"（**本项目自己的反模式**）

**症状**：用户给了 `--ncores 16`，就拿 16 去校验一批
**实际跑在 40/64 核上**的算例 ⇒ 命中 60%，全是噪声。

**为什么错**：**用户给的参数是"意图"，输出里的是"事实"。**
两者都在时，**用事实**。

> ✅ **自查**：工具里凡是"用户告诉我的"与"文件里读到的"冲突，
> **一律以文件里读到的一手事实为准**，并把来源标出来。

### AM-10 · "分支没触发"与"分支正确"长得一模一样

**症状**：新增一条带条件分支的检查，测试通过、输出正常 ⇒ 以为没问题。
实际是**另一个分支永远走不到**（变量从没被赋值）。

**为什么错**：不触发的分支**不产生任何可观察的差异**。

> ✅ **自查**：新增带分支的检查时，**每个分支都要造一个样本**。
> 只有小体系算例通过，**证明不了**大体系那条路是通的。

---

## §5 报错原文速查
> **用法**：拿到输出后直接 grep 左列的原文；命中后按"怎么办"操作；带 `→ S<n>` 的到 §1 看完整四要素。
> **本表的边界**：只列**在现有资料里读到过原文**的串。凡本文件没有原文的报错（见 §1.9 的检索清单）**一律不列**，不猜含义。

| 报错 / 输出原文 | 出处 | 含义 | 怎么办 |
|---|---|---|---|
| `VERY BAD NEWS! internal error in subroutine IBZKPT: Tetrahedron method fails for NKPT<4. NKPT = 1` | `[讲义]` L2 P46（原文见 `references/raw/L2.txt` 第 580 行） | `ISMEAR=-5`（Blöchl 修正四面体法）在不可约 k 点 < 4 时无法构造四面体 | 把 `ISMEAR` 改成 **0** 或 **1**；配 `SIGMA = 0.05`（非金属）。`-5` 时程序**不读 `SIGMA`**。**必须用 Γ 居中网格**（`[官方]` `references/official/pages/ISMEAR.md`）。→ **S48** |
| `For charged systems, the potential correction is currently only implemented for cubic supercells. VASP will stop if the supercell is not cubic and LDIPOL is used.` | `[官方]` `references/official/pages/LDIPOL.md` | 带电体系 + 非立方超胞 + `LDIPOL=.TRUE.` → 程序停 | 三选一：① 做成立方超胞；② 关 `LDIPOL` 改用中和背景电荷；③ 用抗衡离子代替改总电荷（`[答疑]` D1-P12 / D3-P45/D3-P46）。**另：不要同时设 `LMONO`（会抑制偶极修正输出）**。→ **S49** |
| `WARNING: mass on POTCAR and INCAR are incompatible.` | `[官方]` `references/official/pages/POMASS.md` | `INCAR` 里的 `POMASS` 与 `POTCAR` 的质量不一致 | 删掉 `INCAR` 里的 `POMASS`（用 `POTCAR` 自带质量），或改成与 `POTCAR` 一致的值。`POMASS` 一般只在做同位素/特殊质量时才写 |
| `reached required accuracy - stopping structural energy minimisation` | `[算例]` `day1/fe2o3/OUTCAR`（与 `[讲义]` L1 P30 给的串逐字一致） | **离子步收敛**的判据串 | 这是**你要找的**成功信号。`grep reached OUTCAR` 命中它 = 结构优化收敛。→ **S50** |
| `------------------------ aborting loop because EDIFF is reached ------------------------` | `[算例]` `day1/fe2o3/OUTCAR`（9 次，对应 9 个离子步） | **每个离子步内部的 SCF 收敛**（≠ 离子步收敛） | 不要把它当结构优化收敛的证据。数一数它出现了几次 = 跑过的离子步数。两种串的区别见 **S50** |
| `OPT: skip step - force has converged` | `[讲义]` L3 P153 | **Dimer 收敛**的判据串 | 配合 `grep RMS OUTCAR`（最大原子受力 < \|EDIFFG\|）与 `tail -1 OSZICAR`（取 `E0`）三条一起确认。→ **S21** |
| `using selective dynamics as specified on POSCAR` / `Analysis of constrained symmetry for selective dynamics` | `[算例]` `.../oer/{o,oh,ooh}/freq/OUTCAR` | `IBRION=5` 的有限差分**遵守选择性动力学、只位移标 T 的原子** | 这是**成功信号**：说明"只算吸附物振动"生效了。要核对自由度数看 `DYNMAT` 第一行（= 元素种类数 / 总原子数 / 被位移的自由度数）。→ §2 W6.1 |
| `Finite differences progress:` 下的 `Degree of freedom:   1/  3` | `[讲义]` L3 P31；`[算例]` `7-4-Au-O-freq/{ts,o2}/OUTCAR` | 分母**不是**整个体系的 3N，而是 **3 ×（放开的原子数）** | 按"实际离子步数 = 3 × 放开原子数 × `NFREE` + 1"核对。→ **S10** |
| `EMIN = 10.00; EMAX =-10.00  energy-range for DOS` | `[算例]` `day2/{Ag,ni-co,al2o3}/OUTCAR` | VASP 自身在 DOS 能量范围输出里的**哨兵/默认写法**，并非"EMIN > EMAX"的错误 | **留默认，不要手填 `EMAX`/`EMIN`**；它们只影响作图效果。→ **S37** |
| `Vacuum-Level (eV): 6.673` + `Check the Convergence of Vacuum-Level Versus Vacuum Thickness!` | `[讲义]` L2 P137（vaspkit 功函数流程回显） | vaspkit 自动判断了真空能级位置；**并主动提醒你要检查真空能级对真空层厚度的收敛** | 按 W1.3 扫 c；真空区必须出现水平平台。→ **S30** |
| `d-Band Center is Sensitive to the Number of Unoccupied Band. Anyway, the Trends are More Important than the Absolute Energies.` | `[讲义]` L2 P92（vaspkit 503 自带的 Warm Tips） | d 带中心绝对值不稳，依赖积分窗口与空带数目 | 报数字时**同时报积分窗口 + 自旋 + 来源**；只比趋势。→ **S35** |
| `frequencies less than 50 cm-1 are set to 50 cm-1.` / `Neglect PV contribution to translation for adsorbed molecules.` | `[讲义]` L3 P64（vaspkit 501 输出） | vaspkit 已经**自动**做了低频截断与平动 PV 项忽略 | 这是**成功信号**。注意该处理**只适用于表面吸附分子**，不要套到气相分子。→ §2 W6.3 |
| `If one is searching for a spin polarised (ferro- or antiferromagnetic) solution, it is usually safest to start from larger local magnetic moments` | `[讲义]` L1 P45（引 VASP 手册原话） | 找自旋极化解时的取向建议 | 初猜磁矩**可以尽量设大**（比如 5.0），程序会自动优化到合理的磁矩。→ **S25** |
| `running on   64 total cores` / `each k-point on  N cores,  M groups` / `one band on NCORES_PER_BAND=  X cores,  Y groups` | `[算例]` `day1/{fe2o3,mos2}/LOG` | 并行划分的实际生效情况 | 用来反推 `KPAR`/`NCORE` 是否真的生效：`总核数 = KPAR × NCORE × 能带组数`（本文件归纳 `[待核对]`）。这两行**也含站点/核数信息**，写进论文或仓库时要剔除。→ §0.13 |
| `POSCAR found type information on POSCAR  S  Mo` / `POSCAR found :  2 types and  3 ions` | `[算例]` `day1/mos2/LOG` | VASP 从 POSCAR 第 6 行读元素名并要求 `POTCAR` 顺序匹配 | 用这两行**核对元素顺序**，而不是看 `SYSTEM`。→ **S32 / S52** |
| `LDA+U is selected, type is set to LDAUTYPE =  2` + `angular momentum for each species LDAUL = ...` + `U (eV) for each species LDAUU = ...` + `LMAXMIX = 4 max onsite mixed and CHGCAR` | `[算例]` `day1/fe2o3/OUTCAR` | DFT+U 参数的实际生效回显 | 用这段**逐项核对**你的 `LDAUL/LDAUU/LDAUJ/LMAXMIX` 是否与 `POSCAR` 元素顺序匹配。f 电子要把 `LMAXMIX` 提到 6。→ §0.12 / **S32** |
| `LUSE_VDW = T` / `LASPH = T` / `LEXCH =  44` | `[算例]` `day1/vdw-df2/OUTCAR` | 非局域 vdW-DF 是否真正生效（`LEXCH=44` 对应 `GGA = ML`；PBE 是 `LEXCH = 8`） | 用 `grep -E "LUSE_VDW|LEXCH" OUTCAR` 确认泛函/vdW 设置生效。**⚠ `LEXCH=44` ↔ `GGA=ML` 的对应关系本文件未在权威文档核实** `[待核对]`。→ §0.11 |
| `E-fermi : 5.4353  XC(G=0): -11.0891  alpha+bet :-15.2081` | `[算例]` `day2/al2o3/OUTCAR` | 费米能级 + 两个只由结构与赝势决定的量 | **`XC(G=0)` 与 `alpha+bet` 相同 = 同一体系同一赝势**；`E-fermi` 会在同结构不同次计算间漂移 ~0.01 eV → 跨计算比较前必须 shift/对齐。→ **S39** |
| `SOL:` 行（`OSZICAR` 里） | `[算例]` `.../vaspsol-H2O/vaspsol/OSZICAR` | VASPsol 溶剂模型已生效 | 这是**成功信号**。**但该行四个数字各列的含义、以及第一项（−0.4408 eV）为什么与总能差（−0.3128 eV）不等，本文件没有依据** `[待核对]`。→ **S46** |
| `OK, ALL SETUP HERE` / `FOR LATER ANALYSIS, PUT OUTCARs IN FOLDERS 00 and 02 !!!` | `[讲义]` L3 P126 | `nebmake.pl` 插点成功 | 自动生成 `./00 ./01 ./02`；00 = IS，02 = FS，文件名都是 `POSCAR`。→ §2 W7.2 |
| `filetype1: vasp5` / `filetype2: vasp5` | `[讲义]` L3 P126（`nebmake.pl` 回显） | 两个端点文件被识别为 VASP5 格式 | 若是 `vasp4` 说明缺元素名行，**先补元素行再插点**（VASP4 格式没有物种名行，会让后续步骤错位） |
| `Extremum 1 found at image 0.998685 with energy: 0.494221` | `[讲义]` L3 P134（`nebresults.pl` 输出） | spline 拟合出的极值点位置与能量 | **拟合出的极值点不一定是真实存在的**，需要自己判断并做频率验证；一般只关注能量最高的 image（用 `nebef.pl`）。→ §2 W7.7 |
| `Unziping the OUTCARs ... done` / `Do nebbarrier.pl ; nebspline.pl` | `[讲义]` L3 P134 | `nebresults.pl` 在解压并依次调用子脚本 | 不想被压缩：`gunzip 0*/OUTCAR.gz`。→ §2 W7.7 |
| DIMCAR 的表头 `Step  Force  Torque  Energy  Curvature  Angle` | `[讲义]` L3 P149/P150 | Dimer 的六列诊断量 | 关键看 Force / Torque / Curvature 三列；**Curvature 为负才是接近过渡态**。→ **S21** / §2 W8.4 |
| `MODECAR` 文件里出现逐行 ~1E-14 量级的数、**最后一行是主分量** | `[讲义]` L3 P145 | 生成的 `MODECAR` 形态正常 | 主分量应在**要位移的那个原子**对应的行上。→ §2 W8.2 |
| `NEWMODECAR` | `[讲义]` L3 P145 | 每个 Dimer 旋转步都会更新的新方向 | 用 `dimmode.pl CENTCAR NEWMODECAR 32 0.5` 生成 `dimmode.xyz` 看动画（**该脚本要求 CENTCAR 第一行是元素组成**）。→ §2 W8.6 |
| 21 行连续的 `NaN NaN NaN`（出现在 `POSCAR` 尾部） | `[算例]` `day3/ts/dim/POSCAR` 第 32–52 行 | 转换工具产生的残留（行数恰等于原子数，疑似速度/预测块被写成 NaN） | **入库/提交前清理掉这些多余行**。VASP 对 POSCAR 多余行的容忍度本文件未验证 `[待核对]`。→ §3.7 自查清单 |
| `Timing`/`LOOP:` 类计时块 | — | — | **本文件不给**（避免涉及具体机器性能信息） |

**报错排查的通用顺序（本文件给出的操作序，不是资料原文）**：
1. `tail -60 OUTCAR` / `tail -30 stdout` 看最后停在哪个阶段（读入？SCF？离子步？后处理？）；
2. `grep -E "aborting loop|reached required|VERY BAD|WARNING|Error|error" OUTCAR | tail -20`；
3. 核对 `OUTCAR` 头部的参数回显与你的 `INCAR` 是否一致（`ENCUT`/`ISMEAR`/`SIGMA`/`ISYM`/`LREAL`/`NELMDL`/`ISPIN`/`MAGMOM`）；
4. 核对元素顺序（`POSCAR found type information` vs `head -7 POSCAR`）；
5. 到本表与 §1 查对应的 `S<n>`。

---

## 附录 A · 本文件的引用权威序与裁定记录

按 `_WRITING_CONTRACT.md` §8 的权威序：`[官方]` > `[算例]` > `[讲义]` > `[答疑]` > `[经验]`。
本文件遇到的多处冲突，**裁定结果与依据**记录如下（不默默选一个）：

| 位置 | A 怎么说 | B 怎么说 | 本文件的裁定 | 依据 |
|---|---|---|---|---|
| `EDIFF` 结构优化取值 | `[讲义]` L1 P28：1E-5 | `[算例]` 4/4 写 1E-6（GaN 1E-8）；讲师 3 个模板也都写 1E-6 | **默认用 1E-6** | `[官方]` `EDIFF` 页明确"1E-6 很可能是最佳折中"；算例与模板一致 |
| `NELM` | `[官方]` 默认 60，"40 步不收敛就基本不会收敛" | `[讲义]` L1 P28：300 或以上 | **写 300（给观察余量），但按官方口径排查而非加步数** | `[官方]` 优先；加步数不解决根因 |
| `LREAL` | `[讲义]` L1 P28："表面计算 Auto" | `[算例]` 3 个 slab/2D 算例全用 `.FALSE.` | **默认 `.FALSE.`；原子数 > 30 再上 `Auto`** | `[官方]` `LREAL` 页推荐"原子数 > ~30 用实空间"；讲义缺"体系大小"前提 |
| `ISYM` | `[答疑]` D4-P22："需要设置 `ISYM = 0`" | `[算例]` 随课 OER 实际跑在 `ISYM = 2` | **两者都保留，按目的二选一**（复现随课数值用 2；按讲师建议用 0）；MD 一定用 0 | `[官方]` `ISYM` 页只说 MD 该设 0；冲突不可裁定，故给出"按目的选"的可执行规则 |
| `NCORE` | `[讲义]` P48："每节点核数/2" | `[讲义]` 模板写 5；`[算例]` 写 16 | **按 `[官方]` 的规则：`≈√(可用核数)` 或每节点核数的因子；**做一次扫描** | `[官方]` `NCORE` 页给的三个区制 + "正式计算前应做 `NCORE` 扫描" |
| `POTIM` | `[答疑]` D1-P38："默认 0.5 就可以" | `[讲义]`/`[算例]` 结构优化一律 0.2 | **结构优化用 0.2；`IBRION=5` 用 0.015；过渡态用 0** | 两者不矛盾（答疑在说"可以不动"），但实操值 6/6 是 0.2 |
| `ENCUT` | `[讲义]` L1 P28："= ENMAX" | `[算例]` 晶胞优化用 1.3×ENMAX | **晶胞优化 > 1.3×ENMAX；常规 ≥ ENMAX；一律显式写死** | `[官方]` "必须检查收敛 + 强烈建议手动写死"；`[算例]` `day1/fe2o3` 定量验证 1.30 |
| `ISMEAR=-5` 的适用 | `[讲义]` L2 P36：DOS 首选 −5 | `[算例]` 6 个 day2 DOS 步里只有 1 个用 −5 | **按 `[讲义]` 的规则走（能用的场合就用 −5），但把它当"更准"而不是"必须"** | `[官方]` 只规定"四面体法要用 Γ 居中网格"与 NKPT 约束；算例的偏差属"INCAR 复用"而非反例 |
| `VASPsol` 四个溶剂参数 | `[讲义]` L4 P54 列出 78.4/0.6/0.0025/0.000525 | `[算例]` 一个都没写 | **写成"不写就是这组默认值（标 `[待核对]`）；换溶剂必须显式写 `EB_K`"** | 算例能跑出 `SOL:` 行说明默认生效；但本文件未读源码，故不下断言 |
| `SHE` 绝对电位 | `[讲义]` L4 P41：**4.44 V** | 配套 PDF：**4.6 V** | **报数前必须声明用哪一个**；同一文章内不混用 | 两个值来源不同（实验外推 vs PZC 拟合），非笔误 |
| `EDIFFG`（过渡态） | `[讲义]` L3 P129/P147 模板：−0.03 | `[讲义]` L3 P153 自述 + 3 个真实算例：−0.01 | **−0.03 起步，简单体系可收到 −0.01，难收敛放宽到 −0.05** | 两者都可用；讲义自己没给"该用哪个"的判据 |
| `ZPE` 求和 | `[讲义]` L3 P61："全部 meV 求和 / 2000" | `[讲义]` L3 P71 自己算 O₂ 时只取第一个频率 | **只对真实振动模式求和，虚频不计入**（标 `[待核对]`） | P71 的算例可复现（0.097145 eV），全量求和得 0.10836 eV 与讲义不符 |

## 附录 B · 本文件的口径声明

1. **没有报错原文的报错，本文件一律不写**。检索范围与检索式见 §1.9。凡后续补到原文，再按四要素补条目。
2. **凡 `[待核对]` 的条目不得当断言使用**。本文件里所有"由本文件推出"的结论都显式标了 `[待核对]`，主要包括：k 网格与 `R` 的取整公式、`ka = 1/R`、`OPTCELL` 不回显、`总核数 = KPAR × NCORE × 能带组数`、能量口径取 `sigma->0`、ZPE 不含虚频、`LDAUL` 槽位对应 POSCAR 元素顺序、Fe₂O₃ 的 AFM 比 FM 低 0.83 eV、CI-NEB 与 Dimer 的 2.0 meV 之差。
3. **`[官方]` 引用中，若本仓库未镜像该 wiki 页，本文件给外链而不给本地路径**。已知未镜像但仍使用外链的页：`DOSCAR`、`smearing technique`、`k-point integration` 等。已核到本地文件的官方页见正文标注。
4. **不含任何站点信息**。核数、队列、账号、机器路径、`module load` 模块版本一律未录入；`POTCAR` 正文未读取、未引用。
5. **不声称验证过没验证的事**。本文件没有运行 VASP；所有"实测"均指**读取随课真实算例文件**（`things to study/` 下的 `INCAR`/`KPOINTS`/`POSCAR`/`OUTCAR`/`OSZICAR`/`LOG`/`DYNMAT`/`neb*.dat`/`D_BAND_CENTER`/`oer.xlsx` 等）与**算术复算**。
6. **"为什么"不在这里**。本文件凡涉及物理机制、泛函选择、方法学取舍的"为什么"，一律交叉引用 `decide.md`。
