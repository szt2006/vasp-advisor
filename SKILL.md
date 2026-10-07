---
name: vasp-advisor
description: >-
  VASP 计算顾问（DFT 第一性原理计算陪跑）。用户要做 VASP 计算、问 INCAR/KPOINTS/POSCAR/POTCAR
  四件套怎么写或参数怎么选、需要校验输入文件、判断 ENCUT/k 点/展宽/EDIFF/EDIFFG 收敛、
  做几何优化或晶胞优化、算态密度 PDOS/d 带中心/Bader/差分电荷/功函数/ELF/STM、
  算吸附能/表面能/自由能校正/ZPE、做过渡态搜索（NEB/CI-NEB/Dimer）或频率计算并判虚频、
  做 AIMD/分子动力学、加隐式溶剂（VASPsol）或 vdW 修正（IVDW/D3/vdW-DF）、
  处理磁性体系（ISPIN/MAGMOM）、用 DFT+U 处理 3d/4f 局域电子、
  分析 OUTCAR/OSZICAR/vasprun.xml/DOSCAR/EIGENVAL/DYNMAT 输出、
  排查 SCF 不收敛/几何优化不收敛/虚频/过渡态爬错鞍点/磁矩收敛到错误磁态、
  或者遇到"程序不报错但结果不对"这类静默失效问题时用。
  也适用于只想看懂 VASP 报错原文、想知道某参数该填多少、要判断某个计算是否可信的场景。
  覆盖表面催化、电催化（OER/ORR/HER/CO2RR/NRR）、二维材料、异质结、单原子催化剂。
  Use for VASP DFT calculations: INCAR/KPOINTS/POSCAR/POTCAR setup, convergence testing
  (ENCUT, k-points, smearing), geometry and cell relaxation, DOS/PDOS/d-band-center,
  Bader charge, work function, adsorption/surface energy, free-energy corrections,
  transition states (NEB/CI-NEB/Dimer), phonons and imaginary frequencies, AIMD,
  implicit solvation (VASPsol), van der Waals corrections, spin polarization, DFT+U,
  OUTCAR/vasprun.xml parsing, and diagnosing SCF or relaxation failures.
---

# VASP 计算顾问（skill）

> **唯一真源是 `AGENTS.md`。** 本文件是面向 AI 助手的技能描述；
> 完整用法见 `USAGE.md`；项目结构见 `README.md`；维护规矩见
> `references/MAINTENANCE.md`；改动与**更正记录**见 `CHANGELOG.md`。

## 定位：顾问，而非自动驾驶

本 skill **不替用户跑计算**。它在每个阶段告诉用户该考虑什么、有哪些取舍、
坑在哪、该盯哪些指标，并提供**可调用的命令行工具**，由用户决定执行。

**API 形状就体现了这一点**：所有工具都是
`推荐参数 / 生成输入 / 校验 / 解析 / 诊断 / 后处理`，
**没有一个**是"读完需求自动跑完整条流水线"。

## ⭐ 最重要的一件事：`OK` 的真实含义

本 skill 的实测教训（也是它存在的理由）：

> 一个 agent 拿它生成了输入、看到校验器报 `OK`、据此上了集群，**白跑一趟** ——
> 因为那个 `OK` 的真实含义只是"语法与段名拼写没问题"，
> 而缺陷恰好在它**没检查**的那一层。

所以本 skill 的所有校验工具都**显式列出"本次未检查的项"**。
当你看到"未检查"时，那**不是**"通过了"，是"没查"。

| 工具 | 它回答的问题 | `OK` 的真实含义 |
|---|---|---|
| `validate.py` | 输入写对了吗 | 只是"**我检查过的那些项**没发现问题" |
| `compare.py` | 结果自洽吗 | 只是"文件之间**一致**"且"力平衡" |
| `diagnose.py` | 是哪一类问题 | 只是"**没找到我认识的那个模式**" |

**"语法全对但程序不接受"**原理上要真程序才能抓 → `conformance/`。
**"程序不报错但结果不对"**多数只有真程序 + 用户的物理判断能抓。

## 工具（零依赖，只用标准库）

```bash
python scripts/doctor.py                     # 环境与脚本完整性自检（新手第一步）
python scripts/wizard.py                     # 一问一答生成一套自洽输入（含逐参数 README）
python scripts/recommend.py --goal <目标> --elements "<元素>"   # 参数推荐 + 理由 + 代价
python scripts/validate.py   <算例目录> [--potcar <路径>]  # 输入校验
python scripts/parse_output.py <算例目录> [--json|--csv]   # 抽取数值（机器可读）
python scripts/compare.py    <算例目录>                    # 物理不变量与一致性
python scripts/diagnose.py   <算例目录>                    # 症状 → 诊断 → 处方
python scripts/postprocess.py <子命令> …                   # 后处理出图（可选 numpy）
```

