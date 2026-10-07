#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_inventory_assets.py —— 登记 LVTHW 附带的脚本与数据（**不复制内容，只登记**）

为什么需要它
============
《Learn VASP The Hard Way》原站每篇都挂着一个同名 asset 目录，
里面除了配图，还有**一批可直接用的脚本与小数据**：

| 类型 | 例子 | 价值 |
|---|---|---|
| 功函数 | `ex50/vtotav-v5.2.f`（Fortran）、`ex50/wplot.py`、`ex52/get-vacuum.py` | **`LOCPOT` 平面平均的参考实现** —— 本 skill 的 `postprocess.py` 核对了它的算法 |
| 坐标转换 | `ex51/dire2cart.py` | Direct→Cartesian + 保留 `T T T` |
| 排序/整理 | `ex59/sortcar.py` | `CONTCAR` 整理 |
| 批量处理 | `ex61/script_yh.zip`、`ex63/scripts-ex63.zip` | 命名/归档类脚本 |
| 计算题包 | `ex67/ex67-exercise.zip` | 一整套练习输入 |
| 建模 | `A19/expand.py`、`A20/smiles_to_xyz.py`、`A24/test.py` | 扩胞 / SMILES→XYZ / 迁移路径 |
| 数据 | `A26/materials_bg_gt_4.csv`（237 KB）、`A24/pda.vasp`、`A26/*.ipynb` | 带隙数据、迁移轨迹、Notebook |
| **书** | `ex15/Density_Functional_Theory_A_Practical_Introduction.zip`（9.5 MB） | ⚠️ **第三方教材，有版权** |

⚠️ **两条硬约束**
----------------
1. **不把内容复制进仓库**。本脚本只输出**清单**（路径 / 大小 / 类型 / 一句话用途），
   用途说明由人工/精读报告补。理由：
   - 版权（`ex15` 那本书、Notebook 里的数据）；
   - 体积（`pda.vasp` 434 KB、`materials_bg_gt_4.csv` 237 KB、
     `ex67-exercise.zip` 24.7 KB —— 单看不大，但**这一层的规矩是一律不复制**）；
   - **原始素材层已经逐字保留了正文**，脚本属于"外部工具"，不进交付物。

2. **不把 `POTCAR` 相关的东西写进清单正文**。
   `A05` 那个"自动生成 POTCAR 的脚本"是**教学材料**；
   本 skill 的边界是**不生成、不复制 `POTCAR`**（见 `MAINTENANCE.md` §0.2）。
   所以清单里对它的记载只写"⚠️ 该脚本会代为拼接 `POTCAR` —— 本 skill **不采用**
   它的 '生成' 部分，只参考它的 '顺序校验' 思路"。

用法
----
    python references/raw/_inventory_assets.py --src "<LVTHW-master 目录>"
    python references/raw/_inventory_assets.py --src "..." --only-scripts
