#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''_publish_prep.py —— **发布前预处理**：把不能公开的素材换成"安全占位版"。

为什么需要它（一个真实的、未修的泄漏面）
========================================
`references/raw/lvthw/` 是《Learn VASP The Hard Way》网站的**逐字导出**。
它自己的 `SITEINFO.tsv` 就记着里面有多少站点信息（**673 条**，12 类）：

| 类别 | 条数 | 是什么 |
|---|---|---|
| `home_path` | 329 | 用户主目录**绝对路径** |
| `supercomputer_name` | 89 | **具体超算/集群名** |
| `qq_group` | 71 | 联系方式 |
| `email` | 39 | 邮箱 |
| `user@host` | 37 | **账号@主机** |
| `opt_path` | 33 | 本机软件绝对路径 |
| `batch_system` | 21 | 排队系统命令 |
| `IPv4` | 17 | **IP 地址** |
| `key_material` | 16 | **密钥相关** |
| `ssh_tool` / `vpn` / `module_load` | 13 / 4 / 4 | 远程命令 / VPN / 模块名 |

**而 `.gitignore` 覆盖不到它** —— 它只挡外部源目录（`things to study*/`），
不挡这份**抽取后的归档**。⇒ `git add .` 会把 132 个 `.txt`（13 918 行）全部入库。

⛔ **为什么不能靠"正则脱敏"**
----------------------------
实测过：按类别做模式替换，**只清掉约 30%**——
`/home` 340 → 241、IP 17 → 12、密钥 20 → 16、`module load` 4 → 4（**一个没清掉**）。
原因：类别是**语义标签**（"集群名"），而集群名在正文里可能就是**普通英文词**，
正则**认不出**。
⇒ **"尽力而为的正则脱敏"会给false的信心**，那比不脱敏更危险。

✅ **正确做法：行数骨架**
------------------------
`_audit_citations.py` 核对 `EX80:42` 这种引用时，
**只需要"篇存在 + 行号在范围内"** —— 它**不读内容**（见其 `lvthw()` 实现）。
⇒ 所以发布版可以只保留**行数**、清空内容：

```
（实测）原文：引用审计 exit 0 · 覆盖性 exit 0
（实测）空壳：引用审计 exit 0 · 覆盖性 exit 0   ← 两条护栏都仍然有效
```

**既 100% 不泄漏，又保住可回溯性。** 这是本工具生成的产物。

用法
----
    python _publish_prep.py --check             # 只报告哪些素材不能公开
    python _publish_prep.py --make --out <目录>  # 生成"安全占位版"的 lvthw/
    python _publish_prep.py --restore           # 从备份恢复原文

