#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""_build_examples.py —— **现场生成** `examples/` 下的可运行输入（**零依赖**）

为什么要"现场生成"而不是"存静态文件"
====================================
CP2K skill 的实测教训：

> **静态卡片会过期** —— 生成器改了、卡片没跟着改，检查就在验证**历史**而不是**现在**。
> （一批旧卡片在生成器演进后开始报错，而仓库里**没有对应的生成器**，只能手工修。）

所以本仓库的做法是：**示例目录里放"生成脚本 + README"**，
输入文件由脚本**现场生成**，并且生成后**立刻调 `validate.py` 校验**
（生成物过期 ⇒ 校验立刻红）。

⚠️ **它不生成 `POTCAR`**（受许可保护）。所以 `validate.py` 会报一条 WARN
"本目录里没有 POTCAR" —— 那是**预期的**，示例 README 里写明了。
`--with-potcar <路径>` 可以让它用你自己的 `POTCAR` 做完整校验。

用法
----
    python examples/_build_examples.py              # 生成全部示例
    python examples/_build_examples.py --list       # 只列出会生成什么
    python examples/_build_examples.py --check      # 只校验已有的输入（不重新生成）
    python examples/_build_examples.py --example 02_ag_slab
    python examples/_build_examples.py --with-potcar <POTCAR 路径>

退出码
------
0 = 全部生成并通过 `validate.py`（可能带"缺 POTCAR"的 WARN）
1 = 有示例生成失败或校验报 ERROR · 2 = 用法错误
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, os.pardir))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)

EXIT_OK, EXIT_FAIL, EXIT_USAGE = 0, 1, 2


