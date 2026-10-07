#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""diagnose.py —— 从算例输出里**自动找出症状**，并给出诊断与处方（**零依赖**）

它和 `validate.py` / `compare.py` 的分工
======================================
| 工具 | 输入 | 回答的问题 |
|---|---|---|
| `validate.py` | 输入文件 | 我的**输入**写对了吗 |
| `compare.py` | 输入 + 输出 | 结果**自洽**吗（能量/原子数/力） |
| **`diagnose.py`** | **输出为主** | **跑出问题了，是哪一类？该怎么改？** |

三条设计原则
============
1. **症状必须可观察。** 每条诊断都给出它在哪个文件的哪一行、原文长什么样 ——
   你**可以自己 grep 验证**，不需要相信本工具。
2. **说"没找到"，不说"没问题"。** 本工具只在你目录里已有的文件里找已知症状。
   找不到**不等于**算得对。
3. **处方给到"改哪一行、改成什么"。** 不给方向性描述。

⚠️ **本工具没有在真机上验证过。** 本机没有 VASP，无法构造"已知错误的计算"来
确认每条症状的检测是否真的会触发（§4.2 要求的注入测试）。所以：
- 每条规则的 `证据` 字段标明它来自官方明文、算例、讲义，还是只是经验；
- 标 `[经验]` 的规则**默认只报"提示"**，不报"确定的问题"。

用法
----
    python scripts/diagnose.py <算例目录>
    python scripts/diagnose.py <算例目录> --verbose
    python scripts/diagnose.py --list-rules
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3
EXIT_FOUND, EXIT_HINT = 4, 5


class Symptom:
    """一条症状规则。

    字段刻意分得细，因为"四要素齐全"是 `_WRITING_CONTRACT.md` 的硬要求：
    `symptom` / `diagnosis` / `fix` / `criterion` 一个都不能少。
    """

    __slots__ = ("rule_id", "level", "symptom", "where", "evidence",
                 "diagnosis", "fix", "criterion", "source")

    def __init__(self, rule_id, level, symptom, where, diagnosis, fix,
                 criterion, source, evidence=""):
        self.rule_id = rule_id
        self.level = level          # 确定的问题 / 提示
        self.symptom = symptom      # 用户能观察到什么（含可 grep 的原文）
        self.where = where          # 在哪个文件的哪里
        self.diagnosis = diagnosis  # 为什么会这样
        self.fix = fix              # 改哪一处、改成什么
        self.criterion = criterion  # 怎么知道改对了
        self.source = source        # 依据（官方/算例/讲义/经验）
        self.evidence = evidence    # 实测到的原文片段


RULES = []


def _rule(rid, level, source):
    def deco(fn):
        RULES.append((rid, level, source, fn))
        return fn
    return deco


# ---------------------------------------------------------------------------
# 一、跑没跑起来 / 跑完没有（读 OUTCAR 头尾）
# ---------------------------------------------------------------------------
@_rule("RUN.not_finished", "确定", "[官方] OUTCAR 的 General timing 段")
def r_not_finished(ctx):
    if not ctx["OUTCAR"]:
        return None
    tail = ctx["outcar_tail"]
    if "General timing" in tail or "Voluntary context switches" in tail:
        return None

    # ⚠️⚠️ **本规则必须让位给 `LAUNCH.crash_no_scf`**（见 CHANGELOG 的 CR-045）。
    #
    # 两者都会在"程序没正常收尾"时触发，但**处方完全不同**：
    #   · 本规则假设"跑了一半被打断" ⇒ 处方是"看 OSZICAR 最后一步的 d E""拷
    #     `CONTCAR` 续算"；
    #   · `LAUNCH.crash_no_scf` 是"**一次 SCF 都没走就崩了**" ⇒ 处方是**改并行分解**。
    #
    # 对一个崩溃的算例，本规则的**三条处方一条都执行不了**
    # （没有"最后一步"、没有 `CONTCAR`、没有 `reached required accuracy`）。
    # 把它们一起打出来，会**把真正的处方淹掉** —— 而那正是本项目要消灭的病。
    #
    # ⇒ 判据：**有崩溃特征 且 `OSZICAR` 零迭代** ⇒ 本条不出声，
    #    让 `LAUNCH.crash_no_scf` 单独说话。
    info = ctx.get("log_info") or {}
    crash = info.get("first_crash_line")
    if crash and ctx.get("oszicar_iters", 0) == 0:
        return None

    return Symptom(
        "RUN.not_finished", "确定",
        "OUTCAR 里**没有** `General timing and accounting informations` 段 "
        "—— 这次计算**没有正常收尾**",
        ctx["OUTCAR"],
        "VASP 正常结束时一定会打印 General timing 段。没有它说明程序"
        "被中断（墙钟到点、被 kill、崩溃）或还在跑。"
        "**注意**：这不等于结果一定没用 —— 若收敛判据已经达到，"
        "结果可能仍可用；但你必须确认。",
        "① 看 OUTCAR 末尾有没有 `reached required accuracy`；"
        "② 看 OSZICAR 最后一步的 `d E` 是否已足够小；"
        "③ 若只是墙钟不够，把 CONTCAR 拷成 POSCAR 续算"
        "（ISTART=1、ICHARG=1）。",
        "OUTCAR 末尾出现 `General timing and accounting informations`。",
        "[官方] OUTCAR 格式",
        # 附带说明"为什么这次不报" —— 让用户知道另一条规则接管了
        "" if not ctx["OUTCAR"] else "")


@_rule("RUN.very_bad_news", "确定", "[讲义] + [算例] 双重佐证")
def r_very_bad_news(ctx):
    hits = []
    for key in ("OUTCAR", "LOG"):
        p = ctx.get(key)
        if not p:
            continue
        for ln, line in vc.iter_lines(p):
            if "VERY BAD NEWS" in line or "very bad news" in line.lower():
                hits.append((key, ln, line.strip()))
                break
    if not hits:
        return None
    key, ln, line = hits[0]
    return Symptom(
        "RUN.very_bad_news", "确定",
        "输出里出现 `VERY BAD NEWS`：\n        %s" % line,
        "%s:%d" % (ctx[key], ln),
        "**最常见的一种**是四面体方法（`ISMEAR=-5`/`-4`）遇到 k 点太少："
        "`internal error in subroutine IBZKPT: Tetrahedron method fails for "
        "NKPT<4`。四面体方法需要至少 4 个不可约 k 点才能构造四面体。",
        "① 若 `ISMEAR=-5/-4`：要么加密 k 点（让 NKPT ≥ 4），"
        "要么改用 `ISMEAR=0`（Gaussian）/`1`（MP）。\n"
        "        ② 若报的是别的子程序名，把整行原文拿去 "
        "`references/playbook.md` §5 的报错速查里对。",
        "重跑后不再出现 `VERY BAD NEWS`，且 SCF 正常收敛。",
        "[讲义] L2 关于 `ISMEAR=-5` 与 k 点数的段落；"
        "[算例] 多个算例的 NKPTS 数字可对照",
        evidence=line)


