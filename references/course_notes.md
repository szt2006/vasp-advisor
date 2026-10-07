# 课程速查（C 层）· 研之成理第四届固体与表面计算中级班（表面方向-催化专题，刘锦程）

> **这是摘要层**：只放实战精华（常用数值、常踩的坑、常用命令、讲义↔主题映射），供 grep 直击。
> **深度内容在 `course_learned.md`**（分主题，含冲突裁定与差异表）。
> **有冲突时以 `course_learned.md` 与 `references/official/` 为准** —— 本层不承担裁定职责。
> 引用格式：`L1 P28` = 讲义第 28 页；`D2-P14` = 答疑第 14 段。页号上界 L1≤82 / L2≤157 / L3≤196 / L4≤56；段号上界 D1≤60 / D2≤82 / D3≤48 / D4≤67。
> 标记：`[讲义]` `[答疑]` 为课程原话（经精读报告转录）；`[算例]` 为精读报告对 `things to study/` 真实文件的核对结果；`[官方]` 为本轮读过 `references/official/pages/<X>.md` 后的事实；`[官方·未抓取]` 为「有官方说法但该页不在本地官方层、无法逐字复核」（如官方 DOSCAR 页）；`[待核对]` 不得当断言。
> 课程本身有免责声明：「不能保证所有授课内容的正确性和准确性」`[讲义] L1 P3`。

## 1. 讲义 ↔ 主题映射（想知道 X 去哪一页）

| 想查什么 | 去哪一页 |
|---|---|
| 研究思路、模型设计为什么重要 | `[讲义] L1 P4–P7` |
| 表面基元反应 / AIMD / 自由能校正 / TOF 图 | `[讲义] L1 P8–P10` |
| VASP 输入输出文件全景 | `[讲义] L1 P13` |
| POSCAR 格式 / Selective Dynamics 语法 | `[讲义] L1 P14–P16` |
| vaspkit 402 / 403 固定原子 | `[讲义] L1 P17–P19` |
| KPOINTS 生成、k 点密度（R 值与 ka 表） | `[讲义] L1 P20–P22` |
| 赝势后缀 / POTCAR 生成顺序 | `[讲义] L1 P23–P27` |
| INCAR 电子步 / 离子步建议（课程口径总表） | `[讲义] L1 P28–P29` |
| 收敛判据与能量提取命令 | `[讲义] L1 P30` |
| 结构优化 INCAR 模板 | `[讲义] L1 P31` |
| OPTCELL 固定面内（保护真空） | `[讲义] L1 P32–P33` |
| 泛函 / HSE06 设置 | `[讲义] L1 P34–P35` |
| vdW：DFT-D3 / vdW-DF 变体 / TS / MBD | `[讲义] L1 P36–P39` |
| 泛函对吸附能的影响（PBE/RPBE/BEEF/RPA） | `[讲义] L1 P40–P41` |
| DFT+U 原理与 INCAR | `[讲义] L1 P42–P43` |
| 磁性分类 / MAGMOM / Fe₂O₃ AFM 实例 | `[讲义] L1 P44–P47` |
| 提速技巧 / 编译与插件 | `[讲义] L1 P48–P50` |
| 复杂表面建模总览 / 切面四原则 | `[讲义] L1 P51–P57` |
| 赝氢饱和 / GaN(0001) 建模 | `[讲义] L1 P58–P60` |
| Wood 标记 / Redefine Lattice / 手性 | `[讲义] L1 P61–P63` |
| √3×√3R30° / 魔角石墨烯 / magicAngle.py | `[讲义] L1 P64–P69` |
| g-C₃N₄/TiO₂ 异质结建模六步 | `[讲义] L1 P70–P76` |
| MS 论文出图 / Cu-H₂O 界面 | `[讲义] L1 P77–P80` |
| 分子轨道→能带、紧束缚、布里渊区 | `[讲义] L2 P3–P19` |
| DOS / PDOS 定义与判据 | `[讲义] L2 P20–P25` |
| 电子结构分析七个案例 | `[讲义] L2 P26–P31` |
| NBANDS / NEDOS / EMAX / EMIN | `[讲义] L2 P32–P34` |
| DOS 计算流程与 INCAR | `[讲义] L2 P35–P36` |
| p4vasp / vaspkit 提 DOS 与费米能级对齐 | `[讲义] L2 P37–P44` |
| DOS 注意事项 (1)–(7) | `[讲义] L2 P45–P49` |
| LORBIT 的 total charge 警告 / 原子电荷方法 | `[讲义] L2 P50` |
| 轨道相互作用四模型 / 表面特殊作用 / 吸附能垒 | `[讲义] L2 P51–P57` |
| Ni(100)-CO 全流程与结论 | `[讲义] L2 P58–P71` |
| N₂/Fe₃-Al₂O₃ 片段 PDOS 与定量结论 | `[讲义] L2 P72–P77` |
| d 带中心理论与调控三思路 | `[讲义] L2 P80–P88` |
| d 带中心计算流程 / vaspkit 503 / 脚本法 | `[讲义] L2 P89–P93` |
| CHGCAR 格式 / Bader / 差分电荷两定义 | `[讲义] L2 P97–P104` |
| 实空间波函数 / EIGENVAL | `[讲义] L2 P105–P106` |
| partial charge 概念 / LPARD 关键词 / 三种用法 | `[讲义] L2 P107–P124` |
| STM 模拟 | `[讲义] L2 P125–P129` |
| 静电势 / 功函数 / 异质结电子流向 | `[讲义] L2 P130–P145` |
| 分子范德华表面静电势 | `[讲义] L2 P146–P149` |
| ELF | `[讲义] L2 P150–P156` |
| 三种吸附 / 吸附能定义 / 吸附位点 / 覆盖度 | `[讲义] L3 P3–P19` |
| 频率原理（Hessian / 3N−6 / ZPE / NFREE） | `[讲义] L3 P20–P28` |
| 频率实操（vaspkit 403 / INCAR / 虚频判读） | `[讲义] L3 P29–P37` |
| 配分函数 / 振动平动转动电子四项 / 低频截断 | `[讲义] L3 P38–P62` |
| vaspkit 501/502、气体分子自由能校正 | `[讲义] L3 P63–P73` |
| Langmuir / 覆盖度 / CO 毒化 | `[讲义] L3 P77–P90` |
| 表面能 γ(T,p) 与 RuO₂(110) 算例 | `[讲义] L3 P91–P103` |
| 多自变量相图 / Ostwald / 方法学总结 | `[讲义] L3 P104–P112` |
| 过渡态定义 / 方法分类 / NEB 原理 / CI-NEB | `[讲义] L3 P113–P124` |
| CI-NEB 完整 12 步 | `[讲义] L3 P125–P136` |
| DIMER 原理 / MODECAR / DIMCAR 解读 / 收敛 | `[讲义] L3 P137–P153` |
| 过渡态五类常见问题 | `[讲义] L3 P154–P158` |
| NEB+Dimer 组合 / neb2dim.pl | `[讲义] L3 P159–P167` |
| 线性插点缺陷 / IDPP | `[讲义] L3 P168–P173` |
| 反应动力学（Arrhenius / TST / 隧穿） | `[讲义] L3 P174–P183` |
| 三大机理 LH / ER / MvK | `[讲义] L3 P184–P195` |
| 电催化台阶图 / 过电势 / OER 四步 ΔG | `[讲义] L4 P3–P11` |
| ORR 与 OER 的关系 / pH 修正 | `[讲义] L4 P14–P17` |
| NRR / CO₂RR 补充 | `[讲义] L4 P21–P24` |
| 标度关系 / 火山曲线（ORR/OER/NRR/CO₂RR/HER） | `[讲义] L4 P25–P31` |
| 传统模型缺陷 / 双电层 / 显式 vs 隐式溶剂 | `[讲义] L4 P32–P47` |
| VASPsol 来历、编译、参数、用法 | `[讲义] L4 P49、P54` |
| 溶解自由能与标准态校正（+1.89 kcal/mol） | `[讲义] L4 P52` |

