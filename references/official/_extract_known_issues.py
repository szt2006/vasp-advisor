#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_extract_known_issues.py —— 把官方 `Known issues` 页变成可查询的表

为什么需要它
============
官方 `references/official/pages/Known_issues.md` 是一份**结构化**的
缺陷数据库（不是散文）：每个问题带

```
{{KnownIssue
  ID                  = 110
  resolved_in_version = -          ← 还没修（`-`）
  reported_in_version = 6.2.0      ← ⭐ 从哪个版本开始有这个问题
  date_added          = 2026-09-28
  resolved_in_commit  = 854ea1087
  text                = **某个功能在某条件下是错的** …
}}
```

**为什么这对本 skill 特别重要**：它正是
「**程序不报错、但结果是错的**」这一类问题的**官方登记簿** ——
本项目一直说这类问题"多数只有真程序和你的物理判断能抓"，
而官方其实**把它们逐条登记出来了**，还标了版本。

⇒ 一个用 VASP 6.2.0 的人，如果他的计算落在 issue 110 的条件里，
**结果可能是错的而不报错**。Skill 有责任把这件事告诉他。

官方自己在页首写明：`Below we provide an **incomplete** list of known issues.`
⇒ **提取到的不是全部**，这一点必须如实传达。

用法
----
    python references/official/_extract_known_issues.py
    python references/official/_extract_known_issues.py --for-version 5.4.4
    python references/official/_extract_known_issues.py --list-open
    python references/official/_extract_known_issues.py --match ELPH

输出：`_known_issues.tsv`
    列：`id` `reported_in` `resolved_in` `resolved_in_commit` `date`
        `status` `text`

`status` ∈ `open`（未修）/ `fixed`（已修）/ `obsolete`（已作废）
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "pages", "Known_issues.md")
OUT = os.path.join(HERE, "_known_issues.tsv")

# `{{KnownIssue` … `}}` 块
RE_BLOCK = re.compile(r"\{\{KnownIssue(.*?)\n\}\}", re.S)
# 字段名；用于**在块内切片**，不直接取值。
#
# ⚠️ 这份清单必须**包含页面里出现的全部字段**，否则切片在错误的位置断开。
# 实测踩过：官方有 2 条带 `hide = True`，而当时清单里没有 `hide`，
# 于是 `text` 一路吞到块尾 —— **那两条的正文直接变成空串**。
# 教训：解析模板时，**字段清单要从页面里枚举出来核对，不要凭印象写**。
RE_FIELDNAME = re.compile(
    r"^\s*(ID|resolved_in_version|reported_in_version|date_added"
    r"|resolved_in_commit|hide|style|text)\s*=", re.M | re.I)

# 版本字段里**不是 VASP 程序版本**的东西：
# 实测 #25 的 `resolved_in_version = PBE.64` —— 那是 **POTCAR 数据发布版**。
# 混在一起会误导用户（他会去找一个叫 "VASP PBE.64" 的版本）。
RE_DATA_RELEASE = re.compile(r"^(PBE|LDA|PW|GW|pot|paw)[.\-_]?\d*", re.I)


def _classify_version(v: str) -> str:
    """分类：`code`（VASP 程序版本）/ `data`（POTCAR 数据发布版）/ `unknown`。

    **分类不改变数值，只影响怎么向用户描述** ——
    否则用户会去查一个不存在的 "VASP PBE.64"。
    """
    v = (v or "").strip()
    if not v or v == "-":
        return "unknown"
    if RE_DATA_RELEASE.match(v):
        return "data"
    return "code" if _vtuple(v) else "unknown"


def _fields(body: str) -> dict:
    """把 `{{KnownIssue}}` 的块切成字段。

    ⚠️ **不能用 `^\\s*(\\w+)\\s*=\\s*(.*)$` 逐行取值** ——
    官方有些条目的 `text` 是**多行**的（实测 #110 / #108 直接取成空串）。
    正确做法：先找出所有"字段名"出现的位置，再按位置把块切片，
    这样多行内容就自然包含进来了。
    """
    hits = list(RE_FIELDNAME.finditer(body))
    out = {}
    for i, m in enumerate(hits):
        name = m.group(1).lower()
        start = m.end()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(body)
        out[name] = body[start:end].strip()
    return out


