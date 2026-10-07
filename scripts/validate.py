#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""validate.py —— VASP 四件套的离线校验（**零依赖**）

它到底查什么、不查什么（**先读这段，否则会误信它的 OK**）
=======================================================
本工具的 `OK` **只表示"我检查过的那些项没发现问题"**。它检查的层次是：

| 层 | 本工具能查 | 说明 |
|---|---|---|
| ① 语法 | ✅ | tag = value 形式、`;` 分隔、续行、引号跨行 |
| ② 关键字归属 | ✅（**有覆盖率上限**） | tag 是否真的存在、是否属于该文件 |
| ③ 值域/类型 | ✅（**部分**） | 已知取值域的 tag 会查；很多 tag 的取值域本工具**没收录** |
| ④ 跨文件一致性 | ✅ | 元素顺序、ENCUT vs ENMAX、ISPIN vs MAGMOM 个数、维度 vs k 点 |
| ⑤ 设置之间的矛盾 | ✅（**只覆盖一部分组合**） | 见每一项的 id |
| ⑥ **"语法全对但程序不接受"** | ❌ | 原理上要**真程序**才能抓 —— 见 `conformance/` |
| ⑦ **"算得不对"**（物理错误） | ❌ | 见 `compare.py`（物理不变量）与 `diagnose.py` |

**每一份报告都会显式列出"本次未检查的项"** —— 这是本工具的核心设计，
因为本项目最贵的教训就是"校验器报 OK，用户据此上了集群，白跑一趟"：
那个 OK 的真实含义只是"语法与段名拼写没问题"，而缺陷恰好在它没检查的那一层。

退出码
------
| 码 | 含义 |
|---|---|
| 0 | 未发现 ERROR 级问题（**不等于"算得对"**） |
| 1 | 文件不存在/读不了 |
| 2 | 命令行用法错误 |
| 4 | 发现 ERROR 级问题 |
| 5 | 只发现 WARNING 级问题（`--strict` 时提升为 4） |

用法
----
    python scripts/validate.py <算例目录>
    python scripts/validate.py <算例目录> --strict
    python scripts/validate.py --incar INCAR --kpoints KPOINTS --poscar POSCAR
    python scripts/validate.py <目录> --potcar <目录外的POTCAR路径>
    python scripts/validate.py --list-checks
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3
EXIT_ERROR, EXIT_WARN = 4, 5

HERE = os.path.dirname(os.path.abspath(__file__))
KW_TABLE = os.path.join(HERE, os.pardir, "references", "official",
                        "_keywords.tsv")
KW_ALIAS = os.path.join(HERE, os.pardir, "references", "official",
                        "_keyword_aliases.tsv")