## 2. 最常用数值（一行一条）

- 真空层：二维/表面算例实际 ≈15 Å（Ag/Au/MoS₂ 系）；答疑口径「一般 10–15 Å 就够了」`[待核对] D4-P10`。
- 建真空层的方法：`build – crystal – rebuild crystal` 把 c 增大 15 Å`[讲义] L1 P76`；OER 算例 c = 15 Å`[算例] learn_L4 K42`。
- k 点（vaspkit R 值）：一般 0.04，精确 0.03/0.02`[讲义] L1 P20`；算例实际 0.040（多数）/0.050（MoS₂-WS₂、OER）。
- k 点密度（ka 刻度）：d 区金属 ≈30 Å、普通金属 ≈25 Å、半导体 ≈20 Å、绝缘体 ≈15 Å`[讲义] L1 P21`。
- 两套刻度换算：`ka = 1/R`，故 R=0.04 ↔ ka=25 Å`[待核对] learn_L1 §3.2`。
- DOS 计算的 k 点要更密，但讲义无数值判据`[讲义] L2 P46 / 待核对`。
- ENCUT：= POTCAR 的 ENMAX；晶胞优化/弹性 > 1.3×ENMAX`[讲义] L1 P28`；算例取值 400/500/520。
- 「1.3×ENMAX」的官方对应是**已弃用**的 `PREC=High` 档`[官方] references/official/pages/PREC.md`。
- 展宽：金属 `ISMEAR=1`+`SIGMA=0.2`；非金属 `0`+`0.05`；分子 `0`+`0.01``[讲义] L1 P28`。
- DOS 首选 `ISMEAR=-5`；k 点数 ≤3 时会报错，要换 0 或 1`[讲义] L2 P46、P47`。
- 「结构优化不能用 -5」「-5 不读 SIGMA」在本地官方 ISMEAR/SIGMA 页里找不到对应表述`[待核对]`。
- EDIFF：结构优化/MD 讲义写 1E-5，但模板与 4/4 算例都写 **1E-6**；官方推荐 1E-6`[官方] EDIFF.md`。
- EDIFF：**频率与过渡态一律 1E-7**`[讲义] L3 P26、P129`；官方「有限差分甚至可能需要 1E-7」`[官方] EDIFF.md`。
- EDIFFG：晶胞优化 −0.01；结构优化 −0.02；过渡态模板 −0.03（难收敛 −0.05），但真实 TS 算例多为 −0.01`[讲义] L1 P29、L3 P129 / 算例`。
- EDIFFG 默认 = EDIFF×10（正值 = 能量判据）——**忘写就不是按力收敛**`[官方] references/official/pages/EDIFFG.md`。
- POTIM：优化 0.5（默认）/ 初始结构不好 0.2（算例一律 0.2）；频率 0.015（IBRION=5/6 默认）`[讲义] L1 P29、L3 P30`。
- POTIM=0 配 IBRION=3 是 **VTST 生效的标志**（必须用编译了 VTST 的 VASP）`[讲义] L3 P129、P148`。
- NSW：讲义写 500，模板与算例一律 300`[讲义] L1 P29 / 算例`。
- ISIF：晶胞优化 3；表面/结构优化 2；MD 0；E-V 曲线 4`[讲义] L1 P29`。
- NFREE：频率 2（中心差分）或 4；官方「强烈建议避免 NFREE=1」`[官方] references/official/pages/NFREE.md`。
- 频率实际离子步数 = 3 × 放开原子数 × NFREE + 1（NFREE=2 时即 6×放开原子数+1）`[讲义] L3 P31 + 算例核对`。
- LREAL：官方「含 **>约 30 个原子**才用实空间投影，且只用 `Auto`」`[官方] LREAL.md`；小体系用 `.FALSE.`。
- ISYM：官方默认 2；官方给 `ISYM=0` 的理由是 **MD（IBRION=0）**，不是「表面计算」`[官方] ISYM.md`。
- ADDGRID：官方「**不要在所有计算里默认开启**」，需仔细测试；常能降低力的噪声`[官方] ADDGRID.md`。
- NCORE：官方推荐 ≈√可用核数，~100 原子用 4、>400 原子用 12–16，**必须实测**；不要与 NPAR 同写`[官方] NCORE.md`。
- LMAXMIX：DFT+U 必设，d 电子 **4**、f 元素 **6**（默认 2）`[讲义] L1 P43 / [官方] LMAXMIX.md`。
- DFT+U 的 U 值两套写法不可混比：`Ueff = U − J`；不同 U/J 的**总能不可比**`[官方] LDAUU.md`。
- MAGMOM 只在「没读 CHGCAR/WAVECAR」或「读了非自旋极化 CHGCAR」时才被采用`[讲义] L1 P45`；初始磁矩可设大（如 5.0）。
- 赝氢：加在**原有化学键中点**、**计算中固定**`[讲义] L1 P58`；单层 MoS₂ 切 100 面不需要`[答疑] D1-P58`。
- 固定层数：固定下 2–3 层，可弛豫原子数 ≥ 固定层数`[讲义] L1 P15`；Ni(100) 取 6 个原子层`[讲义] L2 P59`。
- NEDOS：默认 301，建议 1000（金属体系模板用 2000）`[讲义] L2 P33、P62`。
- 差分电荷片段单点必须收敛，且参数与吸附态一致、结构直接截取不再优化`[讲义] L2 P103 + [答疑] D2-P24`。
- partial charge：简并轨道必须合并输出（如 287+288 = VBM、289+290 = CBM）`[讲义] L2 P124`。
- 跨费米能级的 partial charge 窗口写作：`NBMOD=-3` + `EINT=-2 2`（两个值都加到 E_f 上）`[官方] NBMOD.md`。
- 功函数：`Φ = Evac − EF`；用 `LVHAR=.TRUE.`；**两个都设 T 时 LVHAR 优先**，拿到的是纯静电势`[讲义] L2 P135 / [官方] LVHAR.md`。
- Au(111)-p(2×2) 例：Evac=6.673、E_F=1.6561 → Φ=5.02 eV；O/Au(111)：Φ=5.6097 eV`[讲义] L2 P139、P142`。
- ELF：`LELF=.TRUE.` + `PREC=Accurate` + ⚠️ **必须显式写 `NPAR=1`**
  （`[官方]` `references/official/pages/LELF.md:9` 原文：
  `If LELF is set, NPAR=1 has to be set explicitely`）。
  ⚠️ **讲义说「去掉 `NPAR`、`NCORE`」—— 那与官方方向相反，不要照抄。**
  「**去掉**」和「**显式写 `NPAR=1`**」听起来像一回事，**其实只在少核小体系下等价**：
  - 「去掉 `NPAR`」⇒ `NPAR` 落到官方默认 = **可用 rank 数**（即 `NCORE=1`）；
  - 官方要的 `NPAR=1` ⇒ **全部 rank 协作处理一个 band**。
  在 **16 rank 以上**两者**不等价**：前者每个 rank 独占一个 band、独自完成整块 FFT，
  大体系下内存/栈会爆（`[官方]` `references/official/pages/NCORE.md:19`）。
  详见 `references/decide.md`（已按官方裁定）与该行的实测记录。