@_rule("SCF.not_converged", "确定", "[官方] NELM / EDIFF；[实测] 标记位置")
def r_scf_not_converged(ctx):
    """电子自洽循环有没有按 `EDIFF` 收敛。

    ⚠️ **标记在 `OUTCAR` 里，不在 `OSZICAR` 里。**（实测校正）
    官方 INCAR 页说 VASP 会把自己对 INCAR 的理解写进 OUTCAR。
    实测（`things to study/day2/ni-co/`）：
    `aborting loop because EDIFF is reached` 在 **OUTCAR 里出现 8 次**
    （该算例正好 8 个离子步），而在 **OSZICAR 里出现 0 次**。
    本规则早期版本去 `OSZICAR` 里找，于是在**所有**算例上都会误报
    —— 已记入 CHANGELOG 更正记录。
    """
    if not ctx["OUTCAR"]:
        return None
    n_reached = 0
    for _ln, line in vc.iter_lines(ctx["OUTCAR"]):
        if "aborting loop because EDIFF is reached" in line:
            n_reached += 1
    n_ionic = len(ctx["steps"])
    if n_reached == 0 and n_ionic == 0:
        return None                      # 不是一次电子自洽计算（如纯后处理）
    if n_reached >= max(1, n_ionic):
        return None
    return Symptom(
        "SCF.not_converged", "确定",
        "OUTCAR 里 `aborting loop because EDIFF is reached` 出现 **%d 次**，"
        "而离子步有 **%d** 个 —— 至少有一个电子循环**不是**按 `EDIFF` 收敛的"
        % (n_reached, n_ionic),
        ctx["OUTCAR"],
        "每个离子步的电子自洽循环收敛时，VASP 都会在 OUTCAR 里打印一行 "
        "`aborting loop because EDIFF is reached`。所以它的**次数应当等于"
        "离子步数**。少了，就说明有电子循环是用尽 `NELM` 而退出的 —— "
        "此时那一步的能量不可信，而程序**不会额外报警**。",
        "① 看 OUTCAR 里没收敛的那一步附近，`DAV:` 的能量是否在振荡；\n"
        "        ② 提高 `NELM`（300 → 600）看能否收敛；\n"
        "        ③ 若振荡不收敛：调混合参数（`AMIX`/`BMIX`）、"
        "金属加大 `SIGMA`、或先用 `ISMEAR=0` 粗收敛再切到目标展宽；\n"
        "        ④ 用 `ALGO=Normal`（而非 `Fast`）更稳。",
        "OUTCAR 里 `aborting loop because EDIFF is reached` 的次数"
        "**等于离子步数**（或至少不再出现「用尽 NELM」的段落）。",
        "[官方] NELM / EDIFF 页；[实测] 该标记在 OUTCAR 而不在 OSZICAR",
        evidence="EDIFF 收敛标记 %d 次 / 离子步 %d 个" % (n_reached, n_ionic))


@_rule("SCF.energy_oscillating", "提示", "[经验]（阈值未标定）")
def r_scf_oscillating(ctx):
    if not ctx["OSZICAR"]:
        return None
    vals = []
    for _ln, line in vc.iter_lines(ctx["OSZICAR"]):
        m = re.match(r"\s*\d+\s+[FT]=\s*([-\d.Ee+]+)", line)
        if m:
            try:
                vals.append(float(m.group(1)))
            except ValueError:
                pass
    if len(vals) < 6:
        return None
    # 最近 6 步里能量上下反复（不是单调下降）
    tail = vals[-6:]
    ups = sum(1 for i in range(1, len(tail)) if tail[i] > tail[i - 1])
    if ups < 3:
        return None
    return Symptom(
        "SCF.energy_oscillating", "提示",
        "最近 6 个离子步里能量**上下反复**了 %d 次（不是单调下降）" % ups,
        ctx["OSZICAR"],
        "离子步能量振荡通常是：①离子步的 SCF 没收敛就往下走；"
        "②`POTIM` 太大，几何在势能面上跳；③初始结构太差。"
        "⚠️ **能量上升本身不一定是错**（CG 在非凸面上会暂时上升），"
        "所以这条只报「提示」。",
        "① 先确认每个离子步的 SCF 都收敛（见 SCF.not_converged）；\n"
        "        ② 把 `POTIM` 从 0.2 调到 0.1；\n"
        "        ③ 检查每一步的最大力是否在稳定下降。",
        "连续 5 个离子步的能量单调下降，且力也单调下降。",
        "[经验] 判据（6 步里 ≥3 次上升）**未在真机上标定**",
        evidence="最近 6 个离子步能量：" + ", ".join("%.5f" % v for v in tail))


