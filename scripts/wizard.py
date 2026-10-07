#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""wizard.py —— 一问一答生成一套自洽的 VASP 输入（**零依赖**）

它做什么
========
按"你要算什么"逐步问 5–7 个问题，然后生成：

    <输出目录>/
    ├── INCAR          ← 生成
    ├── KPOINTS        ← 生成
    ├── POSCAR         ← 从你给的结构文件复制（归一成 LF，去掉 BOM）
    ├── POTCAR.README  ← **说明为什么这里没有 POTCAR**（见下）
    ├── README.md      ← 这套输入是什么、每个参数为什么这么选、下一步做什么
    └── submit.sh      ← 提交脚本骨架（**占位符，必须你自己改**）

它**不做什么**（这是设计上的硬边界，不是没来得及做）
==================================================
1. **不生成 `POTCAR`。** `POTCAR` 受 VASP 许可保护，不得再分发。
   本 skill 既不能替你下载、也不能替你生成它 —— 只能**校验**你已经有的那个。
   所以生成物里留一个 `POTCAR.README` 告诉你该怎么拼。
2. **不提交作业。** `submit.sh` 里凡是站点相关的东西（队列名、核数、
   `module load`）一律写成 `<<<请填写>>>` 占位符。理由见
   `references/MAINTENANCE.md`：**机器细节不进仓库**。
3. **不做收敛测试。** 它给的数值是**起点**，不是收敛值。

⚠️ **生成完必须再校验一次**：
```
python scripts/validate.py <输出目录> --potcar <你本地的 POTCAR 路径>
```
`wizard.py` 自己给的参数**没有经过真机验证** —— 校验器能查语法与跨文件一致性，
但"这套参数能不能跑"只有真程序能回答（见 `conformance/README.md`）。

用法
----
    python scripts/wizard.py                      # 交互式
    python scripts/wizard.py --non-interactive \
        --goal slab-adsorption --poscar POSCAR --out ./calc \
        --elements "Pt O" --metal --outdir-desc "Pt(111) 上 O 吸附"
    python scripts/wizard.py --list-goals
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3


# ---------------------------------------------------------------------------
# "目标" 定义表：每一项目标给出它需要的参数与理由
# ---------------------------------------------------------------------------
class Goal:
    __slots__ = ("key", "title", "desc", "why", "needs", "params", "notes")

    def __init__(self, key, title, desc, why, needs, params, notes=()):
        self.key = key
        self.title = title
        self.desc = desc
        self.why = why
        self.needs = needs          # 需要用户额外提供什么
        self.params = params        # 参数模板
        self.notes = list(notes)