- 频率：过渡态**虚频一般 > ~100 cm⁻¹**，太小说明 TS 找错`[讲义] L3 P33 / 待核对`；`f/i` 即虚频。
- 频率：极小点 0 个虚频；过渡态**恰好 1 个**；气态分子最小的 6 个频率出虚频可无视`[讲义] L3 P33、P36、P157`。
- ZPE = ½Σhν；只对真实振动模式（3N−6 或 3N−5）求和，虚频不计入`[讲义] L3 P52、P71 / 待核对`。
- 低频截断：吸附分子自由能校正把 **< 50 cm⁻¹ 的频率按 50 cm⁻¹** 计（另处说 50 或 60）`[讲义] L3 P55、P64`。
- 吸附熵：Nørskov 估算约 **−0.002 eV/K**`[讲义] L3 P81`。
- 覆盖度对吸附能的敏感区间 **−0.7 ~ −0.5 eV**；多组分吸附能差 ±0.1 eV 即可让覆盖度反转`[讲义] L3 P84、P86`。
- CI-NEB：插点 **3–4 个足够**（含初末态 3–5 个点）；「越多越好」是错的`[讲义] L3 P124`。
- CI-NEB 插点数经验式 ≈ `dist.pl` 返回值 / 0.8；`dist.pl` 返回值 < 5 Å 再继续`[讲义] L3 P125、P126`。
- CI-NEB：`IMAGES` = 中间像数，总点数 = IMAGES+2；**核数必须整除插点数量**`[讲义] L3 P131、P132`。
- CI-NEB 收敛判据：**所有插点的最大原子受力 < abs(EDIFFG)**`[讲义] L3 P133`；`SPRING=-5` 是官方默认且推荐`[官方] SPRING.md`。
- DIMER：两点间距 2ΔR ≈ **0.01 Å**；收敛 = 力 < abs(EDIFFG) **且曲率 C < 0**`[讲义] L3 P137、P140`。
- DIMCAR 六列 = Step/Force/Torque/Energy/Curvature/Angle；**Energy 不能当过渡态能量**，取 OSZICAR 最后一个 E0`[讲义] L3 P149、P151`。
- IDPP 与线性插点的差距实例：同一个 image 的 C–H 键 0.59 Å（线性）vs 1.09 Å（IDPP）`[讲义] L3 P169、P171`。
- 电催化：OER 总自由能变化 **4.92 eV**、理想每步 1.23 eV；`η = U − Ueq``[讲义] L4 P10、P5`。
- 电催化：OER 的 U 取**能量上升最高**的一步；ORR 取**下降最小**的一步`[讲义] L4 P6、P14`；决速步 = `Max(ΔG1..ΔG4)`，过电势 = 决速步吸热 − 1.23`[讲义] L4 P11`。
- CHE：`G(H₂)/2 = G(H⁺)+G(e⁻)`；液态水用 **0.035 bar 饱和蒸汽**能量`[讲义] L4 P9`。
- 电催化：`G(O₂)` 必须由 `2G(H₂O) − 2G(H₂) − G(O₂) = −4.92 eV` 反推（O₂ 的 DFT 电子能不准）`[讲义] L4 P9 + [答疑] D4-P20`。
- pH = 14 时 OER 的 ΔG = **−1.605 eV**、标准电极电势 0.401 V；pH=0 为 1.23 V（表里写 1.229 V）`[讲义] L4 P16、P17`。
- 火山顶点：ORR ≈ 0.9 V、OER ≈ 1.5 V；限制因素「*OH 吸附过强 / *OOH 吸附过弱」`[讲义] L4 P27`。
- 标度关系：`ΔG_OOH = ΔG_OH + 3.2`、`ΔG_O = 2ΔG_OH`（与 P29 的 η=0 顶点不自洽，见差异表）`[讲义] L4 P25 / 算例 learn_L4 C3`。
- VASPsol：`LSOL=T` + `NSW=0`（关离子步）；换溶剂必须**显式写 `EB_K`**，默认是水 78.4`[讲义] L4 P54 + [算例] learn_L4 K37`。
- VASPsol 溶剂化对能量影响量级：H₂O 分子 ΔE = −0.3128 eV（−7.21 kcal/mol）`[算例] learn_L4 K26`。
- SHE 相对真空绝对电位：讲义用 **4.44 V**，配套 `VASPsol原理.pdf` 拟合值 **4.6 V** —— 报 vs SHE 前必须声明用哪个`[讲义] L4 P41 / 算例 learn_L4 C5`。
- 溶解自由能标准态校正 **+1.89 kcal/mol = 0.08196 eV**（出处与适用范围待核对）`[讲义] L4 P52 / 待核对`。

