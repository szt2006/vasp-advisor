#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""parse_output.py —— 从 VASP 输出里**抽取数值**（机器可读，**零依赖**）

它和 `compare.py` 的分工
=======================
| 工具 | 输出 | 用途 |
|---|---|---|
| `compare.py` | 带判断的**报告** | 人读："有没有问题" |
| **`parse_output.py`** | **纯数据（TSV / JSON）** | **脚本接**：拿去画图、批量汇总、拟合 |

`parse_output.py` **不做任何判断**，只把数读出来。判断交给 `compare.py`
与 `diagnose.py`。这样"抽取"与"判断"各只有一份实现（见 MAINTENANCE.md：
不要出现两份逻辑）。

抽什么
======
- 程序版本（**每次都要带**——输出格式会跨版本漂移）
- 每个离子步：`energy(sigma->0)`、`free energy TOTEN`、`E-fermi`、
  最大力、RMS 力、`total drift`、SCF 步数
- 收敛状态：是否达到离子判据、电子循环收敛了几次
- 实际生效的关键参数（从 OUTCAR 的回显里读，**这是最可信的来源**）

⚠️ **能量的口径**：默认输出 `energy(sigma->0)`（外推到 `SIGMA→0`），
**不是** `free energy TOTEN`（含展宽熵项 `−TS`，不同展宽参数之间不可比）。
要 `TOTEN` 请显式加 `--toten`。

用法
----
    python scripts/parse_output.py <算例目录>
    python scripts/parse_output.py <算例目录> --json
    python scripts/parse_output.py <算例目录> --csv energies.csv
    python scripts/parse_output.py <目录1> <目录2> ... --summary
    python scripts/parse_output.py <算例目录> --param ENCUT

退出码
------
0 = 成功 · 1 = 目录/文件问题 · 2 = 用法错误 · 3 = 没有可解析的输出
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3


def parse_one(directory: str) -> dict:
    inp = vc.discover_inputs(directory)
    d = {"dir": inp["dir"], "version": "", "n_ionic_oszicar": None,
         "e0_oszicar": None, "encut_outcar": None, "nions_outcar": None,
         "n_electronic_converged": 0, "steps": [], "params": {},
         "source_files": {}, "warnings": []}
    for k in ("INCAR", "KPOINTS", "POSCAR", "POTCAR", "OUTCAR", "OSZICAR",
              "vasprun"):
        if inp.get(k):
            d["source_files"][k] = os.path.basename(inp[k])

    if inp["OUTCAR"]:
        d["version"] = vc.outcar_version(inp["OUTCAR"])
        d["encut_outcar"] = vc.outcar_encut(inp["OUTCAR"])
        d["nions_outcar"] = vc.outcar_nions(inp["OUTCAR"])
        steps = vc.outcar_ionic_steps(inp["OUTCAR"])
        n_conv = 0
        for _ln, line in vc.iter_lines(inp["OUTCAR"]):
            if "aborting loop because EDIFF is reached" in line:
                n_conv += 1
        d["n_electronic_converged"] = n_conv
        for st in steps:
            d["steps"].append({
                "index": st.index,
                "energy_sigma0": st.energy_sigma0,
                "toten": st.toten,
                "fermi": st.fermi,
                "max_force": st.max_force,
                "rms_force": st.rms_force,
                "total_drift": list(st.total_drift) if st.total_drift else None,
                "n_forces": len(st.forces),
                "reached_required": st.reached_required,
            })
        # 从 OUTCAR 回显里读**实际生效**的关键参数（比 INCAR 可信）
        wanted = ("ENCUT", "ISPIN", "ISMEAR", "SIGMA", "EDIFF", "EDIFFG",
                  "NELM", "NSW", "IBRION", "ISIF", "ISYM", "PREC", "LREAL",
                  "GGA", "NELECT", "LMAXMIX", "IVDW")
        for _ln, line in vc.iter_lines(inp["OUTCAR"]):
            for key in wanted:
                if key in d["params"]:
                    continue
                m = __import__("re").search(
                    r"(?<![A-Z_])%s\s*=\s*([-\d.Ee+]+|\.[A-Za-z]+\.|[A-Za-z]+)"
                    % key, line)
                if m:
                    d["params"][key] = m.group(1)
    else:
        d["warnings"].append(
            "没有 OUTCAR —— 离子步能量/力/参数回显都读不到（只剩 OSZICAR 的能量）")

    if inp["OSZICAR"]:
        e0, n = vc.oszicar_last_energy(inp["OSZICAR"])
        d["e0_oszicar"] = e0
        d["n_ionic_oszicar"] = n
    if inp["vasprun"]:
        d["vasprun"] = vc.vasprun_meta(inp["vasprun"])
    return d


