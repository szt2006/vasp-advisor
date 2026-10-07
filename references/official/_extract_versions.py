#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_extract_versions.py —— 从官方层**逐行提取版本门控**（`_versions.tsv`）

为什么需要它
============
**这是一个真实存在的、全局性的风险**（本项目实测）：

| 来源 | 实测版本 |
|---|---|
| 官方 wiki 语料（我们抓的） | **VASP 6.6 时代** —— 91 处 `{{Available}}` 门槛里 61×`6.5.0`、25×`6.6.0` |
| `things to study/` 的 98 个真实算例 | **全部 `vasp.5.4.4`**（无一例外） |
| LVTHW 教程 | 以 `vasp.5` / `VASP5` 为主 |
| 讲义 | 提到 `VASP5.4.4` |

⇒ 我们**一直在用 6.6 时代的文档支撑 5.4.4 的行为断言**，
而 `vasp_common.outcar_version()` 虽然读出了版本号，**却没有任何一处拿它做判断**。
一个用 5.4.4 的人如果照抄一个 6.5.0 才有的标签，程序会**静默忽略**它
（或报一个看不懂的错）—— 正是本项目最想消灭的那类问题。

核心设计决策：**从官方层逐行提取，不手写版本清单。**
----------------------------------------------------
手写的版本表**必然腐烂**（官方一直在发新版），而且会与官方层**互相冲突**。
逐行提取则像 `_keywords.tsv` 一样：**可重建、可审计、每条都指得回原文行号**。

提取什么（**只提取官方语料里"写着"的东西，不推断**）
----------------------------------------------------
| 类型 | 官方模板 | 含义 |
|---|---|---|
| `available` | `{{Available\|6.5.0}}` | **该标签从哪个版本才有** |
| `available_upto` | `{{Available\|6.2.0\|6.4.0}}` | 该标签的**版本区间**（两个参数时） |
| `removed` | `{{Available\|…\|removed}}` / 正文 `removed in VASP` | 已移除 |
| `deprecated` | `{{NB\|deprecated\|…}}` | 已弃用（**能跑，但不推荐**） |
| `cond_default` | `{{DEF\|TAG\|cond1\|val1\|…}}` | **条件默认值**（随别的标签变） |
| `min_version_text` | 正文里的 `as of VASP.6.4.1` / `in VASP.5.4.4` | 正文写明的版本 |
| `ml_gate` | ML / ELPH / NMR 等**新功能**页 | 由 `available` 覆盖，不重复提取 |

⚠️ **它提取不到什么（必须让用户知道）**
--------------------------------------
1. **绝大多数标签没有版本标注。** 官方只对"新加的"标 `{{Available}}`。
   ⇒ **没有标注 ≠ 所有版本都有**，它只意味着"官方没写"。
   → 工具的措辞必须是「**官方未标注版本门槛**」，不能是「所有版本都支持」。
2. **标了 `Available` 也不等于"老版本一定没有"** —— 有些功能在成为正式标签前
   就以别的形式存在过。
3. **提取的是"标在页面上的版本"，不是"该行为首次出现的版本"。**
   官方可能事后补标，也可能忘了标。
4. ⚠️⚠️ **`min_version_text`（散文里的版本）只作线索，不能当门槛。**
   本项目**实测过这个反例**：把散文版本也当门槛的话，对一个 5.4.4 用户会报出
   `GGA` 需 6.4.3（94 个真实算例）、`ISIF` 需 6.4.1（94 个）、
   `ISPIN` 需 6.5.0（49 个）—— 而这三个标签**显然在 5.4.4 里就有**。
   根因：那句话讲的是**某个新增取值**的版本（如"`ISIF=8` 自 6.4.1 起"），
   不是"整个标签自那时才有"。
   ⇒ `vasp_common.load_version_gates()` **只采信 `available` 三种结构化标注**。

用法
----
    python references/official/_extract_versions.py
    python references/official/_extract_versions.py --list      # 按版本汇总
    python references/official/_extract_versions.py --gate ISMEAR  # 查一个标签
    python references/official/_extract_versions.py --out X.tsv