"""

from __future__ import annotations

import argparse
import os
import sys

# 我们关心哪些后缀（其余是配图/打赏码/二维码，不进清单）
KEEP_EXT = {".py", ".ipynb", ".f", ".sh", ".zip", ".csv", ".vasp", ".vesta",
            ".txt", ".pdf", ".json", ".cif", ".xyz"}

# 明确"要提醒"的条目（逐条列理由，**不用宽泛通配**）
NOTES = {
    "vtotav": "VASP 官方工具源码（Fortran）：读 LOCPOT 做**平面平均**，"
              "输出 VLINE。本 skill 的 postprocess.py 已核对过它的索引用法。",
    "wplot.py": "画平面平均势曲线（需要 matplotlib）。读的是 VLINE/LOCPOT_Z。",
    "wplot-f.py": "同上，读 Fortran 版输出。",
    "get-vacuum.py": "**从平面平均势估真空能级** —— 取「最高原子 z 与晶胞 z 的中点」"
                     "±1 Å 求平均。⚠️ 它自己写明「这只是粗略估计」，"
                     "且要求**先看图确认中点落在平台上**。Python 2 语法。",
    "dire2cart.py": "Direct → Cartesian 转换，**会保留 Selective dynamics 的 T/F**。"
                    "Python 2 语法。",
    "sortcar.py": "CONTCAR/POSCAR 整理脚本。",
    "expand.py": "ASE 扩胞小脚本。",
    "smiles_to_xyz.py": "SMILES → XYZ（建初始构型用）。",
    "test.py": "离子迁移相关的小脚本。",
    "li_conductivity.py": "离子电导率后处理。",
    "getjpg.py": "🟡 从网页抓配图的小工具 —— **与 VASP 无关**，只是作者的写作辅助。",
}

COPYRIGHT_WARN = {
    "Density_Functional_Theory_A_Practical_Introduction.zip":
        "⛔ **第三方教材（有版权）** —— 原站附的是下载包。"
        "本项目的规矩是**版权不明/受限的东西不进仓库**，"
        "引用其内容时只标『作者推荐的书 + 章节』，不放文件。",
    "IDM_Vaspwiki.pdf": "🟡 VASP wiki 的 Improved Dimer 页导出 —— "
                        "来源是官方 wiki，但**导出件本身不必入库**（官方页已在 G 层）。",
    "Ubuntu_A23.pdf": "🟡 系统安装类操作记录 —— 非 VASP 知识。",
    "通过ASE获取原子之间的距离.pdf": "🟡 该篇的 PDF 版 —— 正文已在 E 层。",
}

POTCAR_WARN_KEYS = ("POTCAR",)


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.1f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0
    return "%d B" % n


def note_for(name: str) -> str:
    for key, txt in NOTES.items():
        if key in name:
            return txt
    for key, txt in COPYRIGHT_WARN.items():
        if key == name:
            return txt
    if any(k in name for k in POTCAR_WARN_KEYS):
        return ("⛔ **该脚本会代为拼接 POTCAR** —— 本 skill 的边界是"
                "**不生成、不复制 POTCAR**（受许可保护）。"
                "只参考它『按 POSCAR 元素顺序校验/提示』的思路，"
                "**不采用它『代为生成』的部分**。")
    if name.endswith(".ipynb"):
        return "Jupyter Notebook —— 含可执行代码与内嵌数据，**不复制内容**。"
    if name.endswith((".csv", ".vasp", ".vesta", ".cif", ".xyz")):
        return "数据/结构文件 —— 仅登记，不复制。"
    if name.endswith(".zip"):
        return "打包的脚本/练习集 —— 仅登记，不复制。"
    return ""


def main(argv=None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(
        prog="_inventory_assets.py",
        description="登记 LVTHW 附带脚本与数据（只出清单，不复制内容）",
    )
    ap.add_argument("--src", default=os.environ.get("LVTHW_SRC", ""),
                    help="LVTHW-master 目录（或 source/_posts）")
    ap.add_argument("--out", default=os.path.join(here, "lvthw",
                                                  "ASSETS.tsv"),
                    help="输出 TSV 路径")
    ap.add_argument("--only-scripts", action="store_true",
                    help="只列脚本类（.py/.f/.sh/.ipynb/zip）")
    args = ap.parse_args(argv)

    src = args.src
    if not src:
        guess = os.path.normpath(
            os.path.join(here, os.pardir, os.pardir, "things to study2",
                         "LVTHW-master"))
        if os.path.isdir(guess):
            src = guess
    if not src or not os.path.isdir(src):
        sys.stderr.write("错误：没找到 LVTHW 目录。请用 --src 指定，"
                         "或设环境变量 LVTHW_SRC。\n")
        return 3

    posts = os.path.join(src, "source", "_posts")
    if not os.path.isdir(posts):
        posts = src if any(f.endswith(".md") for f in os.listdir(src)) else ""
    if not posts:
        sys.stderr.write("错误：在 %s 里找不到 source/_posts\n" % src)
        return 1

    rows = []
    for dirpath, _dirnames, filenames in os.walk(posts):
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in KEEP_EXT:
                continue
            if args.only_scripts and ext not in (".py", ".f", ".sh", ".ipynb",
                                                 ".zip"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, posts).replace("\\", "/")
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            rows.append((rel, size, ext.lstrip("."), note_for(fn)))

    rows.sort()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# LVTHW 附带脚本与数据清单（**只登记，内容不入库**）\n")
        fh.write("# 由 references/raw/_inventory_assets.py 生成。\n")
        fh.write("# 路径相对于 LVTHW 的 source/_posts/。\n")
        fh.write("# ⚠️ 版权不明的（如第三方教材）与 POTCAR 相关的一律**不复制**，"
                 "本表只说明用途。\n")
        fh.write("# rel_path\tsize_bytes\ttype\tnote\n")
        for rel, size, typ, note in rows:
            fh.write("%s\t%d\t%s\t%s\n" % (rel, size, typ, note))

    n_script = sum(1 for r in rows if r[2] in ("py", "f", "sh", "ipynb", "zip"))
    print("已写出 %s" % args.out)
    print("  共 %d 个条目（其中脚本/程序包 %d 个）" % (len(rows), n_script))
    print()
    print("⚠️ 本清单**只是登记**：")
    print("   · 脚本内容、数据文件、Notebook 一律**不复制进仓库**；")
    print("   · 版权不明的（如第三方教材 zip）与原站导出件只记用途；")
    print("   · 与 POTCAR 相关的脚本只参考『顺序校验』思路，"
          "**不采用『代为生成』部分**。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
