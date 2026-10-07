#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""extract_lvthw.py —— 《Learn VASP The Hard Way》第二版 → 逐篇可引用文本（E 层）

背景
----
`things to study2/LVTHW-master/` 是 **Hexo 静态站导出**，
正文在 `source/_posts/*.md`（132 篇 / 约 20110 行 / 937 KB），
每篇带 YAML front-matter（`title` / `categories` / `tags` / `date`），
配图在同名 asset 目录里（1015 张 / 94 MB）。

它在知识库里的位置：**E 层原始素材**（`references/raw/lvthw/`）。

抽取铁律（与 `extract_lectures.py` / `extract_qa.py` 完全一致）
--------------------------------------------------------------
**逐字保留、只统一换行为 LF、绝不加头注/尾注。**

为什么这条不能破：本仓库的**整个引用体系**挂在"文件的第 N 行"上。
一旦插入任何行，`lvthw/ex09:42` 这类引用就**整体失效**。
溯源信息（源文件名 / 篇数 / 行数 / sha256）登记到
`references/raw/lvthw/README.md`，**不要写进正文文件本身**。

与其它抽取脚本的关键区别
------------------------
本脚本**保留 front-matter**（作为 `========== POST <id> ==========` 行之后的
原文一部分），因为：
- 正文里的 `title` 是**引用时需要的信息**（`[讲义]` 风格要给篇名）；
- 删掉它会改变行号，破坏"逐字保留"。

但**引用行号时以本脚本输出的行号为准**，不是原始 `.md` 的行号。

⚠️ **站点信息**
--------------
这是**网站导出**，Shell 提示符里带大量现场信息（实测：`/home/` 路径 337 处、
`用户名@主机` 42 处、IPv4 17 处、`module load` 4 处、密钥相关 22 处）。

本脚本**逐字保留它们**（归档层的职责就是"原样"，见 `MAINTENANCE.md` §0.1）。
**消费层不得复制这些细节** —— 用 `--scan-site-info` 生成"SITEINFO 清单"，
供后续写作时逐条核对"哪一句只能提方法、不能提机器"。

用法
----
    python references/raw/extract_lvthw.py --src "<LVTHW-master 目录>"
    python references/raw/extract_lvthw.py --list          # 只列不抽
    python references/raw/extract_lvthw.py --scan-site-info # 生成站点信息清单
    python references/raw/extract_lvthw.py --clean         # 清掉输出目录后重抽

依赖：只用标准库（不需要 pypdf / python-docx）。
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys

DEFAULT_SRC_HINT = "things to study2/LVTHW-master"

# 站点/敏感信息的形态（**只用于生成清单，不用于修改正文**）
SITE_PATTERNS = [
    ("IPv4", r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
     "IP 地址 —— 消费层只能写「某超算」，不能写地址"),
    ("user@host", r"\b[A-Za-z_][\w.-]*@[\w.-]+\.\w+",
     "账号@主机 —— 消费层不得出现账号"),
    ("home_path", r"/home/[A-Za-z_][\w.-]*",
     "用户主目录绝对路径 —— 消费层用 ~ 或占位符代替"),
    ("opt_path", r"/opt/[\w./+-]+",
     "软件绝对路径 —— 消费层不得出现本机路径"),
    ("module_load", r"module\s+load\s+\S+",
     "具体模块名 —— 消费层只能写「按集群文档加载 MPI/编译器」"),
    ("batch_system", r"\b(?:#SBATCH|sbatch|qsub|bsub)\b",
     "排队系统命令 —— 可提「用排队系统提交」，不得写队列名/核数上限"),
    ("ssh_tool", r"\b(?:sshfs|scp\s+-|rsync\s+)", "远程传输命令 —— 可提方法"),
    ("key_material", r"id_rsa|\.ssh/|私钥|秘钥|密钥",
     "密钥相关 —— 消费层**绝对不得**出现任何密钥内容或路径"),
    ("vpn", r"\b(?:VPN|SCVPN|EasyConnect)\b", "VPN —— 可提「需要 VPN」"),
    ("supercomputer_name", r"(?:国科智算|超算中心|天河|曙光|蓝海|集群名)",
     "具体超算/集群名 —— 消费层只能写「你的集群」"),
    ("email", r"[\w.+-]+@[\w-]+\.[\w.]+", "邮箱 —— 一般不需要进消费层"),
    ("qq_group", r"(?:QQ群|qq群|公众号|微信群)", "联系方式 —— 不进消费层"),
]


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_posts(src: str) -> str:
    """定位 `source/_posts`。"""
    for cand in (os.path.join(src, "source", "_posts"), src):
        if os.path.isdir(cand) and any(
                f.endswith(".md") for f in os.listdir(cand)):
            return cand
    return ""


