#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VASP Wiki 官方内容抓取 → references/official/

为什么需要它
------------
本项目的一个关键调研结论是：**VASP 没有 CP2K 那样的官方机器可读 schema
（`cp2k_input.xml`）**。但 VASP Wiki（vasp.at/wiki）是**官方**维护的，且是
MediaWiki —— 于是 `Category:INCAR_tag` 这类分类页本身就是一份**可机器枚举的
关键字全集**。这个脚本把它抓下来，作为：

1. **G 层官方权威层**（`references/official/`）的内容来源；
2. **归属校验表**（`references/official/_keywords.tsv`）的生成输入 ——
   这张表是"INCAR 关键字拼错/不存在"能被本地拦下的唯一依据。

抓什么
------
| 类别 | 用途 |
|---|---|
| `Category:INCAR_tag` | INCAR 关键字全集（含子页，如 `KERNEL_TRUNCATION/LTRUNCATE`） |
| `Category:KPOINTS_tag` | KPOINTS 关键字 |
| `Category:POSCAR_tag` / `Category:POSCAR_file` | POSCAR 相关（不常校验，作参考） |
| `Category:POTCAR` / `Category:POTCAR_tag` | POTCAR 相关 |
| 具名页 | `INCAR` `KPOINTS` `POSCAR` `POTCAR` `OUTCAR` `vasprun.xml` 等 |

输出
----
- `_sources.tsv`  每个页面的 URL / 抓取日期 / 修订号 / 字节数 / sha256（**溯源**）
- `raw/<页面名>.wiki`  **原始 wikitext，逐字保存，永不修改**（可回原文核对）
- `pages/<页面名>.md`  轻量清洗后的正文（供人读与 grep）
- `_keywords.tsv`  关键字 → 所属文件/分类/页面（归属校验表）

设计约束（照 `references/MAINTENANCE.md`）
------------------------------------------
- 站点信息（URL 前缀）由 `--api` 参数给，默认值是**官方公共地址**，不是某台机器；
- 断点续抓：`raw/` 已有同名文件就跳过，除非加 `--refresh`；
- SSL/超时**必须重试**（实测 vasp.at 会偶发 `UNEXPECTED_EOF_WHILE_READING`）；
- 抓取产物**单独一笔提交**，不要和代码改动混在一起。

依赖：只用标准库。它是"资料入库"工具，不属于面向用户的零依赖 CLI 工具链。

用法
----
    python references/official/_fetch_wiki.py --list        # 只列将抓哪些页
    python references/official/_fetch_wiki.py               # 抓取（可反复跑，续抓）
    python references/official/_fetch_wiki.py --refresh     # 忽略已抓内容重抓
    python references/official/_fetch_wiki.py --limit 20    # 先抓 20 页试水
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import random
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_API = "https://vasp.at/wiki/api.php"
UA = "vasp-skill-doc-fetcher/0.1 (+local documentation mirror; contact: skill maintainer)"

# 分类 → 归到哪个输入文件（用于生成 _keywords.tsv 的 "file" 列）
CATEGORY_TARGETS = [
    ("Category:INCAR_tag", "INCAR"),
    ("Category:KPOINTS_tag", "KPOINTS"),
    ("Category:POSCAR_tag", "POSCAR"),
    ("Category:POSCAR_file", "POSCAR"),
    ("Category:POTCAR_tag", "POTCAR"),
    ("Category:POTCAR_file", "POTCAR"),
]

# 具名总览/文件页（这些是 wiki 的骨架页，优先抓）
NAMED_PAGES = [
    "INCAR", "KPOINTS", "POSCAR", "POTCAR", "OUTCAR", "vasprun.xml",
    "Category:INCAR_tag", "Category:KPOINTS_tag", "Category:POSCAR_tag",
    "Category:POSCAR_file", "Category:POTCAR_tag", "Category:POTCAR_file",
    "Category:Input_files", "Category:Output_files", "Category:Files",
    "Category:Tutorials", "Category:Howto",
    "Calculation setup", "Electronic minimization", "Ionic minimization",
    "Molecular dynamics", "Transition states", "Band structure",
    "Density of states", "Dielectric properties", "Phonons",
    "Machine learning", "Many-body perturbation theory", "Hybrid functionals",
    "DFT+U", "Van der Waals interactions", "Spin-orbit coupling",
    "Convergence", "Accuracy", "Performance", "Parallelization",
    "Installation", "Licence", "VASP", "Makefile.include",
]