# ---------------------------------------------------------------------------
# 示例定义：每个都**极小**，目的是"跑起来 + 演示一个概念"，不是"算个真结果"
# ---------------------------------------------------------------------------
EXAMPLES = [
    {
        "dir": "01_si_bulk_static",
        "title": "Si 块体 · 单点",
        "teaches": "最小闭环：四件套齐了就能算。演示 Γ 居中 k 点、"
                   "绝缘体用 ISMEAR=0、单点用 NSW=0。",
        "goal": "bulk-static",
        "dim": "3d",
        "metal": False,
        "poscar": """Si2 bulk (diamond, primitive cell)
1.0
   2.7150000000   2.7150000000   0.0000000000
   0.0000000000   2.7150000000   2.7150000000
   2.7150000000   0.0000000000   2.7150000000
Si
2
Direct
   0.0000000000   0.0000000000   0.0000000000
   0.2500000000   0.2500000000   0.2500000000
""",
        "encut": 300.0,
        "kpoints": """Gamma-centered 6x6x6 (Si 块体)
0
Gamma
   6   6   6
0.0 0.0 0.0
""",
    },
    {
        "dir": "02_ag_slab_relax",
        "title": "Ag(111) slab · 几何优化（固定底层）",
        "teaches": "**Selective dynamics** 怎么用（底层 `F F F`、表层 `T T T`）、"
                   "金属用 `ISMEAR=1`、`ISIF=2`（**slab 不要用 3**）、"
                   "`LDIPOL`/`IDIPOL` 偶极修正。",
        "goal": "slab-relax",
        "dim": "2d",
        "metal": True,
        "poscar": """Ag(111) 3x3 slab, 3 layers, bottom layer fixed
1.0
   8.6820000000   0.0000000000   0.0000000000
   4.3410000000   7.5186960000   0.0000000000
   0.0000000000   0.0000000000  25.0000000000
Ag
27
Selective dynamics
Direct
   0.0000000000   0.0000000000   0.3200000000   F   F   F
   0.3333333333   0.3333333333   0.3200000000   F   F   F
   0.6666666667   0.6666666667   0.3200000000   F   F   F
   0.3333333333   0.0000000000   0.3200000000   F   F   F
   0.6666666667   0.3333333333   0.3200000000   F   F   F
   0.0000000000   0.6666666667   0.3200000000   F   F   F
   0.6666666667   0.0000000000   0.3200000000   F   F   F
   0.0000000000   0.3333333333   0.3200000000   F   F   F
   0.3333333333   0.6666666667   0.3200000000   F   F   F
   0.0000000000   0.0000000000   0.4200000000   T   T   T
   0.3333333333   0.3333333333   0.4200000000   T   T   T
   0.6666666667   0.6666666667   0.4200000000   T   T   T
   0.3333333333   0.0000000000   0.4200000000   T   T   T
   0.6666666667   0.3333333333   0.4200000000   T   T   T
   0.0000000000   0.6666666667   0.4200000000   T   T   T
   0.6666666667   0.0000000000   0.4200000000   T   T   T
   0.0000000000   0.3333333333   0.4200000000   T   T   T
   0.3333333333   0.6666666667   0.4200000000   T   T   T
   0.0000000000   0.0000000000   0.5200000000   T   T   T
   0.3333333333   0.3333333333   0.5200000000   T   T   T
   0.6666666667   0.6666666667   0.5200000000   T   T   T
   0.3333333333   0.0000000000   0.5200000000   T   T   T
   0.6666666667   0.3333333333   0.5200000000   T   T   T
   0.0000000000   0.6666666667   0.5200000000   T   T   T
   0.6666666667   0.0000000000   0.5200000000   T   T   T
   0.0000000000   0.3333333333   0.5200000000   T   T   T
   0.3333333333   0.6666666667   0.5200000000   T   T   T
""",
        "encut": 300.0,
        "kpoints": """Gamma-centered 5x5x1 (slab, 真空方向取 1)
0
Gamma
   5   5   1
0.0 0.0 0.0
""",
    },
    {
        "dir": "03_mos2_monolayer_optcell",
        "title": "单层 MoS₂ · 面内晶胞优化（OPTCELL）",
        "teaches": "**二维材料不能直接用 `ISIF=3`** —— 真空方向会被一起优化掉。"
                   "演示 `OPTCELL` 冻结真空方向，以及怎么核对它生效了"
                   "（`OPTCELL` **不在 `OUTCAR` 回显**，只能比 `POSCAR`/`CONTCAR`）。",
        "goal": "bulk-relax",
        "dim": "2d",
        "metal": False,
        "poscar": """MoS2 monolayer (1H), 15 A vacuum along c
1.0
   3.1660000000   0.0000000000   0.0000000000
  -1.5830000000   2.7418950000   0.0000000000
   0.0000000000   0.0000000000  18.4100000000
Mo  S
1   2
Direct
   0.3333333333   0.6666666667   0.5000000000
   0.6666666667   0.3333333333   0.5896000000
   0.6666666667   0.3333333333   0.4104000000
""",
        "encut": 300.0,
        "kpoints": """Gamma-centered 9x9x1 (2D material, 真空方向取 1)
0
Gamma
   9   9   1
0.0 0.0 0.0
""",
        "optcell": "100\n010\n000\n",
    },
    {
        "dir": "04_si_bulk_dos",
        "title": "Si 块体 · 态密度（PDOS）",
        "teaches": "DOS 的**正确姿势**：在**已优化的结构**上做**单点**（`NSW=0`）、"
                   "`ISMEAR=-5`（四面体，**必须 Γ 居中**）、`LORBIT=11` 写 `PROCAR`。"
                   "还演示了一条**无报错的错误**：用弛豫计算的 DOS 是错的。",
        "goal": "dos",
        "dim": "3d",
        "metal": False,
        "poscar": """Si2 bulk (diamond, primitive cell)
1.0
   2.7150000000   2.7150000000   0.0000000000
   0.0000000000   2.7150000000   2.7150000000
   2.7150000000   0.0000000000   2.7150000000
Si
2
Direct
   0.0000000000   0.0000000000   0.0000000000
   0.2500000000   0.2500000000   0.2500000000
""",
        "encut": 300.0,
        "kpoints": """Gamma-centered 12x12x12 (**四面体方法必须更密**)
0
Gamma
  12  12  12
0.0 0.0 0.0
""",
    },
    {
        "dir": "05_bad_inputs_demo",
        "title": "**故意写坏的输入** · 演示校验器能抓什么",
        "teaches": "**这个示例不要拿去算！** 它故意包含了四类真实踩过的缺陷，"
                   "用来演示 `validate.py` 报什么。"
                   "这是本 skill 最该被理解的一课：**`OK` 只覆盖它检查过的那一层**。",
        "goal": "bulk-static",
        "dim": "3d",
        "metal": False,
        "poscar": """Si2 bulk (diamond) —— 这个文件本身是对的
1.0
   2.7150000000   2.7150000000   0.0000000000
   0.0000000000   2.7150000000   2.7150000000
   2.7150000000   0.0000000000   2.7150000000
Si
2
Direct
   0.0000000000   0.0000000000   0.0000000000
   0.2500000000   0.2500000000   0.2500000000
""",
        "encut": 80.0,      # 故意低于 Si 的 ENMAX(245.345)
        "kpoints": """Gamma-centered 6x6x6
0
Gamma
   6   6   6
0.0 0.0 0.0
""",
        # 故意注入四类缺陷
        "incar_extra": """
#### 下面四行是**故意写坏的**，用来演示校验器（不要照抄）####
# ① 关键字拼错 —— 会被 VASP 静默忽略
ENCUTT = 300
# ② 关键字发到了不属于它的文件（Selective dynamics 属于 POSCAR）
Selective dynamics = .TRUE.
# ③ 值里混进说明文字（抄 wiki 时把 # 丢了）
ISTART = 1   job   : 0-new  1-cont  2-samecut
# ④ 圆括号说明里含分号 —— 圆括号不是注释，; 是语句分隔符
ALGO = Normal   (Electronic Minimisation Algorithm; ALGO=58)
""",
    },
]


