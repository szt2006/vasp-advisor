# _ENTRY —— **症状入口**：先分清是哪一类，再查

> **这一页只做一件事**：让你在 **30 秒内**确定「我遇到的是**哪一类**问题」，
> 然后把你送到**已经写好的**那一页去。
>
> ⚠️ **它不重复知识** —— 每条都指向 `playbook.md` / `diagnose.py` /
> `_SYSTEMS.md` / `_GATES.md`。**这一页只是入口。**

---

## ⚠️ 为什么需要这一页（一次真实事故）

使用者（有经验的算力用户）报来一个真实失效：

> 179 原子团簇、16 MPI rank、Γ 点、`ENCUT=400`、
> **没写 `NPAR`/`NCORE`** ⇒ 第一次 SCF 就 `SIGSEGV`，`OSZICAR` 只有表头。

他**自己花了几小时**才找到原因。事后复盘，本 skill 当时的缺陷不是"知识不够"
（`NCORE` 的适用条件**同时存在于四个地方**），而是：

> ⭐ **知识与使用者之间没有"入口"。**
> 他不知道该去查 `NCORE` —— 因为**没有人告诉他"你这个症状属于哪一类"**。

⇒ 所以这一页的**唯一职责**是分流。

---

## 第 0 步：**先分清三类**（这一步不能跳）

VASP 出的问题，**先归到下面三类之一**，因为三类的**查法完全不同**：

| | 症状长什么样 | 本质 | 先跑 |
|---|---|---|---|
| **A** | **作业根本没跑起来** —— `OSZICAR` 只有表头 / 立刻退出 / 报 SIGSEGV、`BAD TERMINATION` | **资源与并行分解**的问题（不是物理问题） | `diagnose.py` 的 `LAUNCH.*` |
| **B** | **跑完了，但结果不对**（或可疑）—— 有 `General timing`，数值却说不通 | **物理与设置**的问题，**多数不报错** | `compare.py` → `diagnose.py` |
| **C** | **能跑对，但太慢 / 太贵** | **并行与算法**的调优问题 | `playbook.md` §0.13 等 |

> ⚠️ **为什么必须先分类**：三类的**处方是冲突的**。例如
> 「调大并行度」对 C 类是对的，对 A 类可能是**火上浇油**。
> **在没分类之前调参，等于赌博。**

### 60 秒分诊命令

```bash
# ① 它跑起来了吗？—— 数 SCF 迭代行
grep -cE "^(DAV|RMM):" OSZICAR        # 0 = 一次 SCF 都没走 ⇒ A 类

# ② 它正常收尾了吗？
grep -c "General timing" OUTCAR        # 0 = 没正常收尾（崩了/墙钟/还在跑）

# ③ 崩在哪一行？（只看第一条，别被后面的 SIGKILL 带偏）
grep -nE "forrtl|SIGSEGV|BAD TERMINATION|KILLED BY SIGNAL" LOG | head -5

# ④ 并行是怎么分的？（A 类的关键线索）
grep -E "running on|distrk:|distr:" LOG

# ⑤ 一次问全（推荐）
python scripts/diagnose.py <目录>
```

**判据**：`OSZICAR` 里有没有 `DAV:` / `RMM:` 行。
⚠️ **不要用 `exit code` 判断** —— `mpirun` 下崩溃时它可能仍是 0 或 255。

---

## A 类 · 作业没跑起来

### A-1 最常见的那个：`distr: one band on 1 cores`

**这是本 skill 见过的最贵的一类坑。** 它的完整链条是：

```
INCAR 里没写 NCORE/NPAR
   ⇒ 走官方默认 NCORE = 1
   ⇒ 每个 rank 独占一个 band、独自完成整块 FFT
   ⇒ 大体系 + 多 rank 下，每个 rank 的栈/内存需求爆掉
   ⇒ 第一次 SCF 就 SIGSEGV（而 OSZICAR 只有表头）
```

**先做这一件事**（在怀疑系统/队列配置**之前**）：

```
在 INCAR 里加一行  NCORE ≈ √(可用 rank 数)
⚠️ 用 NCORE，不要用 NPAR；两者同时写会让 NPAR 优先、NCORE 被静默忽略
```

**为什么敢这么说**：官方 `NCORE` 页明文 —— `NCORE=1` 时
「投影函数必须**完整存在每个 rank 上** ⇒ **高内存占用**」；
而 `NCORE ≈ √(ranks)` 会「**同时降低内存需求**与正交化成本」。
本项目的实测对照也一致（同二进制、同 INCAR、同栈上限，只改并行分解）。

| 去哪里 | 看什么 |
|---|---|
| `python scripts/diagnose.py <目录>` | `LAUNCH.crash_no_scf`（含判据与处方） |
| `python scripts/validate.py <目录> --ncores <核数>` | **提交前**的并行预检 |
| `references/_SYSTEMS.md` | **规模轴**：≥100 原子就是这一类的高发区 |
| `references/_GATES.md` §3 | 规模敏感标签清单（后果随核数/原子数变） |

### A-2 ⚠️ 红鲱鱼：`ulimit: stack size: cannot modify limit`

