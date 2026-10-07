#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_doc_consistency.py —— 文档口径一致性 + 泄漏扫描（**零依赖**）

两个功能，都很便宜，但都抓到过真问题。

功能一：**防数字漂移**
====================
历史事故（CP2K skill）：`SKILL.md` 同一页出现"23 类特征输入"与"生成 15 类输入"
两种说法；README 写"7 类模板"而实际 8 个。根因是**数字靠手写、没有单一真值来源**。

**做法：真值只在代码/目录里，本脚本实测后比对 —— 不硬编码真值。**

| 数字 | 真值来源 |
|---|---|
| 向导目标数 | `scripts/wizard.py` 的 `GOALS` |
| `validate.py` 检查项数 | 它的 `CHECK_DESCRIPTIONS` |
| `diagnose.py` 规则数 | 它的 `RULES` |
| 注入用例数 | `_inject_test.py` 的 `CASES` |
| 核心脚本数 | `scripts/*.py`（排除 `vasp_common.py`） |
| 官方页面数 | `references/official/pages/*.md` |
| 关键字表条数 | `references/official/_keywords.tsv` 的非注释行 |

因为它是**实测**而不是硬编码，所以不会随版本失效。

功能二：**泄漏扫描**（`--scan-leaks`）
===================================
扫全仓库，找三类**绝不该出现**的东西：

1. **`POTCAR` 内容** —— TITEL 行、`End of Dataset`、成片的赝势数据表；
2. **站点信息** —— 集群地址、队列名、核数上限、账号、机器绝对路径、
   `module load` 的具体模块版本；
3. **密钥/凭据** —— `BEGIN ... PRIVATE KEY`、token、password 字面量。

⚠️ **它必然会漏**（正则查不出"语义上的站点信息"）。所以它的定位是
"**便宜的第一道网**"，不是"保证干净"。真正的保证靠
`references/MAINTENANCE.md` 的规矩 + 人工审查。

用法
----
    python _doc_consistency.py            # 只查数字口径
    python _doc_consistency.py --list     # 先打印所有真值
    python _doc_consistency.py --scan-leaks
    python _doc_consistency.py --all      # 两样都做

退出码
------
0 = 一致且无泄漏 · 1 = 有口径不一致 或 发现泄漏 · 2 = 用法错误
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))

EXIT_OK, EXIT_BAD, EXIT_USAGE = 0, 1, 2