## 3. 最常用命令（一行一条）

- 收敛检查：`grep reached OUTCAR`（命中 `aborting loop because EDIFF is reached` = SCF 收敛；`reached required accuracy - stopping structural energy minimisation` = 离子步收敛）`[讲义] L1 P30`。
- 取能量：`tail -1 OSZICAR`（最后一个 `E0`）；讲师做自由能图用 `energy(sigma->0)` 而非 `free energy TOTEN``[讲义] L1 P30 / 算例 learn_L4 K70`。
- 取费米能级：`grep E-fermi OUTCAR``[讲义] L2 P40`。
- 查 NBANDS：`grep NBANDS OUTCAR`；查格点：`grep NGXF OUTCAR`；查总电子数：`grep NELECT OUTCAR``[讲义] L2 P32、P98 / [答疑] D1-P12`。
- 自旋密度拆分：`chgsplit.pl CHGCAR` → `CHGCAR_mag` / `CHGCAR_tot``[讲义] L2 P97`。
- Bader：`chgsum.pl AECCAR0 AECCAR2` 然后 `bader CHGCAR -ref CHGCAR_sum`（需 `LAECHG=.TRUE.`；讲义排成了 en dash，实际用 ASCII `-`）`[讲义] L2 P100 / 算例 learn_L2 §4.4-F7`。
- 查虚频：`grep cm OUTCAR`（看 `f/i` 标记）`[讲义] L3 P33`。
- 查有限位移进度：`grep -3 Finite OUTCAR`（输出 `Degree of freedom` / `Displacement` / `Total`）`[讲义] L3 P31`。
- NEB 前置检查：`dist.pl ini/CONTCAR fin/CONTCAR`（< 5 Å 可继续）`[讲义] L3 P125`。
- NEB 插点：`nebmake.pl ../is/CONTCAR ../fs/CONTCAR 1`（成功提示 `OK, ALL SETUP HERE`，生成 `00/01/02`）`[讲义] L3 P126`。
- NEB 后处理：`nebresults.pl`（跑 nebbarrier/nebspline/nebef/nebmovie/nebjmovie/nebconverge，并把 OUTCAR 打包 `.gz`）`[讲义] L3 P134–P136`。
- NEB 能量跟踪：`nebef.pl`（后三列 = 最大原子受力 / 能量 / 相对初态能量）`[讲义] L3 P132`。
- Dimer 方向文件：`modemake.pl ../is/CONTCAR ../fs/CONTCAR` → `MODECAR``[讲义] L3 P144`。
- Dimer 收敛三条：`grep converged OUTCAR`、`grep RMS OUTCAR`、`tail -1 OSZICAR``[讲义] L3 P153`。
- Dimer 动画：`dimmode.pl CENTCAR NEWMODECAR 32 0.5` → `dimmode.xyz`（要求 CENTCAR 首行是元素组成）`[讲义] L3 P152`。
- IDPP 插点：`python3 idpp.py POSCARis POSCARfs 4` → `00 ~ 05``[讲义] L3 P173`。
- 自由能校正：`vaspkit 501`（吸附物）；`vaspkit 502`（气体分子，写法如 `vaspkit-502-298.15-0.035-1`）`[讲义] L3 P63 / L4 P9`。
- DOS/PDOS 提取：`vaspkit 111`（总 DOS）/`113`（按元素）/`115`（按轨道）`[讲义] L2 P41–P44`。
- d 带中心：`vaspkit 503`（输出 `D_BAND_CENTER`）或 `115` + 脚本（给能量上限）`[讲义] L2 P92、P93`。
- 差分电荷：`vaspkit 314`（依次给三个 CHGCAR）→ `CHGDIFF.vasp`；改名 CHGCAR 后 `vaspkit 316` 得 `CHGPAVG.dat``[讲义] L2 P103、P104`。
- 功函数：`LVHAR=.TRUE.` + vaspkit 对 LOCPOT 做 z 积分得 `POTPAVG.dat``[讲义] L2 P136–P137`。
- 固定原子：`vaspkit 402`（按层）或 `403`（按 z 阈值，如 `0 0.48`）`[讲义] L1 P17–P19 / L3 P29`。
- 结构文件互转：VESTA、`vaspkit 105`（CIF↔POSCAR）`[讲义] L1 P14`。