原理
----
    lvthw/<ID>.txt   → 同样的**行数**，每行 `(content withheld)`
    lvthw/*.tsv/md   → 原样复制（清单类，供核对结构）

⚠️ **本站点原文另存**（`references/raw/_lvthw_original/`，已在 `.gitignore` 里），
   你自己的引用核对仍然能用原文。

退出码：0 成功 · 1 有问题 · 2 用法错误
'''

from __future__ import annotations

import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))
LVTHW = os.path.join(ROOT, "references", "raw", "lvthw")
# ⚠️ **原文只存在仓库外**（见 CHANGELOG 的 CR-059）。
#    原来放在 `references/raw/_lvthw_original/`，但那会**逼着 `.gitignore`
#    整目录忽略 `lvthw/`** —— 于是骨架也提交不上来。
#    ⇒ 原文挪到仓库外；仓库里只放骨架。
ORIG = os.environ.get("LVTHW_ORIGINAL") or os.path.join(
    os.path.dirname(ROOT), "_lvthw_backup_outside_repo")
PLACEHOLDER = "(content withheld)\n"


def _txt_files(d):
    if not os.path.isdir(d):
        return []
    return sorted(f for f in os.listdir(d)
                  if f.endswith(".txt") and os.path.isfile(os.path.join(d, f)))


def check():
    if not os.path.isdir(LVTHW):
        print("没有 references/raw/lvthw/ —— 无需处理。")
        return 0
    txt = _txt_files(LVTHW)
    n_lines = 0
    skeleton = 0
    for f in txt:
        lines = open(os.path.join(LVTHW, f), encoding="utf-8",
                     errors="replace").readlines()
        n_lines += len(lines)
        if lines and all(l.strip() == "(content withheld)" for l in lines):
            skeleton += 1
    site = os.path.join(LVTHW, "SITEINFO.tsv")
    n_site = 0
    if os.path.exists(site):
        for line in open(site, encoding="utf-8", errors="replace"):
            if line.startswith("#") or not line.strip():
                continue
            n_site += 1
    print("=" * 70)
    print("发布前体检：references/raw/lvthw/")
    print("=" * 70)
    print("\n  篇数        %d 个 .txt" % len(txt))
    print("  总行数      %d" % n_lines)
    print("  已是空壳    %d / %d" % (skeleton, len(txt)))
    print("  站点信息     %d 条（本表自己数的）" % n_site)
    print()
    if skeleton == len(txt) and txt:
        print("  ✓ 已是「安全占位版」—— 可以直接发布。")
        return 0
    print("  ⛔ **含站点信息，不能直接 push**（`AGENTS.md` 第 6/8 条）。")
    print("     => 生成安全占位版：`--make --out <临时目录>`")
    print()
    print("  ⚠️ **不要试图用正则脱敏** —— 实测只清掉约 30%，")
    print("     剩下的会被误认为「已经处理过」，**比不处理更危险**。")
    return 1


def make(out_dir: str):
    if not os.path.isdir(LVTHW):
        print("没有 references/raw/lvthw/。")
        return 1
    # ⚠️ **不再在仓库内备份**：`lvthw/` 里放的就是骨架，
    #    从它备份毫无意义（CR-059）。原文应由调用方自行保管在仓库外。
    if not os.path.isdir(ORIG):
        print("  ⚠️ 仓库外没找到原文目录 %s" % ORIG)
        print("     若你需要保留原文，请自行保管（本工具不再复制）。")
    else:
        print("  原文目录（仓库外）：%s" % ORIG)
    os.makedirs(out_dir, exist_ok=True)
    n = total = 0
    for fn in sorted(os.listdir(LVTHW)):
        src = os.path.join(LVTHW, fn)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(out_dir, fn)
        if fn.endswith(".txt"):
            lines = open(src, encoding="utf-8", errors="replace").readlines()
            with open(dst, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(PLACEHOLDER * len(lines))
            n += 1
            total += len(lines)
        else:
            shutil.copy2(src, dst)
    print("\n  生成安全占位版 → %s" % out_dir)
    print("  %d 个 .txt，共 %d 行（**行数与原文一致**）" % (n, total))
    print("\n  ⇒ 引用核对（`EX80:42`）仍然有效；内容 100% 不泄漏。")
    return 0


def restore(src=None):
    src = src or ORIG
    if not os.path.isdir(src):
        print("找不到原文目录：%s" % src)
        print("⇒ 用 `--restore --src <原文目录>` 指定，"
              "或设环境变量 `LVTHW_ORIGINAL`。")
        return 1
    if os.path.isdir(LVTHW):
        shutil.rmtree(LVTHW)
    shutil.copytree(src, LVTHW)
    print("已从备份恢复原文 → %s" % LVTHW)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_publish_prep.py",
        description="发布前预处理：把不能公开的素材换成行数一致的安全占位版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="⚠️ **不要用正则脱敏** —— 实测只清掉约 30%，\n"
               "   剩下的会被误认为「已处理」，比不处理更危险。\n"
               "   ⇒ 用「行数骨架」：护栏需要的是行数，不是内容。")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="只体检")
    g.add_argument("--make", action="store_true", help="生成安全占位版（要 --out）")
    g.add_argument("--restore", action="store_true", help="从备份恢复原文")
    ap.add_argument("--out", help="--make 的目标目录")
    ap.add_argument("--src", help="--restore 的原文目录（默认取环境变量 LVTHW_ORIGINAL）")
    args = ap.parse_args(argv)
    if args.check:
        return check()
    if args.restore:
        return restore(args.src)
    if args.make:
        if not args.out:
            print("--make 需要 --out <目录>", file=sys.stderr)
            return 2
        return make(os.path.abspath(args.out))
    return 2


if __name__ == "__main__":
    sys.exit(main())