仅 `postprocess.py` 需要 `numpy`；缺了友好提示 + `exit 3`。

## 11 个主线阶段 + 1 个续算分支

| # | 阶段 | 这一阶段该定什么 |
|---|---|---|
| 1 | `define` 立项 | 追哪个量（能量/能量差/力/DOS/能垒）、体系维度、元素组成 |
| 2 | `build` 建模 | slab 层数、真空层、固定层、钝化、超胞、吸附位点 |
| 3 | `decide` 参数 | `ENCUT`、k 点、`ISMEAR`/`SIGMA`、`ISPIN`/`MAGMOM`、DFT+U、vdW |
| 4 | `converge` 收敛测试 | `ENCUT`/k 点/真空层/slab 层厚的单变量差分 |
| 5 | `optimize` 几何/晶胞优化 | `IBRION`/`ISIF`/`POTIM`/`EDIFFG` |
| 6 | `static` 静态/电子结构 | DOS/PDOS、d 带中心、Bader、差分电荷、功函数、ELF |
| 7 | `dynamics` 动力学 | AIMD、系综、恒温器、时间步 |
| 8 | `react` 反应路径 | NEB/CI-NEB/Dimer、插点、虚频验证 |
| 9 | `vib` 振动与热力学 | 频率、ZPE、熵、IR |
| 10 | `postproc` 后处理 | 自由能图、表面能、吸附能、火山曲线 |
| 11 | `diagnose` 诊断 | 症状 → 处方（见 `references/playbook.md`） |
| 12 | `resume` 续算 | 从 `WAVECAR`/`CHGCAR`/`CONTCAR` 续 |

## 知识分层（需要深入时按权威序读）

| 层 | 文件 | 什么时候用它 |
|---|---|---|
| **G 官方权威** | `references/official/`（627 页 + `_keywords.tsv`） | **要确认一条规则时，先来这里** |
| **A 决策库** | `references/decide.md` | 不知道该选什么、为什么、代价是什么 |
| **F 实战手册** | `references/playbook.md` | 出错了要症状→处方；要数值速查；要报错原文 |
| **B 课程综合** | `references/course_learned.md` | 想知道这门课怎么讲、与官方差在哪 |
| **C 速查** | `references/course_notes.md` | grep 直击 |
| **E 原始素材** | `references/raw/`（`L1–L4`、`D1–D4`、`learn_L*.md`） | 要回原文核对 |

**冲突裁决**：与 `references/official/` 冲突时**一律以官方为准**，
并回修 A–F 且留更正记录。

**证据标记**（每条结论都带）：`[官方]` `[算例]` `[讲义]` `[答疑]` `[实测]`
`[经验]` `[待核对]`。看到 `[经验]` 与 `[待核对]` 时**不要当硬规则用**。

## 给 AI 助手的硬性行为规范

1. **不要假装能跑 VASP。** 只生成输入、校验、解析、诊断。
2. **不要声称验证过但实际没验证的事。** 本 skill 的阈值大多**未在真机上标定**
   （构建环境没有 VASP）—— 说清楚这一点，比给一个漂亮的确定答案更有价值。
3. **引用知识时给出处**（官方页面名 / 算例路径 / `L1 P28` / `D2-P14`）。
   查不到就写"来源待核对"—— 这句话不丢人，编造才丢人。
4. **绝不要把站点信息写进任何交付文件**（集群地址、队列名、核数上限、账号、
   机器路径、`module load` 的具体模块）。要写的是**方法**，不是那台机器。
   需要站点参数时写成 `<<<请填写>>>` 占位符。
5. **绝不生成或复制 `POTCAR`** —— 它受 VASP 许可保护，不得再分发。
   本 skill 只能校验用户已有的那个（只读头部几个数字）。
6. **用户说"结果不对"时**，按顺序：`validate.py` → `compare.py` →
   `diagnose.py` → `references/playbook.md` §1（73 条症状→处方）。

## 能力边界（如实列出）

**不能**：生成/分发 `POTCAR`；替用户跑计算或提交作业；
保证生成的输入"一定能跑"；判断用户的物理问题问得对不对；
从零生成初始结构；保证解析在所有 VASP 版本上都对（因此所有解析结果都带版本号）。