**这一行不能单独当证据。** 当队列的栈硬限由调度器设死时，
作业脚本里的 `ulimit -s unlimited` **必然**失败并打印它 ——
**在成功的作业里也会出现**。

⇒ 把它当根因，会把你引向「去找管理员改队列」，而那通常**不是**真原因。
`diagnose.py` 的 `LAUNCH.ulimit_redherring` 就是专门用来**防这个误判**的。

### A-3 其它 A 类症状

| 症状原文 | 去哪里 |
|---|---|
| `VERY BAD NEWS` / `internal error in subroutine` | `playbook.md` §5（报错原文速查） |
| 输入被程序拒绝（标签不认、值非法） | `python scripts/validate.py <目录>` |
| 程序根本没启动（可执行文件/路径/POTCAR 问题） | `playbook.md` §1.7 |

---

## B 类 · 跑完了，但结果不对

> ⚠️ **这一类是本 skill 花力气最多的地方**，因为
> **「程序不报错但结果不对」多数只有真程序 + 你的物理判断能抓**。
> 本 skill 能做到的是：**把"可疑"变成"可查"**。

### B-1 先做自洽性检查（**最值钱的一个动作**）

```bash
python scripts/compare.py <目录>
```

它查的是**跨文件/跨算例的一致性**：能量自洽、原子数一致、
`ENCUT` 一致、**力平衡**（孤立体系受力应为 0）。
不一致**不等于错**，但**必须先解释清楚**才能往下走。

### B-2 然后按"哪一类不对"查

| 你觉得哪里不对 | 去哪里 |
|---|---|
| 能量/收敛 | `diagnose.py` 的 `SCF.*` / `GEO.*` |
| 磁矩 | `playbook.md` §1.5（磁矩不收敛 / 收敛到错误磁态） |
| 频率 / 虚频 | `playbook.md` §1.3，注意「最小 6 个虚频可无视」**只对孤立分子成立** |
| 过渡态 | `playbook.md` §1.4（搜错鞍点 / NEB 不收敛） |
| DOS / PDOS / 电荷 / 功函数 | `playbook.md` §4（后处理判读经验） |
| **说不清哪里不对，就是"感觉不对"** | `playbook.md` **§1.6**（"算完了但结果不对"）与 **§1.10**（输入解析类静默失效） |

### B-3 ⚠️ 三类**最阴**的（不报错、设置根本没生效）

1. **`NCORE` 与 `NPAR` 同时写** ⇒ `NPAR` 优先，`NCORE` **被静默忽略**
2. **`ISTART=1` 但没有 `WAVECAR`** ⇒ 程序忽略它、从头算
3. **版本不支持的标签在老版本上被静默忽略** ⇒ 见 `references/VERSIONS.md`

⇒ 这三个的共性是：**你写的和你得到的不一样，而程序一声不吭。**
`playbook.md` §1.10 专门收这一类。

### B-4 ⚠️ 诊断时最容易犯的错

**先读 `references/playbook.md` §4b「诊断反模式」**（AM-1 ~ AM-10）。
最常犯的两条：

- **报资源数字（栈/内存/耗时）时必须同时报"在什么并行配置下测的"** ——
  不带配置的资源数字**没有意义**；
- **「某个取值没救回来」≠「该变量无关」**。

---

## C 类 · 能跑对，但太慢 / 太贵

| 你想省什么 | 去哪里 |
|---|---|
| **并行效率**（核数、`NCORE`、`KPAR`） | `references/playbook.md` §0.13 |
| **k 点数量** | `playbook.md` §0.2；`decide.md` 的 k 点条目 |
| **`ENCUT` / 基组** | `decide.md` 的 `ENCUT` 条目（注意变胞要重测） |
| **算法选择**（`ALGO` / `LREAL` / `NELM`） | `decide.md`；`playbook.md` §0 |
| **不知道从哪下手** | `python scripts/guide.py show params`（阶段 3 的决策点） |

⚠️ **C 类的优化有两个纪律**：

1. **先确认它算得对，再优化它跑得快。** 对一个结果还不可信的计算调性能，
   是在优化一个你不需要的东西。
2. **并行参数依赖核数与体系大小** —— 别照抄别人的值。
   官方给的是「跑一个简短的 `NCORE` 扫描」，不是固定值。

---

## 附：本页与其它入口的分工

| 你想问 | 去 |
|---|---|
| **我遇到的是哪一类问题？** | **本页** |
| 我现在该干什么？（按项目阶段） | `python scripts/guide.py scan <目录>` |
| 我算的是哪类体系？该类注意什么？ | `python _system_types.py --lookup <目录>` |
| 具体某个症状怎么办？ | `references/playbook.md` §1（73 条） |
| 某条报错的原文是什么意思？ | `references/playbook.md` §5 |
| 该选哪个参数值？ | `references/decide.md` |
| 这个标签我的版本支持吗？ | `references/VERSIONS.md` |
| 这句话在什么条件下才成立？ | `references/_GATES.md` |
| **诊断时我怎么想错了？** | `references/playbook.md` §4b |

---

_本页是**入口**，不是知识。如果你的问题在本页找不到入口，
那说明**本页有缺口** —— 请按 `references/MAINTENANCE.md` 的流程补一条。_