## 4. 症状 → 处方（原文可 grep）

- `VERY BAD NEWS! internal error in subroutine IBZKPT: Tetrahedron method fails for NKPT<4.` → k 点 < 4 用了 `ISMEAR=-5`；改 `ISMEAR=0/1` 或加密 k 点`[讲义] L2 P46`。
- DOS 图毛刺多 → 增大 k 点数，或改用 `ISMEAR=0``[讲义] L2 P33`。
- DOS/PDOS 积分对不上电子数 → `ISPIN=2` 时积分在第 4、5 列（不是第 3 列）；PDOS 之和本就小于总 DOS`[官方·未抓取] 官方 DOSCAR 页（经 learn_L2 §4.2-D1）/ [讲义] L2 P48`。
- 差分电荷图很丑 → 片段单点没收敛；三个片段参数必须与吸附态一致、结构直接截取`[答疑] D2-P24 / [讲义] L2 P103`。
- partial charge 图不对称 → 简并轨道要合并输出（查 EIGENVAL 的占据数）`[讲义] L2 P124`。
- 力不收敛 / TS 不收敛 → 先上 `EDIFF=1E-7`，再考虑 `PREC=Accurate`；仍不行试 `IOPT=7` 或放宽 EDIFFG`[讲义] L3 P129、P156 / [官方] PREC.md`。
- CI-NEB 一开始力 > 10 eV/Å → 初始结构不合理；用 `idpp.py` 非线性插点或人工改 POSCAR`[讲义] L3 P155`。
- `nebmake.pl` 出来的结构很乱 → 初末态**原子顺序**没一一对应`[讲义] L3 P158`。
- TS 收敛了但没有虚频 / 有多个虚频 → 力精度不够（`EDIFF=1E-7`）；多个虚频可换 Dimer`[讲义] L3 P157`。
- CINEB 中间点能量比初末态低 → IS/FS 不是真极小点，用更严精度重算初末态`[讲义] L3 P154`。
- DIMCAR 的 Torque 不下降 → 更小的 EDIFF、`PREC=Accurate`，或提高 `DdR``[讲义] L3 P151`。
- `neb2dim.pl` 报错 → 检查 NEB 的 CONTCAR；手动删掉末尾速度信息；或用 `modemake` 自己生成`[答疑] D4-P49、D4-P50`。
- 优化「很快收敛」但结构没动 → 可能忘写 `EDIFFG`（默认走能量判据）`[官方] EDIFFG.md`。
- `OPTCELL` 看不出有没有生效 → OUTCAR 不回显它；比对 POSCAR 与 CONTCAR 的晶格矢量`[算例] learn_L1 §3.15`。
- `OPTCELL(100; 000; 000)` 这类带空格/分号的写法出问题 → 正确写法是**三行、无空格无分号**`[答疑] D4-P2`。
- 赝氢钝化后算不出表面能 → 只能算上下表面的平均表面能`[答疑] D1-P56`。
- 台阶图最后一步不等于 4.92 eV → 手算取整累积误差；用脚本校验总包反应能量`[算例] learn_L4 C11`。
- 功函数曲线不是静电势 → 可能两个都开了 `LVHAR`/`LVTOT`（LVHAR 优先，拿到的是纯静电势）`[官方] LVHAR.md`。

