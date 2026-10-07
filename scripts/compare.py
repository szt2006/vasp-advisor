#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""compare.py —— 物理不变量与跨文件一致性检查（**零依赖**）

为什么需要它（**这是本 skill 里唯一能抓"算得不对"的离线工具**）
============================================================
`validate.py` 查的是**输入**（语法/归属/值域/跨文件一致性）。
它抓不到"输入完全合法、程序不报错、但结果错了"。

有一类判据**不需要参照值**，却能把这类缺陷抓出来 —— 就是**物理不变量**。
本工具实现三个（按"值不值得做"排序）：

| # | 不变量 | 成本 | 抓什么 |
|---|---|---|---|
| ① | **力平衡** `ΣF`（孤立体系应严格为 0） | **零**（输出里本来就有） | 力/对称性处理错误。几何优化的收敛判据建立在力上，力错了 ⇒ 优化停错位置 |
| ② | **能量自洽**：`OSZICAR` 的最后 `E0` == `OUTCAR` 的最后 `energy(sigma->0)` | 零 | 解析错文件/读了中间步/文件被截断 |
| ③ | **跨文件一致**：`OUTCAR`/`vasprun.xml`/`POSCAR` 的原子数、`ENCUT` 是否一致 | 零 | "跑的不是这套输入"（最常见的低级但致命的错误） |

⚠️ **诚实的能力边界（必读）**
----------------------------
1. **本工具没有在真实反例上标定过阈值。** 原因很直接：**本机没有 VASP**，
   无法构造"已知错误的计算"来做正例/反例对照（§4.2 的注入测试要求）。
   所以阈值部分一律标 `[未标定]`，并且**默认给 WARN 而不是 ERROR**。
   要把它变成 ERROR 级判据，必须先用真程序标定 —— 见 `conformance/README.md`。
2. **力平衡只对孤立体系成立**。有固定原子/约束/外场的体系里 `ΣF ≠ 0` 是正常的。
   本工具靠 `POSCAR` 的 `Selective dynamics` 判断"有没有固定原子"，
   但**这只是一个启发式**：它判断不了"整个体系是否孤立"。
3. **它查不出"能量面的形状错"**。参照 CP2K 的实测教训：
   力-能量自洽检验在"能量差 12 Ha"的缺陷下残差只有 0.067%、会判通过 ——
   因为解析力是那个**错误**能量面的**正确**导数。
   本工具做的是"平衡/自洽"检查，不是"正确性"证明。

退出码
------
0 = 没发现问题 · 1 = 文件问题 · 2 = 用法错误 · 3 = 缺 OUTCAR 等必要文件
4 = 有 ERROR 级问题 · 5 = 只有 WARN/未标定项（`--strict` 时提升为 4）

用法
----
    python scripts/compare.py <算例目录>
    python scripts/compare.py <算例目录> --strict
    python scripts/compare.py <算例目录> --json
    python scripts/compare.py --list-checks
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3
EXIT_ERROR, EXIT_WARN = 4, 5

CHECKS = [
    ("E.selfconsistent",
     "OSZICAR 的最后 E0 == OUTCAR 的最后 energy(sigma->0)（能量自洽）"),
    ("X.nions_consistent",
     "POSCAR 原子数 == OUTCAR 的 NIONS == vasprun.xml 的原子数"),
    ("X.encut_consistent",
     "INCAR 的 ENCUT == OUTCAR 实际用的 ENCUT"),
    ("X.version_recorded", "解析结果带上程序版本号（防跨版本静默失效）"),
    ("F.balance_isolated",
     "力平衡 |ΣF|（孤立体系应为 0；**阈值未标定**）"),
    ("F.balance_relative",
     "|ΣF| 与最大单原子受力之比（**阈值未标定**）"),
    ("F.drift_reported", "报告 OUTCAR 自带的 total drift（免费的自查量）"),
    ("E.ionic_history", "离子步能量序列是否单调下降/是否收敛"),
    ("C.isif3_cell", "ISIF=3 时晶胞体积是否真的变了（核对 OPTCELL/冻结是否生效）"),
    ("C.freq_dof", "IBRION=5 时自由度应为 3×放开原子数（不是 3N）"),
]

