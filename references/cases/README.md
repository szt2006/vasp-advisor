# references/cases —— 真实生产算例登记（案例层）

> **这一层登记的是"真的被算出来的东西"。**
> 按本项目的引用优先级，**真实交付文件（输入/输出）比任何课件都值钱** ——
> 它们**不会说谎**。
>
> ⚠️ **本层不含 `POTCAR`**（受 VASP 许可保护，不得再分发），
> 也不复制原始算例文件（体积大：本批含 `WAVECAR`/`CHGCAR` 共 GB 量级）。
> 本层只保留**登记清单**与**从中学到的东西**。

---

## 1. 为什么要有这一层

课程讲义是**二手**（讲师的理解与讲法）；而算例是**一手**：
作者当时**实际写了什么**。两者常不一致 —— 而**不一致处几乎总是坑**。

本项目已经从这批算例里挖出了一批**讲义没讲、但算例里做了**的东西：

| 发现 | 算例证据 | 价值 |
|---|---|---|
| `ENCUT` 恰为 `max(ENMAX)` 的 **1.3 倍** | `day1/fe2o3`：O 的 `ENMAX = 400.000` → `ENCUT = 520`（`ISIF=3` 晶胞优化） | 给出一个**具体起点**；同时也说明"1.3 倍"是已弃用的 `PREC=High` 行为 |
| `OPTCELL` 冻结真空方向 | `day1/mos2`、`day1/vdw-df2`、`day2/mos2ws2` | 二维/表面体系做 `ISIF=3` 的正确做法 |
| **`OPTCELL` 不在 `OUTCAR` 回显** | 在上述算例的 `OUTCAR` 里搜不到它（`[实测]`） | 程序**不会告诉你它有没有生效** ⇒ 只能比 `POSCAR`/`CONTCAR` |
| 赝氢在**键中点**且固定 | `day1/GaN`：H–N = 0.9865 Å ≈ Ga–N(1.9742 Å)/2，H 标 `F F F` | 精确到 0.0006 Å 的可复查判据 |
| 赝势是 **`H.75`**（分数占据，`ZVAL=0.75`） | `day1/GaN` 的 `POTCAR` TITEL | 一个容易被忽略的赝势变体；`ENCUT` 要重新核对 |
| **DOS 出自弛豫计算** | `day2/ni-co`：`NSW=300`，`OUTCAR` 里 `E-fermi` 出现 8 次 | 与讲义 P62 要求的"DOS 步用 `NSW=0`"**相悖** → 一条**无报错**的错误 |
| 讲义说"和优化一样"，算例多出偶极修正 | 讲义 L2 P141 vs `4-thermo/7-2-adsorptionO-Au/hollow` 的 `LDIPOL=.TRUE./IDIPOL=3` | 讲义自相矛盾；按算例为准 |
| 频率计算只放开吸附物 | `6-electronic/oer/{o,oh,ooh}/freq/`：31 个 slab 原子全 `F F F` | ZPE 校正的实操约定 |

`[实测]` = 本项目构建时真的核对出来的。**每一条都可以用登记清单里的路径复现。**

---

## 2. 本批算例的总体情况

