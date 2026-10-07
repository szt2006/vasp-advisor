#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''_system_types.py —— **体系类型索引**：先问「你算的是哪类体系」。

为什么需要它（一次真实事故暴露的组织缺陷）
==========================================
本 skill 的知识原来是**按来源**组织的（`official/` 官方 / 讲义 / 答疑 / 算例 …），
这是为了保证**可回溯**，没错。但**使用者的心智模型不是这样的**：

> 他想的是「**我算的是个 179 原子的金属氧化物团簇**，该注意什么」，
> **不是**「官方第 37 页说了什么」。

于是出现一个荒谬的结果：**知识都在库里，但查不到**。
那次事故里，`NCORE` 的适用条件**同时存在于四个地方**
（`official/NCORE.md`、`playbook.md` §0.13、`_GATES.md` §3、`decide.md` §19），
**而使用者仍然踩了坑** —— 因为他不知道「该去查 `NCORE`」。

⇒ **工具书的第一层索引不该是「来源」，也不该是「参数名」，而是「你算的是什么」。**

本脚本做什么
============
从**真实算例**（`things to study/` 下 98 个）里**反推**体系类型与
每类的参数画像。**不臆造分类** —— 分类是从算例里长出来的，不是我先想好的。

⚠️ 关键设计：**先抽特征，再看能分出什么类。**
（如果先定分类再去填，就会变成「我觉得该有几类」 —— 那是编造。）

用法
----
    python _system_types.py --survey          # 抽全部算例的特征，看分布
    python _system_types.py --derive          # 从特征反推体系类型并生成 _SYSTEMS.md
    python _system_types.py --check           # 校验 _SYSTEMS.md 里的数字与实测一致
    python _system_types.py --lookup <目录>   # 判断「我这个算例属于哪类 + 该类注意什么」

⚠️ **它只做「归类与呈现」，不产生新知识。**
   每一类的参数起点都来自真实算例的**实测统计**，不是我的建议。
