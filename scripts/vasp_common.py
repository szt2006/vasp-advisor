#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vasp_common —— 所有脚本共用的基础设施（**只用标准库**）

这个模块存在的唯一理由：**同一个逻辑绝不能有两份实现**。
本 skill 踩过的坑是"两份错误分类逻辑"——同一份输入在两个脚本里得到相反结论。
所以凡是"读文件 / 判体系维度 / 报错退出 / 认路径"这类逻辑，全部收在这里，
其它脚本一律 `from vasp_common import ...`，**不要另写一份**。

内容
----
1. 控制台编码兼容层（中文 Windows 下 print 中文会崩）
2. 统一退出码与友好报错（**绝不抛 traceback**）
3. 路径与输入集发现（POSCAR/CONTCAR 变体、gz 解压）
4. 物理小工具（晶格、倒格矢、体积、维度判定、k 点密度）
5. 解析结果的公共数据类

退出码约定（全 skill 统一，务必遵守）
------------------------------------
| 码 | 含义 |
|---|---|
| 0 | 成功（**校验类**工具里 0 表示"没发现问题"，不表示"算得对"） |
| 1 | 用户输入/文件有问题（文件不存在、内容解析不了） |
| 2 | 命令行用法错误（无参数、选项组合非法） |
| 3 | 缺依赖或缺少必要的外部信息（如没给 VASP 可执行文件路径） |
| 4 | 检查发现了**错误级**问题（校验/审计报红） |
| 5 | 检查发现了**警告级**问题（可用 `--strict` 提升为 4） |
"""

from __future__ import annotations

import gzip
import io
import math
import os
import re
import sys

__all__ = [
    "EXIT_OK", "EXIT_USER", "EXIT_USAGE", "EXIT_DEP", "EXIT_ERROR", "EXIT_WARN",
    "setup_console", "die", "warn", "info",
    "read_text", "open_maybe_gz", "iter_lines",
    "find_file", "discover_inputs", "POSCAR_NAMES",
    "Cell", "Elements",
    "read_poscar", "PoscarData",
    "read_kpoints", "KpointsData",
    "read_incar", "IncarData",
    "parse_potcar_header", "PotcarInfo",
    "outcar_version", "outcar_recognized_tags", "outcar_fermi", "outcar_nions",
    "outcar_encut", "IonicStep", "outcar_ionic_steps", "outcar_cell_volumes",
    "outcar_reciprocal_lengths", "oszicar_last_energy", "vasprun_meta",
    # 版本意识（见 references/VERSIONS.md）
    "parse_version_number", "parse_version_tuple",
    "load_version_gates", "version_gate_status",
    "loaded_version_gates_path",
    "BOHR", "RY", "HA",
]

EXIT_OK = 0
EXIT_USER = 1
EXIT_USAGE = 2
EXIT_DEP = 3
EXIT_ERROR = 4
EXIT_WARN = 5

# 单位换算（CODATA 常用值；用于把 OUTCAR 里的 a.u./Ry 换成 eV/Å）
BOHR = 0.529177210903          # Å
RY = 13.605693122994           # eV
HA = 27.211386245988           # eV


# ---------------------------------------------------------------------------
# 1. 控制台编码兼容层
# ---------------------------------------------------------------------------
def setup_console() -> None:
    """让中文输出在 Windows 控制台不崩。

    中文 Windows 的默认代码页常是 GBK；直接 print 中文/特殊符号（如 `Å`、`Γ`）
    会抛 `UnicodeEncodeError` 或被替换成乱码。这里把三个流尽量切到 UTF-8，
    **失败也不报错**（有些环境不支持 reconfigure，或流被重定向到文件）。
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:                                          # noqa: BLE001
            pass


# ---------------------------------------------------------------------------
# 2. 统一退出与报错
# ---------------------------------------------------------------------------
def die(msg: str, code: int = EXIT_USER, hint: str = "") -> "None":
    """友好中文报错后退出。**绝不抛 traceback。**

    Parameters
    ----------
    msg  : 一句话说清出了什么事
    code : 见模块头的退出码表
    hint : 可选的"下一步怎么办"
    """
    setup_console()
    sys.stderr.write("错误：%s\n" % msg.rstrip())
    if hint:
        for line in hint.rstrip().splitlines():
            sys.stderr.write("  " + line.strip() + "\n")
    raise SystemExit(code)


def warn(msg: str) -> None:
    setup_console()
    sys.stderr.write("警告：%s\n" % msg.rstrip())


def info(msg: str) -> None:
    setup_console()
    sys.stdout.write(msg.rstrip() + "\n")


# ---------------------------------------------------------------------------
# 3. 路径与文本读取
# ---------------------------------------------------------------------------
def read_text(path: str) -> str:
    """读文本，自动处理 BOM 与常见编码，并统一成 LF。

    VASP 输入文件是 ASCII 为主的自由格式，但**用户从 Windows 编辑器里存出来
    的文件常带 BOM 或 CRLF**，而某些解析路径对 `\\r` 敏感（见 SKILL.md 的坑表）。
    这里统一在入口处规整，让下游不用各自处理。

    读不到就 `die(..., EXIT_USER)`。
    """
    if not os.path.exists(path):
        die("文件不存在：%s" % path,
            EXIT_USER, "请检查路径，或用 --help 看用法。")
    if os.path.isdir(path):
        die("这是一个目录，不是文件：%s" % path, EXIT_USER)
    try:
        with open_maybe_gz(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        die("读不了文件 %s：%s" % (path, exc), EXIT_USER)
        return ""                                        # 不可达，仅为类型
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return raw.decode(enc).replace("\r\n", "\n").replace("\r", "\n")
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def open_maybe_gz(path: str, mode: str = "rt"):
    """透明打开 `.gz`：`OUTCAR.gz` 与 `OUTCAR` 用同一段代码读。

    二进制模式返回 gzip 或普通文件对象；文本模式额外套一层 utf-8。
    """
    is_gz = path.lower().endswith(".gz")
    if "b" in mode:
        return gzip.open(path, mode) if is_gz else open(path, mode)
    if is_gz:
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8",
                                errors="replace", newline="")
    return open(path, mode, encoding="utf-8", errors="replace", newline="")


def iter_lines(path: str, encoding: str = "utf-8"):
    """逐行读（可 .gz），供大文件（OUTCAR 动辄几十 MB）流式处理。

    返回 (行号从 1 开始, 去掉尾部换行的字符串)。**不要**用它读小文件后再
    全部塞进内存做随机访问——那正是 OUTCAR 解析常见的 OOM 来源。
    """
    with open_maybe_gz(path, "rb") as fh:
        n = 0
        for raw in fh:
            n += 1
            try:
                line = raw.decode(encoding)
            except UnicodeDecodeError:
                line = raw.decode("latin-1")
            yield n, line.rstrip("\r\n")


# POSCAR / CONTCAR 的常见别名。VASP 本体只认 POSCAR/CONTCAR，
# 但真实算例目录里常见这些衍生名（本项目的算例里就有 POSCAR.vasp / POSCAR_FIX）。
POSCAR_NAMES = ("POSCAR", "CONTCAR", "POSCAR.vasp", "POSCAR.vasp", "POSCAR.xyz",
                "POSCAR_fix", "POSCAR_FIX", "POSCAR.bak", "POSCAR.relax1")


def find_file(directory: str, names, required: bool = True,
              what: str = "") -> "str | None":
    """在目录里按名字候选表找文件（**大小写不敏感**，真实算例里大小写很乱）。"""
    if not os.path.isdir(directory):
        if required:
            die("目录不存在：%s" % directory, EXIT_USER)
        return None
    try:
        entries = os.listdir(directory)
    except OSError as exc:
        die("读不了目录 %s：%s" % (directory, exc), EXIT_USER)
        return None
    lower = {e.lower(): e for e in entries}
    for name in names:
        hit = lower.get(name.lower())
        if hit:
            return os.path.join(directory, hit)
    if required:
        die("在 %s 里找不到 %s（找过这些名字：%s）"
            % (directory, what or "目标文件", ", ".join(names)),
            EXIT_USER,
            "如果结构文件名很特别，请用 --poscar <路径> 显式指定。")
    return None


