#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""doctor.py —— 环境与脚本完整性自检（**零依赖，新手第一步跑它**）

它检查什么
==========
1. Python 版本（本 skill 要求 ≥ 3.8，因为用了 `importlib` 的一些行为与 f-string）
2. **所有脚本能不能被 import/编译** —— 这是"脚本完整性"
3. 知识库文件是否都在、能不能读
4. 官方关键字表在不在（**不在就等于归属校验不生效** —— 必须明说）
5. 引用审计能不能跑（它守的是整个知识库的价值主张）
6. 目录里有没有算例（有的话顺手体检一下）
7. `things to study` 之类的外部资料在不在（**不在不是错误**，只是提醒）

它**不检查**什么（说清楚，免得给你假的安心）
==========================================
- **不检查有没有 VASP**。本 skill 的任何离线工具都不需要 VASP；
  需要真程序的是 `conformance/`（见那里的 README）。
- 不检查网络。
- 不检查你的算例对不对。

退出码
------
0 = 核心功能可用 · 1 = 有文件缺失但部分功能可用 · 2 = 用法错误 · 3 = Python 太旧

用法
----
    python scripts/doctor.py
    python scripts/doctor.py --dir <算例目录>     # 顺便体检一个算例
    python scripts/doctor.py --json
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import platform
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vasp_common as vc                                       # noqa: E402

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))

# 核心脚本（只用标准库）+ 可选脚本（需要第三方库）
CORE_SCRIPTS = [
    "vasp_common.py", "doctor.py", "wizard.py", "validate.py", "compare.py",
    "diagnose.py", "recommend.py", "postprocess.py", "parse_output.py",
]
# ⚠️ 这张表要**把所有可选依赖都列全**。
# 历史事故：这张表曾只写 "需要 numpy"，而实际代码用的是 `matplotlib` ——
# 于是自检把 `postprocess.py` 判成"违反零依赖承诺"，
# 而它其实是**声明过的可选依赖**。**假红会让人学会忽略自检。**
OPTIONAL_SCRIPTS = {
    "postprocess.py": "出图（`--plot`）需要 matplotlib；"
                      "缺了会友好提示 + exit 3，**数值照样打出来**",
}
# 允许出现在"可选增强"里的第三方库白名单（与上表的说明**互相印证**）。
# 加新库时两处都要改 —— 这比让自检静默放过一个真依赖安全。
OPTIONAL_LIBS = {"numpy", "matplotlib", "scipy", "pandas"}

# 知识库的关键文件（缺了功能会退化，必须如实报）
KB_FILES = [
    ("AGENTS.md", "唯一真源入口", True),
    ("SKILL.md", "面向 AI 的技能描述", True),
    ("USAGE.md", "面向人的说明", True),
    ("README.md", "项目说明", True),
    ("references/decide.md", "A 层决策库", True),
    ("references/playbook.md", "F 层实战手册", True),
    ("references/course_learned.md", "B 层课程综合", False),
    ("references/course_notes.md", "C 层速查", False),
    ("references/MAINTENANCE.md", "维护规矩", True),
    ("references/_WRITING_CONTRACT.md", "写作契约（内部规范）", True),
    ("references/official/_keywords.tsv", "官方关键字表（归属校验的依据）", True),
    ("references/official/_sources.tsv", "官方层溯源清单", True),
    ("references/official/pages/INCAR.md", "官方 INCAR 页", True),
    ("references/official/pages/KPOINTS.md", "官方 KPOINTS 页", True),
    ("references/official/pages/POSCAR.md", "官方 POSCAR 页", True),
    ("references/official/pages/POTCAR.md", "官方 POTCAR 页", True),
    ("references/raw/L1.txt", "讲义原文 L1", False),
    ("references/raw/L2.txt", "讲义原文 L2", False),
    ("references/raw/L3.txt", "讲义原文 L3", False),
    ("references/raw/L4.txt", "讲义原文 L4", False),
    ("references/raw/D1.txt", "答疑原文 D1", False),
    ("references/raw/D2.txt", "答疑原文 D2", False),
    ("references/raw/D3.txt", "答疑原文 D3", False),
    ("references/raw/D4.txt", "答疑原文 D4", False),
    ("references/raw/learn_L1.md", "精读报告 L1", False),
    ("references/raw/learn_L2.md", "精读报告 L2", False),
    ("references/raw/learn_L3.md", "精读报告 L3", False),
    ("references/raw/learn_L4.md", "精读报告 L4", False),
]