# ⚠️ 这些数值是**起点**，不是收敛值。每一条都在 README 里附上"为什么"与出处。
GOALS = {
    "bulk-static": Goal(
        "bulk-static", "块体/晶体 单点（静态）",
        "只算一个固定结构的能量与电子结构，不做任何弛豫。",
        "最常见的起点：先确认结构、磁态、收敛性都对了，再往下做。",
        [], {
            "NSW": 0, "IBRION": -1, "ISMEAR": 0, "SIGMA": 0.05,
        },
        ["单点计算不需要 EDIFFG（没有离子步）。",
         "如果体系是金属，把 ISMEAR 改成 1、SIGMA 改成 0.2。",
         "ISIF 在这里没有意义（NSW=0，没有离子步）—— 写了也不会生效。"]),
    "bulk-relax": Goal(
        "bulk-relax", "块体/晶体 几何优化（含晶胞）",
        "同时优化原子位置与晶胞形状/体积。",
        "块体没有表面，晶胞必须一起优化，否则应力没释放。",
        [], {
            "NSW": 200, "IBRION": 2, "ISIF": 3, "POTIM": 0.2,
            "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.05,
        },
        ["⚠️ ISIF=3 会改晶胞。这是块体该做的，但**slab 千万不要用 ISIF=3**"
         "（真空方向会被优化掉）。",
         "POTIM=0.2 偏保守；不收敛时可以调小到 0.1。"]),
    "slab-relax": Goal(
        "slab-relax", "表面/slab 几何优化（固定底部）",
        "只放开表层与吸附物，固定底部若干层。",
        "全部放开会让 slab 整体弛豫，表面能贡献会混进吸附能里。",
        ["POSCAR 里要有 Selective dynamics（T/F 标志）"], {
            "NSW": 300, "IBRION": 2, "ISIF": 2, "POTIM": 0.2,
            "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.05,
            "LDIPOL": ".TRUE.", "IDIPOL": 3,
        },
        ["ISIF=2 冻结晶胞 —— slab 的**默认**选择（真空方向不能动）。",
         "LDIPOL/IDIPOL：偶极修正。对**不对称** slab（一面吸附、一面裸）"
         "是需要的；对**对称** slab 可以去掉。",
         "⚠️ 官方明文：LDIPOL 用于带电体系 + 非立方超胞时 VASP 会直接停"
         "（见 references/playbook.md §5 的报错速查）。",
         "如果 slab 的原子数 > 30，加 LREAL = Auto（官方建议）。"]),
    "slab-adsorption": Goal(
        "slab-adsorption", "表面吸附能",
        "slab + 吸附物，做几何优化。",
        "吸附能是最常用的量；它要求**所有对比体系用完全相同的参数**，"
        "否则误差不会抵消。",
        ["POSCAR 里要有 Selective dynamics"], {
            "NSW": 300, "IBRION": 2, "ISIF": 2, "POTIM": 0.2,
            "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.05,
            "LDIPOL": ".TRUE.", "IDIPOL": 3, "LCHARG": ".TRUE.",
        },
        ["⚠️ **算吸附能必须把「干净 slab」和「孤立吸附物」用同一套参数各算一次**，"
         "否则 E_ads 里的系统误差不抵消。",
         "LCHARG=.TRUE. 留着电荷密度，方便后续做差分电荷。"]),
    "dos": Goal(
        "dos", "态密度 / PDOS / d 带中心",
        "在**已优化的结构**上做单点，输出 DOSCAR / PROCAR。",
        "DOS 必须来自**单点**（NSW=0）。用弛豫过程中的 DOS 是错的。",
        ["先用同一结构跑过一次几何优化"], {
            "NSW": 0, "IBRION": -1, "ISMEAR": -5, "SIGMA": 0.05,
            "LORBIT": 11, "NEDOS": 2000, "LCHARG": ".TRUE.",
        },
        ["ISMEAR=-5（四面体 + Blöchl）是 DOS 的常用选择。",
         "⚠️ **四面体方法必须用 Γ 居中的 k 点**（官方明文）——"
         "本向导生成的 KPOINTS 就是 Γ 居中。",
         "⚠️ **ISMEAR=-5 要求 NKPT ≥ 4**；k 点太少会报 "
         "`VERY BAD NEWS! ... Tetrahedron method fails for NKPT<4`。",
         "LORBIT=11 才会写出 PROCAR（分轨道投影）。",
         "判据：跑完后 grep 一次 `E-fermi`，结果应为 **1**；"
         "大于 1 说明这不是单点计算。"]),
    "freq": Goal(
        "freq", "频率 / 振动 / ZPE",
        "在**已充分优化**的结构上做有限差分频率。",
        "频率是能量的二阶导，几何不收敛就没有意义。",
        ["结构必须已经优化到力的判据以下"], {
            "NSW": 0, "IBRION": 5, "NFREE": 2, "POTIM": 0.015,
            "ISMEAR": 0, "SIGMA": 0.05, "EDIFF": 1e-7,
        },
        ["IBRION=5：有限差分，不做对称性约化（最稳，也最慢）。",
         "POTIM=0.015 Å 是官方对 IBRION=5 的**默认位移量**。",
         "⚠️ `Q1：OUTCAR 里的 Degree of freedom 是 3N 吗？`"
         "**不是** —— 它是 3×**放开**原子数。见 references/decide.md §13.1。",
         "只想算吸附物的 ZPE？把 slab 原子全标 F F F、吸附物标 T T T。"]),
    "band": Goal(
        "band", "能带结构（line 模式）",
        "沿高对称路径的非自洽能带。",
        "line 模式**不能**做自洽计算（官方 Warning）。",
        ["先用规则网格算出自洽电荷密度"], {
            "NSW": 0, "IBRION": -1, "ICHARG": 11, "NELM": 1,
            "ISMEAR": 0, "SIGMA": 0.05, "LORBIT": 11,
        },
        ["本轮生成的 KPOINTS 是**规则网格**，用来先做自洽。",
         "⚠️ 拿到 CHGCAR 之后，**把 KPOINTS 换成 line 模式**再跑第二轮，"
         "配 ICHARG=11 + NELM=1（本向导已经写好 ICHARG/NELM）。",
         "官方 Warning：line 模式生成的网格 not suitable for self-consistent"
         " calculations，必须配 ICHARG=11。"]),
    "molecule": Goal(
        "molecule", "孤立分子 / 团簇",
        "放在足够大的盒子里做单点或优化。",
        "孤立体系没有周期性，盒子要足够大以避免镜像相互作用。",
        ["POSCAR 的盒子要够大（建议各方向 ≥ 15 Å 真空）"], {
            "NSW": 100, "IBRION": 2, "ISIF": 2, "POTIM": 0.2,
            "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.01,
        },
        ["孤立分子的 k 点只需 Γ（1 1 1）。",
         "SIGMA 取小值（0.01）—— 分子有能隙，不需要大展宽。",
         "⚠️ 分子体系**一定要做自旋判断**：先跑一次 ISPIN=2 看最终磁矩是否为零。",
         "⚠️ 孤立体系是「力平衡」这个免费判据真正适用的场合："
         "跑完后用 `python scripts/compare.py <目录>` 看 |ΣF| 是否 ~0。"]),
    "neb": Goal(
        "neb", "过渡态：NEB / CI-NEB",
        "知道初态与末态，要整条最小能量路径与鞍点。",
        "CI-NEB 是唯一能给出**真实鞍点**的常用路线；Dimer 也能，"
        "但对初始方向敏感。",
        ["初态与末态的 POSCAR", "要插几个像（建议含端点 3–5 个点）"], {
            "NSW": 300, "IBRION": 2, "ISIF": 2, "POTIM": 0.0,
            "EDIFF": 1e-7, "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.05,
            "LCLIMB": ".TRUE.", "SPRING": -5.0, "IMAGES": 4,
        },
        ["⚠️ **本向导只生成 `INCAR`/`KPOINTS`/`POSCAR`（初态）+ README。**",
         "NEB 还需要 `00/`…`0N/` 各像的目录，每个里面一份 `POSCAR`。"
         "插点用你自己的工作流（`nebmake.pl` / `vaspkit` / `ASE` / IDPP 都行），"
         "**本向导不替你做插点**（那是工具链选择，不是参数问题）。",
         "`IMAGES` 在 `INCAR` 里是**可选**的：VASP 会按子目录数自动判定；"
         "写出来更明确，但**必须与实际的像数一致**。",
         "⚠️ 开 `LCLIMB` 会让最高能量的像爬到鞍点、**改变它的受力方式**；"
         "习惯做法是先用普通 NEB 收敛路径，**再**开 `LCLIMB` 精修。"
         "本向导默认开着，因为多数人的目的是拿鞍点 —— 若你要的是整条路径的形状，"
         "先把这行注释掉。",
         "⚠️ `POTIM` 对 `IBRION=2` 是步宽缩放；NEB 里更关键的是 `SPRING`"
         "（像之间的弹簧常数，单位 eV/Å²）。",
         "`EDIFF = 1e-7` 比常规更严 —— 能垒是两步能量之差，误差会叠加。",
         "⚠️ **过渡态的 `EDIFFG` 有争议**：讲义模板写 −0.03，"
         "而真实算例与讲义自述都是 −0.01。本向导取 −0.01（更严、且与真实算例一致），"
         "理由见 references/decide.md §12.3。"]),
    "dimer": Goal(
        "dimer", "过渡态：Dimer 方法",
        "只知道初态 + 一个粗略的反应方向。",
        "比 NEB 便宜（不用插点），但只能给**一个**鞍点，且对初始方向敏感。",
        ["初态 POSCAR", "一个 `MODECAR`（初始方向），或先跑一次频率得到它"], {
            "NSW": 300, "IBRION": 3, "ISIF": 2, "POTIM": 0.0,
            "EDIFF": 1e-7, "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.05,
            "ICHAIN": 2, "IOPT": 2,
        },
        ["⚠️ **`POTIM = 0` 在 `IBRION = 3`（Damped MD）下是官方默认值，"
         "完全合法**（官方 POTIM 页 Default 表）。"
         "真实算例 `day3/ts/dim` 就是这么写的。",
         "`ICHAIN = 2` 选 Dimer；`IOPT` 选优化器"
         "（1=LBFGS, 2=CG, 3=QM, 4=SD, 7=FIRE）。",
         "⚠️ **`ICHAIN`/`IOPT`/`LCLIMB` 不在官方 wiki 的 `Category:INCAR tag` 里**"
         "（它们没有独立页面）。本向导的用法来自真实算例，标 `[算例]`。",
         "⚠️ `MODECAR` 需要**单独提供**（本向导不生成）。"
         "没有它时可以先跑一次 `IBRION=5` 频率，把最软的那个模写成 `MODECAR`。",
         "⚠️ **自查**：IBRION=3/5 的 OUTCAR 里 `Degree of freedom` 是"
         "**3 × 放开原子数**，不是 3N（见 references/decide.md §13.1）。"]),
    "aimd": Goal(
        "aimd", "从头算分子动力学（AIMD / MD）",
        "让原子按牛顿方程跑起来，取系综平均。",
        "MD 能给出静态计算给不出的动态信息（扩散、振动谱、构象平均）。",
        ["结构（通常先在目标温度附近预平衡）", "时间步（`POTIM`，单位 fs）"], {
            "NSW": 2000, "IBRION": 0, "ISIF": 2, "POTIM": 1.0,
            "ISMEAR": 1, "SIGMA": 0.2, "NELM": 100, "NELMIN": 2,
            "LWAVE": ".FALSE.", "LCHARG": ".FALSE.",
        },
        ["⚠️ **`IBRION = 0` 时 `POTIM` 是必需项**，不给会"
         "`crash immediately after having started`（官方 POTIM 页明文）。"
         "单位是 **fs**。",
         "⚠️ **`EDIFFG` 对分子动力学不适用**（官方 EDIFFG 页 Warning）——"
         "所以本向导没给 `EDIFFG`，给了也是无效的。",
         "⚠️ **恒温器：本向导没有给 `SMASS`/`MDALGO`**，即默认是"
         "**微正则（NVE）** —— 能量守恒但温度会漂。"
         "要做 NVT 请自己加 `MDALGO` + `SMASS`；本 skill **没有**核实过"
         "具体取值的官方依据，故不替你选（见 references/decide.md 附录 B）。",
         "`POTIM = 1.0 fs` 是常见起点，但**必须自己测**："
         "太大则能量漂移、太小则采样不足。判据是**能量守恒性**。",
         "⚠️ `NSW = 2000` × `POTIM = 1 fs` 只有 2 ps。"
         "真实算例 `things to study/INCAR` 里写的是 `NSW = 2000/20000`。",
         "MD 的 `ISMEAR` 用 1（MP）—— 金属/高温下占据数会变。"]),
    "resume": Goal(
        "resume", "续算（从已有输出接着跑）",
        "上一次没跑完（墙钟到点、NSW 用尽），想接着算。",
        "续算比重跑省时间，但**最容易出的错是「读了不该读的文件」**。",
        ["上一次的 `CONTCAR`（拷成 `POSCAR`）",
         "可选：`WAVECAR`（有则更快）、`CHGCAR`"], {
            "ISTART": 1, "ICHARG": 1, "NSW": 300, "IBRION": 2, "ISIF": 2,
            "POTIM": 0.2, "EDIFFG": -0.01, "ISMEAR": 0, "SIGMA": 0.05,
            "LWAVE": ".TRUE.", "LCHARG": ".TRUE.",
        },
        ["⚠️ **续算前必须看上一轮有没有真的收敛**："
         "`python scripts/diagnose.py <上一次的目录>`。"
         "如果上一轮是 SCF 没收敛就停了，接着算只会继续错。",
         "`ISTART = 1` + `ICHARG = 1`：读 `WAVECAR` 与 `CHGCAR`。"
         "若没留 `WAVECAR`，用 `ISTART = 0` + `ICHARG = 2`（从头算电荷密度）。",
         "⚠️ **磁性体系注意**：官方 MAGMOM 页明文 —— 续算时 `MAGMOM`"
         "**只用来定对称性、不再设初值**；而且"
         "`if you remove the MAGMOM tag before restarting from a converged "
         "WAVECAR or CHGCAR, the magnetization is likely to be symmetrized away`"
         "（删掉反而会把磁矩对称化掉）。**所以续算时要把 `MAGMOM` 留着。**",
         "⚠️ 本向导生成的 `MAGMOM` 是**占位符** —— 续算时请照抄上一次 `INCAR` 里"
         "那一行，别重新猜。",
         "续算完请**把两次的离子步轨迹拼起来看**，而不是只看第二次。"]),
}

