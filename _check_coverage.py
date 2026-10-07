#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_check_coverage.py —— 分段表覆盖性核查（**"真的读完了"的客观证据**）

为什么需要它
============
本项目对精读报告有两条**机器可验**的要求（见 `references/MAINTENANCE.md` §Phase 2）：

1. **页覆盖清单** —— 逐页/逐篇列出，确认无遗漏；
2. **主题分段表** —— 行区间必须**连续覆盖全文、无重叠、无空档**。

> 这两条是"是否真的逐行读完"的**唯一客观证据**。
> 没有它们，"我读完了"就只是一句声明 —— 而声明无法被证伪。

CP2K skill 的历史教训：某轮综合稿写了"所有【新】标记项已落入本库"，
复核发现多条**零命中** —— **声明是假的，而且当时无人能证伪**。

本脚本把这条从"声明"变成"断言"。

核查对象
========
| 家族 | 分段表 | 正文 | 标记 |
|---|---|---|---|
| 讲义 | `references/raw/seg_L*.tsv` | `references/raw/L*.txt` | `========== PAGE N ==========` |
| LVTHW | `references/raw/lvthw/seg_G*.tsv` | `references/raw/lvthw/<ID>.txt` | 每篇一个文件 |

`seg_*.tsv` 的格式约定：**制表符分隔**，
- 讲义：`起始行  结束行  主题  要点`（4 列）
- LVTHW：`post_id  起始行  结束行  主题  要点`（5 列）

核查什么
========
对每个 (分段表, 正文) 对：
1. **行号合法**：`起 ≥ 1`、`止 ≥ 起`、`止 ≤ 该正文的实际行数`；
2. **连续无空档**：按行号排序后，`下一段的起 == 上一段的止 + 1`；
3. **无重叠**：同上（相等即重叠）；
4. **完整覆盖**：第一段从第 1 行起，最后一段到末行止；
5. **篇/页标记齐全**（LVTHW 额外查）：`_GROUPS.tsv` 里列的每一篇，
   都必须**至少出现在分段表里一次**。

**不查什么**（诚实说明）
------------------------
- 不查"主题写得对不对""要点是否抓住了原文" —— 那是内容质量，机器判不了；
- 不查"分段粒度是否合理" —— 一段覆盖 200 行不算错，只是粗。
  本脚本会**报告粒度统计**供人判断。

用法
----
    python _check_coverage.py
    python _check_coverage.py --family lvthw
    python _check_coverage.py --tsv references/raw/lvthw/seg_G6.tsv
    python _check_coverage.py --json

退出码
------
0 = 全部通过 · 1 = 有覆盖问题 · 2 = 用法错误
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))

EXIT_OK, EXIT_BAD, EXIT_USAGE = 0, 1, 2

RAW = os.path.join(ROOT, "references", "raw")
LVTHW = os.path.join(RAW, "lvthw")


def _nlines(path: str) -> int:
    """正文的**权威行数**。

    ⚠️ **必须是"物理行数"，不能是 `len(text.split("\\n"))`。**
    这是本项目踩过的一个真坑（见 `CHANGELOG.md` 的 CR-025）：

    - 我们的抽取文件**以 `\\n` 结尾**（这是 LF 行尾的规范做法）；
    - 于是 `text.split("\\n")` 会多出**一个末尾空串** ⇒ 比真实行数 **+1**；
    - 而 `for line in fh`、`str.splitlines()`、`wc -l` 都给同一个数（真实行数）。

    `_audit_citations.py` 与 `references/raw/extract_lvthw.py` 用的都是
    "`for line in fh`" 这一种。**三处必须一致**，否则：
    - 审计会说"你引到了第 172 行，文件只有 171 行"；
    - 覆盖核查会说"止行 172 超过总行数 171"；
    而分段表作者其实是按"含末尾空行"数的 —— 两边都没错，是**口径没统一**。

    ⇒ 本函数统一用 `for line in fh` 计数。
    """
    n = 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for _ in fh:
                n += 1
    except OSError:
        return 0
    return n