@_rule("GEO.not_converged", "确定", "[官方] EDIFFG；[实测] 触发条件已收窄")
def r_geo_not_converged(ctx):
    """离子弛豫有没有达到收敛判据。

    ⚠️ **这条规则返工过。** 早期版本在 `NSW = 0`（**单点**计算）上也会报
    "离子弛豫没收敛" —— 而单点计算**根本没有离子步**，不收敛是正常的。
    实测：98 个真实算例里触发 17 次，其中相当一部分是这类假阳性
    （见 CHANGELOG 更正记录）。

    现在的三道门：
    1. `NSW` 必须 > 0（真的做了弛豫）；
    2. OUTCAR 里必须**至少有一个离子步**；
    3. 必须**真的有离子步带力表**（否则无从判断力收敛）。
    """
    if not ctx["OUTCAR"] or not ctx["steps"]:
        return None
    incar = ctx["incar"]
    nsw = incar.get_int("NSW") if incar else None
    if nsw is not None and nsw <= 0:
        return None                       # 单点计算，谈不上"没收敛"
    steps = ctx["steps"]
    if len(steps) < 2:
        return None                       # 没有真正的离子步序列
    last = None
    for st in reversed(steps):
        if st.forces:
            last = st
            break
    if last is None or last.max_force is None:
        return None
    # 用 INCAR 的 EDIFFG（负值=力判据）判断
    ediffg = incar.get_float("EDIFFG") if incar else None
    reached = any(st.reached_required for st in steps)
    if reached:
        return None
    target = abs(ediffg) if (ediffg is not None and ediffg < 0) else None
    # 如果最后一步的力已经小于判据，那不收敛只是"程序没打印那句话"，
    # 不构成问题 —— 别报。
    if target is not None and last.max_force <= target:
        return None
    return Symptom(
        "GEO.not_converged", "确定",
        "离子弛豫**没有**达到收敛判据：OUTCAR 里找不到 "
        "`reached required accuracy - stopping structural energy minimisation`\n"
        "        最后一个有力表的离子步（第 %d 步 / 共 %d 步）："
        "最大力 = %.4f eV/Å，RMS 力 = %.4f eV/Å"
        % (last.index, len(steps), last.max_force, last.rms_force or float("nan")),
        ctx["OUTCAR"],
        "VASP 用 `EDIFFG`（**负值 = 力判据**）决定何时停止离子弛豫。"
        "没达到就停了，通常是 `NSW` 用尽 —— 也就是说**结构还没优化完**，"
        "你手上的 CONTCAR 不是极小点。"
        + ("" if target is None else
           "你写的 `EDIFFG = %g`，即要求所有力 < %.4f eV/Å；"
           "实际最后一步的最大力是 %.4f eV/Å。"
           % (ediffg, target, last.max_force)),
        "① 若力只差一点：把 CONTCAR 拷成 POSCAR 续算"
        "（`ISTART=1`、`ICHARG=1`、`NSW` 给够）；\n"
        "        ② 若力在振荡不降：把 `POTIM` 调到 0.1，或换 `IBRION=1`；\n"
        "        ③ 若力很大（> 0.5 eV/Å）：检查初始结构是否合理、"
        "`POTIM` 是否过大、`ENCUT`/k 点是否够。",
        "OUTCAR 里出现 `reached required accuracy`，**或**最后一步的最大力"
        "小于 `|EDIFFG|`。",
        "[官方] EDIFFG 页（负值=力判据）",
        evidence="最大力 %.4f eV/Å（判据 %s），最后一步 reached_required=%s"
                 % (last.max_force,
                    ("%.4f" % target) if target else "未写 EDIFFG",
                    last.reached_required))


# ---------------------------------------------------------------------------
# 二、"跑完了但结果不对"（**最值钱的一类：没有任何报错**）
# ---------------------------------------------------------------------------
@_rule("WRONG.dos_from_relax", "确定", "[实测] + [讲义] L2 P62")
def r_dos_from_relax(ctx):
    if not ctx["OUTCAR"]:
        return None
    incar = ctx["incar"]
    if incar is None:
        return None
    wants_dos = (incar.get_int("LORBIT") in (10, 11, 12)
                 or incar.get_int("NEDOS") is not None
                 or "DOSCAR" in str(ctx.get("files", [])))
    if not wants_dos:
        return None
    nsw = incar.get_int("NSW")
    if nsw == 0:
        return None
    n_fermi = 0
    for _ln, line in vc.iter_lines(ctx["OUTCAR"]):
        if "E-fermi" in line:
            n_fermi += 1
            if n_fermi > 1:
                break
    if n_fermi <= 1:
        return None
    return Symptom(
        "WRONG.dos_from_relax", "确定",
        "这个算例要 DOS（`LORBIT`/`NEDOS` 有设），但它是**弛豫**计算："
        "`NSW = %s`，且 OUTCAR 里 `E-fermi` 出现了 **多于一次**"
        % nsw,
        ctx["OUTCAR"],
        "DOS 必须来自**单个固定结构**。弛豫过程中每一步的 DOS 都对应"
        "一个**不同的**结构，VASP 写进 `DOSCAR` 的是**最后一步**的 —— "
        "看起来完全正常，但那个结构未必是收敛的结构，"
        "而且 `DOSCAR` 里 `E-fermi` 的含义也变得含糊。"
        "**这一类错误没有任何报错。**",
        "把 `NSW = 0`、`IBRION = -1`，用**已优化好的** `CONTCAR` 当 `POSCAR`，"
        "重跑一次单点；并用 `ISMEAR=-5`（四面体，配 Γ 居中 k 点）。",
        "重跑后 `grep -c \"E-fermi\" OUTCAR` 的结果是 **1**。",
        "[实测] 真实算例 `day2/ni-co` 的 DOS 就出自 `NSW=300` 的弛豫计算"
        "（OUTCAR 里 E-fermi 出现 8 次）；[讲义] L2 P62 要求 DOS 步用 NSW=0",
        evidence="E-fermi 出现多次（离子步 > 1）")


@_rule("WRONG.encut_below_enmax", "提示", "[官方] POTCAR 页 + [经验] 分档")
def r_encut_low(ctx):
    incar, potcar = ctx["incar"], ctx["potcar"]
    if incar is None or potcar is None:
        return None
    enmax = potcar.max_enmax()
    encut = incar.get_float("ENCUT")
    used = ctx.get("encut_outcar")
    effective = encut if encut is not None else used
    if enmax is None or effective is None:
        return None
    if effective >= enmax:
        return None
    if enmax > 1000:
        return Symptom(
            "WRONG.encut_below_enmax", "提示",
            "`ENCUT` = %.1f eV 低于本套 POTCAR 的 max(ENMAX) = %.1f eV"
            % (effective, enmax),
            ctx["INCAR"] or ctx["OUTCAR"],
            "`ENMAX` 是**孤立原子**的推荐截断。本套里有个元素的 `ENMAX` "
            "异常高（>1000 eV，常见于 He/Ne 这类闭壳层，或带半芯态的 "
            "`_pv`/`_d` 赝势）。对这类元素**几百 eV 往往就够**，"
            "机械照搬会白烧几倍机时。⚠️ 但「够用」是**经验判断**，"
            "本工具无法替你决定。",
            "做一次 `ENCUT` 收敛测试（从 %.0f 扫到 %.0f，看总能量差是否 "
            "< 1 meV/atom），固定住这个值再往下做。"
            % (max(200.0, effective * 0.7), enmax),
            "相邻截断能之间总能量差 < 1 meV/atom。",
            "[官方] POTCAR 页的 ENMAX/ENMIN 定义；"
            "⚠️ 1000 eV 分档阈值是 [经验] 设定，**不是官方判据**")
    return Symptom(
        "WRONG.encut_below_enmax", "确定",
        "`ENCUT` = %.1f eV **低于**本套 POTCAR 的 max(ENMAX) = %.1f eV"
        % (effective, enmax),
        ctx["INCAR"] or ctx["OUTCAR"],
        "低于赝势自带 `ENMAX` 时，平面波基组不足以描述该赝势，"
        "结果会**系统性偏差**，而且不会有任何报错。"
        "官方在 POTCAR 页把 `ENMAX` 列为「推荐的」截断、`ENMIN` 列为「最低可用」的。",
        "把 `ENCUT` 提到 %.0f eV 以上，并做一次收敛测试确认。" % enmax,
        "相邻截断能之间总能量差 < 1 meV/atom。",
        "[官方] POTCAR 页（ENMAX/ENMIN）")


