#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_validate_all_suites.py —— **串行**跑全部护栏（**零依赖**）

为什么必须串行
=============
CP2K skill 实测过：并行跑校验会因为临时目录/内存竞争而**假红**
（单独跑全绿、同时跑崩溃）。所以本仓库沿用"串行"这条规矩 ——
**一次只跑一个套件**。

跑哪几套
========
| # | 套件 | 守住什么 |
|---|---|---|
| 1 | `_audit_citations.py` | **可回溯**：所有引用指向真实页/段/文件 |
| 2 | `_doc_consistency.py` | 文档数字与代码/目录里的**真值**一致 |
| 3 | `_inject_test.py` | 上面每条护栏**真的会红**，且合法输入放行 |
| 4 | `scripts/doctor.py` | 环境与脚本完整性（**含"零依赖"承诺的核对**） |
| 5 | `_smoke_entrypoints.py`（内置） | 每个脚本 `--help` 必须 `exit 0`；无参数必须是 `exit 2` |

**为什么第 4 项也在里面**：它会核对"核心脚本是否真的只用标准库"。
那条承诺一旦破了，"能不能跑起来不依赖用户的环境运气"就没了。

**为什么第 5 项要单独做**：本项目踩过"没写参数解析 ⇒ `--help` 被当成无参数 ⇒
直接跑起全套再按结果非 0 退出"的坑，而那会让入口扫描类护栏**稳定判红**。

用法
----
    python _validate_all_suites.py
    python _validate_all_suites.py --only audit
    python _validate_all_suites.py --list
    python _validate_all_suites.py --fast      # 跳过 injection（最慢的一套）

退出码
------
0 = 全部通过 · 1 = 有套件失败 · 2 = 用法错误
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))
SCRIPTS = os.path.join(ROOT, "scripts")

EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2
TIMEOUT = 900


def run(cmd, timeout=TIMEOUT):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT,
                           env=env, timeout=timeout, encoding="utf-8",
                           errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 999, "（超时 %ds）" % timeout


def suite_audit() -> "tuple[int, str]":
    return run([sys.executable, os.path.join(ROOT, "_audit_citations.py")])


def suite_doc() -> "tuple[int, str]":
    return run([sys.executable, os.path.join(ROOT, "_doc_consistency.py"),
                "--all"])


def suite_inject() -> "tuple[int, str]":
    return run([sys.executable, os.path.join(ROOT, "_inject_test.py")])


def suite_coverage() -> "tuple[int, str]":
    """分段表覆盖性：精读报告是否**真的读完了**。

    这一套守的是"**声明 vs 断言**"的区别 ——
    "我读完了"是声明（无法证伪），"每篇行区间连续覆盖"是断言（可机器核）。
    见 references/MAINTENANCE.md 的 Phase 2 与 _check_coverage.py 的说明。
    """
    return run([sys.executable, os.path.join(ROOT, "_check_coverage.py")])


def suite_doctor() -> "tuple[int, str]":
    return run([sys.executable, os.path.join(SCRIPTS, "doctor.py")])


def suite_entrypoints() -> "tuple[int, str]":
    """每个面向用户的脚本：`--help` 必须 exit 0。

    ⚠️ 这一套**不检查"无参数必须 exit 2"** —— 因为有些脚本（如 `doctor.py`）
    的合理默认行为就是"检查当前目录"，无参数不是错误。
    硬套"无参数必须 exit 2"会制造假红，而**假红会让人学会忽略红灯**。
    真正重要的一条是 `--help` 必须 exit 0（见文件头说明）。
    """
    out = []
    bad = []
    scripts = sorted(f for f in os.listdir(SCRIPTS)
                     if f.endswith(".py") and not f.startswith("_")
                     and f != "vasp_common.py")
    for s in scripts:
        rc, txt = run([sys.executable, os.path.join(SCRIPTS, s), "--help"],
                      timeout=60)
        flag = "OK " if rc == 0 else "BAD"
        out.append("  [%s] %s --help → exit %d" % (flag, s, rc))
        if rc != 0:
            bad.append((s, rc, txt[:200]))
    if bad:
        for s, rc, txt in bad:
            out.append("")
            out.append("  ✗ %s --help 退出码 %d（应为 0）：" % (s, rc))
            out.append("      " + txt.replace("\n", "\n      ")[:400])
    return (1 if bad else 0), "\n".join(out)


