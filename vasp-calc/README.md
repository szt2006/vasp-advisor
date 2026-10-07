# 这套 VASP 输入是什么

bulk-static 

- 目标：**块体/晶体 单点（静态）** —— 只算一个固定结构的能量与电子结构，不做任何弛豫。
- 为什么这么选：最常见的起点：先确认结构、磁态、收敛性都对了，再往下做。
- 生成时间/工具：由 `scripts/wizard.py` 生成（**未经过真机验证**）

---

## ⚠️ 用之前必须做三件事

### 1. 自己拼 `POTCAR`（本 skill 不提供）

`POTCAR` 受 VASP 许可保护，**不得再分发**，所以这里**故意没有**它。
按 `POSCAR` 第 6 行的**元素顺序**拼接：

```bash
# 顺序必须与 POSCAR 完全一致 —— VASP 按位置配对，不按元素名
cat <你本地的赝势目录>/<元素1>/POTCAR \
    <你本地的赝势目录>/<元素2>/POTCAR > POTCAR
```

拼完**立刻校验**（这一步会核对顺序、`ENCUT` vs `ENMAX`、原子数等）：

```bash
python scripts/validate.py . --potcar ./POTCAR
```

### 2. 改 `submit.sh` 里的占位符

`submit.sh` 里凡是 `<<<请填写>>>` 的地方都是**站点相关信息**
（队列名、核数、`module load`）。本 skill **故意不猜**这些 ——
猜错一次就是白跑一趟，而且写进仓库会把别人带沟里。
（理由见 `references/MAINTENANCE.md`：机器细节不进，结论进。）

### 3. 先跑一个极小算例

在正式提交前，把 `NSW` 临时改成 `2`、`NELM` 改成 `20`，
在登录节点或极短队列上跑一次，确认：
- VASP 能起来（不是编译/库的问题）；
- 没有语法类报错；
- `OUTCAR` 里回显的 `ENCUT`、`ISMEAR`、`ISPIN` 与你的本意一致。

### 4. 上线后立刻自查

```bash
python scripts/validate.py .   --potcar ./POTCAR   # 输入对不对
python scripts/compare.py  .                       # 结果自不自洽
```

`compare.py` 会告诉你：能量在 `OSZICAR` 与 `OUTCAR` 里是否一致、
原子数在三处是否一致、`INCAR` 写的 `ENCUT` 与程序实际用的是否一致、
力是否平衡（孤立体系）。
⚠️ 它**不能**告诉你"算得对不对" —— 它的阈值都没有在真机上标定过（见 `conformance/README.md`）。

---

## 本套参数逐条说明

| 参数 | 值 | 为什么 / 代价 |
|---|---|---|
| `EDIFF` | `1e-06` | 电子步收敛判据。1E-6 常用；过渡态/高精度用 1E-7。 |
| `ENCUT` | `400.0` | 用户输入 |
| `IBRION` | `-1` | 离子更新算法。-1=不动，2=CG，3=Damped MD，5/6=频率。 |
| `ISMEAR` | `0` | 展宽方式。绝缘体用 0，金属用 1，DOS 用 -5。**MP 展宽（>0）对绝缘体不安全**（官方明文）。 |
| `LCHARG` | `.TRUE.` | 是否写 CHGCAR。后续做差分电荷/DOS 要留下。 |
| `LREAL` | `.FALSE.` | 投影算符在实空间还是倒空间。>30 原子官方建议 Auto；高精度能量差建议 .FALSE. 复核。 |
| `LWAVE` | `.FALSE.` | 是否写 WAVECAR。续算要留；纯单点可以关掉省磁盘。 |
| `NELM` | `300` | 最大电子步数。 |
| `NELMIN` | `5` | 最少电子步数。 |
| `NSW` | `0` | 最大离子步数。0=单点。 |
| `PREC` | `Accurate` | 精度模式。Accurate 最稳最慢。 |
| `SIGMA` | `0.05` | 展宽宽度。默认 0.2；绝缘体 0.01–0.05。 |
| `POTCAR` | **不生成** | 受许可保护，不得再分发。见 `POTCAR.README` |
| `KPOINTS` | Γ 居中规则网格 | 四面体方法必须 Γ 居中；fcc/hexagonal 也只能用 Γ 居中（官方明文） |