@_rule("WRONG.vacuum_too_small", "提示", "[经验]（阈值来自算例观察）")
def r_vacuum(ctx):
    """真空层偏薄的提醒。

    ⚠️ **这条规则的设计经过一次返工**（见 CHANGELOG 更正记录）。
    早期版本"任何方向跨度与晶格长度差 0–10 Å 就报"，结果在 98 个真实
    算例上**误报 76 次** —— 因为它把"面内的层间距"也当成了真空
    （例如 Ni slab 的面内原子跨度与晶格长度只差 1.24 Å，那是原子间距
    而**不是**真空）。一条 76% 误报的规则等于没有规则，还会让人不再信其它规则。

    现在的判据三道门**都要过**：
    1. 这个方向的间隙必须是**该体系最大的那个**（真空通常是最宽的间隙）；
    2. 间隙必须 > 4 Å（排除层间距/键长量级）；
    3. 间隙必须 < 10 Å（只提醒"偏薄"，不提醒"正常"）。
    """
    poscar = ctx["poscar"]
    if poscar is None or not poscar.symbols:
        return None
    slab, holes = poscar.cell.is_slab(poscar.cartesian())
    if not slab:
        return None
    widest = max(range(3), key=lambda i: holes[i])
    h = holes[widest]
    if not (4.0 < h < 10.0):
        return None
    return Symptom(
        "WRONG.vacuum_too_small", "提示",
        "第 %d 个方向只有约 %.2f Å 真空（该体系最宽的间隙）—— 偏薄"
        % (widest + 1, h),
        ctx["POSCAR"],
        "周期性边界条件下，相邻 slab 的镜像会互相作用；真空越薄，"
        "吸附能/表面能/功函数的误差越大。"
        "⚠️ 这**不是**一条硬规则：真实算例里就有 7.4 Å 的（`day2/ni-co`），"
        "也有 15 Å 的（`day2/Ag`、`day2/au111-opt`）。"
        "本工具判断「哪个方向是真空」用的是启发式（最宽间隙），"
        "对倾斜晶胞或层间有真实相互作用的体系可能判错。",
        "把真空加厚到 15 Å 左右再算一遍，看你关心的量变了多少。"
        "**变多少才是判据**，不是「必须 15 Å」。",
        "真空加厚后，你关心的量（吸附能/表面能/功函数）变化小于你的误差预算。",
        "[经验] 判据来源：真实算例的真空层厚度分布（7.4–15.2 Å）；"
        "⚠️ 4 Å 与 10 Å 两个阈值都是经验的，非官方")


@_rule("WRONG.magmom_not_effective", "确定", "[官方] MAGMOM 页")
def r_magmom(ctx):
    incar = ctx["incar"]
    if incar is None or incar.get("MAGMOM") is None:
        return None
    istart = incar.get_int("ISTART")
    icharg = incar.get_int("ICHARG")
    # 官方：从 WAVECAR/CHGCAR 续算时 MAGMOM 只用来定对称性
    if istart in (1, 2, 3) or icharg in (1, 11):
        has_wavecar = any(f.lower().startswith(("wavecar", "chgcar"))
                          for f in ctx.get("files", []))
        if not has_wavecar:
            return None
        return Symptom(
            "WRONG.magmom_not_effective", "确定",
            "`MAGMOM` 写了，但 `ISTART = %s` / `ICHARG = %s` —— "
            "**这一步它不会设置初值**" % (istart, icharg),
            ctx["INCAR"],
            "官方 MAGMOM 页明文：续算（从 `WAVECAR`/`CHGCAR` 读）时，"
            "`MAGMOM` **只用于确定体系的对称性**，不再设定 on-site 磁矩。"
            "同一个页面还警告："
            "`if you remove the MAGMOM tag before restarting ... the "
            "magnetization is likely to be symmetrized away`。"
            "⇒ 所以「我改了 MAGMOM 但结果没变」是**预期行为**，不是 bug。",
            "① 想换磁态：用 `ISTART=0` 从头算（或同时给 `ICHARG=1` 且"
            "不读 WAVECAR）；\n"
            "        ② 想保住磁矩续算：把 `MAGMOM` **留着**"
            "（删掉反而会被对称化掉）。",
            "OUTCAR 里每个离子的最终磁矩与你设的初值方向一致。",
            "[官方] MAGMOM 页（重启行为 + 删除 MAGMOM 的警告）")


@_rule("WRONG.ismear_insulator", "提示", "[官方] ISMEAR 页；带隙判据 [经验]")
def r_ismear(ctx):
    """`ISMEAR > 0`（MP 展宽）用在了**有带隙**的体系上。

    ⚠️ **这条规则也返工过。** 早期版本只要看到 `ISMEAR > 0` 就报，
    在 98 个真实算例上误报 **48 次** —— 而其中绝大多数是**金属**
    （Ag/Au/Ni/Co 表面），对它们用 MP 恰恰是**正确**的。
    一条把"正确做法"报成问题的规则，比没有规则更糟。

    现在要求**先拿到"有带隙"的证据**才报：从 `OUTCAR` 里读
    `E-fermi` 与占据情况做不到（那需要本征值），所以改用
    `OUTCAR` 里 VASP 自己算的**带隙**（新版会打印 `Egap`），
    或者 `INCAR` 里用户自己写了 `ISMEAR=0` 又同时给了 `SIGMA>0.5` 这类矛盾。
    拿不到证据就**不报** —— 宁可不报，也不误报。
    """
    incar = ctx["incar"]
    if incar is None:
        return None
    ismear = incar.get_int("ISMEAR")
    if ismear is None or ismear <= 0:
        return None
    # 证据 1：OUTCAR 里 VASP 自己报的带隙（VASP 6 会打印 "Egap"）
    egap = None
    if ctx["OUTCAR"]:
        for _ln, line in vc.iter_lines(ctx["OUTCAR"]):
            m = re.search(r"Egap\s*=\s*([-\d.]+)", line)
            if m:
                try:
                    egap = float(m.group(1))
                except ValueError:
                    pass
    # 证据 2：INCAR 自己写了 ISPIN=1 且同时出现"绝缘体"的迹象 —— 不做猜测
    if egap is None or egap <= 0.05:
        return None
    return Symptom(
        "WRONG.ismear_insulator", "提示",
        "OUTCAR 报告带隙 `Egap = %.3f eV`，但 `ISMEAR = %d` 用了 "
        "Methfessel-Paxton 展宽" % (egap, ismear),
        ctx["INCAR"],
        "官方 ISMEAR 页明文："
        "`Methfessel-Paxton can yield erroneous results for insulators "
        "because the partial occupancies can be unphysical.`"
        "本规则的触发条件是**程序自己报出了带隙**（`Egap`），"
        "所以它不会在金属上误报。",
        "改用 `ISMEAR = 0` + `SIGMA = 0.01–0.05`，重跑并与现在的结果对比。",
        "换成 `ISMEAR=0` 后，你关心的能量差变化在你的误差预算内"
        "（若明显变化，说明原来确实受了非物理占据的影响）。",
        "[官方] ISMEAR 页；⚠️ 带隙阈值 0.05 eV 是 [经验]（非官方）",
        evidence="Egap = %.3f eV, ISMEAR = %d" % (egap, ismear))