# ---------------------------------------------------------------------------
# 真值采集（**全部实测，不硬编码**）
# ---------------------------------------------------------------------------
def truth() -> dict:
    t = {}

    # 向导目标数（从源码 AST 里数 GOALS 的键）
    wp = os.path.join(ROOT, "scripts", "wizard.py")
    if os.path.exists(wp):
        tree = ast.parse(open(wp, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for tgt in node.targets:
                    if isinstance(tgt, ast.Name) and tgt.id == "GOALS" and \
                            isinstance(node.value, ast.Dict):
                        t["wizard_goals"] = len(node.value.keys)

    # validate.py 检查项 / diagnose.py 规则数（数 _reg(...) 调用）
    vp = os.path.join(ROOT, "scripts", "validate.py")
    if os.path.exists(vp):
        src = open(vp, encoding="utf-8").read()
        t["validate_checks"] = len(re.findall(r'^_reg\("', src, re.M))
    dp = os.path.join(ROOT, "scripts", "diagnose.py")
    if os.path.exists(dp):
        src = open(dp, encoding="utf-8").read()
        t["diagnose_rules"] = len(re.findall(r'^@_rule\("', src, re.M))

    # 注入用例数
    ip = os.path.join(ROOT, "_inject_test.py")
    if os.path.exists(ip):
        src = open(ip, encoding="utf-8").read()
        # ⚠️ **两种引号都要数** —— 早期只数双引号 `^@case\("`，
        #    而后来新增的用例按 CR-050 的规矩用了**单引号** ⇒
        #    真值**静默少报**（实际 51 条，报成 44 条）。
        #    这条 bug 的隐蔽处在于：**没有任何文档声称那个数字**，
        #    所以 `_doc_consistency.py` 自己也不会红 —— 它只是**悄悄给错真值**，
        #    而真值会被 `--list` 打印、被别人抄走。
        #    ⇒ 教训：**"没人声称"不等于"不需要对"**。
        t["inject_cases"] = len(
            re.findall(r'^@case\(\s*[\'\"]', src, re.M))

    # 核心脚本数（排除 vasp_common.py 与下划线开头的）
    sd = os.path.join(ROOT, "scripts")
    if os.path.isdir(sd):
        t["core_scripts"] = len([f for f in os.listdir(sd)
                                 if f.endswith(".py")
                                 and not f.startswith("_")
                                 and f != "vasp_common.py"])

    # 官方页面数 / 关键字表条数
    od = os.path.join(ROOT, "references", "official")
    pg = os.path.join(od, "pages")
    if os.path.isdir(pg):
        t["official_pages"] = len([f for f in os.listdir(pg)
                                   if f.endswith(".md")])
    kt = os.path.join(od, "_keywords.tsv")
    if os.path.exists(kt):
        n = 0
        for line in open(kt, encoding="utf-8"):
            if line.startswith("#") or not line.strip():
                continue
            n += 1
        t["keyword_rows"] = n

    # 原始素材：页数 / 段数 / 行数
    for tag in ("L1", "L2", "L3", "L4"):
        p = os.path.join(ROOT, "references", "raw", "%s.txt" % tag)
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read()
            t["%s_pages" % tag] = len(re.findall(r"^=+ PAGE \d+ =+", txt, re.M))
    for tag in ("D1", "D2", "D3", "D4"):
        p = os.path.join(ROOT, "references", "raw", "%s.txt" % tag)
        if os.path.exists(p):
            txt = open(p, encoding="utf-8").read()
            t["%s_paras" % tag] = len(re.findall(r"^=+ %s-P\d+ =+" % tag,
                                                 txt, re.M))
    return t


# 文档里"声称"的数字，用正则抓出来与真值比对。
# 只抓**明确的、容易漂移的**说法，不抓所有数字（那会全是噪声）。
CLAIM_PATTERNS = [
    (r"(\d+)\s*个主线阶段", "main_stages"),
    (r"(\d+)\s*条注入", "inject_cases"),
    (r"(\d+)\s*条用例", "inject_cases"),
    (r"(\d+)\s*个页面", "official_pages"),
    (r"(\d+)\s*条（?归属校验", "keyword_rows"),
    (r"(\d+)\s*条\s*$", None),
]


def check_claims(t: dict, fix: bool = False):
    """扫文档里的数字声称，与真值比对。

    返回 `(问题列表, 检查条数, 文档数)`。

    `fix=True` 时**把文档里的数字改成实测真值**（而不是只报错）。
    为什么要有这个模式：这条护栏的**价值在于"抓到漂移"**，
    但每次漂移都要人工去改 5 个地方，维护成本高到会让人
    干脆关掉这条检查。⇒ 提供一键同步，**但默认不修**（`fix=False`），
    让"改了什么"仍然是一次显式动作。
    """
    problems = []
    fixed = []
    n_checked = 0
    docs = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "things to study",
                                    "raw", "pages", "cases")
                       and not d.startswith(".")]
        for name in filenames:
            if name.endswith(".md"):
                docs.append(os.path.join(dirpath, name))

    # 明确的、单值可比的声称（**保守**：只查这几个最容易漂移的）
    def scan(rel, pattern, key, label):
        nonlocal n_checked
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            return
        actual = t.get(key)
        text = open(p, encoding="utf-8").read()
        lines = text.split("\n")
        changed = False
        for i, line in enumerate(lines, start=1):
            # 先收齐这一行里所有匹配的**捕获组区间**
            spans = []
            for m in re.finditer(pattern, line):
                n_checked += 1
                claimed = int(m.group(1))
                if actual is None or claimed == actual:
                    continue
                problems.append(
                    "%s:%d  声称「%s」= %d，实测 %s = %d"
                    % (rel, i, label, claimed, key, actual))
                spans.append(m.span(1))
            if fix and spans:
                # ⚠️ **必须从后往前替换**：从前往后会让后面 span 的偏移失效。
                # （早期版本用一个 `new` 变量跨行累积，多匹配时会写错位置 ——
                #  已改为"按行、倒序、只改捕获组"。）
                newline = line
                for a, b in sorted(spans, reverse=True):
                    newline = newline[:a] + str(actual) + newline[b:]
                lines[i - 1] = newline
                changed = True
        if changed:
            with open(p, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(lines))
            fixed.append(rel)

    scan("AGENTS.md", r"症状→处方\s*(\d+)\s*条", "playbook_symptoms",
         "症状→处方条数")
    scan("AGENTS.md", r"注入测试.*?(\d+)\s*条用例", "inject_cases",
         "注入用例数")
    scan("AGENTS.md", r"官方.*?(\d+)\s*个页面", "official_pages",
         "官方页面数")
    scan("AGENTS.md", r"关键字归属表.*?(\d+)\s*条", "keyword_rows",
         "关键字表条数")
    scan("README.md", r"(\d+)\s*个 wiki 页面", "official_pages",
         "官方页面数")
    scan("README.md", r"(\d+)\s*条关键字表", "keyword_rows", "关键字表条数")
    scan("README.md", r"症状→处方\s*\*{0,2}(\d+)\s*条", "playbook_symptoms",
         "症状→处方条数")
    scan("README.md", r"注入测试.*?(\d+)\s*条", "inject_cases", "注入用例数")
    # ⚠️ 判据**只认加粗的断言**（`**N 条规则**`）。
    #    早期写法是 `(\d+)\s*条规则`，会把**叙述性**的
    #    「原来那些规则……看 13 条规则」也当成"声称" ⇒ 假红。
    #    这类"描述 vs 断言"的混淆，与本项目 `_audit_gates.py`
    #    要审的是同一个毛病（见 CHANGELOG 的 CR-042）。
    scan("USAGE.md", r"\*\*(\d+)\s*条规则\*\*", "diagnose_rules",
         "诊断规则数")
    scan("USAGE.md", r"查\s*(\d+)\s*项", "validate_checks", "校验项数")
    scan("_inject_test.py", r"(\d+)\s*条用例", "inject_cases", "注入用例数")
    scan("CHANGELOG.md", r"约\s*(\d+)\s*条更正记录", "changelog_cr",
         "更正记录数")
    return problems, n_checked, len(docs), fixed