def _vtuple(v: str):
    v = (v or "").strip()
    if not v or v == "-":
        return None
    try:
        parts = [int(x) for x in v.split(".")]
    except ValueError:
        return None
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def parse(path: str):
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8", errors="replace").read()
    rows = []
    for m in RE_BLOCK.finditer(txt):
        f = _fields(m.group(1))
        iid = f.get("id", "").strip()
        if not iid:
            continue
        rep = f.get("reported_in_version", "").strip()
        res = f.get("resolved_in_version", "").strip()
        text = f.get("text", "").strip()
        text = re.sub(r"\s+", " ", text)
        if res and res != "-":
            status = "fixed"
        elif "obsolete" in f.get("text", "").lower():
            status = "obsolete"
        else:
            status = "open"
        rows.append({
            "id": iid,
            "reported_in": rep,
            "resolved_in": "" if res in ("", "-") else res,
            "resolved_in_commit": f.get("resolved_in_commit", "").strip(),
            "date": f.get("date_added", "").strip(),
            "status": status,
            "kind": _classify_version(rep),
            "text": text,
        })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_extract_known_issues.py",
        description="官方 Known issues 页 → 可查询的 TSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法\n----", 1)[-1].strip(),
    )
    ap.add_argument("--src", default=SRC)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--for-version", help="只列「该版本可能受影响」的问题")
    ap.add_argument("--list-open", action="store_true", help="只列未修的")
    ap.add_argument("--match", help="按关键词过滤正文")
    ap.add_argument("--limit", type=int, default=40, help="最多打印几条")
    args = ap.parse_args(argv)

    rows = parse(args.src)
    if rows is None:
        sys.stderr.write(
            "错误：找不到 %s\n"
            "  请先抓这一页：python references/official/_fetch_named.py "
            "--title \"Known issues\"\n" % args.src)
        return 3
    if not rows:
        sys.stderr.write("错误：解析到 0 条 —— 页面格式可能变了（见该页的 "
                         "{{KnownIssue}} 模板）\n")
        return 1

    with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# 官方 Known issues（**逐条可回原文**）\n")
        fh.write("# 由 references/official/_extract_known_issues.py 生成。\n")
        fh.write("# ⚠️ 官方自己写明这是 **incomplete** 列表 ⇒ 没列出来的"
                 "不代表没问题。\n")
        fh.write("# ⚠️ 这是「**程序不报错但结果可能错**」那类问题的官方登记簿。\n")
        fh.write("# kind: code = VASP 程序版本；data = **POTCAR 数据发布版**（如 PBE.64，\n")
        fh.write("#       别去查一个叫 'VASP PBE.64' 的版本号）；unknown = 未标或读不出。\n")
        fh.write("# id\treported_in\tresolved_in\tresolved_in_commit\tdate"
                 "\tstatus\tkind\ttext\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in
                               ("id", "reported_in", "resolved_in",
                                "resolved_in_commit", "date", "status",
                                "kind", "text")) + "\n")

    sel = rows
    head = "全部"
    if args.for_version:
        want = _vtuple(args.for_version)
        if want is None:
            sys.stderr.write("错误：--for-version 要写成 6.2.0 这样\n")
            return 2
        def affected(r):
            rep = _vtuple(r["reported_in"])
            res = _vtuple(r["resolved_in"])
            if rep is None:
                return False
            # 该版本 >= 首次出现；且要么没修，要么修在更晚的版本
            if want < rep:
                return False
            if res is not None and want >= res:
                return False
            return True
        sel = [r for r in rows if affected(r)]
        head = "**%s 可能受影响**" % args.for_version
    elif args.list_open:
        sel = [r for r in rows if r["status"] == "open"]
        head = "**未修（open）**"

    if args.match:
        kw = args.match.lower()
        sel = [r for r in sel if kw in r["text"].lower()
               or kw in r["reported_in"].lower()
               or kw in r["resolved_in"].lower()]
        head += " 且含 `%s`" % args.match

    print("已写出 %s" % args.out)
    print("  共解析 %d 条：open %d / fixed %d / obsolete %d"
          % (len(rows),
             sum(1 for r in rows if r["status"] == "open"),
             sum(1 for r in rows if r["status"] == "fixed"),
             sum(1 for r in rows if r["status"] == "obsolete")))
    print()
    print("=== %s：%d 条 ===" % (head, len(sel)))
    for r in sel[:args.limit]:
        tag = ("[已修 %s]" % r["resolved_in"]) if r["resolved_in"] \
            else "[**未修**]"
        print("  #%-4s 首现 %-8s %s  %s"
              % (r["id"], r["reported_in"] or "?", tag,
                 r["text"][:88]))
    if len(sel) > args.limit:
        print("  …… 还有 %d 条（用 --limit 调大）" % (len(sel) - args.limit))
    print()
    print("⚠️ 官方原话：`Below we provide an **incomplete** list of known issues.`")
    print("   ⇒ **没列出来的不代表没问题。** 本表只能当「第一道网」。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