SUITES = [
    ("audit", "引用审计（可回溯）", suite_audit),
    ("doc", "文档口径一致 + 泄漏扫描", suite_doc),
    ("inject", "注入测试（护栏真的会红）", suite_inject),
    ("coverage", "分段表覆盖性（精读报告真的读完了）", suite_coverage),
    ("doctor", "环境与脚本完整性（含零依赖承诺）", suite_doctor),
    ("entry", "入口健壮性（--help 必须 exit 0）", suite_entrypoints),
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_validate_all_suites.py",
        description="串行跑全部护栏（**不要并行**）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=全部通过；1=有套件失败；2=用法错误。",
    )
    ap.add_argument("--only", help="只跑某一套（按 id）")
    ap.add_argument("--fast", action="store_true",
                    help="跳过 injection（最慢的一套）")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="把每个套件的完整输出也打出来")
    args = ap.parse_args(argv)

    if args.list:
        print("套件（**串行**跑）：\n")
        for sid, title, _fn in SUITES:
            print("  %-8s %s" % (sid, title))
        return EXIT_OK

    todo = SUITES
    if args.only:
        todo = [s for s in SUITES if s[0] == args.only]
        if not todo:
            sys.stderr.write("错误：没有这个套件 id：%s\n" % args.only)
            return EXIT_USAGE
    elif args.fast:
        todo = [s for s in SUITES if s[0] != "inject"]

    print("=" * 72)
    print("全部护栏 —— **串行**运行（并行会因临时目录竞争而假红）")
    print("=" * 72)
    print("仓库根：%s" % ROOT)
    print("跑 %d 个套件：%s\n" % (len(todo), ", ".join(s[0] for s in todo)))

    results = []
    for i, (sid, title, fn) in enumerate(todo, start=1):
        print("[%d/%d] %s —— %s" % (i, len(todo), sid, title))
        print("-" * 72)
        rc, txt = fn()
        results.append((sid, title, rc, txt))
        if args.verbose:
            print(txt)
        else:
            # 只印最后几行（结论行通常在那里）
            lines = [l for l in txt.strip().split("\n") if l.strip()]
            for l in lines[-6:]:
                print("   " + l)
        mark = "✓ 通过" if rc == 0 else "✗ 失败（exit %d）" % rc
        print("   → %s\n" % mark)

    n_bad = sum(1 for _s, _t, rc, _x in results if rc != 0)
    print("=" * 72)
    print("汇总")
    print("=" * 72)
    for sid, title, rc, _txt in results:
        print("  %-8s %-6s %s" % (sid, "✓" if rc == 0 else "✗", title))
    print()
    if n_bad:
        print("结论：**%d/%d 个套件失败**。" % (n_bad, len(results)))
        print()
        print("⚠️ 红了先弄明白再改 —— **不要为了让灯变绿而放宽判据**。")
        print("   先问：是判据太严，还是被检对象真的错了？")
        print("   本项目两种都遇到过，都在 CHANGELOG.md 的更正记录里有记录。")
        for sid, title, rc, txt in results:
            if rc == 0:
                continue
            print()
            print("── %s 的输出尾部 ──" % sid)
            lines = [l for l in txt.strip().split("\n") if l.strip()]
            for l in lines[-14:]:
                print("   " + l)
    else:
        print("结论：**全部 %d 个套件通过**。" % len(results))
        print()
        print("⚠️ 但请记住这**不等于「全部正确」** —— 它只说明：")
        print("   · 所有引用指向真实位置（不说明引用得对不对）；")
        print("   · 文档数字与代码里的真值一致（不说明那些数对不对）；")
        print("   · 每条护栏在被注入缺陷时真的会红（不说明它覆盖了全部缺陷）；")
        print("   · 脚本完整、零依赖、入口健壮（不说明逻辑没有盲区）。")
    print("=" * 72)
    return EXIT_FAIL if n_bad else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