def discover_inputs(directory: str = ".") -> dict:
    """扫描一个 VASP 算例目录，返回各输入/输出文件的实际路径。

    找不到的键对应的值是 None —— 调用方自己决定"缺这个算不算致命"。
    **不要**在这里替调用方做判断（否则又会变成两份逻辑）。
    """
    out = {}
    out["dir"] = os.path.abspath(directory)
    out["INCAR"] = find_file(directory, ("INCAR",), required=False)
    out["KPOINTS"] = find_file(directory, ("KPOINTS", "KPOINTS.bak"),
                               required=False)
    out["POSCAR"] = find_file(directory, POSCAR_NAMES, required=False)
    out["POTCAR"] = find_file(directory, ("POTCAR",), required=False)
    out["OUTCAR"] = find_file(directory, ("OUTCAR", "OUTCAR.gz"),
                              required=False)
    out["OSZICAR"] = find_file(directory, ("OSZICAR",), required=False)
    out["vasprun"] = find_file(directory, ("vasprun.xml",), required=False)
    out["CONTCAR"] = find_file(directory, ("CONTCAR",), required=False)
    out["XDATCAR"] = find_file(directory, ("XDATCAR",), required=False)
    out["DOSCAR"] = find_file(directory, ("DOSCAR",), required=False)
    out["EIGENVAL"] = find_file(directory, ("EIGENVAL",), required=False)
    out["IBZKPT"] = find_file(directory, ("IBZKPT",), required=False)
    out["DYNMAT"] = find_file(directory, ("DYNMAT",), required=False)
    out["CHGCAR"] = find_file(directory, ("CHGCAR",), required=False)
    out["LOCPOT"] = find_file(directory, ("LOCPOT",), required=False)
    out["PROCAR"] = find_file(directory, ("PROCAR", "PROCAR.gz"),
                              required=False)
    # `LOG` —— **作业"起没起来"这一层的关键文件**（见 `parse_launch_log`）。
    # ⚠️ 本项目在此处返工过一次：`diagnose.py` 的 LAUNCH.* 规则要读 LOG，
    #    但 `discover_inputs` **原来根本不找它** ⇒ 规则永远不触发、
    #    而"读到的文件"列表里也看不出少了什么。
    #    ⇒ 教训：**新增一层规则时，先确认它的输入在发现函数里**。
    #
    # 常见名：`LOG` / `log` / `vasp.log` / `stdout` / `out.log` /
    #        `slurm-*.out` / `*.o<jobid>`（不同排队系统/个人习惯不同）。
    # 这里只认**几个通用名**；找 `slurm-*.out` 这类需要通配，
    # 由 `find_file` 的候选名机制承担不了 ⇒ 单独兜底扫一遍。
    out["LOG"] = find_file(directory,
                           ("LOG", "log", "vasp.log", "stdout", "out.log",
                            "vasp.out", "output", "OUTPUT"), required=False)
    if not out["LOG"]:
        out["LOG"] = _find_glob_first(
            directory, ("slurm-*.out", "*.o[0-9]*", "*.e[0-9]*",
                        "PBS*.o*", "*.log"))
    return out


def _find_glob_first(directory: str, patterns):
    """在目录里按给定 glob 模式找**第一个**存在的文件（用于作业日志）。"""
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        return None
    for pat in patterns:
        rx = re.compile("^" + re.escape(pat).replace(r"\*", ".*")
                        .replace(r"\?", ".") + "$")
        for n in names:
            if rx.match(n):
                p = os.path.join(directory, n)
                if os.path.isfile(p):
                    return p
    return None


# ---------------------------------------------------------------------------
# 4. 物理小工具
# ---------------------------------------------------------------------------
class Cell:
    """晶格 + 由它派生的一切（体积、倒格矢、长度）。

    只用三行晶格矢量（VASP 的 POSCAR 格式），不引入任何第三方库。
    """

    def __init__(self, vectors, scale: float = 1.0):
        self.v = [[float(x) * scale for x in row] for row in vectors]

    def __repr__(self) -> str:
        return "Cell(%s)" % (self.v,)

    def volume(self) -> float:
        a, b, c = self.v
        return abs(a[0] * (b[1] * c[2] - b[2] * c[1])
                   - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0]))

    def lengths(self):
        return tuple(math.sqrt(sum(x * x for x in row)) for row in self.v)

    def reciprocal(self):
        """倒格矢（**不带 2π**，与 VASP 内部 ulx,y,z 的约定一致）。

        b1 = (a2 × a3)/V 等。带不带 2π 影响"k 点密度"的定义，
        本模块统一用不带 2π 的约定，并在用到的地方写清楚。
        """
        a, b, c = self.v
        vol = self.volume()
        if vol <= 0:
            raise ValueError("晶格体积为 0，无法求倒格矢（结构文件有问题？）")
        def cross(u, w):
            return [u[1] * w[2] - u[2] * w[1],
                    u[2] * w[0] - u[0] * w[2],
                    u[0] * w[1] - u[1] * w[0]]
        return [[x / vol for x in cross(b, c)],
                [x / vol for x in cross(c, a)],
                [x / vol for x in cross(a, b)]]

    def reciprocal_lengths(self):
        return tuple(math.sqrt(sum(x * x for x in row))
                     for row in self.reciprocal())

    def is_vacuum_axis_present(self, min_vacuum: float = 8.0):
        """粗判哪些方向"像是有真空"。

        判据：该方向的晶格长度 **远大于** 该方向原子的实际跨度。
        这是**启发式**，不是 VASP 的定义；只在"该不该提醒用户这是 slab"时用，
        **不要**用它替代物理判断，也不要在正式报告里当成事实陈述。
        """
        return None  # 需要原子坐标，见 is_slab()；此处保留接口占位

    def is_slab(self, positions, tol: float = 6.0):
        """返回 (是否像 slab, 每个方向的真空尺度)。

        `positions` 是笛卡尔坐标列表（Å）。判据：某方向的原子跨度比晶格长度
        小 `tol` Å 以上 ⇒ 该方向有真空 ⇒ 体系是低维的。
        """
        if not positions:
            return False, (0.0, 0.0, 0.0)
        holes = []
        for d in range(3):
            coord = sorted(p[d] for p in positions)
            span = coord[-1] - coord[0]
            length = self.lengths()[d]
            holes.append(max(0.0, length - span))
        return any(h >= tol for h in holes), tuple(holes)

    def kpoint_density(self, mesh, shift=(0.0, 0.0, 0.0)):
        """把 k 点网格折算成"每 Å⁻¹ 的采样密度"，用于跨体系比较。

        返回 (按倒格矢长度定义的密度, 每段实际间距 (d1,d2,d3))。
        间距 d_i = |b_i| / N_i —— 这是**跨体系可比的量**，
        比"N 取多少"更适合做收敛判据的比较基准。
        """
        bl = self.reciprocal_lengths()
        try:
            ns = [max(1, int(round(float(n)))) for n in mesh]
        except Exception:                                   # noqa: BLE001
            raise ValueError("k 点网格必须是三个整数，收到：%r" % (mesh,))
        spacing = tuple(bl[i] / ns[i] for i in range(3))
        return spacing


class Elements:
    """元素符号 ↔ 序号 的极简表（只覆盖常见元素，够用且零依赖）。

    ⚠️ 覆盖范围有限：1–96 号。若遇到表里没有的符号，`z()` 返回 None，
    调用方必须**如实说"不认识这个元素"**，不要猜。
    """

    SYMBOLS = (
        "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co "
        "Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb "
        "Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re "
        "Os Ir Pt Au Hg Tl Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es "
        "Fm Md No Lr"
    ).split()

    _Z = {s: i + 1 for i, s in enumerate(SYMBOLS)}

    @classmethod
    def z(cls, symbol: str):
        s = symbol.strip()
        if not s:
            return None
        return cls._Z.get(s[0].upper() + s[1:].lower())

    @classmethod
    def is_known(cls, symbol: str) -> bool:
        return cls.z(symbol) is not None


