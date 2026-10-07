#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_audit_citations.py —— 引用审计（**守住本 skill 唯一的价值主张：可回溯**）

它查什么
========
把 `references/` 与根目录下所有 Markdown 里出现的引用抽出来，逐条断言
**指向真实存在的页/段/文件**。越界即报红。

| 引用形态 | 断言 |
|---|---|
| `L1 P28` | `references/raw/L1.txt` 存在，且其中 `========== PAGE 28 ==========` 存在，且 28 ≤ 该文件实际页数 |
| `D2-P14` | `references/raw/D2.txt` 存在，且 `========== D2-P14 ==========` 存在，且 14 ≤ 实际段数 |
| `references/official/pages/ISMEAR.md` | 该文件存在 |
| `references/decide.md` §14 等 | 该文件存在（**不校验 § 号** —— 见下面的能力边界） |
| `scripts/validate.py:120` | 文件存在，且行号 ≤ 该文件实际行数 |

⚠️ **它查不出什么（必须如实传播，否则会给人假的安心）**
=====================================================
1. **查不出"行号没越界、但指向了别的内容"**。文件被改写后行号会**语义漂移**。
   （CP2K skill 实测过：某处引 `course_learned.md:650–651` 讲 SHE 常数，
   而该行已移位到 Au20 建模。）
   ⇒ 引用行号密集的文件时，**引之前先 grep 一次确认指向的内容对得上**。
2. **不校验 `§` 号**。Markdown 没有章节锚点的机器可读表示，
   靠正则抽 `§14` 再回文件里找标题是不可靠的（标题写法会变）。
   ⇒ 本工具只校验"文件存在"。`§` 号的正确性靠人。
3. **不校验引用的"内容是否正确"**。它只查**存在性**，不查**语义**。
4. **不校验 `things to study/` 下的路径**（那批资料不在仓库里）。

设计要点
========
- **举例用的"坏写法"要被天然跳过**：页号写成 `L1 P##` 占位形式，
  正则只认 `L` 后跟数字，所以 `##` 不会被当真引用。
- 只读**本地仓库**，不联网。

用法
----
    python _audit_citations.py            # 审全仓库
    python _audit_citations.py --verbose  # 连通过项也逐条列出
    python _audit_citations.py --file references/decide.md
    python _audit_citations.py --json

退出码
------
0 = 全部引用都指向真实位置 · 1 = 有越界/不存在的引用 · 2 = 用法错误
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_root() -> str:
    """确定"仓库根"。

    判据（按可靠性排序）：
    1. 环境变量 `VASP_SKILL_ROOT`（显式覆盖，测试夹具用）；
    2. **本脚本所在目录**，若它下面有 `references/raw`；
    3. 本脚本所在目录的**上一级**，若它下面有 `references/raw`
       （脚本被放进 `scripts/` 时）；
    4. 退回到"本脚本所在目录"（并由 main 打印警告）。

    ⚠️ 历史教训：早期版本无条件取 `dirname(HERE)`，于是当脚本放在仓库根时
    会把**工作区**当成仓库根 —— 症状是"审了 637 个文件、报 2328 条越界"，
    而那 637 个文件根本不是本仓库的。**判根错了，审计结果全是噪声。**
    """
    env = os.environ.get("VASP_SKILL_ROOT")
    if env and os.path.isdir(os.path.join(env, "references", "raw")):
        return os.path.abspath(env)
    for cand in (HERE, os.path.abspath(os.path.join(HERE, os.pardir))):
        if os.path.isdir(os.path.join(cand, "references", "raw")):
            return cand
    return HERE


ROOT = _find_root()
sys.path.insert(0, os.path.join(ROOT, "scripts"))

EXIT_OK, EXIT_BAD, EXIT_USAGE = 0, 1, 2

# 我们要审的文件：仓库里的 Markdown（**排除**原始素材层与外部资料）
SKIP_DIRS = {".git", "__pycache__", "cases", "things to study"}
# CHANGELOG 里会**引用**历史引用（"我原先写成 XXX，现在改成 YYY"），天然会越界；
SKIP_BASENAMES = {"CHANGELOG.md"}