def check_python() -> "tuple[bool, str]":
    v = sys.version_info
    ok = (v.major, v.minor) >= (3, 8)
    return ok, "Python %d.%d.%d（%s）%s" % (
        v.major, v.minor, v.micro, platform.system(),
        "" if ok else "  ⚠️ 需要 ≥ 3.8")


def check_scripts() -> "list[tuple[str, str, str]]":
    """逐个编译脚本，报出**语法错误**（比 import 更安全：不会真的执行）。"""
    out = []
    # 可选脚本也列进来，但**不重复**报（它们在 CORE_SCRIPTS 里已经有条目）
    for name in CORE_SCRIPTS + [n for n in OPTIONAL_SCRIPTS
                                if n not in CORE_SCRIPTS]:
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            out.append(("MISSING", name, "文件不存在"))
            continue
        try:
            src = open(path, encoding="utf-8").read()
            ast.parse(src)
        except SyntaxError as exc:
            out.append(("ERROR", name, "语法错误：第 %s 行 %s"
                        % (exc.lineno, exc.msg)))
            continue
        except Exception as exc:                              # noqa: BLE001
            out.append(("ERROR", name, "读/解析失败：%s" % exc))
            continue
        # 检查是否只用标准库（粗筛：列出 import 的顶层模块名）
        third = []
        try:
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        third.append(a.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.level == 0:
                        third.append(node.module.split(".")[0])
        except Exception:                                     # noqa: BLE001
            pass
        stdlib_ok = {"os", "sys", "re", "json", "math", "argparse", "ast",
                     "io", "gzip", "hashlib", "datetime", "platform",
                     "subprocess", "glob", "shutil", "textwrap", "typing",
                     "collections", "itertools", "importlib", "time",
                     "random", "ssl", "urllib", "unicodedata", "string",
                     "tempfile", "csv", "traceback", "__future__"}
        # ⚠️ 两类"看起来像第三方、其实不是"的，必须分开处理，
        #    否则会制造**假红**，而假红会让人学会忽略整个自检：
        #    · `wizard` —— 是**本仓库自己的模块**（`scripts/wizard.py`），
        #      `recommend.py` 复用它以避免"两份逻辑给出不同答案"。
        #    · `matplotlib` —— 是**可选依赖**（只有 `postprocess.py --plot` 用），
        #      而 `OPTIONAL_SCRIPTS` 表里已经声明了它。
        local_mods = {f[:-3] for f in os.listdir(HERE) if f.endswith(".py")}
        declared_optional = set(OPTIONAL_LIBS)
        extra = sorted(set(third) - stdlib_ok - local_mods - declared_optional)
        optional = sorted(set(third) & declared_optional)
        if extra and name in CORE_SCRIPTS:
            out.append(("THIRDPARTY", name,
                        "**核心脚本引入了第三方库**：%s —— 这违反零依赖承诺"
                        % ", ".join(extra)))
        elif optional:
            out.append(("OPTIONAL", name,
                        "声明过的**可选**依赖：%s（缺了会友好提示 + exit 3）"
                        % ", ".join(optional)))
        elif extra:
            out.append(("OPTIONAL", name, "可选依赖：%s" % ", ".join(extra)))
        else:
            out.append(("OK", name, "语法正常，只用标准库"))
    return out


def check_kb() -> "list[tuple[str, str, str]]":
    out = []
    for rel, desc, required in KB_FILES:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            out.append(("MISSING" if required else "ABSENT", rel,
                        "%s —— %s" % (desc, "**必需**" if required else "可选（缺了功能退化）")))
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                head = fh.read(4096)
        except Exception as exc:                              # noqa: BLE001
            out.append(("ERROR", rel, "读不了：%s" % exc))
            continue
        # 检查 BOM 与 CRLF（本仓库要求无 BOM、LF）
        bom = head.startswith("\ufeff")
        try:
            with open(p, "rb") as fh:
                raw = fh.read(200000)
            crlf = b"\r\n" in raw
        except Exception:                                     # noqa: BLE001
            crlf = False
        msgs = []
        if bom:
            msgs.append("**有 BOM**（下游程序可能拒收）")
        if crlf:
            msgs.append("**含 CRLF**（本仓库要求 LF）")
        size = os.path.getsize(p)
        out.append(("OK" if not msgs else "WARN", rel,
                    "%s（%d 字节）%s" % (desc, size,
                                        ("；" + "；".join(msgs)) if msgs else "")))
    return out


def check_keyword_table() -> "tuple[str, str, str]":
    p = os.path.join(ROOT, "references", "official", "_keywords.tsv")
    if not os.path.exists(p):
        return ("ERROR", "关键字表", "**不存在** → 归属校验完全不生效。"
                "生成它：python references/official/_fetch_wiki.py")
    n = 0
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            n += 1
    return ("OK", "关键字表", "%d 条（归属校验可用；⚠️ 该表**已知不完整**，"
            "见 decide.md §1.2）" % n)


def check_version_tables() -> "list[tuple[str, str, str]]":
    """版本门控表与官方缺陷登记簿在不在。

    **为什么单列一段**：这两张表决定了"这个参数你的版本支持吗"这类判断
    能不能做。缺了它们，工具只能**降级为"版本未检查"** ——
    而用户看到 `OK` 会以为查过了。⇒ **必须在这里明说。**
    """
    out = []
    od = os.path.join(ROOT, "references", "official")

    # 版本门控表
    p = os.path.join(od, "_versions.tsv")
    if not os.path.exists(p):
        out.append(("ERROR", "版本门控表",
                    "**不存在** → 「这个标签你的版本支持吗」**完全不检查**。"
                    "生成它：python references/official/_extract_versions.py"))
    else:
        n_gate = 0
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                t = line.rstrip("\n").split("\t")
                if len(t) >= 3 and t[2] in ("available", "available_upto"):
                    n_gate += 1
        out.append(("OK", "版本门控表",
                    "%d 条**结构化**版本门槛（⚠️ 绝大多数标签官方**没标**版本 ⇒ "
                    "「没条目」只能读作「官方未标注」，"
                    "**不能**读作「所有版本都支持」。见 references/VERSIONS.md）"
                    % n_gate))

    # 官方缺陷登记簿
    p2 = os.path.join(od, "_known_issues.tsv")
    if not os.path.exists(p2):
        out.append(("WARN", "官方缺陷登记簿",
                    "不存在 → 「你那个版本有哪些已知 bug」查不了。"
                    "生成它：python references/official/_extract_known_issues.py"))
    else:
        n_all = n_open = 0
        with open(p2, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                t = line.rstrip("\n").split("\t")
                n_all += 1
                if len(t) >= 6 and t[5] == "open":
                    n_open += 1
        out.append(("OK", "官方缺陷登记簿",
                    "%d 条（其中**未修 %d 条**）。⚠️ 官方自称该列表 "
                    "**incomplete** ⇒ 没列出来的不代表没问题。" % (n_all, n_open)))

    # 官方版本页（Changelog / Known issues）
    for fn, desc in (("Changelog", "官方 Changelog（Release notes）"),
                     ("Known_issues", "官方 Known issues 原文")):
        if os.path.exists(os.path.join(od, "pages", fn + ".md")):
            out.append(("OK", desc, "已在 references/official/pages/%s.md" % fn))
        else:
            out.append(("WARN", desc,
                        "**没有镜像** ⇒ 版本相关的原始依据查不到。"
                        "抓它：python references/official/_fetch_named.py "
                        "--title \"%s\"" % fn.replace("_", " ")))
    return out


def check_case(directory: str) -> "list[str]":
    """顺手体检一个算例目录：它是不是一个 VASP 算例。"""
    lines = []
    inp = vc.discover_inputs(directory)
    have = [k for k in ("INCAR", "KPOINTS", "POSCAR", "POTCAR", "OUTCAR",
                        "OSZICAR", "vasprun") if inp.get(k)]
    lines.append("目录：%s" % inp["dir"])
    lines.append("读到的文件：%s" % (", ".join(have) if have else "（一个都没有）"))
    if not have:
        lines.append("⚠️ 这看起来不是一个 VASP 算例目录。")
        return lines
    if inp["POSCAR"]:
        try:
            p = vc.read_poscar(inp["POSCAR"])
            lines.append("结构：%s，%d 个原子，%s 坐标"
                         % (p.formula(), p.nions, p.mode))
        except SystemExit:
            lines.append("结构文件解析失败（见上面的错误）")
    if inp["KPOINTS"]:
        k = vc.read_kpoints(inp["KPOINTS"])
        lines.append("k 点：模式 %s，%s，网格 %s"
                     % (k.mode, k.scheme or "-", k.mesh))
    if inp["OUTCAR"]:
        lines.append("程序版本：%s" % (vc.outcar_version(inp["OUTCAR"]) or "?"))
        lines.append("OUTCAR 实际用的 ENCUT：%s eV"
                     % vc.outcar_encut(inp["OUTCAR"]))
    return lines


def main(argv=None) -> int:
    vc.setup_console()
    ap = argparse.ArgumentParser(
        prog="doctor.py",
        description="环境与脚本完整性自检（**新手第一步**）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=核心可用；1=有文件缺失；2=用法错误；3=Python 太旧。",
    )
    ap.add_argument("--dir", help="顺便体检这个算例目录")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    report = {"python": "", "scripts": [], "kb": [], "keyword_table": "",
              "case": [], "notes": []}
    problems = 0
    fatal = 0

    print("=" * 72)
    print("VASP 计算顾问 skill —— 环境自检")
    print("=" * 72)

    ok, msg = check_python()
    report["python"] = msg
    print("[%s] %s" % ("OK" if ok else "ERROR", msg))
    if not ok:
        fatal = 1

    print("\n── 脚本完整性（%d 个）──" % len(CORE_SCRIPTS))
    for level, name, msg in check_scripts():
        report["scripts"].append({"level": level, "name": name, "msg": msg})
        mark = {"OK": "OK  ", "MISSING": "缺失", "ERROR": "错误",
                "THIRDPARTY": "违约", "OPTIONAL": "可选"}.get(level, level)
        print("  [%s] %-18s %s" % (mark, name, msg))
        if level in ("MISSING", "ERROR", "THIRDPARTY"):
            problems += 1

    print("\n── 知识库文件 ──")
    core_missing = 0
    for level, name, msg in check_kb():
        report["kb"].append({"level": level, "name": name, "msg": msg})
        if level == "OK":
            continue
        print("  [%s] %-38s %s" % (level, name, msg))
        if level in ("MISSING", "ERROR"):
            problems += 1
            core_missing += 1
    if not any(x["level"] in ("MISSING", "ERROR") for x in report["kb"]):
        print("  全部就位")

    print("\n── 归属校验的关键字表 ──")
    level, name, msg = check_keyword_table()
    report["keyword_table"] = msg
    print("  [%s] %s" % (level, msg))
    if level != "OK":
        problems += 1

    print("\n── 版本意识（见 references/VERSIONS.md）──")
    for level, name, msg in check_version_tables():
        report.setdefault("versions", []).append(
            {"level": level, "name": name, "msg": msg})
        print("  [%-5s] %-24s %s" % (level, name, msg))
        if level == "ERROR":
            problems += 1
    print("  ⚠️ **本 skill 的知识来自不同世代的 VASP**：官方语料是 6.6 时代的，")
    print("     而 things to study 的 98 个真实算例**全部是 5.4.4**。")
    print("     报参数前**先确认版本**：OUTCAR 第一行，或 validate.py "
          "--vasp-version。")

    if args.dir:
        print("\n── 算例体检：%s ──" % args.dir)
        for line in check_case(args.dir):
            report["case"].append(line)
            print("  " + line)

    print("\n" + "=" * 72)
    if fatal:
        print("结论：**Python 版本太旧**，核心功能不可用。")
        print("      请升级到 Python 3.8 或更高。")
    elif problems == 0:
        print("结论：核心功能可用 ✓")
    else:
        print("结论：核心功能**部分可用**（%d 项有问题）。" % problems)
        print("      关键能力缺失时会**降级**而不是说谎 —— 见上面每条的说明。")
    print("=" * 72)

    print("\n下一步：")
    print("  1. 生成一套输入      python scripts/wizard.py")
    print("  2. 校验输入          python scripts/validate.py <算例目录> "
          "--potcar <POTCAR>")
    print("  3. 跑完后查结果      python scripts/compare.py <算例目录>")
    print("  4. 出错了想诊断      python scripts/diagnose.py <算例目录>")
    print()
    print("⚠️ 本工具**不检查有没有 VASP** —— 上面所有离线工具都不需要它。")
    print("   需要真程序的是 conformance/（见那里的 README）。")
    print("⚠️ 它**不检查网络、不检查你的算例对不对**。")

    if args.json:
        report["problems"] = problems
        print()
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if fatal:
        return EXIT_DEP
    if problems:
        return EXIT_USER
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
