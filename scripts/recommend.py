#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""recommend.py —— 参数推荐（**零依赖**）

它给什么
========
给定「算什么目标」+「体系含哪些元素」+「几维」，输出一组**带理由与代价**的
参数推荐。**每条都带出处**（`[官方]`/`[算例]`/`[经验]` 等，见
`references/_WRITING_CONTRACT.md`）。

它**不**做什么
=============
- ❌ **不替你决定**。它给的是**起点与取舍**，不是"照抄就对"。
- ❌ **不保证收敛**。`ENCUT`/k 点的收敛值**必须你自己测**
  （官方唯一的要求就是这个，见 `references/decide.md` §4.2）。
- ❌ **不读你的 POTCAR**（除 `--potcar` 显式给出时只读头部数字）。
- ❌ **不评价赝势选型**（该不该用 `_pv`/`_d`、该用 PBE 还是 PW91）。

⚠️ **本工具的所有推荐值都没有在真机上验证过**（构建环境没有 VASP）。
它们的定位是"安全的起点"，出处逐条标注，便于你**自己判断该不该采信**。

它与 `wizard.py` 的分工
=====================
| 工具 | 输出 | 什么时候用 |
|---|---|---|
| `wizard.py` | **文件**（`INCAR`/`KPOINTS`/…） | 要直接开算 |
| **`recommend.py`** | **文字**（推荐 + 理由 + 代价 + 出处） | 想先搞明白为什么 |

两者共用**同一份**目标定义（`wizard.GOALS`）—— 避免"两份逻辑给出不同答案"。

用法
----
    python scripts/recommend.py --list-goals
    python scripts/recommend.py --goal slab-adsorption --elements "Pt O"
    python scripts/recommend.py --goal dos --elements "Co N C" --potcar ./POTCAR
    python scripts/recommend.py --goal bulk-relax --elements "Fe O" --metal
    python scripts/recommend.py --goal slab-relax --elements "Au" --dim 2d --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402
from wizard import GOALS, PARAM_DOC, build_kpoints             # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3

# 常见磁性元素（Z 序号）。用途：提醒用户"要不要 ISPIN=2"。
# ⚠️ 这是**经验清单**，不是官方定义；它的作用是"提醒"，不是"判定"。
MAGNETIC_Z = {24, 25, 26, 27, 28, 29, 42, 44, 45, 46, 57, 58, 59, 60, 61, 62,
              63, 64, 65, 66, 67, 68, 69, 70, 71, 92, 93, 94, 95, 96}

# 常见强关联元素（需要认真考虑 DFT+U）。同样是**经验清单**。
CORRELATED_Z = {22, 23, 24, 25, 26, 27, 28, 29, 40, 41, 42, 43, 44, 45, 46,
                57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
                90, 91, 92, 93, 94, 95, 96}

# 关键词 → 是否"金属性"的经验提示。**不是判定**，只用于提醒。
# 依据：真实算例里 Ag/Au/Ni/Co 表面用 ISMEAR=1，Fe2O3/Al2O3/MoS2 用 ISMEAR=0。
METAL_HINT_Z = {3, 4, 11, 12, 13, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                30, 31, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
                50, 55, 56, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83}


def _z_of(sym: str):
    return vc.Elements.z(sym)


def analyse_elements(elements):
    """把元素列表分析成几条**提醒**（不是判定）。"""
    syms = [s for s in elements.replace(",", " ").split() if s]
    unknown = [s for s in syms if not vc.Elements.is_known(s)]
    zs = [_z_of(s) for s in syms if vc.Elements.is_known(s)]
    return {
        "symbols": syms,
        "unknown": unknown,
        "magnetic": [s for s in syms if _z_of(s) in MAGNETIC_Z],
        "correlated": [s for s in syms if _z_of(s) in CORRELATED_Z],
        "metal_like": [s for s in syms if _z_of(s) in METAL_HINT_Z],
        "lanthanide_actinide": [s for s in syms
                                if _z_of(s) is not None and (58 <= _z_of(s) <= 71
                                                             or _z_of(s) >= 90)],
    }


