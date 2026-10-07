#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_audit_gates.py —— **适用条件审计**：这句话在什么条件下才成立？

为什么需要它（本项目的一次真实事故）
====================================
用户报来一个真实失效：179 原子团簇、16 MPI rank、**没写 `NPAR`/`NCORE`**（走默认
`NCORE=1`）⇒ 每个 rank 独占一个 band 并独自完成整块 FFT ⇒ **第一次 SCF 就 `SIGSEGV`**。
调一行 `NPAR=2` 就好了。

**离线工具抓不到它**（`NPAR` 是合法标签、值域正常）。但真正要命的不是"抓不到"，
而是**知识库里躺着一条会把使用者引向反方向的东西**：

    learn_G1.md（照录 LVTHW 作者）：
      「VASP 都会输出一个大大的 WARNING 来吓唬你，**不用担心，无视即可**。
        但如果你的计算失败了，这个警告信息**或许**对你排查错误可能会有所帮助」

作者那句「无视即可」**在他自己的规模下是安全的**（中小体系、少核），
但它是**一个依赖规模的建议**，而 skill 把它当成**无条件建议**收进来了。
⇒ 使用者看到 `WARNING`、看到"权威说无视"，于是**跳过了唯一能救命的那一行**。

**结构缺陷的量化形态**（实测）：

| 维度 | 数量 |
|---|---|
| 证据标记（"**谁**说的"）：官方 201 / 讲义 283 / 答疑 131 / 算例 163 / … | **约 850 处** |
| 「适用条件」结构化字段（"**什么时候**成立"） | **0 处** |

⇒ **skill 只记来源，不记适用条件。** 于是"条件性建议"被当成"无条件事实"存进来，
**使用者看不出区别** —— 而这正是"顾问"失效的方式。

本脚本做什么
============
逐行扫消费层，把**看起来在给指令、却没写条件**的地方捞出来：

| 类别 | 形态 | 为什么可疑 |
|---|---|---|
| `A_defer` | 「无视即可」「不用担心」「可以忽略」 | **跟着权威转述进来的框定**，最可能压掉一条真信号 |
| `B_absolute` | 「一律」「总是」「从不」「绝对」 | 绝对化措辞几乎总是过度概括 |
| `C_value` | 「设成 N」「取 N」「用 N」+ 单位/数字 | **数值建议几乎都依赖规模/体系/站点** |
| `D_scale` | 「不适用」「受限于」「只能」 | 反向：已经在讲限制，但没给**边界在哪** |

对每条，再判它**附近有没有"条件门"**（`如果` / `当` / `适用于` / `规模` /
`体系` / `核数` / `原子数` / `版本` / `节点` / `>N` / `N 个原子` …）。

**没有门的** ⇒ 报告为"缺适用条件"。

⚠️ **它不是判据，是"该看的地方"清单。**
本脚本**看不懂语义**：一条建议完全可能隐含条件而无需写出来
（例如"`ISMEAR` 默认 0.2"是**官方定义**，不需要条件）。
⇒ 它产出的是**待人工裁定**的候选，不是一个分数。
   这一点与本项目其它护栏不同，**必须说清楚**，否则会变成"为了绿而绿"。

用法
----
    python _audit_gates.py                  # 全部
    python _audit_gates.py --kind A_defer   # 只看某一类
    python _audit_gates.py --file decide.md
    python _audit_gates.py --limit 40

退出码
------
0 = 跑完（**不代表通过** —— 这是审计工具，不是判据）
2 = 用法错误
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))

TARGETS = [
    ("references/decide.md", "A 决策库"),
    ("references/playbook.md", "F 实战手册"),
    ("references/course_learned.md", "B 课程综合"),
    ("references/course_notes.md", "C 速查"),
    ("references/VERSIONS.md", "V 版本层"),
]

# --- A：跟着权威转述进来的"框定" ---
PAT_DEFER = re.compile(
    r"无视即可|不用担心|可以忽略|忽略即可|无需担心|不必管|无所谓|"
    r"不重要|可无视")