# 文档里**故意**用来示范"这个文件该长什么样"的占位名。
# 它们出现在"命名约定""给站点信息一个出口"这类**说明**里，
# 不是"我引用了一个真实存在的文件"。
#
# ⚠️ 为什么要有这一条：审计必须对**真**问题保持敏感。
# 如果把 `SITE.md` 这类也报红，用户就会看到一堆"不用管"的红灯，
# 于是**学会忽略整个审计** —— 那比不审计更糟。
# 但也不能靠放宽正则把这一类一起放过去（那会连真问题也漏掉），
# 所以用**精确的占位名清单**，一条一条列出来。
PLACEHOLDER_PATTERNS = (
    r"(^|/)SITE\.md$",              # MAINTENANCE 约定的站点信息出口，永不入库
    r"_YYYYMMDD",                   # 命名约定里的日期占位
    r"L\{n\}\.txt$", r"D\{n\}\.txt$",   # 命名约定里的编号占位
    r"L\{1\.\.n\}", r"survey_YYYYMMDD",
    # "泛指的示例文件名"：文档用它们说明**这一类**文件该怎么命名，
    # 而不是声称某个具体文件存在。写成 X / Y / 占位符形式。
    r"pages/X\.md$", r"pages/Y\.md$",
    # "本层还没实现、计划要加的工具"：conformance/README.md §5 明确说
    # run_conformance.py **尚未实现**（因为需要真 POTCAR + 真程序）。
    # 把它当"引用了不存在的文件"是审计**读不懂上下文**，不是文档写错。
    # ⚠️ 这类例外必须**逐条列出并写明理由** —— 不许用宽泛通配，
    #    否则真问题会被一起放过去。
    r"conformance/run_conformance\.py$",
    # ⚠️ `EXnn` / `EX##` / `EX<编号>` 这类**泛指写法**：
    # 精读报告会在"§0 引用格式说明"里写一句
    # 「引用形式用 `EXnn:行`」，那是**在讲格式**，不是在引用某一篇。
    # 这是主线自己在任务书里教的写法 ⇒ 审计必须认它，否则**教什么就红什么**。
    r"/EXnn\.txt$", r"/EX##\.txt$",
)


def _is_placeholder(path: str) -> bool:
    """这个被引用的路径是不是"文档里故意举的占位样例"。"""
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, path):
            return True
    return False


# ---------------------------------------------------------------------------
# 引用抽取
# ---------------------------------------------------------------------------
# `L1 P28` / `L1 P28-30` / `L1 P28–30`（en-dash）
RE_LPAGE = re.compile(r"\bL([1-9]\d*)\s+P(\d+)(?:\s*[-–—]\s*(\d+))?")
# `D2-P14` / `D2-P14` 变体：D2 P14
RE_DPARA = re.compile(r"\bD([1-9]\d*)\s*[-–—]?\s*P(\d+)")
# LVTHW（Learn VASP The Hard Way）的篇+行引用：`EX80:42`、`EX80:42-45`、`M_02:12`
# 篇 id 的形态：字母开头、含字母数字下划线，全大写（如 EX80 / A29 / M_02 / S04 /
# EX01_V3 / A01_NOT_USED）。要求全大写是为了**避开普通中文文本里的
# 冒号+数字**（那种不行）。这条会由 RawIndex 逐个断言"该篇文件存在且行号在范围内"。
RE_LVTHW = re.compile(r"(?<![A-Za-z0-9_])"
                      r"([A-Z][A-Z0-9_]{1,20}?)"
                      r":(\d+)(?:\s*[-–—]\s*(\d+))?")
# 仓库内相对路径引用
RE_RELPATH = re.compile(
    r"(?<![\w./-])((?:references|scripts|examples|conformance|\.github)"
    r"/[A-Za-z0-9_./~-]+\.(?:md|tsv|txt|py|wiki|yml|json|SH|sh))")
# 带行号的文件引用：path:123 或 path:123-130
RE_WITHLINE = re.compile(
    r"((?:references|scripts|conformance|examples)/[A-Za-z0-9_./-]+"
    r"\.(?:md|py|txt|tsv)):(\d+)(?:\s*[-–—]\s*(\d+))?")