# ---------------------------------------------------------------------------
# 5. POSCAR
# ---------------------------------------------------------------------------
class PoscarData:
    """POSCAR 的解析结果。

    字段名与 VASP wiki 的 POSCAR 页一一对应，便于交叉核对。
    """

    __slots__ = ("path", "comment", "scale", "cell", "symbols", "counts",
                 "selective", "mode", "positions", "velocities", "lattice",
                 "species_line_is_symbols", "nions", "extra")

    def __init__(self):
        self.path = ""
        self.comment = ""
        self.scale = 1.0
        self.cell = None
        self.symbols = []          # 元素符号（若文件没写，则为空表）
        self.counts = []           # 每个元素几个原子
        self.selective = False
        self.mode = "Direct"       # Direct / Cartesian
        self.positions = []        # 分数或笛卡尔坐标，依 mode
        self.lattice = None        # None=全放开；否则每原子 3 个 T/F
        self.velocities = None
        self.species_line_is_symbols = False
        self.nions = 0
        self.extra = {}

    def cartesian(self):
        """把坐标统一成笛卡尔（Å）。Direct 时用晶格矩阵乘。"""
        if self.mode.lower().startswith("d"):
            v = self.cell.v
            out = []
            for p in self.positions:
                out.append([p[0] * v[0][d] + p[1] * v[1][d] + p[2] * v[2][d]
                            for d in range(3)])
            return out
        return [list(p) for p in self.positions]

    def formula(self) -> str:
        if self.symbols and len(self.symbols) == len(self.counts):
            return "".join("%s%d" % (s, c) for s, c in zip(self.symbols, self.counts))
        return "(元素未知)"

    def species_counts_line(self) -> str:
        return " ".join(str(c) for c in self.counts)


def _is_int(tok: str) -> bool:
    try:
        int(tok)
        return True
    except ValueError:
        return False


def read_poscar(path: str) -> PoscarData:
    """解析 POSCAR / CONTCAR。

    容错点（都是真实算例里见过的写法）：
    - 第二行 scale 可以是负数（= 目标体积）或三个数（= 每个方向一个缩放）；
    - 第 6 行**可能**是元素符号行，也可能直接是数目行 —— 靠"能不能都当整数读"判；
    - Direct/Cartesian 行可能被省略（老格式默认 Direct）；
    - Selective dynamics 存在时，坐标行后多三个 T/F。
    """
    text = read_text(path)
    lines = [ln for ln in text.split("\n")]
    # 丢掉纯空行是不安全的（坐标行不可能是空行，但注释行可能是空的），
    # 这里只在**开头**跳过空行。
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1

    def need(idx: int, what: str) -> str:
        if idx >= len(lines):
            die("POSCAR 格式不完整：读到文件结尾时还需要『%s』那一行。\n  文件：%s"
                % (what, path), EXIT_USER,
                "POSCAR 最少需要 8 行：注释 / scale / 3 行晶格 / 元素(可选) / 数目 / "
                "Direct|Cartesian / 坐标。")
        return lines[idx]

    d = PoscarData()
    d.path = path
    d.comment = need(i, "注释").strip()
    i += 1

    scale_line = need(i, "scale").split()
    i += 1
    try:
        scale_vals = [float(x) for x in scale_line[:3]]
    except ValueError:
        die("POSCAR 第 2 行（scale）不是数字：%r\n  文件：%s"
            % (need(i - 1, "scale").strip(), path), EXIT_USER)
        raise
    if len(scale_vals) == 1:
        scale = scale_vals[0]
        uniform = True
    elif len(scale_vals) == 3:
        uniform = False
        scale = 1.0
    else:
        die("POSCAR 第 2 行（scale）应有 1 个或 3 个数字，实际 %d 个。\n  文件：%s"
            % (len(scale_vals), path), EXIT_USER)
        raise AssertionError

    vecs = []
    for k in range(3):
        toks = need(i, "晶格矢量 %d" % (k + 1)).split()
        if len(toks) < 3:
            die("POSCAR 第 %d 行（晶格矢量）不足 3 个数：%r\n  文件：%s"
                % (i + 1, need(i, "").strip(), path), EXIT_USER)
        try:
            vecs.append([float(toks[0]), float(toks[1]), float(toks[2])])
        except ValueError:
            die("POSCAR 第 %d 行（晶格矢量）含非数字：%r\n  文件：%s"
                % (i + 1, need(i, "").strip(), path), EXIT_USER)
        i += 1

    if uniform:
        d.scale = scale
        d.cell = Cell(vecs, scale)
    else:
        d.scale = 1.0
        d.cell = Cell([[vecs[r][c] * scale_vals[c] for c in range(3)]
                       for r in range(3)])

    # 元素符号行 / 数目行
    line = need(i, "元素(可选)或数目").strip()
    i += 1
    toks = line.split()
    if toks and all(_is_int(t) for t in toks):
        d.symbols = []
        d.counts = [int(t) for t in toks]
        d.species_line_is_symbols = False
    else:
        d.symbols = toks
        d.species_line_is_symbols = True
        cnt_line = need(i, "数目").strip()
        i += 1
        ctoks = cnt_line.split()
        if not ctoks or not all(_is_int(t) for t in ctoks):
            die("POSCAR 的元素数目行不是整数：%r\n  文件：%s"
                % (cnt_line, path), EXIT_USER)
        d.counts = [int(t) for t in ctoks]

    if len(d.symbols) and len(d.symbols) != len(d.counts):
        die("POSCAR 元素符号有 %d 个，数目有 %d 个 —— 两者必须一一对应。\n  文件：%s"
            % (len(d.symbols), len(d.counts), path), EXIT_USER)

    # Selective dynamics
    line = need(i, "Selective dynamics 或 Direct/Cartesian").strip()
    i += 1
    if line[:1].lower() == "s":
        d.selective = True
        line = need(i, "Direct/Cartesian").strip()
        i += 1

    if line[:1].lower() in ("d",):
        d.mode = "Direct"
    elif line[:1].lower() in ("c", "k"):
        d.mode = "Cartesian"
    else:
        # 老格式允许省略这一行 —— 按 Direct 处理，但要提醒
        d.mode = "Direct"
        d.extra["mode_line_missing"] = line
        i -= 1
        warn("POSCAR 的 Direct/Cartesian 行缺失或无法识别（读到 %r），按 Direct 处理。\n"
             "  文件：%s" % (line, path))

    d.nions = sum(d.counts)
    if d.nions <= 0:
        die("POSCAR 的原子总数为 %d —— 数目行有问题。\n  文件：%s"
            % (d.nions, path), EXIT_USER)

    for k in range(d.nions):
        toks = need(i, "第 %d 个原子的坐标" % (k + 1)).split()
        if len(toks) < 3:
            die("POSCAR 第 %d 行（第 %d 个原子）不足 3 个坐标：%r\n  文件：%s"
                % (i + 1, k + 1, need(i, "").strip(), path), EXIT_USER)
        try:
            coord = [float(toks[0]), float(toks[1]), float(toks[2])]
        except ValueError:
            die("POSCAR 第 %d 行（第 %d 个原子）坐标含非数字：%r\n  文件：%s"
                % (i + 1, k + 1, need(i, "").strip(), path), EXIT_USER)
        d.positions.append(coord)
        if d.selective:
            flags = [t.upper()[:1] for t in toks[3:6]]
            if len(flags) < 3 or any(f not in ("T", "F") for f in flags):
                flags = (flags + ["T", "T", "T"])[:3]
                warn("POSCAR Selective dynamics 的 T/F 标志缺失或异常，"
                     "第 %d 个原子按全放开(T T T)处理。" % (k + 1))
            if d.lattice is None:
                d.lattice = []
            d.lattice.append(flags)
        i += 1

    # 可选的初速度
    if i < len(lines) and lines[i].strip():
        head = lines[i].strip().lower()
        if head.startswith(("c", "k")) and "cart" in head:
            i += 1
            vels = []
            for k in range(d.nions):
                if i >= len(lines):
                    break
                toks = lines[i].split()
                if len(toks) >= 3:
                    try:
                        vels.append([float(toks[0]), float(toks[1]), float(toks[2])])
                    except ValueError:
                        break
                i += 1
            if len(vels) == d.nions:
                d.velocities = vels
    return d


# ---------------------------------------------------------------------------
# 6. KPOINTS
# ---------------------------------------------------------------------------
class KpointsData:
    __slots__ = ("path", "comment", "nk", "mode", "scheme", "mesh", "shift",
                 "coords", "explicit", "tetra", "line_npts", "line_segments",
                 "auto_length", "gen_vectors", "raw_mode_line")

    def __init__(self):
        self.path = ""
        self.comment = ""
        self.nk = None
        self.mode = ""            # explicit|regular|generalized|line|auto|unknown
        self.scheme = ""          # Gamma|Monkhorst-Pack
        self.mesh = None
        self.shift = None
        self.coords = ""          # Cartesian|Reciprocal|fractional
        self.explicit = []        # [(kx,ky,kz,weight)]
        self.tetra = None
        self.line_npts = None
        self.line_segments = []   # [( (x,y,z), (x,y,z) )]
        self.auto_length = None
        self.gen_vectors = None
        self.raw_mode_line = ""