UNCHECKED = [
    "力 = −能量对坐标的导数（F = −dE/dx）：需要**额外跑几个单点**，本工具不替你做。"
    "做法见 decide.md §14 与 conformance/README.md",
    "整体平移不变性：需要额外跑一个单点",
    "对称性是否被磁性/缺陷正确打破：需要真程序",
    "能量面的**形状**是否正确（本工具只查自洽，不查正确）",
    "绝对能量是否正确（离线无法判断 —— 没有参照值）",
]


def _f(x, nd=6):
    return "None" if x is None else ("%.*f" % (nd, x))


def gather(inp: dict) -> dict:
    """把一次算例的全部可读信息收成一个字典（供各项检查共用）。"""
    d = {"dir": inp["dir"], "notes": [], "errors": [], "warns": [], "infos": []}
    d["has_outcar"] = bool(inp["OUTCAR"])
    d["version"] = vc.outcar_version(inp["OUTCAR"]) if inp["OUTCAR"] else ""
    d["nions_outcar"] = vc.outcar_nions(inp["OUTCAR"]) if inp["OUTCAR"] else None
    d["encut_outcar"] = vc.outcar_encut(inp["OUTCAR"]) if inp["OUTCAR"] else None
    d["steps"] = vc.outcar_ionic_steps(inp["OUTCAR"]) if inp["OUTCAR"] else []
    d["oszicar"] = (vc.oszicar_last_energy(inp["OSZICAR"])
                    if inp["OSZICAR"] else (None, 0))
    d["poscar"] = vc.read_poscar(inp["POSCAR"]) if inp["POSCAR"] else None
    d["incar"] = vc.read_incar(inp["INCAR"]) if inp["INCAR"] else None
    d["vmeta"] = vc.vasprun_meta(inp["vasprun"]) if inp["vasprun"] else {}
    return d