## 5. 常踩的坑（一行一条）

- **优化任务的 DOSCAR 不能用**（`NSW>1` 时 DOS 是各离子步的平均）；自查：数 OUTCAR 里 `E-fermi` 出现几次`[官方·未抓取] 官方 DOSCAR 页 / [算例] learn_L2 §3.9-A3`。
- 结构优化用 `ISMEAR=-5` 会让**力**有误差（课程口径）`[讲义] L2 P46`。
- 跨 U/J（或 U−J）比总能**无意义**；引用 U 值必须说明是 Ueff 还是 U、J 分开写`[官方] LDAUU.md / [算例] learn_L1 §3.8`。
- DFT+U + `ICHARG=11` 的结果未必等于自洽；DFT+U 算能带必须 `LMAXMIX=4`(d)/6(f)`[官方] LMAXMIX.md`。
- `LORBIT` 输出的 `total charge` 不能定量（讲义自己说「一般无视就行了」）`[讲义] L2 P50`。
- d 带中心**必须同时报积分窗口**，否则不可复现（同一 PDOS 换上限差 0.027 eV）`[算例] learn_L2 §3.9-A14`。
- `EINT` 不是实验偏压，两者需自行标定`[讲义] L2 P126`。
- 不能用 `DOSCAR`/`EIGENVAL` 头的体系名判断体系（是 `SYSTEM` 残留名）`[算例] learn_L2 §3.9-A11`。
- 文献里没说明 U/J 的那个数**往往是磁矩**，要去 OUTCAR 最后读`[答疑] D1-P30`。
- 泛函/格点精度/溶剂模型/vdW 校正只要有一项不同，**频率就不能与优化结果配对使用**`[讲义] L3 P26`。
- 「前 3N−6 个频率」不是通用规则（虚频排在最后）；逐行看 `f/i``[算例] learn_L3 §4.1-C-6`。
- ZPE 不要机械地对全部 meV 求和（含虚频会算错）`[讲义] L3 P61 vs P71 / 待核对`。
- 只对**能量最高的 image** 做频率验证即可`[答疑] D3-P33`。
- `OUTCAR` 里 `NFREE` 的说明文字是给 IBRION=2 的，会误导`[算例] learn_L3 §3.8.2-X18`。
- 不要把 CINEB 的参数留在 Dimer 的 INCAR 里（讲义 P166 那段本身就是排版坑）`[讲义] L3 P166 / 算例 learn_L3 C-10`。
- 讲义把 `.TRUE.` 拼成 `.TURE.`（两处）；不要照抄`[算例] learn_L1 §4-C10/C11`。
- 讲义里孤立的 s/p 与「键/轨道」连用，多半是 σ/π 被抽取退化了`[算例] learn_L2 §4.3-E1`。
- `OUTCAR` 回显 KPOINTS 注释行会**截断到 40 字符**（别据此判断原始文件写了什么）`[算例] learn_L1 §3.1`。
- 加真空层的目的是**得到真空能级**，不是为了避免与下表面作用`[答疑] D1-P48`。
- 赝氢下表面只能算平均表面能；金属表面不需要 H 钝化；氧化物 O 终端一般不需要钝化`[答疑] D1-P56、D2-P26、D4-P3`。
- 单原子 / 氧化物上的 d 带中心规律**没有纯金属好**`[答疑] D2-P15/P18/P20`。
- `N₂` 解离 / `O₂ + * → *O₂` 这类「非电化学基元步骤」不含 `eU`、**不随 U 变化**`[答疑] D4-P45/P46、D4-P15/P16`。
- `O₂` 的 DFT 电子能不准确 → 用 4.92 eV 反推 G(O₂)；液态水要用 0.035 bar 蒸汽`[讲义] L4 P9`。
- IOPT 只影响「能不能找到过渡态」，找到后用哪个 IOPT 都不影响能量`[答疑] D4-P41/P42`。

## 6. 课程口径 vs 官方口径（速判，详见 `course_learned.md` §10）