# 参数模板里"用户可能要改"的，连同理由一起写进 README
PARAM_DOC = {
    "SYSTEM": ("任意字符串", "只写进输出，便于你自己认。**不要**往里塞机器路径。"),
    "ENCUT": ("eV", "平面波截断。生成时按你的 POTCAR 的 max(ENMAX) 定，"
                    "但**必须自己做收敛测试**。见 decide.md §4。"),
    "ISMEAR": ("-5|-4|-1|0|1|2..", "展宽方式。绝缘体用 0，金属用 1，DOS 用 -5。"
                                   "**MP 展宽（>0）对绝缘体不安全**（官方明文）。"),
    "SIGMA": ("eV", "展宽宽度。默认 0.2；绝缘体 0.01–0.05。"),
    "EDIFF": ("eV", "电子步收敛判据。1E-6 常用；过渡态/高精度用 1E-7。"),
    "EDIFFG": ("eV/Å（负）或 eV（正）", "离子步收敛判据。**负值=力判据**（常用），"
                                       "正值=能量判据，0=只跑 NSW 步。"
                                       "⚠️ **对 MD 不适用**（官方 Warning）。"),
    "NSW": ("整数", "最大离子步数。0=单点。"),
    "IBRION": ("-1..8", "离子更新算法。-1=不动，2=CG，3=Damped MD，5/6=频率。"),
    "ISIF": ("0..7", "是否算应力、是否动晶胞。2=只动原子，3=连晶胞一起动。"
                     "⚠️ **slab 不要用 3**。"),
    "POTIM": ("fs 或无量纲", "MD 时间步 / 弛豫步宽 / 频率位移量。"
                            "**IBRION=0 时必须给**，否则程序立即崩。"),
    "ISPIN": ("1|2", "是否自旋极化。含磁性元素要用 2，并配 MAGMOM。"),
    "MAGMOM": ("实数列表", "逐原子初始磁矩。**最终磁态强依赖初值**（官方明文）。"),
    "LREAL": (".FALSE.|Auto", "投影算符在实空间还是倒空间。>30 原子官方建议 Auto；"
                              "高精度能量差建议 .FALSE. 复核。"),
    "LCHARG": (".TRUE.|.FALSE.", "是否写 CHGCAR。后续做差分电荷/DOS 要留下。"),
    "LWAVE": (".TRUE.|.FALSE.", "是否写 WAVECAR。续算要留；纯单点可以关掉省磁盘。"),
    "LORBIT": ("0|1|2|5|10|11|12", "是否写 PROCAR 及投影方式。11 常用。"),
    "NEDOS": ("整数", "DOSCAR 的能量点数。"),
    "NELM": ("整数", "最大电子步数。"),
    "NELMIN": ("整数", "最少电子步数。"),
    "ICHARG": ("0|1|2|4|10|11|12", "初始电荷密度的来源。11=从 CHGCAR 读且**不再更新**"
                                  "（非自洽/能带）。"),
    "LDIPOL": (".TRUE.|.FALSE.", "偶极修正。对不对称 slab 需要。"),
    "IDIPOL": ("1|2|3|4", "偶极修正的方向。3 = 沿 z。"),
    "NFREE": ("整数", "有限差分频率时每个自由度的位移次数。"),
    "IVDW": ("0|1|2|10|11|12|202|...", "vdW 修正（D3 类）。11=D3，12=D3-BJ。"),
    "LDAU": (".TRUE.|.FALSE.", "DFT+U 总开关。开了要配 LDAUTYPE/LDAUL/LDAUU。"),
    "PREC": ("Low|Medium|High|Normal|Accurate", "精度模式。Accurate 最稳最慢。"),
    "NCORE": ("整数", "并行粒度（每个轨道用几个核）。**与 KPAR 的乘积不要超过核数**。"),
    "KPAR": ("整数", "k 点并行分组数。"),
    "ISTART": ("0|1|2|3", "波函数从哪来。0=从头；1=读 WAVECAR；"
                          "2/3=按不同规则重用。"),
    "LCLIMB": (".TRUE.|.FALSE.", "CI-NEB 的 climbing image：让最高能量的像爬到鞍点。"
                                 "⚠️ 它会改变该像的受力方式。"),
    "IMAGES": ("整数", "NEB 的中间像数目。**必须与实际子目录数一致**"
                       "（VASP 也能自动判定）。"),
    "SPRING": ("eV/Å²（常为负）", "NEB 像之间的弹簧常数。"),
    "ICHAIN": ("0|1|2|3", "过渡态方法：0=CI-NEB，2=Dimer，3=Improved Dimer。"
                          "⚠️ 该标签**不在官方 wiki 的 INCAR tag 分类里**"
                          "（见 references/official/_keywords.tsv 的覆盖说明）。"),
    "IOPT": ("1|2|3|4|7", "过渡态的优化器：1=LBFGS，2=CG，3=QM，4=SD，7=FIRE。"
                          "同样**不在官方分类表里**。"),
}