# ---------------------------------------------------------------------------
# 泄漏扫描
# ---------------------------------------------------------------------------
LEAK_PATTERNS = [
    # --- POTCAR ---
    (r"^\s*TITEL\s*=\s*PAW", "POTCAR 的 TITEL 行（POTCAR 内容不得入仓库）"),
    (r"^\s*End of Dataset\s*$", "POTCAR 的 End of Dataset 标记"),
    (r"^\s*VRHFIN\s*=", "POTCAR 的 VRHFIN 行"),
    (r"^\s*POMASS\s*=.*ZVAL\s*=", "POTCAR 的 POMASS/ZVAL 行"),

    # --- 密钥 / 凭据 ---
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "私钥内容"),
    (r"-----BEGIN RSA PRIVATE KEY-----", "RSA 私钥内容"),
    (r"^\s*(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*\S+",
     "凭据字面量"),

    # --- 站点信息 ---
    (r"#SBATCH\s+-p\s+(?!<<<)\S+", "真实队列名（应写成 <<<请填写>>>）"),
    (r"#SBATCH\s+--partition=\s*(?!<<<)\S+", "真实队列名"),
    (r"#SBATCH\s+--account=\s*(?!<<<)\S+", "真实账号"),
    # ⚠️ 这条要求 `module load` 后面**跟着一个看起来像模块名的 token**
    # （字母开头、含字母数字/下划线/点/斜杠，且不含中文）。
    # 早期版本写成 `module\s+load\s+(?!<<<)\S+`，于是把
    # 「……机器路径 / `module load` 的具体模块……」这类**规范文档里的说明文字**
    # 也报成了泄漏 —— 那是**假红**，而假红会让人学会忽略整个扫描。
    (r"module\s+load\s+(?!<<<)(?!`)[A-Za-z][\w./-]{1,60}",
     "具体的 module load（站点信息）"),
    (r"#PBS\s+-q\s+(?!<<<)\S+", "真实队列名（PBS）"),
    (r"\bssh\s+\w+@[\w.-]+", "真实的 ssh 目标"),
    (r"\bslurm-\d+\.out\b", "真实的作业号文件名"),
]