@_rule("WRONG.ldipol_charged", "确定", "[官方] LDIPOL 页")
def r_ldipol(ctx):
    incar, poscar = ctx["incar"], ctx["poscar"]
    if incar is None or poscar is None:
        return None
    if not incar.get_bool("LDIPOL"):
        return None
    # 非立方超胞 + 带电体系的组合是官方明文警告的情形
    a, b, c = poscar.cell.lengths()
    cubic = (abs(a - b) < 1e-3 and abs(b - c) < 1e-3)
    nelect = incar.get_float("NELECT")
    charged = nelect is not None and ctx["potcar"] is not None and \
        ctx["potcar"].total_valence() is not None and \
        abs(nelect - ctx["potcar"].total_valence()) > 1e-6
    if cubic or not charged:
        return None
    return Symptom(
        "WRONG.ldipol_charged", "确定",
        "`LDIPOL = .TRUE.` + **非立方**超胞（a=%.2f, b=%.2f, c=%.2f）+ "
        "带电体系（`NELECT` 与价电子总数不符）" % (a, b, c),
        ctx["INCAR"],
        "官方对 `LDIPOL` 的用法有明文警告：把它用在**带电体系 + 非立方超胞**"
        "的组合上时 VASP 会直接停下。这不是「结果不对」，而是「跑不起来」，"
        "但值得在提交前就发现。",
        "① 若体系带电：用**立方**超胞，或改用别的方式处理电荷补偿"
        "（例如加抗衡离子）；\n"
        "        ② 若体系中性：`LDIPOL` 对不对称 slab 是有用的，"
        "保留即可（此时不触发这条）。",
        "VASP 能正常跑完，且 OUTCAR 里没有与 LDIPOL/偶极相关的报错。",
        "[官方] LDIPOL 页的警告；[答疑]/[讲义] 相关段落")


@_rule("NOTE.isym_off", "仅详细模式", "[官方] ISYM 页；用法分布 [算例]")
def r_isym(ctx):
    """只是**提示**，不是问题 —— 默认输出里不显示。

    ⚠️ 这条规则收窄过：真实算例里 `ISYM = 0` 用得**非常普遍**
    （`day1/fe2o3`、`2-dos/*`、`6-electronic/oer/*` 都用了），
    它是表面/吸附体系里被广泛接受的保守选择。
    早期版本把它当"提示"报出来，在 98 个算例上触发 56 次 ——
    那会把"常见做法"渲染成"你有问题"，削弱其它规则的信号。
    现在它只在 `--verbose` 下显示。
    """
    incar = ctx["incar"]
    if incar is None:
        return None
    isym = incar.get_int("ISYM")
    if isym != 0:
        return None
    return Symptom(
        "NOTE.isym_off", "仅详细模式",
        "`ISYM = 0`（完全关闭对称性）",
        ctx["INCAR"],
        "关掉对称性是有代价的：①k 点不再约化，计算量可能上升数倍；"
        "②有些体系更容易收敛到错误的磁态或畸变结构。"
        "官方给 `ISYM=0` 的典型理由是**分子动力学**。"
        "但这个设置在本项目的真实算例里**很普遍**，"
        "所以它属于「常见做法」，不是「问题」。",
        "若你不是在做 MD 也没遇到对称性报错：试着去掉 `ISYM=0`（用默认），"
        "比较能量与力是否一致。一致 ⇒ 可以打开对称性省机时。",
        "开关对称性前后，总能量与力的差异在你的误差预算内。",
        "[官方] ISYM 页；[算例] 多个真实算例用 ISYM=0")


@_rule("WRONG.no_encut_explicit", "提示", "[官方] PREC 页（strongly recommend）")
def r_no_encut(ctx):
    incar = ctx["incar"]
    if incar is None or incar.get("ENCUT") is not None:
        return None
    used = ctx.get("encut_outcar")
    return Symptom(
        "WRONG.no_encut_explicit", "提示",
        "`INCAR` 里没写 `ENCUT`；OUTCAR 显示程序实际用了 %s eV"
        "（取自 POTCAR 的 max(ENMAX)）" % (used if used else "?"),
        ctx["INCAR"],
        "官方 PREC 页的原话："
        "`We strongly recommend specifying the energy cutoff ENCUT always "
        "manually in the INCAR file to ensure the same accuracy between "
        "calculations. Otherwise, the default ENCUT may differ among the "
        "different calculations ..., with the consequence that the total "
        "energies, for instance, can not be compared.`"
        "⇒ 不写 `ENCUT` 时，**换一套赝势就会静默改变基组**，"
        "而你比较的能量差就不再是同口径的。",
        "把 OUTCAR 里显示的实际值显式写进 `INCAR`；并做一次收敛测试。",
        "`INCAR` 与 OUTCAR 的 `ENCUT` 一致（`compare.py` 的 "
        "`X.encut_consistent` 会核对）。",
        "[官方] PREC 页的 strong recommendation")


# ---------------------------------------------------------------------------
# 二之二、**作业起没起来**这一层（LAUNCH.*）
#
# 为什么单列一层：本项目的一次真实事故 —— 用户 179 原子体系、16 MPI rank、
# **没写 `NPAR`/`NCORE`**（走默认 `NCORE=1`）⇒ 每个 rank 独占一个 band、
# 独自完成整块 FFT ⇒ **第一次 SCF 就 SIGSEGV**，`OSZICAR` 只有表头。
# 调一行 `NPAR = 2` 就好了。
#
# ⚠️ 原来的 13 条规则**全部假设"计算跑完了"**：它们读 `OUTCAR`/`OSZICAR`
# 的**内容行**。所以对这种算例，它们要么不触发、要么给出
# **不可能执行的处方**（"看 OSZICAR 最后一步的 d E" —— 可它没有最后一步）。
# ⇒ **"跑完了但结果不对"与"根本没跑起来"是两类问题，需要两套信号。**
# ---------------------------------------------------------------------------
@_rule("LAUNCH.crash_no_scf", "确定",
       "[实测] 单变量对照（同二进制/同 INCAR/同栈上限，只改 NPAR）；"
       "机制 [官方] NCORE 页")
