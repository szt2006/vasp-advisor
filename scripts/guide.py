#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''guide.py —— **项目阶段向导**：我在哪个阶段？下一步做什么？

⚠️ **本文件的书写规矩（血泪教训，见 CHANGELOG 的 CR-050）**：
   本项目的文档里满是中文引号，而 Python 里如果**同时**用双引号做定界符，
   一次机械替换就会把字符串截断，而且**极难修回来**（试过，越修越坏）。
   ⇒ 所以本文件里：
     · **Python 字符串定界符一律用单引号**；
     · 正文里的引号一律用**中文直角引号**。
   这样**内容与定界符永远不可能冲突**。

为什么需要它
============
本 skill 原来能回答「参数怎么选」（`recommend.py`）、
「输入写对没有」（`validate.py`）、「跑完怎么读」（`parse_output.py`）、
「出了症状怎么办」（`diagnose.py`）。

**但它不能回答使用者最先问的那句话：「我现在该干什么？」**

具体表现：`AGENTS.md` 说本 skill「按 **11 个主线阶段 + 1 个续算分支**陪跑项目」
（`AGENTS.md:19`），而那 11 个阶段的名字只在 `AGENTS.md:191-192` 出现**一次** ——
**没有对应的工具，也没有逐阶段的指引文件。**
⇒ 那是一句**悬空的声称**（本项目最忌讳的东西）。
本文件把它**落实**：那 11 个阶段在这里被定义一次，并被 `scan` 真正用起来。

定位与边界（**必读**）
======================
本向导**不是**「自动跑命令的工作流」，也**不替你做决定**。它做的是：

1. 看你目录里**已经有什么**（**只读**，不改任何文件）；
2. 据此推断你**大概在哪个阶段**、**下一步最该做什么**；
3. 把该阶段的「决策点 / 常见坑 / 该跑的已有命令」列出来。

⚠️ **推断是启发式的**：本质是「按文件存在性判断」。
   所以每一处推断都会**打印它的依据**（看到了哪个文件），
   你可以直接推翻它。**它不猜、不含糊其辞。**

⚠️ **本文件不产生新知识**：每一阶段的内容都指向已有的知识条目
   （`decide.md` / `playbook.md` / `_SYSTEMS.md` / `_GATES.md`）。

用法
----
    python scripts/guide.py list                  # 列 11 个主线阶段 + 续算分支
    python scripts/guide.py show <阶段>           # 展开某阶段的完整指引
    python scripts/guide.py scan <目录>           # 推断「卡在哪、下一步做什么」
    python scripts/guide.py next <目录>           # 只要下一步（scan 的精简版）