# --- B：绝对化措辞 ---
#
# ⚠️ 这三条正则里**有两条方向相反地错过**（它们造成**漏报** —— 比误报更危险，
#    因为漏报是"该看的地方没被标出来"）。逐条实测核对过（见 CHANGELOG 的 CR-046）：
#
#   1. `绝对(?!值)` —— **这条其实是对的**：`绝对错的` 能匹配、
#      `取绝对值` 不匹配。（子 agent 的报告说它"漏掉 `绝对值`"，**方向说反了** ——
#      `绝对值` 是数学名词，**本就该排除**。核对报告里的技术断言时，
#      不能只信描述，要**跑一遍**。）
#   2. `永远(?!不)` —— **确实错**：`永远不要` / `永远不能` 是**最强**的
#      绝对化措辞，却被这条负向断言**全部排除**了。
#      ⇒ 去掉负向断言，`永远` 一律收进来（这一类的漏报代价高于误报）。
#      ⚠️ 同时把 `从不` 收回来 —— 它和 `从来不` 是同一个词族的两种写法，
#         早期版本只收了 `从来不`。
#   3. `只能` —— 中文里**既表"仅仅"、也表"仅限"**：
#      `只能知道主题`（仅仅，**不是**限制条件）
#      对比 `只能用于绝缘体`（仅限，**是**限制条件）。
#      ⇒ 收窄为**后接实义动词/介词**的用法。
PAT_ABSOLUTE = re.compile(
    r"一律|总是|从来不|从不|绝对(?!值)|永远|"
    r"普适|任何(?:体系|情况|时候)都|所有(?:体系|情况)都")

# --- C：数值建议（"设/取/用 + 数字"） ---
PAT_VALUE = re.compile(
    r"(?:设成|设为|取|用|写成|填)\s*\*{0,2}[=＝]?\s*"
    r"\d+(?:\.\d+)?(?:\s*[-–~]\s*\d+(?:\.\d+)?)?\s*"
    r"(?:eV|Å|A|核|个原子|cm-1|cm⁻¹|meV|THz|K|bar|GPa|%|倍)?")

# --- D：已经在讲限制，但没给边界 ---
#
# ⚠️ `只能` 收窄为「后接实义动词/介词」—— 中文里它同时表示"仅仅"与"仅限"：
#    只能知道主题（仅仅、**不是**限制条件）vs 只能用于绝缘体（仅限、**是**）。
#    早期写法裸收 `只能`，会把大量"仅仅"误当"限制条件"。
PAT_SCALE = re.compile(
    r"不适用|受限于|仅限于|不适合|"
    r"只能(?:算|用|取|做|在|是|给|选|跑|支持|用于|适用)")

# --- E：**文档维护条款**（宾语是"本文/本表"，不是 INCAR/计算）---
#
# ⚠️ 为什么单列这一类（第一轮实测反馈）：
#   第一轮审计的**最大单一误报源（9/52 ≈ 17%）**就是它 ——
#   `一律` 命中了大量"本文的指针**一律**按主题名给"、"机器细节**一律**不写"
#   这类**维护规矩**。它们的宾语是**文档**、不是计算参数，
#   所以问"适用条件是什么"是**问错了问题**。
#   ⇒ 但**不能一律排除**：这一类里恰恰有条目缺的是"**时效/边界**"
#     （例："本文的指针一律按主题名给"的前提**被它自己下一句推翻了** ——
#      见 `references/_GATE_AUDIT.md` 的 G-02）。
#   ⇒ 进 `E_meta` 类，**换一个问题问**：
#     「这条维护规则的前提现在还成立吗 / 边界划清了吗？」
PAT_META = re.compile(
    r"本(?:文|文件|表|层|节|手册|报告|库)|该(?:表|层)|"
    r"一律不(?:写|列|复制|收)|指针|引用格式|维护")