# 同名但大小写/下划线不一致时的归一
_SAFE = re.compile(r"[^0-9A-Za-z._\-]+")


def _safe_name(title: str) -> str:
    """把 MediaWiki 标题变成本地安全文件名（空格→_，其余非法字符→_）。"""
    return _SAFE.sub("_", title.replace(" ", "_"))[:150]


class Fetcher:
    def __init__(self, api: str, retries: int = 6, delay: float = 0.6, verbose: bool = False):
        self.api = api
        self.retries = retries
        self.delay = delay
        self.verbose = verbose
        self.ctx = ssl.create_default_context()
        self.n_requests = 0

    def _raw_get(self, params: dict) -> bytes:
        params = dict(params)
        params.setdefault("format", "json")
        url = self.api + "?" + urllib.parse.urlencode(params)
        last = None
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60, context=self.ctx) as resp:
                    self.n_requests += 1
                    return resp.read()
            except Exception as exc:                      # noqa: BLE001 - 全部重试
                last = exc
                sleep = self.delay * (2 ** attempt) + random.random() * 0.4
                if self.verbose:
                    sys.stderr.write("  重试 %d/%d：%s（等 %.1fs）\n"
                                     % (attempt + 1, self.retries, exc, sleep))
                time.sleep(sleep)
        raise RuntimeError("请求失败（已重试 %d 次）：%s\n  URL: %s"
                           % (self.retries, last, url))

    def get_json(self, **params) -> dict:
        return json.loads(self._raw_get(params).decode("utf-8"))

    # ---- 高层接口 -------------------------------------------------------
    def category_members(self, cat: str) -> "list[str]":
        """枚举分类成员（自动翻页）。"""
        out: "list[str]" = []
        cont = None
        while True:
            kw = dict(action="query", list="categorymembers", cmtitle=cat,
                      cmlimit="500", cmnamespace="0|14")
            if cont:
                kw["cmcontinue"] = cont
            d = self.get_json(**kw)
            out.extend(m["title"] for m in d.get("query", {}).get("categorymembers", []))
            cont = d.get("continue", {}).get("cmcontinue")
            if not cont:
                break
            time.sleep(self.delay)
        return out

    def fetch_pages(self, titles: "list[str]", batch: int = 40) -> "dict[str, dict]":
        """用 revisions+content 批量取 wikitext（比逐页取快一个量级）。"""
        pages: "dict[str, dict]" = {}
        for i in range(0, len(titles), batch):
            chunk = titles[i:i + batch]
            d = self.get_json(action="query", prop="revisions|info",
                              rvprop="content|timestamp|ids", rvslots="main",
                              titles="|".join(chunk), redirects="1")
            for pid, page in d.get("query", {}).get("pages", {}).items():
                title = page.get("title")
                if not title or "missing" in page:
                    pages[title or ("?#" + pid)] = {"missing": True}
                    continue
                rev = (page.get("revisions") or [{}])[0]
                slots = rev.get("slots", {}).get("main", {})
                pages[title] = {
                    "revid": rev.get("revid"),
                    "timestamp": rev.get("timestamp"),
                    "content": slots.get("content", slots.get("*", "")),
                }
            sys.stderr.write("  已取 %d/%d 页\n" % (min(i + batch, len(titles)), len(titles)))
            time.sleep(self.delay)
        return pages