def _ask(prompt: str, default: str = "", choices=None) -> str:
    """交互式问一个问题。**没有输入时用默认值**（便于管道化与自动化测试）。"""
    hint = ""
    if choices:
        hint = " [%s]" % "/".join(choices)
    if default:
        hint += "（默认 %s）" % default
    try:
        sys.stdout.write("%s%s: " % (prompt, hint))
        sys.stdout.flush()
        ans = sys.stdin.readline()
    except (EOFError, KeyboardInterrupt):
        ans = ""
    ans = (ans or "").strip()
    if not ans:
        return default
    if choices and ans not in choices:
        vc.warn("%r 不在候选里，仍按你输入的用。" % ans)
    return ans


def _write(path: str, text: str) -> None:
    """**无 BOM、LF 行尾**写出。这两条是硬要求（见 references/MAINTENANCE.md）。"""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def build_kpoints(goal: str, dim: str, mesh=None) -> str:
    """生成 KPOINTS。

    ⚠️ **一律生成 Γ 居中的规则网格**。理由：
    - 官方把规则网格列为生产计算的首选；
    - 四面体方法（`ISMEAR=-5`）**要求** Γ 居中；
    - fcc / hexagonal 晶格**只能**用 Γ 居中（官方明文，Monkhorst-Pack
      在偶数细分时会破坏对称性并可能直接报 IBZKPT 错误）。
      → 所以本向导**不提供** MP 网格选项，避免你踩这个坑。
    """
    if goal == "molecule":
        return ("Gamma 1x1x1 (isolated molecule)\n"
                "0\n"
                "Gamma\n"
                "   1   1   1\n"
                "0.0  0.0  0.0\n")
    if goal in ("band",):
        m = mesh or [0, 0, 0]
        return ("Regular mesh for the SCF step of a band-structure run\n"
                "0\n"
                "Gamma\n"
                "   %d   %d   %d\n"
                "0.0  0.0  0.0\n" % tuple(m))
    if mesh:
        m = mesh
    elif dim == "2d":
        m = [9, 9, 1]
    elif dim == "1d":
        m = [1, 9, 1]
    else:
        m = [6, 6, 6]
    return ("Gamma-centered regular mesh (recommended in VASP wiki: KPOINTS)\n"
            "0\n"
            "Gamma\n"
            "   %d   %d   %d\n"
            "0.0  0.0  0.0\n" % tuple(m))