- 讲义说 `EDIFF=1E-5` 够用 → 官方推荐 **1E-6**；模板与算例站在 1E-6`[官方] EDIFF.md`。
- 讲义说「表面计算 `LREAL=Auto`」→ 官方判据是**原子数（>约 30）**，且只用 Auto`[官方] LREAL.md`。
- 讲义说「表面计算 `ISYM=0`」→ 官方默认 2，给 0 的理由是 **MD**`[官方] ISYM.md`。
- 讲义说 `NCORE=` 每节点核数/2 → 官方推荐 ≈√可用核数 / 按原子数，且必须实测`[官方] NCORE.md`。
- 讲义说 ELF「去掉 NPAR、NCORE」→ 官方要求**显式写 `NPAR=1`**（方向**相反**，见上面 §8 的详解）`[官方] LELF.md`。
- 讲义用 `PREC=High`（ELF）→ 官方把 Low/Medium/High 标为**已弃用**，用 Normal/Accurate`[官方] PREC.md`。
- 讲义全程用 `IBRION=5` 算频率 → 官方标 5 为**已弃用（无对称性）**，建议用 6（带对称性）`[官方] IBRION.md`。
- 讲义 P36 的 `EMAX=-20 / EMIN=15` 看似写反 → 官方 EMIN 页明确「不确定区间时把 EMIN 设得比 EMAX 大」`[官方] EMIN.md`。
- 讲义说 `NBANDS` 自旋默认 `0.6*NELECT+NMAG` → 官方公式含 `int(3/5·NELECT)`，**没有 NMAG**`[官方] NBANDS.md`。
- 讲义说 `LORBIT=11` 是「区分磁量子数」→ 官方称 **lm-decomposed**；且 VASP<6 + `LORBIT≥11` + `ISYM=2` 有 known issues`[官方] LORBIT.md`。
- 讲义只讲 `NBMOD=-3` 配单值 `EINT` → 官方 `-3` **也接受两个值**（加到 E_f 上）`[官方] NBMOD.md`。
- `OPTCELL` / VTST 的 `ICHAIN,LCLIMB,IOPT` / VASPsol 的 `LSOL,EB_K,SIGMA_K,NC_K,TAU,LRHOB` **在本地官方层没有对应页面**（检索范围：`references/official/pages/` 的 627 个文件名）→ 引用时不要挂 `[官方]`。
- 与官方一致、可放心用的：弛豫任务的 DOSCAR 不可用；频率/过渡态 `EDIFF=1E-7`；`POTIM=0.015`（IBRION=5/6）；`SPRING=-5`；四面体法要 Γ 中心网格；`IVDW` 的 11/12/20/202 语义；`EDIFFG` 负值判力。

## 7. 不可引用 / 待核对（引用前扫一眼）

- **公式缺失页**（PDF 公式对象未抽出，不要据这些页引用公式）：`L4 P34`（平板电容 Cd）、`L4 P36`（Poisson–Boltzmann）、`L4 P37`（电容-电位-浓度）、`L4 P50`（隐式溶剂三步）。
- **纯图片页**（只有页眉页脚）：`L3 P34`、`L3 P75`、`L3 P119`、`L4 P7`、`L4 P19`、`L4 P51`。
- **讲义内部数值对不上**：`L1 P47` 引的 AFM OSZICAR 行与真实算例九个离子步都不等（磁矩块却完全一致）；`L3 P64` vs `P65` 的 ZPE/ΔH/ΔG 三项不等；`L3 P98` vs `P99` 差 0.0224 eV；`L4 P9` 表 O₂ 的 −9.91 vs `oer.xlsx` 的 −9.92。
- **讲义用词错误**：`L1 P44` 把 Fe₂O₃ 说成「反磁性」（应为反铁磁）；`L2 P31`、`L1 P11` 的 `10 mB` 应为 μB；`L1 P2/P3` 的「4 月 31 日」不存在。
- **算例归档坑**：`day3/idpp/nebmake/` 装的是 IDPP 结果；`day3/ts/dim/POSCAR` 尾部有 21 行 NaN；`ts-dimer/` 没有 DIMCAR；`day3/ts/05` 与 `ts-neb/00` 的 OUTCAR 是普通几何优化（不能核对 TS）；`oer/o2/` 没有结果文件；`ni-co` 的 DOSCAR 出自弛豫计算。
- **待核对（不要当断言）**：`ka = 1/R` 换算；「统一用 R=0.040」；vdW-DF2 使 MoS₂ 的 a 增大 3.09% 是否正常；能量口径 = `energy(sigma->0)`；ZPE 与 TΔS 的拆分方式；VASPsol 四参数走默认值；`+1.89 kcal/mol` 的出处；SHE 绝对电位 4.44 V 的出处；「TS 虚频 > 100 cm⁻¹」的适用范围；`IOPT=0` 的实际行为；官方 known issues 的具体内容。

---

## 8. E′ 层速查 · 《Learn VASP The Hard Way》第二版

> 引用写法 `<篇 ID>:<行号>`（如 `EX80:42`）。导航与差异表见
> `course_learned.md` §13；原文与精读报告在 `references/raw/lvthw/`。

### 8.1 三条**零成本自检**（数字已在输出里，不用重算）

| 自检 | 命令 | 判据 |
|---|---|---|
| 金属的 `SIGMA` 够不够 | `grep "entropy T" OUTCAR`，取 `entropy T*S` **除以原子数** | **< 1 meV/atom**（`[官方]` Smearing technique 页；`[LVTHW]` `EX01:167`） |
| `DOS` 的 `NEDOS` 够不够 | 看 `DOSCAR` 表头 | 经验 **≈ 3000**（`EX37:53`） |
| `k` 点密度够不够 | `K × a` | 经验 **≈ 45**（`EX37:45`；⚠️ `k·a≈30` 那条出处是 GPAW，**不是 VASP 官方**） |

### 8.2 最常用的 grep 与判据

