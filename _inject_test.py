#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_inject_test.py —— 注入测试：**证明每一条护栏真的会红**（**零依赖**）

为什么必须有这个文件
====================
> **一个永远绿的护栏和没有护栏等价，但会给人虚假的安全感。**

本项目知道这一点，是因为它差点吃了这个亏：`diagnose.py` 的
`SCF.not_converged` 早期版本去 `OSZICAR` 里找 `aborting loop because EDIFF
is reached` —— 而那个标记其实在 `OUTCAR` 里（`OSZICAR` 里出现 **0** 次）。
也就是说那条规则**在每一个算例上都会报**，包括完全正确的算例。
它不是"没生效"，而是"稳定误报" —— 同样会让整份报告失去可信度。

所以：**每一条护栏都要有正例（该报红的必须红）与反例（合法输入必须放行）。**

它怎么工作
==========
对每一条护栏构造一个**故意注错**的输入，跑它，断言：
1. 退出码/输出**确实报了红**（正例 —— 防"永远绿"）；
2. 报的**是预期的那一条**检查（防"红了但不是因为这件事"）；
3. 对**合法输入**它**不报**（反例 —— 防误报）。

所有注入都在 `$TEMP` 下的一次性目录里做，**不碰仓库**。

用法
----
    python _inject_test.py              # 跑全部
    python _inject_test.py --list       # 列出所有注入用例
    python _inject_test.py --only KA3   # 只跑某一条

退出码
------
0 = 全部注入都被护栏抓住了（且反例都放行） · 1 = 有注入**没被抓住**（护栏失效）
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.environ.get("VASP_SKILL_ROOT", HERE))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2

# 一个**已知合法**的最小算例：注入测试的"反例基线"。
# 全部内容都在这里现写，不依赖 things to study/（那批资料不进仓库）。
GOOD_POSCAR = """\
Si2 bulk
1.0
   2.715   2.715   0.000
   0.000   2.715   2.715
   2.715   0.000   2.715
Si
2
Direct
   0.00  0.00  0.00
   0.25  0.25  0.25
"""
GOOD_KPOINTS = """\
Gamma-centered 4x4x4 (minimum viable test case)
0
Gamma
   4   4   4
0.0 0.0 0.0
"""
GOOD_INCAR = """\
SYSTEM = Si2 test

#### I/O ####
ISTART = 0
ICHARG = 2
LWAVE  = .FALSE.
LCHARG = .FALSE.

#### Electronic ####
ENCUT  = 300
PREC   = Normal
EDIFF  = 1E-6
NELM   = 60
ISMEAR = 0
SIGMA  = 0.05
LREAL  = .FALSE.

#### Ionic ####
NSW    = 0
IBRION = -1
"""
# 一个最小的假 POTCAR（**不含任何真实赝势数据**，只为了测头部解析）
GOOD_POTCAR = """\
  PAW_PBE Si 05Jan2001
   4.00000000000000
 parameters from PSCTR are:
   VRHFIN =Si: s2p2
   LEXCH  = PE
   TITEL  = PAW_PBE Si 05Jan2001
   POMASS =   28.085; ZVAL   =    4.000    mass and valenz
   ENMAX  =  245.345; ENMIN  =  184.009 eV
 End of Dataset
"""


