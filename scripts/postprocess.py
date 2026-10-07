#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""postprocess.py —— 后处理：从 VASP 输出算物性（**核心零依赖，出图可选 numpy**）

**边界声明（先读这段）**
======================
- **计算部分零依赖**：`dos`（态密度与 d 带中心）、`workfunc`（功函数）、
  `efermi`、`gap`、`evac` 都只用标准库。
- **只有 `--plot` 出图**才需要 `matplotlib`。**缺了会友好提示 + `exit 3`**，
  **不会抛 traceback**，也**不会**因此让整个脚本不可用 ——
  数值照样打出来。

它算什么
========
| 子命令 | 从哪读 | 算什么 |
|---|---|---|
| `dos` | `DOSCAR` | 态密度、带中心（d 带中心）、积分电子数 |
| `workfunc` | `LOCPOT` + `POSCAR` | 真空能级、功函数 |
| `efermi` | `OUTCAR` / `DOSCAR` | 费米能级 |
| `gap` | `EIGENVAL` / `OUTCAR` | 带隙（粗略，见下面的诚实说明） |
| `potdiff` | 两个 `LOCPOT`/`CHGCAR` | 静电势差（工作函数/band offset 的粗算） |

⚠️ **诚实说明：本工具没有在真机上验证过**（构建环境没有 VASP）。
它的算法**对着真实算例的 DOSCAR/LOCPOT 校准过格式**，
但"算出来的物理量对不对"必须由用户自己判断。
每个子命令的输出里都写清了它的**假设与已知局限**。

一个**必须记住的陷阱**（来自本项目的实测）
==========================================
`DOSCAR` 的列语义**依赖 `ISPIN`**：

| `ISPIN` | 每行的列 |
|---|---|
| 1 | `energy  DOS  intDOS` |
| 2 | `energy  DOS(up)  DOS(dn)  intDOS(up)  intDOS(dn)` |

⇒ **`ISPIN=2` 时积分值在第 4、5 列，不是第 3 列。**
（课程答疑里说"看第三列的积分值"，那只对 `ISPIN=1` 成立。
本工具按**实际列数**自动判断，并在输出里说明它按哪种解释读的。）

用法
----
    python scripts/postprocess.py <子命令> <算例目录> [选项]
    python scripts/postprocess.py dos      <目录> --band-center
    python scripts/postprocess.py dos      <目录> --window -10 5 --plot dos.png
    python scripts/postprocess.py workfunc <目录>
    python scripts/postprocess.py gap      <目录>
    python scripts/postprocess.py --list

退出码
------
0=成功 · 1=文件问题 · 2=用法错误 · 3=缺依赖（只在 **用了 --plot** 时）