def _read_tsv(path: str):
    """读分段表，返回 (rows, ncols)。rows = [(key, start, end, topic, note)]。"""
    rows = []
    ncols = 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            t = [x.strip() for x in line.rstrip("\n").split("\t")]
            if not rows:
                ncols = len(t)
            if len(t) == 4:                      # 讲义：起 止 主题 要点
                try:
                    rows.append(("", int(t[0]), int(t[1]), t[2], t[3]))
                except ValueError:
                    continue
            elif len(t) >= 5:                    # LVTHW：篇 起 止 主题 要点
                try:
                    rows.append((t[0], int(t[1]), int(t[2]), t[3], t[4]))
                except ValueError:
                    continue
    return rows, ncols


def check_lecture(tsv: str):
    """讲义分段表：一个文件覆盖一份 L*.txt。"""
    base = os.path.basename(tsv)
    m = re.match(r"seg_(L\d+)\.tsv$", base)
    if not m:
        return None
    tag = m.group(1)
    doc = os.path.join(RAW, "%s.txt" % tag)
    if not os.path.exists(doc):
        return {"name": base, "ok": False,
                "problems": ["正文 %s.txt 不存在" % tag], "stats": {}}
    total = _nlines(doc)
    rows, _ = _read_tsv(tsv)
    return _judge(base, tag, total, rows)