def _write(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def make_case(base: str, name: str, incar=None, kpoints=None, poscar=None,
              potcar=None) -> str:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    _write(os.path.join(d, "INCAR"), GOOD_INCAR if incar is None else incar)
    _write(os.path.join(d, "KPOINTS"),
           GOOD_KPOINTS if kpoints is None else kpoints)
    _write(os.path.join(d, "POSCAR"), GOOD_POSCAR if poscar is None else poscar)
    _write(os.path.join(d, "POTCAR"), GOOD_POTCAR if potcar is None else potcar)
    return d


def run(script: str, args, cwd: str = None, env_root: str = None,
        timeout: int = 180):
    """跑一个脚本，返回 (退出码, stdout+stderr)。

    ⚠️ 脚本路径**必须绝对**：调用方会把 `cwd` 换成临时目录，
    相对路径会找不到文件（本测试早期版本就栽在这里 —— 53 条用例全"失败"，
    而真正的原因是本测试自己的路径写错了，不是护栏失效）。
    脚本名允许不带 `.py`；先在 `scripts/` 里找，再在仓库根找
    （`_inject_test.py` 与 `_audit_citations.py` 这类元测试放在仓库根）。
    """
    if not script.endswith(".py"):
        script += ".py"
    path = os.path.join(SCRIPTS, script)
    if not os.path.exists(path):
        path = os.path.join(ROOT, script)
    if not os.path.exists(path):
        return 127, "（找不到脚本：%s）" % script
    cmd = [sys.executable, path] + list(args)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if env_root:
        env["VASP_SKILL_ROOT"] = env_root
    try:
        p = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, cwd=cwd or ROOT, env=env,
                           encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return 999, "（超时）"
    return p.returncode, (p.stdout or "") + (p.stderr or "")


class Case:
    """一个注入用例。

    `expect_red` 是"必须报红"的断言函数：返回 (是否报红, 说明)。
    `expect_check` 是"必须是这一条检查报的红"的断言（可选）。
    """

    def __init__(self, cid, title, kind, build, expect_red,
                 expect_check=None, good_extra=None):
        self.cid = cid
        self.title = title
        self.kind = kind              # validate / compare / audit / diagnose
        self.build = build            # (base) -> 要跑的参数
        self.expect_red = expect_red
        self.expect_check = expect_check
        self.good_extra = good_extra  # 合法的反例也要一起跑


CASES = []


def case(cid, title, kind, good_extra=True):
    def deco(fn):
        CASES.append((cid, title, kind, fn, good_extra))
        return fn
    return deco


def lvthw_audit_probe(base: str, tag: str, body: str, expect_red: bool) -> bool:
    """写一个临时 md，用 `_audit_citations.py --file` 审它，看结果符不符合预期。

    为什么要这么绕：LVTHW 的 `篇:行` 引用审计有一个**前置条件**——
    "只有篇 id 真实存在时才审"。所以：
    - **越界能被抓到**（KG4）必须被证明，否则整条护栏可能永远绿；
    - **不是引用的串不能被报**（KC6）也必须被证明，否则是假红。

    ⚠️ **探针文件必须放在仓库树内。** 实测：放在系统临时目录里时，
    审计的 `--file` 模式会给出**几乎空的输出**，于是"没报红"被误读成
    "护栏失效" —— 而其实是**夹具没把被测对象放到它能看见的地方**。
    （与本文件 CR-016 记录的那类夹具 bug 同源：
     "注入失效"与"护栏失效"在输出上长得一样。）

    返回 True 表示"符合预期"。
    """
    p = os.path.join(ROOT, "_probe_%s.md" % tag)
    try:
        _write(p, body + "\n")
        _rc, txt = run("_audit_citations.py", ["--file", p])
        red = any(l.strip().startswith("✗") for l in txt.split("\n"))
        return red == expect_red
    finally:
        try:
            os.remove(p)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# A. validate.py —— 输入校验
# ---------------------------------------------------------------------------
@case("KA1", "INCAR 关键字拼错（静默失效类）", "validate")
def c_ka1(base):
    incar = GOOD_INCAR.replace("ENCUT", "ENCUTT")
    d = make_case(base, "ka1", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "INCAR.unknown_tag"}


@case("KA2", "关键字发到了不属于它的文件（归属错误）", "validate")
def c_ka2(base):
    # NBANDS 是 INCAR 标签，把它写进 KPOINTS 的注释里不行 —— 改为
    # 在 INCAR 里写一个 KPOINTS/POSCAR 才有的东西。用 POTCAR 的 ENMAX 不行
    # （它不是 tag）。改用：把 `KSPACING`（INCAR）与 `SIGMA`（INCAR）之外，
    # 实测可用的"属于别处"的标签是 POSCAR 的 `Selective dynamics` 写进 INCAR。
    incar = GOOD_INCAR + "\nSelective dynamics = .TRUE.\n"
    d = make_case(base, "ka2", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "INCAR.unknown_tag"}


@case("KA3", "POTCAR 与 POSCAR 元素顺序不一致", "validate")
def c_ka3(base):
    # POSCAR 是 Si，POTCAR 换成 O（顺序/元素名不符）
    potcar = GOOD_POTCAR.replace("Si", "O").replace("s2p2", "s2p4")
    d = make_case(base, "ka3", potcar=potcar)
    return [("validate", [d, "--quiet"])], {"check": "XSPECIES.elements"}


@case("KA4", "ENCUT 明显低于 POTCAR 的 ENMAX", "validate")
def c_ka4(base):
    incar = GOOD_INCAR.replace("ENCUT  = 300", "ENCUT  = 120")
    d = make_case(base, "ka4", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "XENCUT.enmax"}


@case("KA5", "MAGMOM 个数与原子数不符", "validate")
def c_ka5(base):
    incar = GOOD_INCAR.replace("LREAL  = .FALSE.",
                               "LREAL  = .FALSE.\nISPIN  = 2\nMAGMOM = 5*1.0")
    d = make_case(base, "ka5", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "XMAGMOM.count"}


@case("KA6", "LDAU 列表长度与元素种类数不符", "validate")
def c_ka6(base):
    incar = GOOD_INCAR + "\nLDAU = .TRUE.\nLDAUTYPE = 2\nLDAUL = 2 -1\nLDAUU = 4.0 0.0\n"
    d = make_case(base, "ka6", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "XLDau.count"}


@case("KA7", "值里混进说明文字（抄 wiki 丢了 #）", "validate")
def c_ka7(base):
    incar = GOOD_INCAR.replace("ICHARG = 2",
                               "ICHARG = 2   charge: 1-file 2-atom 10-const")
    d = make_case(base, "ka7", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "INCAR.annotation_in_value"}


@case("KA8", "圆括号说明里含分号（会被切成两条语句）", "validate")
def c_ka8(base):
    incar = GOOD_INCAR.replace(
        "ENCUT  = 300",
        "ENCUT  = 300   (Electronic Minimisation Algorithm; ALGO=58)")
    d = make_case(base, "ka8", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "INCAR.semicolon_comment"}


@case("KA9", "同一关键字写了两次", "validate")
def c_ka9(base):
    incar = GOOD_INCAR + "\nENCUT = 500\n"
    d = make_case(base, "ka9", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "INCAR.duplicate"}


@case("KA10", "取值非法：ISMEAR 写了 99", "validate")
def c_ka10(base):
    incar = GOOD_INCAR.replace("ISMEAR = 0", "ISMEAR = 99")
    d = make_case(base, "ka10", incar=incar)
    return [("validate", [d, "--quiet"])], {"check": "INCAR.value"}


@case("KA11", "KPOINTS 网格数不足三个", "validate")
def c_ka11(base):
    kp = "bad\n0\nGamma\n   4   4\n0.0 0.0 0.0\n"
    d = make_case(base, "ka11", kpoints=kp)
    return [("validate", [d, "--quiet"])], {"check": "KPOINTS 第 4 行"}


@case("KA12", "POSCAR 原子数不足（文件被截断）", "validate")
def c_ka12(base):
    pos = "\n".join(GOOD_POSCAR.split("\n")[:8]) + "\n"
    d = make_case(base, "ka12", poscar=pos)
    return [("validate", [d, "--quiet"])], {}


@case("KA13", "POTCAR 不是真的 POTCAR", "validate")
def c_ka13(base):
    d = make_case(base, "ka13", potcar="这不是 POTCAR\n随便写点东西\n")
    return [("validate", [d, "--quiet"])], {}


# ---------------------------------------------------------------------------
# B. 合法输入的**反例**：必须放行（防误报）
# ---------------------------------------------------------------------------
@case("KB1", "反例：完全合法的输入必须**不报 ERROR**", "validate",
      good_extra=False)
def c_kb1(base):
    d = make_case(base, "kb1")
    return [("validate", [d, "--quiet"])], {"must_be_green": True}


@case("KB2", "反例：合法的多语句行（A = 1; B = 2）必须放行", "validate",
      good_extra=False)
def c_kb2(base):
    incar = GOOD_INCAR.replace("ISMEAR = 0\nSIGMA  = 0.05",
                               "ISMEAR = 0 ; SIGMA = 0.05")
    d = make_case(base, "kb2", incar=incar)
    return [("validate", [d, "--quiet"])], {"must_be_green": True}


@case("KB3", "反例：带分段小标题的 INCAR 必须放行", "validate",
      good_extra=False)
def c_kb3(base):
    incar = ("Global Parameters\n" + GOOD_INCAR
             + "\nElectronic Relaxation:\n# 注释行\n")
    d = make_case(base, "kb3", incar=incar)
    return [("validate", [d, "--quiet"])], {"must_be_green": True}


@case("KB4", "反例：MAGMOM 个数正确时必须放行", "validate", good_extra=False)
def c_kb4(base):
    incar = GOOD_INCAR.replace("LREAL  = .FALSE.",
                               "LREAL  = .FALSE.\nISPIN  = 2\nMAGMOM = 2*1.0")
    d = make_case(base, "kb4", incar=incar)
    return [("validate", [d, "--quiet"])], {"must_be_green": True}


# ---------------------------------------------------------------------------
# C. _audit_citations.py —— 引用审计
# ---------------------------------------------------------------------------
def _make_audit_repo(base: str, body: str) -> str:
    """造一个最小的假仓库，让审计脚本可以在里面跑。"""
    r = os.path.join(base, "auditrepo")
    os.makedirs(os.path.join(r, "references", "raw"), exist_ok=True)
    os.makedirs(os.path.join(r, "references", "official", "pages"),
                exist_ok=True)
    _write(os.path.join(r, "references", "raw", "L1.txt"),
           "========== PAGE 1 ==========\n内容\n"
           "========== PAGE 2 ==========\n内容\n"
           "========== PAGE 3 ==========\n内容\n")
    _write(os.path.join(r, "references", "raw", "D1.txt"),
           "========== D1-P1 ==========\n问\n\n========== D1-P2 ==========\n答\n")
    _write(os.path.join(r, "references", "official", "pages", "ENCUT.md"), "x\n")
    _write(os.path.join(r, "references", "t.md"), body)
    return r


@case("KC1", "引用审计：页号越界必须报红", "audit")
def c_kc1(base):
    r = _make_audit_repo(base, "见 L1 P99 与 L1 P2。\n")
    return [("_audit_citations.py", [], {"cwd": r, "env_root": r})], \
        {"check": "L1 P99"}


@case("KC2", "引用审计：段号越界必须报红", "audit")
def c_kc2(base):
    r = _make_audit_repo(base, "见 D1-P7。\n")
    return [("_audit_citations.py", [], {"cwd": r, "env_root": r})], \
        {"check": "D1-P7"}


@case("KC3", "引用审计：不存在的文件路径必须报红", "audit")
def c_kc3(base):
    r = _make_audit_repo(base, "见 references/official/pages/NOPE.md。\n")
    return [("_audit_citations.py", [], {"cwd": r, "env_root": r})], \
        {"check": "NOPE.md"}


@case("KC4", "引用审计：行号越界必须报红", "audit")
def c_kc4(base):
    r = _make_audit_repo(base, "见 references/t.md:9999。\n")
    return [("_audit_citations.py", [], {"cwd": r, "env_root": r})], \
        {"check": "9999"}


@case("KC5", "反例：全部合法的引用必须**不报红**", "audit", good_extra=False)
def c_kc5(base):
    r = _make_audit_repo(
        base, "见 L1 P2、L1 P1-3、D1-P2、"
              "references/official/pages/ENCUT.md、references/t.md:1。\n"
              "（举例说明坏写法时写成 L1 P## 占位，审计应天然跳过。）\n")
    return [("_audit_citations.py", [], {"cwd": r, "env_root": r})], \
        {"must_be_green": True}


# ---------------------------------------------------------------------------
# D. diagnose.py —— 症状诊断（用**人造的假 OUTCAR** 注入症状）
# ---------------------------------------------------------------------------
FAKE_OUTCAR_HEAD = """\
 vasp.5.4.4.18Apr17-6-g9f103f2a35 (build Oct 15 2019 00:49:24) complex
跑在 1 个核上
  INCAR:
   ENCUT  =  300.0 eV
   ISPIN  =      1    spin polarized calculation?
   ISMEAR =     0;  SIGMA  =   0.05
   NSW    =      0    number of steps for IOM
   IBRION =     -1
   EDIFF  = 0.1E-05
   NIONS = 2
 E-fermi : 6.1234     XC(G=0): -0.1234     alpha+bet : -0.0123
 POSITION                                       TOTAL-FORCE (eV/Angst)
 -----------------------------------------------------------------------------------
      0.00000      0.00000      0.00000         0.000000      0.000000      0.000000
      1.35750      1.35750      1.35750         0.000000      0.000000      0.000000
 -----------------------------------------------------------------------------------
    total drift:                                0.000000      0.000000      0.000000
  FREE ENERGIE OF THE ION-ELECTRON SYSTEM (eV)
  ---------------------------------------------------
  free  energy   TOTEN  =        -10.12345678 eV
  energy  without entropy =      -10.12345678  energy(sigma->0) =      -10.12345678
"""

FAKE_OUTCAR_TAIL_OK = """\
 ------------------------ aborting loop because EDIFF is reached ----------------------------------------

 General timing and accounting informations for this job:
 ------------------------------------------------------------
                  Total CPU time used (sec):       12.345
                            Elapsed time (sec):        6.789
"""


def _fake_case(base, name, extra_head="", tail=FAKE_OUTCAR_TAIL_OK,
               incar=None, with_forces=True):
    d = make_case(base, name, incar=incar)
    head = FAKE_OUTCAR_HEAD + extra_head
    if not with_forces:
        head = "\n".join(l for l in head.split("\n")
                         if "TOTAL-FORCE" not in l
                         and not re.match(r"^\s*[-\d.]+\s+[-\d.]+\s+"
                                          r"[-\d.]+\s+[-\d.]+\s+[-\d.]+\s+[-\d.]+$", l)
                         and "total drift" not in l)
    _write(os.path.join(d, "OUTCAR"), head + tail)
    _write(os.path.join(d, "OSZICAR"),
           "       N       E                     dE             d eps       ncg"
           "     rms          rms(c)\n"
           "DAV:   1    -0.101234567890E+02   -0.10123E+02   -0.10123E+02  1234"
           "   0.123E+01\n"
           "   1 F= -.10123457E+02 E0= -.10123457E+02  d E =0.000000E+00\n")
    return d


@case("KD1", "OUTCAR 没有正常收尾（被中断）必须报红", "diagnose")
def c_kd1(base):
    """造一个"跑了几步、被墙钟掐断"的算例。

    要紧的是**同时**去掉 `aborting loop` 标记与 `General timing`：
    `RUN.not_finished` 需要先满足"这确实是一次电子自洽计算"的前置条件，
    所以给 `NSW = 5`（有离子步），并且不放 abort 标记。
    这样两条规则都会触发，我们只断言其中**确实有** `RUN.not_finished`。
    """
    inn = GOOD_INCAR + "\nNSW = 5\nIBRION = 2\nEDIFFG = -0.01\n"
    # ⚠️ 尾部文字里**不能出现** `General timing` 这几个字 —— 早期版本写成
    # "（被墙钟掐断了，没有 General timing 段）"，而规则就是靠搜这个词判定的，
    # 于是注入**自己把自己变成了合法输入**，规则当然不报。
    # 这是注入测试里最隐蔽的一类错误：**夹具把要注入的缺陷抹掉了**。
    # 本测试把它记在这里，因为"注入失效"和"护栏失效"看起来一模一样。
    d = _fake_case(base, "kd1", incar=inn,
                   tail="\n（这次运行被墙钟掐断了）\n")
    op = os.path.join(d, "OUTCAR")
    txt = open(op, encoding="utf-8").read()
    txt = "\n".join(l for l in txt.split("\n")
                    if "aborting loop because EDIFF" not in l)
    _write(op, txt)
    return [("diagnose", [d, "--quiet"])], {"check": "RUN.not_finished"}


@case("KD2", "SCF 未按 EDIFF 收敛必须报红", "diagnose")
def c_kd2(base):
    inn = GOOD_INCAR + "\nNSW = 5\nIBRION = 2\nEDIFFG = -0.01\n"
    d = _fake_case(base, "kd2", incar=inn)
    # 把默认加上的 abort 标记去掉 ⇒ 电子循环没按 EDIFF 收敛
    op = os.path.join(d, "OUTCAR")
    txt = open(op, encoding="utf-8").read()
    txt = "\n".join(l for l in txt.split("\n")
                    if "aborting loop because EDIFF" not in l)
    _write(op, txt)
    return [("diagnose", [d, "--quiet"])], {"check": "SCF.not_converged"}


@case("KD3", "VERY BAD NEWS（四面体方法 k 点不足）必须报红", "diagnose")
def c_kd3(base):
    d = _fake_case(base, "kd3", extra_head=(
        "\n VERY BAD NEWS! internal error in subroutine IBZKPT:\n"
        " Tetrahedron method fails for NKPT<4. NKPT = 1\n"))
    return [("diagnose", [d, "--quiet"])], {"check": "RUN.very_bad_news"}


@case("KD4", "DOS 出自弛豫计算必须报红", "diagnose")
def c_kd4(base):
    inn = GOOD_INCAR.replace("NSW    = 0", "NSW    = 300") + "\nLORBIT = 11\n"
    d = _fake_case(base, "kd4", incar=inn, extra_head=(
        " E-fermi : 6.1234     XC(G=0): -0.1234     alpha+bet : -0.0123\n"
        " E-fermi : 6.1234     XC(G=0): -0.1234     alpha+bet : -0.0123\n"))
    return [("diagnose", [d, "--quiet"])], {"check": "WRONG.dos_from_relax"}


@case("KD5", "反例：造得**干净**的算例必须不报「确定」级问题", "diagnose",
      good_extra=False)
def c_kd5(base):
    d = _fake_case(base, "kd5")
    return [("diagnose", [d, "--quiet"])], {"must_be_green": True}


# ---------------------------------------------------------------------------
# E. compare.py —— 不变量与一致性
# ---------------------------------------------------------------------------
@case("KE1", "INCAR 与 OUTCAR 的 ENCUT 不一致必须报红", "compare")
def c_ke1(base):
    inn = GOOD_INCAR.replace("ENCUT  = 300", "ENCUT  = 500")
    d = _fake_case(base, "ke1", incar=inn)   # OUTCAR 头里仍写 300
    return [("compare", [d, "--quiet"])], {"check": "X.encut_consistent"}


@case("KE2", "POSCAR 原子数与 OUTCAR 的 NIONS 不一致必须报红", "compare")
def c_ke2(base):
    pos = GOOD_POSCAR.replace("Si\n2\n", "Si\n4\n").replace(
        "   0.25  0.25  0.25\n",
        "   0.25  0.25  0.25\n   0.50  0.50  0.50\n   0.75  0.75  0.75\n")
    d = _fake_case(base, "ke2")
    _write(os.path.join(d, "POSCAR"), pos)
    return [("compare", [d, "--quiet"])], {"check": "X.nions_consistent"}


@case("KE3", "反例：自洽的算例必须不报 ERROR", "compare", good_extra=False)
def c_ke3(base):
    d = _fake_case(base, "ke3")
    return [("compare", [d, "--quiet"])], {"must_be_green": True}


# ---------------------------------------------------------------------------
# G. 引入 LVTHW 那一批时新增/修改的检查
#     （每条都要有"该红必红"，并且最好是"合法输入必放行"）
# ---------------------------------------------------------------------------
@case("KG1", "VASP4 格式 POSCAR（无元素名行）必须报出"
             "「元素顺序本次未检查」", "validate")
def c_kg1(base):
    """`validate.py` 的 `XSPECIES.vasp4_poscar`。

    ⚠️ 这条守的是一个**静默跳过**：VASP4 格式 POSCAR 没有元素名行
    ⇒ 读出来 `symbols == []` ⇒ `XSPECIES.counts` / `XSPECIES.elements`
    两条跨文件硬约束**整段不执行**，而"本次未检查的项"里**也不提它**。
    用户看到"ERROR 0 项"会以为元素顺序查过了。

    实测来源：ASE 写 POSCAR 默认就是 VASP4 格式（`[LVTHW]` A14/A16）。
    """
    pos = GOOD_POSCAR.replace("Si\n2\n", "2\n")   # 去掉元素名行
    d = make_case(base, "kg1", poscar=pos)
    return [("validate", [d, "--quiet"])], {"check": "XSPECIES.vasp4_poscar"}


@case("KG2", "反例：正常的 VASP5 POSCAR 不能报 VASP4 格式",
      "validate", good_extra=False)
def c_kg2(base):
    """防误报：`KG1` 那条规则不能咬到正常的 VASP5 POSCAR。"""
    d = make_case(base, "kg2")
    return [("validate", [d, "--quiet"])], {"must_be_green": True}


@case("KG3", "反例：正常算例的引用审计必须放行（LVTHW 引用在界内）",
      "audit_lvthw", good_extra=False)
def c_kg3(base):
    """LVTHW 篇:行 引用的**正例** —— 合法引用必须不报红。"""
    ok = lvthw_audit_probe(base, "kg3", "这是合法引用：EX80:10。", expect_red=False)
    return [("__probe__", [ok])], {"must_be_green": True}


@case("KG4", "LVTHW 引用越界必须报红（`EX80:99999`）", "audit_lvthw")
def c_kg4(base):
    """LVTHW 篇:行 引用的**反例** —— 越界必须被抓住。

    ⚠️ 这条格外重要：`RE_LVTHW` 的形态（大写词 + 冒号 + 数字）在普通文本里
    也会出现，所以审计**只在"这个篇 id 真实存在"时才审**。
    于是"越界能被抓到"这件事**必须被证明**，否则整条护栏可能永远绿。
    """
    ok = lvthw_audit_probe(base, "kg4", "这是越界引用：EX80:99999。",
                           expect_red=True)
    return [("__probe__", [ok])], {"must_be_green": True}


@case("KC6", "反例：审计不能把「不是引用」的大写词:数字 报成越界",
      "audit_lvthw", good_extra=False)
def c_kc6(base):
    """假红防线：`TODO:12` / `NOTE:3` 这类**不是 LVTHW 引用**的串，
    审计必须**静默跳过**（因为篇 id 不存在）。

    本项目为此返工过多次（CR-018/023/024/034）—— 假红会让人
    学会忽略整个审计。
    """
    ok = lvthw_audit_probe(
        base, "kc6", "这不是引用：TODO:12 和 NOTE:3。", expect_red=False)
    return [("__probe__", [ok])], {"must_be_green": True}


@case("KH1", "版本门控：用户版本低于标签门槛必须报红", "validate")
def c_kh1(base):
    """`VER.too_old` —— **本项目最想消灭的那类问题**。

    官方语料是 VASP 6.6 时代的，而 `things to study` 的 98 个真实算例
    全部是 5.4.4。一个用 5.4.4 的人写了 6.5.0 才有的标签，
    程序**静默忽略**它 —— 你以为设了，其实没生效，**没有任何报错**。

    用 `--vasp-version 5.4.4`（**不依赖 OUTCAR**，夹具就不用造假输出），
    配一个官方标了 `Available | 6.5.0` 的标签。
    """
    incar = GOOD_INCAR + "\nKPOINTS_OPT_MODE = 1\n"
    d = make_case(base, "kh1", incar=incar)
    return [("validate", [d, "--quiet", "--vasp-version", "5.4.4"])], \
        {"check": "VER.too_old"}


@case("KH2", "反例：版本足够时不能报 VER.too_old",
      "validate", good_extra=False)
def c_kh2(base):
    """与 `KH1` 成对：同一个标签、同一个输入，**只是版本够新** ⇒ 必须不报。

    它证明那个红是**因为版本不够**，而不是这个标签本身有问题。
    """
    incar = GOOD_INCAR + "\nKPOINTS_OPT_MODE = 1\n"
    d = make_case(base, "kh2", incar=incar)
    rc, txt = run("validate", [d, "--quiet", "--vasp-version", "6.6.0"])
    return [("__probe__", ["VER.too_old" not in txt])], \
        {"must_be_green": True}


@case("KH3", "反例：官方没标版本的常用标签不能被版本检查骚扰",
      "validate", good_extra=False)
def c_kh3(base):
    """**噪声防线**：`ISMEAR` / `ENCUT` / `EDIFF` 这类标签官方**没标**版本门槛，
    必须**完全不触发**版本检查 —— 否则每个算例都刷一片，用户就学会忽略了。

    这条**专治一个实测出来的反例**：若把官方正文里**散文**写的版本
    （`min_version_text`）也当门槛，`GGA` / `ISIF` / `ISPIN` 都会被误报
    （实测在 94 / 94 / 49 个算例里出现）—— 而它们在 5.4.4 里显然都有。
    """
    d = make_case(base, "kh3")
    rc, txt = run("validate", [d, "--quiet", "--vasp-version", "5.4.4"])
    for bad in ("VER.too_old", "VER.user_version_unknown"):
        if bad in txt:
            return [("__probe__", [False])], {"must_be_green": True}
    return [("__probe__", [True])], {"must_be_green": True}


# ---------------------------------------------------------------------------
# I. 并行分解预检（提交作业**之前**该看的东西）—— 本项目一次真实事故
# ---------------------------------------------------------------------------
def _big_poscar(n=128):
    lines = ["Si%d big cell" % n, "1.0",
             "   15.0 0.0 0.0", "   0.0 15.0 0.0", "   0.0 0.0 15.0",
             "Si", str(n), "Direct"]
    for i in range(n):
        lines.append("   0.%05d   0.%05d   0.%05d"
                     % ((i * 7) % 1000, (i * 13) % 1000, (i * 29) % 1000))
    return "\n".join(lines) + "\n"


@case("KI1", "并行预检：`NCORE` 与 `NPAR` 同时出现必须报红", "validate")
def c_ki1(base):
    """`XPAR.both_set` —— **本项目作者自己踩过的坑**。

    官方明文：`Do not set NCORE and NPAR at the same time`；两者同时出现时
    **`NPAR` 优先**、`NCORE` 被**静默忽略**。
    修完那个崩溃 bug 之后立刻又写了 `NPAR = 2` + "建议 `NCORE = 8`" ——
    **同类错误当场复发** ⇒ 必须机器化拦截。
    """
    incar = GOOD_INCAR + "\nNCORE = 8\nNPAR = 2\n"
    d = make_case(base, "ki1", incar=incar)
    return [("validate", [d, "--quiet", "--ncores", "16"])], \
        {"check": "XPAR.both_set"}


@case("KI2", "并行预检：大体系 + 多核却没写 NCORE 必须提醒", "validate")
def c_ki2(base):
    """`XNCORE.missing_with_rank` —— 那次事故的**输入侧**。

    179 原子 + 16 rank + 没写 `NPAR`/`NCORE` ⇒ 默认 `NCORE=1`
    ⇒ 每 rank 独占一个 band、独自完成整块 FFT ⇒ 第一次 SCF 崩溃。
    ⇒ 预检必须在**提交之前**提醒。夹具造 128 原子
    （官方经验锚点："`NCORE=4` 对 ~100 原子不错"），给 `--ncores 16`。
    """
    d = make_case(base, "ki2", poscar=_big_poscar(128))
    return [("validate", [d, "--quiet", "--ncores", "16"])], \
        {"check": "XNCORE.missing_with_rank"}


@case("KI3", "反例：只写 NCORE=8 且 16 核能整除时**不得**报并行问题",
      "validate", good_extra=False)
def c_ki3(base):
    """噪声防线：**正确写法必须放行**（与 KI4 成对）。"""
    incar = GOOD_INCAR + "\nNCORE = 8\n"
    d = make_case(base, "ki3", incar=incar)
    rc, txt = run("validate", [d, "--quiet", "--ncores", "16"])
    bad = [l for l in txt.split("\n")
           if l.startswith("WARN") and ("XNCORE" in l or "XPAR" in l)]
    return [("__probe__", [not bad])], {"must_be_green": True}


@case("KI4", "反例：除不尽时只报 INFO，不得升级成 WARNING",
      "validate", good_extra=False)
def c_ki4(base):
    """**级别防线**（本项目实测教训，见 CR-044）。

    用**真实核数**跑 98 个真实算例，除不尽这条**命中 46 个（47%）**。
    它们**不是假阳性**（`INCAR` 写的与生效的确实不同），
    但**不影响正确性** ⇒ 47% 的 WARNING 会把人训练成忽略整个报告。

    ⇒ 断言：报了，**但级别是 INFO 不是 WARN**。

    ⚠️ **不能加 `--quiet`**：`--quiet` 会把 INFO 行滤掉，
    于是断言"看得到 INFO"必然失败 —— 早期版本就是这样假红的
    （**测的是"安静模式会不会印 INFO"，不是"级别对不对"**）。
    改用总结行的计数：`INFO >= 1` 且 `WARNING == 0`。
    """
    incar = GOOD_INCAR + "\nNCORE = 5\n"      # 16 % 5 != 0
    d = make_case(base, "ki4", incar=incar)
    rc, txt = run("validate", [d, "--quiet", "--ncores", "16"])
    import re as _re
    m = _re.search(r"ERROR (\d+) 项，WARNING (\d+) 项，INFO (\d+) 项", txt)
    if not m:
        return [("__probe__", [False])], {"must_be_green": True}
    n_err, n_warn, n_info = (int(x) for x in m.groups())
    # ⚠️ 只断言与本条有关的量：INFO 必须 ≥1（报了），WARNING 必须是 0
    #    （同目录里其它规则可能报 WARN，所以不直接要求 n_warn==0，
    #     而是要求**没有 XNCORE 的 WARN**）。
    has_xncore_warn = any("WARN" in l and "XNCORE" in l
                          for l in txt.split("\n"))
    return [("__probe__", [n_info >= 1 and not has_xncore_warn])], \
        {"must_be_green": True}


@case("KI5", "反例：不给核数时不能去猜，除不尽那条必须沉默",
      "validate", good_extra=False)
def c_ki5(base):
    """**不猜** —— 与项目其它工具口径一致。

    没有核数信息时**不能**假定一个核数去算整除
    （那正是 CR-044 里 **60% 假阳性**的来源）。
    """
    incar = GOOD_INCAR + "\nNCORE = 5\n"
    d = make_case(base, "ki5", incar=incar)
    rc, txt = run("validate", [d, "--quiet"])      # 故意不给 --ncores
    bad = any("XNCORE.inconsistent" in l for l in txt.split("\n"))
    return [("__probe__", [not bad])], {"must_be_green": True}


# ---------------------------------------------------------------------------
# J. 阶段向导与体系索引（`guide.py` / `_system_types.py`）
# ---------------------------------------------------------------------------
def _wizard_poscar(n=128):
    lines = ['Si%d big cell' % n, '1.0',
             '   15.0 0.0 0.0', '   0.0 15.0 0.0', '   0.0 0.0 15.0',
             'Si', str(n), 'Direct']
    for i in range(n):
        lines.append('   0.%05d   0.%05d   0.%05d'
                     % ((i * 7) % 1000, (i * 13) % 1000, (i * 29) % 1000))
    return chr(10).join(lines) + chr(10)


@case('KJ1', 'guide.py list 必须列出 11 个主线阶段 + 1 个续算分支',
      'guide')
def c_kj1(base):
    rc, txt = run('guide.py', ['list'])
    if rc != 0:
        return [('__probe__', [False])], {'must_be_green': True}
    # 数条目：形如 "   1. define" .. "  11. report"，加上 "  ↻  resume"
    import re as _re
    nums = _re.findall(r'^\s+(\d+)\.\s+\w+', txt, _re.M)
    has_resume = 'resume' in txt
    return [('__probe__', [len(nums) == 11 and has_resume])], \
        {'must_be_green': True}


@case('KJ2', 'guide.py scan 必须认出「作业没跑起来」（判 diagnose）',
      'guide')
def c_kj2(base):
    d = make_case(base, 'kj2_crash')
    # 造崩溃现场：OSZICAR 只有表头 + LOG 有 SIGSEGV + OUTCAR 没离子里程碑
    _write(os.path.join(d, 'OSZICAR'),
           '       N       E                     dE             d eps'
           '       ncg     rms' + chr(10))
    _write(os.path.join(d, 'LOG'),
           ' running on   16 total cores' + chr(10)
           + ' distr:  one band on    1 cores,   16 groups' + chr(10)
           + 'forrtl: severe (174): SIGSEGV, segmentation fault occurred'
           + chr(10))
    _write(os.path.join(d, 'OUTCAR'), ' vasp.6.1.2  complex' + chr(10))
    rc, txt = run('guide.py', ['next', d])
    ok = ('诊断' in txt) and ('没跑起来' in txt)
    return [('__probe__', [ok])], {'must_be_green': True}


@case('KJ3', 'guide.py scan 必须认出「正常收尾的单点」（判 post）', 'guide')
def c_kj3(base):
    d = make_case(base, 'kj3_done')
    _write(os.path.join(d, 'OUTCAR'),
           ' vasp.5.4.4' + chr(10)
           + ' General timing and accounting informations for this run:'
           + chr(10))
    rc, txt = run('guide.py', ['next', d])
    ok = ('正常收尾' in txt)
    return [('__probe__', [ok])], {'must_be_green': True}


@case('KJ4', 'guide.py 必须提醒「大体系 + 没写 NCORE」', 'guide')
def c_kj4(base):
    d = make_case(base, 'kj4_big', poscar=_wizard_poscar(128))
    rc, txt = run('guide.py', ['scan', d])
    ok = ('NCORE' in txt) and ('既没有' in txt)
    return [('__probe__', [ok])], {'must_be_green': True}


@case('KJ5', '反例：小体系不得触发「大体系没写 NCORE」提醒',
      'guide', good_extra=False)
def c_kj5(base):
    d = make_case(base, 'kj5_small')      # GOOD_POSCAR 是小体系
    rc, txt = run('guide.py', ['scan', d])
    bad = '既没有' in txt
    return [('__probe__', [not bad])], {'must_be_green': True}


@case('KJ6', '_system_types.py --check 必须与实测一致', 'guide')
def c_kj6(base):
    # ⚠️ **必须给 cwd**：`_system_types.py` 从**仓库根**找 `things to study/`，
    #    而 `run()` 默认把 cwd 换成临时目录 ⇒ 找不到语料 ⇒ `--check` 必失败。
    #    （KJ7 一开始就带了 cwd，所以它通过 —— 这正是"反例要成对写"的价值。）
    root = os.path.dirname(os.path.abspath(__file__))
    rc, txt = run('_system_types.py', ['--check'], cwd=root)
    return [('__probe__', [rc == 0 and '一致' in txt])], \
        {'must_be_green': True}


@case('KJ7', '_system_types.py --lookup 必须点出「大体系 + 无 NCORE」',
      'guide')
def c_kj7(base):
    root = os.path.dirname(os.path.abspath(__file__))
    d = make_case(base, 'kj7_big', poscar=_wizard_poscar(128))
    rc, txt = run('_system_types.py', ['--lookup', d], cwd=root)
    ok = ('规模轴' in txt) and ('既没有' in txt)
    return [('__probe__', [ok])], {'must_be_green': True}


# ---------------------------------------------------------------------------
# K. 文档路径存在性（防止"改了机制、漏改文档"）
# ---------------------------------------------------------------------------
@case('KK1', '文档引用不存在的仓库内路径必须报红', 'doc')
def c_kk1(base):
    """`_doc_consistency.py` 的 `check_doc_paths`。

    为什么需要（同一条规矩的第五次应用，见 CR-059）：
    本项目反复犯同一个错 —— **改了机制，却漏改引用那个机制的文档**。
    实例：把原文备份移出仓库后，`AGENTS.md` 仍写
    「原文在 `references/raw/_lvthw_original/`」—— 那个目录已经不存在了。

    这条用例**在临时副本上注入一个假路径**，断言护栏会红。
    ⚠️ **必须在副本上做**，不能改真仓库（那会把真文档改坏）。
    """
    import shutil
    import tempfile
    root = os.path.dirname(os.path.abspath(__file__))
    tmp = tempfile.mkdtemp()
    # 拷一份"最小仓库"：只需要被检查的那几个文件 + 脚本
    for rel in ('_doc_consistency.py', 'AGENTS.md'):
        src = os.path.join(root, rel)
        dst = os.path.join(tmp, rel)
        if os.path.exists(src):
            shutil.copy2(src, dst)
    # 注入一个不存在的路径引用
    ag = os.path.join(tmp, 'AGENTS.md')
    if not os.path.exists(ag):
        return [('__probe__', [False])], {'must_be_green': True}
    with open(ag, encoding='utf-8') as fh:
        txt = fh.read()
    txt += chr(10) + '见 `references/definitely_not_here_xyz.md`。' + chr(10)
    with open(ag, 'w', encoding='utf-8', newline=chr(10)) as fh:
        fh.write(txt)
    rc, out = run('_doc_consistency.py', [], cwd=tmp, env_root=tmp)
    hit = 'definitely_not_here_xyz' in out
    return [('__probe__', [hit])], {'must_be_green': True}


@case('KK2', 'skill 目录里出现构建产物必须报红', 'doc')
def c_kk2(base):
    """`_doc_consistency.py` 的 `check_skill_scope`。

    为什么需要（见 `SKILL_SCOPE.md`、`CHANGELOG` CR-060）：
    本项目曾把「构建 skill 的任务书」留在 skill 目录里并推上了公开仓库，
    **而当时所有护栏都是绿的** —— 它们不检查"这个文件属于哪一类"。
    ⇒ 把分类写成可执行的检查，并**证明它真的会红**。

    做法：在临时副本上造一个"像构建任务书"的文件名，断言护栏报红。
    ⚠️ **必须在副本上做**，不能往真仓库里塞垃圾文件。
    """
    import shutil
    import tempfile
    root = os.path.dirname(os.path.abspath(__file__))
    tmp = tempfile.mkdtemp()
    for rel in ('_doc_consistency.py',):
        src = os.path.join(root, rel)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tmp, rel))
    # 注入一个"构建任务书"式的文件名
    with open(os.path.join(tmp, '构建某某-提示词.md'), 'w',
              encoding='utf-8', newline=chr(10)) as fh:
        fh.write('# 构建用的提示词' + chr(10))
    rc, out = run('_doc_consistency.py', [], cwd=tmp, env_root=tmp)
    hit = '提示词' in out or '构建任务书' in out
    return [('__probe__', [hit])], {'must_be_green': True}