# 根目录下的文档
RE_ROOTDOC = re.compile(r"(?<![\w./-])((?:AGENTS|SKILL|USAGE|README|CONTRIBUTING|"
                        r"CHANGELOG|SITE)\.md)")


class Hit:
    __slots__ = ("kind", "text", "lineno", "ok", "detail")

    def __init__(self, kind, text, lineno, ok, detail=""):
        self.kind = kind
        self.text = text
        self.lineno = lineno
        self.ok = ok
        self.detail = detail


class RawIndex:
    """缓存 `references/raw/L*.txt` 与 `D*.txt` 的页/段集合。"""

    def __init__(self, root: str):
        self.root = root
        self._pages = {}
        self._paras = {}
        self._lines = {}
        self._lvthw = {}
        self._lvthw_dir = os.path.join(self.root, "references", "raw", "lvthw")

    def lvthw(self, pid: str):
        """LVTHW 篇：返回 (是否存在, 该篇总行数)。

        篇 id 用**全大写**（与 `extract_lvthw.py` 的 `post_id()` 一致），
        文件名即 `<ID>.txt`。判据只有"文件存在 + 行号在范围内" ——
        与 `_audit_citations.py` 对 `path:行号` 的处理口径一致
        （**只查存在性，不查语义**，见文件头的"它查不出什么"）。
        """
        if pid in self._lvthw:
            return self._lvthw[pid]
        p = os.path.join(self._lvthw_dir, "%s.txt" % pid)
        if not os.path.exists(p):
            self._lvthw[pid] = (False, 0)
            return self._lvthw[pid]
        n = 0
        try:
            with open(p, encoding="utf-8", errors="replace") as fh:
                for _ in fh:
                    n += 1
        except OSError:
            n = 0
        self._lvthw[pid] = (True, n)
        return self._lvthw[pid]

    def lvthw_ids(self):
        """返回 lvthw 层里所有可用的篇 id（用于区分"拼错的篇名"与"不是引用"）。"""
        if not os.path.isdir(self._lvthw_dir):
            return set()
        return {f[:-4] for f in os.listdir(self._lvthw_dir)
                if f.endswith(".txt") and not f.startswith("_")}

    def _path(self, name: str) -> str:
        return os.path.join(self.root, "references", "raw", name)

    def pages(self, tag: str):
        """返回 (是否存在, 页号集合, 实际页数)。"""
        if tag in self._pages:
            return self._pages[tag]
        p = self._path("%s.txt" % tag)
        if not os.path.exists(p):
            self._pages[tag] = (False, set(), 0)
            return self._pages[tag]
        nums = set()
        try:
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"=+\s*PAGE\s+(\d+)\s*=+", line.strip())
                    if m:
                        nums.add(int(m.group(1)))
        except OSError:
            pass
        self._pages[tag] = (True, nums, max(nums) if nums else 0)
        return self._pages[tag]

    def paras(self, tag: str):
        """返回 (是否存在, 段号集合, 实际段数)。"""
        if tag in self._paras:
            return self._paras[tag]
        p = self._path("%s.txt" % tag)
        if not os.path.exists(p):
            self._paras[tag] = (False, set(), 0)
            return self._paras[tag]
        nums = set()
        try:
            with open(p, encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"=+\s*%s-P(\d+)\s*=+" % re.escape(tag),
                                 line.strip())
                    if m:
                        nums.add(int(m.group(1)))
        except OSError:
            pass
        self._paras[tag] = (True, nums, max(nums) if nums else 0)
        return self._paras[tag]

    def nlines(self, relpath: str) -> int:
        if relpath in self._lines:
            return self._lines[relpath]
        p = os.path.join(self.root, relpath)
        n = 0
        if os.path.exists(p):
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    for _ in fh:
                        n += 1
            except OSError:
                n = 0
        self._lines[relpath] = n
        return n