def read_kpoints(path: str) -> KpointsData:
    """解析 KPOINTS。

    wiki 定义的五种模式（见 references/official/pages/KPOINTS.md）：
    显式列表 / 规则网格 / 广义规则网格 / line 模式 / 全自动。
    识别靠**第三行第一个非空字符**，这与 wiki 的说明一致。
    """
    text = read_text(path)
    lines = text.split("\n")
    d = KpointsData()
    d.path = path
    if len(lines) < 3:
        die("KPOINTS 至少需要 3 行（注释 / k 点数 / 模式行）。\n  文件：%s" % path,
            EXIT_USER)
    d.comment = lines[0].strip()
    try:
        d.nk = int(lines[1].split()[0])
    except (ValueError, IndexError):
        die("KPOINTS 第 2 行应为 k 点数目（整数），实际是：%r\n  文件：%s"
            % (lines[1].strip(), path), EXIT_USER)
        raise

    mode_line = lines[2] if len(lines) > 2 else ""
    d.raw_mode_line = mode_line.strip()
    first = mode_line.strip()[:1]

    if d.nk > 0:
        d.mode = "explicit"
        if len(lines) > 3:
            d.coords = lines[3].strip()
        for ln in lines[4:4 + d.nk]:
            toks = ln.split()
            if len(toks) < 3:
                continue
            try:
                vals = [float(t) for t in toks[:4]]
            except ValueError:
                continue
            while len(vals) < 4:
                vals.append(1.0)
            d.explicit.append(tuple(vals))
        # 四面体方法
        rest = lines[4 + d.nk:]
        for idx, ln in enumerate(rest):
            if ln.strip()[:1].lower() == "t":
                d.tetra = {"header": ln.strip()}
                if idx + 1 < len(rest):
                    d.tetra["count_line"] = rest[idx + 1].strip()
                break
        return d

    # nk == 0 起，都是自动模式
    if first.lower() == "l":
        d.mode = "line"
        try:
            d.line_npts = int(lines[1].split()[0]) if False else None
        except Exception:                                   # noqa: BLE001
            d.line_npts = None
        # line 模式下：第 2 行是每段点数
        try:
            d.line_npts = int(lines[1].split()[0])
        except (ValueError, IndexError):
            d.line_npts = None
        if len(lines) > 3:
            d.coords = lines[3].strip()
        pts = []
        for ln in lines[4:]:
            toks = ln.split()
            if len(toks) < 3:
                if ln.strip() == "" and pts:
                    continue
                continue
            try:
                pts.append((float(toks[0]), float(toks[1]), float(toks[2]),
                            toks[3] if len(toks) > 3 else ""))
            except ValueError:
                continue
        for k in range(0, len(pts) - 1, 2):
            d.line_segments.append(((pts[k][0], pts[k][1], pts[k][2]),
                                    (pts[k + 1][0], pts[k + 1][1], pts[k + 1][2])))
        return d

    if first.lower() == "a":
        d.mode = "auto"
        if len(lines) > 3:
            try:
                d.auto_length = float(lines[3].split()[0])
            except (ValueError, IndexError):
                d.auto_length = None
        return d

    # Gamma / Monkhorst-Pack / 广义规则网格（靠第 3 行是字母还是 'c'/'r' 区分）
    grid_line = lines[3] if len(lines) > 3 else ""
    if first.lower() in ("c", "k", "r"):
        d.mode = "generalized"
        d.coords = mode_line.strip()
        vecs = []
        for ln in lines[3:6]:
            toks = ln.split()
            if len(toks) < 3:
                break
            try:
                vecs.append([float(t) for t in toks[:3]])
            except ValueError:
                break
        d.gen_vectors = vecs or None
        if len(lines) > 6:
            try:
                d.shift = [float(t) for t in lines[6].split()[:3]]
            except ValueError:
                d.shift = None
        return d

    d.mode = "regular"
    d.scheme = "Gamma" if first.lower() == "g" else (
        "Monkhorst-Pack" if first.lower() == "m" else "unknown(%r)" % first)
    toks = grid_line.split()
    if len(toks) < 3:
        die("KPOINTS 第 4 行应为三个网格数（N1 N2 N3），实际是：%r\n  文件：%s"
            % (grid_line.strip(), path), EXIT_USER)
    try:
        d.mesh = [int(t) for t in toks[:3]]
    except ValueError:
        die("KPOINTS 第 4 行的网格数不是整数：%r\n  文件：%s"
            % (grid_line.strip(), path), EXIT_USER)
    if len(lines) > 4:
        stoks = lines[4].split()
        if len(stoks) >= 3:
            try:
                d.shift = [float(t) for t in stoks[:3]]
            except ValueError:
                d.shift = None
    return d


# ---------------------------------------------------------------------------
# 7. INCAR
# ---------------------------------------------------------------------------
class IncarData:
    """INCAR 的解析结果。

    保留**行号**与**原始行**，因为"哪个关键字写在第几行"对报错定位很重要，
    也是引用审计能核对的对象。
    """

    __slots__ = ("path", "tags", "lines", "comments", "raw", "semicolon_split",
                 "unknown_lines")

    def __init__(self):
        self.path = ""
        self.tags = {}         # TAG -> (值字符串, 行号)
        self.lines = []        # (行号, 原始行)
        self.comments = {}     # TAG -> 行内注释
        self.raw = ""
        self.semicolon_split = []
        self.unknown_lines = []

    def get(self, tag: str, default=None):
        t = self.tags.get(tag.upper())
        return t[0] if t else default

    def get_int(self, tag: str, default=None):
        v = self.get(tag)
        if v is None:
            return default
        try:
            return int(float(v.split()[0]))
        except (ValueError, IndexError):
            return default

    def get_float(self, tag: str, default=None):
        v = self.get(tag)
        if v is None:
            return default
        try:
            return float(v.split()[0])
        except (ValueError, IndexError):
            return default

    def get_bool(self, tag: str, default=None):
        v = self.get(tag)
        if v is None:
            return default
        s = v.strip().strip(".").upper()
        if s.startswith("T") or s == "TRUE":
            return True
        if s.startswith("F") or s == "FALSE":
            return False
        return default

    def line_of(self, tag: str):
        t = self.tags.get(tag.upper())
        return t[1] if t else None


def read_incar(path: str) -> IncarData:
    """解析 INCAR（tagged free-ASCII）。

    按 VASP wiki 的 INCAR 格式页，需要处理：
    - `#` 或 `!` 之后是注释；
    - 一行可以有**多条**语句，用 `;` 分隔；
    - 长行可用 `\\` 续行（**反斜杠后不能有空格**，某些版本会解析失败）；
    - 值可用双引号包裹以跨行（如 WANNIER90_WIN）；
    - 嵌套标签 `A/B = ...`，或用 `PREFIX { ... }` 块。
    """
    text = read_text(path)
    d = IncarData()
    d.path = path
    d.raw = text
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        lineno = i + 1
        raw = lines[i]
        d.lines.append((lineno, raw))
        stripped = raw.strip()
        i += 1
        if not stripped:
            continue

        # 剥注释（引号内的 # / ! 不算注释）
        code, comment = _strip_comment(raw)
        code = code.strip()
        if not code:
            continue

        # 处理续行
        while code.rstrip().endswith("\\"):
            back = code.rstrip()[:-1]
            if code.rstrip() != code.rstrip() + "" and code.rstrip()[-2:-1] == " ":
                d.unknown_lines.append((lineno, "反斜杠前有空格（某些 VASP 版本会解析失败）"))
            code = back
            if i < len(lines):
                nxt, _ = _strip_comment(lines[i])
                d.lines.append((i + 1, lines[i]))
                code += " " + nxt.strip()
                i += 1
            else:
                break

        # 引号跨行
        if code.count('"') % 2 == 1:
            while i < len(lines) and code.count('"') % 2 == 1:
                code += "\n" + lines[i]
                d.lines.append((i + 1, lines[i]))
                i += 1

        # 分号分隔的多语句
        parts = [p.strip() for p in code.split(";") if p.strip()]
        if len(parts) > 1:
            d.semicolon_split.append((lineno, parts))
        for part in parts:
            _record_tag(d, part, lineno, comment)

    return d


def _strip_comment(raw: str):
    out = []
    in_quote = False
    comment = ""
    for idx, ch in enumerate(raw):
        if ch == '"':
            in_quote = not in_quote
        if not in_quote and ch in "#!":
            comment = raw[idx + 1:].strip()
            break
        out.append(ch)
    return "".join(out), comment