| 目的 | 命令 / 判据 | 出处 |
|---|---|---|
| 判几何优化**收敛** | `grep reached OUTCAR \| tail -1` 的首词是 `reached`（`reached required accuracy - stopping structural energy minimisation`，**全文只 1 次**） | `M_02:58-70` |
| 分清两类 `reached` | `aborting loop because EDIFF is reached` = **电子步**（会出现很多次）；上面那条 = **离子步**（1 次） | 同上 |
| 读频率（**排除虚频**） | `grep 'f  =' OUTCAR`（**两个空格**，天然不匹配 `f/i=`）⚠️ 它也会匹配到 `EDIFF  =` 这类行 ⇒ **别拿它当唯一解析手段** | `EX26:161/179`；本项目 `[实测]` |
| 看有没有虚频 | `grep 'f/i=' OUTCAR` | 本项目 `[实测]` |
| 看 Bader 前要什么 | `INCAR` 里 `LAECHG=.TRUE.` **和** `LCHARG=.TRUE.`（**两个都要**；缺 `CHGCAR` 则 `bader` 没输入而 VASP **不报错**） | `A07:29-76` |
| Bader 净电荷 | `ACF.dat` 的 `CHARGE` 列 = 该原子**总价电子数**；净电荷 = `CHARGE` − 该元素 `ZVAL` | `A07:100-102` |
| Bader 自检（**本项目保留**） | `ACF.dat` 的 `CHARGE` 之和应等于 `NELECT` | `[实测]`（LVTHW **没有**这条，是本项目自己的） |

### 8.3 工程上的坑（都会静默出问题）

| 坑 | 症状 | 处方 | 出处 |
|---|---|---|---|
| **改真空层没转 Cartesian** | 直接改 `POSCAR` 第 5 行 `c` ⇒ **层间距被等比拉长**（实测 2.547 → 2.956 Å），**VASP 不报错** | 先把 `POSCAR` 转 Cartesian（`dire2cart.py` 的思路），或在 `Direct` 下同时按比例缩放原子 z | `EX51:74-96` |
| **NEB 运行期跑 `nebresults.pl`** | 它把各 image 的 `OUTCAR` gzip ⇒ VASP **找不到 `OUTCAR` 直接挂** | 装脚本时就把 `# Zip the OUTCARs again` 那段注释掉 | `EX72:56`、`EX77:119-142` |
| **NEB 的 00/09 混了高 k 点的 `OUTCAR`** | 剖面首末差 **23.1 eV**，真实能垒被淹没（**不报错**） | 给 00/09 各做一次**单点**，或粗算阶段 `cp 01/OUTCAR 00` | `EX77:245-264` |
| **`nebmake.pl` 逐维线性插值** | 某一维端点差很小时，该维"**什么都没插**"（原子横着走）⇒ 虚频多、收敛慢 | 手动加拱形：插 8 点时第 2/7 个抬 0.1 Å、3/6 抬 0.15、4/5 抬 0.2（`EX80:55`）。⚠️ **旋转类体系不适用** | `EX80:31/43`、`EX82:36` |
| **ASE 导出的 `POSCAR` 是 VASP4 格式** | 没有元素名行 ⇒ 元素顺序核对**整段静默跳过** | 补上第 6 行元素名（本项目已加 `XSPECIES.vasp4_poscar` 警告） | `A14:109`、`A16:48` |
| **`OPTCELL` 不回显** | 程序**不会告诉你它有没有生效** | 比 `POSCAR` 与 `CONTCAR` 的晶格 | `[实测]`（讲义层已有） |
| **`LDIPOL` 下真空能级有两个** | "最平窗口"会挑错，差 0.62 eV（Au+O slab 实测 7.196 vs 6.578 eV） | **两侧都报**，按面对应各自的功函数 | `pages/LDIPOL.md:12`；本项目 `[实测]` |

### 8.4 参数阶梯与取值（教程口径）

| 参数 | 教程给的 | 说明 |
|---|---|---|
| **过渡态 `EDIFFG`** | **`-0.05`（粗算）/ `-0.02`（一般）/ `-0.01`（出结果）** | 作者明说 `-0.05`"只是个形式""摆设"⇒ **它是阶梯，不是笔误**（`EX75:133/148`、`EX76:37`） |
| **表面/分子优化 `POTIM`** | **`0.1`** | 作者说官方默认 `0.5`"个人感觉比较大"（`EX44:93`）。现有层算例一律 `0.2` ⇒ **两者都记，标出差异** |
| **虚频可忽略的门槛** | **< 100 cm⁻¹**（严格 50） | `[经验]`，作者未给出处（`EX26:125`、`EX27:257`） |
| **Improved Dimer** | `IBRION = 44`（**VASP 原生**，不必编 VTST）；老口径 `ICHAIN=3`+`IBRION=3` | `[官方]` `IBRION.md:24,66`；`A32` |
| **气相分子自由能** | `G = E_DFT + E_ZPE + nRT − TS` | `TS` 作者**直接查 CRC / NIST-JANAF 表**（并提醒"别人也是查表、没算"，`EX68:143/165`） |
| **频率求和模数** | 加**全部实频**（3N） | 与讲义"3N"一致；与"只加 3N−6"差多少**未复算** ⇒ `[待核对]`（`C-1`） |

### 8.5 本层**不要**当来源的东西

- **DOSCAR 列语义**：G3 六篇里 `ISPIN`/`LORBIT` **0 命中** ⇒ 别挂到这一层。
- **d 带中心的积分窗口**：教程口径**更松**（"积分区间也不是很绝对"，`EX41:87`）⇒
  **本项目"必须同时报窗口"的纪律更强，保留本项目的**。
- **毛刺峰的成因**：`EX37:56` 说加 `NEDOS` 可解决，与本项目"根因是 k 点、`NEDOS` 不参与 SCF"**冲突** ⇒
  **以本项目为准**，教程那条标 `[待核对]`。
- **单原子破对称性**：`EX08:129-133` 有做法但**官方层没找到对应页** ⇒ `[待核对]`。
- **`ker`（k 点 × a）经验值**：出处是 **GPAW 教程**，不是 VASP 官方 ⇒ 别挂 `[官方]`。