# --- 表格表头里出现这些词 ⇒ 这一行属于"已经带了条件列"的表 ---
PAT_TABLE_GATE_HEADER = re.compile(
    r"适用范围|适用条件|例外|反例|条件|不适用|限(?:制|定)")

# --- "条件门"：出现这些词，就认为这一行/邻域在讲条件 ---
PAT_GATE = re.compile(
    r"如果|若|当|一旦|适用于|适用条件|适用范围|规模|体系|原子数|核数|"
    r"节点|版本|VASP\s*[4-6]|大体系|小体系|≥|≤|大于|小于|超过|"
    r"取决于|看情况|分情况|前提|条件是|此时|这时|反例|例外")

NEIGHBOR = 3          # 上下各看几行算"邻域"

# ---------------------------------------------------------------------------
# ⭐ 规模敏感标签（见 `references/_GATES.md` §3）
#
# 为什么单列这一类（那次事故暴露的**结构性**教训）：
#   第一轮审计 52 条候选里，**提到 `NPAR`/`NCORE`/`KPAR`/核数/内存的 0 条** ——
#   不是漏扫，而是 `playbook.md` §0.13 的 `NCORE` 表**格式太规范**
#   （每行都有"适用范围"列）⇒ 被 `gated` **整表跳过**。
#   **而那张表恰好有一行把两列装反了、把"高内存"降级成了脚注。**
#   ⇒ **"条件写得好"可能只是"格式规范"。**
#
# 所以这一类**不走 gated 逻辑**：只要提到这些标签，
# 就要求它**在同一行/邻域内点明"后果随什么变"**（核数/原子数/内存/版本）。
# ---------------------------------------------------------------------------
SCALE_TAGS = re.compile(
    r"\b(NCORE|NPAR|KPAR|LREAL|NBANDS|NGX|NGY|NGZ|NGXF|NGYF|NGZF|"
    r"LPLANE|NSIM|IMAGES|SPRING|KSPACING)\b")

# "后果随什么变"的判据：出现这些词，就认为它标注了规模依赖
SCALE_DEP = re.compile(
    r"核数|rank|原子数|内存|栈|网格|节点|带宽|体系大小|规模|"
    r"可用\s*rank|√|sqrt|越大|越小|多核|单核|并行")


def _is_path_like(s: str) -> bool:
    """这一行是不是**在列文件名/路径**（而不是在给参数建议）？

    为什么需要（实测出来的**最大误报源**）：
      `references/official/pages/{…,NCORE,KPAR}.md` 这类"检索范围"行
      会因为含 `NCORE`/`KPAR` 而被 S 类命中 —— 但那是在**列文件名**，
      不是"告诉你 `NCORE` 该设多少"。
    判据：含 `/` 或 `.md` 或 `references` 或花括号展开 `{…}`。
    """
    return ("/" in s or ".md" in s or "references" in s or "{" in s)


def _is_quote_or_listing(s: str) -> bool:
    """这一行是不是**在引用原文**或**列表格**？

    为什么需要（与 `_is_path_like` 同源的第二大误报源）：
      `>` 开头是 Markdown **引用块** —— 里面是**官方原话或算例原文**，
      它**本来就不需要**"适用条件"（条件是被引对象的事，不是我们的处方）；
      表格行则多半在列"某模板用了什么"。

    ⚠️ 这与 `_table_context` **不同**：那个只看"表头有没有条件列"，
      这里只看"这一行是不是在引用/列举"。

    判据：行首是 `>`，或这一行是 Markdown 表格行（`|` 开头）。
    """
    return s.startswith(">") or s.startswith("|")


def _table_context(lines, i):
    """第 i 行是不是在**一张带「适用范围/例外」列的表**里。

    为什么需要（第一轮实测的**第二大误报源，8/52 ≈ 15%**）：
      `playbook.md` §0 的每张数值表**都有「适用范围」+「例外/反例」两列**，
      文件里还明文规定"两列缺一，这条数值就不许用"。
      **检测器逐行看，看不到"这一行属于一张有条件列的表"**，
      于是把表里每一行都报成"缺条件"。
    """
    j = i
    while j >= 0:
        s = lines[j].strip()
        if not s.startswith("|"):
            return False          # 出了表格范围
        if j == 0 or not lines[j - 1].strip().startswith("|"):
            return bool(PAT_TABLE_GATE_HEADER.search(s))   # 表格块的第一行
        j -= 1
    return False