def recommend(goal_key: str, elements: str, dim: str, metal_override=None,
              potcar_path=None) -> dict:
    G = GOALS[goal_key]
    info = analyse_elements(elements)
    params = dict(G.params)

    # --- ENCUT ---
    encut = None
    encut_note = ""
    if potcar_path and os.path.exists(potcar_path):
        pc = vc.parse_potcar_header(potcar_path)
        enmax = pc.max_enmax()
        if enmax:
            # 变胞目标按官方给的例子抬高截断能；定胞目标用 max(ENMAX) 就够。
            # `[官方]` references/official/pages/ISIF.md:38：
            #   `volume changes should be done only with an increased energy
            #    cutoff, e.g., ENCUT = 1.3×max(ENMAX), and PREC=High.`
            # ⚠️ 本项目在这件事上错过两次（CR-002 → CR-026），
            #    现口径：**1.3× 是官方给变胞场景的值，不是通用推荐值；
            #    被弃用的是 `PREC=High` 开关，不是这个倍数。**
            # ⚠️ `G` 是 `Goal` **对象**（有 `.params` 字典属性），不是 dict。
            _var_cell = str(G.params.get("ISIF", "")) in ("3", "7", "8")
            factor = 1.3 if _var_cell else 1.0
            encut = round(enmax * factor, 1)
            if _var_cell:
                encut_note = (
                    "从你的 POTCAR 读到 max(ENMAX) = %.3f eV。这是**变胞**目标"
                    "（`ISIF` 会改晶胞），所以按**官方明文给的值**取 1.3 倍"
                    "（`[官方]` references/official/pages/ISIF.md:38）—— "
                    "因为变胞时 PAW 基组不跟着变，有 **Pulay 应力**。"
                    "⚠️ 但**它不代表收敛**：官方同时要求"
                    "`The convergence … should always be checked`。"
                    "**请自己测一遍，并把最终值显式写进 INCAR。**" % enmax)
            else:
                encut_note = (
                    "从你的 POTCAR 读到 max(ENMAX) = %.3f eV。这是**定胞**目标"
                    "（不改晶胞），所以**不需要**变胞场景那个 1.3 倍抬高。"
                    "⚠️ 官方仍要求 `The convergence … should always be checked` "
                    "—— **请从这个值起步自己做 ENCUT 收敛测试**，"
                    "并把最终值显式写进 INCAR。" % enmax)
    if encut is None:
        encut = 400.0
        encut_note = ("**400 eV 是一个保守的猜测值**，因为你没给 `--potcar`。"
                      "请用你自己的 POTCAR 读 `max(ENMAX)` 再定，"
                      "并做收敛测试。`scripts/validate.py --potcar` 会帮你核对。")

    # --- 展宽 ---
    if metal_override is True:
        ismear, sigma, smear_note = 1, 0.2, (
            "你标了金属。真实算例里金属体系**一致**用 `ISMEAR=1` + `SIGMA=0.2`"
            "（`day2/Ag`、`day2/au111-opt`、`day2/ni-co`、`day3/ts/dim`、"
            "`4-thermo/7-2-adsorptionO-Au/hollow`）。")
    elif metal_override is False:
        ismear, sigma, smear_note = 0, 0.05, (
            "你标了绝缘体/半导体。官方明文：MP 展宽（`ISMEAR>0`）"
            "对绝缘体不安全（`partial occupancies can be unphysical`）。"
            "真实算例 `day1/fe2o3` 用 `ISMEAR=0, SIGMA=0.05`。")
    elif goal_key == "dos":
        ismear, sigma, smear_note = -5, 0.05, (
            "DOS 用四面体方法（`ISMEAR=-5`）。⚠️ **官方明文：四面体方法必须用 "
            "Γ 居中的 k 点**；且 **ISMEAR=-5 要求 NKPT ≥ 4**，"
            "k 点太少会报 `VERY BAD NEWS! ... Tetrahedron method fails for NPKT<4`。")
    elif goal_key == "molecule":
        ismear, sigma, smear_note = 0, 0.01, "分子有能隙，用小 `SIGMA`。"
    elif info["metal_like"] and not info["correlated"]:
        ismear, sigma, smear_note = 1, 0.2, (
            "你的元素里有金属性元素（%s）—— **提醒**你考虑 `ISMEAR=1`。"
            "⚠️ 这只是**经验清单**的提醒，不是判定；"
            "若你的体系有带隙（氧化物、半导体），应当用 `ISMEAR=0`。"
            % " ".join(info["metal_like"]))
    else:
        ismear, sigma, smear_note = 0, 0.05, (
            "默认给 `ISMEAR=0`（对绝缘体安全）。若体系是金属，"
            "改成 `ISMEAR=1` + `SIGMA=0.2`。")
    params["ISMEAR"], params["SIGMA"] = ismear, sigma

    # --- 自旋 ---
    spin_note = ""
    if info["magnetic"]:
        params["ISPIN"] = 2
        params["MAGMOM"] = "NIONS 个初值"
        spin_note = (
            "⚠️ 含磁性元素（%s）⇒ 用 `ISPIN=2` 且**必须显式写 `MAGMOM`**。"
            "官方明文：`The final magnetic state strongly depends on the initial "
            "values for MAGMOM`，并建议取实验磁矩的 **1.2–1.5 倍**。"
            "真实算例写法：反铁磁 `MAGMOM = 5.0 -5.0 5.0 -5.0 6*0.0`；"
            "单中心 `MAGMOM = 32*0.0 2.0 0.0`。"
            % " ".join(info["magnetic"]))
    elif info["lanthanide_actinide"]:
        params["ISPIN"] = 2
        params["MAGMOM"] = "NIONS 个初值"
        spin_note = ("含镧系/锕系元素 —— 通常要 `ISPIN=2` 且认真考虑 DFT+U。")
    else:
        spin_note = ("你的元素不在常见磁性清单里。⚠️ 清单是**经验**的，"
                     "不是判定 —— 不确定时先跑一次 `ISPIN=2` 看最终磁矩是否为零。")

    # --- DFT+U ---
    ldau_note = ""
    if info["correlated"]:
        ldau_note = (
            "⚠️ 含强关联元素（%s）：认真考虑 DFT+U。"
            "真实算例 `day1/fe2o3` 用 `LDAU=.TRUE.`、`LDAUTYPE=2`、"
            "`LDAUL=2 -1`、`LDAUU=5.3 0.0`、`LDAUJ=0.0 0.0`、`LMAXMIX=4`。\n"
            "    ⚠️ **引用 U 值必须注明写法**：本项目的讲师模板写 "
            "`LDAUU=4.6, LDAUJ=0.4`（U_eff=4.2），而讲义与真实算例写 "
            "`LDAUU=5.3, LDAUJ=0.0`（U_eff=5.3）—— **两者相差 1.1 eV**。\n"
            "    ⚠️ `LMAXMIX` 官方明文：DFT+U 含 d 电子用 **4**、含 f 电子用 **6**；"
            "**DFT+U 的能带计算（`ICHARG=11`）严格必须**。"
            % " ".join(info["correlated"]))

    # --- k 点 ---
    kp_text = build_kpoints(goal_key, dim)
    kp_note = (
        "生成的网格是 **Γ 居中** 的。理由（官方明文）："
        "①规则网格是生产计算首选；②四面体方法**必须** Γ 居中；"
        "③**fcc / hexagonal 晶格只能**用 Γ 居中 —— "
        "Monkhorst-Pack 在偶数细分时会破坏对称性，可能直接报 "
        "`IBZKPT` 与 `generating k-lattice` 的错误。\n"
        "    网格数是**起点**，必须做 k 点收敛测试。")

    return {
        "goal": goal_key,
        "goal_title": G.title,
        "goal_desc": G.desc,
        "goal_why": G.why,
        "goal_needs": list(G.needs),
        "goal_notes": list(G.notes),
        "elements": info,
        "params": params,
        "encut": encut,
        "encut_note": encut_note,
        "smear_note": smear_note,
        "spin_note": spin_note,
        "ldau_note": ldau_note,
        "kpoints": kp_text,
        "kpoints_note": kp_note,
        "dim": dim,
    }