# ---------------------------------------------------------------------------
# wikitext → 轻量 markdown（**只做结构性清洗，不改写文字**）
# ---------------------------------------------------------------------------
def wikitext_to_md(text: str) -> str:
    if not text:
        return ""
    s = text
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*?/>", "", s)
    s = re.sub(r"<ref[^>]*?>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"</?(?:div|span|p|br|small|big|center|blockquote|sup|sub|code|tt|nowiki|pre|gallery|math|chem|syntaxhighlight)[^>]*?>",
               "", s, flags=re.I)
    # 表格 → 保留为单元格行（不渲染成 markdown 表，避免引入错误结构）
    s = re.sub(r"^\s*\{\|.*$", "", s, flags=re.M)
    s = re.sub(r"^\s*\|\}", "", s, flags=re.M)
    s = re.sub(r"^\s*\|[-+].*$", "", s, flags=re.M)
    s = re.sub(r"^\s*[!|]\s*", "  ", s, flags=re.M)
    # 标题
    s = re.sub(r"^\s*======\s*(.+?)\s*======\s*$", r"###### \1", s, flags=re.M)
    s = re.sub(r"^\s*=====\s*(.+?)\s*=====\s*$", r"##### \1", s, flags=re.M)
    s = re.sub(r"^\s*====\s*(.+?)\s*====\s*$", r"#### \1", s, flags=re.M)
    s = re.sub(r"^\s*===\s*(.+?)\s*===\s*$", r"### \1", s, flags=re.M)
    s = re.sub(r"^\s*==\s*(.+?)\s*==\s*$", r"## \1", s, flags=re.M)
    # 链接：[[A|B]] → B ; [[A]] → A ; 外链 [U T] → T (U)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]|]+)\]\]", r"\1", s)
    s = re.sub(r"\[(https?://\S+)\s+([^\]]+)\]", r"\2 (\1)", s)
    s = re.sub(r"\[(https?://\S+)\]", r"\1", s)
    s = re.sub(r"'''''(.+?)'''''", r"**\1**", s)
    s = re.sub(r"'''(.+?)'''", r"**\1**", s)
    s = re.sub(r"''(.+?)''", r"*\1*", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip() + "\n"


def parse_values_from_wikitext(text: str) -> "list[str]":
    """从 wikitext 里尽力抽取"可选值"列表。

    这是**尽力而为**的启发式，不是权威解析：VASP wiki 的取值一般写在正文或
    `{{TAG|...}}` 模板里，格式并不统一。抽不到就返回空表 —— **空表表示
    "本工具没抽到"，不表示"该关键字没有取值"**。不要在文档里把空表说成"无参数"。
    """
    vals: "list[str]" = []
    for m in re.finditer(r"^\s*[#*:;]\s*([A-Za-z0-9_.\-]+)\s*[:：]", text, flags=re.M):
        vals.append(m.group(1))
    return sorted(set(vals))


def first_paragraph(text: str, limit: int = 400) -> str:
    body = re.sub(r"^\s*\{\{[^}]*\}\}\s*$", "", text, flags=re.M)
    body = re.sub(r"^\s*\[\[Category:[^\]]*\]\]\s*$", "", body, flags=re.M)
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p.startswith(("{{", "|", "==", "__")):
            continue
        p = wikitext_to_md(p).strip().replace("\n", " ")
        if len(p) > 20:
            return p[:limit]
    return ""


def main(argv: "list[str] | None" = None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(
        prog="_fetch_wiki.py",
        description="VASP Wiki 官方内容抓取（生成 references/official/ 与归属校验表）",
    )
    ap.add_argument("--api", default=os.environ.get("VASP_WIKI_API", DEFAULT_API),
                    help="MediaWiki api.php 地址（默认官方公共地址）")
    ap.add_argument("--out", default=here, help="输出目录（默认本脚本所在目录）")
    ap.add_argument("--list", action="store_true", help="只列出将抓取哪些页面")
    ap.add_argument("--refresh", action="store_true", help="忽略本地已有 raw 文件，重抓")
    ap.add_argument("--limit", type=int, default=0, help="最多抓多少页（0=不限）")
    ap.add_argument("--no-categories", action="store_true",
                    help="不展开分类，只抓 --named 页（快速试水用）")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    raw_dir = os.path.join(args.out, "raw")
    page_dir = os.path.join(args.out, "pages")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(page_dir, exist_ok=True)

    f = Fetcher(args.api, verbose=args.verbose)

    print("== 1/4 枚举官方分类 ==")
    keyword_rows: "list[tuple[str, str, str]]" = []   # (keyword, file, page)
    cat_members: "dict[str, list[str]]" = {}
    for cat, target in CATEGORY_TARGETS:
        try:
            members = f.category_members(cat)
        except Exception as exc:                       # noqa: BLE001
            sys.stderr.write("  警告：分类 %s 枚举失败：%s\n" % (cat, exc))
            members = []
        cat_members[cat] = members
        print("  %-28s %4d 个成员  → %s" % (cat, len(members), target))
        for m in members:
            title = m.split(":", 1)[1] if m.startswith("Category:") else m
            keyword_rows.append((title, target, cat))

    titles: "list[str]" = list(NAMED_PAGES)
    if not args.no_categories:
        for members in cat_members.values():
            titles.extend(members)
    # 去重、保序
    seen = set()
    uniq = []
    for t in titles:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    titles = uniq
    if args.limit:
        titles = titles[:args.limit]

    print("\n== 2/4 计划抓取 %d 个页面 ==" % len(titles))
    if args.list:
        for t in titles:
            print("  " + t)
        return 0

    print("\n== 3/4 抓取 wikitext ==")
    # 断点续抓：先按批请求，已有本地 raw 的页面从结果里剔除后再请求
    todo = []
    for t in titles:
        p = os.path.join(raw_dir, _safe_name(t) + ".wiki")
        if args.refresh or not os.path.exists(p):
            todo.append(t)
    print("  需抓取 %d 页（已缓存 %d 页）" % (len(todo), len(titles) - len(todo)))

    fetched: "dict[str, dict]" = {}
    if todo:
        fetched = f.fetch_pages(todo)

    print("\n== 4/4 写出 raw / pages / _sources / _keywords ==")
    sources = []
    today = _dt.date.today().isoformat()
    n_missing = 0
    for t in titles:
        safe = _safe_name(t)
        raw_path = os.path.join(raw_dir, safe + ".wiki")
        info = fetched.get(t)
        if info is None:
            if os.path.exists(raw_path):
                content = open(raw_path, encoding="utf-8").read()
                info = {"content": content, "revid": None, "timestamp": None,
                        "cached": True}
            else:
                info = {"missing": True}
        if info.get("missing"):
            n_missing += 1
            sources.append((t, "MISSING", today, "", 0, ""))
            continue
        content = info.get("content", "")
        if not args.refresh or t in fetched:
            with open(raw_path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        url = ("https://vasp.at/wiki/index.php/" +
               urllib.parse.quote(t.replace(" ", "_")))
        sources.append((t, url, today, info.get("timestamp") or "",
                        len(content.encode("utf-8")), sha))
        with open(os.path.join(page_dir, safe + ".md"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write(wikitext_to_md(content))

    with open(os.path.join(args.out, "_sources.tsv"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("# title\turl\tfetched\trevision_ts\tbytes\tsha256\n")
        for row in sources:
            fh.write("\t".join(str(x) for x in row) + "\n")

    # 归属校验表：只收 namespace 0 的关键字页
    kw_seen = set()
    with open(os.path.join(args.out, "_keywords.tsv"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("# keyword\tfile\tcategory\tsummary\n")
        for keyword, target, cat in sorted(keyword_rows):
            key = (keyword, target)
            if key in kw_seen:
                continue
            kw_seen.add(key)
            safe = _safe_name(keyword)
            wp = os.path.join(raw_dir, safe + ".wiki")
            summary = ""
            if os.path.exists(wp):
                summary = first_paragraph(open(wp, encoding="utf-8").read())
            summary = summary.replace("\t", " ").replace("\n", " ")[:300]
            fh.write("%s\t%s\t%s\t%s\n" % (keyword, target, cat, summary))

    print("  页面 %d 个（其中 %d 个不存在/404），关键字表 %d 行"
          % (len(titles), n_missing, len(kw_seen)))
    print("  写出：%s" % args.out)
    print("  提示：抓取产物请**单独一笔提交**，并在 references/official/README.md 登记。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