⚠️ 注意：即使 `--plot` 因缺 numpy 而失败，**数值已经打印过了**，
退出码是 3 —— 它是"可选增强没做成"，不是"计算失败"。
"""

from __future__ import annotations

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3

HARTREE = vc.HA          # 27.211... eV


# ---------------------------------------------------------------------------
# DOSCAR
# ---------------------------------------------------------------------------
def read_doscar(path: str):
    """读 `DOSCAR`。

    返回 ``{"header", "nedos", "emin", "emax", "efermi", "rows", "ispin"}``；
    `rows` 是 ``[(E, up, dn, int_up, int_dn)]``（`ISPIN=1` 时 dn/int_dn 为 None）。

    **真实文件的结构**（对着 `day2/Ag/DOSCAR` 与 `day2/al2o3/DOSCAR` 核对过）：

    ```
    行 1            ：元素与原子数          `  16  16   1   0`
    行 2            ：部分占据              `  0.4131174E+02 ...`
    行 3            ：缩放因子              `  1.000000000000000E-004`
    行 4            ：晶格类型              `  CAR`
    行 5            ：体系名                ` GDY`
    行 6            ：EMAX EMIN NEDOS EFERMI 权重
    行 7 .. 6+NEDOS ：能量与 DOS
    ```

    ⚠️ **两个实测教训（都记进 CHANGELOG）**：

    1. **表头不在固定行号上。** 早期版本按"第 7 行"读，于是把第一个数据点
       当成表头 —— 症状是 `NEDOS = -8`、`EFERMI = 0.0`，而**它不会报错**，
       只是给出完全错误的数。现在改为**找第一行恰好 5 个纯数字、
       且第 3 个是正整数的行**。
    2. **`ISPIN` 不要猜，按每行的列数判**：`ISPIN=2` 时是 5 列
       （`E DOS(up) DOS(dn) intDOS(up) intDOS(dn)`），`ISPIN=1` 时是 3 列。
       这比读 `INCAR` 更可靠 —— **DOSCAR 自己就说明了它是什么格式**。
    """
    if not os.path.exists(path):
        return None
    lines = []
    with vc.open_maybe_gz(path, "rb") as fh:
        for i, raw in enumerate(fh):
            try:
                lines.append(raw.decode("utf-8").rstrip("\r\n"))
            except UnicodeDecodeError:
                lines.append(raw.decode("latin-1").rstrip("\r\n"))
            if i > 400000:
                break

    if len(lines) < 8:
        return None

    def _nums(s):
        out = []
        for t in s.split():
            try:
                out.append(float(t))
            except ValueError:
                return None
        return out

    hdr_idx = None
    for i, ln in enumerate(lines[:20]):
        vals = _nums(ln)
        if vals and len(vals) == 5:
            if vals[2] >= 1 and abs(vals[2] - round(vals[2])) < 1e-9:
                hdr_idx = i
                break
    if hdr_idx is None:
        return None
    hv = _nums(lines[hdr_idx])
    emax, emin, nedos, efermi = hv[0], hv[1], int(round(hv[2])), hv[3]

    rows = []
    for ln in lines[hdr_idx + 1: hdr_idx + 1 + nedos]:
        vals = _nums(ln)
        if not vals or len(vals) < 3:
            continue
        if len(vals) >= 5:
            rows.append((vals[0], vals[1], vals[2], vals[3], vals[4]))
        else:
            rows.append((vals[0], vals[1], vals[2], None, None))
    if not rows:
        return None
    ispin = 2 if rows[0][3] is not None else 1
    return {"header": lines[:hdr_idx + 1], "nedos": nedos, "emin": emin,
            "emax": emax, "efermi": efermi, "rows": rows, "ispin": ispin,
            "hdr_line": hdr_idx + 1}


def cmd_dos(args) -> int:
    inp = vc.discover_inputs(args.directory)
    p = inp["DOSCAR"] or os.path.join(args.directory, "DOSCAR")
    d = read_doscar(p)
    if d is None:
        vc.die("读不到或读不懂 DOSCAR：%s" % p, EXIT_USER,
               "确认目录里有 DOSCAR，且它来自一次**单点**计算"
               "（弛豫过程中的 DOSCAR 对应的是最后一步的结构，见 "
               "references/decide.md §17.3）。")
    print("=" * 72)
    print("态密度 —— %s" % p)
    print("=" * 72)
    print("NEDOS = %d ；EFERMI = %s eV" % (d["nedos"], d["efermi"]))
    print("按 **ISPIN = %d** 解释列（由每行的列数自动判断）。" % d["ispin"])
    if d["ispin"] == 2:
        print("  → 每行是 `energy DOS(up) DOS(dn) intDOS(up) intDOS(dn)`")
        print("    ⚠️ **积分值在第 4、5 列**，不是第 3 列。")
        print("    （课程答疑说「看第三列」，那只对 ISPIN=1 成立。）")
    else:
        print("  → 每行是 `energy DOS intDOS`")
    rows = d["rows"]
    print("读入 %d 个能量点，范围 %.4f … %.4f eV" % (len(rows), rows[0][0],
                                                    rows[-1][0]))
    if d["efermi"] is not None:
        x = [(r[0] - d["efermi"], r[1], r[2], r[3], r[4]) for r in rows]
        print("\n（下面的能量都是**相对 EFERMI** 的）")
    else:
        x = rows
    # 积分电子数（最靠近 EFERMI 的那个点的 intDOS）
    if d["ispin"] == 2 and rows[0][3] is not None:
        i_up, i_dn = rows[0][3], rows[0][4]
        print("DOSCAR 首点的积分电子数：up=%.4f dn=%.4f 合计=%.4f"
              % (i_up, i_dn, i_up + i_dn))
    else:
        print("DOSCAR 首点的积分电子数：%.4f" % rows[0][2])

    if args.window:
        lo, hi = args.window
        sel = [r for r in x if lo <= r[0] <= hi]
    else:
        sel = x
    if not sel:
        vc.warn("给定的窗口里没有能量点。")
        return EXIT_OK

    # 简单统计
    dos_up = [r[1] for r in sel]
    print("\n窗口 [%.2f, %.2f] eV 内：" % (sel[0][0], sel[-1][0]))
    print("  DOS 最大值 = %.4f ；最小值 = %.4f" % (max(dos_up), min(dos_up)))
    if d["ispin"] == 2:
        dos_dn = [r[2] for r in sel]
        tot = sum(dos_up) + sum(dos_dn)
        print("  自旋向上积分 ≈ %.4f ；向下 ≈ %.4f" % (sum(dos_up), sum(dos_dn)))
        if abs(tot) > 1e-12:
            print("  自旋极化（(up−dn)/(up+dn)）≈ %.4f"
                  % ((sum(dos_up) - sum(dos_dn)) / tot))

    # d 带中心
    if args.band_center:
        lo, hi = (args.window if args.window else (sel[0][0], sel[-1][0]))
        num = den = 0.0
        for r in sel:
            w = r[1] + (r[2] if d["ispin"] == 2 else 0.0)
            num += r[0] * w
            den += w
        if abs(den) > 1e-12:
            bc = num / den
            print()
            print("── 带中心（band center）──")
            print("  中心 = %.4f eV（相对 EFERMI）" % bc)
            print("  **积分窗口** = [%.4f, %.4f] eV（相对 EFERMI）" % (lo, hi))
            print()
            print("  ⚠️⚠️ **报带中心时必须同时报积分窗口。**")
            print("    本项目实测：同一份 PDOS，仅把积分上限定成 20 eV 而不是"
                  " EMAX−EFERMI，")
            print("    结果就差 0.027 eV（−3.7502 vs −3.7771 eV）——")
            print("    **足以改变结论**。见 references/decide.md 与 playbook.md §4。")
            print("  ⚠️ 本工具算的是**整个 DOSCAR**（全部原子全部轨道）的带中心。")
            print("    要算**某个元素的 d 带中心**，需要读 DOSCAR 后面"
                  "每个原子的分段，")
            print("    或用 `LORBIT=11` 后的 `PROCAR`/`vasprun.xml` —— "
                  "**本工具不做这件事**。")
        else:
            vc.warn("窗口内的 DOS 积分接近 0，算不出带中心。")

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            if d["ispin"] == 2:
                fh.write("E_minus_Efermi\tDOS_up\tDOS_dn\tintDOS_up\tintDOS_dn\n")
                for r in x:
                    fh.write("%.6f\t%.6f\t%.6f\t%s\t%s\n"
                             % (r[0], r[1], r[2],
                                "" if r[3] is None else "%.6f" % r[3],
                                "" if r[4] is None else "%.6f" % r[4]))
            else:
                fh.write("E_minus_Efermi\tDOS\tintDOS\n")
                for r in x:
                    fh.write("%.6f\t%.6f\t%.6f\n" % (r[0], r[1], r[2]))
        print("\n已写出 %s" % args.out)

    if args.plot:
        return _plot_dos(x, d["ispin"], args.plot, args.directory)
    return EXIT_OK


def _plot_dos(x, ispin, out, directory) -> int:
    """出图 —— **这一步才需要 numpy/matplotlib**。缺了给友好提示 + exit 3。"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        sys.stderr.write(
            "错误：出图需要 matplotlib，但当前 Python 里没有装。\n"
            "  → **数值结果已经打印在上面了**，出图只是可选增强。\n"
            "  → 安装：python -m pip install matplotlib\n"
            "  → 或者用 --out <文件> 导出纯文本（TSV），自己在别处画。\n"
            "  → 本 skill 的核心工具**不需要任何第三方库**。\n")
        return EXIT_DEP
    E = [r[0] for r in x]
    up = [r[1] for r in x]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(E, up, lw=1, label="DOS up")
    if ispin == 2:
        ax.plot(E, [-r[2] for r in x], lw=1, label="DOS dn (−)")
    ax.axvline(0, color="k", lw=0.6, ls="--")
    ax.set_xlabel(r"$E - E_F$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(os.path.basename(os.path.abspath(directory)))
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print("已出图 %s" % out)
    return EXIT_OK


# ---------------------------------------------------------------------------
# LOCPOT → 真空能级 / 功函数
# ---------------------------------------------------------------------------
def read_locpot_planar(path: str):
    """读 `LOCPOT`，按**第三个晶格方向**做平面平均。

    返回 (z_array_angs, vplanar_eV, cell_c, comment)。

    ⚠️ **假设与局限（必须让用户看到）**：
    1. 本工具**只沿第三个晶格方向**做平均 —— 即假设 slab 的法线是 **c 轴**，
       且 c 轴与真空方向一致。**若你的 slab 法线不是 c，这个结果没有意义。**
    2. `LOCPOT` 里的势是**总局部势**（含 Hartree + 交换关联 + 离子），
       单位 eV。功函数应当用**静电势**；若你同时设了 `LVTOT=.TRUE.` 与
       `LVHAR=.TRUE.`，官方行为是 **`LVHAR` 优先**（拿到的是纯静电势）。
       本工具**不检查**这一点 —— 请你自己确认 `INCAR`。
    3. 平面平均的**收敛性**依赖真空层足够厚。真空薄时真空能级平台不明显。
    """
    if not os.path.exists(path):
        return None
    # 头 8 行：注释 / scale / 3 晶格 / 元素 / 数目
    head = []
    with vc.open_maybe_gz(path, "rb") as fh:
        for i, raw in enumerate(fh):
            try:
                head.append(raw.decode("utf-8").rstrip("\r\n"))
            except UnicodeDecodeError:
                head.append(raw.decode("latin-1").rstrip("\r\n"))
            if i >= 8:
                break
    if len(head) < 8:
        return None
    comment = head[0].strip()
    try:
        scale = float(head[1].split()[0])
        cvec = [float(x) for x in head[4].split()[:3]]
    except (ValueError, IndexError):
        return None
    c = math.sqrt(sum(v * v for v in cvec)) * scale
    if c <= 0:
        return None

    # 数据区：先**按 POSCAR 的结构数出原子坐标行**，再找网格行。
    #
    # ⚠️⚠️ 这里必须严格按结构走，不能"找第一行有 3 个 >1 的整数"。
    #     本项目在一个真实 LOCPOT 上踩过这个坑（见 CHANGELOG 的 CR-029）：
    #     原子坐标是 **Direct** 分数坐标，形如
    #         `  0.333556  0.667061  0.333532`
    #     —— **恰好 3 个数、且都 >1（只要有一个 >1 就够）**，
    #     于是被误认成网格行 `nx ny nz`；之后的解析全乱，函数直接返回 None，
    #     用户看到的是"读不到或读不懂 LOCPOT"，而文件其实完全正常。
    #
    #     正确做法：**用第 7 行的原子数把坐标行跳过去**，再往后找网格行。
    #     （VASP 的 `LOCPOT` 与 `POSCAR` 前 8 行结构相同：
    #       1 注释 / 2 scale / 3-5 晶格 / 6 元素名 / 7 数目 [/ 8 Selective]，
    #       然后是 nions 行坐标。注意**第 8 行可能是 `Selective dynamics`
    #       也可能直接是 `Direct`**，要看第 7 行之后第一行的首字母。）
    nions = 0
    if len(head) >= 7:
        try:
            nions = sum(int(float(x)) for x in head[6].split())
        except (ValueError, IndexError):
            nions = 0

    nx = ny = nz = None
    vals = []

    def _isnum(tok):
        try:
            float(tok)
            return True
        except ValueError:
            return False

    def _isposint(tok):
        if not _isnum(tok):
            return False
        v = float(tok)
        return v > 1 and abs(v - round(v)) < 1e-9

    with vc.open_maybe_gz(path, "rb") as fh:
        for i, raw in enumerate(fh):
            if i < 8:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            toks = line.split()
            # 阶段一：跳过 nions 行坐标（+ 可能的 `Selective dynamics` / `Direct` 行）
            if nions > 0:
                up = line.upper()
                if (up.startswith("S") or up.startswith("D")
                        or up.startswith("C")) and not _isnum(toks[0]):
                    continue          # `Selective dynamics` / `Direct` / `Cartesian`
                nions -= 1
                continue
            # 阶段二：找网格行（恰好 3 个 >1 的整数）
            if nx is None:
                if len(toks) == 3 and all(_isposint(t) for t in toks):
                    nx, ny, nz = (int(float(t)) for t in toks)
                continue
            # 阶段三：读势值。⚠️ **一行可能有多个数**（VASP 默认一行 5 个），
            # 早期版本只取 `toks[0]`，会把 5/6 的数据丢掉 ⇒ 平面平均全错。
            for t in toks:
                if not _isnum(t):
                    break
                vals.append(float(t))
            if len(vals) >= nx * ny * nz:
                break
    if not (nx and ny and nz) or len(vals) < nx * ny * nz:
        return None
    # 沿 z 平面平均（VASP 的存储顺序：z 最慢变化 ⇒ 按 (ix,iy) 内层）
    # 实际上 VASP 写 LOCPOT 的顺序是 x 最快、z 最慢。
    planar = [0.0] * nz
    plane = nx * ny
    for k in range(nz):
        s = 0.0
        base = k * plane
        for j in range(plane):
            s += vals[base + j]
        planar[k] = s / plane
    dz = c / nz
    zs = [(k + 0.5) * dz for k in range(nz)]
    return zs, planar, c, comment


def cmd_workfunc(args) -> int:
    inp = vc.discover_inputs(args.directory)
    p = inp["LOCPOT"] or os.path.join(args.directory, "LOCPOT")
    r = read_locpot_planar(p)
    if r is None:
        vc.die("读不到或读不懂 LOCPOT：%s" % p, EXIT_USER,
               "功函数需要 `LOCPOT`。生成它：在 INCAR 里设 `LVHAR = .TRUE.`"
               "（推荐，拿到纯静电势）或 `LVTOT = .TRUE.`。")
    zs, planar, c, comment = r
    print("=" * 72)
    print("功函数 —— %s" % p)
    print("=" * 72)
    print("体系：%s" % comment)
    print("沿 **c 轴**（长度 %.4f Å）做了平面平均，共 %d 个平面。" % (c, len(zs)))
    print()
    print("⚠️ **本工具只沿第三个晶格方向平均。** 若你的 slab 法线不是 c 轴，")
    print("   这个结果**没有意义** —— 请先用 POSCAR 确认方向。")
    print()

    # 真空能级：**不能替用户选一个**。
    #
    # ⚠️ 这里返工过两次，第二次是本项目**在一个真实 LOCPOT 上量出来的**
    #    （见 CHANGELOG 的 CR-028 / CR-030）。现在知道的事实：
    #
    # ① **不对称 slab 的两侧真空能级本来就不等**，用哪一侧会直接改功函数。
    # ② **若开了偶极修正（`LDIPOL=.TRUE.` + `IDIPOL=3`），两侧不等是
    #    「按设计如此」，不是错误。** 官方 `pages/LDIPOL.md:12` 原文：
    #      `The decisive advantage of this mode is that leading errors in the
    #       forces are corrected and that the work function can be evaluated
    #       for asymmetric slabs.`
    #    ⇒ 偶极修正的目的之一，正是让**每个面各自有明确的真空能级**。
    # ③ ⚠️ 而且**真空区不再是一段平坦平台**。实测那个算例
    #    （Au+O slab，开了 `LDIPOL/IDIPOL=3`，`LVHAR=.TRUE.`）：
    #      z≈14–18 Å 平在 **7.196 eV**；z≈20–22 Å 平在 **6.578 eV**；
    #      中间在 z≈18.9 处掉了 0.6 eV。
    #    ⇒ 所以"找最平窗口"这种启发式会**挑到错的那一段**。
    #
    # ⇒ 结论：本工具**只报事实，不替用户裁定**：
    #    · 报出检测到的偶极修正状态；
    #    · 报出**每一个**明显的平台及其 z 区间与宽度；
    #    · 明确说"用哪个是你的物理选择，结论里必须写明"。
    n = len(planar)
    if n < 10:
        vc.die("平面数太少（%d），无法判断真空区。" % n, EXIT_USER)

    # --- 检出偶极修正（这决定"两侧不等"是设计如此还是异常）---
    dipol_on, idipol = False, None
    incar = inp.get("INCAR")
    if incar:
        try:
            tags = vc.read_incar(incar)
            ld = str(tags.get("LDIPOL", "")).strip().upper()
            dipol_on = ld.startswith(".T") or ld.startswith("T")
            if "IDIPOL" in tags:
                try:
                    idipol = int(float(str(tags["IDIPOL"]).split()[0]))
                except ValueError:
                    idipol = None
        except Exception:
            pass

    # --- 找所有"平台"：连续且极差很小的区段 ---
    tol = 0.02          # 平台内允许的起伏（eV）
    min_w = max(3, n // 40)
    plateaus = []
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(planar[j + 1] - planar[i]) <= tol:
            j += 1
        if j - i + 1 >= min_w:
            seg = planar[i:j + 1]
            plateaus.append({
                "z0": zs[i], "z1": zs[j], "n": j - i + 1,
                "v": sum(seg) / len(seg),
                "ripple": max(seg) - min(seg),
            })
            i = j + 1
        else:
            i += 1

    print("── 真空能级：检测到的**平台**（本工具不替你选）──")
    if dipol_on:
        print("  ⚠️ 检测到**偶极修正已开启**（`LDIPOL=.TRUE.`%s）。"
              % ("，`IDIPOL=%d`" % idipol if idipol else ""))
        print("     ⇒ 不对称 slab 上**两侧真空能级不同是正常的、按设计的**。")
        print("     官方 `pages/LDIPOL.md:12`：偶极修正的优点之一正是"
              "「the work function can be evaluated for asymmetric slabs」。")
        print("     ⇒ 这时你应当**分别报两个面的功函数**，而不是只报一个。")
        print("     ⚠️ 而且此时**真空区不是一段平平台**（偶极修正会加一个线性势），"
              "下面每一段都要自己判断是不是真平台。")
    if not plateaus:
        print("  （没找到明显平台 —— 真空层可能太薄，或势在真空区仍有斜率。）")
    else:
        for k, pl in enumerate(plateaus, 1):
            print("  平台%d：**%.4f eV**  z = %.2f–%.2f Å（宽 %.2f Å，"
                  "段内起伏 %.4f eV）"
                  % (k, pl["v"], pl["z0"], pl["z1"], pl["z1"] - pl["z0"],
                     pl["ripple"]))
        if len(plateaus) > 1:
            vs = [pl["v"] for pl in plateaus]
            print("  ⚠️ **有 %d 个平台，极差 %.4f eV** —— 不要随便取一个。"
                  % (len(plateaus), max(vs) - min(vs)))
            if dipol_on:
                print("     有偶极修正时这是**预期**的（两个面各自一个真空能级）。")
            else:
                print("     没有偶极修正却出现多个平台，请**看图**确认哪一段是"
                      "真真空（其余可能是 slab 内部或层间区域）。")

    # 仍然给一个"默认值"，但**必须说明它是怎么来的**，且不掩盖其它平台。
    evac = None
    if plateaus:
        hi = max(plateaus, key=lambda p: p["v"])
        evac = hi["v"]
        print()
        print("── 本工具给计算器用的**默认** Evac ──")
        print("  Evac = **%.4f eV**（= 上面所有平台里**最高**的那个，"
              "位于 z = %.2f–%.2f Å）" % (evac, hi["z0"], hi["z1"]))
        print("  ⚠️ **这只是个默认值，不是判据。** 「取哪一侧」是**物理选择**：")
        print("     · 报**功函数**时要写明用的是哪个面、真空能级取在哪；")
        print("     · 开了偶极修正的**不对称** slab，两个面各有各的功函数；")
        print("     · 结论里不写清楚，别人**复现不出你的数**。")

    efermi = None
    if inp["OUTCAR"]:
        efermi = vc.outcar_fermi(inp["OUTCAR"])
    if efermi is None and inp["DOSCAR"]:
        d = read_doscar(inp["DOSCAR"])
        if d:
            efermi = d["efermi"]
    if efermi is None:
        vc.warn("读不到 EFERMI（OUTCAR 与 DOSCAR 都没有）。"
                "功函数没法算。")
        print("\n⚠️ **功函数 = Evac − EFERMI**，没有 EFERMI 就算不出来。")
        print("   请提供 OUTCAR，或用 `--efermi <值>` 手动给出。")
        if args.efermi is not None:
            efermi = args.efermi
        else:
            # 仍把平面平均导出来，方便用户自己算
            if args.out:
                with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("z_Angstrom\tplanar_avg_potential_eV\n")
                    for z, v in zip(zs, planar):
                        fh.write("%.6f\t%.6f\n" % (z, v))
                print("   （已把平面平均势导出到 %s，你可以自己算）" % args.out)
            return EXIT_USER
    if args.efermi is not None:
        efermi = args.efermi
        print("EFERMI = %.4f eV（由 --efermi 给出）" % efermi)
    else:
        print("EFERMI = %.4f eV（从输出文件读到）" % efermi)
    wf = evac - efermi
    print()
    print("── 功函数 ──")
    print("  Φ = Evac − EFERMI = %.4f − %.4f = **%.4f eV**" % (evac, efermi, wf))
    print()
    print("⚠️ 已知局限（必须自己判断）：")
    print("  ① 只沿 c 轴平均；slab 法线不是 c 时结果无意义。")
    print("  ② 势的口径：`LVHAR=.TRUE.` 给纯静电势（推荐）；"
          "`LVTOT=.TRUE.` 给总势。")
    print("     两者都有时官方行为是 **LVHAR 优先**。本工具**不检查**这一点。")
    print("  ③ 真空层太薄时「最平区域」不明显，Evac 会不准 —— 判据是"
          "平面平均曲线在真空区应当**明显平坦**。")
    print("  ④ 本工具**没有在真机上验证过**。请把它当「辅助核对」，不是「权威值」。")

    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("z_Angstrom\tplanar_avg_potential_eV\n")
            for z, v in zip(zs, planar):
                fh.write("%.6f\t%.6f\n" % (z, v))
        print("\n已写出 %s" % args.out)

    if args.plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            sys.stderr.write(
                "错误：出图需要 matplotlib，当前 Python 里没有装。\n"
                "  → **数值结果已经打印在上面**，出图只是可选增强。\n"
                "  → 安装：python -m pip install matplotlib\n"
                "  → 或加 `--out <文件>` 导出 TSV 自己在别处画。\n")
            return EXIT_DEP
        fig, ax = plt.subplots(figsize=(6, 3.2))
        ax.plot(zs, planar, lw=1)
        ax.axhline(evac, color="r", lw=0.8, ls="--", label="Evac")
        ax.axhline(efermi, color="b", lw=0.8, ls=":", label="EFERMI")
        ax.set_xlabel("z (Å)")
        ax.set_ylabel("planar-averaged potential (eV)")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(args.plot, dpi=150)
        print("已出图 %s" % args.plot)
    return EXIT_OK


# ---------------------------------------------------------------------------
# 费米能级 / 带隙
# ---------------------------------------------------------------------------
def cmd_efermi(args) -> int:
    inp = vc.discover_inputs(args.directory)
    src, val = None, None
    if inp["OUTCAR"]:
        val = vc.outcar_fermi(inp["OUTCAR"])
        src = inp["OUTCAR"]
    if val is None and inp["DOSCAR"]:
        d = read_doscar(inp["DOSCAR"])
        if d:
            val, src = d["efermi"], inp["DOSCAR"]
    if val is None:
        vc.die("读不到 EFERMI（找过 OUTCAR 与 DOSCAR）", EXIT_USER)
    print("EFERMI = %.6f eV   （来自 %s）" % (val, src))
    if inp["OUTCAR"]:
        print("程序版本：%s" % (vc.outcar_version(inp["OUTCAR"]) or "（读不到）"))
        print()
        print("⚠️ **同一份输出里 EFERMI 可能出现多次**（每个离子步一次）。")
        print("   本工具给的是**最后一个** —— 只有单点计算（`NSW=0`）时它才明确。")
        print("   判据：`grep -c \"E-fermi\" OUTCAR` 应当是 **1**。")
    return EXIT_OK


def cmd_gap(args) -> int:
    """从 `EIGENVAL` 粗略估带隙。

    ⚠️ **必须按文件自身的结构找 k 点块，不能信第 6 行的 `NKPTS NBANDS`。**

    实测（`things to study/` 下的真实文件）：
    | 文件 | 第 6 行声称 | 实际结构 |
    |---|---|---|
    | `day2/al2o3/EIGENVAL` | `48  115` | **113 个 k 点块，每块 33 条带** |
    | `day1/mos2/EIGENVAL`  | `18   12` | **12 个 k 点块，每块 14 条带** |

    两者都对不上 —— 因为这些文件被**后处理工具改过**（很可能是 vaspkit
    的能带/DOS 提取，或手工截取过能量窗口），表头没跟着更新。
    早期版本照表头算块大小，于是**整份文件都错位**：Al₂O₃ 算出 −5.85 eV 的
    "负带隙"、Ag 算出 −14.9 eV，而且**不会报错**。

    现在改为：**扫描结构** —— k 点行的特征是"恰好 4 个数值字段"
    （`kx ky kz 权重`），而能带行是 3 个（`序号 能量 占据数`）。
    取相邻 k 点行的间距（取中位数，抗尾部噪声）作为块大小。

    ⚠️ 其余局限见输出里的说明：**只按已有 k 点判断**（间接带隙会高估）、
    不做自旋分辨、本工具**没有在真机上验证过**。
    """
    inp = vc.discover_inputs(args.directory)
    p = inp["EIGENVAL"] or os.path.join(args.directory, "EIGENVAL")
    if not os.path.exists(p):
        vc.die("找不到 EIGENVAL：%s" % p, EXIT_USER)
    with open(p, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    if len(lines) < 10:
        vc.die("EIGENVAL 太短，读不出内容：%s" % p, EXIT_USER)

    def _row(i):
        """返回第 i 行（0-based）的数值字段列表；含非数字则返回 None。"""
        if i < 0 or i >= len(lines):
            return None
        out = []
        for t in lines[i].split():
            try:
                out.append(float(t))
            except ValueError:
                return None
        return out

    try:
        hdr = [int(float(x)) for x in lines[5].split()[:3]]
    except (ValueError, IndexError):
        vc.die("EIGENVAL 的第 6 行不是 `NKPTS NBANDS NELECT`：%r" % lines[5],
               EXIT_USER)
    # ⚠️ **表头里哪一个是 NKPTS 也可能被换过位置。**
    # 实测：`day2/Ag/EIGENVAL` 的表头是 `176 13 32`，
    # 而文件实际是 **13 个 k 点块、每块 176 条带** ——
    # 也就是说 NKPTS 与 NBANDS **被写反了**（或本来就是另一种约定）。
    # ⇒ 正确的做法是把两个候选都试一遍，**用数据验证哪一个说得通**：
    #   块大小 = N_bands + 1；且每块内第二、三行的第一个字段应当是 1 与 2。
    # 找 k 点行：**恰好 4 个数值字段**。
    #
    # ⚠️ 光判"4 个字段"还不够 —— 实测 `day2/al2o3/EIGENVAL` 的**表头第 6 行**
    # 也恰好是 4 个数，会被误认成 k 点行，于是块数多算 1 个、块大小错位。
    # ⇒ 加一条**语义验证**：真正的 k 点行之后应当是 band 行，
    #   其第 1 个字段依次是 1、2、3…。用这一条把表头排除掉。
    def _is_kpoint_row(i):
        v = _row(i)
        if v is None or len(v) != 4:
            return False
        a, b = _row(i + 1), _row(i + 2)
        if not (a and b and len(a) >= 3 and len(b) >= 3):
            return False
        return abs(a[0] - 1.0) < 1e-6 and abs(b[0] - 2.0) < 1e-6

    krows = [i for i in range(6, min(len(lines), 300000)) if _is_kpoint_row(i)]
    if len(krows) < 2:
        vc.die("EIGENVAL 里找不到 k 点行（特征是恰好 4 个数值字段、"
               "且其后两行的首个字段是 1 与 2）。"
               "文件可能被截断或格式与预期不同。", EXIT_USER)
    gaps = sorted(krows[i + 1] - krows[i] for i in range(len(krows) - 1))
    blk_med = gaps[len(gaps) // 2]

    cand_a = (len(krows), blk_med - 1)
    cand_b = (blk_med - 1, len(krows))
    # **不依赖表头**的判据：`krows` 的个数就是 k 点块数（每个 k 点一行），
    # 块大小 = 带数 + 1。这条来自文件自身的结构，所以最可靠。
    nk, nb = len(krows), blk_med - 1
    hdr_a, hdr_b = hdr[0], hdr[1]
    print("=" * 72)
    print("带隙（粗估）—— %s" % p)
    print("=" * 72)
    print("文件表头声称：NKPTS = %d ；NBANDS = %d" % (hdr_a, hdr_b))
    print("按文件结构实测：**%d 个 k 点块，每块 %d 条带**" % (nk, nb))
    if (nk, nb) != (hdr_a, hdr_b):
        extra = ("（本例里 **NKPTS 与 NBANDS 看起来被写反了**。）"
                 if (nk, nb) == (hdr_b, hdr_a) else "")
        print("⚠️ **表头与实际结构不符** —— 这个文件被改过"
              "（很可能是 vaspkit，或手工截取过能量窗口），表头没跟着更新。"
              + extra)
        print("   本工具**按实际结构解析**"
              "（照表头算会整份错位，而且**不会报错**）。")
    print()

    per_k = []
    for k, base in enumerate(krows):
        bands = []
        for j in range(1, blk_med):
            v = _row(base + j)
            if v is None or len(v) < 3:
                continue
            bands.append((v[1], v[2], int(v[0])))   # (能量, 占据数, 带序号)
        if bands:
            per_k.append((k + 1, bands))
    if not per_k:
        vc.die("EIGENVAL 里没解析到任何本征值", EXIT_USER)

    # ⚠️ **必须逐 k 点分别找 VBM/CBM，再取全局极值。**
    # 把所有 (E, occ) 混在一起排序会给出荒谬结果（实测早期版本在 `day1/mos2`
    # 上给出"VBM 与 CBM 落在同一个 band"的结论）。
    # **带隙 = 全局 VBM 与全局 CBM 之差。**
    vbm = cbm = None
    metal = False
    for ik, bands in per_k:
        occ_b = [b for b in bands if b[1] > 0.5]
        emp_b = [b for b in bands if b[1] <= 0.5]
        if not occ_b or not emp_b:
            metal = True
            continue
        top = max(occ_b, key=lambda b: b[0])
        bot = min(emp_b, key=lambda b: b[0])
        if vbm is None or top[0] > vbm[0]:
            vbm = (top[0], ik, top[2])
        if cbm is None or bot[0] < cbm[0]:
            cbm = (bot[0], ik, bot[2])
    if vbm is None or cbm is None:
        print("体系看起来是**金属或半金属**（某些 k 点上没有明确的"
              "占据/空态分界），EIGENVAL 无法给出带隙。")
        return EXIT_OK
    gap = cbm[0] - vbm[0]
    direct = None
    for ik, bands in per_k:
        ob = [b for b in bands if b[1] > 0.5]
        eb = [b for b in bands if b[1] <= 0.5]
        if not ob or not eb:
            continue
        g = min(eb, key=lambda b: b[0])[0] - max(ob, key=lambda b: b[0])[0]
        if direct is None or g < direct:
            direct = g
    print("VBM = %.4f eV（band %d, k 点 #%d）" % vbm)
    print("CBM = %.4f eV（band %d, k 点 #%d）" % cbm)
    print("**间接**带隙 ≈ **%.4f eV**" % gap)
    if direct is not None:
        print("**最小直接**带隙 ≈ **%.4f eV**"
              "（在所有 k 点上取'最低空带 − 最高占带'的最小值）" % direct)
        # ⚠️ **"直接/间接"的判据是 VBM 与 CBM 是否在同一个 k 点**，
        # 不是"间接带隙是否等于最小直接带隙"。
        # 早期版本用后者判，会在 `day1/mos2` 上得出自相矛盾的结论：
        # 明明 VBM 在 k#9、CBM 在 k#10（不同 k 点），却因为两个数恰好相等
        # 而报"直接带隙"。已记入 CHANGELOG 更正记录。
        if vbm[1] == cbm[1]:
            print("  → VBM 与 CBM 落在**同一个 k 点**（#%d）⇒ 这是**直接带隙**"
                  % vbm[1])
        else:
            print("  → VBM（k#%d）与 CBM（k#%d）**不在同一个 k 点**"
                  "⇒ 这是**间接带隙**" % (vbm[1], cbm[1]))
    if gap < 0:
        print()
        print("⚠️ **带隙是负的** —— 这通常意味着：")
        print("  ① 体系其实是金属/半金属（占据与空态在某些 k 点重叠）；")
        print("  ② 或者这份 `EIGENVAL` 被截取过能量窗口，"
              "band 序号与占据数已经不连续。")
        print("  **不要把这个负数当带隙用。**")
    if metal:
        print("⚠️ 有 k 点上没有明确的占据/空态分界 —— 可能是金属。")
    print()
    print("⚠️ **这是粗估，不是权威值。** 已知局限：")
    print("  ① **只按已有的 k 点判断** —— 间接带隙材料上会**高估**"
          "（真实 CBM 可能落在两个已采样的 k 点之间）。")
    print("  ② 不做自旋分辨（`ISPIN=2` 时应当分别看 up/dn）。")
    print("  ③ 用占据数（第 3 列）做分界判据，阈值取 0.5。")
    print("  ④ **官方没有承诺 `EIGENVAL` 的格式跨版本稳定** —— "
          "本工具按**文件自身结构**解析，但换版本后仍可能有变。")
    print("  ⑤ 本工具**没有在真机上验证过**。")
    return EXIT_OK


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="postprocess.py",
        description="后处理：态密度/d 带中心、功函数、费米能级、带隙（粗估）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=成功；1=文件问题；2=用法错误；"
               "3=**只在用了 --plot 且缺 matplotlib** 时。\n"
               "⚠️ `--plot` 缺依赖时**数值已经打印过了**，退出码 3 表示"
               "「可选增强没做成」，不是「计算失败」。",
    )
    sub = ap.add_subparsers(dest="cmd", metavar="<子命令>")
    ap.add_argument("--list", action="store_true", help="列出所有子命令")

    d = sub.add_parser("dos", help="态密度与带中心（从 DOSCAR）")
    d.add_argument("directory")
    d.add_argument("--window", nargs=2, type=float, metavar=("LO", "HI"),
                   help="积分窗口（相对 EFERMI，eV）")
    d.add_argument("--band-center", action="store_true",
                   help="算带中心（**必须同时报窗口**）")
    d.add_argument("--out", help="把曲线写成 TSV")
    d.add_argument("--plot", metavar="PNG", help="出图（需要 matplotlib）")

    w = sub.add_parser("workfunc", help="功函数（从 LOCPOT）")
    w.add_argument("directory")
    w.add_argument("--efermi", type=float, help="手动给 EFERMI（读不到时用）")
    w.add_argument("--out", help="把平面平均势写成 TSV")
    w.add_argument("--plot", metavar="PNG", help="出图（需要 matplotlib）")

    e = sub.add_parser("efermi", help="费米能级")
    e.add_argument("directory")

    g = sub.add_parser("gap", help="带隙（**粗估**，从 EIGENVAL）")
    g.add_argument("directory")

    args = ap.parse_args(argv)

    if args.list or not args.cmd:
        print("postprocess.py 的子命令：\n")
        print("  dos      <目录>  态密度、积分电子数、带中心（含 d 带中心提醒）")
        print("  workfunc <目录>  功函数（LOCPOT 平面平均）")
        print("  efermi   <目录>  费米能级")
        print("  gap      <目录>  带隙（**粗估**，见子命令自己的局限说明）")
        print()
        print("⚠️ **只有 `--plot` 需要 matplotlib**；缺了给友好提示 + exit 3，")
        print("   **数值照样打出来**。核心计算零依赖。")
        print("⚠️ 所有子命令都**没有在真机上验证过**（构建环境没有 VASP）。")
        print("   它们是对着真实算例的**格式**校准的，物理正确性要你自己判断。")
        return EXIT_OK if args.list else EXIT_USAGE

    if not os.path.isdir(args.directory):
        vc.die("不是一个目录：%s" % args.directory, EXIT_USER)

    if args.cmd == "dos":
        return cmd_dos(args)
    if args.cmd == "workfunc":
        return cmd_workfunc(args)
    if args.cmd == "efermi":
        return cmd_efermi(args)
    if args.cmd == "gap":
        return cmd_gap(args)
    vc.die("不认识的子命令：%s" % args.cmd, EXIT_USAGE)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