def r_crash_no_scf(ctx):
    """程序崩在**第一次 SCF 之前/之中** —— 要给出"先看并行分解"的处方。

    ⚠️ 这条规则**刻意把两件事分开**（它们原来被混在 `RUN.not_finished` 里）：
      · **没跑起来**（本规则）：`OSZICAR` **0 行迭代** + 有崩溃特征；
      · **跑了一半**（墙钟/被 kill）：已有若干次迭代。
    处方完全不同：前者要动**并行配置**，后者是续算/加机时。
    """
    info = ctx.get("log_info") or {}
    if not info.get("found"):
        return None
    crash = info.get("first_crash_line")
    if not crash:
        return None
    iters = ctx.get("oszicar_iters", 0)
    if iters > 0:
        return None            # 已经跑过 SCF ⇒ 不是"起不来"这一类

    distr = info.get("distr")
    cores = info.get("total_cores")
    incar = ctx.get("incar")
    tags = set(t.upper() for t in incar.tags) if incar else set()
    has_par = bool(tags & {"NCORE", "NPAR"})

    # 判据：**每个 band 落在 1 个核上**（= 默认 NCORE=1 的签名）
    one_band_per_rank = bool(distr and distr[0] == 1)

    ev = ["LOG 第一条崩溃：%s（第 %d 行）" % (crash[1], crash[2])]
    if cores:
        ev.append("running on %d total cores" % cores)
    if distr:
        ev.append("distr: one band on %d cores, %d groups" % distr)
    if iters == 0:
        ev.append("OSZICAR 迭代行数 = 0（**一次 SCF 都没走**）")
    if not has_par:
        ev.append("INCAR 里**没有** NCORE / NPAR（走默认）")

    diag = ("**程序在第一次 SCF 就崩了**（`OSZICAR` 一次迭代都没有）。"
            "这**不是**输入文件语法问题（那些会被 `validate.py` 抓住），"
            "而是**每个 rank 的资源需求超过了它拿到的上限** —— "
            "在并行分解上。")
    if one_band_per_rank:
        diag += ("\n        关键线索：横幅写 `one band on 1 cores` —— "
                 "**每个 band 落在一个 rank 上**（正是默认 `NCORE = 1` 的签名）。"
                 "此时该 rank 必须**独自完成整块 FFT**，"
                 "临时数组按整个网格分配 ⇒ 大体系 + 多 rank 时把每 rank 的"
                 "**栈/内存**撑爆。")
    diag += ("\n        ⚠️ 机制依据是 `[官方]` `references/official/pages/"
             "NCORE.md`：`NCORE=1` 时「投影函数必须**完整存在每个 rank 上**、"
             "**内存占用高**」；`NCORE ≈ √(可用 rank 数)` 则"
             "「**同时降低内存需求**与正交化成本」。"
             "官方原话称后者是 modern multi-core 机器的 **recommended regime**。")

    if one_band_per_rank:
        fix = ("**先动并行分解，不要先怀疑系统配置。**\n"
               "        ① 在 `INCAR` 里加一行 `NCORE ≈ √(可用 rank 数)`。"
               "16 rank ⇒ 先试 `NCORE = 4`，不行再 `8`。\n"
               "           ⚠️ **用 `NCORE`，不要用 `NPAR`**（`NPAR` 是 legacy，"
               "且**两者同时出现时 `NPAR` 优先**、`NCORE` 被静默忽略）。\n"
               "        ② 同时确认 `KPAR = 1`（Γ 点单点）。\n"
               "        ③ 改完**重跑**，看横幅是否变成 `one band on N cores, "
               "M groups`。\n"
               "        ⚠️ **在动系统/队列配置之前必须做完这一步。**")
    else:
        fix = ("并行分解看起来**不是**每个 band 一个 rank（横幅不是 "
               "`one band on 1 cores`）⇒ 先看 ①：\n"
               "        ① 你的 `INCAR` 里 `NCORE`/`NPAR` 是怎么写的？"
               "两者同时出现会让 `NCORE` 被静默忽略。\n"
               "        ② 试 `NCORE ≈ √(可用 rank 数)` 扫一遍（4 / 8 / 16）。\n"
               "        ③ 若都不行，再查内存/栈（`ulimit -s`、节点内存）。")

    return Symptom(
        "LAUNCH.crash_no_scf", "确定",
        "LOG 里有崩溃特征，但 **`OSZICAR` 一次 SCF 迭代都没有**：\n"
        "        %s" % crash[1],
        "%s:%d" % (ctx.get("LOG") or "LOG", crash[2]),
        diag, fix,
        "`OSZICAR` 里出现 `DAV:` / `RMM:` 行（即越过了崩点）。"
        "⚠️ **不要用 `exit code` 判断** —— `mpirun` 下崩溃时退出码可能仍是 "
        "0 或 255，语义不可靠。",
        "[官方] references/official/pages/NCORE.md（默认值的内存后果）；"
        "[实测] 单变量对照（只改 NPAR：默认⇒0 步 SCF 崩溃；NPAR=2⇒7 步 SCF 收敛）",
        "\n        ".join(ev))


# ⚠️ 等级**刻意降为"仅详细模式"**（见 CHANGELOG 的 CR-041）。
#    理由：实测它在 **98 个真实算例里触发 15 次**（≈15%）。
#    那些都不是错误——`NCORE` 与"生效值"不一致常常是 VASP 自己
#    为了整除而调整的。**15% 误报的规则等于噪声**，会让人学会
#    忽略整个诊断（对照 CR-009：那条规则曾误报 76/98）。
#    它仍然有价值（"你写的值没生效"是静默失效），但只该在
#    用户**主动要详细模式**时出现。
@_rule("LAUNCH.par_tags_inconsistent", "仅详细模式",
       "[官方] NCORE 页 / NPAR 页")
