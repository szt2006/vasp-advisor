#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按**显式标题**补抓官方 wiki 页面（补齐分类枚举漏掉的主题页）。

为什么需要它
------------
`_fetch_wiki.py` 靠 `Category:INCAR tag` 等分类页枚举标签页，
`_discover_pages.py` 靠一份候选名单探测主题页。
两者**都会漏**：官方有一些"how-to 主题页"既不在标签分类里，
也不在那份候选名单里 —— 但它们是**官方明文**，
而且有些恰好给出了**别处查不到的判据**。

实测踩到的例子（本项目引入 LVTHW 资料时发现）：
- `Smearing technique` —— ISMEAR 页正文里链接了它，本地却没有。
  它给出了 ISMEAR 页**没写**的两条关键判据：
  ①四面体方法"**at least 4 k points**"；②金属的熵项"**< 1 meV/atom**"。
- `K-point integration` —— ISMEAR 页"Related tags"里列了它。
- `DOSCAR` —— 输出文件页，讲列语义（正是本项目反复要引的那件事）。

所以本脚本提供一个**显式补抓**入口：给标题就抓，带溯源、可反复跑。

设计
----
- **复用** `_fetch_wiki.py` 的 `Fetcher` / `wikitext_to_md`（避免两份实现）；
- 已存在的页面**不覆盖**，除非 `--refresh`；
- 追加登记到 `_sources_round3.tsv`（**不覆盖** `_sources.tsv`；
  "哪一轮抓的"是有用信息，见 `MAINTENANCE.md` 的"抓取产物单独一笔提交"）；
- 站点信息（API 地址）由参数给，默认是**官方公共地址**。

用法
----
    python references/official/_fetch_named.py                  # 抓内置清单
    python references/official/_fetch_named.py --title "DOSCAR"
    python references/official/_fetch_named.py --list
    python references/official/_fetch_named.py --refresh
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _fetch_wiki import (Fetcher, _safe_name, wikitext_to_md,  # noqa: E402
                         DEFAULT_API)

# 内置的"已知缺失、且有用"的页面。
# ⚠️ 加条目时**写清理由** —— 否则这份清单会变成杂物箱。
WANTED = [
    ("Smearing technique",
     "ISMEAR 页正文链接的 how-to 主题页。给出别处没有的判据："
     "四面体方法『at least 4 k points』、金属熵项『< 1 meV/atom』、"
     "未知体系起步用 Gaussian SIGMA=0.1。"),
    ("K-point integration",
     "ISMEAR/KPOINTS 页『Related tags』里列的**理论页** —— "
     "讲 k 点积分方法的原理（为什么展宽与四面体各适合什么）。"),
    ("DOSCAR",
     "输出文件页：**DOSCAR 的列语义**（`ISPIN=1` 三列 / `ISPIN=2` 五列）。"
     "本项目反复要引它，之前只在外部链接里提过，没镜像。"),
    ("Smearing",
     "可能存在的重定向/短名页；抓到就登记，404 就如实跳过。"),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_fetch_named.py",
        description="按显式标题补抓官方 wiki 页面（带溯源，可反复跑）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法\n----", 1)[-1].strip(),
    )
    ap.add_argument("--title", action="append", default=[],
                    help="要抓的页面标题，可重复；不给则用内置清单")
    ap.add_argument("--api", default=os.environ.get("VASP_WIKI_API", DEFAULT_API))
    ap.add_argument("--list", action="store_true", help="只列标题")
    ap.add_argument("--refresh", action="store_true", help="已存在的也重抓")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    titles = args.title if args.title else [t for t, _why in WANTED]
    if args.list:
        print("内置补抓清单：\n")
        for t, why in WANTED:
            print("  %-26s %s" % (t, why))
        return 0

    raw_dir = os.path.join(HERE, "raw")
    page_dir = os.path.join(HERE, "pages")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(page_dir, exist_ok=True)

    todo = [t for t in titles
            if args.refresh
            or not os.path.exists(os.path.join(raw_dir, _safe_name(t) + ".wiki"))]
    print("计划 %d 页，其中需抓取 %d 页" % (len(titles), len(todo)))

    f = Fetcher(args.api, verbose=args.verbose)
    got = f.fetch_pages(todo) if todo else {}

    today = _dt.date.today().isoformat()
    rows, n_missing = [], 0
    for t in titles:
        safe = _safe_name(t)
        raw_path = os.path.join(raw_dir, safe + ".wiki")
        page_path = os.path.join(page_dir, safe + ".md")
        info = got.get(t)
        if info is None:
            if os.path.exists(raw_path):
                content = open(raw_path, encoding="utf-8").read()
                rows.append((t, "cached", today, len(content.encode("utf-8"))))
                continue
            info = {"missing": True}
        if info.get("missing"):
            n_missing += 1
            rows.append((t, "MISSING", today, 0))
            print("  ⚠️ %-26s 404 / 不存在（如实登记，不编造）" % t)
            continue
        content = info.get("content", "")
        with open(raw_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        with open(page_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(wikitext_to_md(content))
        rows.append((t, "OK", today, len(content.encode("utf-8"))))
        print("  ✓ %-26s %6d 字节 wikitext → pages/%s.md"
              % (t, len(content.encode("utf-8")), safe))

    out_tsv = os.path.join(HERE, "_sources_round3.tsv")
    with open(out_tsv, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# title\tstatus\tfetched\tbytes_wikitext\tsha256\n")
        for t, status, when, nbytes in rows:
            raw_path = os.path.join(raw_dir, _safe_name(t) + ".wiki")
            sha = ""
            if os.path.exists(raw_path):
                sha = hashlib.sha256(
                    open(raw_path, "rb").read()).hexdigest()
            fh.write("%s\t%s\t%s\t%d\t%s\n" % (t, status, when, nbytes, sha))

    print()
    print("溯源写入 %s（**不覆盖** _sources.tsv —— 「哪一轮抓的」是有用信息）"
          % os.path.basename(out_tsv))
    print("其中不存在/404：%d 页（已如实登记，**没有编造**）" % n_missing)
    print()
    print("⚠️ 抓取产物请**单独一笔提交**（700+ 文件不该和代码改动混在一起）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