# 允许出现的例外（逐条列出理由，**不要用宽泛的白名单**）
LEAK_ALLOW = [
    # 这些是**规范文档**在说明"什么不许写"，必须能引用这些形态
    (r"_doc_consistency\.py$", "本脚本自身的检测模式"),
    (r"_inject_test\.py$", "注入测试里的示例数据"),
    (r"\.gitignore$", "列出要忽略的文件名"),
    (r"\.gitattributes$", "二进制文件类型声明"),
    # CHANGELOG 的**更正记录**里会**引用**它纠正的那个坏例子
    # （"泄漏扫描曾把 `module load python/3.6.6` 报成泄漏，而那其实是课程原文"）。
    # 那是**在说明一条规矩**，不是"我们写了一条站点信息"。
    # ⚠️ 排除 CHANGELOG 是**有意的**，理由同 references/raw：
    #    更正记录的价值恰恰在于**能引用错误本身**。
    (r"^CHANGELOG\.md$", "更正记录需要引用被纠正的坏例子"),
]

# ⚠️ `raw` 也被排除，理由是**它不是"我们写的东西"而是逐字归档的原文**：
# `references/raw/L*.txt` / `D*.txt` 里出现的任何模块名/路径/命令，
# 都是**原文在 2020 年这么写的**，我们按 MAINTENANCE 的铁律**不改它**。
# 同理 `learn_L*.md` 里会**引用**这些原文（并把它们标成"依赖特定环境"的坑）。
# 把归档层报成"泄漏"会制造永远消不掉的红灯 —— 那会让人学会忽略整个扫描。
# 这条排除是**有意**的，不是漏配。见 CHANGELOG 的更正记录 CR-018。
# ⚠️ `things to study2` 也必须排除 —— 它是**外部教程站点导出**
# （LVTHW 的 Hexo 源），里面有真实集群地址/账号/密钥命令，
# 以及 POTCAR 头部回显的教学示例。它已经写进 `.gitignore`（`things to study*/`），
# 所以**不是仓库内容**，扫描它只会刷出一堆"不用管"的红灯。
# 教训同 CR-018/024：**假红会让人学会忽略整个扫描。**
SKIP_DIRS = {".git", "__pycache__", "things to study", "things to study2",
             "official", "raw"}
SCAN_EXT = {".md", ".py", ".txt", ".tsv", ".sh", ".yml", ".yaml",
            ".gitignore", ".gitattributes", ""}