def _record_tag(d: IncarData, part: str, lineno: int, comment: str) -> None:
    if "=" not in part:
        # 不是 tag = value 形式 —— VASP 会忽略，但我们记下来供校验器提示
        d.unknown_lines.append((lineno, part))
        return
    tag, _, val = part.partition("=")
    tag = tag.strip()
    val = val.strip()
    if not tag:
        d.unknown_lines.append((lineno, part))
        return
    key = tag.upper()
    if key in d.tags:
        d.unknown_lines.append(
            (lineno, "重复出现：%s（本文件第 %d 行已给过）"
             % (tag, d.tags[key][1])))
    d.tags[key] = (val, lineno)
    if comment:
        d.comments[key] = comment


# ---------------------------------------------------------------------------
# 8. POTCAR 头部（**只读头部，不读表数据**）
# ---------------------------------------------------------------------------
class PotcarInfo:
    __slots__ = ("path", "titles", "elements", "enmax", "enmin", "zval",
                 "pomass", "lexch", "n_datasets", "has_copyright")

    def __init__(self):
        self.path = ""
        self.titles = []
        self.elements = []
        self.enmax = []
        self.enmin = []
        self.zval = []
        self.pomass = []
        self.lexch = []
        self.n_datasets = 0
        self.has_copyright = False

    def max_enmax(self):
        return max(self.enmax) if self.enmax else None

    def total_valence(self):
        return sum(self.zval) if self.zval else None


def parse_potcar_header(path: str) -> PotcarInfo:
    """只读 POTCAR 的**头部元数据**（TITEL/ENMAX/ENMIN/ZVAL/POMASS/LEXCH）。

    ⚠️ **许可与设计边界（必读）**
    - POTCAR 受 VASP 许可保护，**不得进仓库、不得再分发**。本函数**不复制、
      不缓存、不写出**任何 POTCAR 内容；它只在用户自己的目录里就地读取头部
      几个数字，用于：
        * 判断 `ENCUT` 是否低于 POTCAR 自身的 `ENMAX`（这是最常见的"欠收敛"来源）；
        * 核对 POSCAR 的元素顺序与 POTCAR 的 TITEL 顺序是否一致（**跨文件硬约束**）；
        * 估算电子数（ZVAL 之和），供 `NELECT`/带电体系检查用。
    - 输出里**只出现数字与元素名**，绝不回显 POTCAR 正文。
    - 这也意味着本 skill **不能**替你生成 POTCAR —— 它只能**校验**你已经有的那个。

    POTCAR 由多个数据块拼接，每块以 `End of Dataset` 结束。
    """
    d = PotcarInfo()
    d.path = path
    cur_title = None
    with open_maybe_gz(path, "rb") as fh:
        for raw in fh:
            try:
                line = raw.decode("utf-8")
            except UnicodeDecodeError:
                line = raw.decode("latin-1")
            line = line.rstrip("\r\n")
            if "End of Dataset" in line:
                d.n_datasets += 1
                continue
            # 真实 POTCAR 里标签**有前导空格**（`   TITEL  = ...`），
            # 所以一律用 "in line"，不能用 startswith —— 早期版本这里写错，
            # 导致 titles/enmax 全空却静默通过（已记录在 CHANGELOG 的更正记录里）。
            if "TITEL" in line and "=" in line:
                val = line.split("=", 1)[1].strip()
                d.titles.append(val)
                # TITEL = PAW_PBE Ti_pv 07Sep2000  → 元素是第 2 个 token
                # 变体要一并剥掉：
                #   `Ti_pv` `Ga_d` `Y_sv`  → 下划线后缀表示半芯态参与价电子
                #   `H.75`                 → 点号后缀表示**分数占据**的赝势
                #     （真实算例 day1/GaN 用的就是 H.75，ZVAL=0.75；
                #      见 references/raw/D1.txt 里学员就此提问的那一段）
                toks = val.split()
                el = toks[1] if len(toks) > 1 else ""
                for sep in ("_", "."):
                    if sep in el:
                        el = el.split(sep)[0]
                d.elements.append(el)
                cur_title = val
                continue
            if "LEXCH" in line and "=" in line:
                d.lexch.append(line.split("=", 1)[1].strip())
                continue
            if "ENMAX" in line or "ENMIN" in line:
                # 形如：   ENMAX  =  267.882; ENMIN  =  200.911 eV
                # —— **两个标签在同一行**，所以不能 continue，要都处理。
                for key, bucket in (("ENMAX", d.enmax), ("ENMIN", d.enmin)):
                    if key in line:
                        seg = line.split(key, 1)[1].lstrip(" =")
                        num = ""
                        for ch in seg:
                            if ch.isdigit() or ch == ".":
                                num += ch
                            else:
                                break
                        try:
                            bucket.append(float(num))
                        except ValueError:
                            pass
                continue
            if "POMASS" in line or "ZVAL" in line:
                for key, bucket in (("POMASS", d.pomass), ("ZVAL", d.zval)):
                    if key in line:
                        seg = line.split(key, 1)[1].lstrip(" =")
                        num = ""
                        for ch in seg:
                            if ch.isdigit() or ch in ".+-":
                                num += ch
                            else:
                                break
                        try:
                            bucket.append(float(num))
                        except ValueError:
                            pass
                continue
            if "COPYRIGHT" in line.upper() or "copyright" in line:
                d.has_copyright = True
    # 循环结束后（**不是循环体内**）再判：一份 POTCAR 至少要有一处可识别标记
    if d.n_datasets == 0 and not d.titles:
        die("这个文件看起来不是 POTCAR（没有 TITEL 行，也没有 'End of Dataset'）：%s"
            % path, EXIT_USER,
            "POTCAR 由多个数据块拼接，每块以 'End of Dataset' 结束。\n"
            "请确认你指向的是真正的 POTCAR。")
    return d


# ---------------------------------------------------------------------------
# 9. OUTCAR —— **只读"程序到底认了什么"这一层**
# ---------------------------------------------------------------------------
def outcar_version(path: str, max_lines: int = 400) -> str:
    """取 OUTCAR 第一行的 VASP 版本字符串（解析结果里**必须带版本号**）。

    为什么必须带：输出格式会**跨版本漂移**。不带版本号的解析结果，
    在换了 VASP 版本之后无法判断"解析不到"是因为格式变了还是因为算例本身没有这项。

    取不到返回空串（**不要编一个版本号**）。
    """
    n = 0
    for _lineno, line in iter_lines(path):
        n += 1
        s = line.strip()
        if s.lower().startswith("vasp."):
            return s
        if n >= max_lines:
            break
    return ""


def parse_version_number(version_line: str):
    """从版本串里取出**可比的三元组**，例如
    `vasp.5.4.4.18Apr17-6-g9f103f2a35 (build …)` ⇒ `(5, 4, 4)`。

    取不到返回 `None`（**不要编一个版本号**）。

    为什么需要它：`outcar_version()` 只是把那一行**原样读回来**，
    而做"这个标签你的版本支持吗"这种判断**必须能比大小**。
    """
    if not version_line:
        return None
    m = re.search(r"vasp\.?\s*(\d+)\.(\d+)(?:\.(\d+))?", version_line, re.I)
    if not m:
        return None
    return (int(m.group(1)), int(m.group(2)), int(m.group(3) or 0))


def parse_version_tuple(v: str):
    """把 `6.5.0` / `6.4` 这类字符串转成三元组。取不到返回 None。"""
    v = (v or "").strip()
    if not v or v == "-":
        return None
    try:
        parts = [int(x) for x in v.split(".")]
    except ValueError:
        return None
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


# --- 版本门控表（从 `references/official/_versions.tsv` 惰性载入） ---
_VERSIONS_CACHE = None
_VERSIONS_PATH = None


def _versions_file() -> str:
    """定位 `references/official/_versions.tsv`。"""
    global _VERSIONS_PATH
    if _VERSIONS_PATH is not None:
        return _VERSIONS_PATH
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (
        os.environ.get("VASP_SKILL_ROOT", ""),
        os.path.abspath(os.path.join(here, os.pardir)),
        os.path.abspath(os.path.join(here, os.pardir, os.pardir)),
    ):
        if not cand:
            continue
        p = os.path.join(cand, "references", "official", "_versions.tsv")
        if os.path.exists(p):
            _VERSIONS_PATH = p
            return p
    _VERSIONS_PATH = ""
    return ""


def loaded_version_gates_path() -> str:
    """返回版本门控表的实际路径（`` 表示没找到）。

    工具用它来如实告知"版本知识这次**有没有生效**" ——
    找不到表时**必须降级为"未检查"**，不能假装检查过了。
    """
    return _versions_file()