def _in_code_fence(lines, i):
    """第 i 行是不是在 ``` 围栏内（代码块里的数字不是散文建议）。"""
    n = 0
    for j in range(0, i):
        if lines[j].lstrip().startswith("```"):
            n += 1
    return n % 2 == 1


def _has_gate(lines, i, n=NEIGHBOR):
    """第 i 行（0-based）上下 n 行里有没有"条件门"。"""
    lo, hi = max(0, i - n), min(len(lines), i + n + 1)
    for j in range(lo, hi):
        if PAT_GATE.search(lines[j]):
            return True
    return False


def scan(path: str, rel: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    hits = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("#!"):
            continue
        # ⚠️ 代码块里的行**不是散文建议**（第一轮实测：2 条误报来自围栏内）。
        if _in_code_fence(lines, i):
            continue
        # ⚠️ 在"带条件列的表"里的行，条件在**表头**，不在这一行
        #    （第一轮实测：这是第二大误报源，8/52 ≈ 15%）。
        in_gated_table = _table_context(lines, i)

        kinds = []
        # ⭐ S 类（规模敏感标签）**独立于 gated 逻辑**：
        #    只要提到这些标签、而邻域里**没有**说明"后果随什么变"，
        #    就报出来 —— 即使这一行在一张"格式规范"的表里。
        #    （那次事故里 §0.13 的表就是被 gated 整表跳过的。）
        if (SCALE_TAGS.search(s) and not _has_gate(lines, i, n=1)
                and not SCALE_DEP.search(s)
                and not _is_path_like(s)
                and not _is_quote_or_listing(s)):
            hits.append({
                "file": rel, "line": i + 1, "kind": "S_scale",
                "gated": False, "text": s, "in_table": False, "soft": False,
            })

        # E 类先判：宾语是"本文/本表"的**维护条款**，与计算参数是两类问题。
        # 归到 E 之后**不再进 A–D**（否则同一行会被两类重复报）。
        if PAT_META.search(s) and PAT_ABSOLUTE.search(s):
            kinds.append("E_meta")
        else:
            if PAT_DEFER.search(s):
                kinds.append("A_defer")
            if PAT_ABSOLUTE.search(s):
                kinds.append("B_absolute")
            if PAT_SCALE.search(s):
                kinds.append("D_scale")
            # C 类只在"整行不长"时算 —— 长段落里的数字多半是叙述而非建议
            if len(s) <= 160 and PAT_VALUE.search(s) and re.search(r"\d", s):
                kinds.append("C_value")
        if not kinds:
            continue
        gated = _has_gate(lines, i) or in_gated_table
        for k in kinds:
            hits.append({
                "file": rel, "line": i + 1, "kind": k,
                "gated": gated, "text": s,
                "in_table": in_gated_table,
                # ---------------------------------------------------------
                # ⭐ `A_defer`（"无视即可"类）**不参与 gated 过滤**。
                #
                # 为什么单开这条规矩（本项目的一次真实事故）：
                #   最早版本里，三条 `A_defer` 命中**全部被判成 gated 而滤掉** ——
                #   也就是说，**造成那次事故的那一类，在默认输出里根本看不见**。
                #   原因是 `_has_gate` 的邻域窗口（上下 3 行）太宽：
                #   "可以忽略"旁边常有一个"如果/当"，于是被判成"已带条件"。
                #
                # 但 A_defer 与 B/C/D **性质不同**：
                #   · B/C/D 是"给指令但没写条件" ⇒ 附近有条件就算写了；
                #   · **A_defer 是"叫你忽略某个信号"** —— 它的危险恰恰在于
                #     **读者看到了附近的那个条件，却没把它与"忽略"联系起来**。
                #     所以"附近有条件"**不构成豁免**，必须单独列出让人裁。
                #
                # ⇒ A_defer 一律保留，并用 `soft` 标出"附近有条件"这一事实。
                # ---------------------------------------------------------
                "soft": gated if k == "A_defer" else False,
            })
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_audit_gates.py",
        description="适用条件审计：找出「给了指令、没给条件」的地方",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="⚠️ 这是**审计工具不是判据**：它看不懂语义，只标出「该看的地方」。\n"
               "   「没有门」不等于「错了」—— 有些建议（如官方默认值）本就不需要条件。",
    )
    ap.add_argument("--kind", help="只看某一类：A_defer / B_absolute / C_value / D_scale")
    ap.add_argument("--file", help="只审一个文件（文件名或相对路径）")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--only-ungated", action="store_true", default=True)
    ap.add_argument("--show-gated", action="store_true",
                    help="连「已经写了条件」的也列出来（用于对照）")
    args = ap.parse_args(argv)

    allhits = []
    for rel, _desc in TARGETS:
        if args.file and args.file not in rel:
            continue
        h = scan(os.path.join(ROOT, rel), rel)
        if h:
            allhits.extend(h)

    if args.kind:
        allhits = [h for h in allhits if h["kind"] == args.kind]
    if not args.show_gated:
        # ⚠️ `A_defer` **不参与** gated 过滤（见 scan() 里的说明）——
        #    它正是造成那次事故的那一类，不能在默认输出里消失。
        allhits = [h for h in allhits
                   if h["kind"] == "A_defer" or not h["gated"]]

    # 统计
    from collections import Counter
    kc = Counter(h["kind"] for h in allhits)
    fc = Counter(h["file"] for h in allhits)
    print("=" * 78)
    print("适用条件审计 —— 「这句话在什么条件下才成立？」")
    print("=" * 78)
    print("扫描范围：%d 个消费层文件" % len(TARGETS))
    print()
    print("命中（**未标条件**的）：")
    for k in ("A_defer", "B_absolute", "C_value", "D_scale", "E_meta",
              "S_scale"):
        if kc.get(k):
            print("  %-12s %4d" % (k, kc[k]))
    print("  %-12s %4d" % ("合计", sum(kc.values())))
    print()
    print("按文件：")
    for f, n in fc.most_common():
        print("  %-34s %4d" % (f, n))
    print()

    # A 类最危险，先列
    order = {"A_defer": 0, "S_scale": 1, "B_absolute": 2, "C_value": 3,
             "D_scale": 4, "E_meta": 5}
    allhits.sort(key=lambda h: (order.get(h["kind"], 9), h["file"], h["line"]))
    cur = None
    for h in allhits:
        if h["kind"] != cur:
            cur = h["kind"]
            print("-" * 78)
            print("### %s" % cur)
            print("-" * 78)
        soft = "  ⚠️ 附近有条件（**仍列出来**：忽略类必须逐条裁）" \
            if h.get("soft") else ""
        print("  %s:%d%s" % (h["file"], h["line"], soft))
        print("      %s" % h["text"][:150])
    if len(allhits) > args.limit * 4:
        print("\n…… 共 %d 条，上面按类别列出。" % len(allhits))

    print()
    print("=" * 78)
    print("⚠️ **这是审计工具，不是判据。**")
    print("   · 它**看不懂语义**：一条建议完全可能隐含条件而无需写出来")
    print("     （例如「`ISMEAR` 默认 0.2」是**官方定义**，不需要条件）；")
    print("   · 「没有门」**不等于**「错了」，只等于「**该看一眼**」；")
    print("   · 它的用途是**缩小人工裁定的范围**，不是给出分数。")
    print("   裁定后该做什么：给那条建议补上**适用条件**，或明确它无条件。")
    print("   见 references/MAINTENANCE.md §8b「条件性建议的写法」。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