退出码：0 正常 · 1 目录/文件问题 · 2 用法错误 · 3 缺依赖
'''

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import vasp_common as vc
except ImportError:                                          # pragma: no cover
    print('找不到 vasp_common.py —— 请从 skill 的 scripts/ 目录运行。')
    raise SystemExit(3)

EXIT_OK, EXIT_USER, EXIT_USAGE, EXIT_DEP = 0, 1, 2, 3


# ===========================================================================
# 一、11 个主线阶段 + 1 个续算分支
# ===========================================================================
# ⚠️ **这是全库唯一定义这 11 个阶段的地方**（名单来自 `AGENTS.md:191-192`）：
#    立项 / 建模 / 参数 / 收敛 / 优化 / 电子结构 / 动力学 / 反应路径 /
#    后处理 / 诊断 / 报告。
#    改这里就要同步 `AGENTS.md` 与 `USAGE.md`（`_doc_consistency.py` 会核对数量）。
#
# 每个阶段六类内容（与 `AGENTS.md` 的行为指引一致）：
#   goal —— 这个阶段要产出什么
#   do   —— 该做的动作
#   fork —— **决策点**（选错了会白算）
#   trap —— **常见坑**
#   cmd  —— 该跑的**已有**命令（不在这里发明新命令）
#   read —— 该读的**已有**知识条目
STAGES = [
    dict(key='define', n=1, title='立项与问题定义',
         first='先跑 `python _system_types.py --lookup <目录>` 确认体系类型与**规模** —— 规模决定并行配置，而并行配置决定作业能不能起来。',
         goal='把科学问题翻译成可计算的任务，并估清规模。',
         do=['明确要算的量（吸附能 / 反应能垒 / DOS / 频率 / 扩散系数…）',
             '判断体系类型与维度（体相 / slab / 分子 / 线状）',
             '粗估原子数与核数 ⇒ **决定并行配置**'],
         fork=['静态 vs 有限温（表面反应、扩散必须有限温）',
               '是否需要反应路径（NEB / Dimer）'],
         trap=['任务类型选错 ⇒ 整套白算',
               '⚠️ **不定规模就开始写 INCAR** —— 这正是那次事故的来源：'
               '179 原子 + 16 rank 却没写 `NCORE`'],
         cmd=['python _system_types.py --lookup <目录>   # 先确认「你是哪类体系 + 规模轴」',
              'python scripts/recommend.py --goal <目标> --elements "<元素>"',
              'python scripts/doctor.py'],
         read=['`references/_SYSTEMS.md`（体系类型索引 + 规模轴）',
               '`references/decide.md`（决策总览）']),

    dict(key='model', n=2, title='建模与初始结构',
         first='先量**真空层够不够**（该方向有没有 ≥10 Å 真空）—— 不够会被镜像作用污染，而**程序不报错**。',
         goal='拿到一个**物理上站得住**的初始结构（`POSCAR`）。',
         do=['按实验数据（配位环境、键长、电镜、元素组成）搭模型',
             '定晶胞与真空层厚度',
             '定元素顺序 —— 它决定 `POTCAR` 的拼接顺序'],
         fork=['表面切哪个晶面、几层、固定几层', '真空层多厚'],
         trap=['⚠️ **真空层不够** ⇒ slab 与自己的镜像作用，**而程序不报错**',
               '⚠️ **`POSCAR` 元素顺序与 `POTCAR` 不一致** ⇒ 静默错',
               '⚠️ **某方向设 1 个 k 点**只对**真有真空**的方向成立'
               '（3D 体相照做会静默算错）'],
         cmd=['python scripts/validate.py <目录>   # 会查真空方向与 k 点的关系'],
         read=['`references/playbook.md` §1 的 S30（真空层不够）',
               '`references/playbook.md` §0.3（真空层、slab 层数、固定层数）',
               '`references/_GATES.md` §3（规模敏感标签）']),

    dict(key='params', n=3, title='参数设定（INCAR / KPOINTS）',
         first='先跑 `python scripts/validate.py <目录> --ncores <你的核数>` —— 它会在**提交之前**查并行分解。',
         goal='一套**自洽**的输入。',
         do=['选泛函与 `ENCUT`', '选展宽 `ISMEAR` / `SIGMA`（按金属性）',
             '选 k 点密度', '**定并行配置**（`NCORE` / `KPAR`）'],
         fork=['要不要 +U / 杂化 / vdW / 隐式溶剂',
               '金属 vs 绝缘体的展宽口径', '**k 点密度 vs 机时**'],
         trap=['⚠️ **`NCORE` 不写就走默认 1** ⇒ 大体系 + 多 rank 会'
               '**第一次 SCF 就崩**',
               '⚠️ **`NCORE` 与 `NPAR` 同时写** ⇒ `NPAR` 优先、'
               '`NCORE` 被**静默忽略**',
               '⚠️ `ISMEAR=-5`（四面体法）在 k 点 < 4 时失败'],
         cmd=['python scripts/wizard.py   # 生成一套自洽输入 + 逐参数 README',
              'python scripts/recommend.py --goal <目标> --elements "<元素>"',
              'python scripts/validate.py <目录> --ncores <你的核数>'],
         read=['`references/decide.md`（遇到 X 该选 Y，因为 Z，代价是 W）',
               '`references/_SYSTEMS.md`（该类体系的参数画像）',
               '`references/_GATES.md` §3（规模敏感标签清单）']),

    dict(key='converge', n=4, title='收敛测试',
         first='先只扫**一个**参数（`ENCUT` 或 k 点），固定其余 —— 一次只动一个才能归因。',
         goal='证明**你的数值设置够用**（`ENCUT` / k 点 / `SIGMA`）。',
         do=['固定其它参数，只扫一个；看目标物理量随它变化',
             '画收敛曲线，取「变化小于你的精度要求」的那个值'],
         fork=['收敛判据取多少（能量 1 meV/atom？力 0.01 eV/Å？）',
               '⚠️ **收敛测试要按「要算的量」来定** —— 算能量差和算力，要求不同'],
         trap=['⚠️ **跳过收敛测试** ⇒ 后面所有结论都建立在一个没验证的基组上',
               '⚠️ 只测了 `ENCUT` 没测 k 点（或反过来）',
               '⚠️ **变胞优化（`ISIF=3`）要重测 `ENCUT`** —— 胞变了基组也变了'],
         cmd=['python scripts/compare.py <目录>   # 跨算例一致性',
              'python scripts/parse_output.py <目录>'],
         read=['`references/decide.md`（`ENCUT` / k 点 / `SIGMA` 的条目）',
               '`references/playbook.md` §0（数值速查表，每张都带「适用范围」列）']),

    dict(key='optimize', n=5, title='几何优化 / 晶胞优化',
         first='先确认 `OUTCAR` 里**力真的到了 `EDIFFG`**，而不是只看"跑完了"。',
         goal='找到**力收敛**的驻点结构。',
         do=['选 `IBRION` / `ISIF` / `NSW` / `EDIFFG`',
             '看 `OUTCAR` 的力是否到 `EDIFFG`',
             '收敛后确认**没有跑偏**（对比初末结构）'],
         fork=['`ISIF=2`（冻胞）vs `ISIF=3`（变胞）',
               'slab 要不要固定底层原子'],
         trap=['⚠️ **`IBRION=5`（频率）配 `ISIF=3`** ⇒ 晶胞在动，'
               'Hessian 不是你要的',
               '⚠️ **`POTIM` 给 0 但 `IBRION` 不是 3** ⇒ 离子不动'
               '**而程序不报错**（「没报错但白干」）',
               '⚠️ 只看到 `reached required accuracy` 就以为一定对 —— '
               '要确认**收敛到的是你要的那个结构**'],
         cmd=['python scripts/diagnose.py <目录>   # 查 GEO.not_converged',
              'python scripts/compare.py <目录>     # 查力平衡'],
         read=['`references/playbook.md` §1（几何优化相关 S 条目）',
               '`references/decide.md`（`ISIF` / `EDIFFG` 条目）']),

    dict(key='electronic', n=6, title='电子结构分析',
         first='先确认**这一步的 k 点比优化时更密**（DOS 的毛刺根因是 k 点，不是 `NEDOS`）。',
         goal='拿到 DOS / PDOS / 电荷 / 势 / 功函数这类**可观测量**。',
         do=['先做**自洽**单点，再算目标量',
             'DOS 用比优化更密的 k 点；能带用 line 模式',
             '电荷分析选对方法（Bader / DDEC / Löwdin…）'],
         fork=['`ISMEAR` 用哪个（DOS 要 `-5` 还是 `0`）',
               '电荷分析用哪种布居'],
         trap=['⚠️ **拿优化用的粗 k 点去算 DOS** ⇒ 曲线有毛刺'
               '（根因是 k 点，**不是** `NEDOS`）',
               '⚠️ **`LORBIT` 输出的 `total charge` 不能定量**'
               '（那是半径球内的布居）',
               '⚠️ `ISMEAR=-5` 要求 k 点 ≥ 4'],
         cmd=['python scripts/diagnose.py <目录>',
              'python scripts/postprocess.py <子命令>   # DOS / 功函数 / 电荷'],
         read=['`references/playbook.md` §4（后处理判读经验）',
               '`references/course_learned.md` §4（电子结构分析）']),

    dict(key='dynamics', n=7, title='分子动力学（AIMD）',
         first='先跑**很短**的一段确认能量不漂，再上生产段。',
         goal='有限温下的轨迹与统计量。',
         do=['定系综与温控（`MDALGO` / `TEBEG` / `TEEND`）',
             '定时间步与步数；先跑短的确认稳定',
             '丢平衡段，只用生产段做统计'],
         fork=['时间步长（含 H 要更小）', '系综选择'],
         trap=['⚠️ **把平衡段也算进统计** ⇒ 统计量有系统偏差',
               '⚠️ 时间步太大 ⇒ 能量漂移，**不一定报错**'],
         cmd=['python scripts/parse_output.py <目录>',
              'python scripts/postprocess.py <子命令>'],
         read=['`references/decide.md`（MD 相关条目）',
               '`references/playbook.md` §2（工作流）']),

    dict(key='path', n=8, title='反应路径 / 过渡态',
         first='先确认**插点数能被核数整除**（NEB 的硬约束），再提交。',
         goal='找到**一阶鞍点**并验证它。',
         do=['NEB / CI-NEB 或 Dimer', '用频率确认**恰好一个虚频**',
             '做 IRC 或至少两端点确认连接的是你要的两个态'],
         fork=['NEB vs Dimer（知道大致路径 vs 只知初末态）',
               '插点数量（**必须能被核数整除**）'],
         trap=['⚠️ **过渡态必须恰好 1 个虚频**；0 个是极小点、≥2 个没爬到鞍点',
               '⚠️ **NEB 的核数必须整除插点数**，否则并行出错',
               '⚠️ 频率计算里「最小 6 个频率出虚频可无视」'
               '**只对孤立分子成立**'],
         cmd=['python scripts/diagnose.py <目录>',
              'python scripts/parse_output.py <目录>   # 读 DYNMAT 判虚频'],
         read=['`references/playbook.md` §1（频率 / 虚频相关 S 条目）',
               '`references/_SYSTEMS.md`（孤立分子那一节）']),

    dict(key='post', n=9, title='后处理与物性',
         first='先跑 `python scripts/compare.py <目录>` 做**自洽性检查** —— 这是最值钱的一个动作。',
         goal='从输出里抽出**可用的数值**，并核对自洽性。',
         do=['抽数值（能量 / 力 / 频率 / DOS / 功函数）',
             '**做自洽性检查**（能量闭合、力平衡、原子数一致）',
             '把口径（`ENCUT` / k 点 / 版本）记下来'],
         fork=['要不要做自由能校正（ZPE / 熵）', '参考态怎么选'],
         trap=['⚠️ **不做闭合性检查** ⇒ 一个常数偏移能悄悄进到结论里',
               '⚠️ 不同算例的 `ENCUT` / k 点不一致 ⇒ 能量差**不可比**'],
         cmd=['python scripts/parse_output.py <目录>',
              'python scripts/compare.py <目录>',
              'python scripts/postprocess.py <子命令>'],
         read=['`references/playbook.md` §4（后处理判读）',
               '`references/course_learned.md`（自由能校正）']),

    dict(key='diagnose', n=10, title='诊断（出问题时）',
         first='**先分类**：`grep -cE "^(DAV|RMM):" OSZICAR` —— 0 就是「没跑起来」（A 类），否则是「结果不对」（B 类）。**三类的处方是冲突的。**',
         goal='从**症状**定位到**原因**，并给出**改哪一处**。',
         do=['先分清三类：**没跑起来** / **跑完但结果不对** / **慢**',
             '按症状查 `diagnose.py`，对不上再查 `playbook.md` §1'],
         fork=['⚠️ **不要在没分清「哪一类」之前就开始调参**'],
         trap=['⚠️ **把「某个取值没救回来」当成「该变量无关」**',
               '⚠️ **把日志里「总会出现的行」当根因**（红鲱鱼）',
               '⚠️ **在动系统 / 队列配置之前没试并行分解**'],
         cmd=['python scripts/diagnose.py <目录>',
              'python scripts/validate.py <目录> --ncores <核数>',
              'python scripts/compare.py <目录>'],
         read=['`references/playbook.md` §4b（**诊断反模式**，先读这个）',
               '`references/playbook.md` §1（症状 → 处方 73 条）',
               '`references/playbook.md` §5（报错原文速查）']),

    dict(key='report', n=11, title='结论与报告',
         first='先把**每个数的来源**记下来（哪个目录、哪个文件）—— 事后补不回来。',
         goal='把结果写成**别人能复核**的形式。',
         do=['记清每个数的来源（哪个目录、哪个文件、哪一行）',
             '写清方法学参数（泛函 / `ENCUT` / k 点 / 版本 / 展宽）',
             '**列出本次没检查的项**'],
         fork=['结论的置信度怎么表述'],
         trap=['⚠️ 不写 `ENCUT` / k 点 ⇒ 别人无法复现也无法判断可比性',
               '⚠️ 把「程序没报错」当成「结果对」'],
         cmd=['python scripts/compare.py <目录>',
              'python scripts/doctor.py   # 报告环境'],
         read=['`references/templates/report.md`（**报告模板**：只给结构不给数值）',
               '`references/VERSIONS.md`（写清版本）',
               '`references/_WRITING_CONTRACT.md`（证据分级）']),
]

RESUME = dict(key='resume', n=0, title='↻ 续算（旁路分支）',
              first='先判断**已经算到哪**（离子步 / 电子步），再决定从 `CONTCAR` 还是 `WAVECAR` 续。',
         goal='计算被中断（墙钟 / 被 kill / 崩溃）后接着跑，而不是从头。',
              do=['判断**已经算到哪**（离子步 / 电子步）',
                  '决定从 `CONTCAR` 还是 `WAVECAR` / `CHGCAR` 续',
                  '改 `ISTART` / `ICHARG`'],
              fork=['要几何结构还是要波函数 / 电荷密度'],
              trap=['⚠️ **`ISTART=1` 但没有 `WAVECAR`** ⇒ 程序忽略它、'
                    '从头算（**不报错**）',
                    '⚠️ 续算时**改了 `ENCUT` / k 点** ⇒ 与前面的结果不可比'],
              cmd=['python scripts/diagnose.py <目录>   # 先看 RUN.not_finished',
                   'python scripts/wizard.py --goal resume'],
              read=['`references/playbook.md` §1（续算相关 S 条目）',
                    '`references/decide.md`（`ISTART` / `ICHARG` 条目）'])

ALL = {s['key']: s for s in STAGES}
ALL[RESUME['key']] = RESUME


# ===========================================================================
# 二、扫描：目录里有哪些「阶段标志物」
# ===========================================================================
def _n_ionic_steps(path) -> int:
    if not path:
        return 0
    try:
        return len(vc.outcar_ionic_steps(path))
    except Exception:                                        # noqa: BLE001
        return 0


def _has_finished(path) -> bool:
    '''OUTCAR 里有没有 `General timing`（正常收尾的标志）。'''
    if not path:
        return False
    try:
        size = os.path.getsize(path)
        with vc.open_maybe_gz(path, 'rb') as fh:
            if size > 200000:
                fh.seek(max(0, size - 200000))
            tail = fh.read().decode('utf-8', errors='replace')
        return ('General timing' in tail
                or 'Voluntary context switches' in tail)
    except Exception:                                        # noqa: BLE001
        return False


def scan_directory(directory: str) -> dict:
    '''**只读**地看一个目录，回报「看到了什么」。不猜、不改。'''
    inp = vc.discover_inputs(directory)
    seen = {}
    for k in ('INCAR', 'KPOINTS', 'POSCAR', 'POTCAR', 'OUTCAR', 'OSZICAR',
              'CONTCAR', 'CHGCAR', 'WAVECAR', 'DOSCAR', 'EIGENVAL', 'PROCAR',
              'LOCPOT', 'CHG', 'vasprun', 'IBZKPT', 'DYNMAT', 'XDATCAR',
              'PCDAT', 'LOG'):
        if inp.get(k):
            seen[k] = inp[k]
    out = {'dir': os.path.abspath(directory), 'files': seen,
           'n_ionic': _n_ionic_steps(inp.get('OUTCAR')),
           'finished': _has_finished(inp.get('OUTCAR')),
           'crash': False, 'subdirs': []}
    # 崩溃特征（复用 `parse_launch_log` 的判据，口径与 diagnose.py 一致）
    info = vc.parse_launch_log(inp.get('LOG') or '')
    out['log_info'] = info
    if info.get('first_crash_line') and not out['n_ionic']:
        out['crash'] = True
    # 子目录（像是「一个项目多个算例」）
    try:
        for name in sorted(os.listdir(directory)):
            p = os.path.join(directory, name)
            if os.path.isdir(p) and os.path.exists(os.path.join(p, 'INCAR')):
                out['subdirs'].append(name)
    except OSError:
        pass
    return out


def guess_stage(sc: dict):
    '''按「看到了什么」推断阶段。返回 `(stage_key, 依据列表)`。

    ⚠️ 顺序即优先级：**从最靠后的阶段往前判**（算完了就是算完了）。
    '''
    f = sc['files']
    why = []
    if sc['crash']:
        why.append('LOG 里有崩溃特征，且 OUTCAR 里 **0 个离子步** '
                   '⇒ **作业没跑起来**')
        return 'diagnose', why
    elec = [k for k in ('DOSCAR', 'EIGENVAL', 'PROCAR') if k in f]
    if elec:
        why.append('看到了 %s ⇒ 已经在做电子结构' % '、'.join(elec))
        return 'electronic', why
    pot = [k for k in ('LOCPOT', 'CHG') if k in f]
    if pot:
        why.append('看到了 %s ⇒ 已在做势 / 电荷分析' % '、'.join(pot))
        return 'electronic', why
    if 'DYNMAT' in f:
        why.append('看到了 DYNMAT ⇒ 在做频率 / 过渡态验证')
        return 'path', why
    if 'OUTCAR' in f:
        if sc['finished']:
            why.append('OUTCAR 里有 `General timing` ⇒ 这次计算**正常收尾**')
            if sc['n_ionic'] >= 2:
                why.append('OUTCAR 里有 %d 个离子步 ⇒ 做过几何优化'
                           % sc['n_ionic'])
                return 'optimize', why
            why.append('OUTCAR 里只有 %d 个离子步 ⇒ 像是单点 / 静态计算'
                       % sc['n_ionic'])
            return 'post', why
        if sc['n_ionic'] > 0:
            why.append('OUTCAR 里**没有** `General timing`，但有 %d 个离子步 '
                       '⇒ 跑了一半被打断' % sc['n_ionic'])
            return 'resume', why
        why.append('OUTCAR 里既没有 `General timing` 也没有离子步 '
                   '⇒ 没正常收尾（崩溃 / 墙钟 / 还在跑）')
        return 'diagnose', why
    if 'INCAR' in f and 'KPOINTS' in f and 'POSCAR' in f:
        why.append('三件套齐了，但**还没有 OUTCAR** ⇒ 准备提交')
        return 'params', why
    if 'POSCAR' in f:
        why.append('只有 POSCAR ⇒ 结构就绪，还没写输入')
        return 'params', why
    why.append('没看到任何 VASP 文件')
    return 'define', why


def render_stage(s: dict, brief=False):
    print('-' * 74)
    print('%s  【阶段 %s】' % (s['title'], s['n'] or '↻'))
    print('-' * 74)
    print('**目标**：%s' % s['goal'])
    if s.get('first'):
        print()
        print('**⭐ 第一件事**：%s' % s['first'])
    if brief:
        for c in s['cmd'][:2]:
            print('  $ %s' % c)
        return
    print('\n**该做的**：')
    for x in s['do']:
        print('  · %s' % x)
    print('\n**决策点**：')
    for x in s['fork']:
        print('  · %s' % x)
    print('\n**常见坑**：')
    for x in s['trap']:
        print('  · %s' % x)
    print('\n**该跑的命令**：')
    for x in s['cmd']:
        print('  $ %s' % x)
    print('\n**该读的条目**：')
    for x in s['read']:
        print('  · %s' % x)


def cmd_list(args):
    print('=' * 74)
    print('VASP 项目陪跑 —— %d 个主线阶段 + 1 个续算分支' % len(STAGES))
    print('=' * 74)
    print('\n> 阶段名单与 `AGENTS.md` 一致；**本文件是全库唯一定义它们的地方**。\n')
    for s in STAGES:
        print('  %2d. %-12s %s' % (s['n'], s['key'], s['title']))
        print('      %s' % s['goal'])
    print('\n  %2s  %-12s %s' % ('↻', RESUME['key'], RESUME['title']))
    print('      %s' % RESUME['goal'])
    print('\n用法：python scripts/guide.py show <阶段>    展开某个阶段')
    print('      python scripts/guide.py scan <目录>    推断「卡在哪、下一步做什么」')
    return EXIT_OK


def cmd_show(args):
    key = (args.stage or '').strip().lower()
    if key in ('resume', '续算', '↻'):
        render_stage(RESUME)
        return EXIT_OK
    if key not in ALL:
        if key.isdigit():
            for s in STAGES:
                if s['n'] == int(key):
                    render_stage(s)
                    return EXIT_OK
        print('认不出阶段：%r' % args.stage, file=sys.stderr)
        print('可用：%s' % ', '.join(
            ['%d-%s' % (s['n'], s['key']) for s in STAGES] + ['resume']),
            file=sys.stderr)
        return EXIT_USAGE
    render_stage(ALL[key])
    return EXIT_OK


def cmd_scan(args, brief=False):
    d = args.directory or '.'
    if not os.path.isdir(d):
        vc.die('目录不存在：%s' % d, EXIT_USER)
    sc = scan_directory(d)
    print('=' * 74)
    print('项目阶段扫描 —— %s' % sc['dir'])
    print('=' * 74)
    print('\n**看到了什么**（这就是全部依据，你可以直接推翻下面的推断）：')
    if sc['files']:
        for k in sorted(sc['files']):
            print('  %-10s %s' % (k, os.path.basename(sc['files'][k])))
    else:
        print('  （没有任何 VASP 文件）')
    if sc['subdirs']:
        extra = '  …' if len(sc['subdirs']) > 8 else ''
        print('  子目录里有 INCAR 的：%s%s'
              % (', '.join(sc['subdirs'][:8]), extra))
    if sc['n_ionic']:
        print('  OUTCAR 离子步数：%d' % sc['n_ionic'])
    li = sc['log_info']
    if li.get('total_cores'):
        print('  LOG 实际核数：%d' % li['total_cores'])
    if li.get('distr'):
        print('  LOG 并行分解：distr: one band on %d cores, %d groups'
              % li['distr'])

    key, why = guess_stage(sc)
    print('\n**推断：你现在在【%s】**' % ALL[key]['title'])
    for w in why:
        print('  ← %s' % w)

    if brief:
        st = ALL[key]
        if st.get('first'):
            print('\n**⭐ 第一件事**：')
            print('  %s' % st['first'])
        print('\n**然后**：')
        for c in st['cmd'][:2]:
            print('  $ %s' % c)
        print('\n（看完整指引：python scripts/guide.py show %s）' % key)
        return EXIT_OK

    print()
    render_stage(ALL[key])
    _big_system_warning(sc, d)
    print('\n提示：本向导**只读你的目录**，不改任何文件、不提交作业。')
    return EXIT_OK


def _big_system_warning(sc, d):
    '''大体系 + 没写并行标签 ⇒ 显式提醒（口径与 validate.py 一致）。

    ⚠️ 阈值 **100 原子** 与 `validate.py` 的 `XNCORE.missing_with_rank`
       以及 `_system_types.py` 的 `SCALE_ORDER` **必须是同一个数** ——
       三处口径不一致会让人不知道信哪个。
    '''
    ps = sc['files'].get('POSCAR')
    if not ps:
        return
    try:
        n = vc.read_poscar(ps).nions
    except Exception:                                        # noqa: BLE001
        return
    inc_path = sc['files'].get('INCAR')
    tags = set()
    if inc_path:
        try:
            tags = set(t.upper() for t in vc.read_incar(inc_path).tags)
        except Exception:                                    # noqa: BLE001
            tags = set()
    if n and n >= 100 and not (tags & {'NCORE', 'NPAR'}):
        print('\n' + '!' * 74)
        print('⚠️⚠️ **这个体系有 %d 个原子，而 `INCAR` 里既没有 `NCORE` '
              '也没有 `NPAR`**' % n)
        print('      ⇒ 走官方默认 `NCORE = 1`；大体系 + 多 rank 下'
              '**第一次 SCF 就可能崩**。')
        print('      ⇒ 提交前务必跑：')
        print('         python scripts/validate.py %s --ncores <你的核数>' % d)
        print('!' * 74)




# ===========================================================================
# 三、导出成文档（`references/workflow.md`）
# ===========================================================================
def cmd_export(args):
    '''把 11 个阶段导出成 `references/workflow.md`（供人阅读 / grep）。

    ⚠️ **不要手改那个文件** —— 它由这里生成，改了会被 `--export` 覆盖。
       要改阶段内容请改本文件的 `STAGES`。
    '''
    A = []
    add = A.append
    add('# workflow —— **项目阶段向导**：我在哪个阶段？下一步做什么？')
    add('')
    add('> ⚠️ **本文件由 `python scripts/guide.py --export` 生成，请不要手改。**')
    add('> 要改内容请改 `scripts/guide.py` 的 `STAGES`。')
    add('')
    add('> **这不是一个「自动跑命令的工作流」。** 它在**每个阶段**告诉你：')
    add('> 现在该做什么、有哪些决策点、坑在哪、该跑哪条已有命令、该读哪个条目。')
    add('>')
    add('> ⚠️ **它不替你决定**，也不提交作业 —— 定位是「顾问，而非自动驾驶」。')
    add('')
    add('## 怎么用')
    add('')
    add('```bash')
    add('python scripts/guide.py list                  # 列全部阶段')
    add('python scripts/guide.py show <阶段>           # 展开某阶段')
    add('python scripts/guide.py scan <你的项目目录>    # 推断「卡在哪、下一步做什么」')
    add('python scripts/guide.py next <你的项目目录>    # 只要下一步')
    add('```')
    add('')
    add('⚠️ `scan` 是**启发式**（按文件存在性判断），'
        '它会**打印依据**，你可以直接推翻它。')
    add('')
    add('---')
    add('')
    add('## %d 个主线阶段 + 1 个续算分支' % len(STAGES))
    add('')
    add('| # | 阶段 | 一句话 |')
    add('|---|---|---|')
    for s in STAGES:
        add('| %d | [%s](#%d-%s) | %s |'
            % (s['n'], s['title'], s['n'], s['key'], s['goal']))
    add('| ↻ | [%s](#resume) | %s |' % (RESUME['title'], RESUME['goal']))
    add('')
    for s in STAGES + [RESUME]:
        add('---')
        add('')
        if s is RESUME:
            add('<a id="resume"></a>')
            add('')
        add('## %s %s' % (s['n'] or '↻', s['title']))
        add('')
        add('**目标**：%s' % s['goal'])
        add('')
        if s.get('first'):
            add('**⭐ 第一件事**：%s' % s['first'])
            add('')
        add('**该做的**：')
        add('')
        for x in s['do']:
            add('- %s' % x)
        add('')
        add('**决策点**：')
        add('')
        for x in s['fork']:
            add('- %s' % x)
        add('')
        add('**常见坑**：')
        add('')
        for x in s['trap']:
            add('- %s' % x)
        add('')
        add('**该跑的命令**：')
        add('')
        add('```bash')
        for x in s['cmd']:
            add(x)
        add('```')
        add('')
        add('**该读的条目**：')
        add('')
        for x in s['read']:
            add('- %s' % x)
        add('')
    add('---')
    add('')
    add('## 相关页')
    add('')
    add('- **体系索引**：`references/_SYSTEMS.md`（先问「你算的是哪类」）')
    add('- **条件与规模**：`references/_GATES.md`')
    add('- **症状 → 处方**：`references/playbook.md` §1')
    add('- **诊断反模式**：`references/playbook.md` §4b')
    txt = chr(10).join(A) + chr(10)
    dest = getattr(args, 'out', None) or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'references', 'workflow.md')
    with open(dest, 'w', encoding='utf-8', newline=chr(10)) as fh:
        fh.write(txt)
    print('已写出 %s（%d 行）' % (dest, txt.count(chr(10))))
    return EXIT_OK


def cmd_next(args):
    return cmd_scan(args, brief=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog='guide.py',
        description='项目阶段向导：我在哪个阶段？下一步做什么？',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='阶段名单见 `AGENTS.md`；本文件是全库唯一定义它们的地方。\n'
               '⚠️ 扫描是**启发式**（按文件存在性），每处推断都会打印依据。')
    sub = ap.add_subparsers(dest='cmd')

    sub.add_parser('list', help='列全部阶段')

    p_show = sub.add_parser('show', help='展开某个阶段')
    p_show.add_argument('stage', nargs='?', help='阶段名或编号，或 resume')

    p_scan = sub.add_parser('scan', help='扫描目录，推断阶段与下一步')
    p_scan.add_argument('directory', nargs='?', default='.')

    p_next = sub.add_parser('next', help='只要下一步（scan 的精简版）')
    p_next.add_argument('directory', nargs='?', default='.')



    ap.add_argument('--export', action='store_true',
                    help='把 11 个阶段导出成 references/workflow.md')
    ap.add_argument('--out', help='配合 --export：写到指定路径（默认 references/workflow.md）')
    args = ap.parse_args(argv)
    if args.export:
        return cmd_export(args)
    if not args.cmd:
        ap.print_help()
        return EXIT_USAGE
    if args.cmd == 'list':
        return cmd_list(args)
    if args.cmd == 'show':
        return cmd_show(args)
    if args.cmd == 'scan':
        return cmd_scan(args)
    if args.cmd == 'next':
        return cmd_next(args)
    ap.print_help()
    return EXIT_USAGE


if __name__ == '__main__':
    sys.exit(main())