def check(d: dict) -> None:
    steps = d["steps"]
    # ⚠️ **用"最后一个有力表的离子步"，不是"最后一个离子步"。**
    # 实测：弛豫算例（如 day1/fe2o3）的 OUTCAR 会在所有离子步之后再打印一个
    # 只有能量的收尾块（`FREE ENERGIE` 而没有 `TOTAL-FORCE`）。
    # 早期版本取 `steps[-1]`，于是在所有**弛豫**算例上都报
    # "没有解析到力表" —— 而力明明都在前面的离子步里。已记入 CHANGELOG 更正记录。
    last = None
    for st in reversed(steps):
        if st.forces:
            last = st
            break
    any_forces = last is not None

    # ---- ① 能量自洽 ----
    e0_osz, n_ionic = d["oszicar"]
    e_out = None
    for st in reversed(steps):
        if st.energy_sigma0 is not None:
            e_out = st.energy_sigma0
            break
    d["e0_oszicar"] = e0_osz
    d["e0_outcar"] = e_out
    d["n_ionic_oszicar"] = n_ionic
    if e0_osz is not None and e_out is not None:
        diff = abs(e0_osz - e_out)
        d["e0_diff"] = diff
        # 1e-5 eV：两个文件打印精度不同（OSZICAR 用 E 格式 8 位有效数字），
        # 所以不能要求逐位相同。这个容差是**按打印精度**定的，不是物理判据。
        if diff > 1e-4:
            d["errors"].append(
                ("E.selfconsistent",
                 "OSZICAR 的最后 E0 = %s，而 OUTCAR 的最后 energy(sigma->0) = %s，"
                 "差 %s eV" % (_f(e0_osz), _f(e_out), _f(diff)),
                 "两个文件说的是同一次计算的同一个量，正常情况只该差打印精度"
                 "（≤1e-5 eV 量级）。差得多通常意味着：算例被中断过、"
                 "OSZICAR 是续算拼起来的、或者你读到的不是同一次计算。",
                 "确认 OSZICAR 与 OUTCAR 来自同一次运行；"
                 "若确实做过续算，以 OUTCAR 为准（它记录了完整历史）。",
                 "[实测] 容差 1e-4 eV 是按两个文件的打印精度定的"))
        elif diff > 1e-5:
            d["warns"].append(
                ("E.selfconsistent",
                 "OSZICAR 与 OUTCAR 的能量差 %s eV，略大于打印精度" % _f(diff),
                 "可能是续算拼接或打印截断。",
                 "若这个算例的结果要进论文，建议核对 OUTCAR 的完整历史。",
                 "[实测]"))
        else:
            d["infos"].append(("E.selfconsistent",
                               "OSZICAR 与 OUTCAR 的能量一致（差 %s eV）" % _f(diff),
                               "", "", ""))

    # ---- ② 原子数一致 ----
    vals = {}
    if d["poscar"]:
        vals["POSCAR"] = d["poscar"].nions
    if d["nions_outcar"]:
        vals["OUTCAR"] = d["nions_outcar"]
    vm_n = d["vmeta"].get("NIONS")
    if vm_n:
        try:
            vals["vasprun.xml"] = int(vm_n)
        except ValueError:
            pass
    d["nions_seen"] = vals
    if len(set(vals.values())) > 1:
        d["errors"].append(
            ("X.nions_consistent",
             "原子数在各文件里不一致：%s"
             % ", ".join("%s=%d" % kv for kv in sorted(vals.items())),
             "这几乎总意味着 **实际跑的计算和你现在看到的 POSCAR 不是同一套**。"
             "最常见的原因：跑完后把 POSCAR 换成了别的东西（例如把 CONTCAR 拷成 "
             "POSCAR 却没重跑），或者目录里混了两次计算的文件。",
             "确认这个目录里**哪些文件属于同一次运行**。"
             "OUTCAR 是唯一带完整历史的自证文件，以它为准。",
             "[实测] 这类不一致在真实算例目录里确实存在（见 CHANGELOG）"))

    # ---- ③ ENCUT 一致 ----
    enc_incar = d["incar"].get_float("ENCUT") if d["incar"] else None
    enc_outcar = d["encut_outcar"]
    d["encut_incar"] = enc_incar
    if enc_incar is not None and enc_outcar is not None:
        if abs(enc_incar - enc_outcar) > 0.5:
            d["errors"].append(
                ("X.encut_consistent",
                 "INCAR 写 ENCUT = %s，但 OUTCAR 实际用的是 %s eV"
                 % (_f(enc_incar, 2), _f(enc_outcar, 2)),
                 "OUTCAR 是程序自己的回显，一定是对的。两者不符说明"
                 "**这个目录里的 INCAR 不是那次运行用的那个**"
                 "（被改过、或者属于另一次计算）。",
                 "用 OUTCAR 里回显的参数作为「这次计算实际用了什么」的唯一依据。",
                 "[官方] INCAR 页：VASP writes its interpretation of the data in "
                 "the INCAR file to the OUTCAR file"))
        else:
            d["infos"].append(("X.encut_consistent",
                               "INCAR 与 OUTCAR 的 ENCUT 一致（%s eV）"
                               % _f(enc_outcar, 2), "", "", ""))
    elif enc_incar is None and enc_outcar is not None:
        d["infos"].append(
            ("X.encut_consistent",
             "INCAR 没写 ENCUT；OUTCAR 显示实际用了 %s eV（取自 POTCAR 的 ENMAX）"
             % _f(enc_outcar, 2),
             "这正是「不写 ENCUT 时结果静默依赖 POTCAR」的体现。",
             "建议把它显式写进 INCAR，让这次计算可复现。", "[官方] POTCAR 页"))

    # ---- ④ 版本号 ----
    if d["version"]:
        d["infos"].append(("X.version_recorded", "程序版本：%s" % d["version"],
                           "", "", ""))
    elif not d.get("has_outcar"):
        # 只有 OSZICAR、没有 OUTCAR —— 版本号**本来就不在** OSZICAR 里。
        # 这不是缺陷，如实说明它让哪些检查变弱了即可。
        d["infos"].append(
            ("X.version_recorded",
             "本目录只有 OSZICAR，没有 OUTCAR —— 无法记录程序版本号",
             "OSZICAR 只记每一步的能量与收敛信息，**不含版本号**。"
             "缺少版本号意味着：这次解析的结论在换了 VASP 版本之后，"
             "无法判断「解析不到」是因为格式变了还是算例本身没有这项。"
             "另外，只有 OSZICAR 时**力表、`ENCUT` 实际值、`total drift`、"
             "离子步历史之外的多数检查都无法执行**。",
             "若可能，保留 OUTCAR（哪怕压缩）。它是唯一带完整历史的自证文件。",
             "[经验]"))
    else:
        d["warns"].append(
            ("X.version_recorded", "OUTCAR 里读不到 VASP 版本号",
             "输出格式会**跨版本漂移**。不带版本号的解析结论，"
             "在换版本之后无法判断「解析不到」是因为格式变了还是算例本身没有这项。",
             "确认 OUTCAR 完整（版本号在第一行）；若文件被截断，解析结果不可信。",
             "[经验]"))

    # ---- ⑤⑥⑦ 力平衡 ----
    if not last:
        # 两种情况要分开报，别混成一条：
        #  (a) 有 OUTCAR 但里面没有力表 ⇒ 值得提醒
        #      （可能是没请求力、文件被截断、或版本不打印 TOTAL-FORCE）
        #  (b) 根本没有 OUTCAR ⇒ 力平衡**本来就没法查**，如实说明即可，不是缺陷
        if d.get("has_outcar"):
            d["warns"].append(
                ("F.balance_isolated",
                 "OUTCAR 里没有解析到力表 —— 力平衡检查**未执行**",
                 "可能原因：这是一次非自洽/仅电子的计算（没有请求力）、"
                 "OUTCAR 被截断、或这个 VASP 版本不打印 TOTAL-FORCE。",
                 "确认你是否需要力：几何优化/频率/MD 才需要力。"
                 "若需要，检查 OUTCAR 里是否有 `POSITION  TOTAL-FORCE` 段。",
                 "[经验]"))
        else:
            d["infos"].append(
                ("F.balance_isolated",
                 "本目录没有 OUTCAR，只有 OSZICAR —— 力平衡检查**无法执行**"
                 "（不是「没通过」，是「没查」）",
                 "`OSZICAR` 只记每一步的能量与收敛信息，**不含力表**。"
                 "所以力平衡、`total drift`、`ENCUT` 实际值、离子步力的历史"
                 "这些量都只能从 `OUTCAR` 拿。",
                 "若你关心「力算得对不对」，请保留 `OUTCAR`（压缩成 `.gz` 也可以，"
                 "本工具能直接读 `.gz`）。",
                 "[经验]"))
        # 其余与力无关的检查继续做
        _check_history_and_cell(d)
        return
    has_fixed = bool(d["poscar"] and d["poscar"].selective and
                     d["poscar"].lattice)
    d["has_selective"] = has_fixed
    if last.forces:
        sv = last.sum_forces_vec()
        d["sum_force"] = sv
        d["max_force"] = last.max_force
        d["total_drift"] = last.total_drift
        if sv:
            mag = sv[3]
            d["sum_force_mag"] = mag
            if has_fixed:
                # 有固定原子 ⇒ ΣF ≠ 0 正常，改用相对判据
                if last.max_force and last.max_force > 0:
                    ratio = mag / last.max_force
                    d["drift_ratio"] = ratio
                    if ratio > 0.5:
                        d["warns"].append(
                            ("F.balance_relative",
                             "有 Selective dynamics（存在固定/放开的区分），"
                             "|ΣF| = %s eV/Å，最大单原子受力 = %s eV/Å，"
                             "比值 = %.3f" % (_f(mag), _f(last.max_force), ratio),
                             "含固定原子的体系里 ΣF ≠ 0 是**正常的**"
                             "（约束力不体现在 TOTAL-FORCE 里）。"
                             "但比值偏大时值得看一眼：可能固定层没固定住、"
                             "或者放开/固定的标志写反了。",
                             "核对 POSCAR 的 Selective dynamics 标志是否与你的本意一致；"
                             "**不要**用这个量判「算得对不对」。",
                             "[经验] 阈值 0.5 **未标定** —— 本机没有 VASP，"
                             "无法构造反例来定这个数"))
            else:
                # 无固定原子 ⇒ 应该是孤立体系，ΣF 应接近 0
                if last.max_force and last.max_force > 0:
                    ratio = mag / last.max_force
                    d["drift_ratio"] = ratio
                if last.max_force and mag > 1e-3 * max(last.max_force, 1e-12):
                    d["warns"].append(
                        ("F.balance_isolated",
                         "**没有** Selective dynamics（按孤立体系处理），"
                         "但 |ΣF| = %s eV/Å（最大单原子受力 %s eV/Å）"
                         % (_f(mag), _f(last.max_force)),
                         "孤立体系的受力之和必须为零（牛顿第三定律）。"
                         "偏大意味着力的计算或对称性处理有问题 —— 而"
                         "**几何优化的收敛判据正是建立在力上的**，"
                         "力错了 ⇒ 优化会停在一个错误的位置，且**不报错**。",
                         "① 检查 POSCAR 的对称性与元素顺序；"
                         "② 检查 OUTCAR 里 total drift 是否同样偏大；"
                         "③ 与本工具给出的「未标定」说明一起看："
                         "**这条判据的阈值本 skill 没有标定过**，"
                         "请自己用一个「已知正确的极小算例」对照（见 conformance/）。",
                         "[经验] 判据来源：牛顿第三定律（不是官方明文）；"
                         "⚠️ **阈值未标定**"))
                elif mag > 0:
                    d["infos"].append(
                        ("F.balance_isolated",
                         "孤立体系力平衡 |ΣF| = %s eV/Å（相对最大受力 %.2e）"
                         % (_f(mag), (mag / last.max_force)
                            if last.max_force else float("nan")),
                         "", "", "[实测]"))
        if last.total_drift:
            d["infos"].append(
                ("F.drift_reported",
                 "OUTCAR 自带 total drift = (%.6f, %.6f, %.6f) eV/Å"
                 % last.total_drift,
                 "这是**免费**的自查量，不需要任何额外计算。",
                 "把它和你体系里最大单原子受力比一比，而不是只看绝对值。",
                 "[实测]"))
    # ---- ⑧⑨⑩ 与力无关的部分单独成函数，便于在"没有力"时也能跑 ----
    _check_history_and_cell(d)