| 组 | 目录 | 体系 | 演示什么 |
|---|---|---|---|
| day1 | `day1/fe2o3` | Fe₄O₆（赤铁矿型胞） | DFT+U（`LDAUU=5.3`）、`ISIF=3`、`ISPIN=2`、反铁磁 `MAGMOM` |
| day1 | `day1/GaN` | GaN slab + 赝氢 | 赝氢钝化、`H.75` 赝势、真空层 15 Å |
| day1 | `day1/mos2` | 单层 MoS₂ | **`OPTCELL`** 面内优化；`ISPIN=1` |
| day1 | `day1/vdw-df2` | 单层 MoS₂ | **vdW-DF2**：`GGA=ML` + `LUSE_VDW=.TRUE.` + `ZAB_VDW=-1.8867` + `AGGAC=0` |
| day2 | `day2/Ag` | Ag(111) slab | 金属 `ISMEAR=1`/`SIGMA=0.2`；`Selective dynamics`；单点 |
| day2 | `day2/al2o3` | Al₂O₃ 胞 | 绝缘体 `ISMEAR=0`；**`ISIF=3` 但 `NSW=0`**（单点 → `ISIF` 不生效） |
| day2 | `day2/au111-opt` | Au(111) + O | 弛豫到底（`reached required accuracy`）；**力平衡 `\|ΣF\| ≈ 0`** |
| day2 | `day2/c` | 石墨烯条带 | 一维体系（`KPOINTS` 用 `1 5 1`） |
| day2 | `day2/mos2ws2` | MoS₂/WS₂ 异质结（96 原子） | 大体系 + `OPTCELL` |
| day2 | `day2/ni-co` | Ni slab + CO | **DOS 出自弛豫计算**（无报错的错误）；`D_BAND_CENTER`/`FERMI_ENERGY` |
| day3 | `day3/ts/dim` | Au + O 的 Dimer 过渡态 | `IBRION=3` + **`POTIM=0`**（官方默认值）+ `ICHAIN=2`/`IOPT=2` + `MODECAR` |
| day3 | `day3/ts-neb/00`、`day3/ts/05` | 过渡态 | ⚠️ `OUTCAR` 实际是 `IBRION=2` 的**普通优化**（不能用来核验过渡态流程） |
| day3 | `day3/idpp/*` | 插点对比 | 线性插值 vs **IDPP**（C–H = 0.5916 vs 1.0879 Å）；⚠️ **目录名与内容不符** |
| day4 | `day4/oer/*` | CoN₄ OER 中间体 | 频率计算（`POSCAR_fix`、`DYNMAT`） |
| 中级班 | `线上中级班-催化资料/1-fundamental/*` | 晶胞优化 / HSE / 表面优化 | `cellopt-mos2-withconstrain`、`hse`（**分号陷阱**在这里）、`optsurface-au111` |
| 中级班 | `.../2-dos/*` | DOS 与 d 带中心 | `dos-ex2-d-band-center-slab/dos-slab/{ag,au,co,cu,fe,ir,Ni,os,pd,pt,rh,ru}` —— **12 种金属的对照集** |
| 中级班 | `.../3-electronicStructure/*` | 电子结构 | Bader、差分电荷、ELF（`Na2He`）、静电势、band offset |
| 中级班 | `.../4-thermo/*` | 表面能与吸附 | 表面能（100/110/111 三个面）、吸附 O、RuO₂、频率、IR |
| 中级班 | `.../5-ts/*` | 过渡态 | `8-1-ex1-O-Au`（CI-NEB / Dimer）、`8-1-ex2c6h12ptgraphene`（00–05 全套） |
| 中级班 | `.../6-electronic/*` | 电催化与溶剂 | OER（`slab`+`o`/`oh`/`ooh`/`o2`）、VASPsol（H₂O / GaN 各两套 `INCAR`） |

**总计 98 个含 `INCAR` 的算例目录**（`[实测]`：`_validate_all_suites.py` 与
`_inject_test.py` 的回归就是在它们上面跑的）。

---

## 3. 这些算例**不是**"正确答案"

必须说清楚：

- **真实算例也会有笔误。** 例如 `1-fundamental/hse/INCAR:62` 的圆括号里含 `;`
  （会被切成两条语句）；`partialCharge/INCAR` 抄 wiki 时丢了 `#`。
- **算例也不总是自洽。** 例如 `day3/ts/05` 与 `day3/ts-neb/00` 的 `OUTCAR`
  实际是普通优化，与目录名暗示的"过渡态"不符。
- **目录名可能骗人**（`[实测]`）：`day3/idpp/` 下名为 `nebmake` 的目录装的
  其实是 **IDPP 结果**（与 `c6h12-idpp` 的文件 MD5 逐字节相同）。