README_TMPL = """# 这套 VASP 输入是什么

{title}

- 目标：**{goal_title}** —— {goal_desc}
- 为什么这么选：{goal_why}
- 生成时间/工具：由 `scripts/wizard.py` 生成（**未经过真机验证**）

---

## ⚠️ 用之前必须做三件事

### 1. 自己拼 `POTCAR`（本 skill 不提供）

`POTCAR` 受 VASP 许可保护，**不得再分发**，所以这里**故意没有**它。
按 `POSCAR` 第 6 行的**元素顺序**拼接：

```bash
# 顺序必须与 POSCAR 完全一致 —— VASP 按位置配对，不按元素名
cat <你本地的赝势目录>/<元素1>/POTCAR \\
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
{param_table}

### 这个目标特有的注意事项

{notes}

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
> 官方只对**新加的**标签标 `{{Available}}`；绝大多数标签根本**没标**。
> 正确措辞是「**官方未标注版本门槛**」。

总纲见 `references/VERSIONS.md`。

---

## 诚实声明

本文件由 `scripts/wizard.py` 的参数模板生成。模板里的每个数值都标了出处，
但**没有任何一条经过真机验证**（本机没有 VASP）。它们的定位是"安全的起点"，
不是"已验证的正确答案"。

**你的第一次计算就是对这个模板的验证。** 跑完之后，
请按 `conformance/README.md` 的说明把结果反馈回来 —— 那才是它变成可信知识的唯一途径。
"""


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="wizard.py",
        description="一问一答生成一套自洽的 VASP 输入（不生成 POTCAR、不提交作业）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="⚠️ 生成物**未经过真机验证**。生成后请跑 validate.py 再上机。",
    )
    ap.add_argument("--out", default="./vasp-calc", help="输出目录")
    ap.add_argument("--poscar", help="结构文件（POSCAR/CONTCAR/CIF 转出的 POSCAR）")
    ap.add_argument("--potcar", help="你本地的 POTCAR 路径（**只读头部**用于定 ENCUT，"
                                     "不复制、不写出）")
    ap.add_argument("--goal", help="计算目标（见 --list-goals）")
    ap.add_argument("--system", default="", help="SYSTEM 标签的内容（只用于标识）")
    ap.add_argument("--elements", default="",
                    help="元素符号，空格分隔，顺序必须与 POSCAR 一致")
    ap.add_argument("--metal", action="store_true", help="体系是金属（影响 ISMEAR/SIGMA）")
    ap.add_argument("--insulator", action="store_true",
                    help="体系是绝缘体/半导体（影响 ISMEAR/SIGMA）")
    ap.add_argument("--spin", action="store_true", help="需要自旋极化（ISPIN=2）")
    ap.add_argument("--dim", choices=["3d", "2d", "1d", "0d"], default="",
                    help="体系维度（影响 k 点）")
    ap.add_argument("--encut", type=float, default=None,
                    help="直接指定 ENCUT（不给则按 POTCAR 的 max(ENMAX) 或默认 400）")
    ap.add_argument("--non-interactive", action="store_true",
                    help="不提问，全部用命令行参数/默认值")
    ap.add_argument("--list-goals", action="store_true")
    args = ap.parse_args(argv)

    if args.list_goals:
        print("可用的计算目标：\n")
        for k, g in GOALS.items():
            print("  %-18s %s" % (k, g.title))
            print("      %s" % g.desc)
        print("\n用法：python scripts/wizard.py --goal <key> --out <目录> ...")
        return EXIT_OK

    interactive = not args.non_interactive and sys.stdin.isatty()

    # ---- 问目标 ----
    goal = args.goal
    if not goal and interactive:
        print("=" * 70)
        print("VASP 输入向导 —— 先确认你要算什么")
        print("=" * 70)
        for k, g in GOALS.items():
            print("  %-18s %s" % (k, g.title))
        print()
        goal = _ask("请选一个目标（输入前面的短名）", "bulk-static",
                    list(GOALS.keys()))
    if not goal:
        vc.die("没有指定计算目标。", EXIT_USAGE,
               "用 --goal <key>，或加 --list-goals 看有哪些目标。\n"
               "交互式：直接跑 python scripts/wizard.py（不要加 --non-interactive）")
    if goal not in GOALS:
        vc.die("不认识的目标：%s" % goal, EXIT_USAGE,
               "可用目标：%s" % ", ".join(GOALS.keys()))
    G = GOALS[goal]

    # ---- 问维度 / 金属性 / 自旋 ----
    dim = args.dim
    if not dim and interactive:
        dim = _ask("体系维度（3d 块体 / 2d 表面或二维 / 1d 纳米带 / 0d 分子）",
                   "2d" if goal.startswith(("slab", "dos")) and goal != "dos"
                   else "3d", ["3d", "2d", "1d", "0d"])
    dim = dim or ("2d" if goal.startswith("slab") else
                  ("0d" if goal == "molecule" else "3d"))

    metal = args.metal
    if not metal and not args.insulator and interactive:
        ans = _ask("体系是金属吗（y=金属 / n=绝缘体或半导体）", "n", ["y", "n"])
        metal = ans.lower().startswith("y")
    if metal and args.insulator:
        vc.warn("同时给了 --metal 与 --insulator，按金属处理。")

    spin = args.spin
    if not spin and interactive:
        ans = _ask("需要自旋极化吗（y/n；含 Fe/Co/Ni/Mn/Cr 等通常要）", "n",
                   ["y", "n"])
        spin = ans.lower().startswith("y")

    # ---- 问结构文件 ----
    poscar_src = args.poscar
    if not poscar_src and interactive:
        poscar_src = _ask("结构文件路径（POSCAR/CONTCAR）", "")
    poscar = None
    if poscar_src:
        if not os.path.exists(poscar_src):
            vc.die("结构文件不存在：%s" % poscar_src, EXIT_USER)
        poscar = vc.read_poscar(poscar_src)
    else:
        vc.warn("没有给结构文件 —— 这次**不会生成 POSCAR**，"
                "你需要自己放一个进去。")

    # ---- 定 ENCUT ----
    #
    # ⚠️ 这里用的是 `1.3 × max(ENMAX)`，而且**它确实是官方明文写过的值** ——
    #    见 `references/official/pages/ISIF.md:38`：
    #      `Generally, volume changes should be done only with an increased
    #       energy cutoff, e.g., ENCUT = 1.3×max(ENMAX), and PREC=High.`
    #    语境是**变胞/体积变化**（Pulay 应力对策）。
    #
    #    本项目在这件事上**错过两次**（CR-002 → CR-026）：
    #      第一次：把它说成"官方建议的常用做法"，但归因给了讲义（归因错）；
    #      第二次：改口说"官方从来没有说过倍数"（**断言过强** ——
    #              当时只查了 ENCUT.md / PREC.md，漏了 ISIF.md）。
    #    现在的口径：**变胞用 1.3×（官方例子）；定胞用 max(ENMAX) 就够。**
    #
    #    被官方标 deprecated 的是 `PREC=High` **这个开关**（官方说它
    #    "essentially only increases the energy cutoff by 30 %, which can also
    #    be achieved by just manually increasing ENCUT"）——
    #    所以我们**手工写 ENCUT**，而**不**去设 `PREC=High`。
    #
    #    注意：向导按目标自动选倍数 —— 变胞目标取 1.3×，定胞目标取 1.0×。
    encut = args.encut
    encut_reason = "用户用 --encut 直接指定"
    if encut is None and args.potcar:
        if not os.path.exists(args.potcar):
            vc.die("POTCAR 不存在：%s" % args.potcar, EXIT_USER)
        info = vc.parse_potcar_header(args.potcar)
        enmax = info.max_enmax()
        if enmax:
            # 这个目标会不会改变晶胞形状/体积？会 ⇒ 按官方抬高截断能。
            # ⚠️ `GOALS` 的值是 `Goal` **对象**，不是 dict ——
            #    早期写成了 `_g.get("params", {}).get(...)`，
            #    会在运行时抛 AttributeError（`Goal` 没有 `.get`）。
            #    见 CHANGELOG 的 CR-027。
            _g = GOALS.get(args.goal)
            _var_cell = str((_g.params if _g else {}).get("ISIF", "")) \
                in ("3", "7", "8")
            factor = 1.3 if _var_cell else 1.0
            encut = round(enmax * factor, 1)
            if _var_cell:
                encut_reason = (
                    "按你 POTCAR 的 max(ENMAX)=%.3f eV 取 **1.3 倍**(= %.1f eV)。"
                    "这是**官方明文给的值**，语境正是变胞（`[官方]` "
                    "references/official/pages/ISIF.md:38："
                    "`volume changes should be done only with an increased "
                    "energy cutoff, e.g., ENCUT = 1.3×max(ENMAX)`）—— "
                    "原因是变胞时 PAW 基组不跟着变，有 **Pulay 应力**。"
                    "⚠️ 但**它不代表收敛**：官方同时要求"
                    "`The convergence … should always be checked`。"
                    "**请自己按 references/decide.md §3.2 测一遍，"
                    "并把最终值显式写进 INCAR。**" % (enmax, encut))
            else:
                encut_reason = (
                    "按你 POTCAR 的 max(ENMAX)=%.3f eV 取 **1.0 倍**(= %.1f eV)。"
                    "这个目标是**定胞**计算（不改晶胞），所以**不需要**官方给变胞"
                    "场景的那个 1.3 倍抬高（见 `[官方]` references/official/"
                    "pages/ISIF.md:38 的语境）。⚠️ 官方仍要求"
                    "`The convergence … should always be checked` —— "
                    "**请自己测一遍 ENCUT 收敛**，并把最终值显式写进 INCAR。"
                    % (enmax, encut))
    if encut is None and interactive:
        encut = float(_ask("ENCUT（eV）", "400"))
        encut_reason = "用户输入"
    if encut is None:
        encut = 400.0
        encut_reason = ("默认 400 eV —— ⚠️ **这是一个猜测值**，"
                        "因为你既没给 --potcar 也没给 --encut。"
                        "请务必用你自己的 POTCAR 核对 max(ENMAX)！")

    # ---- 组装 INCAR ----
    params = dict(G.params)
    params["ENCUT"] = encut
    params["EDIFF"] = params.get("EDIFF", 1e-6)
    params["NELM"] = params.get("NELM", 300)
    params["NELMIN"] = params.get("NELMIN", 5)
    params["PREC"] = params.get("PREC", "Accurate")
    params["LREAL"] = params.get("LREAL",
                                 "Auto" if (poscar and poscar.nions > 30)
                                 else ".FALSE.")
    params["LWAVE"] = params.get("LWAVE", ".FALSE.")
    params["LCHARG"] = params.get("LCHARG", ".TRUE.")

    if metal:
        params["ISMEAR"] = 1
        params["SIGMA"] = 0.2
    elif goal == "dos":
        params["ISMEAR"] = -5
        params["SIGMA"] = 0.05
    elif goal == "molecule":
        params["ISMEAR"] = 0
        params["SIGMA"] = 0.01
    else:
        params.setdefault("ISMEAR", 0)
        params.setdefault("SIGMA", 0.05)

    if spin or (poscar and any(
            vc.Elements.z(s) in (24, 25, 26, 27, 28, 29, 42, 44, 45, 46, 57, 58,
                                 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70,
                                 71, 92)
            for s in (poscar.symbols or []))):
        params["ISPIN"] = 2
        params["MAGMOM"] = "<<<请填写：NIONS 个初值，见 README>>>"
        if not spin:
            vc.warn("POSCAR 里有常见磁性元素，已自动加上 ISPIN=2。"
                    "**必须**把 MAGMOM 的占位符换成真实初值。")

    system = args.system or ("%s %s" % (G.key, poscar.formula() if poscar else ""))

    incar_lines = ["#### 由 scripts/wizard.py 生成 —— 数值是起点，不是收敛值 ####",
                   "# 生成后请跑：python scripts/validate.py . --potcar ./POTCAR",
                   "SYSTEM = %s" % system,
                   "",
                   "#### 起始参数 I/O ####",
                   "ISTART = 0",
                   "ICHARG = %s" % params.get("ICHARG", 2),
                   "LWAVE  = %s" % params["LWAVE"],
                   "LCHARG = %s" % params["LCHARG"],
                   ""]
    if "LORBIT" in params:
        incar_lines.append("LORBIT = %s" % params["LORBIT"])
    if "NEDOS" in params:
        incar_lines.append("NEDOS  = %s" % params["NEDOS"])
    incar_lines += ["", "#### 电子步 ####",
                    "ENCUT  = %.1f" % float(params["ENCUT"]),
                    "PREC   = %s" % params["PREC"],
                    "EDIFF  = %s" % ("%g" % float(params["EDIFF"])),
                    "NELM   = %s" % params["NELM"],
                    "NELMIN = %s" % params["NELMIN"],
                    "ISMEAR = %s" % params["ISMEAR"],
                    "SIGMA  = %s" % params["SIGMA"],
                    "LREAL  = %s" % params["LREAL"],
                    ""]
    if params.get("ISPIN"):
        incar_lines += ["#### 自旋 ####", "ISPIN = %s" % params["ISPIN"]]
        if params.get("MAGMOM"):
            incar_lines.append("MAGMOM = %s" % params["MAGMOM"])
        incar_lines.append("")
    incar_lines += ["#### 离子步 ####",
                    "NSW    = %s" % params.get("NSW", 0),
                    "IBRION = %s" % params.get("IBRION", -1)]
    if "ISIF" in params:
        incar_lines.append("ISIF   = %s" % params["ISIF"])
    if "POTIM" in params:
        potim = params["POTIM"]
        incar_lines.append("POTIM  = %s%s" % (
            potim,
            "   # IBRION=3 时 0 是官方默认值；IBRION=0(MD) 时这是时间步(fs)，必需"
            if float(potim) == 0 else ""))
    if "EDIFFG" in params:
        incar_lines.append("EDIFFG = %s" % params["EDIFFG"])
    if "NFREE" in params:
        incar_lines.append("NFREE  = %s" % params["NFREE"])
    incar_lines.append("")
    # 过渡态专用标签：单独一段，并注明它们的证据级别
    ts_tags = [k for k in ("ICHAIN", "IOPT", "IMAGES", "SPRING", "LCLIMB")
               if k in params]
    if ts_tags:
        incar_lines += [
            "#### 过渡态专用 ####",
            "# ⚠️ ICHAIN / IOPT / LCLIMB 不在官方 wiki 的 Category:INCAR tag 里",
            "#    （没有独立页面）。下面这些取值来自真实算例，标 [算例]。",
            "#    见 references/decide.md §12 与 references/official/_keywords.tsv。"]
        for k in ts_tags:
            incar_lines.append("%-6s = %s" % (k, params[k]))
        incar_lines.append("")
    if params.get("LDIPOL"):
        incar_lines += ["#### 偶极修正（不对称 slab 需要）####",
                        "LDIPOL = %s" % params["LDIPOL"],
                        "IDIPOL = %s" % params["IDIPOL"], ""]
    if params.get("LDAU"):
        incar_lines += ["#### DFT+U ####",
                        "LDAU     = .TRUE.",
                        "LDAUTYPE = 2",
                        "LDAUL    = <<<请填写：每个元素一个值，-1 表示不加 U>>>",
                        "LDAUU    = <<<请填写：每个元素一个值>>>",
                        "LDAUJ    = <<<请填写>>>",
                        "LMAXMIX  = 4   # d 电子用 4，f 电子用 6（官方明文）", ""]
    if params.get("IVDW"):
        incar_lines += ["#### vdW ####", "IVDW = %s" % params["IVDW"], ""]
    incar_lines += ["#### 并行（**与站点相关，请自己定**）####",
                    "# NCORE = <<<请填写>>>",
                    "# KPAR  = <<<请填写>>>",
                    ""]

    # ---- 写出 ----
    out = args.out
    os.makedirs(out, exist_ok=True)
    _write(os.path.join(out, "INCAR"), "\n".join(incar_lines))

    _write(os.path.join(out, "KPOINTS"), build_kpoints(goal, dim))

    if poscar_src:
        text = vc.read_text(poscar_src)
        _write(os.path.join(out, "POSCAR"), text)
    else:
        _write(os.path.join(out, "POSCAR"),
               "# <<<请把结构粘到这里>>>\n"
               "# 最少 8 行：注释 / scale / 3 行晶格 / 元素(可选) / 数目 / "
               "Direct|Cartesian / 坐标\n")

    _write(os.path.join(out, "POTCAR.README"), """\
# 为什么这里没有 POTCAR

`POTCAR` 受 VASP 许可保护，**不得再分发**。所以本 skill **不会**替你生成或
复制它 —— 它只能**校验**你已经有的那个。

## 怎么拼

```bash
cat <赝势目录>/<元素1>/POTCAR \\
    <赝势目录>/<元素2>/POTCAR > POTCAR
```

**顺序必须与 POSCAR 第 6 行的元素顺序完全一致。**
VASP 是**按位置**把 POTCAR 的数据集配给 POSCAR 的元素的，不按元素名匹配。
顺序错了，每个原子的赝势都是错的，而且**程序不会报错**。

## 拼完立刻校验

```bash
python scripts/validate.py . --potcar ./POTCAR
```

它会核对：
- POSCAR 元素顺序 vs POTCAR 的 TITEL 顺序（`XSPECIES.elements`）
- 数据集个数 vs 元素种类数（`XSPECIES.counts`）
- `ENCUT` vs POTCAR 的 `ENMAX`（`XENCUT.enmax`）
- `MAGMOM` 个数 vs 原子数（`XMAGMOM.count`）

## 也可以用它来定 ENCUT

```bash
python scripts/wizard.py --potcar ./POTCAR ...   # 会按 max(ENMAX)×1.3 定 ENCUT
```

本工具**只读** POTCAR 头部的几个数字（`TITEL`/`ENMAX`/`ZVAL` 等），
**不复制、不缓存、不写出**任何 POTCAR 内容。
""")

    _write(os.path.join(out, "submit.sh"), """\
#!/bin/bash
# ⚠️ 这个脚本里**所有** <<<...>>> 都是**站点相关信息**，必须你自己填。
#    本 skill 故意不猜这些 —— 猜错一次就是白跑一趟，
#    而且把它写进通用文档会把下一个用的人带沟里。
#    （理由见 references/MAINTENANCE.md「机器细节不进，结论进」）

#SBATCH -J <<<作业名>>>
#SBATCH -N <<<节点数>>>
#SBATCH -n <<<总核数>>>
#SBATCH -p <<<队列名>>>
#SBATCH -t <<<时限，如 24:00:00>>>

# <<<如果集群需要 module load，写在这里>>>
# module load <<<...>>>

cd "$SLURM_SUBMIT_DIR" || exit 1

# ⚠️ 把 <VASP 可执行文件> 换成你自己编译出来的那个的**绝对路径**。
#    本 skill 不猜任何路径。
srun -n <<<总核数>>> <VASP 可执行文件> > LOG 2>&1

echo "退出码：$?"
""")

    # README 的参数表
    rows = []
    for k in sorted(params.keys()):
        val = params[k]
        doc = PARAM_DOC.get(k, ("", "（本向导未收录该参数的说明）"))
        reason = ""
        if k == "ENCUT":
            reason = encut_reason
        rows.append("| `%s` | `%s` | %s |" % (k, val, reason or doc[1]))
    rows.append("| `POTCAR` | **不生成** | 受许可保护，不得再分发。见 `POTCAR.README` |")
    rows.append("| `KPOINTS` | Γ 居中规则网格 | 四面体方法必须 Γ 居中；"
                "fcc/hexagonal 也只能用 Γ 居中（官方明文） |")
    notes = "\n".join("- " + n for n in G.notes) or "- （本目标没有额外注意事项）"
    if poscar is None:
        notes += "\n- ⚠️ **这次没有生成 POSCAR**（你没给结构文件）—— 请自己放一个进去。"

    _write(os.path.join(out, "README.md"), README_TMPL.format(
        title="%s%s" % (system, ("（%s）" % poscar.formula()) if poscar else ""),
        goal_title=G.title, goal_desc=G.desc, goal_why=G.why,
        param_table="\n".join(rows), notes=notes))

    print()
    print("=" * 70)
    print("已生成：%s" % os.path.abspath(out))
    print("=" * 70)
    for name in ("INCAR", "KPOINTS", "POSCAR", "POTCAR.README", "README.md",
                 "submit.sh"):
        p = os.path.join(out, name)
        print("  %-16s %s" % (name, "已写出" if os.path.exists(p) else "（缺）"))
    print()
    print("下一步（**按顺序做**）：")
    print("  1. 拼 POTCAR（见 POTCAR.README）")
    print("  2. 改 submit.sh 里的所有 <<<请填写>>>")
    if params.get("MAGMOM", "").startswith("<<<"):
        print("  3. ⚠️ 填 INCAR 里的 MAGMOM 占位符（**现在它是无效的**）")
    print("  4. python scripts/validate.py %s --potcar %s/POTCAR"
          % (out, out))
    print("  5. 先跑一个极小算例（NSW=2, NELM=20）确认能起来")
    print("  6. 正式跑；跑完 python scripts/compare.py %s" % out)
    print()
    print("⚠️ 本向导给的数值是**起点**，不是收敛值。收敛测试见 README.md。")
    print("⚠️ 生成物**未经过真机验证**（本机没有 VASP）——")
    print("   你的第一次计算就是它的验证。")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
