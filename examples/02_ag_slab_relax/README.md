# examples/02_ag_slab_relax —— Ag(111) slab · 几何优化（固定底层）

## 这个例子教你什么

**Selective dynamics** 怎么用（底层 `F F F`、表层 `T T T`）、金属用 `ISMEAR=1`、`ISIF=2`（**slab 不要用 3**）、`LDIPOL`/`IDIPOL` 偶极修正。

## ⚠️ 它不是"生产算例"

每个示例都**极小**（2–27 个原子），目的是"**跑起来 + 演示一个概念**"，
**不是**"算一个能进论文的结果"。参数都是**起点**，不是收敛值。


## 文件

| 文件 | 说明 |
|---|---|
| `INCAR` | 由 `_build_examples.py` **现场生成** |
| `KPOINTS` | Γ 居中规则网格 |
| `POSCAR` | 极小结构 |
| `OPTCELL` | — |
| **没有 `POTCAR`** | **受许可保护，不得再分发**。见下 |
| `README.md` | 本文件 |

## 用之前

### 1. 自己拼 `POTCAR`

```bash
# 顺序必须与 POSCAR 第 6 行的元素顺序**完全一致**
cat <你本地的赝势目录>/Ag/POTCAR > POTCAR
```

> ⚠️ VASP 是**按位置**把 POTCAR 的数据集配给 POSCAR 的元素的，不按元素名匹配。
> 顺序错了，每个原子的赝势都是错的，而**程序不会报错**。

### 2. 校验

```bash
python scripts/validate.py examples/02_ag_slab_relax --potcar examples/02_ag_slab_relax/POTCAR
```

不带 `--potcar` 也能跑，但会报一条 WARN（"本目录里没有 POTCAR —— 与 POTCAR
相关的 5 项检查**本次未执行**"）。那是**预期的**。

### 3. 跑

本示例**不含** `submit.sh`（那是站点相关的）。
你可以：

- 直接 `mpirun -np N <你的 vasp_std>`；
- 或用 `python scripts/wizard.py --goal slab-relax` 生成一份带
  `submit.sh` 骨架的输入（所有站点相关的都写成 `<<<请填写>>>`）。

### 4. 跑完

```bash
python scripts/parse_output.py examples/02_ag_slab_relax   # 数值
python scripts/compare.py      examples/02_ag_slab_relax   # 自洽性 + 力平衡
python scripts/diagnose.py     examples/02_ag_slab_relax   # 症状诊断
```

## 接下来读什么

| 你想知道 | 去哪 |
|---|---|
| 参数怎么选、代价是什么 | `references/decide.md` |
| 出错了怎么修 | `references/playbook.md` §1（73 条症状→处方） |
| 官方原话 | `references/official/pages/` |
| 真实生产算例长什么样 | `references/cases/` |

## 诚实声明

本示例的输入由 `examples/_build_examples.py` **现场生成**，
生成后自动跑 `scripts/validate.py` 校验。

**但"校验通过"只表示"检查过的那些项没发现问题"** ——
它**不**表示这套参数能算对。⚠️ **所有示例都没有在真机上跑过**
（构建环境没有 VASP）。你的第一次运行就是它的验证。
