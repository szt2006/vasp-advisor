#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讲义 PDF → 分页纯文本（E 层原始素材抽取）

用途
----
把课程讲义 PDF 逐页抽取为带页码标记的纯文本，落进 `references/raw/`。
抽取结果**只统一换行为 LF，不加任何头注/尾注** —— 一旦插入任何行，
"L2.txt:第 N 行" 这个引用体系就整体失效。溯源信息（原始文件名 / 页数 /
sha256）登记在 `references/raw/README.md`，**不要写进 L*.txt 本身**。

页码标记
--------
每页前一行 `========== PAGE N ==========`，N 从 1 开始。
这是"页引用"能被脚本核对的前提（见 `_audit_citations.py`）。

依赖
----
`pypdf`（第三方）。**这一个脚本是唯一允许的第三方依赖**：
它只在"新增/更新资料"时手工跑一次，不属于交付给用户的零依赖工具链。
缺 pypdf 时给出友好提示与 exit 3，不抛 traceback。

用法
----
    # 默认：从环境变量 VASP_COURSE_SRC 指向的目录里找讲义 PDF
    python references/raw/extract_lectures.py

    # 显式指定源目录与输出目录
    python references/raw/extract_lectures.py --src "<讲义目录>" --out references/raw

    # 只列出会抽哪些文件，不实际抽取
    python references/raw/extract_lectures.py --list

    # 指定讲义排序（按文件名子串匹配，可重复）
    python references/raw/extract_lectures.py --pick "专题-1:L1" --pick "专题-2:L2"
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys


def _die(msg: str, code: int) -> "None":
    """友好中文提示后退出（不抛 traceback）。"""
    sys.stderr.write(msg.rstrip() + "\n")
    raise SystemExit(code)


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_pdfs(src: str) -> "list[str]":
    out = []
    for dirpath, _dirnames, filenames in os.walk(src):
        for name in filenames:
            if name.lower().endswith(".pdf"):
                out.append(os.path.join(dirpath, name))
    return sorted(out)


def _default_picks(root_pdfs: "list[str]") -> "list[tuple[str, str]]":
    """默认把名字里带 `专题-N` 的四份主讲义映射为 L1..L4。

    只按**文件名子串**匹配，因此换机器、换目录都能用；
    匹配不到就返回空表，由调用方决定是报错还是跳过。
    """
    picks: "list[tuple[str, str]]" = []
    for token, tag in (("专题-1", "L1"), ("专题-2", "L2"),
                       ("专题-3", "L3"), ("专题-4", "L4")):
        hit = [p for p in root_pdfs if token in os.path.basename(p)]
        if hit:
            picks.append((hit[0], tag))
    return picks


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(
        prog="extract_lectures.py",
        description="讲义 PDF → 分页纯文本（E 层原始素材抽取，带 PAGE 标记）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法\n----", 1)[-1].strip(),
    )
    ap.add_argument("--src", default=os.environ.get("VASP_COURSE_SRC", ""),
                    help="讲义 PDF 所在目录（默认取环境变量 VASP_COURSE_SRC）")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__))),
                    help="输出目录（默认本脚本所在目录）")
    ap.add_argument("--pick", action="append", default=[],
                    metavar="SUBSTR:TAG",
                    help="按文件名子串选一份讲义并指定输出名，可重复；"
                         "如 --pick \"专题-2:L2\"")
    ap.add_argument("--list", action="store_true",
                    help="只列出将要抽取的文件与页数，不写文件")
    args = ap.parse_args(argv)

    if not args.src:
        _die("错误：没有指定讲义目录。\n"
             "  请用 --src <目录>，或设置环境变量 VASP_COURSE_SRC。\n"
             "  例：python references/raw/extract_lectures.py --src \"D:/.../000课件\"",
             3)
    if not os.path.isdir(args.src):
        _die("错误：讲义目录不存在：%s" % args.src, 1)

    try:
        from pypdf import PdfReader
    except ImportError:
        _die("错误：缺少依赖 pypdf。\n"
             "  本脚本只在『新增/更新资料』时使用，不属于交付给用户的零依赖工具链。\n"
             "  安装：python -m pip install pypdf\n"
             "  提示：其余所有脚本都只用标准库，无需任何安装。",
             3)

    all_pdfs = _find_pdfs(args.src)
    if not all_pdfs:
        _die("错误：目录里没有 PDF：%s" % args.src, 1)

    if args.pick:
        picks: "list[tuple[str, str]]" = []
        for spec in args.pick:
            if ":" not in spec:
                _die("错误：--pick 需要写成 SUBSTR:TAG，例如 专题-2:L2", 2)
            token, tag = spec.rsplit(":", 1)
            hit = [p for p in all_pdfs if token in os.path.basename(p)]
            if not hit:
                _die("错误：没有文件名包含 %r 的 PDF" % token, 1)
            picks.append((hit[0], tag))
    else:
        picks = _default_picks(all_pdfs)

    if not picks:
        _die("错误：没有匹配到任何讲义。请用 --pick SUBSTR:TAG 显式指定。\n"
             "  本次扫描到的 PDF：\n    " + "\n    ".join(
                 os.path.basename(p) for p in all_pdfs),
             1)

    os.makedirs(args.out, exist_ok=True)
    manifest = []
    for src_path, tag in picks:
        reader = PdfReader(src_path)
        npages = len(reader.pages)
        lines: "list[str]" = []
        empty_pages = []
        for idx, page in enumerate(reader.pages, start=1):
            lines.append("========== PAGE %d ==========" % idx)
            try:
                text = page.extract_text() or ""
            except Exception as exc:  # 单页抽取失败不该让整份讲义失败
                text = ""
                sys.stderr.write("  警告：%s 第 %d 页抽取失败：%s\n"
                                 % (os.path.basename(src_path), idx, exc))
            text = text.replace("\r\n", "\n").replace("\r", "\n")
            body = text.rstrip("\n")
            if not body.strip():
                empty_pages.append(idx)
            lines.append(body)
        content = "\n".join(lines) + "\n"
        dest = os.path.join(args.out, "%s.txt" % tag)

        nlines = content.count("\n")
        rel_src = os.path.basename(src_path)
        manifest.append((tag, rel_src, npages, nlines, _sha256(src_path), empty_pages))

        if args.list:
            print("%-4s <- %-60s %4d 页  %6d 行  空页 %s"
                  % (tag, rel_src, npages, nlines,
                     ",".join(map(str, empty_pages)) or "无"))
            continue

        # 无 BOM、LF 行尾、utf-8
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        print("已写出 %-4s <- %-50s %4d 页 → %6d 行%s"
              % (tag, rel_src, npages, nlines,
                 ("  空页 " + ",".join(map(str, empty_pages))) if empty_pages else ""))

    if not args.list and manifest:
        print("\n溯源清单（请登记到 references/raw/README.md，勿写入 L*.txt 本身）：")
        for tag, rel_src, npages, nlines, sha, empty in manifest:
            print("  %s | 源文件 %s | 页数 %d | 行数 %d | sha256(源) %s | 空页 %s"
                  % (tag, rel_src, npages, nlines, sha,
                     ",".join(map(str, empty)) or "无"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