def _check_history_and_cell(d: dict) -> None:
    """离子步历史 / ISIF=3 晶胞变化 / 频率自由度语义。

    这三项都不需要力表，所以即使 OUTCAR 里没有力也照跑。
    """
    steps = d["steps"]
    e0_osz, n_ionic = d["oszicar"]

    # ---- ⑧ 离子步能量历史 ----
    energies = [s.energy_sigma0 for s in steps if s.energy_sigma0 is not None]
    d["n_ionic_outcar"] = len(steps)
    d["energies"] = energies[:5] + (["..."] if len(energies) > 10 else []) \
        + energies[-5:] if len(energies) > 10 else energies
    if len(energies) >= 3:
        rising = sum(1 for i in range(1, len(energies))
                     if energies[i] > energies[i - 1] + 1e-6)
        d["n_rising_steps"] = rising
        if rising > len(energies) // 2:
            d["warns"].append(
                ("E.ionic_history",
                 "%d 个离子步里有 %d 步能量**上升**" % (len(energies), rising),
                 "能量上升本身**不一定是错**（CG/准牛顿在非凸面上会暂时上升，"
                 "MD 更是正常）。但如果它持续上升，通常是：初始结构太差、"
                 "`POTIM` 太大、或者 SCF 没收敛就往下走了。",
                 "看 OUTCAR 里每步的力是否在下降；若力也不降，"
                 "把 `POTIM` 调小（例如 0.2 → 0.1）再试。",
                 "[经验] 这不是判据，只是提示"))
    if d["n_ionic_outcar"] and n_ionic:
        if d["n_ionic_outcar"] != n_ionic:
            d["warns"].append(
                ("E.ionic_history",
                 "OUTCAR 解析到 %d 个离子步，OSZICAR 有 %d 个"
                 % (d["n_ionic_outcar"], n_ionic),
                 "两个文件对离子步的计数应该一致。不符可能是"
                 "OSZICAR 被截断/续算拼接，或者其中一边的格式与解析器不匹配。",
                 "以 OUTCAR 为准；若差异大，检查文件是否完整。",
                 "[经验]"))

    # ---- ⑨ ISIF=3 的晶胞变化 ----
    #
    # ⚠️ 只在**真的做了离子步**时才检查这一项。
    # 实测反例：`things to study/al2o3` 里 `ISIF = 3` 但 `NSW = 0`
    # —— 这是一次**单点**计算，不会有任何离子步，晶胞当然不变。
    # 早期版本在这里报 WARN，属于假阳性（已记入 CHANGELOG 更正记录）。
    # 判据：只有 `NSW > 0` 且实际有 ≥2 个离子步时，"体积不变"才值得怀疑。
    isif = d["incar"].get_int("ISIF") if d["incar"] else None
    nsw = d["incar"].get_int("NSW") if d["incar"] else None
    d["isif"] = isif
    d["nsw"] = nsw
    if isif == 3:
        vols = vc.outcar_cell_volumes(inp_path(d))
        d["n_cell_records"] = len(vols)
        if nsw == 0:
            d["infos"].append(
                ("C.isif3_cell",
                 "ISIF = 3 但 NSW = 0 —— 这是**单点**计算，没有离子步，"
                 "所以 ISIF 实际不起作用（晶胞当然不变）",
                 "这不是问题，只是提醒：`ISIF` 只在有离子步时才有意义。",
                 "无需改动。", "[实测] 依据：things to study/al2o3 的 INCAR"))
        elif len(steps) < 2:
            d["infos"].append(
                ("C.isif3_cell",
                 "ISIF = 3 且 NSW = %s，但 OUTCAR 里只有 %d 个离子步 —— "
                 "晶胞变化无从判断" % (nsw, len(steps)),
                 "离子步太少（可能一步就满足了收敛判据，或算例被中断）。",
                 "看 CONTCAR 与 POSCAR 的晶格差异。", "[实测]"))
        elif len(vols) >= 2:
            v0, v1 = vols[0][0], vols[-1][0]
            d["volume_change"] = (v0, v1)
            if abs(v1 - v0) / max(v0, 1e-9) < 1e-6:
                d["warns"].append(
                    ("C.isif3_cell",
                     "ISIF=3 但晶胞体积从 %s 到 %s Å³ **几乎没变**"
                     % (_f(v0, 3), _f(v1, 3)),
                     "`ISIF=3` 应该同时优化晶胞形状与体积。体积完全不变说明"
                     "优化可能没真正动晶胞（步数用完、或者 `OPTCELL` 之类的"
                     "外部约束把方向全冻住了 —— 而 `OPTCELL` **不在 OUTCAR 回显**，"
                     "所以程序不会告诉你这件事）。",
                     "比对优化前后 `POSCAR` 与 `CONTCAR` 的晶格；"
                     "并确认你的 `OPTCELL` 只冻结了真空方向。",
                     "[实测] 依据：真实算例 day1/mos2 的 POSCAR vs CONTCAR 对比"))
            else:
                d["infos"].append(
                    ("C.isif3_cell",
                     "ISIF=3，晶胞体积 %s → %s Å³（变 %.2f%%）"
                     % (_f(v0, 3), _f(v1, 3),
                        100.0 * (v1 - v0) / max(v0, 1e-9)),
                     "", "", "[实测]"))

    # ---- ⑩ 频率自由度语义 ----
    ibrion = d["incar"].get_int("IBRION") if d["incar"] else None
    d["ibrion"] = ibrion
    if ibrion == 5:
        n_free = None
        if d["poscar"] and d["poscar"].lattice:
            n_free = sum(1 for row in d["poscar"].lattice if any(t == "T" for t in row))
        else:
            n_free = d["poscar"].nions if d["poscar"] else None
        expected = 3 * n_free if n_free else None
        # 找 "Degree of freedom"（可能写作 DOF）
        dof_seen = None
        for _ln, line in vc.iter_lines(inp_path(d, "OUTCAR")):
            if "Degree of freedom" in line or "degree of freedom" in line:
                m = __import__("re").search(r"(\d+)\s*/\s*(\d+)", line)
                if m:
                    dof_seen = (int(m.group(1)), int(m.group(2)))
                    break
        d["freq_dof"] = {"n_free_atoms": n_free, "expected": expected,
                         "outcar": dof_seen}
        if dof_seen and expected:
            if dof_seen[1] == expected:
                d["infos"].append(
                    ("C.freq_dof",
                     "IBRION=5：OUTCAR 报自由度 %d/%d，与「3 × 放开原子数(= %d)」一致"
                     % (dof_seen[0], dof_seen[1], n_free),
                     "", "",
                     "[实测] 这条语义在真实算例上核实过：21 原子只放开 1 个 → 3/3；O2 → 6/6"))
            else:
                d["warns"].append(
                    ("C.freq_dof",
                     "IBRION=5：OUTCAR 报自由度 %d/%d，但按「3 × 放开原子数(%d)」"
                     "应是 %d" % (dof_seen[0], dof_seen[1], n_free, expected),
                     "本工具按「自由度 = 3 × 放开原子数」核对（这条语义来自"
                     "真实算例的核对，见 decide.md §13.1）。不符时可能"
                     "①POSCAR 的 Selective dynamics 标志与运行时不同；"
                     "②这个 VASP 版本的自由度语义不同。",
                     "以 OUTCAR 的实际回显为准；确认 POSCAR 是那次跑用的那个。",
                     "[实测] 语义来源；⚠️ 跨版本未验证"))


