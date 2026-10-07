# examples —— 开箱即用的示例

> 每个示例都教你**一件事**。它们都**极小**（2–27 个原子），
> 目的是"**跑起来 + 演示一个概念**"，**不是**"算一个能进论文的结果"。
>
> ⚠️ **所有示例都没有在真机上跑过**（构建环境没有 VASP）。
> 输入由 `_build_examples.py` **现场生成**并**立刻校验**，
> 但"校验通过"只表示"**检查过的那些项**没发现问题"。

---

## 为什么输入是"现场生成"而不是"存好的文件"

CP2K skill 的实测教训：

> **静态卡片会过期** —— 生成器改了、卡片没跟着改，
> 检查就在验证**历史**而不是**现在**。

所以本目录放的是**生成脚本 + 每个示例的 README**，
输入由脚本**现场生成**，生成后**立刻调 `scripts/validate.py`**——
**生成物过期 ⇒ 校验立刻红。**

---

## 示例清单

| 目录 | 体系 | 学到什么 |
|---|---|---|
| [`01_si_bulk_static`](01_si_bulk_static/README.md) | Si 块体（2 原子） | **最小闭环**：四件套齐了就能算。Γ 居中 k 点、绝缘体 `ISMEAR=0`、单点 `NSW=0` |
| [`02_ag_slab_relax`](02_ag_slab_relax/README.md) | Ag(111) slab（27 原子） | **`Selective dynamics`**（底层 `F F F`、表层 `T T T`）、金属 `ISMEAR=1`、**`ISIF=2`（slab 不要用 3）**、`LDIPOL`/`IDIPOL` |
| [`03_mos2_monolayer_optcell`](03_mos2_monolayer_optcell/README.md) | 单层 MoS₂（3 原子） | **二维材料不能直接用 `ISIF=3`** —— 真空方向会被一起优化掉。演示 `OPTCELL`，以及**怎么核对它生效了**（它**不在 `OUTCAR` 回显**） |
| [`04_si_bulk_dos`](04_si_bulk_dos/README.md) | Si 块体（2 原子） | DOS 的**正确姿势**：单点 + `ISMEAR=-5`（**必须 Γ 居中**）+ `LORBIT=11`；以及一条**无报错的错误**（用弛豫计算的 DOS 是错的） |
| [`05_bad_inputs_demo`](05_bad_inputs_demo/README.md) | Si 块体 | ⛔ **故意写坏的** —— 演示校验器能抓什么。**本 skill 最该被理解的一课** |

**推荐顺序**：`01` → `05` → `02` → `03` → `04`。

先看 `01`（知道正常长什么样），再看 `05`（知道不正常长什么样）——
**先建立"什么是错的"的直觉，比先学会"什么是标准的"更重要。**

---

## 怎么用

```bash
# 1. 生成（并自动校验）
python examples/_build_examples.py
python examples/_build_examples.py --list          # 看会生成什么
python examples/_build_examples.py --example 02_ag_slab_relax

# 2. 想用你自己的 POTCAR 做完整校验（推荐）
python examples/_build_examples.py --with-potcar <你的 POTCAR 路径>

# 3. 拼 POTCAR（**顺序必须与 POSCAR 第 6 行一致**）
cd examples/02_ag_slab_relax
cat <赝势目录>/Ag/POTCAR > POTCAR

# 4. 校验
python ../../scripts/validate.py . --potcar ./POTCAR

# 5. 跑（本目录**不含** submit.sh —— 那是站点相关的）
mpirun -np N <你的 vasp_std>

# 6. 跑完
python ../../scripts/parse_output.py .
python ../../scripts/compare.py      .
python ../../scripts/diagnose.py     .
```

---

## ⚠️ 三件必须知道的事

### 1. 这里的示例**不含 `POTCAR`**

`POTCAR` 受 VASP 许可保护，**不得再分发**。所以：

- 每个示例目录里都**故意没有** `POTCAR`；
- 不带 `--potcar` 跑 `validate.py` 时，会有一条 WARN
  "本目录里没有 POTCAR —— 与 POTCAR 相关的 5 项检查**本次未执行**"——
  **那是预期的**，不是错误。

### 2. `05_bad_inputs_demo` **不要拿去算**

它**故意**包含了四类真实踩过的缺陷：

| # | 缺陷 | 校验器报什么 |
|---|---|---|
| ① | 关键字拼错（`ENCUTT`） | `INCAR.unknown_tag`（WARN —— 见下） |
| ② | 关键字发到了不属于它的文件（`Selective dynamics` 写进 `INCAR`） | `INCAR.unknown_tag`（WARN） |
| ③ | 值里混进说明文字（抄 wiki 时丢了 `#`） | `INCAR.annotation_in_value`（**ERROR**） |
| ④ | 圆括号说明里含 `;`（**圆括号不是注释，`;` 是语句分隔符**） | `INCAR.semicolon_comment`（**ERROR**） |

> ⚠️ ① 和 ② 报的是 **WARN 而不是 ERROR** ——
> 因为那个目录里**没有 `OUTCAR`**，工具**无法证明** VASP 到底认没认这个标签。
> 它**不会假装知道**。
> **这正是本 skill 的设计原则**：没有 `OUTCAR` 可比时，
> 它说"我分不出来"，而不是"肯定错了"。

### 3. 示例里的参数是**起点**，不是收敛值

`ENCUT` 都取 300 eV（为了让示例跑得快）。真要算东西：

```bash
python scripts/recommend.py --goal <目标> --elements "<你的元素>" --potcar ./POTCAR
```

然后**自己做收敛测试**（见 `references/decide.md` §3）。
官方对 `ENCUT` 的**唯一**要求就是"显式写 + 单独测收敛"。

---

## 接下来读什么

| 你想知道 | 去哪 |
|---|---|
| 参数怎么选、为什么、代价是什么 | `references/decide.md` |
| 出错了怎么修（73 条症状→处方） | `references/playbook.md` §1 |
| 官方原话怎么说 | `references/official/pages/` |
| **真实的**生产算例长什么样 | `references/cases/` |
| 这门课怎么讲的 | `references/course_learned.md` |