def scan_leaks():
    findings = []
    n_files = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext not in SCAN_EXT and name not in (".gitignore",
                                                    ".gitattributes"):
                continue
            p = os.path.join(dirpath, name)
            rel = os.path.relpath(p, ROOT)
            if any(re.search(pat, rel) for pat, _why in LEAK_ALLOW):
                continue
            # 大文件跳过（大文件多半是抓下来的官方原文，已在 SKIP_DIRS 里）
            try:
                if os.path.getsize(p) > 4 << 20:
                    continue
                with open(p, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            n_files += 1
            for i, line in enumerate(text.split("\n"), start=1):
                for pat, why in LEAK_PATTERNS:
                    if re.search(pat, line):
                        findings.append((rel, i, why, line.strip()[:100]))
    return findings, n_files


def check_workflow_fresh():
    '''`references/workflow.md` 是不是 `guide.py --export` 的最新产物？

    为什么需要（与"数字漂移"同一个思路）：
      `workflow.md` 是**生成物**，但人会手改它。
      手改之后 `guide.py --export` 一跑就覆盖 ⇒ **那次手改静默丢失**。
      ⇒ 加这条：重新生成一份到临时文件，与磁盘上的**逐字比**。
        不一致就红，并告诉怎么修。
    '''
    import subprocess
    import tempfile
    root = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(root, 'scripts', 'guide.py')
    dest = os.path.join(root, 'references', 'workflow.md')
    if not os.path.exists(script):
        return []
    if not os.path.exists(dest):
        return [('references/workflow.md', '缺失',
                 '跑 `python scripts/guide.py --export`')]
    try:
        with open(dest, encoding='utf-8') as fh:
            on_disk = fh.read()
    except OSError as e:
        return [('references/workflow.md', '读不到', str(e))]
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, 'workflow.md')
        r = subprocess.run([sys.executable, script, '--export', '--out', tmp],
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(tmp):
            return [('references/workflow.md', '生成失败',
                     (r.stderr or r.stdout or '')[-160:])]
        with open(tmp, encoding='utf-8') as fh:
            fresh = fh.read()
    if fresh == on_disk:
        return []
    return [('references/workflow.md', '已过期',
             '跑 `python scripts/guide.py --export`（**不要手改**：'
             '那是生成物，改了会被覆盖；要改内容请改 `scripts/guide.py` 的 STAGES）')]


def check_doc_paths():
    '''文档里提到的**仓库内路径**是否真的存在。

    为什么需要（同一条规矩的第五次应用）：本项目反复犯同一个错 ——
    **改了机制，却漏改引用那个机制的文档。**
    实例：CR-059 把原文备份移出仓库后，`AGENTS.md` 仍写
    「原文在 `references/raw/_lvthw_original/`」—— 那个目录已经不存在了。

    判据：扫消费层文档里的 `references/...` 路径引用，逐个查存在性。
    ⚠️ **只查"仓库内相对路径"**；`things to study/` 等外部路径跳过
       （它们在 `.gitignore` 里，本来就不该存在）。
    '''
    import re as _re
    docs = ['AGENTS.md', 'README.md', 'USAGE.md', 'NOTICE.md',
            'references/_ENTRY.md', 'references/_GATES.md',
            'references/_SYSTEMS.md', 'references/MAINTENANCE.md',
            'references/VERSIONS.md']
    rx = _re.compile(r'`(references/[\w./\-]+?)`')
    skip = ('things to study', '_lvthw_original')
    bad = []
    for d in docs:
        fp = os.path.join(ROOT, d)
        if not os.path.exists(fp):
            continue
        try:
            txt = open(fp, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        seen = set()
        for m in rx.finditer(txt):
            rel = m.group(1).rstrip('/')
            if rel in seen or any(k in rel for k in skip):
                continue
            seen.add(rel)
            # 允许通配与"模板占位符"
            #   · `*` `?` `{}` —— glob
            #   · `YYYYMMDD` / `YYYY-MM-DD` —— 日期模板
            #   · `<...>` —— 占位符
            #   · 全大写下划线的段（如 `SURVEY_...`）—— 变量名式模板
            # ⚠️ 早期只排除了 glob，于是把 `survey_YYYYMMDD.md` 这种
            #    **模板名**报成"路径不存在"（假红）。模板名本来就不该存在。
            if ('*' in rel or '?' in rel or '{' in rel or '<' in rel
                    or 'YYYY' in rel
                    or re.search(r'[A-Z]{4,}(?:_[A-Z0-9]+)+', rel)):
                continue
            full = os.path.join(ROOT, rel.replace('/', os.sep))
            if not os.path.exists(full):
                bad.append('%s → `%s`（不存在）' % (d, rel))
    return bad


def check_skill_scope():
    '''**skill 目录里不许出现构建过程产物 / 隐私信息。**

    为什么需要（见 `SKILL_SCOPE.md` 与 `CHANGELOG` CR-060）：
    本项目曾把「构建 skill 的任务书」留在 skill 目录里并推上了公开仓库，
    **而当时所有护栏都是绿的** —— 它们不检查"这个文件属于哪一类"。
    ⇒ 把分类写成可执行的检查。

    判据（**只查确定性高的，避免误报**）：
      ① 文件名含"提示词/构建/prompt/build-plan"之类 ⇒ 是构建任务书；
      ② 根目录出现 PUBLISH/HANDOFF 之类 ⇒ 是隐私/过程文件；
      ③ 文件内容含**本机绝对路径**或**远端仓库 owner/URL** ⇒ 隐私。
    '''
    import re as _re
    problems = []

    # ① 文件名黑名单（子串匹配）
    BAD_NAME = ('提示词', '构建', 'prompt', 'build-plan', 'PROMPT')
    # ② 根目录/近根目录的隐私文件名
    BAD_ROOT = ('PUBLISH', 'HANDOFF', 'PRIVATE', 'SECRET')
    # ⚠️ 例外：`_publish_prep.py` 是**发布前预处理工具**，
    #    在 `SKILL_SCOPE.md` 里明确归为 CONTRACT（留在 skill 内）。
    ROOT_OK = ('_publish_prep.py',)

    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in ('.git', '__pycache__',
                                              'things to study',
                                              'things to study2')]
        rel_dir = os.path.relpath(dp, ROOT)
        for fn in fns:
            rel = fn if rel_dir == '.' else os.path.join(rel_dir, fn)
            # ① 构建任务书
            if any(k in fn for k in BAD_NAME):
                problems.append('%s —— 文件名像**构建任务书**'
                                '（应放在 skill 之外，见 SKILL_SCOPE.md）' % rel)
                continue
            # ② 隐私文件名（只在浅层查，避免误伤官方页）
            if (rel_dir.count(os.sep) <= 1 and fn not in ROOT_OK
                    and any(k in fn.upper() for k in BAD_ROOT)):
                problems.append('%s —— 文件名像**隐私/发布文件**'
                                '（应放在 skill 之外，见 SKILL_SCOPE.md）' % rel)
                continue
            # ③ 归档层与官方层不查内容（逐字保留外部原文）
            if rel.startswith(('references' + os.sep + 'raw',
                               'references' + os.sep + 'official')):
                continue
            if not fn.endswith(('.md', '.py')):
                continue
            # ⚠️ **跳过护栏脚本自身**：它们的判据字面量必然命中自己的判据
            #    （曾出现"判据扫到自己"的假阳性）。
            if fn in ('_doc_consistency.py', '_inject_test.py',
                      '_audit_citations.py', '_check_coverage.py',
                      '_validate_all_suites.py', '_publish_prep.py',
                      '_system_types.py', '_audit_gates.py'):
                continue
            try:
                txt = open(os.path.join(dp, fn), encoding='utf-8',
                           errors='replace').read()
            except OSError:
                continue
            # 本机绝对路径（盘符 + 反斜杠开头那种）
            m = _re.search(r'[A-Za-z]:\\[\w\\.-]{6,}', txt)
            if m:
                problems.append('%s —— 含**本机绝对路径** `%s`'
                                % (rel, m.group(0)[:40]))
                continue
            # 远端仓库 owner/repo（排除官方页里引用的公共 GitHub 项目）
            m = _re.search(r'github\.com[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?\b',
                           txt)
            if m and m.group(1).lower() not in ('vasp-dev', 'aradi', 'phonopy',
                                                'vossjo', 'ACEworksGmbH'):
                # 只报"看起来像本项目远端"的（出现在 clone/remote 语境）
                if _re.search(r'git\s+(clone|remote|push)\b', txt) or \
                   'git@github.com' in txt:
                    problems.append('%s —— 含**远端仓库地址** `%s`'
                                    % (rel, m.group(0)[:44]))
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_doc_consistency.py",
        description="文档口径一致性检查 + 泄漏扫描",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=一致且无泄漏；1=有不一致或发现泄漏；2=用法错误。",
    )
    ap.add_argument("--list", action="store_true", help="打印所有实测真值")
    ap.add_argument("--scan-leaks", action="store_true", help="做泄漏扫描")
    ap.add_argument("--all", action="store_true", help="两样都做")
    ap.add_argument("--fix", action="store_true",
                    help="把文档里的数字**改成实测真值**（默认只报不改）")
    args = ap.parse_args(argv)

    t = truth()
    # 更正记录数（真值在 CHANGELOG 里，但它自己就是记录本身）
    cl = os.path.join(ROOT, "CHANGELOG.md")
    if os.path.exists(cl):
        src = open(cl, encoding="utf-8").read()
        t["changelog_cr"] = len(re.findall(r"^### CR-\d+", src, re.M))
    # 排障手册的症状条数（数 S1–S73 这样的编号）
    pb = os.path.join(ROOT, "references", "playbook.md")
    if os.path.exists(pb):
        src = open(pb, encoding="utf-8").read()
        ids = set(re.findall(r"\bS(\d{1,3})\b", src))
        t["playbook_symptoms"] = len(ids)

    if args.list:
        print("实测真值（真值只在代码/目录里，本脚本不硬编码）：\n")
        for k in sorted(t):
            print("  %-22s %s" % (k, t[k]))
        return EXIT_OK

    bad = 0

    if not args.scan_leaks or args.all:
        print("=" * 72)
        print("文档口径一致性 —— 实测真值 vs 文档里的声称")
        print("=" * 72)
        problems, n_checked, n_docs, fixed = check_claims(t, fix=args.fix)
        print("扫了 %d 个 Markdown，检查了 %d 处数字声称。\n" % (n_docs, n_checked))
        if fixed:
            print("── 已按实测真值**改写**：%s ──\n" % ", ".join(fixed))
        if problems and not args.fix:
            print("── **口径不一致（%d 处）** ──" % len(problems))
            for p in problems:
                print("  ✗ " + p)
            bad += 1
        elif not problems:
            print("── 口径一致：0 处不一致 ──")
        print()
        # --- 生成物防漂移：`references/workflow.md` ---
        sbad = check_skill_scope()
        if sbad:
            print("── **skill 目录里有不该在的文件（%d 处）** ──" % len(sbad))
            for b in sbad:
                print("  ✗ " + b)
            bad += 1
        else:
            print("── skill 目录内无构建产物 / 隐私信息 ──")
        print()
        pbad = check_doc_paths()
        if pbad:
            print("── **文档引用了不存在的路径（%d 处）** ──" % len(pbad))
            for b in pbad:
                print("  ✗ " + b)
            bad += 1
        else:
            print("── 文档里的仓库内路径引用全部存在 ──")
        print()
        wf = check_workflow_fresh()
        if wf:
            print("── **生成物已过期（%d 处）** ──" % len(wf))
            for path, why, how in wf:
                print("  ✗ %s：%s" % (path, why))
                print("     %s" % how)
            bad += 1
        else:
            print("── `references/workflow.md` 与 `guide.py` 一致 ──")
        print()
        print("真值速查（写文档时先 `--list` 查真值再照抄）：")
        for k in ("wizard_goals", "validate_checks", "diagnose_rules",
                  "inject_cases", "playbook_symptoms", "official_pages",
                  "keyword_rows", "changelog_cr"):
            if k in t:
                print("  %-22s %s" % (k, t[k]))
        print()
        print("⚠️ **本检查只覆盖少数几个「容易漂移」的数字**（见 CLAIM_PATTERNS）。")
        print("   它不追求覆盖全部数字 —— 那会全是噪声。新增数字时，")
        print("   请顺手在 check_claims() 里加一条。")

    if args.scan_leaks or args.all:
        if not args.scan_leaks or args.all:
            print()
        if args.all:
            print()
        print("=" * 72)
        print("泄漏扫描 —— POTCAR 内容 / 站点信息 / 凭据")
        print("=" * 72)
        findings, n_files = scan_leaks()
        print("扫了 %d 个文本文件。\n" % n_files)
        if findings:
            print("── **发现 %d 处可疑内容** ──" % len(findings))
            for rel, i, why, snippet in findings:
                print("  ✗ %s:%d  [%s]" % (rel, i, why))
                print("        %s" % snippet)
            bad += 1
        else:
            print("── 未发现可疑内容 ──")
        print()
        print("⚠️ **它必然会漏** —— 正则查不出「语义上的站点信息」。")
        print("   它的定位是「**便宜的第一道网**」，不是「保证干净」。")
        print("   真正的保证靠 references/MAINTENANCE.md 的规矩 + 人工审查。")
        print("   已知不扫：things to study/（外部资料）、references/official/（官方原文）、")
        print("             references/raw/（**逐字归档的原文** —— 里面的命令/模块名是"
              "原文这么写的，按铁律不改）。")

    print()
    print("-" * 72)
    if bad:
        print("结论：**有 %d 类问题**，见上。" % bad)
    else:
        print("结论：口径一致、无泄漏。")
    return EXIT_BAD if bad else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