def r_par_tags_consistent(ctx):
    """`INCAR` 写的并行设置与 LOG 横幅**对不上** ⇒ 值得看一眼。

    官方明文：`NPAR` 与 `NCORE` 是**严格互逆**的
    （`NPAR × NCORE = available ranks`），且
    **`Do not set NCORE and NPAR at the same time`** ——
    同时出现时 **`NPAR` 优先**。
    ⇒ 这是个**静默失效**：你以为设了 `NCORE`，实际走的可能是 `NPAR`。

    ⚠️⚠️ **本条规则的设计经过一次返工，理由值得记住**
    （见 `CHANGELOG.md` 的 CR-041）：
    早期版本看到"你写 `NCORE=16`、横幅 `5`"就直接下结论
    「**你写的那行没生效**」。**那是个我没有依据的推断** ——
    实测那个算例是 **40 rank / `NCORE=16`**，而 `40 / 16 = 2.5`
    **不是整数**，VASP 显然自己调整了（报了 5）。
    官方 `NCORE` 页**没有**记载"不能整除时会怎样"。
    ⇒ 所以现在本条**只说可核对的事实**（写的值 ≠ 生效的值），
      **不猜机制**；把"官方明文的两种可能机制"与"官方未记载的情形"分开列。

    另一个官方**明文**的会改 `NCORE` 的场合（同页 Warning）：
    「用 OpenMP 线程或任何 GPU 卸载路径时，`NCORE` 会被**自动重置为 1**」。
    """
    info = ctx.get("log_info") or {}
    incar = ctx.get("incar")
    if not info.get("found") or incar is None:
        return None
    tags = set(t.upper() for t in incar.tags)
    both = {"NCORE", "NPAR"} <= tags
    distr = info.get("distr")
    cores = info.get("total_cores")
    kpar = 1
    try:
        kpar = incar.get_int("KPAR") or 1
    except Exception:                                        # noqa: BLE001
        kpar = 1
    problems = []

    if both:
        problems.append(
            "**`NCORE` 与 `NPAR` 同时出现在 `INCAR` 里** —— "
            "官方明文：*Do not set `NCORE` and `NPAR` at the same time*，"
            "同时出现时 **`NPAR` 优先**。⇒ 那两个值里有一个**没生效**。")

    actual = distr[0] if distr else None
    want = None
    for t in ("NCORE", "NPAR"):
        try:
            v = incar.get_int(t)
        except Exception:                                    # noqa: BLE001
            v = None
        if v:
            want = (t, v)
            break
    if actual and want and want[0] == "NCORE" and want[1] != actual:
        # ⚠️ 只陈述事实 + 给可核对的关系式，**不替 VASP 解释**
        line = ("你写了 `NCORE = %d`，但 **LOG 横幅显示实际是 %d**"
                "（`one band on %d cores`）—— **写的值与生效的值不一致**。"
                % (want[1], actual, actual))
        avail = None
        if cores:
            avail = cores // max(1, kpar)
            line += ("\n          （核对：可用 rank = %d 核 / KPAR %d = %d；"
                     "按官方关系式 `NPAR = 可用 rank / NCORE` 算，"
                     "`%d / %d` 不是整数。）" % (cores, kpar, avail,
                                                avail, want[1]))
        line += ("\n          ⚠️ **官方 `NCORE` 页没有记载「不能整除时怎么处理」。**"
                 "所以这里**只说「值不一致」这个可核对的事实**，"
                 "不替程序解释原因。")
        problems.append(line)

    if not problems:
        return None
    return Symptom(
        "LAUNCH.par_tags_inconsistent", "仅详细模式",
        "并行设置与程序实际采用的**不一致**：\n        " +
        "\n        ".join("· " + p for p in problems),
        str(ctx.get("INCAR") or "INCAR"),
        "`NCORE` / `NPAR` 的语义互逆，而程序在某些情况下会**自己决定**实际值"
        "（不是报错）。**官方明文记载的两种**是："
        "① 同时设 `NCORE` 与 `NPAR` ⇒ `NPAR` 优先；"
        "② 用 OpenMP 线程或 GPU 卸载路径 ⇒ `NCORE` 被重置为 1。"
        "实测还存在**官方未记载**的调整（见「实测」里的整除关系）—— 那一条"
        "本项目**不知道机制**，只能提示你去看横幅。",
        "① **只留一个**，推荐一律用 `NCORE`（`NPAR` 是 legacy，官方建议改用 "
        "`NCORE`）；\n"
        "        ② 改完**看 LOG 横幅**的 `one band on N cores` 是不是你想要的；\n"
        "        ③ 若想指定 `NCORE`，**让可用 rank 数能被它整除**"
        "（`可用 rank = 总核数 / KPAR`）。",
        "`grep -E \"distr:\" LOG` 里的 `one band on N cores` 等于你 `INCAR` 里 "
        "`NCORE` 的值。",
        "[官方] references/official/pages/NCORE.md（`NPAR = available ranks / "
        "NCORE`；`Do not set ... at the same time`；OpenMP/GPU 下重置为 1）、"
        "pages/NPAR.md",
        "实测生效值来自 LOG 横幅 `distr:` 行；"
        "整除核对（该算例 40 核 / NCORE 16 = 2.5，非整数）")


@_rule("LAUNCH.ulimit_redherring", "提示",
       "[实测] 该行在成功与失败的作业里**都会出现**")
def r_ulimit_red_herring(ctx):
    """`ulimit: stack size: cannot modify limit` —— **红鲱鱼**。

    本规则的价值是**防止误判**：这行在**成功**的作业里也会出现
    （队列的栈硬限由调度器设死，`ulimit -s unlimited` 必然失败）。
    它只是"这个队列不允许改栈"的**事实陈述**，
    **不是"栈不够"的证据**。
    """
    info = ctx.get("log_info") or {}
    if not info.get("found"):
        return None
    hit = [c for c in info.get("crashes", []) if c[0] == "stack_ulimit"]
    if not hit:
        return None
    return Symptom(
        "LAUNCH.ulimit_redherring", "提示",
        "日志里有：\n        %s" % hit[0][1],
        "%s:%d" % (ctx.get("LOG") or "LOG", hit[0][2]),
        "**这一行不能单独作为诊断依据。** 队列的栈硬限由调度器设死时，"
        "作业脚本里的 `ulimit -s unlimited` **必然**失败并打印这行 —— "
        "**在成功的作业里也会出现**。"
        "把它当成根因，会把你引向'去找管理员改队列配置'，"
        "而那通常**不是**真正的原因。",
        "① 先确认作业**是不是真的崩了**（看有没有 `forrtl`/`SIGSEGV`、"
        "`OSZICAR` 有没有迭代行）；"
        "② 若真的崩了，**先查并行分解**（见 `LAUNCH.crash_no_scf`），"
        "而不是先查栈上限。",
        "同一二进制、同一 `INCAR`、**同一栈上限**下改并行配置后能跑起来 —— "
        "那就证明栈上限不是根因。",
        "[实测] 该行在成功与失败的作业里都出现",
        "见 references/playbook.md 的「诊断反模式」一节（红鲱鱼）")


