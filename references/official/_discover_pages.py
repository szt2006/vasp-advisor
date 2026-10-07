#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐 `_fetch_wiki.py` 第一轮没抓到的页面（分类页与主题页）。

为什么需要它
------------
第一轮抓取时，`NAMED_PAGES` 里的 `Category:INCAR_tag`、`Transition states`、
`Convergence` 等页面被 API 报成 `missing`。实测原因是**页面名不对**而不是页面不存在：
MediaWiki 的分类页与主题页在本站的命名和常识写法有出入
（例如 "Transition states" 实际不存在，但别的写法存在）。

这个脚本做两件事：
1. 用 `list=allcategories` **枚举全站所有分类名**，避免靠猜；
2. 用 `list=allpages` 按前缀枚举，找主题页的正确名字。

它**只做发现与补齐**，不改 `_fetch_wiki.py` 的逻辑。跑完之后重跑
`_fetch_wiki.py` 会跳过已缓存页面，因此两条命令可以反复跑。

用法
----
    python references/official/_discover_pages.py            # 只报告发现了什么
    python references/official/_discover_pages.py --fetch    # 顺便把发现的页面抓下来
"""

from __future__ import annotations

import argparse
import json
import os
import random
import ssl
import sys
import time
import urllib.parse
import urllib.request

DEFAULT_API = "https://vasp.at/wiki/api.php"
UA = "vasp-skill-doc-fetcher/0.1 (+local documentation mirror)"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _fetch_wiki import Fetcher, _safe_name, wikitext_to_md, first_paragraph  # noqa: E402

# 我们**想**覆盖的主题（用关键词匹配 allcategories / allpages 的结果）
WANTED_CATEGORY_HINTS = (
    "incar", "kpoints", "poscar", "potcar", "input", "output", "file",
    "convergence", "accuracy", "minimization", "minimisation", "dynamics",
    "transition", "band", "density of states", "dos", "hybrid", "dft+u",
    "van der waals", "vdw", "spin", "symmetry", "phonon", "dielectric",
    "performance", "parallel", "install", "tutorial", "howto", "example",
    "electronic", "ionic", "structure", "charge", "potential", "magnet",
    "machine learning", "many-body", "occupancy", "k-point",
)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_discover_pages.py",
        description="发现并补齐 VASP wiki 的分类页与主题页",
    )
    ap.add_argument("--api", default=os.environ.get("VASP_WIKI_API", DEFAULT_API))
    ap.add_argument("--fetch", action="store_true", help="顺便抓取发现的页面")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    f = Fetcher(args.api, verbose=args.verbose)

    print("== 1/3 枚举全站分类 ==")
    cats = []
    cont = None
    while True:
        kw = dict(action="query", list="allcategories", aclimit="500")
        if cont:
            kw["accontinue"] = cont
        d = f.get_json(**kw)
        cats.extend(c["*"] for c in d.get("query", {}).get("allcategories", []))
        cont = d.get("continue", {}).get("accontinue")
        if not cont:
            break
        time.sleep(0.4)
    print("  全站分类共 %d 个" % len(cats))

    hit_cats = [c for c in cats
                if any(h in c.lower() for h in WANTED_CATEGORY_HINTS)]
    print("  与 VASP 输入/输出/方法相关的分类 %d 个：" % len(hit_cats))
    for c in sorted(hit_cats):
        print("    Category:%s" % c)

    print("\n== 2/3 找主题页（namespace 0，非标签页）==")
    # ⚠️ 两个实测教训（都记进 CHANGELOG）：
    #  ① MediaWiki 把 `Category:X_tag` 规范化成 `Category:X tag`（**空格**不是下划线**），
    #     所以分类名一律用空格写。
    #  ② **一次别问太多标题** —— 70 个候选拼成一条 URL 会被服务器直接断连
    #     （SSL UNEXPECTED_EOF）。改成每批 10 个。
    candidates = [
        "Transition states", "Transition state", "Nudged elastic band",
        "Convergence", "Converging", "Accuracy", "Electronic minimization",
        "Electronic minimisation", "Ionic minimization", "Ionic minimisation",
        "Molecular dynamics", "Structure optimization", "Structure optimisation",
        "Band structure", "Band-structure calculation",
        "Density of states", "DOSCAR", "Dielectric properties", "Phonons",
        "Phonon", "Hybrid functionals", "DFT+U", "DFT+U calculations",
        "Van der Waals interactions", "Van der Waals functionals",
        "Van der Waals", "Spin-orbit coupling", "Performance",
        "Parallelization", "Installation", "Licence", "License", "VASP",
        "Input file", "Output file", "Charged systems", "Potential",
        "Electrostatic potential", "Work function", "Bader",
        "Bader charge analysis", "Charge density difference",
        "Machine learning", "Many-body perturbation theory", "Calculations",
        "Tutorials", "Howto", "Smearing technique", "K-point integration",
        "Category:Howto", "Category:Tutorials", "Category:Examples",
        "Category:Convergence", "Category:Electronic minimization",
        "Category:Ionic minimization", "Category:Molecular dynamics",
        "Category:Transition states", "Category:Input files",
        "Category:Output files", "Category:How-to", "Category:VASP",
        "Category:Electronic occupancy", "Category:Density of states",
        "Category:Forces", "Category:Symmetry", "Category:Phonons",
        "Category:Hybrid functionals", "Category:DFT+U",
        "Category:Van der Waals functionals", "Category:Parallelization",
        "Category:Performance", "Category:Potential",
        "Category:Charge density", "Category:Magnetism",
        "Category:Band structure", "Category:Files",
        "Category:Electronic ground-state properties",
        "Category:Elastic band method", "Category:Pseudopotentials",
        "Category:Installation", "Category:Output Files",
    ]
    exists, redir = [], {}
    for i in range(0, len(candidates), 10):
        batch = candidates[i:i + 10]
        d = f.get_json(action="query", prop="info",
                       titles="|".join(batch), redirects="1")
        for r in d.get("query", {}).get("redirects", []):
            redir[r["from"]] = r["to"]
        for pid, p in d.get("query", {}).get("pages", {}).items():
            t = p.get("title", "?#" + pid)
            if "missing" not in p:
                exists.append(t)
        time.sleep(0.3)
    print("  存在（含重定向目标）的页面 %d 个：" % len(set(exists)))
    for t in sorted(set(exists)):
        print("    %s" % t)
    if redir:
        print("  重定向：")
        for a, b in sorted(redir.items()):
            print("    %s → %s" % (a, b))

    if not args.fetch:
        print("\n（加 --fetch 可把这些页面抓下来）")
        return 0

    print("\n== 3/3 抓取（只抓本地还没有的）==")
    raw_dir = os.path.join(HERE, "raw")
    page_dir = os.path.join(HERE, "pages")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(page_dir, exist_ok=True)
    todo = [t for t in sorted(set(exists))
            if not os.path.exists(os.path.join(raw_dir, _safe_name(t) + ".wiki"))]
    todo += ["Category:" + c for c in hit_cats
             if not os.path.exists(os.path.join(raw_dir, "Category_" + c + ".wiki"))]
    print("  需抓取 %d 页" % len(todo))
    if todo:
        got = f.fetch_pages(todo)
        add = []
        for t, info in got.items():
            if info.get("missing"):
                continue
            content = info.get("content", "")
            with open(os.path.join(raw_dir, _safe_name(t) + ".wiki"), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(content)
            with open(os.path.join(page_dir, _safe_name(t) + ".md"), "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(wikitext_to_md(content))
            add.append((t, info.get("revid"), info.get("timestamp"), len(content)))
        print("  新增 %d 页" % len(add))
        # 追加登记到 _sources.tsv（**不覆盖**原文件，只 append 并标注来源轮次）
        import hashlib
        import datetime as dt
        with open(os.path.join(HERE, "_sources_round2.tsv"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("# title\turl\tfetched\tbytes\tsha256\n")
            today = dt.date.today().isoformat()
            for t, _rev, _ts, n in sorted(add):
                p = os.path.join(raw_dir, _safe_name(t) + ".wiki")
                sha = hashlib.sha256(open(p, encoding="utf-8")
                                     .read().encode("utf-8")).hexdigest()
                url = ("https://vasp.at/wiki/index.php/"
                       + urllib.parse.quote(t.replace(" ", "_")))
                fh.write("%s\t%s\t%s\t%d\t%s\n" % (t, url, today, n, sha))
        print("  溯源写入 _sources_round2.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