# ---------------------------------------------------------------------------
# 9b. LOG / 作业输出 —— **作业"起没起来"这一层**
# ---------------------------------------------------------------------------
# 为什么单列一层（本项目的一次真实事故）：
#   `diagnose.py` 原来的 13 条规则**全部建立在"计算跑完了"的假设上** ——
#   它们读 `OUTCAR`/`OSZICAR` 的**内容行**（离子步、能量、力）。
#   而用户真实遇到的问题是「**作业第一次 SCF 就崩**」：
#   `OSZICAR` 只有表头、`OUTCAR` 停在 `entering main loop`，
#   于是那些规则要么不触发、要么给出**不可能执行的处方**
#   （"看 OSZICAR 最后一步的 d E" —— 可它没有最后一步）。
#
#   ⇒ **"跑完了但结果不对"与"根本没跑起来"是两类问题，需要两套信号。**
#     这一层读的是 LOG / 作业日志 / 启动横幅。
#
# ⚠️ 本层的能力边界（必须让用户看到）：
#   · 它**只做文本特征匹配**，不理解 MPI 运行时；
#   · **`exit code` 不参与判断** —— `mpirun` 下崩溃时退出码可能仍是 0 或 255，
#     语义不可靠（`[实测]`，见 `references/playbook.md` 的作业层条目）；
#   · LOG 可能不存在（不一定重定向到文件）⇒ 找不到就**降级为"未检查"**。

# 崩溃 / 并行相关的可 grep 特征。
# ⚠️ 每条都注明"它单独能不能作为证据" —— 见 `parse_launch_log` 的返回说明。
LAUNCH_PATTERNS = [
    ("segv", r"forrtl:\s*severe\s*\(\s*174\s*\)|SIGSEGV|segmentation fault",
     "Fortran 运行时**段错误**（程序崩了）"),
    ("bad_termination", r"BAD TERMINATION OF ONE OF YOUR APPLICATION PROCESSES",
     "MPI 报告：**有 rank 崩了**，其余被收尸"),
    ("killed9", r"KILLED BY SIGNAL:\s*9", "某个 rank 被 SIGKILL（常是收尸，**不是**根因）"),
    ("stack_ulimit", r"ulimit:\s*stack size:\s*cannot modify limit",
     "队列不让改栈上限（⚠️ **红鲱鱼**：成功的作业里也会出现）"),
    ("oom", r"Out of memory|oom-kill|OutOfMemory|cannot allocate memory",
     "内存分配失败"),
    ("mpi_abort", r"MPI_ABORT|mpirun.*detected that one process|"
                 r"One of the processes has terminated", "MPI 中止"),
    ("internal_error", r"internal error in subroutine", "VASP 内部错误"),
]

# 启动横幅里的并行分解信息（**这是诊断的关键线索**）
RE_BANNER_CORES = re.compile(r"running on\s+(\d+)\s+total cores")
RE_BANNER_DISTRK = re.compile(
    r"distrk:\s*each k-point on\s+(\d+)\s+cores,\s*(\d+)\s+groups")
RE_BANNER_DISTR = re.compile(
    r"distr:\s*one band on\s+(?:NCORES_PER_BAND=\s*)?(\d+)\s+cores,?\s*"
    r"(\d+)\s+groups")
RE_BANNER_NCORE_TIP = re.compile(
    r"NCORE\s*=\s*4\s*-\s*approx SQRT", re.I)


def parse_launch_log(path: str, max_bytes: int = 4 << 20):
    """解析 LOG / 作业日志，返回"作业起没起来"这一层的信息。

    返回 dict（**键一定存在**，取不到的值为 `None`/空）：

    | 键 | 含义 |
    |---|---|
    | `found` | 文件读到了吗 |
    | `crashes` | 命中的崩溃特征 `[(kind, 匹配到的行, 行号)]` |
    | `first_crash_line` | **第一条**崩溃行（要引导用户看这一条，不是 SIGKILL） |
    | `total_cores` | `running on N total cores` |
    | `distrk` | `(cores_per_kpoint, groups)` |
    | `distr` | `(cores_per_band, band_groups)` —— **最关键的一行** |
    | `vasp_ncore_tip` | 横幅里有没有 VASP 自己那句 `NCORE = 4 - approx SQRT(...)` |
    | `oszsicar_started` | （由调用方填）`OSZICAR` 里有没有迭代行 |

    ⚠️ **"命中了崩溃特征"只说明程序崩了，不说明为什么崩。**
    归因要结合 `distr` 行、`INCAR` 的并行设置与体系规模 —— 见
    `diagnose.py` 的 `LAUNCH.*` 规则。
    """
    info = {
        "found": False, "crashes": [], "first_crash_line": None,
        "total_cores": None, "distrk": None, "distr": None,
        "vasp_ncore_tip": False, "lines_read": 0,
    }
    if not path or not os.path.exists(path):
        return info
    info["found"] = True
    n = 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, start=1):
                n += 1
                if n > 200000:
                    break
                if RE_BANNER_CORES.search(line):
                    info["total_cores"] = int(
                        RE_BANNER_CORES.search(line).group(1))
                m = RE_BANNER_DISTRK.search(line)
                if m:
                    info["distrk"] = (int(m.group(1)), int(m.group(2)))
                m = RE_BANNER_DISTR.search(line)
                if m:
                    info["distr"] = (int(m.group(1)), int(m.group(2)))
                if RE_BANNER_NCORE_TIP.search(line):
                    info["vasp_ncore_tip"] = True
                for kind, pat, _desc in LAUNCH_PATTERNS:
                    if re.search(pat, line, re.I):
                        info["crashes"].append((kind, line.strip(), i))
    except OSError:
        return info
    info["lines_read"] = n
    # 第一条崩溃行 —— **要引导用户看它，而不是被后面的 SIGKILL 误导**
    if info["crashes"]:
        info["first_crash_line"] = info["crashes"][0]
    return info


def oszsicar_iterations(path: str, max_lines: int = 400) -> int:
    """数 `OSZICAR` 里的**电子步迭代行**（`DAV:` / `RMM:` 开头）。

    为什么要单独一个函数：**"`OSZICAR` 只有表头"是"计算没跑起来"最硬的信号**
    —— 它比任何报错文本都可靠（报错可能没被重定向进文件，而 `OSZICAR`
    是 VASP 自己写的）。

    注意 `OSZICAR` 的表头行是
    `       N       E                     dE             d eps       ncg ...`，
    第 3 行起才是迭代行。这里**只认行首是 `DAV:` / `RMM:` / `CG :` 等算法名**的行。
    """
    if not path or not os.path.exists(path):
        return 0
    n = 0
    got = 0
    for _ln, line in iter_lines(path):
        n += 1
        s = line.lstrip()
        if re.match(r"(DAV|RMM|CG|EDDAV|EDSTEP|BROYDEN)\s*:", s):
            got += 1
        if n >= 500000:
            break
    return got


def load_version_gates() -> dict:
    """载入官方版本门控表：`{TAG: {"available": "6.5.0", ...}}`。

    ⚠️ **表里没有的标签，不代表所有版本都支持。**
    官方只对"新加的"标 `{{Available}}`；"没有条目"只能读作
    「**官方未标注版本门槛**」。工具的措辞必须照这个来。

    ⚠️⚠️ **只采信 `available` / `available_upto` / `deprecated` 这三种结构化标注，
    刻意**不采信** `min_version_text`**（正文散文里的 "in VASP.6.4" 之类）。
    理由是本项目**实测量出来的一个反例**：

        若把 `min_version_text` 也当成门槛，那么对一个 5.4.4 用户会报出
            `GGA`   需 6.4.3  （94 个真实算例里出现）
            `ISIF`  需 6.4.1  （94 个）
            `ISPIN` 需 6.5.0  （49 个）
        而这三个标签**显然在 5.4.4 里就有**。
        根因：那句话是在讲**该标签某个新增取值**的版本（例如"`ISIF=8` 自 6.4.1 起"），
        而不是"整个标签自那时才有"。

    ⇒ **散文里的版本只作线索，不作门槛。** 门槛必须有官方结构化标注兜底。
      这一条让"版本检查"从"噪声制造机"变成"只报官方明文标了的"。
    """
    global _VERSIONS_CACHE
    if _VERSIONS_CACHE is not None:
        return _VERSIONS_CACHE
    gates = {}
    p = _versions_file()
    if not p:
        _VERSIONS_CACHE = gates
        return gates
    try:
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("#") or not line.strip():
                    continue
                t = line.rstrip("\n").split("\t")
                if len(t) < 5:
                    continue
                page, tag, kind, ver, upto = t[0], t[1], t[2], t[3], t[4]
                for key in (tag.upper(), page.upper()):
                    if not key:
                        continue
                    g = gates.setdefault(key, {})
                    if kind == "available":
                        g.setdefault("available", ver)
                    elif kind == "available_upto":
                        g.setdefault("available", ver)
                        g.setdefault("removed", upto)
                    elif kind == "deprecated":
                        g["deprecated"] = True
                    elif kind in ("removed_text", "available_state"):
                        g.setdefault("removed", ver or "?")
    except OSError:
        pass
    _VERSIONS_CACHE = gates
    return gates