def check_lvthw(tsv: str):
    """LVTHW 分段表：一个文件按篇覆盖多个 <ID>.txt。"""
    base = os.path.basename(tsv)
    rows, _ = _read_tsv(tsv)
    problems = []
    per_post = {}
    for pid, a, b, _t, _n in rows:
        per_post.setdefault(pid, []).append((a, b))
    stats = {"posts": len(per_post), "segments": len(rows)}
    # 每篇单独判连续性
    for pid, spans in sorted(per_post.items()):
        doc = os.path.join(LVTHW, "%s.txt" % pid)
        if not os.path.exists(doc):
            problems.append("%s：正文 %s.txt 不存在" % (base, pid))
            continue
        total = _nlines(doc)
        p = _contiguity(spans, total)
        for x in p:
            problems.append("%s / %s：%s" % (base, pid, x))
    # 覆盖完整性：**只看本组该覆盖的篇**。
    #
    # ⚠️ 这里必须读 `_GROUPS.tsv` 里**本组那一行**，不能把全部分组并起来。
    # 早期版本把 `_GROUPS.tsv` 里所有篇都当成"应当出现在本表"，
    # 于是 `seg_G3.tsv`（只该覆盖 6 篇 DOS）被判"缺 126 篇" ——
    # 那不是分段表的问题，是**核查器的逻辑错了**。
    # 教训同 CR-018/023/024：**假红会让人学会忽略整个核查。**
    want = set()
    groups = os.path.join(LVTHW, "_GROUPS.tsv")
    if os.path.exists(groups):
        with open(groups, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                t = line.rstrip("\n").split("\t")
                if len(t) < 2:
                    continue
                members = [x.strip() for x in t[1].split() if x.strip()]
                # 本表覆盖了这组的哪些篇？取交集最多的那一组作为"本组"
                if set(members) & set(per_post):
                    want |= set(members)
    missing = sorted(want - set(per_post))
    if missing:
        problems.append("%s：本组还有这些篇没出现在分段表里：%s"
                        % (base, ", ".join(missing)))
    stats["expected_posts"] = len(want)
    return {"name": base, "ok": not problems, "problems": problems,
            "stats": stats}


def _contiguity(spans, total: int):
    """判一组 (起,止) 是否连续覆盖 1..total。返回问题列表。"""
    problems = []
    spans = sorted(spans)
    if not spans:
        return ["没有任何分段"]
    for a, b in spans:
        if a < 1:
            problems.append("起始行 %d < 1" % a)
        if b < a:
            problems.append("止行 %d < 起行 %d" % (b, a))
        if total and b > total:
            problems.append("止行 %d 超过正文总行数 %d" % (b, total))
    if problems:
        return problems
    if spans[0][0] != 1:
        problems.append("未从第 1 行开始（首段起于 %d）" % spans[0][0])
    if total and spans[-1][1] != total:
        problems.append("未覆盖到末行（末段止于 %d，正文共 %d 行）"
                        % (spans[-1][1], total))
    for i in range(1, len(spans)):
        prev_end = spans[i - 1][1]
        cur_start = spans[i][0]
        if cur_start == prev_end:
            problems.append("第 %d 段与上一段在行 %d 处**重叠**"
                            % (i + 1, cur_start))
        elif cur_start > prev_end + 1:
            problems.append("行 %d..%d 之间**有空档**（%d 行未被覆盖）"
                            % (prev_end + 1, cur_start - 1,
                               cur_start - prev_end - 1))
    return problems


def _judge(name: str, tag: str, total: int, rows) -> dict:
    spans = [(a, b) for _k, a, b, _t, _n in rows]
    problems = _contiguity(spans, total)
    lens = [b - a + 1 for a, b in spans] or [0]
    return {"name": name, "ok": not problems, "problems": problems,
            "stats": {"doc": tag, "doc_lines": total, "segments": len(spans),
                      "avg_span": round(sum(lens) / len(lens), 1),
                      "max_span": max(lens)}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_check_coverage.py",
        description="分段表覆盖性核查（连续 / 无重叠 / 无空档 / 完整覆盖）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=全部通过；1=有覆盖问题；2=用法错误。\n"
               "⚠️ 它只查**覆盖性**，不查内容质量（主题写得对不对、要点抓没抓住）。",
    )
    ap.add_argument("--family", choices=["lecture", "lvthw"],
                    help="只查某一族")
    ap.add_argument("--tsv", help="只查这一个分段表")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    targets = []
    if args.tsv:
        if not os.path.exists(args.tsv):
            sys.stderr.write("错误：文件不存在：%s\n" % args.tsv)
            return EXIT_USAGE
        base = os.path.basename(args.tsv)
        if base.startswith("seg_L"):
            targets.append(("lecture", args.tsv))
        else:
            targets.append(("lvthw", args.tsv))
    else:
        if args.family in (None, "lecture"):
            if os.path.isdir(RAW):
                for f in sorted(os.listdir(RAW)):
                    if re.match(r"seg_L\d+\.tsv$", f):
                        targets.append(("lecture", os.path.join(RAW, f)))
        if args.family in (None, "lvthw"):
            if os.path.isdir(LVTHW):
                for f in sorted(os.listdir(LVTHW)):
                    if re.match(r"seg_G\d+\.tsv$", f):
                        targets.append(("lvthw", os.path.join(LVTHW, f)))

    if not targets:
        sys.stderr.write("错误：没找到任何 seg_*.tsv。\n"
                         "  讲义分段表在 references/raw/，"
                         "LVTHW 分段表在 references/raw/lvthw/。\n")
        return EXIT_USAGE

    results = []
    for kind, path in targets:
        r = (check_lecture(path) if kind == "lecture" else check_lvthw(path))
        if r:
            r["family"] = kind
            results.append(r)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return EXIT_BAD if any(not r["ok"] for r in results) else EXIT_OK

    if not args.quiet:
        print("=" * 72)
        print("分段表覆盖性核查 —— “真的读完了”的客观证据")
        print("=" * 72)
        print("查了 %d 张分段表。\n" % len(results))

    n_bad = 0
    for r in results:
        st = r["stats"]
        if r["ok"]:
            if not args.quiet:
                extra = ""
                if "doc_lines" in st:
                    extra = ("正文 %d 行 / %d 段 / 平均 %.1f 行每段 / 最长 %d 行"
                             % (st["doc_lines"], st["segments"],
                                st.get("avg_span", 0), st.get("max_span", 0)))
                else:
                    extra = ("%d 篇 / %d 段（_GROUPS 里列了 %d 篇，全部出现）"
                             % (st.get("posts", 0), st.get("segments", 0),
                                st.get("expected_posts", 0)))
                print("  ✓ %-16s %s" % (r["name"], extra))
        else:
            n_bad += 1
            print("  ✗ %-16s **%d 个问题**" % (r["name"], len(r["problems"])))
            for p in r["problems"][:25]:
                print("        · %s" % p)
            if len(r["problems"]) > 25:
                print("        …… 还有 %d 条" % (len(r["problems"]) - 25))

    if not args.quiet:
        print()
        print("-" * 72)
        if n_bad:
            print("结论：**%d 张分段表未通过**。" % n_bad)
        else:
            print("结论：全部 %d 张分段表都连续覆盖、无重叠、无空档。"
                  % len(results))
        print()
        print("⚠️ 本检查**只查覆盖性**：")
        print("   · 它证明“行区间没漏”，**不证明**“内容读懂了”；")
        print("   · 它不查主题写得对不对、要点抓没抓住 —— 那是内容质量，机器判不了；")
        print("   · 粒度过粗（一段覆盖几百行）不算错，只是粗 —— 上面的“最长”列供你判断。")
    return EXIT_BAD if n_bad else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