# ---------------------------------------------------------------------------
def gen_incar(ex: dict) -> str:
    """按 `wizard.GOALS` 的同一份定义生成 INCAR（**不另写一份逻辑**）。"""
    sys.path.insert(0, SCRIPTS)
    from wizard import GOALS                       # noqa: E402
    g = GOALS[ex["goal"]]
    p = dict(g.params)

    metal = ex.get("metal", False)
    if metal:
        p["ISMEAR"], p["SIGMA"] = 1, 0.2
    elif ex["goal"] == "dos":
        p["ISMEAR"], p["SIGMA"] = -5, 0.05
    else:
        p["ISMEAR"], p["SIGMA"] = 0, 0.05
    p["ENCUT"] = ex.get("encut", 400.0)

    lines = [
        "#### examples/%s —— %s ####" % (ex["dir"], ex["title"]),
        "# 由 examples/_build_examples.py **现场生成**（不是静态文件，避免过期）。",
        "# 生成后会自动跑 scripts/validate.py 校验。",
        "SYSTEM = %s" % ex["dir"],
        "",
        "#### 起始参数 I/O ####",
        "ISTART = %s" % p.get("ISTART", 0),
        "ICHARG = %s" % p.get("ICHARG", 2),
        "LWAVE  = .FALSE.",
        "LCHARG = %s" % p.get("LCHARG", ".FALSE."),
    ]
    if "LORBIT" in p:
        lines.append("LORBIT = %s" % p["LORBIT"])
    if "NEDOS" in p:
        lines.append("NEDOS  = %s" % p["NEDOS"])
    lines += [
        "",
        "#### 电子步 ####",
        "ENCUT  = %s" % p["ENCUT"],
        "PREC   = Normal",
        "EDIFF  = %s" % ("%g" % p.get("EDIFF", 1e-6)),
        "NELM   = %s" % p.get("NELM", 300),
        "NELMIN = %s" % p.get("NELMIN", 5),
        "# 展宽：%s" % ("金属用 MP" if metal else
                        ("DOS 用四面体（**必须 Γ 居中**）"
                         if ex["goal"] == "dos" else "绝缘体用 Gaussian")),
        "ISMEAR = %s" % p["ISMEAR"],
        "SIGMA  = %s" % p["SIGMA"],
        "LREAL  = .FALSE.",
        "",
        "#### 离子步 ####",
        "NSW    = %s" % p.get("NSW", 0),
        "IBRION = %s" % p.get("IBRION", -1),
    ]
    if "ISIF" in p:
        lines.append("ISIF   = %s" % p["ISIF"])
    if "POTIM" in p:
        lines.append("POTIM  = %s" % p["POTIM"])
    if "EDIFFG" in p:
        lines.append("EDIFFG = %s" % p["EDIFFG"])
    lines.append("")
    if p.get("LDIPOL"):
        lines += ["#### 偶极修正（不对称 slab）####",
                  "LDIPOL = .TRUE.",
                  "IDIPOL = 3",
                  ""]
    lines += ["#### 并行（**与站点相关，请自己定**）####",
              "# NCORE = <<<请填写>>>",
              "# KPAR  = <<<请填写>>>",
              ""]
    if ex.get("incar_extra"):
        lines.append(ex["incar_extra"])
    return "\n".join(lines)