def print_table(d: dict, use_toten: bool = False) -> None:
    key = "toten" if use_toten else "energy_sigma0"
    print("目录：%s" % d["dir"])
    print("版本：%s" % (d["version"] or "（读不到）"))
    print("源文件：%s" % ", ".join("%s=%s" % kv
                                   for kv in sorted(d["source_files"].items())))
    if d["params"]:
        print("OUTCAR 回显的关键参数：%s"
              % "  ".join("%s=%s" % kv for kv in sorted(d["params"].items())))
    print("离子步：OUTCAR %d / OSZICAR %s ；电子循环按 EDIFF 收敛 %d 次"
          % (len(d["steps"]), d["n_ionic_oszicar"],
             d["n_electronic_converged"]))
    if not d["steps"]:
        print("（没有解析到离子步 —— 见 warnings）")
        for w in d["warnings"]:
            print("  警告：%s" % w)
        return
    print()
    print("  %-5s %18s %18s %12s %12s %12s %s"
          % ("step", "energy(sigma->0)", "free energy TOTEN", "max|F|",
             "rms|F|", "|drift|", "收敛"))
    for s in d["steps"]:
        drift = s["total_drift"]
        dmag = ("%.6f" % (sum(x * x for x in drift) ** 0.5)) if drift else "-"
        print("  %-5d %18s %18s %12s %12s %12s %s"
              % (s["index"],
                 ("%.8f" % s["energy_sigma0"]) if s["energy_sigma0"] is not None else "-",
                 ("%.8f" % s["toten"]) if s["toten"] is not None else "-",
                 ("%.5f" % s["max_force"]) if s["max_force"] is not None else "-",
                 ("%.5f" % s["rms_force"]) if s["rms_force"] is not None else "-",
                 dmag,
                 "已收敛" if s["reached_required"] else ""))
    if len(d["steps"]) > 1:
        e_first = d["steps"][0][key]
        e_last = d["steps"][-1][key]
        if e_first is not None and e_last is not None:
            print("\n  ΔE（首步 → 末步，用 %s）= %+.6f eV" % (key, e_last - e_first))
    print("\n⚠️ 默认用 `energy(sigma->0)`（外推到 SIGMA→0）。")
    print("   `free energy TOTEN` 含展宽熵项 −TS，**不同展宽参数之间不可比**。")


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="parse_output.py",
        description="从 VASP 输出里抽取数值（机器可读；**不做判断**）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=成功；1=目录问题；2=用法错误；3=没有可解析的输出。\n"
               "判断交给 compare.py / diagnose.py；本工具只读数。",
    )
    ap.add_argument("directories", nargs="*", default=["."],
                    help="一个或多个算例目录")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--csv", help="把每个离子步写成 CSV 到这个文件")
    ap.add_argument("--summary", action="store_true",
                    help="多个目录时只印一行汇总（便于批量比较）")
    ap.add_argument("--toten", action="store_true",
                    help="用 free energy TOTEN 而不是 energy(sigma->0)")
    ap.add_argument("--param", help="只印 OUTCAR 回显里的这一个参数")
    args = ap.parse_args(argv)

    dirs = args.directories or ["."]
    for d in dirs:
        if not os.path.isdir(d):
            vc.die("不是一个目录：%s" % d, EXIT_USER)

    results = []
    for d in dirs:
        try:
            results.append(parse_one(d))
        except SystemExit:
            raise
        except Exception as exc:                              # noqa: BLE001
            vc.warn("解析 %s 失败（已跳过）：%s" % (d, exc))

    if not results:
        vc.die("没有可解析的算例", EXIT_DEP,
               "本工具读的是**计算结果**（OUTCAR/OSZICAR）。"
               "若只想校验输入，用 scripts/validate.py")

    if args.param:
        for r in results:
            print("%s\t%s" % (r["dir"], r["params"].get(args.param.upper(), "")))
        return EXIT_OK

    if args.json:
        for r in results:
            r.pop("warnings", None)
        print(json.dumps(results if len(results) > 1 else results[0],
                         ensure_ascii=False, indent=2))
        return EXIT_OK

    if args.csv:
        key = "toten" if args.toten else "energy_sigma0"
        with open(args.csv, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("directory,step,%s,toten,fermi,max_force,rms_force,"
                     "drift_x,drift_y,drift_z,reached_required\n" % key)
            for r in results:
                for s in r["steps"]:
                    dr = s["total_drift"] or ["", "", ""]
                    fh.write("%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % (
                        r["dir"], s["index"],
                        "" if s[key] is None else "%.8f" % s[key],
                        "" if s["toten"] is None else "%.8f" % s["toten"],
                        "" if s["fermi"] is None else "%.6f" % s["fermi"],
                        "" if s["max_force"] is None else "%.6f" % s["max_force"],
                        "" if s["rms_force"] is None else "%.6f" % s["rms_force"],
                        dr[0], dr[1], dr[2],
                        s["reached_required"]))
        print("已写出 %s（%d 个目录）" % (args.csv, len(results)))
        return EXIT_OK

    if args.summary and len(results) > 1:
        key = "toten" if args.toten else "energy_sigma0"
        print("%-46s %-12s %8s %18s %12s %12s"
              % ("目录", "版本", "离子步", key, "末步max|F|", "已收敛"))
        for r in results:
            last = r["steps"][-1] if r["steps"] else {}
            e = last.get(key)
            mf = last.get("max_force")
            print("%-46s %-12s %8d %18s %12s %12s"
                  % (os.path.basename(r["dir"]) or r["dir"],
                     (r["version"].split()[0][:12] if r["version"] else "?"),
                     len(r["steps"]),
                     ("%.6f" % e) if e is not None else "-",
                     ("%.5f" % mf) if mf is not None else "-",
                     "是" if last.get("reached_required") else "否"))
        print("\n（判断「有没有问题」请用 compare.py / diagnose.py）")
        return EXIT_OK

    for i, r in enumerate(results):
        if i:
            print()
        print_table(r, use_toten=args.toten)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
