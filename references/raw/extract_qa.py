#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""答疑 Word 文档 → 分页/分段落纯文本（E 层原始素材抽取）

背景
----
课程答疑稿（`dayN-答疑.docx`）是**学员真实问题的答案**，是"经验层"最贴近
实战的来源之一：症状是学员真实报出来的，处方是讲师给的。

铁律（与讲义抽取一致）
----------------------
抽取结果**逐字保留、只统一换行为 LF、不加任何头注/尾注** ——
一旦插入任何行，`D2.txt:第 N 行` 这个引用体系就整体失效。
溯源信息（原始文件名 / 段落数 / sha256）登记在 `references/raw/README.md`。

输出
----
每段一行？**不**。用真实换行保留段落，段落之间空一行，
段首加 `========== D<N>-P<M> ==========` 便于精确引用某一段落。
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys


def _die(msg: str, code: int) -> "None":
    sys.stderr.write(msg.rstrip() + "\n")
    raise SystemExit(code)


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def docx_to_text(path: str) -> "list[str]":
    """按文档顺序把段落与表格取成文本块列表。"""
    try:
        import docx                                    # python-docx
    except ImportError:
        _die("错误：缺少依赖 python-docx。\n"
             "  本脚本只在『新增/更新资料』时使用。\n"
             "  安装：python -m pip install python-docx", 3)
    doc = docx.Document(path)
    blocks: "list[str]" = []
    for para in doc.paragraphs:
        t = para.text.strip()
        if t:
            blocks.append(t)
    for tbl in doc.tables:
        for row in tbl.rows:
            cells = [c.text.strip().replace("\n", " ") for c in row.cells]
            line = " | ".join(cells).strip(" |")
            if line:
                blocks.append(line)
    return blocks


def main(argv: "list[str] | None" = None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(
        prog="extract_qa.py",
        description="答疑 docx → 带段落标记的纯文本（E 层原始素材抽取）",
    )
    ap.add_argument("files", nargs="*",
                    help="docx 文件；缺省则用 --src 下的 *-答疑*.docx")
    ap.add_argument("--src", default="", help="答疑 docx 所在目录")
    ap.add_argument("--out", default=here, help="输出目录（默认本脚本所在目录）")
    ap.add_argument("--list", action="store_true", help="只列段落数，不写文件")
    args = ap.parse_args(argv)

    files = list(args.files)
    if not files:
        if not args.src or not os.path.isdir(args.src):
            _die("错误：请给出 docx 文件，或用 --src <目录> 指定答疑文档目录。", 2)
        for name in sorted(os.listdir(args.src)):
            low = name.lower()
            if low.endswith(".docx") and not name.startswith("~$"):
                files.append(os.path.join(args.src, name))
    if not files:
        _die("错误：没有找到任何 docx 文件。", 1)

    for f in files:
        if not os.path.isfile(f):
            _die("错误：文件不存在：%s" % f, 1)

    os.makedirs(args.out, exist_ok=True)
    manifest = []
    for path in files:
        base = os.path.basename(path)
        # day1-答疑.docx → D1 ; 其它 → 文件名去扩展名
        tag = None
        low = base.lower()
        if low.startswith("day") and low[3].isdigit():
            tag = "D" + low[3]
        if tag is None:
            tag = os.path.splitext(base)[0]
        blocks = docx_to_text(path)
        lines: "list[str]" = []
        for i, b in enumerate(blocks, start=1):
            lines.append("========== %s-P%d ==========" % (tag, i))
            lines.append(b.replace("\r\n", "\n").replace("\r", "\n"))
            lines.append("")
        content = "\n".join(lines).rstrip("\n") + "\n"
        npara = len(blocks)
        nlines = content.count("\n")
        manifest.append((tag, base, npara, nlines, _sha256(path)))
        if args.list:
            print("%-4s <- %-24s %4d 段 %6d 行" % (tag, base, npara, nlines))
            continue
        dest = os.path.join(args.out, "%s.txt" % tag)
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        print("已写出 %-4s <- %-24s %4d 段 → %6d 行" % (tag, base, npara, nlines))

    if not args.list and manifest:
        print("\n溯源清单（请登记到 references/raw/README.md）：")
        for tag, base, npara, nlines, sha in manifest:
            print("  %s | 源文件 %s | 段落数 %d | 行数 %d | sha256(源) %s"
                  % (tag, base, npara, nlines, sha))
    return 0


if __name__ == "__main__":
    sys.exit(main())