输出：`_versions.tsv`
    列：`page` `tag` `kind` `version` `version_upto` `line` `verbatim` `note`

`verbatim` 是**原文那一行**（截断到 200 字符），保证每条都能回原文核对。
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES = os.path.join(HERE, "pages")

# --- `{{Available|6.5.0}}` / `{{Available|6.2.0|6.4.0}}` ---
RE_AVAILABLE = re.compile(r"\{\{Available\|([^}]*)\}\}")
# --- `{{DEF|TAG|cond1|val1|cond2|val2}}`（条件默认值） ---
RE_DEF = re.compile(r"\{\{DEF\|([^}]*)\}\}")
# --- `{{NB|deprecated|...}}` ---
RE_DEPRECATED = re.compile(r"\{\{NB\|\s*deprecated", re.I)
# --- 正文里写明的版本：`as of VASP.6.4.1` / `in VASP.5.4.4` / `VASP.6.2.0 and newer` ---
RE_TEXT_VER = re.compile(
    r"(?:as of|since|from|in|with|requires?)\s+VASP\.?\s*"
    r"(\d+\.\d+(?:\.\d+)*)", re.I)
# --- 移除/废弃的正文写法 ---
RE_REMOVED_TEXT = re.compile(
    r"(?:removed|no longer (?:available|supported|recommended)|obsolete)"
    r"[^.\n]{0,80}?VASP\.?\s*(\d+\.\d+(?:\.\d+)*)", re.I)

# `{{Available}}` 的第二个参数可能是这些"不是版本号"的词
NON_VERSION = {"removed", "deprecated", "yes", "true", "no", "false", "n/a"}


def _vtuple(v: str):
    """把 `6.5.0` 变成可排序的元组；解析不了返回 None。"""
    try:
        parts = [int(x) for x in v.split(".")]
    except ValueError:
        return None
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _tag_of(page_stem: str) -> str:
    """页面主干就是标签名（官方约定：一个 INCAR 标签一页）。"""
    return page_stem