# ---------------------------------------------------------------------------
# 三、诊断主流程
# ---------------------------------------------------------------------------
def build_context(directory: str) -> dict:
    inp = vc.discover_inputs(directory)
    ctx = dict(inp)
    try:
        ctx["files"] = sorted(os.listdir(directory))
    except OSError:
        ctx["files"] = []
    ctx["steps"] = vc.outcar_ionic_steps(inp["OUTCAR"]) if inp["OUTCAR"] else []
    ctx["outcar_tail"] = ""
    if inp["OUTCAR"]:
        # 只读尾部：大文件不能整份读
        try:
            size = os.path.getsize(inp["OUTCAR"])
            with vc.open_maybe_gz(inp["OUTCAR"], "rb") as fh:
                if size > 200000:
                    fh.seek(max(0, size - 200000))
                ctx["outcar_tail"] = fh.read().decode("utf-8", errors="replace")
        except Exception:                                     # noqa: BLE001
            pass
    ctx["encut_outcar"] = vc.outcar_encut(inp["OUTCAR"]) if inp["OUTCAR"] else None
    # --- 作业"起没起来"这一层（见 LAUNCH.* 规则的说明）---
    # `LOG` 可能不存在（不一定会重定向到文件）⇒ 取不到就如实为 None，
    # 规则自己会降级为"未检查"，**不猜**。
    ctx["log_info"] = vc.parse_launch_log(inp.get("LOG") or "")
    ctx["oszicar_iters"] = (vc.oszsicar_iterations(inp["OSZICAR"])
                            if inp.get("OSZICAR") else 0)
    try:
        ctx["incar"] = vc.read_incar(inp["INCAR"]) if inp["INCAR"] else None
    except SystemExit:
        ctx["incar"] = None
    try:
        ctx["poscar"] = vc.read_poscar(inp["POSCAR"]) if inp["POSCAR"] else None
    except SystemExit:
        ctx["poscar"] = None
    try:
        ctx["potcar"] = (vc.parse_potcar_header(inp["POTCAR"])
                         if inp["POTCAR"] else None)
    except SystemExit:
        ctx["potcar"] = None
    return ctx


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="diagnose.py",
        description="从算例输出里找出症状，并给出诊断与处方（四要素齐全）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=没找到已知症状；1=目录/文件问题；2=用法错误；"
               "4=找到「确定」的问题；5=只有「提示」。\n"
               "⚠️ 没找到症状 **不等于** 算得对 —— 本工具只认它认识的模式。",
    )
    ap.add_argument("directory", nargs="?", default=".")
    ap.add_argument("--verbose", action="store_true", help="连「通过」的规则也列出来")
    ap.add_argument("--quiet", action="store_true",
                    help="只印规则号与症状一句话（便于批量跑多个目录）")
    ap.add_argument("--list-rules", action="store_true")
    args = ap.parse_args(argv)

    if args.list_rules:
        print("diagnose.py 的规则表（共 %d 条）：\n" % len(RULES))
        for rid, level, src, _fn in RULES:
            print("  %-26s %-6s %s" % (rid, level, src))
        print("\n⚠️ 这些规则**都没有在真机上做过正例/反例验证**")
        print("   （本机没有 VASP）。所以「确定」级只给「官方明文」或「算例实证」的条目。")
        print("   未覆盖的症状：本工具只认它认识的模式，见 USAGE.md 的诚实边界一节。")
        return EXIT_OK

    directory = args.directory
    if not os.path.isdir(directory):
        vc.die("不是一个目录：%s" % directory, EXIT_USER,
               "用法：python scripts/diagnose.py <算例目录>")

    ctx = build_context(directory)
    # ⚠️ `LOG` 必须在列表里 —— 它是 `LAUNCH.*` 那一层的唯一输入。
    #    早期版本漏了它，于是"读到的文件"看不出少了什么，
    #    而 LAUNCH 规则永远不触发（见 CHANGELOG 的更正记录）。
    have = [k for k in ("INCAR", "KPOINTS", "POSCAR", "POTCAR", "OUTCAR",
                        "OSZICAR", "vasprun", "LOG") if ctx.get(k)]
    if not have:
        vc.die("在 %s 里没找到任何 VASP 文件" % ctx["dir"], EXIT_USER)

    print("=" * 72)
    print("症状诊断 —— %s" % ctx["dir"])
    print("=" * 72)
    if args.quiet:
        pass
    else:
        print("读到的文件：%s" % ", ".join(have))
        if ctx["OUTCAR"]:
            print("程序版本：%s" % (vc.outcar_version(ctx["OUTCAR"]) or "（读不到）"))
        print()

    found, hints, passed, detailed = [], [], [], []
    for rid, level, src, fn in RULES:
        try:
            s = fn(ctx)
        except Exception as exc:                              # noqa: BLE001
            vc.warn("规则 %s 内部出错（已跳过）：%s" % (rid, exc))
            continue
        if s is None:
            passed.append((rid, level, src))
        elif s.level == "确定":
            found.append(s)
        elif s.level == "仅详细模式":
            detailed.append(s)
        else:
            hints.append(s)

    def show(items, header):
        if not items:
            return
        if args.quiet:
            for s in items:
                print("  ● [%s] %s" % (s.rule_id,
                                       s.symptom.replace("\n", " ")[:110]))
            return
        print("── %s ──\n" % header)
        for s in items:
            print("● [%s] %s" % (s.rule_id, s.symptom))
            print("  位置：%s" % s.where)
            if s.evidence:
                print("  实测：%s" % s.evidence)
            print("  诊断：%s" % s.diagnosis)
            print("  处方：    %s" % s.fix)
            print("  判据：%s" % s.criterion)
            print("  依据：%s" % s.source)
            print()

    show(found, "找到的问题（有依据）")
    show(hints, "提示（需要你自己判断）")
    if args.verbose:
        show(detailed, "仅详细模式（常见做法，不是问题）")

    if args.verbose:
        print("── 未触发的规则（%d 条）──" % len(passed))
        for rid, level, src in passed:
            print("  · %s  [%s]" % (rid, level))
        print()

    print("-" * 72)
    print("结论：确定的问题 %d 项，提示 %d 项，仅详细模式 %d 项，未触发 %d 项"
          % (len(found), len(hints), len(detailed), len(passed)))
    if not found and not hints:
        print("      → 没找到本工具认识的症状。")
    if args.quiet:
        return (EXIT_FOUND if found else (EXIT_HINT if hints else EXIT_OK))
    print()
    print("⚠️ **没找到症状不等于算得对。** 本工具只认它认识的模式。")
    print("   建议同时跑：")
    print("     python scripts/validate.py %s     # 输入对不对" % directory)
    print("     python scripts/compare.py  %s     # 结果自不自洽" % directory)
    print()
    print("⚠️ 本工具的规则**都没有在真机上做过正例/反例验证**（本机没有 VASP）。")
    print("   `确定` 级只给「官方明文」或「算例实证」的条目；其余一律降为「提示」。")
    print("   未覆盖的症状请查 references/playbook.md（73 条症状→处方）。")

    if found:
        return EXIT_FOUND
    if hints:
        return EXIT_HINT
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