def version_gate_status(tag: str, user_version):
    """判断一个标签对**这个用户版本**是否可用。

    返回 `(status, detail)`，`status` ∈

    | status | 含义 |
    |---|---|
    | `ok` | 官方标了门槛，且用户版本满足 |
    | `too_old` | **官方标了门槛，用户版本不够** ⇒ 程序可能**静默忽略**它 |
    | `deprecated` | 官方标了 deprecated（**能跑，但不推荐**） |
    | `unknown` | **官方未标注版本门槛**（≠ 所有版本都支持） |

    ⚠️ 两种"不知道"必须分开说：
    - `unknown` = 官方没写门槛（**这是绝大多数标签的情况**）；
    - `user_version` 为 None = **我们没拿到用户的版本**（本来能判却判不了）。
    """
    tag_u = (tag or "").upper()
    g = load_version_gates().get(tag_u)
    if not g:
        return "unknown", "官方未标注版本门槛（≠ 所有版本都支持）"
    if user_version is None:
        return "unknown", ("该标签官方标注了版本门槛 `%s`，"
                           "但**没有拿到你的 VASP 版本**，无法判断"
                           % g.get("available", "?"))
    avail = parse_version_tuple(g.get("available", ""))
    if avail and user_version < avail:
        return "too_old", ("官方标注 `Available | %s`，而你是 `%s` ⇒ "
                           "**这个标签在你的版本上可能不存在**，"
                           "程序可能**静默忽略**它"
                           % (g.get("available"), ".".join(map(str, user_version))))
    removed = parse_version_tuple(g.get("removed", ""))
    if removed and user_version >= removed:
        return "too_old", ("官方标注该标签止于 `%s`，而你是 `%s` ⇒ "
                           "**已被移除**"
                           % (g.get("removed"), ".".join(map(str, user_version))))
    if g.get("deprecated"):
        return "deprecated", "官方标了 `deprecated`（能跑，但不推荐）"
    return "ok", "官方门槛 `%s`，你的版本满足" % g.get("available", "?")


def outcar_recognized_tags(path: str, max_lines: int = 400000) -> "set[str]":
    """扫 OUTCAR，收集**VASP 真正识别到的 INCAR 标签名**。

    这是本 skill 里"归属校验"的**第二来源，也是更强的一来源**。
    依据（官方 INCAR 页原文）：

        VASP writes its interpretation of the data in the INCAR file
        to the OUTCAR file. Please verify that it agrees with the
        intended setup.

    也就是说：**OUTCAR 里出现了这个标签名 ⇒ VASP 确实认了它**。
    反过来，一个不在官方分类页里的标签（插件标签、或在分类页里缺失的
    核心标签）只要出现在 OUTCAR 的回显段里，就不是"拼错了"。

    实现要点
    --------
    * 只看**头部回显区**（默认前 40 万行足够），不看后面几百万行的迭代输出；
    * 用**词边界**匹配，避免 `LDAU` 命中 `LDAUTYPE`；
    * 一行可能有多个标签（`AMIX_MAG = 1.60;   BMIX_MAG = 1.00`），所以逐行 findall。
    """
    pat = re.compile(r"(?<![A-Za-z0-9_/])([A-Z][A-Z0-9_]{2,40})(?![A-Za-z0-9_])")
    found: "set[str]" = set()
    n = 0
    for _lineno, line in iter_lines(path):
        n += 1
        if n > max_lines:
            break
        # 快筛：回显行几乎都含 '='；纯数据行跳过，省时间
        if "=" not in line:
            continue
        for m in pat.finditer(line):
            found.add(m.group(1))
    return found


def outcar_fermi(path: str):
    """取 OUTCAR 里的 `E-fermi`（最后一个值）。取不到返回 None。"""
    val = None
    for _lineno, line in iter_lines(path):
        if "E-fermi" in line:
            parts = line.replace(":", " ").split()
            for i, p in enumerate(parts):
                if p == "E-fermi" and i + 1 < len(parts):
                    try:
                        val = float(parts[i + 1])
                    except ValueError:
                        pass
    return val


def outcar_nions(path: str):
    """取 `NIONS =`。用于核对 POSCAR 与 OUTCAR 的原子数是否一致。"""
    for _lineno, line in iter_lines(path):
        if "NIONS" in line:
            m = re.search(r"NIONS\s*=\s*(\d+)", line)
            if m:
                return int(m.group(1))
    return None


def outcar_encut(path: str):
    """取 `ENCUT  = ... eV` 里 VASP **实际使用**的截断能（eV）。

    ⚠️ 这一项特别值得交叉核对：如果你没在 INCAR 写 ENCUT，
    VASP 用的是 POTCAR 的 ENMAX，而 **OUTCAR 里才看得到它到底取了哪个值**。
    """
    for _lineno, line in iter_lines(path):
        m = re.search(r"ENCUT\s*=\s*([\d.]+)\s*eV", line)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
    return None


# ---------------------------------------------------------------------------
# 10. OUTCAR —— 能量 / 力 / 收敛历史
# ---------------------------------------------------------------------------
class IonicStep:
    """一个离子步的结果。

    ⚠️ **能量取 `energy(sigma->0)`，不是 `free energy TOTEN`。**
    理由见 references/decide.md §14.1：`TOTEN` 含展宽熵项 `−TS`，
    依赖 `SIGMA`/`ISMEAR`，两套不同展宽参数之间**不可比**。
    """

    __slots__ = ("index", "toten", "energy_sigma0", "energy_wo_entropy",
                 "fermi", "max_force", "rms_force", "total_drift",
                 "n_scf_steps", "forces", "volume", "cell", "reached_required")

    def __init__(self, index: int):
        self.index = index
        self.toten = None
        self.energy_sigma0 = None
        self.energy_wo_entropy = None
        self.fermi = None
        self.max_force = None
        self.rms_force = None
        self.total_drift = None
        self.n_scf_steps = 0
        self.forces = []          # [(elem, fx, fy, fz)]
        self.volume = None
        self.cell = None
        self.reached_required = False

    def sum_forces(self):
        """返回 (ΣFx, ΣFy, ΣFz)。这是"力平衡"不变量要用的量。"""
        if not self.forces:
            return None
        return (sum(x[1] for x in self.forces),
                sum(x[2] for x in self.forces),
                sum(x[3] for x in self.forces))

    def sum_forces_vec(self):
        """返回 (ΣFx, ΣFy, ΣFz, |ΣF|)。"""
        s = self.sum_forces()
        if s is None:
            return None
        return (s[0], s[1], s[2], math.sqrt(sum(v * v for v in s)))