def render(r: dict) -> None:
    print("=" * 72)
    print("参数推荐 —— %s" % r["goal_title"])
    print("=" * 72)
    print("目标：%s" % r["goal_desc"])
    print("为什么：%s" % r["goal_why"])
    if r["goal_needs"]:
        print("需要你先准备：%s" % "；".join(r["goal_needs"]))
    print()
    print("── 推荐的参数（**起点，不是收敛值**）──")
    for k in sorted(r["params"]):
        doc = PARAM_DOC.get(k, ("", "（本工具未收录该参数的说明）"))
        print("  %-10s = %-22s %s" % (k, r["params"][k], doc[1]))
    print("  %-10s = %-22s %s" % ("ENCUT", "%.1f" % r["encut"], r["encut_note"]))
    print()
    print("── KPOINTS ──")
    for line in r["kpoints"].split("\n"):
        if line:
            print("  " + line)
    print("  " + r["kpoints_note"].replace("\n    ", "\n  "))
    print()
    print("── 展宽的选择 ──")
    print("  " + r["smear_note"])
    print()
    print("── 自旋 ──")
    print("  " + r["spin_note"])
    if r["ldau_note"]:
        print()
        print("── DFT+U ──")
        print("  " + r["ldau_note"])
    if r["elements"]["unknown"]:
        print()
        print("⚠️ 认不出的元素符号：%s" % " ".join(r["elements"]["unknown"]))
        print("   本工具内置元素表只覆盖 1–96 号；**认不出不等于非法**。")
    if r["goal_notes"]:
        print()
        print("── 这个目标特有的注意事项 ──")
        for n in r["goal_notes"]:
            print("  · " + n)

    # 版本提醒（见 references/VERSIONS.md）。
    # ⚠️ 这一段**必须打**，因为上面那些推荐值是按"较新的 VASP"给的，
    #    而用老版本时**部分标签可能根本不存在**，且程序常常**静默忽略**。
    print()
    print("── ⚠️ 版本提醒（**这条会影响上面所有推荐值**）──")
    print("  本 skill 的知识来自**不同世代的 VASP**：")
    print("    · 官方 wiki 语料是 **6.6 时代**的；")
    print("    · 而 things to study 的 98 个真实算例**全部是 5.4.4**。")
    print("  ⇒ **报参数前先确认你的版本**（跑完看 `OUTCAR` 第一行，形如 "
          "`vasp.5.4.4.…`），")
    print("     或把版本告诉校验器：`validate.py <目录> --vasp-version 5.4.4`。")
    print("  ⚠️ VASP 对 `INCAR` 里**不认识的标签**常常**静默忽略** ——")
    print("     你以为设了、其实没生效，而且**不会有任何报错**。")
    print("  查某个标签的版本门槛：")
    print("     `python references/official/_extract_versions.py --gate <标签>`")
    print("  查你那个版本的已知缺陷：")
    print("     `python references/official/_extract_known_issues.py "
          "--for-version <你的版本>`")
    print("  总纲：`references/VERSIONS.md`")
    print()
    print("-" * 72)
    print("⚠️ 这些数值是**安全的起点**，不是「验证过的正确答案」。")
    print("   官方唯一的要求是：**显式写 ENCUT，并自己做收敛测试**")
    print("   （见 references/decide.md §4.2 与 §3）。")
    print("   收敛判据：相邻 ENCUT / k 点的总能量差 < 1 meV/atom。")
    print()
    print("下一步：")
    print("  python scripts/wizard.py --goal %s --elements \"%s\" ..."
          % (r["goal"], " ".join(r["elements"]["symbols"])))
    print("  python scripts/validate.py <算例目录> --potcar <POTCAR>")
    print()
    print("更细的理由与代价：references/decide.md；出错了：references/playbook.md")


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="recommend.py",
        description="参数推荐（带理由、代价与出处；**不替你决定**）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="⚠️ 所有推荐值都**未在真机上验证过**（构建环境没有 VASP）。\n"
               "   它们是「安全的起点」，出处逐条标注。\n"
               "退出码：0=成功；1=参数问题；2=用法错误；3=缺依赖。",
    )
    ap.add_argument("--goal", help="计算目标（见 --list-goals）")
    ap.add_argument("--elements", default="",
                    help="元素符号，空格分隔（**顺序应与 POSCAR 一致**）")
    ap.add_argument("--dim", choices=["3d", "2d", "1d", "0d"], default="3d")
    ap.add_argument("--metal", action="store_true", help="体系是金属")
    ap.add_argument("--insulator", action="store_true",
                    help="体系是绝缘体/半导体")
    ap.add_argument("--potcar", help="你本地的 POTCAR 路径"
                                     "（**只读头部**用于定 ENCUT，不复制不写出）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list-goals", action="store_true")
    args = ap.parse_args(argv)

    if args.list_goals:
        print("可用的计算目标（共 %d 个）：\n" % len(GOALS))
        for k, g in GOALS.items():
            print("  %-18s %s" % (k, g.title))
            print("      %s" % g.desc)
        print("\n用法：python scripts/recommend.py --goal <key> "
              "--elements \"Pt O\" [--metal]")
        return EXIT_OK

    if not args.goal:
        vc.die("没有指定计算目标。", EXIT_USAGE,
               "用 --goal <key>，或加 --list-goals 看有哪些目标。")
    if args.goal not in GOALS:
        vc.die("不认识的目标：%s" % args.goal, EXIT_USAGE,
               "可用目标：%s" % ", ".join(GOALS.keys()))
    if not args.elements:
        vc.warn("没给 --elements —— 自旋/DFT+U 的提醒会缺失。"
                "（这不影响其它参数）")
    if args.metal and args.insulator:
        vc.warn("同时给了 --metal 与 --insulator，按金属处理。")

    metal = True if args.metal else (False if args.insulator else None)
    r = recommend(args.goal, args.elements, args.dim,
                  metal_override=metal, potcar_path=args.potcar)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        return EXIT_OK
    render(r)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