def audit_file(path: str, rel: str, idx: RawIndex, same_file_lines: int):
    hits = []
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except OSError:
        return hits

    for i, line in enumerate(lines, start=1):
        # L* P*
        for m in RE_LPAGE.finditer(line):
            tag = "L%s" % m.group(1)
            lo = int(m.group(2))
            hi = int(m.group(3)) if m.group(3) else lo
            exists, pages, npages = idx.pages(tag)
            if not exists:
                hits.append(Hit("L-PAGE", m.group(0), i, False,
                                "文件 references/raw/%s.txt 不存在" % tag))
                continue
            miss = [n for n in (lo, hi) if n not in pages]
            if miss:
                hits.append(Hit("L-PAGE", m.group(0), i, False,
                                "页号 %s 在 %s.txt 里不存在（该文件实际 %d 页）"
                                % (",".join(map(str, miss)), tag, npages)))
            else:
                hits.append(Hit("L-PAGE", m.group(0), i, True,
                                "%s 共 %d 页" % (tag, npages)))
        # D*-P*
        for m in RE_DPARA.finditer(line):
            tag = "D%s" % m.group(1)
            n = int(m.group(2))
            exists, paras, nparas = idx.paras(tag)
            if not exists:
                hits.append(Hit("D-PARA", m.group(0), i, False,
                                "文件 references/raw/%s.txt 不存在" % tag))
                continue
            if n not in paras:
                hits.append(Hit("D-PARA", m.group(0), i, False,
                                "段号 %d 在 %s.txt 里不存在（该文件实际 %d 段）"
                                % (n, tag, nparas)))
            else:
                hits.append(Hit("D-PARA", m.group(0), i, True,
                                "%s 共 %d 段" % (tag, nparas)))
        # LVTHW 的篇:行引用（`EX80:42`）—— 只在"这个篇 id 真实存在"时才审。
        #
        # ⚠️ 为什么要加这个前置条件：`RE_LVTHW` 的形态（大写词 + 冒号 + 数字）
        # 在普通文本里也会出现（例如 `TODO:12`、`NOTE:3`）。
        # 若不加前置判断，审计会对每一个这样的串报"篇不存在" ——
        # 那是**假红**，而假红会让人学会忽略整个审计（见 CHANGELOG CR-018/023/024）。
        # ⇒ 判据：**先查这个 id 是否真的是 lvthw 层里的一篇**；
        #    不是 ⇒ 静默跳过（它不是引用）；是 ⇒ 断言行号在范围内。
        known_ids = idx.lvthw_ids()
        for m in RE_LVTHW.finditer(line):
            pid, a = m.group(1), int(m.group(2))
            b = int(m.group(3)) if m.group(3) else a
            if pid not in known_ids:
                continue
            exists, avail = idx.lvthw(pid)
            if not exists:
                hits.append(Hit("LVTHW", m.group(0), i, False,
                                "references/raw/lvthw/%s.txt 不存在" % pid))
                continue
            if avail and b > avail:
                hits.append(Hit("LVTHW", m.group(0), i, False,
                                "%s.txt 只有 %d 行，引到了第 %d 行"
                                % (pid, avail, b)))
            else:
                hits.append(Hit("LVTHW", m.group(0), i, True,
                                "%s 共 %d 行" % (pid, avail)))
        # 带行号的仓库内引用
        seen_span = set()
        for m in RE_WITHLINE.finditer(line):
            target, a = m.group(1), int(m.group(2))
            b = int(m.group(3)) if m.group(3) else a
            key = (target, a, b)
            if key in seen_span:
                continue
            seen_span.add(key)
            tp = os.path.join(ROOT, target)
            if not os.path.exists(tp):
                hits.append(Hit("WITHLINE", m.group(0), i, False,
                                "文件 %s 不存在" % target))
                continue
            # 纯文本行号（决定是否审）
            if not target.endswith((".md", ".py", ".txt", ".tsv")):
                hits.append(Hit("WITHLINE", m.group(0), i, True, "（未审非文本）"))
                continue
            is_self = os.path.abspath(tp) == os.path.abspath(path)
            avail = same_file_lines if is_self else idx.nlines(target)
            if avail and b > avail:
                hits.append(Hit("WITHLINE", m.group(0), i, False,
                                "%s 只有 %d 行，引到了第 %d 行"
                                % (target, avail, b)))
            else:
                hits.append(Hit("WITHLINE", m.group(0), i, True,
                                "%s 共 %d 行" % (target, avail)))

        # 仓库内相对路径（不让它和 WITHLINE 重复报同一个串）
        for m in RE_RELPATH.finditer(line):
            p = m.group(1)
            if any(p == h.text.split(":")[0] for h in hits
                   if h.kind == "WITHLINE" and h.lineno == i):
                continue
            full = os.path.join(ROOT, p)
            ok = os.path.exists(full) or _is_placeholder(p)
            hits.append(Hit("PATH", p, i, ok,
                            "" if ok else "文件不存在：%s" % p))
        # 根目录文档
        for m in RE_ROOTDOC.finditer(line):
            p = m.group(1)
            ok = (os.path.exists(os.path.join(ROOT, p))
                  or _is_placeholder(p))
            hits.append(Hit("PATH", p, i, ok,
                            "" if ok else "文件不存在：%s" % p))
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_audit_citations.py",
        description="引用审计：断言所有引用指向真实存在的页/段/文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法\n----", 1)[-1].strip(),
    )
    ap.add_argument("--file", help="只审这一个文件")
    ap.add_argument("--verbose", action="store_true", help="连通过项也列出")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    idx = RawIndex(ROOT)
    targets = []
    if args.file:
        if not os.path.exists(args.file):
            sys.stderr.write("错误：文件不存在：%s\n" % args.file)
            return EXIT_USAGE
        targets.append(args.file)
    else:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS
                           and not d.startswith(".")]
            for name in filenames:
                if not name.endswith(".md"):
                    continue
                if name in SKIP_BASENAMES:
                    continue
                targets.append(os.path.join(dirpath, name))
        targets.sort()

    all_hits = []
    for p in targets:
        rel = os.path.relpath(p, ROOT)
        try:
            nlines = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
        except OSError:
            nlines = 0
        for h in audit_file(p, rel, idx, nlines):
            h.text = h.text
            all_hits.append((rel, h))

    bad = [(r, h) for r, h in all_hits if not h.ok]
    good = [(r, h) for r, h in all_hits if h.ok]

    if args.json:
        print(json.dumps({
            "files_audited": len(targets),
            "citations": len(all_hits),
            "bad": [{"file": r, "line": h.lineno, "kind": h.kind,
                     "text": h.text, "why": h.detail} for r, h in bad],
        }, ensure_ascii=False, indent=2))
        return EXIT_BAD if bad else EXIT_OK

    print("=" * 72)
    print("引用审计 —— 断言所有引用指向真实存在的页/段/文件")
    print("=" * 72)
    print("审了 %d 个 Markdown 文件，抽出 %d 条引用。\n" % (len(targets), len(all_hits)))

    if args.verbose and good:
        print("── 通过（%d 条）──" % len(good))
        for r, h in good:
            print("  ✓ %s:%d  %-28s %s" % (r, h.lineno, h.text, h.detail))
        print()

    if bad:
        print("── **越界 / 不存在（%d 条）** ──" % len(bad))
        for r, h in bad:
            print("  ✗ %s:%d  [%s] %s" % (r, h.lineno, h.kind, h.text))
            if h.detail:
                print("        %s" % h.detail)
        print()
    else:
        print("── 越界 / 不存在：**0 条** ──\n")

    print("-" * 72)
    print("结论：引用 %d 条，其中越界/不存在 %d 条" % (len(all_hits), len(bad)))
    print()
    print("⚠️ **本审计查不出什么**（如实说明，免得给你假的安心）：")
    print("   ① 查不出「行号没越界、但指向了别的内容」—— 文件被改写后行号会**语义漂移**。")
    print("      引行号密集的文件（course_learned.md 尤甚）前，**先 grep 一次确认**。")
    print("   ② **不校验 `§` 号** —— Markdown 没有机器可读的章节锚点。")
    print("      本工具只校验「文件存在」，`§` 号的正确性靠人。")
    print("   ③ **不校验引用的内容是否正确**，只查存在性。")
    print("   ④ 不校验 `things to study/` 下的路径（那批资料不在仓库里）。")
    print("   ⑤ 不校验 `references/cases/`（原始算例层）—— 那里是逐字节保留的素材。")
    return EXIT_BAD if bad else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