def gen_readme(ex: dict) -> str:
    return f"""# examples/{ex["dir"]} —— {ex["title"]}

## 这个例子教你什么

{ex["teaches"]}

## ⚠️ 它不是"生产算例"

每个示例都**极小**（2–27 个原子），目的是"**跑起来 + 演示一个概念**"，
**不是**"算一个能进论文的结果"。参数都是**起点**，不是收敛值。

{"## ⛔ 这个示例**故意写坏了**，不要拿去算！\n\n"
 "它包含四类真实踩过的缺陷，用来演示 `validate.py` 报什么。\n"
 "**这是本 skill 最该被理解的一课**：`OK` 只覆盖它检查过的那一层。\n"
 if ex["dir"].startswith("05") else ""}
## 文件

| 文件 | 说明 |
|---|---|
| `INCAR` | 由 `_build_examples.py` **现场生成** |
| `KPOINTS` | Γ 居中规则网格 |
| `POSCAR` | 极小结构 |
| `OPTCELL` | {"冻结真空方向的命令行（**不在 `OUTCAR` 回显**，只能比 `POSCAR`/`CONTCAR`）" if ex.get("optcell") else "—"} |
| **没有 `POTCAR`** | **受许可保护，不得再分发**。见下 |
| `README.md` | 本文件 |

## 用之前

### 1. 自己拼 `POTCAR`

```bash
# 顺序必须与 POSCAR 第 6 行的元素顺序**完全一致**
cat <你本地的赝势目录>/{"…/".join(dict.fromkeys(ex["poscar"].split(chr(10))[5].split()))}/POTCAR > POTCAR
```

> ⚠️ VASP 是**按位置**把 POTCAR 的数据集配给 POSCAR 的元素的，不按元素名匹配。
> 顺序错了，每个原子的赝势都是错的，而**程序不会报错**。

### 2. 校验

```bash
python scripts/validate.py examples/{ex["dir"]} --potcar examples/{ex["dir"]}/POTCAR
```

不带 `--potcar` 也能跑，但会报一条 WARN（"本目录里没有 POTCAR —— 与 POTCAR
相关的 5 项检查**本次未执行**"）。那是**预期的**。

### 3. 跑

本示例**不含** `submit.sh`（那是站点相关的）。
你可以：

- 直接 `mpirun -np N <你的 vasp_std>`；
- 或用 `python scripts/wizard.py --goal {ex["goal"]}` 生成一份带
  `submit.sh` 骨架的输入（所有站点相关的都写成 `<<<请填写>>>`）。

### 4. 跑完

```bash
python scripts/parse_output.py examples/{ex["dir"]}   # 数值
python scripts/compare.py      examples/{ex["dir"]}   # 自洽性 + 力平衡
python scripts/diagnose.py     examples/{ex["dir"]}   # 症状诊断
```

## 接下来读什么

| 你想知道 | 去哪 |
|---|---|
| 参数怎么选、代价是什么 | `references/decide.md` |
| 出错了怎么修 | `references/playbook.md` §1（73 条症状→处方） |
| 官方原话 | `references/official/pages/` |
| 真实生产算例长什么样 | `references/cases/` |

## 诚实声明

本示例的输入由 `examples/_build_examples.py` **现场生成**，
生成后自动跑 `scripts/validate.py` 校验。

**但"校验通过"只表示"检查过的那些项没发现问题"** ——
它**不**表示这套参数能算对。⚠️ **所有示例都没有在真机上跑过**
（构建环境没有 VASP）。你的第一次运行就是它的验证。
"""