def inp_path(d: dict, key: str = "") -> str:
    """从 gather 的结果里取回文件路径（避免把整个 inp 传进 check）。"""
    if key:
        return d["_paths"].get(key) or ""
    return d["_paths"].get("OUTCAR") or ""


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="compare.py",
        description="物理不变量与跨文件一致性检查（离线判「算得对不对」的第一道）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=无问题；1=文件问题；3=缺必要文件；4=有 ERROR；5=有 WARN。\n"
               "⚠️ 本工具的阈值**未在真机上标定** —— 详见文件头的能力边界。",
    )
    ap.add_argument("directory", nargs="?", default=".")
    ap.add_argument("--potcar", help="（本工具不用 POTCAR；此参数只为与 validate.py 一致）")
    ap.add_argument("--strict", action="store_true",
                    help="把 WARN 也当成失败")
    ap.add_argument("--quiet", action="store_true",
                    help="只印结论行（便于批量跑多个算例）")
    ap.add_argument("--json", action="store_true", help="输出 JSON（便于接进别的脚本）")
    ap.add_argument("--list-checks", action="store_true")
    args = ap.parse_args(argv)

    if args.list_checks:
        print("compare.py 会做的检查：\n")
        for cid, desc in CHECKS:
            print("  %-22s %s" % (cid, desc))
        print("\n本工具**不做**的检查：")
        for line in UNCHECKED:
            print("  • " + line)
        print("\n⚠️ 所有以 F. 开头的检查，阈值都**未在真机上标定**：")
        print("   本机没有 VASP，无法构造「已知错误的计算」来做正例/反例对照。")
        print("   要标定它们，见 conformance/README.md。")
        return EXIT_OK

    directory = args.directory
    if not os.path.isdir(directory):
        vc.die("不是一个目录：%s" % directory, EXIT_USER,
               "用法：python scripts/compare.py <算例目录>")

    inp = vc.discover_inputs(directory)
    if not inp["OUTCAR"] and not inp["OSZICAR"]:
        vc.die("在 %s 里既没有 OUTCAR 也没有 OSZICAR —— 没有可检查的输出"
               % inp["dir"], EXIT_DEP,
               "本工具检查的是**计算结果**。若你还没跑，先跑起来；\n"
               "若只想校验输入，用：python scripts/validate.py <目录>")

    inp["_paths"] = inp
    d = gather(inp)
    d["_paths"] = inp
    check(d)

    errs, warns, infos = d["errors"], d["warns"], d["infos"]

    if args.json:
        out = {
            "directory": d["dir"],
            "version": d["version"],
            "n_ionic_outcar": d.get("n_ionic_outcar"),
            "n_ionic_oszicar": d.get("n_ionic_oszicar"),
            "e0_outcar": d.get("e0_outcar"),
            "e0_oszicar": d.get("e0_oszicar"),
            "nions_seen": d.get("nions_seen"),
            "encut_incar": d.get("encut_incar"),
            "encut_outcar": d.get("encut_outcar"),
            "sum_force_mag": d.get("sum_force_mag"),
            "max_force": d.get("max_force"),
            "drift_ratio": d.get("drift_ratio"),
            "total_drift": d.get("total_drift"),
            "errors": [{"check": a, "msg": b} for a, b, *_ in errs],
            "warns": [{"check": a, "msg": b} for a, b, *_ in warns],
            "infos": [{"check": a, "msg": b} for a, b, *_ in infos],
            "unchecked": UNCHECKED,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))
        if errs:
            return EXIT_ERROR
        if warns and args.strict:
            return EXIT_ERROR
        return EXIT_WARN if warns else EXIT_OK

    print("=" * 72)
    print("物理不变量与一致性检查 —— %s" % d["dir"])
    print("=" * 72)
    if args.quiet:
        print("版本 %s | 离子步 %s/%s | E=%s | |ΣF|=%s | maxF=%s | ERROR %d WARN %d"
              % ((d["version"].split()[0] if d["version"] else "?"),
                 d.get("n_ionic_outcar"), d.get("n_ionic_oszicar"),
                 _f(d.get("e0_outcar")), _f(d.get("sum_force_mag")),
                 _f(d.get("max_force")), len(errs), len(warns)))
        for cid, msg, *_ in errs:
            print("  ERROR [%s] %s" % (cid, msg.replace("\n", " ")))
        for cid, msg, *_ in warns:
            print("  WARN  [%s] %s" % (cid, msg.replace("\n", " ")))
        return (EXIT_ERROR if errs else
                (EXIT_ERROR if (warns and args.strict) else
                 (EXIT_WARN if warns else EXIT_OK)))
    if d["version"]:
        print("程序版本：%s" % d["version"])
    print("离子步：OUTCAR %s 步 / OSZICAR %s 步"
          % (d.get("n_ionic_outcar"), d.get("n_ionic_oszicar")))
    print("能量：OUTCAR energy(sigma->0) = %s eV ；OSZICAR 最后 E0 = %s eV"
          % (_f(d.get("e0_outcar")), _f(d.get("e0_oszicar"))))
    if d.get("nions_seen"):
        print("原子数：%s" % ", ".join("%s=%d" % kv
                                       for kv in sorted(d["nions_seen"].items())))
    print("ENCUT：INCAR %s / OUTCAR 实际 %s eV"
          % (_f(d.get("encut_incar"), 2), _f(d.get("encut_outcar"), 2)))
    if d.get("sum_force_mag") is not None:
        print("力：|ΣF| = %s eV/Å ；最大单原子受力 = %s eV/Å ；比值 %s"
              % (_f(d.get("sum_force_mag")), _f(d.get("max_force")),
                 _f(d.get("drift_ratio"), 4)))
    if d.get("total_drift"):
        print("OUTCAR 自带 total drift = (%.6f, %.6f, %.6f)"
              % d["total_drift"])
    print()

    def show(items):
        for it in items:
            cid, msg = it[0], it[1]
            why = it[2] if len(it) > 2 else ""
            fix = it[3] if len(it) > 3 else ""
            src = it[4] if len(it) > 4 else ""
            print("[%s] %s" % (cid, msg))
            if why:
                print("    为什么：%s" % why)
            if fix:
                print("    怎么办：%s" % fix)
            if src:
                print("    依据：%s" % src)
            print()

    if errs:
        print("── ERROR ──")
        show(errs)
    if warns:
        print("── WARNING ──")
        show(warns)
    if infos:
        print("── 通过 / 信息 ──")
        for it in infos:
            print("  ✓ [%s] %s" % (it[0], it[1]))
        print()

    print("-" * 72)
    print("结论：ERROR %d 项，WARNING %d 项，通过/信息 %d 项"
          % (len(errs), len(warns), len(infos)))
    if not errs and not warns:
        print("      → 未发现问题。⚠️ 但这**不等于算得对** —— 见下。")
    print()
    print("⚠️ 本次**未检查**的项：")
    for line in UNCHECKED:
        print("   • " + line)
    print()
    print("⚠️ 阈值标定状态：所有 `F.` 开头的力判据阈值**未在真机上标定**")
    print("   （本机没有 VASP，无法构造已知错误的算例做对照 —— 见 conformance/README.md）。")
    print("   它们默认报 WARN 而不是 ERROR，就是为了不给你假的确定感。")
    return (EXIT_ERROR if errs else
            (EXIT_ERROR if (warns and args.strict) else
             (EXIT_WARN if warns else EXIT_OK)))


if __name__ == "__main__":
    sys.exit(main())