### 这个目标特有的注意事项

- 单点计算不需要 EDIFFG（没有离子步）。
- 如果体系是金属，把 ISMEAR 改成 1、SIGMA 改成 0.2。
- ISIF 在这里没有意义（NSW=0，没有离子步）—— 写了也不会生效。
- ⚠️ **这次没有生成 POSCAR**（你没给结构文件）—— 请自己放一个进去。

---

## 收敛测试（**必做**）

本向导给的是**起点值，不是收敛值**。上线前请按 `references/decide.md` §3 做：

| 优先级 | 量 | 判据 |
|---|---|---|
| 1 | `ENCUT` | 相邻截断能的总能量差 < **1 meV/atom** |
| 2 | k 点密度 | 相邻网格的能量差 < **1 meV/atom** |
| 3 | 真空层（slab/二维） | 表面能/吸附能变化 < 0.01 eV/Å² |
| 4 | slab 层数 | 吸附能变化 < 0.05 eV |
| 5 | `SIGMA` | 只对金属/近简并体系重要 |

**做法**：一次只动一个量，其余固定；每次都做**单点**（`NSW=0`、`IBRION=-1`），
读 `OUTCAR` 里的 `energy(sigma->0)`（**不是** `free energy TOTEN`）。

---

## 下一步

| 你想知道 | 去哪 |
|---|---|
| 参数该怎么选、代价是什么 | `references/decide.md` |
| 出错了怎么修（症状→处方） | `references/playbook.md` |
| 这门课讲了什么 | `references/course_learned.md` |
| 官方原文 | `references/official/` |
| 真实算例长什么样 | `references/cases/` |

---

## ⚠️ 版本：用之前先确认你的是哪一版

**这条会影响上面每一个参数。**

本 skill 的知识来自**不同世代的 VASP**（实测）：

| 来源 | 版本 |
|---|---|
| 官方 wiki 语料（本项目抓的 630 页） | **VASP 6.6 时代**（91 处版本门槛中 61×`6.5.0`、25×`6.6.0`） |
| `things to study/` 的 98 个真实算例 | **全部 `vasp.5.4.4`** |
| 本课程讲义 | 提到 `VASP5.4.4` |

**为什么要紧**：VASP 对 `INCAR` 里**不认识的标签**常常**静默忽略** ——
你以为设了，其实没生效，而且**不会有任何报错**。

**怎么做**：

```bash
# ① 看你的版本（最可靠）
head -1 OUTCAR        # → vasp.5.4.4.18Apr17-… complex

# ② 让校验器知道（它会检查"这个标签你的版本支持吗"）
python scripts/validate.py . --vasp-version 5.4.4

# ③ 查某个标签的版本门槛
python references/official/_extract_versions.py --gate EFERMI

# ④ 查你那个版本的已知缺陷（官方登记簿）
python references/official/_extract_known_issues.py --for-version 5.4.4
```

> ⚠️ **「官方没标版本」≠「所有版本都支持」。**
> 官方只对**新加的**标签标 `{Available}`；绝大多数标签根本**没标**。
> 正确措辞是「**官方未标注版本门槛**」。

总纲见 `references/VERSIONS.md`。

---

## 诚实声明

本文件由 `scripts/wizard.py` 的参数模板生成。模板里的每个数值都标了出处，
但**没有任何一条经过真机验证**（本机没有 VASP）。它们的定位是"安全的起点"，
不是"已验证的正确答案"。

**你的第一次计算就是对这个模板的验证。** 跑完之后，
请按 `conformance/README.md` 的说明把结果反馈回来 —— 那才是它变成可信知识的唯一途径。