def run(cmd):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT,
                       env=env, encoding="utf-8", errors="replace",
                       timeout=300)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def write(path, text):
    """**无 BOM、LF** 写出（硬要求）。"""
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def build(ex: dict, with_potcar=None, check_only=False):
    d = os.path.join(HERE, ex["dir"])
    os.makedirs(d, exist_ok=True)
    name = ex["dir"]
    if not check_only:
        write(os.path.join(d, "INCAR"), gen_incar(ex))
        write(os.path.join(d, "KPOINTS"), ex["kpoints"])
        write(os.path.join(d, "POSCAR"), ex["poscar"])
        if ex.get("optcell"):
            write(os.path.join(d, "OPTCELL"), ex["optcell"])
        write(os.path.join(d, "README.md"), gen_readme(ex))

    # **生成后立刻校验** —— 生成物过期 ⇒ 立刻红
    cmd = [sys.executable, os.path.join(SCRIPTS, "validate.py"), d, "--quiet"]
    if with_potcar:
        cmd += ["--potcar", with_potcar]
    rc, txt = run(cmd)
    lines = [l for l in txt.strip().split("\n") if l.strip()]
    concl = next((l for l in reversed(lines) if l.startswith("结论")), "")
    errs = [l for l in lines if l.startswith("ERROR")]
    return name, rc, concl, errs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="_build_examples.py",
        description="现场生成 examples/ 下的可运行输入，并立刻用 validate.py 校验",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="退出码：0=全部生成且无 ERROR；1=有失败；2=用法错误。",
    )
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="只校验已有输入，不重新生成")
    ap.add_argument("--example", help="只处理某一个（按目录名）")
    ap.add_argument("--with-potcar", help="用你自己的 POTCAR 做完整校验")
    args = ap.parse_args(argv)

    if args.list:
        print("示例（共 %d 个）：\n" % len(EXAMPLES))
        for e in EXAMPLES:
            print("  %-28s %s" % (e["dir"], e["title"]))
            print("      %s" % e["teaches"])
        return EXIT_OK

    todo = EXAMPLES
    if args.example:
        todo = [e for e in EXAMPLES if e["dir"] == args.example]
        if not todo:
            sys.stderr.write("错误：没有这个示例：%s\n" % args.example)
            return EXIT_USAGE

    print("=" * 72)
    print("示例 %s —— 现场生成 + 立刻校验" % ("校验" if args.check else "生成"))
    print("=" * 72)
    if not args.with_potcar:
        print("⚠️ 没有给 --with-potcar ⇒ POTCAR 相关的 5 项检查**不会执行**，")
        print("   每个示例都会带一条 WARN。那是**预期的**（POTCAR 不得再分发）。\n")

    n_bad = 0
    for e in todo:
        name, rc, concl, errs = build(e, with_potcar=args.with_potcar,
                                      check_only=args.check)
        # 示例 05 是**故意写坏的**：它**应该**报 ERROR
        expect_bad = name.startswith("05")
        ok = (rc == 4) if expect_bad else (rc in (0, 5))
        if expect_bad:
            print("  %-28s %s" % (name, "✓ 如预期地报出了 ERROR"
                                  if rc == 4 else "✗ **没有报出 ERROR**"))
        else:
            print("  %-28s %s" % (name, "✓" if ok else "✗"))
        print("      %s" % concl)
        for l in errs[:6]:
            print("      " + l[:110])
        if not ok:
            n_bad += 1

    print()
    print("-" * 72)
    if n_bad:
        print("结论：**%d 个示例失败**。" % n_bad)
    else:
        print("结论：%d 个示例都符合预期。" % len(todo))
    print()
    print("⚠️ 生成物**没有在真机上跑过**（构建环境没有 VASP）。")
    print("   校验通过只表示「检查过的那些项没发现问题」。")
    print("   示例 05 是**故意写坏的**，用来演示校验器 —— **不要拿它去算**。")
    return EXIT_FAIL if n_bad else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