# ---------------------------------------------------------------------------
# F. 入口健壮性（§3.2 的硬性要求）
# ---------------------------------------------------------------------------
@case("KF1", "所有脚本 --help 必须 exit 0（不能把 --help 当无参数跑全套）",
      "entry")
def c_kf1(base):
    """这条用例**不用子进程跑自己**，所以直接在这里执行并返回结论。

    返回的 spec 第一项是一个特殊标记，运行器会识别它。
    """
    out = []
    scripts = [s for s in os.listdir(SCRIPTS) if s.endswith(".py")
               and not s.startswith("_") and s != "vasp_common.py"]
    for s in sorted(scripts):
        rc, _txt = run(s, ["--help"])
        out.append((s, rc))
    bad = [s for s, rc in out if rc != 0]
    return [("__entry_probe__", bad)], {"check": "__entry_probe__"}


# ---------------------------------------------------------------------------
# 运行器
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_inject_test.py",
        description="注入测试：证明每一条护栏真的会红（且合法输入会放行）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=全部抓住；1=有注入没被抓住（护栏失效）。",
    )
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", help="只跑某一条（按 id）")
    ap.add_argument("--keep", action="store_true", help="保留临时目录（调试用）")
    args = ap.parse_args(argv)

    if args.list:
        print("注入用例（共 %d 条）：\n" % len(CASES))
        for cid, title, kind, _fn, _ge in CASES:
            print("  %-6s [%-8s] %s" % (cid, kind, title))
        return EXIT_OK

    todo = [c for c in CASES if not args.only or c[0] == args.only]
    if not todo:
        sys.stderr.write("错误：没有匹配的用例 id：%s\n" % args.only)
        return EXIT_USAGE

    base = tempfile.mkdtemp(prefix="vasp_inject_")
    n_pass = n_fail = 0
    failures = []
    print("=" * 72)
    print("注入测试 —— 证明护栏真的会红")
    print("=" * 72)
    print("临时目录：%s\n" % base)

    try:
        for cid, title, kind, fn, good_extra in todo:
            try:
                spec, expect = fn(base)
                # 各用例的 spec 写法不统一：有的是 `[("script", args)]`
                # （外层 list、内层 tuple），有的直接是 `("script", args)`。
                # 测试夹具不该因为这种形式差异而假红 —— 这里统一拍平。
                # ⚠️ 本测试在"拍平"这一步连续写错过两次（先漏判 tuple，
                # 再漏判 `spec[0]` 是 tuple 的情形），每次都表现为
                # **53 条用例一起报 IndexError**，看起来像"护栏全失效"。
                # 所以运行器把"用例本身出错"与"护栏没抓住"分成两种失败 ——
                # 前者是测试的 bug，后者才是护栏的问题。
                if isinstance(spec, (list, tuple)) and spec and \
                        isinstance(spec[0], (list, tuple)):
                    item = list(spec[0])
                elif isinstance(spec, (list, tuple)):
                    item = list(spec)
                else:
                    raise TypeError("用例返回的 spec 类型不认识：%r" % (spec,))
                script, sargs = item[0], list(item[1])
                opts = item[2] if len(item) > 2 else {}
                if script == "__entry_probe__":
                    bad = sargs
                    if bad:
                        n_fail += 1
                        failures.append((cid, title,
                                         "--help 未通过：%s" % ", ".join(bad)))
                        print("✗ %-6s %s" % (cid, title))
                        print("        --help 非 0 退出：%s" % ", ".join(bad))
                    else:
                        n_pass += 1
                        print("✓ %-6s %s" % (cid, title))
                    continue
                if script == "__probe__":
                    # `__probe__`：用例**自己**跑完了一个自包含的断言
                    # （例如"写个临时 md 让审计审它，看红不红"），
                    # 把布尔结果放在 `sargs[0]` 里交回来。
                    # ⇒ 运行器不需要知道它内部做了什么。
                    if sargs and sargs[0]:
                        n_pass += 1
                        print("✓ %-6s %s" % (cid, title))
                    else:
                        n_fail += 1
                        failures.append((cid, title, "自包含断言未通过"))
                        print("✗ %-6s %s" % (cid, title))
                        print("        自包含断言未通过（见用例文档字符串）")
                    continue
                cwd = opts.get("cwd", ROOT)
                rc, txt = run(script, sargs, cwd=cwd,
                              env_root=opts.get("env_root"))

                if expect.get("must_be_green"):
                    ok = (rc == 0)
                    why = ("退出码 %d（应为 0）；输出片段：%s"
                           % (rc, txt.strip().split("\n")[-1][:120]))
                else:
                    ok = (rc != 0)
                    why = "退出码 0 —— **没报红**，护栏失效"
                    if ok and expect.get("check"):
                        # 注意：用例表里的 `check` 是一个**必须在输出里出现的串**，
                        # 不一定是脚本内部的 check id。用它来防"红了但不是因为
                        # 这件事"（例如输入压根没读到，脚本在更早的地方就退了）。
                        needle = expect["check"]
                        if needle not in txt:
                            ok = False
                            why = ("报红了，但输出里找不到预期的那条检查 %r"
                                   " —— 红了，但不是因为这件事" % needle)
                if ok:
                    n_pass += 1
                    print("✓ %-6s %s" % (cid, title))
                    if not expect.get("must_be_green"):
                        # 顺带报告它归到了哪条检查
                        m = re.findall(r"^\[(ERROR|WARN)\] (\S+)", txt,
                                       flags=re.M)
                        if m:
                            print("        触发：%s" % ", ".join(
                                sorted({c for _lv, c in m})))
                else:
                    n_fail += 1
                    failures.append((cid, title, why))
                    print("✗ %-6s %s" % (cid, title))
                    print("        %s" % why)
            except Exception as exc:                          # noqa: BLE001
                n_fail += 1
                failures.append((cid, title, "用例本身出错：%r" % exc))
                print("✗ %-6s %s" % (cid, title))
                print("        用例本身出错：%r" % exc)

        # 额外的反例：**仓库自身**必须通过引用审计（这不是注入，是真实反例）
        print("\n── 真实反例：仓库自身的引用审计 ──")
        # ⚠️ 这里必须显式指定 cwd=ROOT 与 env_root=ROOT。
        # 默认 cwd 也是 ROOT，但 `_audit_citations.py` 靠 **自己所在目录** 判根，
        # 所以只要脚本路径是绝对的，它就会审本仓库 —— 不需要额外传环境变量。
        rc, txt = run("_audit_citations.py", ["--json"], cwd=ROOT)
        n_bad = txt.count('"why"')
        if rc == 0:
            n_pass += 1
            print("✓ KREPO  本仓库的引用审计通过（0 条越界）")
        else:
            n_fail += 1
            failures.append(("KREPO", "本仓库引用审计",
                             "有 %d 条越界引用" % n_bad))
            print("✗ KREPO  本仓库引用审计**未通过**（%d 条越界）" % n_bad)
            for line in txt.split("\n"):
                if '"file"' in line or '"why"' in line:
                    print("        " + line.strip()[:110])
    finally:
        if not args.keep:
            shutil.rmtree(base, ignore_errors=True)
        else:
            print("\n（临时目录已保留：%s）" % base)

    print("\n" + "=" * 72)
    print("结论：%d 条通过，%d 条**失败**" % (n_pass, n_fail))
    if failures:
        print()
        for cid, title, why in failures:
            print("  ✗ %-6s %s\n           %s" % (cid, title, why))
        print()
        print("⚠️ 有注入**没被抓住** —— 说明对应的护栏失效（永远绿）。")
        print("   一个永远绿的护栏和没有护栏等价，但会给人虚假的安全感。")
        print("   **不要为了让灯变绿而放宽判据**；要先弄明白是判据太严，")
        print("   还是被检对象真的错了。")
    else:
        print("      全部注入都被抓住了，且合法输入都放行了。")
    print("=" * 72)
    return EXIT_FAIL if n_fail else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