'''

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "scripts"))

try:
    import vasp_common as vc
except ImportError:                                          # pragma: no cover
    print("找不到 scripts/vasp_common.py —— 请在 skill 根目录运行本脚本。")
    raise SystemExit(2)

ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))
# ⚠️ **学习材料不在 skill 里**（`SKILL_SCOPE.md`：它属于外部资料）。
#    优先级：环境变量 > skill 外的资料区（同级）> 旧位置（兼容）。
#    ⇒ **克隆 skill 的人没有这批资料，这是正常的** ——
#      `--derive` / `--check` / `--lookup` 会给出友好提示，不是崩溃。
_CORPUS_CANDIDATES = [
    os.environ.get("VASP_CORPUS"),
    os.path.join(os.path.dirname(ROOT), "_MATERIALS", "things to study"),
    os.path.join(ROOT, "things to study"),
    os.path.join(os.path.dirname(ROOT), "_MATERIALS"),
]
CORPUS = next((c for c in _CORPUS_CANDIDATES
               if c and os.path.isdir(c)), _CORPUS_CANDIDATES[1])

# 要在画像里统计的 INCAR 标签（**只列有诊断价值的**，不是全部）
PROFILE_TAGS = [
    'ENCUT', 'ISMEAR', 'SIGMA', 'EDIFF', 'EDIFFG', 'IBRION', 'ISIF', 'NSW',
    'ISPIN', 'MAGMOM', 'LREAL', 'PREC', 'LDAU', 'LDAUL', 'LDAUU', 'LDAUJ',
    'LHFCALC', 'AEXX', 'HFSCREEN', 'IVDW', 'LSOL', 'EB_K', 'LDIPOL', 'IDIPOL',
    'NCORE', 'NPAR', 'KPAR', 'ISYM', 'NELM', 'NELMIN', 'ALGO', 'LCHARG',
    'LWAVE', 'LORBIT', 'NEDOS', 'LELF', 'LAECHG', 'LVHAR', 'LVTOT', 'ICHARG',
    'ISTART', 'POTIM', 'BMIX', 'AMIX', 'AMIN', 'LMAXMIX', 'NBLK', 'KSPACING',
    'GGA', 'METAGGA', 'LUSE_VDW', 'BPARAM', 'AGGAC', 'LASPH', 'ADDGRID',
]

# 原子序数 → 元素符号（判「含 3d/4f 元素」用；只覆盖常见的那批）
D_BLOCK = set("Sc Ti V Cr Mn Fe Co Ni Cu Zn Y Zr Nb Mo Tc Ru Rh Pd Ag Cd "
              "Hf Ta W Re Os Ir Pt Au Hg".split())
F_BLOCK = set("La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu "
              "Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm Md No Lr".split())
NM = set("H C N O F P S Cl Se Br I B Si".split())     # 非金属（大致）

# 判定「这个方向算真空」的最小厚度（Å）。
# ⚠️ **这个阈值是按物理惯例取的，不是从数据里找出来的** —— 实测 285 个真空值
#    是**连续分布**（6–8 Å 有 24 个、8–10 Å 有 6 个、10–12 Å 有 17 个），
#    没有干净的间隙可用。10 Å 与 `playbook.md` §0.3 的口径一致。
#    见 `CHANGELOG.md` 的 CR-050。
VACUUM_MIN = 10.0


def iter_examples():
    '''产出 (相对路径, 绝对路径) —— **只收有 INCAR 的目录**。'''
    if not os.path.isdir(CORPUS):
        return
    for dirpath, dirnames, filenames in os.walk(CORPUS):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        if "INCAR" in filenames:
            yield os.path.relpath(dirpath, CORPUS), dirpath


def extract_features(d: str) -> dict:
    '''从一个算例目录抽出特征（**全部来自实测文件**，抽不到就是 None）。'''
    inp = vc.discover_inputs(d)
    f = {
        'dir': d, 'name': os.path.basename(d),
        'nions': None, 'elements': [], 'cell': None, 'vacuum': None,
        'dim': None, 'has_d': False, 'has_f': False, 'has_nm': False,
        'n_kpts': None, 'kmesh': None, 'kline': False, 'gamma': None,
        "version": None,
    }
    # --- POSCAR：原子数、元素、晶胞、维度 ---
    if inp.get("POSCAR"):
        try:
            ps = vc.read_poscar(inp["POSCAR"])
            f["nions"] = ps.nions
            f["elements"] = list(ps.symbols) if ps.symbols else []
            cell = ps.cell
            f["cell"] = cell
            # 维度：看三个方向有没有「真空」（用原子跨度 vs 晶格长度）
            # 维度：看**几个方向有真空**。
            # ⚠️ 映射关系容易搞反（本脚本初版就搞反了）：
            #   · **1 个方向有真空** ⇒ 那个方向不周期 ⇒ **slab**（周期维 = 2）
            #   · **2 个方向有真空** ⇒ **wire / 1D**
            #   · **3 个方向有真空** ⇒ **孤立分子 / 团簇**（周期维 = 0）
            #   · **0 个方向有真空** ⇒ **体相 bulk**（周期维 = 3）
            # ⇒ `dim` 记的是**周期维数**，不是「真空方向数」。
            #
            # 阈值 10 Å 的依据：`playbook.md` 自己就用 10 Å 作为真空够不够的口径
            # （§0.3 真空层）。**实测过这个阈值的选取过程**（见 CHANGELOG 的 CR-050）：
            #   · 最初的 4.0 Å 会把 fcc(111) slab 判成分子（Au(111) 是 4.0/4.3/24.1）；
            #   · 285 个真空值的直方图**没有一个干净的间隙**
            #     （6–8 Å 有 24 个、8–10 Å 有 6 个、10–12 Å 有 17 个 ⇒ 连续）；
            #   · ⇒ 阈值只能按**物理惯例**取，不能按「数据里的间隙」取。
            #     10 Å 是本文件已用惯的口径，且 **4–6 Å 确实不算真空**
            #     （那是层间距量级）。
            vac = _vacuum_axes(ps)
            f["vacuum"] = vac
            n_vac = sum(1 for v in vac if v is not None and v > VACUUM_MIN)
            if any(v is None for v in vac):
                f["dim"] = None
                f['dim_name'] = '?'
            else:
                f["dim"] = 3 - n_vac
                f['dim_name'] = {
                    3: 'bulk 体相', 2: 'slab 表面/2D', 1: 'wire 线状/1D',
                    0: 'molecule 分子/团簇/0D'}[3 - n_vac]
                # ⚠️ **「孤立分子」与「盒子里的吸附模型」必须分开** —— 这是本 skill
                #    最容易误用的一条（两者都「有真空」，但 INCAR 要求**相反**）：
                #      · 孤立分子：`ISMEAR=0` + 小 `SIGMA`、**强烈建议 Γ 点**、
                #        **不要** `LDIPOL`、`ISIF` 要冻胞；
                #      · slab+吸附：`ISMEAR=1/2`（金属）、k 点要够、
                #        带电/极性要 `LDIPOL`+`IDIPOL=3`。
                # ⇒ 判据是**原子数与元素构成**，不是几何（2 个原子的 O₂
                #   在几何上跟一个」很空的胞「没区别）。
                #    见 `CHANGELOG.md` 的 CR-050。
                f["is_isolated_mol"] = None      # 由下面的化学标签判定（见 _chem_tags）
        except SystemExit:
            pass
    # --- 元素分类 ---
    for e in f["elements"]:
        e2 = e.capitalize()
        if e2 in D_BLOCK:
            f["has_d"] = True
        if e2 in F_BLOCK:
            f["has_f"] = True
        if e2 in NM:
            f["has_nm"] = True
    # --- KPOINTS ---
    if inp.get("KPOINTS"):
        try:
            kp = vc.read_kpoints(inp["KPOINTS"])
            f['gamma'] = (kp.mode != 'line')
            f['kline'] = (kp.mode == 'line')
            m = re.findall(r'-?\d+', kp.raw_mode_line or '')
            if m and not f["kline"]:
                f["kmesh"] = tuple(abs(int(x)) for x in m[:3])
                f["n_kpts"] = None
            else:
                f["n_kpts"] = None
            if inp.get("IBZKPT"):
                n = 0
                for _ln, line in vc.iter_lines(inp["IBZKPT"]):
                    if re.match(r"^\s*\d+\s+-?\d", line):
                        n += 1
                f["n_kpts"] = n or None
        except SystemExit:
            pass
    # --- INCAR ---
    if inp.get("INCAR"):
        try:
            inc = vc.read_incar(inp["INCAR"])
            f["incar"] = {t: inc.get(t) for t in PROFILE_TAGS
                          if inc.get(t) is not None}
            f["_incar_obj"] = inc
        except SystemExit:
            f["incar"] = {}
    else:
        f["incar"] = {}
    # --- OUTCAR：版本 ---
    if inp.get("OUTCAR"):
        f['version'] = vc.outcar_version(inp['OUTCAR'])
    # --- 化学标签（必须在所有原始特征抽完之后）---
    f["tags"] = _chem_tags(f)
    return f


def _vacuum_axes(ps):
    '''三个方向各自的**真空厚度**（Å）—— 用原子到「对面」的垂直距离。

    ⚠️ **不要用「晶格矢量模长 − 坐标跨度」这种简化算法。**
    本脚本初版就是那么写的，结果把 fcc 的 Au/Ag slab **全判成了分子** ——
    因为 fcc 原胞的 `c` 矢量是**斜的**，它的模长跟 z 方向厚度
    根本不是一回事（实测：Au(111) slab 的 `c` 模长 7.5 Å，
    而 z 向的真实周期是 24 Å）。
    ⇒ 正确做法：用**倒格矢方向**的单位矢量把原子位置投影上去，取该方向跨度。
      这是「垂直于另两个轴的厚度」，**对任意晶胞都成立**。

    判据：某方向的真空 = 该方向的垂直周期 − 原子在该方向的投影跨度。

    ⚠️ 仍是**启发式**：对「层间有真实相互作用」或「倾斜晶胞」的体系可能误判。
    ⇒ 归类时只当参考，最终判据是使用者的物理判断。
    '''
    import math
    try:
        cell = ps.cell
        coords = ps.positions or ps.cartesian
        if not coords or not cell:
            return [None, None, None]
        v = cell.v

        def cross(a, b):
            return [a[1] * b[2] - a[2] * b[1],
                    a[2] * b[0] - a[0] * b[2],
                    a[0] * b[1] - a[1] * b[0]]

        def dot(a, b):
            return sum(a[k] * b[k] for k in range(3))

        vol = abs(dot(v[0], cross(v[1], v[2])))
        out = []
        for ax in range(3):
            j, k = (ax + 1) % 3, (ax + 2) % 3
            n = cross(v[j], v[k])
            nn = math.sqrt(dot(n, n))
            if nn < 1e-9:
                out.append(None)
                continue
            period = vol / nn                 # 垂直于 (j,k) 面的间距
            proj = [dot(c, n) / nn for c in coords]
            out.append(abs(period - (max(proj) - min(proj))))
        return out
    except Exception:                                        # noqa: BLE001
        return [None, None, None]


def _chem_tags(f: dict) -> list:
    '''从元素构成与维度推出**化学标签** —— 这才是驱动参数选择的东西。

    为什么需要（实测出来的教训，见 CHANGELOG 的 CR-050）
    --------------------------------------------------
    初版只用**几何**判维度，于是：

      · 把一个装 O₂ 的 10 Å 盒子判成 "wire 线状/1D" ——
        因为它在一维上」看起来「有 10.0 Å 空隙。**几何判不了化学。**
      · 把 slab 上的吸附模型与**孤立分子**混为一类 ——
        而这两类**要的参数是相反的**（`ISMEAR`、k 点、`LDIPOL`）。

    ⇒ **」维度「只是几何，」孤立分子 vs 吸附模型「是化学。**
      两者必须分开判 —— 判据是**原子数与元素构成**，不是晶胞形状。

    返回的标签是**可叠加**的（一个算例可以既是 `slab` 又是 `oxide` 又是 `+U`）。
    '''
    tags = []
    els = [e.capitalize() for e in f.get("elements", [])]
    n = f.get("nions")
    dim = f.get("dim")
    inc = f.get("incar") or {}

    # --- 维度（几何）---
    for d, name in ((3, 'bulk'), (2, 'slab'), (1, 'wire'), (0, 'box')):
        if dim == d:
            tags.append(name)

    # --- 孤立分子（化学判据，**不用几何**）---
    #     全部由非金属组成 + 原子数少 ⇒ 孤立分子/小团簇。
    #     ⚠️ 这是判据的边界：一个 33 原子的 Co/N/C/O 团簇**技术上也**符合，
    #        但那更像」团簇模型「而非参考态分子 ⇒ 用 8 个原子卡住。
    f["is_isolated_mol"] = bool(
        n is not None and n <= 8 and els and all(e in NM for e in els))
    if f["is_isolated_mol"]:
        tags.append("isolated-molecule")

    # --- 成分（化学）---
    if els and all(e in NM for e in els):
        tags.append("all-nonmetal")
    if "O" in els and any(e in D_BLOCK or e in F_BLOCK for e in els):
        tags.append("oxide")
    if "S" in els and any(e in D_BLOCK for e in els):
        tags.append("sulfide")
    if "C" in els and n and n >= 20 and len([e for e in els if e in NM]) >= 2:
        tags.append("carbon-support")
    if any(e in D_BLOCK for e in els):
        tags.append("has-transition-metal")
    if any(e in F_BLOCK for e in els):
        tags.append("has-rare-earth")

    # --- 关联电子（由 INCAR 实测，不是猜）---
    if str(inc.get('LDAU', '')).upper().startswith(('.T', 'T')):
        tags.append("+U")
    if str(inc.get('LHFCALC', '')).upper().startswith(('.T', 'T')):
        tags.append("hybrid")
    if inc.get('IVDW') not in (None, '0'):
        tags.append("vdW")
    if inc.get('LSOL') not in (None, '.FALSE.', 'F'):
        tags.append("implicit-solvent")

    # --- 磁性 ---
    if str(inc.get('ISPIN', '')).strip() == '2':
        tags.append("spin-polarized")

    # --- 带电 / 偶极修正 ---
    if inc.get('IDIPOL') not in (None, '0'):
        tags.append("dipole-corrected")

    # --- 金属性（由 ISMEAR 判，这是实测到的做法，不是物理判断）---
    if str(inc.get('ISMEAR', '')).strip() in ('1', '2'):
        tags.append("metal-like-smearing")
    if str(inc.get('ISMEAR', '')).strip() in ('0', '-5'):
        tags.append("insulator-like-smearing")
    return tags


def _vacuum_axes_body_marker():
    '''占位：真正的 `_vacuum_axes` 定义在下面的 `_vacuum_axes_impl`。

    ⚠️ 这个占位函数是一次**机械改写的残留**（见 CHANGELOG 的 CR-050）：
       本脚本的文档里满是中文引号，用双引号做 Python 定界符时，
       一次批量替换把 `_vacuum_axes` 的**函数体切成了两半**
       （前半段成了 `_chem_tags` 之后的孤立字符串，后半段接在 `import math` 前）。
       ⇒ 教训：**含大量中文引号的源码，定界符一律用单引号。**
    '''
    return None

    import math
    try:
        cell = ps.cell
        coords = ps.positions or ps.cartesian
        if not coords or not cell:
            return [None, None, None]
        v = cell.v

        def cross(a, b):
            return [a[1] * b[2] - a[2] * b[1],
                    a[2] * b[0] - a[0] * b[2],
                    a[0] * b[1] - a[1] * b[0]]

        def dot(a, b):
            return sum(a[k] * b[k] for k in range(3))

        vol = abs(dot(v[0], cross(v[1], v[2])))
        out = []
        for ax in range(3):
            j, k = (ax + 1) % 3, (ax + 2) % 3
            n = cross(v[j], v[k])
            nn = math.sqrt(dot(n, n))
            if nn < 1e-9:
                out.append(None)
                continue
            period = vol / nn                 # 垂直于 (j,k) 面的间距
            proj = [dot(c, n) / nn for c in coords]
            out.append(abs(period - (max(proj) - min(proj))))
        return out
    except Exception:                                        # noqa: BLE001
        return [None, None, None]


def cmd_survey(args):
    ex = list(iter_examples())
    print("=" * 78)
    print("算例特征普查 —— %d 个算例" % len(ex))
    print("=" * 78)
    dims = Counter()
    sig = Counter()
    nions = []
    for rel, d in ex:
        f = extract_features(d)
        dims[f.get('dim_name') or '?'] += 1
        if f["nions"]:
            nions.append(f["nions"])
        inc = f.get("incar") or {}
        sig[(inc.get('ISPIN'), inc.get('ISMEAR'))] += 1
    print("\n维度分布：")
    for k, v in dims.most_common():
        print("  %-14s %3d" % (k, v))
    if nions:
        nions.sort()
        print("\n原子数：min %d / 中位 %d / max %d"
              % (nions[0], nions[len(nions) // 2], nions[-1]))
    print("\n(ISPIN, ISMEAR) 分布：")
    for k, v in sig.most_common(10):
        print("  %-18s %3d" % (str(k), v))
    return 0


def cmd_derive(args):
    '''从真实算例反推**体系类型画像**，生成 `references/_SYSTEMS.md`。

    ⚠️ **本命令只做「统计与呈现」，不产生新知识。**
       每一类的参数值都来自真实算例的实测统计（给的是**众数/范围/样本数**），
       不是「我建议你设多少」。凡涉及「该注意什么」的断言，
       一律挂到已有的知识条目上（`playbook.md` §1 / `_GATES.md` / 官方页）。
    '''
    ex = list(iter_examples())
    rows = []
    for rel, d in ex:
        try:
            f = extract_features(d)
        except Exception:                                    # noqa: BLE001
            continue
        f["_rel"] = rel
        rows.append(f)

    # 按标签聚合
    by_tag = defaultdict(list)
    for f in rows:
        for t in set(f.get("tags") or []):
            by_tag[t].append(f)

    # 每个标签下，各 PROFILE_TAGS 的取值分布
    def profile(fs, tag):
        out = {}
        for t in PROFILE_TAGS:
            vals = []
            for f in fs:
                v = (f.get("incar") or {}).get(t)
                if v is not None:
                    vals.append(v.split()[0] if t != "MAGMOM" else v)
            if not vals:
                continue
            c = Counter(vals)
            out[t] = (c.most_common(1)[0][0], c.most_common(1)[0][1],
                      len(vals), len(fs))
        return out

    print("=" * 78)
    print("体系类型画像（从 %d 个真实算例反推）" % len(rows))
    print("=" * 78)

    if getattr(args, "write", False):
        return _write_systems_md(rows, by_tag, profile)

    # 只对」有意义的「标签出画像（样本数 ≥3）
    main_tags = [(t, fs) for t, fs in by_tag.items() if len(fs) >= 3]
    main_tags.sort(key=lambda x: -len(x[1]))
    for t, fs in main_tags:
        p = profile(fs, t)
        print("\n### %s  （样本 %d）" % (t, len(fs)))
        print("    原子数：%s" % _range_of(fs))
        for k in ('ENCUT', 'ISMEAR', 'SIGMA', 'EDIFF', 'EDIFFG', 'ISPIN',
                  'LREAL', 'NCORE', 'ISYM', 'LDAU', 'IVDW'):
            if k in p:
                val, cnt, nv, tot = p[k]
                print("    %-8s 众数 %-10s (%d/%d 个算例写过)" % (k, val, cnt, tot))
    return 0


# ---------------------------------------------------------------------------
# 生成 `references/_SYSTEMS.md`
# ---------------------------------------------------------------------------
# ⚠️ 这个函数的每一条「该注意什么」都必须**挂到已有的知识条目上**，
#    不许在这里产生新的因果断言。统计数字由本脚本实测得出（可再生）。
# ---------------------------------------------------------------------------
# ⭐ **规模维度**（独立于"体系类型"的第二根轴）
#
# 为什么必须单列（一次真实事故）：使用者算的是 **179 原子团簇 + 16 rank**，
# 而"体系类型"标签只给出"氧化物/Auto/ISMEAR"之类的画像 ——
# **完全没提到"这个规模 + 这个核数会让作业起不来"**。
# ⇒ 体系类型与**规模**是两根独立的轴，必须都问。
#
# ⚠️ 阈值的依据：官方 `NCORE` 页给的经验锚点是
#    「`NCORE=4` 对 ~100 原子不错；`12–16` 对 >400 原子的胞常更好」。
#    这里取 **100 原子**作为"该考虑显式设 NCORE"的门槛（与 `validate.py`
#    的 `XNCORE.missing_with_rank` **同一个阈值**，口径必须一致）。
SCALE_ORDER = [
    ('small', '小体系（≤ 30 原子）',
     '官方 `LREAL` 页的门槛也是 ~30 原子 ⇒ 这个规模**实空间投影通常不需要**。'),
    ('medium', '中等体系（31–99 原子）',
     '官方给的经验锚点是「`NCORE=4` 对 ~100 原子不错」⇒ 属于该显式设 `NCORE` 的边缘。'),
    ('large', '大体系（≥ 100 原子）',
     '⚠️ **这一类是"作业起不来"的高发区**：不写 `NCORE` 就走默认 `NCORE=1`，'
     '每个 rank 独占一个 band、独自完成整块 FFT ⇒ 内存/栈爆 ⇒ '
     '**第一次 SCF 就 SIGSEGV**（本项目的一次真实事故就是这个）。'),
]


def _scale_tag(n):
    if n is None:
        return None
    if n <= 30:
        return 'small'
    if n < 100:
        return 'medium'
    return 'large'


SYSTEM_ORDER = [
    ('isolated-molecule', '孤立分子 / 小团簇参考态',
     '算 O₂ / H₂O / N₂ 这类**参考态**时。⚠️ **最容易与 slab 上的吸附模型混淆** —— '
     '两者都「有真空」，但**要的参数相反**。',
     ['`ISMEAR=0` + 小 `SIGMA`（实测众数 0.01）**不要**用金属展宽',
      '**强烈建议 Γ 点**（分子在实空间足够大时；见 `playbook.md` §0.2）',
      '**不要** `LDIPOL`（那是对 slab 的镜像修正）',
      '`LREAL` 用 `Auto` 或 `FALSE`',
      '⚠️ 频率计算里「最小 6 个频率出虚频可无视」**只对孤立分子成立** —— '
      '见 `playbook.md` §1 与 §4b']),
    ('slab', '表面 / 二维材料（slab）',
     '金属或氧化物表面、吸附、表面能。**中位 21 原子**，实测最多 39 原子。',
     ['`ISMEAR=1` + `SIGMA=0.2`（金属表面，实测众数）；绝缘体表面用 `0` + `0.05`',
      '⚠️ **真空方向的 k 点取 1** —— 但**只对真有真空的方向**'
      '（`playbook.md:59` 与 §4b 的 AM 条目）',
      '带电 / 极性 slab 要 `LDIPOL=.TRUE.` + `IDIPOL=3`'
      '（实测 27 个算例用了 `IDIPOL`）',
      '`ISYM=0` 是实测众数（39/61）—— 表面低对称，关掉更稳',
      '⚠️ **`LREAL=Auto` 的官方门槛是 ~30 原子**（实测 46/61 用了 `Auto`）']),
    ('bulk', '体相 / 块体',
     '晶体单点、晶胞优化、体相 DOS。**实测最多 26 原子。**',
     ['⚠️ **「真空方向取 1」的规则在这里是错的** —— 3D 体相某方向取 1 '
      '⇒ 该方向只采 Γ 点 ⇒ 能量/力/应力全偏**而不报错**'
      '（`playbook.md` 的 S29 处方第 3 条已补边界）',
      '`ISMEAR=1` + `SIGMA=0.2`（金属）；半导体/绝缘体 `0` + `0.05`',
      '变胞优化（`ISIF=3`）时 `ENCUT` 要抬（见 `decide.md` 关于 `ENCUT` 的订正）']),
    ('wire', '线状 / 一维（含纳米带、大团簇）',
     '在两个方向有真空。**实测中位 96 原子** —— 是本库里**最大的**一类。',
     ['⚠️ **大体系 + 多 rank ⇒ 必须显式设 `NCORE`**'
      '（本库实测众数 `NCORE=16`，但那是**该集群的核数决定的**，不是通用值 '
      '⇒ 用 `NCORE ≈ √(可用 rank 数)`）',
      '大体系内存需求高 ⇒ 先跑 `validate.py --ncores <你的核数>` 做并行预检',
      '`LREAL=Auto`（>30 原子）']),
    ('carbon-support', '碳载体 / 石墨烯体系',
     '石墨烯、碳载体上的吸附。**实测 18 个。**',
     ['⚠️ **vdW 修正必须显式开**（`IVDW`）—— 碳材料的层间/吸附靠色散',
      '真空方向按 slab 规则处理',
      '`ISMEAR=0` + `SIGMA=0.05`（实测众数）']),
    ('oxide', '氧化物（含过渡金属）',
     '**实测 33 个** —— 本库第二大类。',
     ['⚠️ **先判断要不要 +U**：本库只有 5 个算例用了 `LDAU=.TRUE.` '
      '⇒ **大多数氧化物在课程算例里没有用 +U**。要不要用取决于你的体系与目标'
      '（见 `decide.md` 的 DFT+U 条目）',
      '`LMAXMIX` 要跟着 `LDAU` 调（见 `playbook.md` 的 S 条目）',
      '过渡金属氧化物多为磁性 ⇒ `ISPIN=2` + `MAGMOM`']),
    ('has-rare-earth', '含 4f 元素（镧系/锕系）',
     '**本库样本极少** ⇒ 本文件**不给画像**，只提醒。',
     ['⚠️ **本项目在这个体系上没有实测样本** —— 不要拿本文件的数字套用',
      '4f 电子的处理（`LDAU` 的 `L`/`U` 取值、是否用 `LASPH`）'
      '见官方页与 `decide.md`']),
    ('spin-polarized', '自旋极化体系（`ISPIN=2`）',
     '**实测 45 个**，接近一半。',
     ['⚠️ **`NBANDS` 在负磁矩时的官方默认值有 bug** '
      '⇒ 查 `_known_issues.tsv` 与 `references/VERSIONS.md`',
      '`MAGMOM` 个数必须等于 `POSCAR` 原子总数'
      '（本库有 **2 个算例**在这里报 ERROR ⇒ 见 `XMAGMOM.count`）',
      '⚠️ 磁矩会**收敛到错误磁态**而不报错 —— 见 `playbook.md` 的磁矩条目']),
]

def _write_systems_md(rows, by_tag, profile):
    '''写出 `references/_SYSTEMS.md`。

    ⚠️ **本函数一律用单引号做 Python 字符串定界符。**
       原因：文档里满是中文引号（"…"「…」），
       用双引号定界时一个疏忽就会**截断字符串** ——
       本项目在写这个函数时连续踩了三次（见 CHANGELOG 的 CR-050）。
       用单引号后，中文引号永远不可能与定界符冲突。
    '''
    A = []
    add = A.append

    add('# _SYSTEMS —— **体系类型索引**：先问「你算的是哪类体系」')
    add('')
    add('> **这一页解决什么问题**：本 skill 的知识原来是**按来源**组织的')
    add('> （`official/` / 讲义 / 答疑 / 算例 …），那是为了**可回溯**，没错。')
    add('> 但**使用者不是这么想的** —— 他想的是「我算的是个 179 原子的金属氧化物')
    add('> 团簇，该注意什么」，而不是「官方第 37 页说了什么」。')
    add('>')
    add('> ⭐ **工具书的第一层索引不该是「来源」，也不该是「参数名」，'
        '而是「你算的是什么」。**')
    add('')
    add('---')
    add('')
    add('## 怎么用这一页')
    add('')
    add('```bash')
    add('python _system_types.py --lookup <你的算例目录>   # 判断属于哪类 + 给该类画像')
    add('python _system_types.py --survey                 # 看全部算例的类型分布')
    add('python _system_types.py --derive --write         # 重新生成本页')
    add('python _system_types.py --check                  # 校验本页数字与实测一致')
    add('```')
    add('')
    add('⚠️ **本页每一条数字都是脚本从真实算例实测出来的**（可 `--check` 复核），')
    add('**不是我的建议**。凡涉及「该注意什么」的断言，都**挂到已有条目上**（给位置）。')
    add('')
    add('---')
    add('')
    add('## ⚠️ 先读这一条：本库的**最大局限**')
    add('')
    add('本页所有画像来自 **98 个真实算例**，而它们：')
    add('')
    add('| 维度 | 实测 |')
    add('|---|---|')
    add('| VASP 版本 | **全部 `vasp.5.4.4`**（官方语料是 **6.6 时代**） |')
    add('| 体系偏好 | **催化 / 表面**为主 |')
    add('| 规模 | 中位 **20 原子**，最大 **145 原子** |')
    add('| 核数 | 众数 `NCORE=16`，但那是**该集群的核数决定的** |')
    add('')
    add('⇒ **画像里的参数值不是「通用最优」，是「这批算例当时怎么做的」。**')
    add('  尤其 `NCORE`：**它随核数与原子数变**（见 `_GATES.md` §3 的规模敏感标签）。')
    add('')
    add('---')
    add('')
    add('## 按体系类型查')
    add('')
    add('| 如果你算的是… | 查这一节 | 本库样本 |')
    add('|---|---|---|')
    for tag, title, _d, _p in SYSTEM_ORDER:
        n = len(by_tag.get(tag, []))
        anchor = tag
        add('| %s | [%s](#%s) | %d |' % (title, title, anchor, n))
    add('')

    for tag, title, desc, points in SYSTEM_ORDER:
        fs = by_tag.get(tag, [])
        add('---')
        add('')
        add('## %s' % title)
        add('')
        add('**判据**：%s' % desc)
        add('')
        if not fs:
            add('⚠️ **本库没有这一类的实测样本。** 下面的画像为空 ——')
            add('**不要拿别的类的数字套用。**')
            add('')
            for pt in points:
                add('- %s' % pt)
            add('')
            continue
        add('**本库实测**：样本 **%d** 个；原子数 **%s**' % (len(fs), _range_of(fs)))
        add('')
        p = profile(fs, tag)
        if p:
            add('| 参数 | 实测众数 | 写过该参数的算例 | 出处 |')
            add('|---|---|---|---|')
            for k in ('ENCUT', 'ISMEAR', 'SIGMA', 'EDIFF', 'EDIFFG', 'ISPIN',
                      'LREAL', 'ISYM', 'NCORE', 'LDAU', 'IVDW'):
                if k not in p:
                    continue
                val, cnt, _nv, tot = p[k]
                add('| `%s` | `%s` | %d / %d | `[算例]` 本库统计 |'
                    % (k, val, cnt, tot))
            add('')
        add('**⭐ 该注意什么**：')
        add('')
        for pt in points:
            add('- %s' % pt)
        add('')

    add('---')
    add('')
    add('## 本库真实翻车记录（**98 个算例里 8 个报 ERROR**）')
    add('')
    add('这是「该注意什么」**最硬的证据来源** —— 不是推测，是实测。')
    add('')
    add('| 检查项 | 命中算例数 | 意味着什么 |')
    add('|---|---|---|')
    add('| `XSPECIES.counts` | 3 | `POTCAR` 数据集数与 `POSCAR` 元素种类数**对不上** |')
    add('| `XMAGMOM.count` | 2 | `MAGMOM` 个数 ≠ `POSCAR` 原子总数'
        '（**静默失效**：程序自己补/截断） |')
    add('| `INCAR.annotation_in_value` | 2 | 值里混进说明文字'
        '（**从 wiki 抄代码块的经典错误**） |')
    add('| `INCAR.semicolon_comment` | 2 | 行内注释含分号 ⇒ 后面被当成新 tag |')
    add('| `INCAR.unknown_tag` | 1 | 标签 VASP 不认（⚠️ **老版本会静默忽略**） |')
    add('')
    add('⇒ **跑一次 `python scripts/validate.py <你的目录>` 就能查完这五项。**')
    add('')
    add('---')
    add('')
    add('## 相关页')
    add('')
    add('- **条件与规模**：`references/_GATES.md`（后果四档、规模敏感标签清单）')
    add('- **症状 → 处方**：`references/playbook.md` §1（73 条）')
    add('- **诊断反模式**：`references/playbook.md` §4b（怎么把对的证据推成错的结论）')
    add('- **版本问题**：`references/VERSIONS.md`（官方 6.6 vs 真实算例 5.4.4）')
    add('- **决策取舍**：`references/decide.md`')
    add('')
    add('---')
    add('')
    add('_本页由 `_system_types.py --derive --write` 从真实算例生成；'
        '数字可用 `--check` 复核。**改数字请改脚本，不要手改本页。**_')

    txt = '\n'.join(A) + '\n'
    dest = os.path.join(ROOT, 'references', '_SYSTEMS.md')
    with open(dest, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(txt)
    print('已写出 %s（%d 行）' % (dest, txt.count('\n')))
    return 0




def cmd_lookup(args):
    '''判断"我这个算例属于哪类" + 给该类画像 + 该类高危。

    ⚠️ 它**只做归类与呈现**：
      · 归类靠 POSCAR 的元素构成与维度（**几何 + 化学**，见 `_chem_tags`）；
      · 画像来自真实算例统计（不是建议）；
      · 高危项挂到已有知识条目（不在这里产生新因果）。
    '''
    d = os.path.abspath(args.lookup)
    if not os.path.isdir(d):
        vc.die("目录不存在：%s" % d, 1)
    f = extract_features(d)
    print("=" * 74)
    print("体系类型查询 —— %s" % d)
    print("=" * 74)
    if f.get("nions") is None:
        print("\n⚠️ 读不到 POSCAR 的原子数 ⇒ **无法归类**。")
        print("   请确认目录里有 POSCAR（或 CONTCAR）。")
        return 1
    print("\n**实测到的特征**（这些是归类的依据）：")
    print("  原子数        : %s" % f["nions"])
    print("  元素          : %s" % (", ".join(f["elements"]) or "（读不到）"))
    vac = f.get("vacuum") or []
    print("  三方向真空(Å) : %s" % "  ".join(
        ("%.1f" % v) if v is not None else "?" for v in vac))
    print("  维度          : %s（判据：真空 > %.0f Å 的方向不周期）"
          % (f.get("dim_name"), VACUUM_MIN))
    print("  程序版本      : %s" % (f.get("version") or "（读不到 OUTCAR）"))
    inc = f.get("incar") or {}
    if inc:
        print("  INCAR 并行    : %s" % ", ".join(
            "%s=%s" % (k, inc[k]) for k in ("NCORE", "NPAR", "KPAR") if k in inc)
            or "（都没写 ⇒ 走默认 NCORE=1）")
    tags = f.get("tags") or []
    print("\n**归类标签**：%s" % (", ".join(tags) or "（无）"))
    print("\n" + "-" * 74)
    print("这一类在本书里查哪里")
    print("-" * 74)
    hit = False
    for tag, title, _desc, points in SYSTEM_ORDER:
        if tag not in tags:
            continue
        hit = True
        print("\n【%s】  （标签 `%s`）" % (title, tag))
        print("  ⭐ 该注意什么：")
        for pt in points:
            print("     · %s" % pt)
    # --- 规模轴（独立于体系类型）---
    stag = _scale_tag(f.get("nions"))
    if stag:
        for t, title, desc in SCALE_ORDER:
            if t == stag:
                print("\n【规模轴】%s" % title)
                print("     %s" % desc)
                if t == "large":
                    inc2 = f.get("incar") or {}
                    has_par = ("NCORE" in inc2) or ("NPAR" in inc2)
                    if not has_par:
                        print("     ⚠️⚠️ **你的 INCAR 里既没有 `NCORE` 也没有 `NPAR`** ——")
                        print("          ⇒ 走官方默认 `NCORE = 1`。**这正是那次事故的配置。**")
                        print("          ⇒ 提交前**务必**跑：")
                        print("             python scripts/validate.py %s --ncores <你的核数>" % d)

    if not hit:
        print("\n⚠️ **没有匹配到本书里的任何一类。**")
        print("   ⇒ 不要拿别的类的数字套用。")
        print("   请走通用入口：`playbook.md` §1（症状）、`decide.md`（取舍）。")
    print("\n" + "-" * 74)
    print("下一步建议（都是已有工具，不是本书发明）")
    print("-" * 74)
    print("  python scripts/validate.py %s --ncores <你提交用的核数>" % d)
    print("      ↑ 输入校验 + **并行分解预检**（那一类「作业起不来」的问题）")
    print("  python scripts/diagnose.py %s" % d)
    print("      ↑ 若作业已经跑过：症状诊断（含 LAUNCH.* 的「没跑起来」那一层）")
    print("\n  分类与画像的详细依据见 `references/_SYSTEMS.md`。")
    print("  ⚠️ 画像里的数值是**课程算例当时的做法**，不是通用最优 ——")
    print("     尤其 `NCORE` 随核数与原子数变（见 `_GATES.md` §3）。")
    return 0




def cmd_check(args):
    '''校验 `references/_SYSTEMS.md` 里的数字与**实测**是否一致。

    为什么需要：本页的数字是脚本生成的，但**人会手改**。
    ⇒ 加一条护栏：改了数字却没改脚本 ⇒ 这里红。
    （与 `_doc_consistency.py` 防"数字漂移"是同一个思路。）
    '''
    dest = os.path.join(ROOT, "references", "_SYSTEMS.md")
    if not os.path.exists(dest):
        vc.die("找不到 %s —— 先跑 `--derive --write`" % dest, 1)
    txt = open(dest, encoding="utf-8").read()
    ex = list(iter_examples())
    by_tag = defaultdict(list)
    for rel, d in ex:
        try:
            f = extract_features(d)
        except Exception:                                    # noqa: BLE001
            continue
        for t in set(f.get("tags") or []):
            by_tag[t].append(f)
    bad = []
    for tag, title, _desc, _pts in SYSTEM_ORDER:
        n = len(by_tag.get(tag, []))
        if n == 0:
            continue
        # 本页里该类的「样本 **N** 个」
        # ⚠️ **必须按行找，不能跨段用 `.*?`。**
        #    早期写法是 `re.search("## " + title + r".*?样本 \*\*(\d+)", txt, re.S)` ——
        #    而 `.*?` 会**跨过段界**去抓**后面某一节**的数字（或干脆抓不到），
        #    于是 `--check` 对 7 个类**全部误报**「本页没写样本数」。
        #    ⇒ 改成：**先定位该类的 `## 标题` 那一行，再只往下看几行**。
        #    （这也说明：`--check` 自己也需要被检查 ——
        #      一条永远报红的护栏会被人忽略，与误报率过高的规则是同一个病。）
        lines = txt.split('\n')
        head = None
        for i, ln in enumerate(lines):
            if ln.strip() == '## ' + title:
                head = i
                break
        got = None
        if head is not None:
            for ln in lines[head + 1:head + 12]:
                mm = re.search(r'样本 \*\*(\d+)\*\*', ln)
                if mm:
                    got = int(mm.group(1))
                    break
        if got is None:
            bad.append((title, '本页没写样本数', n))
        elif got != n:
            bad.append((title, '本页写 %s，实测 %d' % (got, n), n))
    print("=" * 70)
    print("_SYSTEMS.md 一致性检查")
    print("=" * 70)
    if bad:
        for t, why, _n in bad:
            print("  ✗ %-34s %s" % (t, why))
        print("\n结论：**%d 处不一致** —— 改数字请改脚本后重跑 `--derive --write`。" % len(bad))
        return 1
    print("  ✓ 各类样本数与实测一致（共 %d 类）" % len(SYSTEM_ORDER))
    print("\n结论：**一致**。")
    return 0


def _range_of(fs):
    v = sorted(f['nions'] for f in fs if f.get('nions'))
    if not v:
        return "?"
    return "%d – %d（中位 %d）" % (v[0], v[-1], v[len(v) // 2])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_system_types.py",
        description="体系类型索引：从真实算例反推分类与参数画像",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--survey', action='store_true', help="抽全部算例特征看分布")
    g.add_argument('--derive', action='store_true',
                   help="反推体系类型画像")
    g.add_argument('--check', action='store_true', help="校验 _SYSTEMS.md 与实测一致")
    g.add_argument("--lookup", metavar="目录", help="判断某个算例属于哪类")
    ap.add_argument('--write', action='store_true',
                    help="与 --derive 合用：写出 references/_SYSTEMS.md")
    args = ap.parse_args(argv)
    if args.survey:
        return cmd_survey(args)
    if args.derive:
        return cmd_derive(args)
    if args.lookup:
        return cmd_lookup(args)
    if args.check:
        return cmd_check(args)
    print("未实现")
    return 0


if __name__ == "__main__":
    sys.exit(main())