def outcar_ionic_steps(path: str, want_forces: bool = True,
                       max_steps: int = 100000) -> "list[IonicStep]":
    """流式解析 OUTCAR，返回每个离子步的能量/力/收敛信息。

    为什么必须**流式**：真实的 `OUTCAR` 动辄几十上百 MB
    （本项目里的算例最大 15 MB，生产算例常到 GB）。
    一次性读进内存再找关键行是最常见的 OOM 来源。

    识别逻辑（对着真实 OUTCAR 校准过，见 `day2/Ag/OUTCAR`）：

    * `FREE ENERGIE OF THE ION-ELECTRON SYSTEM` 出现 ⇒ 一个离子步的电子循环结束；
      紧随其后会打印 `free  energy   TOTEN` 与
      `energy  without entropy = ... energy(sigma->0) = ...`
    * `E-fermi :   0.9613 ...` 记录该离子步的费米能
    * `POSITION   TOTAL-FORCE` 之后是力表，表末 `total drift:` 是 ΣF
    * `reached required accuracy - stopping structural energy minimisation`
      表示离子循环按判据收敛了
    * `aborting loop because EDIFF is reached` 表示**电子**循环收敛
      （这是每个离子步都会出现的，**不要**把它当成离子步收敛）
    """
    steps: "list[IonicStep]" = []
    cur: "IonicStep | None" = None
    in_force_block = False

    def _ensure(idx: int) -> IonicStep:
        while len(steps) < idx:
            steps.append(IonicStep(len(steps) + 1))
        return steps[idx - 1]

    for _lineno, line in iter_lines(path):
        if len(steps) >= max_steps:
            break
        s = line.strip()

        # 电子循环收敛（**每个离子步都会出现**，不是离子步收敛）
        if "aborting loop because EDIFF is reached" in line:
            if cur is not None:
                cur.n_scf_steps += 1
            continue

        # ⚠️ 力的解析**不能**依赖 "FREE ENERGIE" 出现过。
        # 实测：`day2/Ag` 是 NSW=0 的单点计算，`TOTAL-FORCE` 块在
        # `FREE ENERGIE OF THE ION-ELECTRON SYSTEM` **之前**就打印了
        # （电子循环末尾），所以早期"先见到 FREE ENERGIE 才建 IonicStep"
        # 的写法会把这些体系的所有力都丢掉。已记入 CHANGELOG 更正记录。
        if "TOTAL-FORCE" in line:
            # 同一离子步里可能出现多个力块（VASP 的不同阶段），
            # 只保留第一个，避免力表被重复追加。
            if cur is not None and cur.forces:
                in_force_block = False
                continue
            if cur is None:
                cur = _ensure(len(steps) + 1)
            in_force_block = True
            continue

        if "FREE ENERGIE OF THE ION-ELECTRON SYSTEM" in line:
            # 若上一步已经建过（因为力块先出现）且已经有能量，则开新的一步
            if cur is not None and (cur.toten is not None
                                    or cur.energy_sigma0 is not None):
                cur = _ensure(len(steps) + 1)
                in_force_block = False
            elif cur is None:
                cur = _ensure(len(steps) + 1)
            continue

        if cur is None:
            continue

        if "free  energy   TOTEN" in line or "free energy    TOTEN" in line:
            m = re.search(r"TOTEN\s*=\s*([-\d.Ee+]+)", line)
            if m:
                try:
                    cur.toten = float(m.group(1))
                except ValueError:
                    pass
            continue
        if "energy  without entropy" in line:
            m = re.search(r"energy  without entropy\s*=\s*([-\d.Ee+]+)", line)
            if m:
                try:
                    cur.energy_wo_entropy = float(m.group(1))
                except ValueError:
                    pass
            m2 = re.search(r"energy\(sigma->0\)\s*=\s*([-\d.Ee+]+)", line)
            if m2:
                try:
                    cur.energy_sigma0 = float(m2.group(1))
                except ValueError:
                    pass
            continue

        if "E-fermi" in line and cur.fermi is None:
            m = re.search(r"E-fermi\s*:\s*([-\d.Ee+]+)", line)
            if m:
                try:
                    cur.fermi = float(m.group(1))
                except ValueError:
                    pass
            continue

        if "reached required accuracy" in line:
            cur.reached_required = True
            continue

        if in_force_block:
            if "total drift" in line:
                toks = line.replace(":", " ").split()
                try:
                    cur.total_drift = tuple(float(t) for t in toks[-3:])
                except ValueError:
                    pass
                in_force_block = False
                continue
            if set(s) <= set("-") and s:
                continue
            if not s:
                in_force_block = False
                continue
            toks = s.split()
            if len(toks) >= 6:
                try:
                    cur.forces.append((toks[0], float(toks[-3]),
                                       float(toks[-2]), float(toks[-1])))
                except ValueError:
                    in_force_block = False
            continue

    # 收尾：算力的统计量
    for st in steps:
        if st.forces:
            mags = [math.sqrt(f[1] ** 2 + f[2] ** 2 + f[3] ** 2)
                    for f in st.forces]
            st.max_force = max(mags)
            st.rms_force = math.sqrt(sum(m * m for m in mags) / len(mags))
    return steps


def outcar_cell_volumes(path: str) -> "list[tuple[float, list]]":
    """取每个离子步的 `volume of cell` 与晶格（Å）。用于看 ISIF=3 有没有生效。"""
    out = []
    vol = None
    cell = []
    for _lineno, line in iter_lines(path):
        if "volume of cell" in line:
            m = re.search(r"volume of cell\s*:\s*([\d.]+)", line)
            if m:
                if vol is not None:
                    out.append((vol, cell))
                try:
                    vol = float(m.group(1))
                except ValueError:
                    vol = None
                cell = []
            continue
        if "direct lattice vectors" in line:
            cell = []
            continue
        m = re.match(r"\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+length", line)
        if m and vol is not None and len(cell) < 3:
            try:
                cell.append([float(m.group(1)), float(m.group(2)),
                             float(m.group(3))])
            except ValueError:
                pass
    if vol is not None:
        out.append((vol, cell))
    return out


def outcar_reciprocal_lengths(path: str):
    """取 OUTCAR 里 `reciprocal lattice vectors` 的长度（用于 k 点密度换算）。"""
    lengths = []
    seen = 0
    for _lineno, line in iter_lines(path):
        if "reciprocal lattice vectors" in line:
            seen += 1
            continue
        if seen == 1:
            m = re.search(r"length\s*=\s*([\d.]+)", line)
            if m:
                try:
                    lengths.append(float(m.group(1)))
                except ValueError:
                    pass
                if len(lengths) == 3:
                    return lengths
    return lengths


# ---------------------------------------------------------------------------
# 11. OSZICAR / vasprun.xml
# ---------------------------------------------------------------------------
def oszicar_last_energy(path: str):
    """从 `OSZICAR` 取最后一个电子步的能量（`E0` 列）与离子步数。

    `OSZICAR` 比 `OUTCAR` 小得多（本项目里最大 800 KB vs 15 MB），
    所以**先看 `OSZICAR` 判断"跑没跑完、几步收敛"比读 `OUTCAR` 快得多**。
    """
    last_E0 = None
    n_ionic = 0
    for _lineno, line in iter_lines(path):
        if re.match(r"\s*\d+\s+F=", line) or re.match(r"\s*\d+\s+T=", line):
            n_ionic += 1
            toks = line.split()
            # 形如：   1 F= -.12345678E+02 E0= -.12345678E+02  d E =-.123E-03
            for i, t in enumerate(toks):
                if t.startswith("E0=") and i + 1 < len(toks):
                    try:
                        last_E0 = float(toks[i + 1])
                    except ValueError:
                        pass
    return last_E0, n_ionic


def vasprun_meta(path: str, max_bytes: int = 4 << 20) -> dict:
    """从 `vasprun.xml` 头部取元信息（**只读前若干字节**）。

    `vasprun.xml` 是**结构化 XML**，理论上比文本输出健壮得多。
    但真实文件可以到几百 MB（本项目里 `ni-co/vasprun.xml` 有 17 MB，
    生产算例常到 GB），所以这里只读头部。

    返回：program / version / subversion / platform / date / time / n_atom /
    n_elect / encut / ispin / ismear / sigma / 等。
    """
    meta = {}
    with open_maybe_gz(path, "rb") as fh:
        chunk = fh.read(max_bytes).decode("utf-8", errors="replace")
    for key in ("program", "version", "subversion", "platform", "date", "time"):
        m = re.search(r'<i\s+name="%s"[^>]*>([^<]*)</i>' % key, chunk)
        if m:
            meta[key] = m.group(1).strip()
    for key in ("ENCUT", "ISPIN", "ISMEAR", "SIGMA", "EDIFF", "EDIFFG",
                "NELM", "NSW", "IBRION", "ISIF", "ISYM", "PREC", "LREAL",
                "GGA", "IVDW", "LDAU", "NELECT"):
        m = re.search(r'<i\s+(?:type="[^"]*"\s+)?name="%s"[^>]*>([^<]*)</i>'
                      % key, chunk)
        if m:
            meta[key] = m.group(1).strip()
    for key in ("NIONS", "NBANDS", "NELECT", "NEDOS", "NKPTS"):
        m = re.search(r'<i\s+name="%s"[^>]*>\s*(\d+)' % key, chunk)
        if m:
            meta[key] = m.group(1)
    m = re.search(r'<atominfo>.*?<atoms>\s*<i>\s*(\d+)', chunk, re.S)
    if m:
        meta.setdefault("NIONS", m.group(1))
    return meta