⇒ 所以权威序是：

```
references/official/（官方）
   ↓ 官方没写
真实算例文件          ← 本层，但**它自己也可能错**
   ↓
讲义 → 答疑 → 自己的推断
```

**"算例里这么写"不等于"这么写是对的"。** 冲突时按上表裁定，
并**把裁定理由写出来**（本项目落在 `references/raw/learn_L*/§4` 与
`references/playbook.md` 附录 A）。

---

## 4. 本层没有什么（诚实说明）

| 项 | 状态 |
|---|---|
| 原始算例文件的副本 | **没有** —— 体积大（含 `WAVECAR`/`CHGCAR`，最大 190 MB 单个文件），且含 `POTCAR` |
| `POTCAR` 或任何片段 | **绝对没有**（许可限制 + `.gitignore` + `_doc_consistency.py --scan-leaks`） |
| 逐字节的 sha256 溯源清单 | **未做**（这一批是"登记"而非"入库"；若要逐字节保留，见下） |
| 站点信息（`sub_vasp`/`makefile.include` 里的路径、队列、模块名） | **没有进仓库** —— 按 `MAINTENANCE.md` §0.1「机器细节不进，结论进」 |

### 如果将来要把某个算例**逐字节入库**

CP2K skill 的做法可以照搬：

1. 只选**极小且许可干净**的算例（**绝不含 `POTCAR`**）；
2. 逐字节复制，并把 `sha256` 写进 `_COPY_MANIFEST.tsv`；
3. 在 `README.md` 里记**已知错误**（CP2K 的 `cases/README.md` 记着
   "4/5 张 `&FIXED_ATOMS` 索引错而 CP2K 静默通过"这类信息）；
4. **把 `cases/` 加进 `_audit_citations.py` 的 `SKIP_DIRS`**（已在里面）。

> ⚠️ 第 3 条最重要：**入库的算例如果带着未标注的错误，它就会变成"权威"** ——
> 而那是**主动传播错误**，比不入库更糟。

---

## 5. 这些算例是怎么被"读"出知识的

不是"看一眼"，而是**逐页读完讲义 + 逐个核对算例**：

1. **四份精读报告**（`references/raw/learn_L1–L4.md`）里，
   每份都有 §3「知识条目」与 §4「冲突日志」，
   而 §3 里凡讲到某参数的页，都会去真实 `INCAR` 里核对
   **讲义说的 vs 算例实际写的**，不一致就**单列一节**。
2. **交叉验证靠数字**，不靠印象。例如：
   - `ENCUT/ENMAX = 520/400 = 1.3`（精确）
   - H–N = 0.9865 Å vs Ga–N/2 = 0.9871 Å（差 0.0006 Å）
   - `OPTCELL` 在 `OUTCAR` 里**零命中**，而 `CONTCAR` 的 c 严格不变
   - IDPP 的 C–H = 1.0879 Å vs 线性插值 0.5916 Å（复现讲义写的 1.09/0.59）
3. **所有 98 个算例都被两个套件反复跑过**：
   `validate.py`（输入层）与 `compare.py`/`diagnose.py`（输出层）。
   本项目因此发现并修掉了 **23 处**自家护栏的缺陷（见 `CHANGELOG.md`）。

---

## 6. 想复现 / 想贡献

**复现**：把原始资料放回 `things to study/`（已 `.gitignore`），然后

```bash
# 输入层：跑遍所有算例
python scripts/validate.py <某个算例目录> --potcar <它的 POTCAR>

# 输出层
python scripts/compare.py  <算例目录>
python scripts/diagnose.py <算例目录>
```

**贡献**：如果你从这批（或你自己的）算例里挖到
「**程序不报错、但结果是错的**」的实例 —— **那是本层最值钱的东西**。
请附：算例路径、你观察到什么、怎么排除掉的、判据是什么。
它会落进 `references/playbook.md` §1.6 与 `references/decide.md`，
并在 `CHANGELOG.md` 留记录。