def scan_page(path: str):
    """扫一页，产出该页的版本条目。"""
    stem = os.path.splitext(os.path.basename(path))[0]
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return out

    for i, line in enumerate(lines, start=1):
        # 1) Available：版本门槛 / 区间
        for m in RE_AVAILABLE.finditer(line):
            args = [a.strip() for a in m.group(1).split("|")]
            args = [a for a in args if a]
            if not args:
                out.append((stem, _tag_of(stem), "available", "", "", i,
                            line.strip(), "{{Available}} 没给参数"))
                continue
            first = args[0]
            if first.lower() in NON_VERSION:
                out.append((stem, _tag_of(stem), "available_state", "", "",
                            i, line.strip(),
                            "{{Available}} 的状态词：%s" % first))
                continue
            v1 = first
            v2 = ""
            note = ""
            for a in args[1:]:
                if a.lower() in NON_VERSION:
                    note = a
                elif _vtuple(a):
                    v2 = a
                else:
                    note = (note + " " + a).strip()
            kind = "available_upto" if v2 else "available"
            out.append((stem, _tag_of(stem), kind, v1, v2, i, line.strip(),
                        note))

        # 2) 条件默认值
        for m in RE_DEF.finditer(line):
            args = [a.strip() for a in m.group(1).split("|")]
            if len(args) >= 3:
                out.append((stem, args[0] or _tag_of(stem), "cond_default",
                            "", "", i, line.strip(),
                            "条件：%s ⇒ %s" % (args[1], args[2])))

        # 3) deprecated 标注
        if RE_DEPRECATED.search(line):
            out.append((stem, _tag_of(stem), "deprecated", "", "", i,
                        line.strip()[:200], "官方标 deprecated"))

        # 4) 正文写明的版本（只在**同一行**里出现版本号时记，避免标题行误触发）
        for m in RE_TEXT_VER.finditer(line):
            out.append((stem, _tag_of(stem), "min_version_text", m.group(1),
                        "", i, line.strip()[:200],
                        "正文写明的版本（措辞：%s）" % m.group(0)[:40]))
        for m in RE_REMOVED_TEXT.finditer(line):
            out.append((stem, _tag_of(stem), "removed_text", m.group(1), "",
                        i, line.strip()[:200], "正文提到移除/不再支持"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_extract_versions.py",
        description="从官方层逐行提取版本门控 → _versions.tsv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法\n----", 1)[-1].strip(),
    )
    ap.add_argument("--out", default=os.path.join(HERE, "_versions.tsv"))
    ap.add_argument("--list", action="store_true", help="按版本汇总")
    ap.add_argument("--gate", help="查某个标签的版本门控")
    ap.add_argument("--strict-after", default="6.4",
                    help="把 >= 此版本的条目视为「新版本专属」（默认 6.4）")
    args = ap.parse_args(argv)

    if not os.path.isdir(PAGES):
        sys.stderr.write("错误：找不到 %s\n" % PAGES)
        return 3

    rows = []
    for fn in sorted(os.listdir(PAGES)):
        if fn.endswith(".md"):
            rows.extend(scan_page(os.path.join(PAGES, fn)))

    if args.gate:
        g = args.gate.upper()
        hit = [r for r in rows if r[1].upper() == g or r[0].upper() == g]
        print("=== %s 的版本门控 ===" % args.gate)
        if not hit:
            print("  **没有找到任何版本标注** ⇒ 官方未标注（≠ 所有版本都支持）")
        for r in hit:
            print("  [%s] %s%s   （pages/%s.md:%d）"
                  % (r[2], r[3], ("–" + r[4]) if r[4] else "", r[0], r[5]))
            print("      %s" % r[7])
        return 0

    if args.list:
        from collections import Counter
        c = Counter(r[3] for r in rows if r[2] in ("available", "available_upto")
                    and r[3])
        print("=== 官方标注了版本门槛的标签，按版本汇总 ===")
        for v, n in sorted(c.items(), key=lambda kv: (_vtuple(kv[0]) or (0, 0, 0))):
            print("  %-10s %3d 个标签" % (v, n))
        thr = _vtuple(args.strict_after)
        new = [r for r in rows if r[2] == "available" and r[3]
               and (_vtuple(r[3]) or (0, 0, 0)) >= thr]
        print("\n=== ⚠️ >= %s 的「新版本专属」标签：%d 个 ==="
              % (args.strict_after, len(new)))
        print("    （用老版本的用户照抄这些标签 ⇒ 程序**静默忽略**或报错）")
        for r in sorted(new, key=lambda x: (_vtuple(x[3]) or (0, 0, 0), x[1])):
            print("    %-9s %s" % (r[3], r[1]))
        return 0

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# 官方层的版本门控（**逐行提取，每条可回原文核对**）\n")
        fh.write("# 由 references/official/_extract_versions.py 生成。\n")
        fh.write("# ⚠️ **没有条目 ≠ 所有版本都支持** —— 官方只对'新加的'标版本；\n")
        fh.write("#    「没有标注」只能理解为「官方没写」，不能理解为「都支持」。\n")
        fh.write("# page\ttag\tkind\tversion\tversion_upto\tline\tverbatim\tnote\n")
        for r in rows:
            fh.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")

    from collections import Counter
    kc = Counter(r[2] for r in rows)
    print("已写出 %s" % args.out)
    print("  共 %d 条，覆盖 %d 个页面" % (len(rows), len({r[0] for r in rows})))
    for k, v in kc.most_common():
        print("    %-18s %4d" % (k, v))
    print()
    print("⚠️ **本索引里没有的标签，不代表所有版本都支持** ——")
    print("   官方只对「新加的」标 {{Available}}。工具的措辞必须是")
    print("   「官方未标注版本门槛」，**不能**是「所有版本都支持」。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