def _front_matter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    fm = m.group(1)

    def one(key):
        mm = re.search(r"^%s:\s*(.*)$" % key, fm, re.M)
        return mm.group(1).strip() if mm else ""

    def lst(key):
        mb = re.search(r"^%s:\s*\n((?:[ \t]*-.*\n?)*)" % key, fm, re.M)
        return [x.strip() for x in re.findall(r"^\s*-\s*(.+)$",
                                              mb.group(1) if mb else "", re.M)]
    return {"title": one("title"), "date": one("date"),
            "categories": lst("categories"), "tags": lst("tags")}


# 篇名 → 稳定 id（引用时用）。规则：文件主干（大写化），保留下划线。
def post_id(filename: str) -> str:
    stem = os.path.splitext(filename)[0]
    return stem.upper().replace("A01_NOT_USED", "A01_NOT_USED")


def main(argv=None) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(
        prog="extract_lvthw.py",
        description="《Learn VASP The Hard Way》逐篇抽取（E 层，带 POST 行标记）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法\n----", 1)[-1].strip(),
    )
    ap.add_argument("--src", default=os.environ.get("LVTHW_SRC", ""),
                    help="LVTHW-master 目录（或 source/_posts）；"
                         "也可用环境变量 LVTHW_SRC")
    ap.add_argument("--out", default=os.path.join(here, "lvthw"),
                    help="输出目录（默认 references/raw/lvthw）")
    ap.add_argument("--list", action="store_true", help="只列不写")
    ap.add_argument("--scan-site-info", action="store_true",
                    help="生成 SITEINFO.tsv（站点信息清单，供消费层核对）")
    ap.add_argument("--clean", action="store_true", help="先清空输出目录")
    args = ap.parse_args(argv)

    src = args.src
    if not src:
        # 从脚本位置往上找默认路径（**不写死绝对路径**）
        guess = os.path.join(here, os.pardir, os.pardir, DEFAULT_SRC_HINT)
        guess = os.path.normpath(guess)
        if os.path.isdir(guess):
            src = guess
    if not src or not os.path.isdir(src):
        sys.stderr.write(
            "错误：没有指定 LVTHW 目录。\n"
            "  请用 --src <LVTHW-master 目录>，或设环境变量 LVTHW_SRC。\n"
            "  例：python references/raw/extract_lvthw.py "
            "--src \"things to study2/LVTHW-master\"\n")
        return 3

    posts_dir = _find_posts(src)
    if not posts_dir:
        sys.stderr.write("错误：在 %s 里找不到 source/_posts（或该目录下没有 .md）\n"
                         % src)
        return 1

    names = sorted(f for f in os.listdir(posts_dir) if f.endswith(".md"))
    if not names:
        sys.stderr.write("错误：%s 里没有 .md 文件\n" % posts_dir)
        return 1

    if args.clean and os.path.isdir(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out, exist_ok=True)

    manifest, site_rows = [], []
    total_lines = 0

    for name in names:
        rel = name
        p = os.path.join(posts_dir, name)
        raw = open(p, encoding="utf-8", errors="replace").read()
        body = raw.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
        pid = post_id(name)
        fm = _front_matter(raw)

        # 站点信息清单（**只记录，不改正文**）
        if args.scan_site_info:
            for i, line in enumerate(body.split("\n"), start=1):
                for kind, pat, why in SITE_PATTERNS:
                    if re.search(pat, line):
                        site_rows.append((pid, i, kind, why,
                                          line.strip()[:120]))

        # 带 POST 标记的逐字正文
        out_text = "========== POST %s ==========\n%s\n" % (pid, body)
        dest = os.path.join(args.out, "%s.txt" % pid)

        nlines = out_text.count("\n")
        total_lines += nlines
        manifest.append({
            "id": pid, "file": rel,
            "title": fm.get("title", ""),
            "cats": "/".join(fm.get("categories", [])),
            "tags": "/".join(fm.get("tags", [])),
            "date": fm.get("date", ""),
            "lines": nlines,
            "sha256_src": _sha256(p),
            "bytes": len(out_text.encode("utf-8")),
        })

        if args.list:
            print("%-14s %5d 行  %-46s %s"
                  % (pid, nlines, fm.get("title", "")[:44],
                     fm.get("date", "")[:10]))
            continue
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out_text)

    if args.list:
        print("\n共 %d 篇" % len(manifest))
        return 0

    # ---- 溯源清单（写进 README，**不写进正文**） ----
    with open(os.path.join(args.out, "_MANIFEST.tsv"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("# id\tfile\ttitle\tcategories\ttags\tdate\tlines\tbytes\tsha256_src\n")
        for r in manifest:
            fh.write("\t".join(str(r[k]) for k in
                               ("id", "file", "title", "cats", "tags", "date",
                                "lines", "bytes", "sha256_src")) + "\n")

    # ---- 篇 → 主题分组表（供 README 与学习分组用） ----
    groups = {
        "G1_基础与四件套": ["PREFACE", "EX00", "EX00_V3", "EX01", "EX01_V3",
                          "EX02", "EX02_V3", "EX03", "EX04", "EX05", "EX06",
                          "EX07"],
        "G2_收敛与块体": ["EX08", "EX09", "EX10", "EX11", "EX12", "EX13",
                        "EX14", "EX15", "EX16", "EX17", "EX18", "EX19",
                        "EX20", "EX32", "EX33", "EX34", "EX35", "EX36"],
        "G3_DOS": ["EX37", "EX38", "EX39", "EX40", "EX41", "M_02"],
        "G4_表面与功函数": ["EX42", "EX43", "EX44", "EX45", "EX46", "EX47",
                        "EX48", "EX49", "EX50", "EX51", "EX52", "EX53"],
        "G5_吸附与热力学": ["EX22", "EX23", "EX24", "EX25", "EX26", "EX27",
                        "EX54", "EX55", "EX56", "EX57", "EX58", "EX59",
                        "EX60", "EX61", "EX62", "EX63", "EX64", "EX65",
                        "EX66", "EX67", "EX68", "EX69", "EX85"],
        "G6_过渡态": ["EX70", "EX71", "EX72", "EX73", "EX74", "EX75", "EX76",
                    "EX77", "EX78", "EX79", "EX80", "EX81", "EX82", "EX83",
                    "EX84"],
        "G7_生态工具": ["A17", "A18", "A19", "A20", "A21", "A22", "A23",
                     "A24", "A25", "A26", "A27", "A28", "A29", "A30", "A31",
                     "A32", "A33", "A34"],
        "G8_脚本与社区": ["A03", "A04", "A05", "A06", "A07", "A08", "A09",
                       "A10", "A11", "A12", "A13", "A14", "A15", "A16",
                       "S01", "S02", "S03", "S04", "S05", "S06", "S07",
                       "M_01", "M_03", "J01", "J02"],
    }
    ids = {r["id"] for r in manifest}
    with open(os.path.join(args.out, "_GROUPS.tsv"), "w",
              encoding="utf-8", newline="\n") as fh:
        fh.write("# group\tpost_ids\n")
        covered = set()
        for g, members in groups.items():
            have = [m for m in members if m in ids]
            covered |= set(have)
            fh.write("%s\t%s\n" % (g, " ".join(have)))
        missing = sorted(ids - covered)
        if missing:
            fh.write("(未归组)\t%s\n" % " ".join(missing))

    if args.scan_site_info and site_rows:
        with open(os.path.join(args.out, "SITEINFO.tsv"), "w",
                  encoding="utf-8", newline="\n") as fh:
            fh.write("# post\tline\tsiteinfo\t消费层怎么写\n"
                     "# ⚠️ 本表**只用于核对**，不用于改正文。\n"
                     "#    正文（*.txt）按铁律逐字保留；消费层不得复制这些细节。\n")
            for r in site_rows:
                fh.write("%s\t%d\t%s\t%s\n"
                         % (r[0], r[1], r[2], r[3]))

    print("已写出 %d 篇 → %s" % (len(manifest), args.out))
    print("总行数 %d" % total_lines)
    print("  _MANIFEST.tsv  溯源清单（篇名/分类/行数/sha256）")
    print("  _GROUPS.tsv    篇 → 学习分组")
    if args.scan_site_info:
        print("  SITEINFO.tsv   站点信息清单 %d 条（**只核对，不改正文**）"
              % len(site_rows))
    else:
        print("  （加 --scan-site-info 可生成站点信息清单）")
    print()
    print("⚠️ 正文里逐字保留了 Shell 提示符等现场信息（归档层的职责）。")
    print("   **消费层（references/*.md）不得复制这些细节** —— 见")
    print("   references/MAINTENANCE.md §0.1「机器细节不进，结论进」。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