# ---------------------------------------------------------------------------
# 关键字表（归属校验的唯一依据）
# ---------------------------------------------------------------------------
class KeywordTable:
    """从 `references/official/_keywords.tsv` 读"关键字 → 所属文件"。

    **覆盖率是有限的，而且这一点必须如实传播到输出里。**
    表由 `references/official/_fetch_wiki.py` 抓官方 wiki 的
    `Category:INCAR_tag` 等分类页生成，因此它反映的是**抓取那天**的官方标签集；
    官方新增标签而没重抓，就会在这里被误报成"未知关键字"。
    """

    def __init__(self, path: str = KW_TABLE, alias_path: str = KW_ALIAS):
        self.by_file = {}          # file -> {tag: (category, summary)}
        self.loaded = False
        self.n = 0
        self.reason = ""
        self.aliases = {}          # 旧名/别名 -> 现名
        self._load(path, alias_path)

    def _load(self, path: str, alias_path: str) -> None:
        if not os.path.exists(path):
            self.reason = ("没有找到官方关键字表 %s。\n"
                           "  → 归属校验（「这个 tag 到底存不存在」）本次**未执行**。\n"
                           "  → 生成它：python references/official/_fetch_wiki.py"
                           % os.path.relpath(path))
            return
        try:
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) < 3:
                        continue
                    tag, target, cat = parts[0], parts[1], parts[2]
                    summary = parts[3] if len(parts) > 3 else ""
                    self.by_file.setdefault(target, {})[tag.upper()] = (cat, summary)
                    self.n += 1
        except OSError as exc:
            self.reason = "读不了关键字表 %s：%s" % (path, exc)
            return
        self.loaded = True
        if os.path.exists(alias_path):
            with open(alias_path, encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("#") or not line.strip():
                        continue
                    parts = line.rstrip("\n").split("\t")
                    if len(parts) >= 2:
                        self.aliases[parts[0].upper()] = parts[1].upper()

    def has(self, target: str, tag: str) -> bool:
        return tag.upper() in self.by_file.get(target, {})

    def resolve(self, tag: str) -> "str | None":
        """把别名解析成现行标签名（如 `LUSE_VDW`→`LUSE_VDW` 之类）。"""
        return self.aliases.get(tag.upper())


# ---------------------------------------------------------------------------
# 已知取值域（**只收录有官方依据的**；没收的不查，并在报告里说明）
# ---------------------------------------------------------------------------
# 每条：(校验函数, 出错信息模板, 出处标记)
def _is_bool_text(v: str) -> bool:
    s = v.strip().strip(".").upper()
    return s in ("TRUE", "FALSE", "T", "F")


def _strip_dots(v: str) -> str:
    """把 VASP 的 `.FALSE.` / `.TRUE.` 归一成 `FALSE` / `TRUE`。

    必须**两端都剥**：早期版本只写了 `rstrip(".")`，于是 `.FALSE.` 变成
    `FALSE` 能过，但 `.TRUE.` 变成 `TRUE` 也能过 —— 看起来对，
    可是 `T.` 这种写法会漏判。统一用 strip 更稳。
    （本条是构建过程中真实踩到的假阳性，已记入 CHANGELOG 更正记录。）
    """
    return v.strip().strip(".").upper()


def _is_int_text(v: str) -> bool:
    try:
        int(float(v.split()[0]))
        return True
    except (ValueError, IndexError):
        return False


def _is_float_text(v: str) -> bool:
    try:
        float(v.split()[0])
        return True
    except (ValueError, IndexError):
        return False


def _is_int_list(v: str, n: "int | None" = None) -> bool:
    toks = v.split()
    if not toks:
        return False
    try:
        [int(float(t)) for t in toks]
    except ValueError:
        return False
    return n is None or len(toks) == n


def _is_float_list(v: str, n: "int | None" = None) -> bool:
    toks = v.split()
    if not toks:
        return False
    try:
        [float(t) for t in toks]
    except ValueError:
        return False
    return n is None or len(toks) == n


# 说明：这里的"取值域"只写**官方明文能背书的**部分。
# 凡是没有把握的 tag，宁可不列 —— 列错了会给出假的确定感。
VALUE_CHECKS = {
    "ISMEAR": (lambda v: _is_int_text(v) and int(float(v)) in
               (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14),
               "ISMEAR 应为整数（-5=四面体+Bloechl 修正，-4=四面体，"
               "-1=Fermi，0=Gaussian，1..=Methfessel-Paxton 阶数）",
               "VASP wiki: ISMEAR"),
    "ISPIN": (lambda v: _is_int_text(v) and int(float(v)) in (1, 2),
              "ISPIN 只能是 1（非自旋极化）或 2（自旋极化）",
              "VASP wiki: ISPIN"),
    "IBRION": (lambda v: _is_int_text(v) and int(float(v)) in
               (-1, 0, 1, 2, 3, 4, 5, 6, 7, 8),
               "IBRION 应为 -1/0/1/2/3/4/5/6/7/8 之一",
               "VASP wiki: IBRION"),
    "ISIF": (lambda v: _is_int_text(v) and int(float(v)) in (0, 1, 2, 3, 4, 5, 6, 7),
             "ISIF 应为 0..7",
             "VASP wiki: ISIF"),
    "ISYM": (lambda v: _is_int_text(v) and int(float(v)) in (-1, 0, 1, 2, 3),
             "ISYM 应为 -1/0/1/2/3",
             "VASP wiki: ISYM"),
    "ALGO": (lambda v: v.strip().upper().rstrip(".") in
             ("NORMAL", "FAST", "VERYFAST", "ALL", "DAMPED", "DIAG", "CHI",
              "SUBROT", "N", "F", "V", "A", "D", "C"),
             "ALGO 应为 Normal/Fast/VeryFast/All/Damped/Diag/Chi/Subrot 之一",
             "VASP wiki: ALGO"),
    "PREC": (lambda v: v.strip().lower() in
             ("low", "medium", "high", "normal", "accurate", "single"),
             "PREC 应为 Low/Medium/High/Normal/Accurate/Single 之一",
             "VASP wiki: PREC"),
    "GGA": (lambda v: v.strip().upper() in
            ("PE", "PBE", "PS", "PB", "RE", "RP", "CA", "HL", "LIBXC", "MK",
             "ML", "OR", "BO", "VI", "VDW", "AM"),
            "GGA 取值见 VASP wiki: GGA（本工具只收录常见缩写，"
            "可能漏掉新版本新增的值）",
            "VASP wiki: GGA"),
    "METAGGA": (lambda v: v.strip().upper() in
                ("NONE", "TPSS", "RTPSS", "M06L", "MBJ", "SCAN", "R2SCAN",
                 "MS0", "MS1", "MS2"),
                "METAGGA 取值见 VASP wiki: METAGGA（本工具收录可能不全）",
                "VASP wiki: METAGGA"),
    "LREAL": (lambda v: _strip_dots(v) in
              ("FALSE", "F", "TRUE", "T", "AUTO", "A"),
              "LREAL 应为 .FALSE./.TRUE./Auto",
              "VASP wiki: LREAL"),
    "LDAUTYPE": (lambda v: _is_int_text(v) and int(float(v)) in (1, 2, 3, 4),
                 "LDAUTYPE 应为 1/2/3/4（2 是常用的 Dudarev 型）",
                 "VASP wiki: LDAUTYPE"),
    "NELM": (lambda v: _is_int_text(v) and int(float(v)) > 0,
             "NELM 应为正整数", "VASP wiki: NELM"),
    "NELMIN": (lambda v: _is_int_text(v) and int(float(v)) >= 0,
               "NELMIN 应为非负整数", "VASP wiki: NELMIN"),
    "NSW": (lambda v: _is_int_text(v) and int(float(v)) >= 0,
            "NSW 应为非负整数（0 = 只做单点）", "VASP wiki: NSW"),
    "ENCUT": (lambda v: _is_float_text(v) and float(v.split()[0]) > 0,
              "ENCUT 应为正数（单位 eV）", "VASP wiki: ENCUT"),
    "SIGMA": (lambda v: _is_float_text(v) and float(v.split()[0]) >= 0,
              "SIGMA 应为非负数（单位 eV）", "VASP wiki: SIGMA"),
    "EDIFF": (lambda v: _is_float_text(v) and float(v.split()[0]) > 0,
              "EDIFF 应为正数（单位 eV）", "VASP wiki: EDIFF"),
    "EDIFFG": (lambda v: _is_float_text(v) and float(v.split()[0]) != 0,
               "EDIFFG 应非零（eV/Å；**负值**表示力判据，正值表示能量判据）",
               "VASP wiki: EDIFFG"),
    "POTIM": None,   # 见下方 SPECIAL_VALUE_CHECKS（需要看 IBRION 才能判）
    "NCORE": (lambda v: _is_int_text(v) and int(float(v)) >= 1,
              "NCORE 应为正整数", "VASP wiki: NCORE"),
    "KPAR": (lambda v: _is_int_text(v) and int(float(v)) >= 1,
             "KPAR 应为正整数", "VASP wiki: KPAR"),
    "IVDW": (lambda v: _is_int_text(v) and int(float(v)) in
             (0, 1, 2, 10, 11, 12, 20, 21, 202, 263, 4, 5, 6, 7, 8, 9),
             "IVDW 取值见 VASP wiki: IVDW（本工具收录可能不全；"
             "11=D3，12=D3(BJ)，202=AXSZ 等）",
             "VASP wiki: IVDW"),
    "NELECT": (lambda v: _is_float_text(v), "NELECT 应为数值（可为小数表示带电）",
               "VASP wiki: NELECT"),
    "MAGMOM": (lambda v: bool(v.split()) and all(
        _is_float_text(t) or re.fullmatch(r"\d+\*[-\d.eE+]+", t)
        for t in v.split()),
        "MAGMOM 每个 token 应为数值，或 `N*x` 形式的重复（如 `4*2.0`）",
        "VASP wiki: MAGMOM"),
    "LDAUL": (lambda v: _is_int_list(v), "LDAUL 应为整数列表", "VASP wiki: LDAUL"),
    "LDAUU": (lambda v: _is_float_list(v), "LDAUU 应为数值列表",
              "VASP wiki: LDAUU"),
    "LDAUJ": (lambda v: _is_float_list(v), "LDAUJ 应为数值列表",
              "VASP wiki: LDAUJ"),
    "NEDOS": (lambda v: _is_int_text(v) and int(float(v)) > 0,
              "NEDOS 应为正整数", "VASP wiki: NEDOS"),
    "LORBIT": (lambda v: _is_int_text(v) and int(float(v)) in (0, 1, 2, 5, 10, 11, 12),
               "LORBIT 应为 0/1/2/5/10/11/12", "VASP wiki: LORBIT"),
    "ICHARG": (lambda v: _is_int_text(v) and int(float(v)) in
               (0, 1, 2, 4, 10, 11, 12),
               "ICHARG 应为 0/1/2/4/10/11/12", "VASP wiki: ICHARG"),
    "ISTART": (lambda v: _is_int_text(v) and int(float(v)) in (0, 1, 2, 3),
               "ISTART 应为 0/1/2/3", "VASP wiki: ISTART"),
    "ISYM_STRICT": (lambda v: True, "", ""),
    "LMAXMIX": (lambda v: _is_int_text(v) and int(float(v)) in (2, 4, 6),
                "LMAXMIX 应为 2/4/6（含 d 电子用 4，含 f 电子用 6）",
                "VASP wiki: LMAXMIX"),
}
# 上面这条占位的 ISYM_STRICT 不是真标签，删掉它避免污染表
VALUE_CHECKS.pop("ISYM_STRICT", None)
# POTIM 的检查需要看 IBRION，所以不放在 VALUE_CHECKS 里（见 _check_potim）
VALUE_CHECKS.pop("POTIM", None)


def _unknown_tag_finding(tag: str, where: str, kw: "KeywordTable",
                         recognized: "set[str]") -> Finding:
    """一个不在官方分类表里的 INCAR 标签，到底该怎么报？—— **分三档**。

    这个分档是本项目一个真实的教训：官方 wiki 的 `Category:INCAR_tag`
    收有 613 个标签，但它**并不完整**。实测（2026-11，用 wiki API 逐页查证）：

    | 标签 | 在 `Category:INCAR_tag` | wiki 有独立页面 |
    |---|---|---|
    | `LUSE_VDW` `ZAB_VDW` `AMIX_MAG` `BMIX_MAG` `NKRED` `HFSCREEN` | ❌ 不在 | ✅ 有 |
    | `ICHAIN` `IOPT` `LCLIMB` | ❌ 不在 | ❌ 没有 |
    | `LSOL` `LRHOB`（VASPsol 插件） | ❌ 不在 | ❌ 没有 |

    ⇒ **光靠分类表会把 `LUSE_VDW` 这种货真价实的标签判成"拼错了"**，
    这正是"放宽判据前先问：是判据太严，还是被检对象真的错了"的场景
    —— 这里是判据太窄。于是分三档：

    1. **OUTCAR 回显里有它** ⇒ `INFO`。官方 INCAR 页明说 VASP 会把自己
       对 INCAR 的理解写进 OUTCAR；出现即证明程序认了它。**证据最强**。
    2. **OUTCAR 存在但没有它** ⇒ `ERROR`。这是**可证伪的静默失效**：
       程序确实没读这个标签，你的设置没生效。
    3. **没有 OUTCAR 可比** ⇒ `WARN`，并如实说明"无法判定，需你自己核对"。
    """
    in_echo = tag in recognized
    if recognized and in_echo:
        return Finding(
            "INFO", "INCAR.unknown_tag", where,
            "%s 不在官方 INCAR 分类表里，但 **OUTCAR 的回显里有它**" % tag,
            "官方 INCAR 页说 VASP 会把自己对 INCAR 的理解写进 OUTCAR。"
            "既然回显里出现了这个名字，说明**程序确实认了它** ——"
            "它只是没被收进 wiki 的 `Category:INCAR_tag`。"
            "⚠️ 本工具因此**不把它判为错误**（判据太窄是判据的问题，不是输入的问题）。",
            "无需改动。若想更放心，可在 references/official/ 里把这个标签"
            "补进人工核对过的清单。",
            "OUTCAR 回显（%s）；对照 VASP wiki 的 Category:INCAR_tag" % tag)
    if recognized and not in_echo:
        return Finding(
            "ERROR", "INCAR.unknown_tag", where,
            "INCAR 里写了 %s，但 **OUTCAR 的回显里找不到它** —— "
            "也就是说这次运行**根本没读这个标签**" % tag,
            "官方 INCAR 页说 VASP 会把自己对 INCAR 的理解写进 OUTCAR。"
            "本目录里**有** OUTCAR，而回显里没有这个标签名 ⇒ "
            "它被**静默忽略**了：不报错，但你的设置完全没生效。"
            "这类缺陷正是「程序不报错、但结果是错的」最常见的成因。"
            "（两种可能：拼错了；或者这个标签属于你**没有编译进去**的插件，"
            "如 VASPsol 的 `LSOL`/`LRHOB`。）",
            "① 核对拼写；② 若这是插件标签，确认运行的可执行文件里"
            "确实编进了该插件；③ 用 grep 在 OUTCAR 里搜一次确认。",
            "OUTCAR 回显（本文件里没有 %s）" % tag)
    return Finding(
        "WARN", "INCAR.unknown_tag", where,
        "INCAR 里出现 %s：它**不在**官方 INCAR 分类表里" % tag,
        "两种可能，本工具**分不出来**：\n"
        "        (a) 拼写错误 —— 会被 VASP 静默忽略，设置不生效；\n"
        "        (b) 真实存在但没被收进 wiki 的 `Category:INCAR_tag`\n"
        "            （实测至少有 LUSE_VDW / ZAB_VDW / AMIX_MAG / BMIX_MAG /\n"
        "             NKRED / HFSCREEN 属于这一类），或者是插件标签\n"
        "            （如 VASPsol 的 LSOL / LRHOB）。\n"
        "        本目录里没有 OUTCAR，所以**无法用真程序裁定**。",
        "三种办法都行：\n"
        "        ① 跑一次（哪怕只跑几步）再看 OUTCAR 的回显里有没有它 —— "
        "这是唯一确凿的判据；\n"
        "        ② 在 references/official/pages/ 或 wiki 上搜这个标签名；\n"
        "        ③ 若确认无误，把它补进 references/official/ 的人工清单。",
        "VASP wiki 的 Category:INCAR_tag（共 %d 条，**已知不完整**）" % kw.n)


def _check_potim(incar, path):
    """POTIM 的合法性**取决于 IBRION** —— 所以不能写成一个无上下文的规则。

    官方 POTIM 页的 Default 表写得很具体：

    | IBRION | POTIM 默认 | 含义 |
    |---|---|---|
    | 0 | 无（**必须给**） | MD 的时间步（fs） |
    | 1, 2, 3 | 0.5 | 离子弛豫的步宽缩放因子 |
    | 5, 6 | 0.015（VASP.5.1 起） | 有限差分频率的位移量（Å） |

    因此 **POTIM = 0 在 IBRION = 3（Damped MD）下是官方默认值，完全合法**。
    早期版本把 POTIM≠0 写成通用规则，把真实算例
    `day3/ts/dim`（Dimer 过渡态，IBRION=3，POTIM=0）误判成 ERROR
    —— 这是本工具构建过程中的一个假阳性，已记入 CHANGELOG 更正记录。
    """
    out = []
    v = incar.get("POTIM")
    if v is None:
        return out
    where = "%s:%s" % (path, incar.line_of("POTIM"))
    if not _is_float_text(v):
        out.append(Finding("ERROR", "INCAR.value", where,
                           "POTIM = %r 不是数值" % v,
                           "POTIM 是实数（时间步 fs 或步宽）。",
                           "改成数值，按 IBRION 选择量级。",
                           "VASP wiki: POTIM"))
        return out
    potim = float(v.split()[0])
    ibrion = incar.get_int("IBRION")
    if potim == 0.0 and ibrion not in (3,):
        out.append(Finding(
            "WARN", "INCAR.value", where,
            "POTIM = 0，而 IBRION = %s" % (ibrion if ibrion is not None else "未写"),
            "POTIM=0 只在 IBRION=3（Damped MD）下是官方默认值。"
            "在其他 IBRION 下给 0，步长缩放因子为 0 —— 离子不会动，"
            "而程序不一定报错。",
            "IBRION=1/2 时给 0.1–0.5（准牛顿对 POTIM 特别敏感）；"
            "IBRION=5/6 时给 ~0.015；做 MD（IBRION=0）时 POTIM 是 fs 且**必须给**。",
            "VASP wiki: POTIM（Default 表）"))
    elif potim < 0:
        out.append(Finding("ERROR", "INCAR.value", where,
                           "POTIM = %g 为负" % potim,
                           "POTIM 是时间步或步宽，不能为负。",
                           "改为正值。", "VASP wiki: POTIM"))
    return out

# "写了这个 tag，通常还需要另一个 tag" —— 配对约束
PAIR_RULES = [
    ("ISPIN", "2", ["MAGMOM"],
     "ISPIN=2 但没给 MAGMOM",
     "自旋极化计算没给初始磁矩时，VASP 会自己猜一个初值。**它不是错的，但不可控**："
     "同一套输入在不同版本/不同核数下可能收敛到不同的磁态。",
     "显式写出 MAGMOM（可用 `N*x` 简写），并在 OUTCAR 里核对每个离子的最终磁矩。",
     "经验判据（不是硬规则）"),
    ("LDAU", ".TRUE.", ["LDAUTYPE", "LDAUL", "LDAUU"],
     "开了 LDAU 但缺 LDAUTYPE/LDAUL/LDAUU",
     "DFT+U 需要逐元素指定 l 量子数与 U 值；缺项时 VASP 用默认，"
     "而默认值往往不是你要的。",
     "补齐 LDAUTYPE（通常 2）、LDAUL、LDAUU（LDAUJ 视实现而定），"
     "并注意**列表顺序必须与 POSCAR 的元素顺序一致**。",
     "硬规则（缺项时 VASP 用默认值，不是报错）"),
    ("LUSE_VDW", ".TRUE.", ["ZAB_VDW"],
     "开了 LUSE_VDW 但没给 ZAB_VDW",
     "用 `LUSE_VDW = .TRUE.` 启用非局域 vdW 泛函时，必须同时指定**用哪一个**："
     "`ZAB_VDW` 是 vdW-DF 系列里选核函数的开关。"
     "真实算例 `day1/vdw-df2/INCAR` 写的是 `GGA = ML` + `LUSE_VDW = .TRUE.` "
     "+ `ZAB_VDW = -1.8867` + `AGGAC = 0.0000`（即 vdW-DF2）。",
     "补上 `ZAB_VDW`（rev-vdW-DF2 一类还要 `AGGAC`/`BPARAM`）。"
     "⚠️ 本工具**不替你判断该选哪个核** —— 那是方法学选择，见 references/decide.md。",
     "经验判据 + 真实算例 day1/vdw-df2/INCAR"),
]


class Finding:
    """一条检查结果。

    `tag` 是**结构化字段**，不是从 msg 里正则抠出来的。
    早期版本靠 `_tag_of()` 从消息文本反解标签名，结果在
    `INCAR.semicolon_comment` 上稳定失败（消息里根本没有标签名），
    导致去重完全失效。**凡是能结构化的信息就不要靠文本反解** ——
    这条已记入 CHANGELOG 更正记录。
    """

    __slots__ = ("level", "check_id", "where", "msg", "why", "fix", "source",
                 "tag")

    def __init__(self, level, check_id, where, msg, why="", fix="", source="",
                 tag=""):
        self.level = level        # ERROR / WARN / INFO
        self.check_id = check_id
        self.where = where
        self.msg = msg
        self.why = why
        self.fix = fix
        self.source = source
        self.tag = tag

    def render(self) -> str:
        out = ["[%s] %s  %s" % (self.level, self.check_id, self.where),
               "      %s" % self.msg]
        if self.why:
            out.append("      为什么：%s" % self.why)
        if self.fix:
            out.append("      怎么办：%s" % self.fix)
        if self.source:
            out.append("      出处：%s" % self.source)
        return "\n".join(out)


# ---------------------------------------------------------------------------
# 各项检查
# ---------------------------------------------------------------------------
CHECK_DESCRIPTIONS = []


def _reg(cid: str, desc: str) -> None:
    CHECK_DESCRIPTIONS.append((cid, desc))


_reg("INCAR.syntax", "INCAR 行语法：无法解析成 tag = value 的行")
_reg("INCAR.duplicate", "INCAR 同一关键字重复出现")
_reg("INCAR.unknown_tag", "INCAR 关键字不在官方标签表里（可能拼错或不属于 INCAR）")
_reg("INCAR.alias", "用了旧名/别名标签（官方已改名）")
_reg("INCAR.value", "INCAR 取值域/类型检查（**只覆盖已收录的 tag**）")
_reg("INCAR.mutual_exclusion", "互斥设置同时出现")
_reg("INCAR.semicolon_comment", "行内注释里含 `;` —— VASP 会把它当语句分隔符")
_reg("INCAR.annotation_in_value", "值里混进了说明文字（抄 wiki 时丢了 `#`）")
_reg("INCAR.pair", "配对约束：写了 A 却没写 B")
_reg("INCAR.smearing", "ISMEAR/SIGMA 的组合是否适合该体系（金属 vs 绝缘体）")
_reg("KPOINTS.syntax", "KPOINTS 结构：能识别出模式、网格/坐标完整")
_reg("KPOINTS.scheme_symmetry", "k 点网格中心与 Bravais 格的对称性相容")
_reg("POSCAR.syntax", "POSCAR 结构：晶格、数目、坐标、Selective dynamics")
_reg("POSCAR.scale", "POSCAR 第二行 scale 的用法")
_reg("POTCAR.header", "POTCAR 头部可读、数据集数可数")
_reg("XSPECIES.elements", "POSCAR 元素顺序 vs POTCAR TITEL 顺序（**跨文件硬约束**）")
_reg("XPAR.both_set", "`NCORE` 与 `NPAR` 同时出现（`NPAR` 优先、`NCORE` 被静默忽略）")
_reg("XNCORE.missing_with_rank", "没写 `NCORE`/`NPAR` 且已知核数时的提醒")
_reg("XNCORE.inconsistent", "`NPAR × NCORE` vs 可用 rank 数")
_reg("XSPECIES.counts", "POTCAR 数据集数 vs POSCAR 元素种类数")
_reg("XENCUT.enmax", "ENCUT vs POTCAR 的 ENMAX（欠收敛最常见来源）")
_reg("XMAGMOM.count", "MAGMOM 展开后的个数 vs POSCAR 原子数")
_reg("XLDau.count", "LDAUL/LDAUU/LDAUJ 列表长度 vs POSCAR 元素种类数")
_reg("XDIM.kpoints", "低维体系（有真空）在真空方向的 k 点是否为 1")
_reg("XCHARGE.nelect", "NELECT 与 POTCAR 价电子总数是否自洽（带电体系）")


def collect_findings(inp: dict, kw: KeywordTable, potcar_path=None,
                     vasp_version=None, ncores=None):
    """`vasp_version` 是**用户实际的 VASP 版本**（三元组），
    用来做版本门控检查；`None` 表示不知道（此时**不猜**，只如实说明）。

    `ncores` 是**用户实际提交用的 MPI 核数**。⚠️ 它有两个来源，优先级如下：

    1. **`LOG` 横幅里的实际核数**（`running on N total cores`）——
       这是**一手事实**，最可靠；
    2. 用户用 `--ncores N` 显式给的 —— 用于**还没跑**的算例。

    ⚠️⚠️ **为什么必须区分这两者**（本项目实测出来的一个教训）：
    早期版本只看 `--ncores`，于是拿 `--ncores 16` 去校验一批
    **实际跑在 40/64 核上**的算例时，`XNCORE.inconsistent`
    在 **30 个里报了 18 个（60%）** —— 因为 `NCORE` 是按它们**各自的**
    核数设的，当然除不尽 16。
    ⇒ **那是纯噪声**（比本项目刚降级的 15% 那条还差）。
    ⇒ 现在：**若 `LOG` 里有实际核数，就用它，并忽略 `--ncores`**
      （一手事实优先于用户记忆）；只有没有 `LOG` 时才用 `--ncores`。
    """
    f = []
    incar = kpoints = poscar = None
    _natoms = None      # 给并行预检用（官方按原子数给经验锚点）
    user_version = vasp_version
    # 实际核数：LOG 一手事实优先
    _log_info = vc.parse_launch_log(inp.get("LOG") or "")
    if _log_info.get("total_cores"):
        ncores = _log_info["total_cores"]
        ncores_src = "LOG 横幅（一手事实）"
    else:
        ncores_src = "--ncores（用户提供）" if ncores else ""

    # 若算例目录里有 OUTCAR，它就是"VASP 到底认了哪些标签"的**一手证据**。
    # 用它来做归属校验的第二来源（比 wiki 分类表更强，因为它来自真程序）。
    # ⚠️ 顺带：**OUTCAR 第一行就是用户的实际版本** —— 这是最可靠的来源，
    #    比让用户口头说"我用 6.3"强得多（说错了他自己也不知道）。
    recognized = set()
    if inp.get("OUTCAR"):
        try:
            recognized = vc.outcar_recognized_tags(inp["OUTCAR"])
        except Exception as exc:                             # noqa: BLE001
            vc.warn("读 OUTCAR 失败（%s），归属校验将只用官方分类表。" % exc)
        if user_version is None:
            try:
                user_version = vc.parse_version_number(
                    vc.outcar_version(inp["OUTCAR"]))
            except Exception:                                # noqa: BLE001
                user_version = None

    # ---------------- INCAR ----------------
    if inp.get("INCAR"):
        incar = vc.read_incar(inp["INCAR"])
        for lineno, text in incar.unknown_lines:
            if "重复出现" in text:
                # 从 text（形如「重复出现：ALGO（本文件第 62 行已给过）」）里
                # 取出被重复的标签名，填进结构化字段 tag —— 去重靠它。
                dup_tag = ""
                m_dup = re.match(r"重复出现：([A-Za-z0-9_/]+)", text)
                if m_dup:
                    dup_tag = m_dup.group(1).upper()
                f.append(Finding("ERROR", "INCAR.duplicate",
                                 "%s:%d" % (inp["INCAR"], lineno), text,
                                 "同一个关键字出现两次时，**VASP 用哪个值不一定是后者**，"
                                 "取决于解析顺序；这类输入的可复现性很差。",
                                 "删掉多余的那一行。",
                                 "VASP wiki: INCAR（Format 节）",
                                 tag=dup_tag))
            elif _looks_like_section_header(text):
                # 形如 `Electronic Relaxation:` —— 这是**人们常用的分段小标题**，
                # 不是语法错误：VASP 忽略所有不符合 `tag = value` 的文字。
                # 早期版本把它报成 WARN，属于假阳性（见 CHANGELOG 更正记录）。
                f.append(Finding(
                    "INFO", "INCAR.syntax", "%s:%d" % (inp["INCAR"], lineno),
                    "分段小标题（VASP 会忽略）：%r" % text,
                    "这类文字不含 = ; \" 字符，因此不会破坏解析，"
                    "只起可读性作用 —— **它是合法的**。",
                    "无需改动。保留它能让人读懂这套输入的分段。",
                    "VASP wiki: INCAR（Format 节："
                    "VASP ignores all text that does not fit the statement format）"))
            else:
                f.append(Finding(
                    "WARN", "INCAR.syntax", "%s:%d" % (inp["INCAR"], lineno),
                    "这一行不像 `tag = value`：%r" % text,
                    "VASP 会**静默忽略**不合格式的文字（除非它含 =;\" 之类的"
                    "语法字符而破坏解析）。也就是说：你以为写了，实际没生效。",
                    "改成 `TAG = VALUE`；注释用 `#` 或 `!`。"
                    "若确实想留自由文字，确认其中不含 = ; \" 字符。",
                    "VASP wiki: INCAR（Format 节）"))

        for tag_upper, (val, lineno) in sorted(incar.tags.items(),
                                               key=lambda kv: kv[1][1]):
            where = "%s:%d" % (inp["INCAR"], lineno)
            # 归属
            if kw.loaded:
                if not kw.has("INCAR", tag_upper):
                    resolved = kw.resolve(tag_upper)
                    if resolved and kw.has("INCAR", resolved):
                        f.append(Finding(
                            "WARN", "INCAR.alias", where,
                            "%s 是旧名/别名，现行标签是 %s" % (tag_upper, resolved),
                            "旧名在新版本里可能被移除或语义改变。",
                            "改用 %s。" % resolved,
                            "references/official/_keyword_aliases.tsv"))
                    else:
                        # 是不是别的文件的关键字？
                        other = [t for t in ("KPOINTS", "POSCAR", "POTCAR")
                                 if kw.has(t, tag_upper)]
                        if other:
                            f.append(Finding(
                                "ERROR", "INCAR.unknown_tag", where,
                                "%s 不是 INCAR 关键字，它属于 %s"
                                % (tag_upper, "/".join(other)),
                                "**这正是 CP2K skill 上真实翻过车的那一类缺陷**："
                                "语法完全合法，但关键字发到了不属于它的地方；"
                                "离线看没问题，真机上直接中止。",
                                "把 %s 从 INCAR 里删掉，写到 %s 文件里。"
                                % (tag_upper, "/".join(other)),
                                "references/official/_keywords.tsv"))
                        else:
                            f.append(_unknown_tag_finding(
                                tag_upper, where, kw, recognized))
            # 取值
            chk = VALUE_CHECKS.get(tag_upper)
            if chk:
                fn, msg, src = chk
                ok = False
                try:
                    ok = bool(fn(val))
                except Exception:                            # noqa: BLE001
                    ok = False
                if not ok:
                    f.append(Finding("ERROR", "INCAR.value", where,
                                     "%s = %r 不合法：%s" % (tag_upper, val, msg),
                                     "取值非法的 tag 会导致 VASP 中止，"
                                     "或（更糟）被解释成别的意思。",
                                     "按 %s 给出的取值域改正。" % (src or "官方文档"),
                                     src, tag=tag_upper))
                # 值里混进了说明文字（**从 wiki 抄代码块时的经典错误**）
                f.extend(_check_annotation_in_value(tag_upper, val, where))

        # 行内"括号注释"里含分号（**真实算例里见过，是个真坑**）。
        # ⚠️ 收集顺序无所谓（`_demote_derived` 按**行号**匹配），
        # 但**必须在 `_demote_derived` 之前**收集完，否则派生的
        # 「关键字重复」「取值非法」会以 ERROR 身份留在报告里。
        f.extend(_check_semicolon_in_comment(inp["INCAR"]))
        # 互斥
        f.extend(_check_mutual_exclusion(incar, inp["INCAR"]))
        # POTIM（需要结合 IBRION）
        f.extend(_check_potim(incar, inp["INCAR"]))
        # 配对
        f.extend(_check_pairs(incar, inp["INCAR"]))
        # 展宽
        f.extend(_check_smearing(incar, inp["INCAR"]))
        # 一个根因不刷几条 ERROR
        _demote_derived(f)

    # ---------------- KPOINTS ----------------
    if inp.get("KPOINTS"):
        try:
            kpoints = vc.read_kpoints(inp["KPOINTS"])
        except SystemExit:
            raise
        if kpoints.mode == "unknown":
            f.append(Finding("ERROR", "KPOINTS.syntax", inp["KPOINTS"],
                             "识别不出 KPOINTS 模式（第 3 行是 %r）"
                             % kpoints.raw_mode_line,
                             "KPOINTS 的模式由**第 3 行第一个非空字符**决定，"
                             "写错一个字母就会走进完全不同的模式。",
                             "对照 references/official/pages/KPOINTS.md "
                             "选用显式/规则网格/广义网格/line/Auto 之一。",
                             "VASP wiki: KPOINTS"))
        if kpoints.mode == "regular" and kpoints.mesh:
            if any(n <= 0 for n in kpoints.mesh):
                f.append(Finding("ERROR", "KPOINTS.syntax", inp["KPOINTS"],
                                 "网格数含非正值：%r" % (kpoints.mesh,),
                                 "网格数必须是正整数。", "改正第 4 行。",
                                 "VASP wiki: KPOINTS"))
        if kpoints.mode == "line":
            if len(kpoints.line_segments) == 0:
                f.append(Finding("ERROR", "KPOINTS.syntax", inp["KPOINTS"],
                                 "line 模式但没解析到任何高对称路径段",
                                 "高对称点要**成对**给出（每两行一段）。",
                                 "检查第 5 行之后是否成对。",
                                 "VASP wiki: KPOINTS（Band-structure 节）"))

    # ---------------- POSCAR ----------------
    if inp.get("POSCAR"):
        poscar = vc.read_poscar(inp["POSCAR"])
        if poscar.extra.get("mode_line_missing") is not None:
            f.append(Finding(
                "WARN", "POSCAR.syntax", inp["POSCAR"],
                "没读到 Direct/Cartesian 行（读到的是 %r），已按 Direct 处理"
                % poscar.extra["mode_line_missing"],
                "这一行缺失时，VASP 会把它当成坐标行的第一行去解析。"
                "若你的文件确实老格式，那没问题；若是**误删**，"
                "坐标会被整体错位解释。",
                "显式补一行 `Direct` 或 `Cartesian`。",
                "VASP wiki: POSCAR"))
        if poscar.scale < 0:
            f.append(Finding(
                "INFO", "POSCAR.scale", inp["POSCAR"],
                "第二行 scale 为负（%g），表示按**目标体积**缩放" % poscar.scale,
                "负的缩放因子是 VASP 支持的写法：|scale| 被解释为目标体积。",
                "确认这就是你的本意；否则改成正的缩放因子。",
                "VASP wiki: POSCAR"))
        if poscar.symbols and not all(vc.Elements.is_known(s) for s in poscar.symbols):
            bad = [s for s in poscar.symbols if not vc.Elements.is_known(s)]
            f.append(Finding(
                "WARN", "POSCAR.syntax", inp["POSCAR"],
                "元素符号表里认不出：%s" % ", ".join(bad),
                "本工具内置的元素表只覆盖 1–96 号元素，"
                "**认不出不等于元素非法**。",
                "若符号确实合法，忽略此条；否则核对 POSCAR 第 6 行。",
                "（本工具的能力边界，非官方出处）"))

    # ---------------- 并行分解预检 ----------------
    # ⚠️ **必须放在 POSCAR 解析之后** —— 它要用原子数（官方按原子数
    #    给 `NCORE` 的经验锚点）。
    #    实测踩过：早期把调用放在 INCAR 段（那时 `poscar` 还是 None）
    #    ⇒ `_natoms` 永远是 None ⇒ "大体系"分支**永远不会触发**，
    #    而输出看起来完全正常（见 CHANGELOG 的 CR-044）。
    #    **测试还显示"工作正常"，因为小体系本来就该走 INFO 分支。**
    if incar is not None:
        if poscar is not None and getattr(poscar, "nions", None):
            _natoms = poscar.nions
        f.extend(_check_parallel(incar, inp["INCAR"],
                                 ncores=ncores, natoms=_natoms,
                                 ncores_src=ncores_src))

    # ---------------- POTCAR ----------------
    potcar = None
    p_path = potcar_path or inp.get("POTCAR")
    if p_path and os.path.exists(p_path):
        potcar = vc.parse_potcar_header(p_path)
        if potcar.n_datasets == 0:
            f.append(Finding("ERROR", "POTCAR.header", p_path,
                             "没有找到任何 'End of Dataset' 标记",
                             "POTCAR 由多个数据集拼接，每个以 'End of Dataset' 结束。"
                             "没有标记说明这个文件不是完整的 POTCAR（拼接被截断？）。",
                             "重新拼接 POTCAR，顺序必须与 POSCAR 的元素顺序一致。",
                             "VASP wiki: POTCAR"))
        elif not potcar.titles:
            f.append(Finding("WARN", "POTCAR.header", p_path,
                             "数到 %d 个数据集，但读不到 TITEL 行"
                             % potcar.n_datasets,
                             "很老的赝势集可能没有完整头部信息。",
                             "若你用的是 potpaw.54 之后的集合，建议重新下载。",
                             "VASP wiki: POTCAR"))
    elif potcar_path:
        f.append(Finding("ERROR", "POTCAR.header", str(potcar_path),
                         "指定的 POTCAR 不存在",
                         "POTCAR 是必需输入文件。",
                         "用 --potcar 指向真实的 POTCAR。", ""))
    elif inp.get("dir"):
        f.append(Finding(
            "WARN", "POTCAR.header", inp.get("dir", ""),
            "本目录里没有 POTCAR —— 与 POTCAR 相关的 %d 项检查**本次未执行**"
            % _n_potcar_checks(),
            "POTCAR 受 VASP 许可保护，**本 skill 不会、也不能替你生成或分发它**。"
            "所以当你不提供它时，这些跨文件硬约束就无法核对。",
            "用 `--potcar <你本地的 POTCAR 路径>` 再跑一次；"
            "或先用 `--only-report` 明确看到底缺了哪些检查。",
            "references/MAINTENANCE.md（许可约束）"))

    # ---------------- 跨文件 ----------------
    f.extend(_check_cross(inp, incar, kpoints, poscar, potcar))

    # ---------------- 版本 ----------------
    f.extend(_check_versions(inp, incar, user_version))
    return f


# 版本门控：对照用户的实际 VASP 版本，看 INCAR 里的标签他能不能用。
#
# **为什么必须做这一条**（本项目实测的全局风险）：
#   · 官方 wiki 语料是 **VASP 6.6 时代**的（91 处版本门槛里 61×6.5.0 / 25×6.6.0）；
#   · 而 `things to study/` 的 98 个真实算例**全部是 vasp.5.4.4**。
#   ⇒ 一个用 5.4.4 的人照抄一个 6.5.0 才有的标签，程序**静默忽略**它
#     （或报一个看不懂的错）—— 正是本项目最想消灭的那类问题。
#
# ⚠️ **这条检查的诚实边界**：
#   1. 官方**只对"新加的"标版本**。绝大多数标签**没有标注** ⇒
#      "不在表里"只能读作「**官方未标注版本门槛**」，
#      **绝不能**读成「所有版本都支持」。所以这一条**只报"确定不支持"的**，
#      对无标注的一律**不说话**（不制造噪声）。
#   2. 没有用户版本时不猜 —— 只把"该标签官方有门槛，但你的版本未知"如实说明。
def _check_versions(inp, incar, user_version):
    out = []
    if incar is None:
        return out

    tbl = vc.loaded_version_gates_path()
    if not tbl:
        # 版本表缺失 ⇒ **降级为"未检查"**，不假装查过。
        out.append(Finding(
            "INFO", "VER.gates_missing", inp.get("dir", ""),
            "找不到版本门控表 `references/official/_versions.tsv` ⇒ "
            "**版本相关的检查本次未执行**。",
            "该表由 `references/official/_extract_versions.py` 从官方层逐行提取。",
            "在仓库根目录跑一次："
            "`python references/official/_extract_versions.py`",
            "references/VERSIONS.md"))
        return out

    if user_version is None:
        # 没拿到版本：只在"有标签确实带门槛"时提示一句，不逐个刷屏。
        gated = [t for t in sorted(incar.tags)
                 if vc.version_gate_status(t, None)[0] == "unknown"
                 and vc.load_version_gates().get(t.upper(), {}).get("available")]
        if gated:
            out.append(Finding(
                "INFO", "VER.user_version_unknown", inp.get("dir", ""),
                "没有拿到你的 VASP 版本 ⇒ **无法判断**这些标签在你的版本上"
                "是否存在：%s（官方都给它们标了版本门槛）"
                % ", ".join(gated[:6]),
                "官方对新增标签会标 `Available | <版本>`。"
                "用老版本时，程序对不认识的标签**常常只是静默忽略**，"
                "于是你以为设了、其实没生效。",
                "跑完一次后看 `OUTCAR` 第一行（形如 `vasp.5.4.4.…`），"
                "或用 `--vasp-version 5.4.4` 显式告知。",
                "references/VERSIONS.md"))
        return out

    uv = ".".join(map(str, user_version))
    too_old = []
    for tag in sorted(incar.tags):
        status, detail = vc.version_gate_status(tag, user_version)
        if status == "too_old":
            too_old.append((tag, detail))
    if too_old:
        for tag, detail in too_old:
            out.append(Finding(
                "WARN", "VER.too_old", str(inp.get("INCAR")),
                "`%s`：%s（你用的是 `%s`）" % (tag, detail, uv),
                "官方只对新增标签标版本门槛。**这条是官方明文标了的**，"
                "所以不是我们的推测。"
                "⚠️ 但要注意**两种情况含义不同**："
                "① 若该标签是 VASP **原生**新增的（如 6.5.0 的 ELPH 系列），"
                "你的版本上它就**真的不存在**；"
                "② 若它**也能由补丁版提供** —— 典型例子：`IMAGES` / `ICHAIN` / "
                "`LCLIMB` / `IOPT` / `SPRING`，官方原生 `IMAGES` 自 6.2.0 才有，"
                "但 **VTST 补丁版的 5.4.4 一直能用** —— 那你可能装了补丁。"
                "⇒ **本检查不知道你装没装补丁**，它报的是"
                "「**官方原生**从哪个版本起有」，"
                "**不等于**「在你的环境里一定不可用」。",
                "① 先确认你的 VASP 是不是补丁版（VTST 等）——"
                "看 `OUTCAR` 里有没有 `VTST` 相关字样，或问集群管理员；"
                "② 查 `references/official/pages/%s.md` 的 `{{Available}}` 标注；"
                "③ 若确实需要这个功能又没有补丁，升级 VASP；"
                "④ 若不需要，删掉这一行，别让它给你虚假的安心。"
                % tag,
                "references/VERSIONS.md（版本门控）；"
                "官方页面的 `{{Available|…}}` 标注"))
    return out


def _n_potcar_checks() -> int:
    return 5


def _check_parallel(incar, path, ncores=None, natoms=None,
                    ncores_src=""):
    """并行分解预检（`XPAR.*` / `XNCORE.*`）—— **提交作业之前**该看的东西。

    为什么要有这一组（本项目的一次真实事故）
    ----------------------------------------
    用户 179 原子团簇、16 MPI rank、**没写 `NPAR`/`NCORE`**（走默认 `NCORE=1`）
    ⇒ 每个 rank 独占一个 band、独自完成整块 FFT ⇒ **第一次 SCF 就 `SIGSEGV`**，
    `OSZICAR` 只有表头。只加一行 `NPAR = 2` 就好了。
    **`validate.py` 当时一项都没查并行标签** —— 它报 `OK`。

    ⚠️⚠️ **这一组检查能做什么、不能做什么（必须看清楚）**
    ---------------------------------------------------
    **能**：抓"标签之间的**关系**错了" —— 这类错误**程序不报错**，而且
    人很容易踩（`NPAR` 与 `NCORE` 同时写时 **`NPAR` 优先**，另一个被静默忽略）。

    **不能**：
    1. **不能判断某个取值会不会导致栈溢出/内存不足** —— 那取决于
       每个 rank 的内存上限、FFT 网格、赝势、编译器，**本工具看不到**；
    2. **不能替你选 `NCORE`** —— 官方给的是"跑一个简短的 `NCORE` 扫描"，
       不是一个固定值（见 `references/decide.md`）；
    3. 没有 `--ncores` 时**不知道你有多少核** ⇒ 相关检查**降级为"未检查"**
       （绝不猜）。

    ⇒ 所以它是**预检**，不是**保证**。这一条与本项目其它工具的口径一致。
    """
    out = []
    got_ncore = incar.get("NCORE")
    got_npar = incar.get("NPAR")
    got_kpar = incar.get("KPAR")

    # ---- ①② 同时设 NPAR 与 NCORE --------------------------------
    # 官方明文（`[官方]` pages/NCORE.md:15）：
    #   `Do not set NCORE and NPAR at the same time.`
    #   若两个都出现 ⇒ `NPAR` 优先，`NCORE` 被**静默忽略**。
    # 本项目作者自己就踩过：修完 bug 写了 `NPAR = 2`，又补了句"建议显式写
    # `NCORE = 8`" ⇒ 两者并存。**这个坑极易踩，必须机器化拦截。**
    if got_ncore is not None and got_npar is not None:
        out.append(Finding(
            "WARN", "XPAR.both_set", str(path),
            "`NCORE` 与 `NPAR` **同时出现**（`NCORE = %s`、`NPAR = %s`）"
            % (got_ncore.split()[0], got_npar.split()[0]),
            "官方明文：`Do not set NCORE and NPAR at the same time.`"
            "两者**严格互逆**（`NPAR × NCORE = 可用 rank 数`），"
            "同时出现时 **`NPAR` 优先**、`NCORE` 被**静默忽略**。"
            "⚠️ **这不是报错** —— 你以为设了 `NCORE`，实际走的是 `NPAR`，"
            "而输出里不会提示你。",
            "**只留一个。** 推荐一律用 `NCORE`（`NPAR` 是 legacy 标签，"
            "官方建议改用 `NCORE`）。删掉 `NPAR` 那一行。",
            "`grep -E \"distr:\" LOG` 里的 `one band on N cores` 等于你要的 "
            "`NCORE`。",
            "[官方] references/official/pages/NCORE.md / NPAR.md"))

    # ---- ③ 都没写 + 知道核数 ⇒ 提醒默认值是危险的 ---------------
    # 官方给的经验起点（`[官方]` pages/NCORE.md）：
    #   `NCORE = 4` 对 ~100 原子不错；`12–16` 对 >400 原子的胞常更好。
    # ⇒ 阈值用"原子数"，因为那是官方唯一给过的规模锚点。
    if got_ncore is None and got_npar is None:
        if ncores is None:
            out.append(Finding(
                "INFO", "XNCORE.missing_with_rank", str(path),
                "**没有** `NCORE`/`NPAR`，且**没告诉我有多少核** ⇒ "
                "「该不该设 `NCORE`」这一项**本次未检查**。",
                "不写就是官方默认 `NCORE = 1`（`NPAR` = 可用 rank 数）。"
                "该默认值**只适用于小胞或通信受限的机器**；"
                "大体系 + 多 rank 下每个 rank 独占一个 band、独自完成整块 FFT，"
                "**内存/栈会爆**（官方原句 `leading to high memory usage`）。",
                "跑一次 `validate.py <目录> --ncores <你实际用的核数>`，"
                "或直接照 `NCORE ≈ √(核数)` 起手。",
                "给出 `--ncores` 后本项会被实际检查。",
                "[官方] references/official/pages/NCORE.md"))
        elif ncores >= 8:
            big = (natoms is not None and natoms >= 100)
            out.append(Finding(
                "WARN" if big else "INFO",
                "XNCORE.missing_with_rank", str(path),
                "**没有** `NCORE`/`NPAR` ⇒ 走默认 `NCORE = 1`"
                "（`NPAR` = 可用 rank 数 = %d%s；核数来源：%s）"
                % (ncores, ("（`KPAR = %s`）" % got_kpar.split()[0])
                   if got_kpar else "", ncores_src or "（未提供）"),
                "官方默认 `NCORE = 1` 的适用条件是"
                "「**小胞，或通信带宽受限的机器**」；"
                "官方同页警示它会让"
                "「**投影函数完整存在每个 rank 上 ⇒ 高内存占用**」。"
                + ("你这个体系**有 %d 个原子**，而官方给的经验锚点是"
                   "「`NCORE=4` 对 ~100 原子不错；`12–16` 对 >400 原子的胞常更好」"
                   "⇒ **你属于该设 `NCORE` 的那一档**。" % natoms if big else
                   "你这个体系不算大，风险较低 —— 但**多 rank 下仍可能偏慢**。"),
                "在 `INCAR` 里加 `NCORE ≈ √(%d) ≈ %d`（先试这个，"
                "不行再按官方说的**跑一个简短的 `NCORE` 扫描**）。"
                "⚠️ **用 `NCORE`，不要用 `NPAR`。**"
                % (ncores, max(2, int(round(ncores ** 0.5)))),
                "重跑后看 `grep -E \"distr:\" LOG` 的 `one band on N cores` "
                "是否等于你设的 `NCORE`。",
                "[官方] references/official/pages/NCORE.md"
                "（默认值的内存后果 + 按原子数的经验锚点）；"
                "[实测] 单变量对照（同二进制/同 INCAR/同栈上限，"
                "只改并行分解：默认⇒0 步 SCF 崩溃；`NPAR=2`⇒7 步 SCF 收敛）"))

    # ---- ④ 三者都给 ⇒ 核对 NPAR × NCORE = 可用 rank -------------
    if ncores is not None and got_ncore is not None and got_npar is not None:
        try:
            nc = int(float(got_ncore.split()[0]))
            npar = int(float(got_npar.split()[0]))
            kpar = int(float(got_kpar.split()[0])) if got_kpar else 1
        except (ValueError, IndexError):
            nc = npar = kpar = None
        if nc and npar and kpar:
            avail = ncores // kpar
            if npar * nc != avail:
                out.append(Finding(
                    "INFO", "XNCORE.inconsistent", str(path),
                    "`NPAR × NCORE` = %d，而可用 rank 数 = %d（= %d 核 / "
                    "`KPAR` %d）—— **对不上**" % (npar * nc, avail, ncores, kpar),
                    "官方关系式：`NPAR = available ranks / NCORE`，"
                    "即 `NPAR × NCORE = available ranks`（二者**严格互逆**）。"
                    "⚠️ 对不上时程序会**自己取一个**，不报错 —— "
                    "而取到的可能不是你要的。"
                    "（`[实测]` 见过一个算例：40 核 / `NCORE=16`，"
                    "而 `40/16` 不是整数，程序实际用了 5。）",
                    "让 `NPAR × NCORE` 等于 `总核数 / KPAR`；"
                    "或者只写 `NCORE`、让程序自己算 `NPAR`。",
                    "`grep -E \"distr:\" LOG` 的值与你的设置一致。",
                    "[官方] references/official/pages/NCORE.md"
                    "（`NPAR × NCORE = available ranks`）"))

    # ---- ⑤ 只写了一个 ⇒ 核对能否整除 -----------------------------
    #
    # ⚠️ 这一格是**补上来的**：④ 只在"两者都写"时才核对，
    #    于是 `NCORE = 5` 配 16 核（`16 % 5 ≠ 0`）**一声不吭** ——
    #    而 `diagnose.py`（`LAUNCH.par_tags_inconsistent`）给用户的建议
    #    恰恰是"让可用 rank 数能被 `NCORE` 整除"。
    #    **两处口径不一致 ⇒ 把一个已知陷阱漏检了**（见 CHANGELOG 的 CR-044）。
    if ncores is not None:
        kpar = 1
        if got_kpar is not None:
            try:
                kpar = int(float(got_kpar.split()[0])) or 1
            except (ValueError, IndexError):
                kpar = 1
        avail = (ncores // kpar) if kpar else ncores
        for tag, val_s in (("NCORE", got_ncore), ("NPAR", got_npar)):
            if val_s is None:
                continue
            try:
                v = int(float(val_s.split()[0]))
            except (ValueError, IndexError):
                continue
            if v <= 0 or avail <= 0 or avail % v == 0:
                continue
            out.append(Finding(
                # ⚠️ **级别是 "INFO" 不是 "WARN"，这是实测定的**（见 CR-044）：
                #    用**真实核数**跑 98 个算例，这条命中 **46 个（47%）**。
                #    它们**不是假阳性** —— `INCAR` 里写的 `NCORE` 确实与
                #    实际生效的不同（VASP 自己调整了，`40/16` 不是整数）。
                #    但**它不影响正确性**：VASP 照样算、照样收敛，
                #    只是每 band 的核数不是你要的那个。
                #    ⇒ **47% 的 WARNING 会把人训练成忽略整个报告**；
                #      47% 的 "INFO 仅供参考" 才是诚实的。
                #    **问题在级别，不在发现本身。**
                "INFO", "XNCORE.inconsistent", str(path),
                "`%s = %d`，而可用 rank 数 = %d（= %d 核 / `KPAR` %d）"
                "—— **%d 不能被 %d 整除**"
                % (tag, v, avail, ncores, kpar, avail, v),
                "官方关系式：`NPAR = available ranks / NCORE`（二者**严格互逆**）。"
                "**不能整除时程序会自己取一个值**，而**不报错** —— "
                "于是你设的与生效的可能不是一个数。"
                "`[实测]` 见过一个算例：40 核 / `NCORE=16`，"
                "`40/16 = 2.5` 不是整数，程序实际用了 **5**。"
                "⚠️ **官方没有记载「不能整除时怎么处理」** ⇒ "
                "本条只报「不一致」这个可核对的事实，**不解释机制**。",
                "把 `%s` 改成一个**能整除可用 rank 数**（= %d）的值；"
                "⚠️ 官方还建议**取每节点核数的因子**，"
                "所以别只看整除，也要看节点结构。"
                % (tag, avail),
                "重跑后看 `grep -E \"distr:\" LOG` 的 `one band on N cores` "
                "是否等于你设的值。",
                "[官方] references/official/pages/NCORE.md"
                "（`NPAR = available ranks / NCORE`；"
                "「不能整除怎么处理」官方未记载 ⇒ 只报不一致，不解释机制）"))
            break        # 一个算例报一次就够，不要 NCORE、NPAR 各刷一条

    return out


def _looks_like_section_header(text: str) -> bool:
    """判断一行「不是 tag = value」的文字是不是**无害的自由文字**。

    官方 INCAR 格式页明确说：VASP 会忽略所有不符合 `tag = value` 形式的文字，
    **只要其中不含语法字符 `= ; "`**（含了就可能破坏解析）。
    因此下面这些**都是合法的**，不该报成问题：

        Global Parameters          ← 人写的分段小标题
        Electronic Relaxation:
        -------- DFT+U --------

    判据：不含 `= ; "` 三个语法字符。
    早期版本要求必须以 `:` 结尾，结果把 `Global Parameters` 这种
    不带冒号的标题误报成 WARN（构建过程中真实踩到的假阳性，
    见 CHANGELOG 更正记录）。
    """
    s = text.strip().lstrip("#!").strip()
    if not s:
        return False
    return not any(ch in s for ch in '=;"')


def _check_mutual_exclusion(incar, path):
    out = []
    pairs = [
        ("LDAU", ".TRUE.", "LDAU", ".FALSE.",
         "LDAU 同时出现 .TRUE. 与 .FALSE."),
        ("LWAVE", ".TRUE.", "LWAVE", ".FALSE.", "LWAVE 同时出现 .TRUE. 与 .FALSE."),
    ]
    # 真正的互斥：某些组合在物理上不能共存
    combos = [
        (("IBRION", "0"), ("NSW", None),
         "IBRION=0（分子动力学）与只做单点的意图冲突",
         "IBRION=0 表示做 MD，需要 NSW>0 才有意义。",
         "做单点请用 IBRION=-1（或干脆不写 IBRION 并设 NSW=0）。",
         "VASP wiki: IBRION"),
        (("IBRION", "5"), ("ISIF", "3"),
         "IBRION=5（有限差分频率）与 ISIF=3（改变晶胞）同时出现",
         "频率计算要求**固定**几何；ISIF=3 会让晶胞也在动，"
         "得到的 Hessian 不再是你要的那个。",
         "频率计算用 ISIF=2（或 0）冻结晶胞。",
         "经验判据（VASP wiki: IBRION 的 Warning 与 phonon 页面）"),
        (("ICHARG", "11"), ("NELM", None),
         "ICHARG=11（固定电荷密度做非自洽）却没设 NELM=1",
         "非自洽计算不需要迭代 SCF；留着默认 NELM 会白跑若干步"
         "（结果仍对，但浪费机时，且容易让人误以为做了自洽）。",
         "配 NELM=1。",
         "VASP wiki: ICHARG"),
    ]
    for (t1, v1), (t2, _v2), msg, why, fix, src in combos:
        got = incar.get(t1)
        if got is None:
            continue
        val = got.split()[0]
        if t1 == "IBRION" and val not in ("0", "5"):
            continue
        if t1 == "ICHARG" and val != "11":
            continue
        if t2 is not None and incar.get(t2) is None:
            continue
        if t2 == "ISIF" and incar.get_int("ISIF") != 3:
            continue
        if t2 == "NSW":
            # 只在 NELM 缺失或明显偏大时提示
            if incar.get_int("NELM") is not None and incar.get_int("NELM") <= 2:
                continue
        out.append(Finding("WARN", "INCAR.mutual_exclusion",
                           "%s:%s" % (path, incar.line_of(t1)), msg, why, fix, src))
    return out


def _check_semicolon_in_comment(path):
    """行内"括号注释"里带 `;` —— 一个**真实算例里踩到的坑**。

    **背景（可复现）**：真实算例 `线上中级班-催化资料/1-fundamental/hse/INCAR`
    第 62 行写的是

        ALGO   =  ALL         (Electronic Minimisation Algorithm; ALGO=58)

    作者的意图显然是"用 ALL，并在括号里注解 ALGO=58 这个编号"。
    但按官方 INCAR 格式页：

    * **注释只能用 `#` 或 `!`**；圆括号**不是**注释，是普通文字；
    * `;` 是**语句分隔符**，用来在一行里写多条 `tag = value`。

    于是这一行在 VASP 眼里是两条语句：`ALGO = ALL` 与 `58)`。
    后者会被当成某条语句去解析（很可能被解释成 `ALGO` 的第二次赋值，
    因为分号只切语句、不切关键字上下文 —— **这一步需要真程序裁定**）。

    **证据等级（很重要，不要把它当实测）**
    - "注释符是 #/!、; 是分隔符"：**官方明文**（INCAR 格式页）。
    - "这一行几乎肯定不是作者本意"：**推论**，但推断很硬（作者在别处
      一直用 `#` 写注释，唯独这里用了圆括号）。
    - "VASP 具体会怎么处理 `58)`"：**本工具没有验证**。
      该目录里只有 INCAR/INCAR.bak，**没有 OUTCAR**，所以无法实测。
      要坐实它，请把这份输入喂给真程序（见 conformance/README.md）。

    因此这里报 ERROR 的**理由**是"这一行几乎肯定不是作者的本意"，
    **不是**"VASP 一定会崩"。
    """
    out = []
    if not os.path.exists(path):
        return out
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            raw_lines = fh.read().replace("\r\n", "\n").split("\n")
    except OSError:
        return out
    for idx, raw in enumerate(raw_lines, start=1):
        # `#` / `!` 之后的文字被 VASP 忽略，所以只需要看它**之前**的部分。
        # 没有 `#`/`!` 时 head 就是整行 —— 早期版本写成 `if sep:` 才继续，
        # 于是**只有带 # 注释的行**才会被检查，真实案例（那行没有 #）被漏掉。
        # 这是构建过程中真实踩到的逻辑错误，已记入 CHANGELOG 更正记录。
        head, sep, comment = _split_at_line_comment(raw)

        # ① `;` 是**语句分隔符** —— 在 head 里切，看是否切出了"说明文字"。
        stmts = [p.strip() for p in head.split(";")]
        if len(stmts) >= 2 and "=" in stmts[0]:
            rest = [s for s in stmts[1:] if s]
            if _prose_split_in_comment(stmts[0], rest):
                out.append(_semicolon_finding(
                    path, idx, stmts, stmts[0].split("=", 1)[0].strip()))
        # ② `#`/`!` 落在**等号之后**且值为空 —— 作者以为后面是注释，
        #    按官方定义它确实被忽略，所以这一行的值成了空（= 静默失效）。
        if sep and "=" in head:
            val = head.split("=", 1)[1].strip()
            if not val and comment.strip():
                out.append(Finding(
                    "WARN", "INCAR.semicolon_comment", "%s:%d" % (path, idx),
                    "等号后面直接是 `%s` 注释，值本身是空的：%r"
                    % (sep, raw.strip()),
                    "`%s` 之后确实会被 VASP 忽略，所以这一行的**值成了空**。"
                    "空值对多数 tag 等于用默认值 —— 静默失效。" % sep,
                    "把值补上，或删掉这一行。",
                    "VASP wiki: INCAR（Format 节）"))
    return out


def _prose_split_in_comment(first_stmt: str, rest: "list[str]") -> bool:
    """半段文字到底是「作者有意写的多条语句」，还是「括号里的说明被切了」？

    两者在字面上都可能长成 `XXX = YYY`，所以光看形状分不开。
    下面两条判据**都要能独立站住**，命中任一即判为"说明被切"：

    判据 A —— **第一段的值里出现了圆括号**。
        作者写 `ALGO = ALL   (...)` 时，`ALL` 与 `(` 之间是空白，
        所以第一段的值会带着 `(Electronic Minimisation Algorithm` 这样的内容。
        而真正有意写多条语句的人写的是 `ISMEAR = -1; SIGMA = 0.05`，
        值里不会突然多出一个括号。

    判据 B —— **后半段的值不是合法字面量**。
        `58)` 不是整数（带尾括号），这不是任何人会主动写的值。

    为什么必须两条都留：只留 A，会漏掉"括号写在值后面偏远处"的写法；
    只留 B，会漏掉"...; ALGO = ALL)"里值是 `ALL)` 这种（同样非法，
    但如果后半段被切成 `XXX = ALL` 就没括号了）。
    反过来，两条都不会把 `A = 1; B = 2` 这类**正常的多语句行**误判。
    """
    if not rest:
        return False
    # 判据 A
    left_val = first_stmt.split("=", 1)[1] if "=" in first_stmt else ""
    if "(" in left_val or ")" in left_val:
        return True
    # 判据 B
    for s in rest:
        if "=" not in s:
            return True
        val = s.split("=", 1)[1].strip().rstrip(",;")
        if val == "":
            continue
        if _is_int_text(val) or _is_float_text(val) or _is_bool_text(val):
            continue
        # 允许纯字母的枚举值（如 `Auto` `Normal`）
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_\-]*\.?", val):
            continue
        return True
    return False


def _semicolon_finding(path, idx, stmts, tag0):
    return Finding(
        "ERROR", "INCAR.semicolon_comment", "%s:%d" % (path, idx),
        "行内用圆括号写了说明，而说明里含分号 `;`；"
        "VASP 会把这一行切成多条语句：%s"
        % " | ".join(repr(s) for s in stmts),
        "官方 INCAR 格式页：注释只能用 `#` 或 `!`，**圆括号不是注释**；"
        "而 `;` 是语句分隔符。也就是说：写在括号里的说明文字"
        "会被当成真的输入去解析 —— 你以为只是写给自己看的注解，"
        "程序却拿去执行了。",
        "把括号里的说明改成 `#` 或 `!` 开头的注释，或删掉其中的分号。例如：\n"
        "        %s   # (……说明文字……)" % stmts[0],
        "VASP wiki: INCAR（Format 节）；真实算例 "
        "线上中级班-催化资料/1-fundamental/hse/INCAR:%d" % idx,
        tag=tag0)


# 「哪个检查是根因」的优先级：数字越小越根本。
# 一个 (行, 标签) 上只保留优先级最高的那条为 ERROR，其余降为 INFO。
ROOT_CAUSE_PRIORITY = {
    "INCAR.semicolon_comment": 0,      # 行被误切，其它都是它的后果
    "INCAR.annotation_in_value": 1,    # 值里混进说明文字
    "INCAR.duplicate": 2,
    "INCAR.value": 3,
    "INCAR.syntax": 4,
}


def _demote_derived(findings) -> None:
    """**就地**处理「一个根因、多条症状」的重复报告。

    真实案例一（`1-fundamental/hse/INCAR:62`）：

        ALGO   =  ALL         (Electronic Minimisation Algorithm; ALGO=58)

    根因只有一个 —— 括号说明里的分号。它在下游同时伪装成三条：
    `INCAR.duplicate`（切出了第二条 `ALGO = ...`）、
    `INCAR.value`（`ALGO = '58)'`）、
    `INCAR.annotation_in_value`（值里有圆括号）。
    四条说的是同一件事，只留根因那条为 ERROR。

    真实案例二（`partialCharge/INCAR` 第 1 行）：

        ISTART =      1    job   : 0-new  1-cont  2-samecut

    根因是「值里混进说明文字」；`INCAR.value`（值不是 0/1/2/3）是它的后果。

    **去重键 = (行号, 标签名)，两者都要相同。**
    只用行号会误伤：同一文件里不同标签各有真问题时会被一起降级 ——
    那是「为了让灯变绿而放宽判据」，本项目明令禁止。
    """
    groups: "dict[tuple, list]" = {}
    for x in findings:
        if x.check_id not in ROOT_CAUSE_PRIORITY:
            continue
        if x.level != "ERROR":
            continue
        groups.setdefault((x.where, x.tag), []).append(x)
    for _key, items in groups.items():
        if len(items) < 2:
            continue
        items.sort(key=lambda y: ROOT_CAUSE_PRIORITY[y.check_id])
        for y in items[1:]:
            y.level = "INFO"
            y.msg = ("（派生症状：与同一行的「%s」是同一个根因）"
                     % items[0].check_id + y.msg)
            y.why = ""
            y.fix = "先修同一行那条根因检查，这条会跟着消失。"
            y.source = ""


def _tag_of(f: "Finding") -> str:
    """取 Finding 涉及的关键字名。

    **优先用结构化字段 `f.tag`**；只有老代码路径没填 tag 时才退回文本反解
    （反解不可靠，只作兼容用，见 `Finding` 的注释）。
    """
    if f.tag:
        return f.tag
    msg = f.msg or ""
    m = re.match(r"\s*([A-Z][A-Z0-9_/]{1,60})\s*=", msg)
    if m:
        return m.group(1)
    m = re.match(r"\s*([A-Z][A-Z0-9_/]{1,60})\s*(?:的值里|不在|里出现)", msg)
    if m:
        return m.group(1)
    m = re.match(r"\s*开了\s*([A-Z][A-Z0-9_/]{1,60})", msg)
    if m:
        return m.group(1)
    return ""


def _check_annotation_in_value(tag: str, val: str, where: str):
    """值里混进了说明文字 —— 抄 wiki 代码块时的经典错误。

    **真实算例**（`3-electronicStructure/ex4-co-wavefunction-partialcharge/
    partialCharge/INCAR` 第 1–2 行）逐字是：

        ISTART =      1    job   : 0-new  1-cont  2-samecut
        ICHARG =      1   charge: 1-file 2-atom 10-const

    这两行**是从 VASP wiki 的 INCAR 示例页抄下来的**（wiki 上原文就是
    `ISTART = 0 # job : 0-new 1-orbitals from WAVECAR` 这类带注解的写法），
    抄的时候把 `#` 丢掉了。

    后果：值变成了 `1    job   : 0-new  1-cont  2-samecut`。
    如果 VASP 用列表读取（free-format read）而不是报错，它会读到很多个数 ——
    `ISTART` 只取第一个数所以恰好还是 1，**看起来一切正常**；
    但换一个 tag（比如 `MAGMOM`、`LDAUU`）就是灾难。
    这类"碰巧还能跑"的输入最危险：它给人一种"抄 wiki 没问题"的错觉。

    判据：值里出现了 **`:` 或 `(`**，或者**空格分隔的 token 超过 3 个且含非数字**。
    （取值范围本来就长的 tag 如 MAGMOM/LDAUU 不适用第二条 —— 用第一条就够，
    因为正常取值里不会出现冒号或括号。）
    """
    out = []
    if not val:
        return out
    v = val.strip()
    hit = None
    if ":" in v:
        hit = "值里含冒号 `:`"
    elif "(" in v or ")" in v:
        hit = "值里含圆括号"
    elif len(v.split()) > 3 and not _all_numeric_or_repeat(v):
        hit = "值里有多个非数值 token（像是说明文字）"
    if hit:
        out.append(Finding(
            "ERROR", "INCAR.annotation_in_value", where,
            "%s 的值里混进了说明文字（%s）：%r" % (tag, hit, v),
            "最常见的原因是**从 VASP wiki 或教程里抄代码块时丢掉了 `#`**。"
            "wiki 上的示例常写成 `ISTART = 0 # job : 0-new 1-cont 2-samecut`，"
            "如果把 `#` 删掉，冒号后面的说明就变成了「值」的一部分。"
            "**能不能碰巧还跑得起来取决于 tag**：只取第一个数的 tag"
            "（如 ISTART）看起来毫无异常，而列表型 tag 会直接错。"
            "也就是说这类错误**没有症状**，直到它恰好落在一个列表型 tag 上。",
            "把说明文字移到 `#` 或 `!` 后面；值只留真正的数值/关键字。\n"
            "        改前：%s = %s\n"
            "        改后：%s = %s   # %s"
            % (tag, v, tag, _first_value_token(v), _annotation_part(v)),
            "VASP wiki: INCAR（Format 节：注释用 # 或 !）", tag=tag))
    return out


def _all_numeric_or_repeat(v: str) -> bool:
    for t in v.split():
        if re.fullmatch(r"\d+\*[-\d.eE+]+", t):
            continue
        try:
            float(t)
        except ValueError:
            return False
    return True


def _first_value_token(v: str):
    m = re.match(r"\s*([-\d.]+|\d+\*[-\d.eE+]+|[A-Za-z]+\.?)", v)
    return m.group(1) if m else "?"


def _annotation_part(v: str) -> str:
    m = re.search(r"[:(].*$", v)
    return m.group(0).strip() if m else "(说明文字)"


def _tag_like(s: str) -> bool:
    """粗判一段文字像不像 INCAR 关键字名（全大写字母/数字/下划线/斜杠）。"""
    s = s.strip()
    if not s or len(s) > 40:
        return False
    return all(ch.isalnum() or ch in "_/" for ch in s)


def _split_at_line_comment(raw: str):
    """在**第一个** `#` 或 `!` 处切开（引号内的不算）。

    官方定义：`#` 与 `!` 之后的所有文字被 VASP 忽略。
    返回 (前半, 分隔符, 后半)；没有注释符时返回 (raw, "", "")。
    """
    in_quote = False
    for idx, ch in enumerate(raw):
        if ch == '"':
            in_quote = not in_quote
        if not in_quote and ch in "#!":
            return raw[:idx], ch, raw[idx + 1:]
    return raw, "", ""


def _strip_comment_local(raw: str):
    head, _sep, tail = _split_at_line_comment(raw)
    return head, tail



    out = []
    for t1, want, need, msg, why, fix, src in PAIR_RULES:
        got = incar.get(t1)
        if got is None:
            continue
        s = got.strip().upper().rstrip(".")
        hit = (s == want.upper().rstrip(".")) if want else True
        if not hit:
            continue
        missing = [n for n in need if incar.get(n) is None]
        if missing:
            out.append(Finding("WARN", "INCAR.pair",
                               "%s:%s" % (path, incar.line_of(t1)),
                               "%s（缺 %s）" % (msg, ", ".join(missing)),
                               why, fix, src))
    return out


def _check_pairs(incar, path):
    """配对约束：写了 A 却通常还需要 B。"""
    out = []
    for t1, want, need, msg, why, fix, src in PAIR_RULES:
        got = incar.get(t1)
        if got is None:
            continue
        s = _strip_dots(got)
        hit = (s == _strip_dots(want)) if want else True
        if not hit:
            continue
        missing = [n for n in need if incar.get(n) is None]
        if missing:
            out.append(Finding("WARN", "INCAR.pair",
                               "%s:%s" % (path, incar.line_of(t1)),
                               "%s（缺 %s）" % (msg, ", ".join(missing)),
                               why, fix, src))
    return out


def _check_smearing(incar, path):
    out = []
    ismear = incar.get_int("ISMEAR")
    sigma = incar.get_float("SIGMA")
    if ismear is None:
        return out
    where = "%s:%s" % (path, incar.line_of("ISMEAR"))
    if ismear > 0 and sigma is None:
        out.append(Finding(
            "WARN", "INCAR.smearing", where,
            "ISMEAR=%d 用了 Methfessel-Paxton 展宽，但没给 SIGMA" % ismear,
            "MP 展宽必须配一个宽度；缺省值不一定是你要的。",
            "显式给出 SIGMA（金属常用 0.1–0.2 eV 量级）。",
            "VASP wiki: SIGMA"))
    if ismear == 0 and sigma is not None and sigma > 0.5:
        out.append(Finding(
            "WARN", "INCAR.smearing", "%s:%s" % (path, incar.line_of("SIGMA")),
            "ISMEAR=0（Gaussian）配了较大的 SIGMA=%g eV" % sigma,
            "Gaussian 展宽把自由能外推到 sigma→0；SIGMA 太大时"
            "外推误差会变大，而且会**改变**某些能量差。",
            "绝缘体/半导体用 ISMEAR=0 + SIGMA=0.01–0.05；"
            "金属优先 ISMEAR=1（或 -5 做 DOS）；SIGMA 一般 ≤0.2。",
            "经验判据（VASP wiki: ISMEAR / SIGMA）"))
    if ismear in (-4, -5):
        out.append(Finding(
            "INFO", "INCAR.smearing", where,
            "用了四面体方法（ISMEAR=%d）" % ismear,
            "四面体方法适合 DOS/绝缘体；但它对**力的计算**可能不稳定，"
            "而且不适合做 MD/弛豫中的金属。",
            "几何优化/分子动力学常用 ISMEAR=0/1；DOS 与静态能量用 -5。",
            "VASP wiki: ISMEAR"))
    return out


def _check_cross(inp, incar, kpoints, poscar, potcar):
    out = []
    # --- 元素顺序 ---
    #
    # ⚠️ 先处理一个**会被静默跳过**的情形：**VASP4 格式的 POSCAR**
    #    （第 6 行直接是数目，没有元素名行）。
    #    实测（见 CHANGELOG 的 CR-031）：这种文件读出来
    #    `symbols == []`、`counts == [2]`，于是下面那个
    #    `if poscar and poscar.symbols and ...` 守卫**整段不成立** ⇒
    #    `XSPECIES.counts` 与 `XSPECIES.elements` 两条**跨文件硬约束**
    #    都被**静默跳过**，而"本次未检查的项"里**也不会提它**。
    #    ⇒ 用户看到"ERROR 0 项"会以为元素顺序查过了 —— **其实没查**。
    #
    #    这不是假想：**ASE 写 POSCAR 默认就是 VASP4 格式**
    #    （`[LVTHW]` `A14:109-123`、`A16:48-54` 两处独立记载），
    #    而本项目推荐的工具链里就有 ASE 类的用法。
    if poscar and not poscar.symbols:
        out.append(Finding(
            "WARN", "XSPECIES.vasp4_poscar", str(inp.get("POSCAR")),
            "这个 POSCAR **没有元素名行**（第 6 行直接是数目）—— "
            "是 **VASP4 格式**。VASP 本身能读，但本工具因此"
            "**无法核对元素顺序**。",
            "`POTCAR` 必须与 `POSCAR` 的**元素顺序**逐一对应，而顺序信息"
            "只存在于那一行元素名里。没有它，"
            "`XSPECIES.elements` / `XSPECIES.counts` 这两条"
            "**跨文件硬约束本次没有执行**。"
            "⚠️ **ASE 等工具默认导出的就是这种格式。**",
            "在 POSCAR 第 6 行补上元素名（按 POTCAR 的 TITEL 顺序），"
            "例如把 `2` 改成 `Si`（或 `Si 2` 的 VASP5 写法），"
            "然后重跑本校验。补之前请自己先确认顺序对不对。",
            "VASP wiki: POSCAR（VASP4/VASP5 格式差异）；"
            "[LVTHW] A14 / A16（ASE 导出为 VASP4 格式）"))
    if poscar and poscar.symbols and potcar and potcar.elements:
        if len(poscar.symbols) != len(potcar.elements):
            out.append(Finding(
                "ERROR", "XSPECIES.counts", "%s vs %s"
                % (inp.get("POSCAR"), inp.get("POTCAR") or "POTCAR"),
                "POSCAR 有 %d 种元素（%s），POTCAR 有 %d 个数据集（%s）"
                % (len(poscar.symbols), " ".join(poscar.symbols),
                   len(potcar.elements), " ".join(potcar.elements)),
                "POTCAR 必须由**与 POSCAR 元素顺序完全一致**的数据集拼接而成。"
                "数目不符时 VASP 会读错赝势 —— 而且**很多情况下不报错**，"
                "只是结果无意义。",
                "按 POSCAR 第 6 行的顺序重新 `cat` 拼 POTCAR。",
                "VASP wiki: POTCAR"))
        else:
            bad = [(i, a, b) for i, (a, b) in
                   enumerate(zip(poscar.symbols, potcar.elements)) if a != b]
            if bad:
                detail = "; ".join("第 %d 位 POSCAR=%s 而 POTCAR=%s"
                                   % (i + 1, a, b) for i, a, b in bad)
                out.append(Finding(
                    "ERROR", "XSPECIES.elements",
                    "%s vs %s" % (inp.get("POSCAR"), inp.get("POTCAR") or "POTCAR"),
                    "元素顺序不一致：" + detail,
                    "这是**跨文件硬约束**：VASP 按位置把 POTCAR 的数据集"
                    "配给 POSCAR 的元素，不按元素名匹配。顺序错了，"
                    "每个原子的赝势都是错的，而程序**不会报错**。",
                    "重排 POTCAR 的拼接顺序，使之与 POSCAR 第 6 行一致；"
                    "然后重跑本校验确认。",
                    "VASP wiki: POTCAR（\"in the same order as in the POSCAR\"）"))
    # --- ENCUT vs ENMAX ---
    if potcar and potcar.max_enmax() is not None:
        enmax = potcar.max_enmax()
        encut = incar.get_float("ENCUT") if incar else None
        where = ("%s:%s" % (inp.get("INCAR"), incar.line_of("ENCUT"))
                 if incar and incar.line_of("ENCUT") else str(inp.get("INCAR")))
        if encut is None:
            out.append(Finding(
                "WARN", "XENCUT.enmax", where,
                "INCAR 里没写 ENCUT；VASP 会取 POTCAR 的 ENMAX 作为默认"
                "（本套 POTCAR 的 max ENMAX = %.3f eV）" % enmax,
                "用 POTCAR 默认截断能不是错，但它**通常偏小**，"
                "而且当你换一个 POTCAR 时结果会**静默**改变 ——"
                "可复现性依赖于你没动过 POTCAR。",
                "显式写出 ENCUT（官方也建议这样做），并做一次收敛测试；"
                "常见做法是取 max(ENMAX) 的 1.0–1.3 倍。",
                "VASP wiki: ENCUT / POTCAR 的 Tip"))
        elif encut < enmax - 1e-6:
            # ⚠️ 这条判据**必须分档**，不能一律报 ERROR。
            #
            # 依据：真实算例 `3-electronicStructure/ex8-NaHe2` 的 INCAR 用
            # ENCUT=520，而 Na2He 的 POTCAR 里 He 的 ENMAX 高达 2135 eV。
            # 但"ENMAX 极高"**不一定**意味着必须用那么高的截断：
            # ENMAX 是**孤立原子**的推荐值，He 是闭壳层、几乎不参与成键，
            # 这类体系几百 eV 通常就够。官方 wiki 的 ENCUT 页只说默认值
            # 取 POTCAR 里的最大值，**没有**断言"低于 ENMAX 一定不收敛"。
            #
            # 所以：**分档报告，并把不确定性写出来**，而不是给一个假的确定感。
            hard_limit = 1000.0
            if enmax > hard_limit:
                out.append(Finding(
                    "WARN", "XENCUT.enmax", where,
                    "ENCUT = %.1f eV 低于本套 POTCAR 的 max ENMAX = %.1f eV"
                    % (encut, enmax),
                    "ENMAX 是**孤立原子**的推荐截断。本套 POTCAR 里有一个元素的 "
                    "ENMAX 异常高（>%.0f eV，常见于 He/Ne 这类闭壳层，或 "
                    "3d 过渡金属的 _pv/_d 半芯态赝势）。对这类元素，"
                    "**几百 eV 往往已经够用**，机械照搬 ENMAX 会白烧几倍机时。"
                    "⚠️ 但「够用」是**经验判断**，不是官方明文 —— "
                    "本工具无法替你决定，只能提示你**必须自己测**。" % hard_limit,
                    "做一次 ENCUT 收敛测试（把 ENCUT 从 %.0f 扫到 %.0f，"
                    "看总能量差是否 < 1 meV/atom），固定住这个值再往下做。"
                    % (max(200.0, encut * 0.7), enmax),
                    "VASP wiki: POTCAR（ENMAX/ENMIN）；"
                    "⚠️ 分档阈值 %.0f eV 是本工具的经验设定，**不是官方判据**"
                    % hard_limit))
            elif encut < enmax * 0.8:
                out.append(Finding(
                    "ERROR", "XENCUT.enmax", where,
                    "ENCUT = %.1f eV 明显低于本套 POTCAR 的 max ENMAX = %.3f eV"
                    "（只有 %.0f%%）" % (encut, enmax, 100.0 * encut / enmax),
                    "低于赝势自带 ENMAX 时，平面波基组不足以描述该赝势，"
                    "结果会**系统性偏差**，而且不会有任何报错。"
                    "官方在 POTCAR 页把 ENMAX 列为「推荐的」截断、"
                    "ENMIN 列为「最低可用」的，并建议在 INCAR 里显式写 ENCUT。",
                    "把 ENCUT 提到 %.0f eV 以上（常用 1.0–1.3×ENMAX），"
                    "并做一次 ENCUT 收敛测试确认。" % (enmax * 1.0),
                    "VASP wiki: POTCAR（ENMAX/ENMIN 节）；VASP wiki: ENCUT"))
            else:
                out.append(Finding(
                    "WARN", "XENCUT.enmax", where,
                    "ENCUT = %.1f eV 略低于本套 POTCAR 的 max ENMAX = %.3f eV"
                    "（%.0f%%）" % (encut, enmax, 100.0 * encut / enmax),
                    "落在 ENMIN 与 ENMAX 之间：属于「能算，但偏离官方推荐」的区间。"
                    "它**不一定是错的** —— 若你做过的 ENCUT 收敛测试显示"
                    "这个值已经够，那就没问题。",
                    "确认你为**这套**赝势做过 ENCUT 收敛测试；"
                    "没做过的话，至少扫到 %.0f eV 看一眼。" % enmax,
                    "VASP wiki: POTCAR（ENMAX/ENMIN 节）"))
        else:
            ratio = encut / enmax
            if ratio < 1.0:
                pass
            elif ratio > 2.2:
                out.append(Finding(
                    "INFO", "XENCUT.enmax", where,
                    "ENCUT = %.1f eV 是 max ENMAX（%.1f eV）的 %.2f 倍"
                    % (encut, enmax, ratio),
                    "截断能远高于赝势推荐值时，计算量按 ENCUT^1.5 量级增长，"
                    "而能量差往往已在小 meV 量级。",
                    "除非收敛测试显示还需要更高，否则 1.0–1.3 倍足够。",
                    "经验判据"))
    # --- MAGMOM 个数 ---
    if incar and poscar and incar.get("MAGMOM"):
        toks = incar.get("MAGMOM").split()
        total = 0
        bad = False
        for t in toks:
            m = re.fullmatch(r"(\d+)\*([-\d.eE+]+)", t)
            if m:
                total += int(m.group(1))
            else:
                try:
                    float(t)
                    total += 1
                except ValueError:
                    bad = True
        if not bad and total != poscar.nions:
            out.append(Finding(
                "ERROR", "XMAGMOM.count",
                "%s:%s" % (inp.get("INCAR"), incar.line_of("MAGMOM")),
                "MAGMOM 展开后是 %d 个，但 POSCAR 有 %d 个原子" % (total, poscar.nions),
                "MAGMOM 是按**原子顺序**逐个给的。个数不符时 VASP 的行为"
                "（补默认值 / 只用前 N 个）不直观，磁态会失控。",
                "补齐到正好 %d 个（可用 `N*x` 简写压缩长列表），"
                "并与 POSCAR/`POSCAR` 的元素分段对齐。" % poscar.nions,
                "VASP wiki: MAGMOM"))
    # --- LDAU 列表长度 ---
    if incar and poscar and poscar.symbols:
        nsp = len(poscar.symbols)
        for tag in ("LDAUL", "LDAUU", "LDAUJ"):
            v = incar.get(tag)
            if not v:
                continue
            n = len(v.split())
            if n != nsp:
                out.append(Finding(
                    "ERROR", "XLDau.count",
                    "%s:%s" % (inp.get("INCAR"), incar.line_of(tag)),
                    "%s 有 %d 个数，但 POSCAR 有 %d 种元素" % (tag, n, nsp),
                    "DFT+U 的参数是**逐元素**给的，顺序必须与 POSCAR 的元素顺序一致。"
                    "长度不符时 VASP 会按默认值补齐，U 就加到了错误的元素上。",
                    "补齐到 %d 个数，顺序与 POSCAR 第 6 行一致。"
                    "不想要 U 的元素写 0（LDAUL 写 -1）。" % nsp,
                    "VASP wiki: LDAUU / LDAUL"))
    # --- 维度 vs k 点 ---
    if poscar and kpoints and kpoints.mode == "regular" and kpoints.mesh:
        try:
            is_slab, holes = poscar.cell.is_slab(poscar.cartesian())
        except Exception:                                    # noqa: BLE001
            is_slab, holes = False, (0.0, 0.0, 0.0)
        if is_slab:
            for d, h in enumerate(holes):
                if h >= 6.0 and kpoints.mesh[d] != 1:
                    out.append(Finding(
                        "WARN", "XDIM.kpoints", inp.get("KPOINTS", ""),
                        "第 %d 个方向有约 %.1f Å 真空（低维体系），"
                        "但 k 点网格在该方向取了 %d"
                        % (d + 1, h, kpoints.mesh[d]),
                        "真空方向取 >1 的 k 点通常**没有物理收益**，"
                        "只是按倍数浪费机时；有些情况下还会引入"
                        "真空方向的杂化而让能带看起来「怪」。",
                        "把该方向的网格数改成 1。⚠️ 本判据是**启发式**"
                        "（按原子跨度与晶格长度的差判断真空），"
                        "对「倾斜晶胞」或「层间有真实相互作用」的体系可能误报 ——"
                        "请自己确认该方向确实只有真空。",
                        "经验判据（非官方硬规则；请以你的体系为准）"))
    # --- NELECT ---
    if incar and potcar and potcar.total_valence() is not None:
        nelect = incar.get_float("NELECT")
        if nelect is not None:
            neutral = potcar.total_valence()
            diff = neutral - nelect
            if abs(diff) > 1e-6:
                out.append(Finding(
                    "INFO", "XCHARGE.nelect",
                    "%s:%s" % (inp.get("INCAR"), incar.line_of("NELECT")),
                    "NELECT = %g，而 POTCAR 价电子总数为 %g（差 %+g）"
                    % (nelect, neutral, -diff),
                    "改 NELECT 是引入**背景电荷**给体系带电的标准做法；"
                    "差值为正表示体系带负电（多了电子）。",
                    "确认这就是你的意图。⚠️ 带电体系必须配**偶极修正**"
                    "（LDIPOL/IDIPOL）并做有限尺寸外推，否则能量不可比；"
                    "并且要自己核对真空能级对齐。",
                    "references/decide.md（带电体系一节）"))
    return out


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
UNCHECKED_ALWAYS = [
    "⑥ \"语法全对但 VASP 不接受\"：**本工具原理上抓不到**，"
    "需要真程序 —— 见 conformance/README.md",
    "⑦ \"VASP 不报错但结果不对\"：见 compare.py（物理不变量）"
    "与 diagnose.py（症状→处方）",
    "• KPOINTS 的广义规则网格\"生成矢量是否与倒格矢 commensurate\"："
    "未实现（官方说 commsurate 不成立时程序会报错退出，属可自查项）",
    "• 赝势\"选得对不对\"（该不该用 _pv/_d、该用 PBE 还是 PW91）："
    "本工具只查顺序与截断，**不评价选型**",
    "• 对称性是否被磁性/缺陷正确打破：需要真程序",
    "• 你声明的物理目标与这套参数是否匹配：**这是人的判断，工具不代替**",
]


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="validate.py",
        description="VASP 四件套离线校验（语法 / 归属 / 值域 / 跨文件一致性）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=无 ERROR；1=文件问题；2=用法错误；4=有 ERROR；"
               "5=仅有 WARNING。\n"
               "⚠️ 退出码 0 **不表示算得对**，只表示「检查过的项」没发现问题。",
    )
    ap.add_argument("directory", nargs="?", default=None,
                    help="算例目录（默认当前目录）")
    ap.add_argument("--incar", help="显式指定 INCAR 路径")
    ap.add_argument("--kpoints", help="显式指定 KPOINTS 路径")
    ap.add_argument("--poscar", help="显式指定 POSCAR 路径")
    ap.add_argument("--potcar", help="显式指定 POTCAR 路径"
                                     "（默认在算例目录里找；**绝不被复制或写出**）")
    ap.add_argument("--strict", action="store_true",
                    help="把 WARNING 也当成失败（退出码 4）")
    ap.add_argument("--quiet", action="store_true", help="只印结论行")
    ap.add_argument("--list-checks", action="store_true",
                    help="列出本工具会做哪些检查，然后退出")
    ap.add_argument("--ncores", type=int,
                    help="你实际提交用的 MPI 核数。给了它，并行分解预检（XPAR.* / XNCORE.*）才能真正生效；"
                         "不给则相关检查**降级为未检查**（不猜）")
    ap.add_argument("--vasp-version",
                    help="你实际使用的 VASP 版本（如 5.4.4 / 6.3.0）。"
                         "不给时会自动从算例目录的 OUTCAR 第一行读；"
                         "两者都没有则**版本相关检查不执行**（不猜）")
    ap.add_argument("--keyword-table", default=KW_TABLE,
                    help="覆盖关键字表路径（默认 references/official/_keywords.tsv）")
    args = ap.parse_args(argv)

    if args.list_checks:
        print("validate.py 会做的检查：\n")
        for cid, desc in CHECK_DESCRIPTIONS:
            print("  %-28s %s" % (cid, desc))
        print("\n本工具**不做**的检查（如实列出，避免误信 OK）：")
        for line in UNCHECKED_ALWAYS:
            print("  " + line)
        return EXIT_OK

    directory = args.directory or "."
    if not os.path.isdir(directory):
        vc.die("不是一个目录：%s" % directory, EXIT_USER,
               "用法：python scripts/validate.py <算例目录>")

    inp = vc.discover_inputs(directory)
    if args.incar:
        inp["INCAR"] = args.incar if os.path.exists(args.incar) else vc.die(
            "指定的 INCAR 不存在：%s" % args.incar, EXIT_USER)
    if args.kpoints:
        inp["KPOINTS"] = args.kpoints if os.path.exists(args.kpoints) else vc.die(
            "指定的 KPOINTS 不存在：%s" % args.kpoints, EXIT_USER)
    if args.poscar:
        inp["POSCAR"] = args.poscar if os.path.exists(args.poscar) else vc.die(
            "指定的 POSCAR 不存在：%s" % args.poscar, EXIT_USER)

    if not any(inp.get(k) for k in ("INCAR", "KPOINTS", "POSCAR", "POTCAR")):
        vc.die("在 %s 里没找到任何 VASP 输入文件"
               "（找过 INCAR / KPOINTS / POSCAR|CONTCAR / POTCAR）" % directory,
               EXIT_USER,
               "如果文件名很特别，用 --incar/--kpoints/--poscar/--potcar 显式指定。")

    kw = KeywordTable(args.keyword_table)

    print("=" * 72)
    print("VASP 输入校验 —— %s" % inp["dir"])
    print("=" * 72)
    print("读到的文件：")
    for key in ("INCAR", "KPOINTS", "POSCAR", "POTCAR"):
        p = inp.get(key)
        print("  %-8s %s" % (key, os.path.basename(p) if p else "（未找到）"))
    if args.potcar:
        print("  %-8s %s（由 --potcar 指定）" % ("POTCAR", args.potcar))
    print()

    if not kw.loaded:
        print("!! 归属校验未执行：" + kw.reason)
        print("   本次**不检查**「关键字是否真的存在」以及「是否属于该文件」。")
        print("   这类缺陷正是「语法全对但程序不接受」的典型来源。\n")

    uv = None
    if args.vasp_version:
        uv = vc.parse_version_tuple(args.vasp_version)
        if uv is None:
            vc.die("--vasp-version 的写法不认识：%s" % args.vasp_version,
                   EXIT_USAGE,
                   "请写成 5.4.4 / 6.3.0 这样（至少两段）。")
    findings = collect_findings(inp, kw, potcar_path=args.potcar,
                               vasp_version=uv, ncores=args.ncores)

    errors = [x for x in findings if x.level == "ERROR"]
    warns = [x for x in findings if x.level == "WARN"]
    infos = [x for x in findings if x.level == "INFO"]

    if not args.quiet:
        for x in errors + warns + infos:
            print(x.render())
            print()
    else:
        for x in errors + warns:
            print("%s %s %s" % (x.level, x.check_id, x.msg))

    print("-" * 72)
    print("结论：ERROR %d 项，WARNING %d 项，INFO %d 项" % (len(errors), len(warns),
                                                          len(infos)))
    if errors:
        print("      → 有 ERROR 级问题。**先修完这些再上机**，"
              "否则很可能白跑一趟。")
    elif warns:
        print("      → 没有 ERROR；有 WARNING 需要你自己判断（--strict 可让"
              "WARNING 也判失败）。")
    else:
        print("      → 未发现 ERROR/WARNING。")
    print()
    print("⚠️ 本次**未检查**的项（这些不是「通过了」，是「没查」）：")
    for line in UNCHECKED_ALWAYS:
        print("   " + line)
    if not kw.loaded:
        print("   • 关键字归属（表缺失，见上）")
    if not inp.get("POTCAR") and not args.potcar:
        print("   • 所有 POTCAR 相关检查（目录里没有 POTCAR 且未用 --potcar 指定）")
    if not inp.get("KPOINTS"):
        print("   • 所有 KPOINTS 相关检查（目录里没有 KPOINTS）")
    print()
    print("要判「算得对不对」，跑：python scripts/compare.py <目录>（物理不变量）")

    if errors:
        return EXIT_ERROR
    if warns and args.strict:
        return EXIT_ERROR
    if warns:
        return EXIT_WARN
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
