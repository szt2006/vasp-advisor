# L3 精读报告 —— 研之成理第四届固体与表面计算中级班（表面方向-催化专题）

- **资料来源**：`references/raw/L3.txt`（讲义正文，196 页，共 2793 行）、`references/raw/D3.txt`（答疑稿，48 段）
- **讲师**：刘锦程；课程时间 2020-04-27 ~ 31
- **正文实际覆盖的模块**（不是只有过渡态）：吸附基础 → 频率计算 → 热力学量计算/自由能校正 → 热力学分析（表面能/化学势/覆盖度）→ **过渡态搜索（重点）** → 反应动力学分析 → 催化反应机理
- **引用格式**：`L3 P<页号>`，页号范围 1..196；答疑稿引用格式 `D3-P<段号>`，范围 1..48
- **书写约定**：
  - 【讲义】= 原文真的这么写（带页码）
  - 推论：= 我根据原文/算例推出的，不是原文的断言
  - `[来源待核对]` = 单一来源或我自己推的，未获第二来源确认

> 阅读完成度声明：L3.txt 第 1–2793 行、L3 全部 196 页、D3.txt 全部 48 段均已逐页/逐段读完。
> 说明：`POTCAR` 一律未读取（许可限制）。`.gz` 一律解压到 `$env:TEMP`，未写入仓库。

---

## §1 页覆盖清单

格式：`P<页号> <主题>`。1..196 连续，无跳页。

```
P1 声明/版权页（盗版必究、举报奖励）
P2 分节封面：表面热力学与动力学（主讲人：刘锦程）
P3 化学吸附、物理吸附、解离吸附：三种吸附模式
P4 物理/化学/解离吸附的定义与吸附方程
P5 吸附能定义与公式 Eads = Em/slab − Em(g) − Eslab
P6 物理吸附：Ar/Cu(111) 势能曲线（−0.5 eV < Eads < 0 eV）
P7 化学吸附：H/Cu(111)，ontop / bridge / threefold-hollow
P8 解离吸附：H2/Cu(111) → 2H，一定存在能垒
P9 吸附位点：top / bridge / hollow，并非所有位点都真实存在
P10 H 原子吸附能公式（Eads = EH/slab − ½EH2 − Eslab）
P11 H/Cu(111) 二维势能面：Top 极大、Bridge 一阶鞍点、Hollow 极小
P12 找全吸附位点的方法：手动摆放 / AIMD 退火
P13 hollow 位分 HCP 与 FCC 两种
P14 表面吸附注意事项：ISYM=0 打破对称性；小能垒极难算
P15 吸附能算例：O/Au(111)-p(2×2)，O2 需 ISPIN=2
P16 轨迹可视化：Jmol / VESTA / vaspkit 405 + VMD
P17 top 位 O 会迁到 hollow；FCC 比 HCP 稳约 0.27 eV
P18 吸附物种间相互作用：覆盖度 1/4 ML、以 2Eads 为参照
P19 覆盖度定义 θ = N/N0 与平均吸附能
P20 分节封面：频率计算
P21 Hessian 矩阵定义（3N 维二阶偏导）
P22 Hessian 一般形式与质量权重坐标 Θ = M^(−1/2) H M^(−1/2)
P23 力常数矩阵（mass-weighted Hessian）与质量矩阵
P24 分子振动：非线性 3N−6、线性 3N−5；本征值/本征矢含义
P25 极小点和过渡态的验证：驻点 ≠ 极小点，必须算频率
P26 频率计算与结构优化必须同级别；频率 EDIFF = 1E-7
P27 谐振子、振动能级、零点振动能 ZPVE
P28 有限位移法：NFREE = 2 或 4；VASP 只算 Γ 点；可固定 slab
P29 频率练习步骤一：重建 freq 目录，vaspkit 403 固定 O 以下原子
P30 频率练习步骤二：INCAR（EDIFF=1E-7 / IBRION=5 / NFREE=2 / POTIM=0.015）
P31 步骤三~五：POTCAR/KPOINTS、提交、离子步数 = 6×放开原子数+1、Finite differences 输出
P32 OUTCAR 末段：力常数矩阵本征值与本征矢；meV 即 hν，hν/2 为 ZPE
P33 检查虚频 grep cm OUTCAR；TS 虚频约 132 cm⁻¹；虚频太小说明 TS 找错
P34 图片页（无正文文字）
P35 IS / TS / FS 频率汇总表（cm⁻¹ 与 meV）
P36 频率练习二：H2O 分子振动频率
P37 H2O 频率输出；3N 个频率中关心 3N−6 个
P38 分节封面：热力学量的计算
P39 做自由能校正的意义：引入温度、压力、pH、电极电势
P40 热力学量拆分为振动/平动/转动/电子激发；只适用气态分子与吸附物
P41 配分函数 Q 的定义与物理意义
P42 热力学量（U/A/H/G/S）与配分函数的关系式
P43 等容/等压热容与升温造成的 ΔU、ΔH
P44 不可分辨独立粒子体系：Q = q^N / N!
P45 理想气体假设：G = A + RT、H = U + RT、Cp = Cv + R
P46 玻尔兹曼常数 k 的数值与 R = k·NA
P47 能量成分拆分 εtot = εtrans+εrot+εvib+εele，qtot 为乘积
P48 lnQ 的分解（平动/转动/振动/电子四项）
P49 其他热力学量同样可分解；转动振动电子对 U 与 H 的贡献等价
P50 吸附后平动转动 6 自由度转为振动，3N 个振动自由度都要算
P51 (一) 振动热力学贡献：qvib 与 Uvib(T) 公式
P52 0 K 时的零点振动能 ZPE = ½Σhνi
P53 ZPE 与频率的关系：H2 伸缩振动 4395 cm⁻¹，ZPE 校正很大
P54 振动熵 Svib；低频模式是热力学数据最困难之处
P55 低频振动对熵的贡献；文献建议把 <50 cm⁻¹ 的频率按 50 cm⁻¹ 计
P56 (二) 平动配分函数（唯一与压力有关）
P57 平动的 U/H/S 校正公式
P58 (三) 转动配分函数：线性与非线性分子
P59 转动的 U/S 校正公式
P60 (四) 电子配分函数与电子熵（基态简并时才有贡献）
P61 0 K 热力学数据：G(0)=H(0)=U(0)=εele+ZPE；ZPE 的读法
P62 T > 0 K 的热力学数据表达式
P63 练习一：O 在 Au(111) 迁移自由能垒；vaspkit 5 → 501 → 输入温度
P64 vaspkit 501 输出示例（<50 cm⁻¹ 按 50 cm⁻¹ 处理）
P65 298.15 K 与 800 K 数据整理表（Is/Ts/Fs）
P66 结论：常温可忽略自由能校正，高温影响大
P67 气体分子自由能校正三法：JANAF-NIST / Gaussian / vaspkit 502
P68 JANAF-NIST 网站
P69 JANAF 表包含的列（温度、热容、熵、焓、生成焓、生成自由能）
P70 用 JANAF 表做 H 校正与 S 校正
P71 计算 O2 振动能与 ZPE（只取第一个频率）
P72 O2 自由能校正表；气体分子校正不可忽略
P73 vaspkit 502 计算 O2 自由能校正，与实验值 −0.45 eV 相符
P74 解离吸附+迁移的能量图（DFT / 298.15 K / 800 K）
P75 能量图（图片页）
P76 分节封面：热力学分析
P77 化学平衡的定义与反应速率关系
P78 表面吸附平衡：rads = rdes
P79 Langmuir 吸附等温式推导
P80 Langmuir 吸附等温式的前提假设
P81 熵变对吸附的影响：Nørskov 估算 −0.002 eV/K
P82 覆盖度与温度的关系（400–600 K 从 1 变到 0，TPD 表征）
P83 覆盖度与压力的关系
P84 覆盖度与吸附能的关系（敏感区间 −0.7 ~ −0.5 eV）
P85 多组分气体竞争吸附的 Langmuir 形式
P86 多组分：吸附能差 ±0.1 eV 即可使覆盖度完全反转
P87 实例：CO 毒化 Pt 电极燃料电池（Eads(H2)=−0.7，Eads(CO)=−1.2 eV）
P88 电流电压曲线：1 ppm CO 即使 CO 覆盖度接近 100%
P89 抗 CO 毒化实例：Pt1/α-MoC
P90 催化剂中毒的其他实例（Ru 氢毒化、合成氨、重整、燃料电池）
P91 最稳定表面的计算（引 Phys. Rev. B 2001, 65, 035406）
P92 表面能公式 γ(T,p) 与环境化学势基准
P93 RuO2(110) 各候选表面（Obridge / Otop / Ru）
P94 RuO2 表面能计算数据；bulk 自由能用 phonopy 算，slab 校正可抵消
P95 O 化学势 μO 的上下限（富氧 / 缺氧）
P96 表面能随 μO 变化：O-rich 时 Otop 最稳，O-poor 时 Obridge 最稳
P97 温度和压力对 μO(T,p) 的影响（用 VASPKIT 算）
P98 vaspkit 502 计算 G(T)（100 K 示例）
P99 μO 随温度（0–1500 K）与压力（log P = 0 ~ −14）的数值表
P100 μO–γ 相图（分别以温度和压力为横轴）
P101 缺陷表面同样处理，只需算清每种表面的 NRu 与 NO
P102 实例：Rh 在 TiO2(110) 上 support/dope 的热力学稳定性随 μO 变化
P103 吸附物种对最稳定表面的影响（RuO2(110)，CO 与 O 共存）
P104 引入 CO 后的表面能公式（两个自变量 μO、μCO）
P105 μO 上下限不变；CO 与 RuO2 反应的稳定性约束
P106 数值代入，得到 ΔμO − ΔμCO > −0.15 eV
P107 相图分区：虚线右下稳定、左上不稳定
P108 金属表面覆盖度与 O 化学势（Ag，引 PRL 2003）
P109 干净表面 / 吸附 O / 被氧化成氧化物
P110 化学势分析 Ostwald ripening（只考虑热力学不考虑动力学）
P111 纳米颗粒化学势（Gibbs–Thomson）与单原子化学势
P112 方法学总结：表面热力学 → 动力学 → TOF → BEP/火山曲线
P113 分节封面：过渡态搜索
P114 过渡态定义：一阶鞍点（沿反应路径是极大，正交方向是极小）
P115 过渡态 = 一阶鞍点（爬山类比）
P116 一些化学过程没有过渡态（离子键断裂、自由基复合、部分吸附脱附）
P117 寻找过渡态方法的分类；VASP(VTST) 推荐 DIMER 与 CI-NEB
P118 NEB 原理：插入 P−1 个点，反应物编号 0、产物编号 P
P119 图片页（NEB 示意）
P120 NEB 受力：势能面的力 + chain 方向的弹簧力
P121 传统 PEB 方法的问题：偏离 MEP、难以找到最高点
P122 nudge 过程：力在路径切向/法向的投影规则
P123 CINEB：NEB 的缺点与 CI-NEB 的改进（最高点不再受弹簧力、平行分量符号反转）
P124 CI-NEB 只需很少的点（含初末态 5 个甚至 3 个）；"插点越多越好"是错的
P125 步骤一/二：优化 IS 与 FS；dist.pl 检查相似程度（< 5 Å）
P126 步骤三：nebmake.pl 插点（插点数 ≈ dist.pl 返回值 / 0.8；本例插 1 个点）
P127 步骤四/五：把 IS/FS 的 OUTCAR 复制到 00/02；nebmovie.pl 检查插点合理性
P128 nebmovie.pl 用法与 movie.xyz 生成
P129 步骤六：CINEB 的 INCAR（EDIFF=1E-7、EDIFFG=−0.03、IBRION=3/POTIM=0、IOPT=1）
P130 VTST 优化算法：IOPT=1,2 适合精收敛；IOPT=7 适合粗收敛
P131 步骤六续：ICHAIN=0、LCLIMB=.TRUE.、IMAGES、SPRING=−5 + INCAR 全文
P132 步骤七/八/九：POTCAR/KPOINTS；核数需被插点数整除；nebef.pl / nebefs.pl 跟踪
P133 收敛判据：所有插点最大原子受力 < |EDIFFG|；本例 14 步收敛；耗时/能量
P134 步骤十二：nebresults.pl 总结输出（Forces and Energy、Extremum）
P135 nebresults.pl 做的事情；mep.eps 含义；会把 OUTCAR 打包成 .gz
P136 vaspgr 目录内的各插点收敛图
P137 DIMER 基本原理：两点组成的二聚体，间距 2ΔR ≈ 0.01 Å，须 EDIFF=1E-7
P138 Dimer 中点受力/能量；旋转 Dimer 即最小化曲率
P139 平移 Dimer：曲率 C>0 与 C<0 时 F' 的不同定义
P140 Dimer 寻找过渡态流程图与收敛判断（F<|EDIFFG| 且 C<0）
P141 DIMER 历史发展（Henkelman 1999 / Heyden 2005 / Kästner 2008 / solid-state dimer 2014）
P142 DIMER 步骤一/二：优化 IS/FS；准备过渡态初猜 POSCAR
P143 初猜技巧：保证没有过短的键；O 在 bridge 位时 z 坐标更高
P144 步骤三：MODECAR 文件与 modemake.pl 原理
P145 MODECAR 内容示例；MODECAR 就是虚频振动方向；NEWMODECAR
P146 步骤四：Dimer 的 INCAR（ICHAIN=2、IBRION=3/POTIM=0、IOPT=2、EDIFF=1E-7）
P147 Dimer INCAR 全文；DdR/DRotMax/DFNMin/DFNMax 被注释；EDIFFG=−0.03
P148 步骤五/六/七：POTCAR/KPOINTS；必须用编译了 VTST 的 VASP；跟踪收敛
P149 DIMCAR 输出示例（Step/Force/Torque/Energy/Curvature/Angle）
P150 DIMCAR 解读：Step、Force、Torque
P151 DIMCAR 解读：Energy、Curvature、Angle；Torque 不降时的处方
P152 CENTCAR 与 NEWMODECAR；dimmode.pl 生成振动方向动画
P153 VTST 收敛判断：grep converged OUTCAR、grep RMS OUTCAR、tail −1 OSZICAR；本例 207 离子步
P154 过渡态常见问题(1)：中间点能量比初末态都低
P155 常见问题(2)：出现极大的原子受力（>10 eV/Å），用 idpp.py 非线性插点
P156 常见问题(3)：接近收敛但力长期不达标 → PREC/EDIFF/IOPT/放宽标准
P157 常见问题(4)：没有虚频或有多个虚频
P158 常见问题(5)：nebmake.pl 插点结构混乱 → 检查原子顺序是否一一对应
P159 分节封面：过渡态搜索（补充内容）
P160 实例：环己烷在 Pt1/graphene 上脱氢的 CINEB INCAR
P161 nebresults.pl 流程；nebef.pl 与 exts.dat 输出
P162 nebspline.pl 输出 spline.dat / exts.dat / mep.eps；极值点需人工判断
P163 图注：可能存在的过渡态需验证；重新优化确定极小值是否真实存在
P164 NEB + Dimer 组合高效搜索过渡态
P165 第一步 CINEB 粗收敛（EDIFFG=−0.5、EDIFF=1E-5）；第二步 neb2dim.pl
P166 neb2dim.pl 生成的 dim 文件夹；需把 CINEB 参数删掉
P167 neb2dim.pl 不指定 image 时自动取 exts.dat 最高点；建议手动准备 POSCAR/MODECAR
P168 NEB 线性插点的问题（nebmake.pl 的两个缺点）
P169 实例：*C6H11 + *H → C6H10 + H2，(03) image 的 C–H 键只有 0.59 Å
P170 IDPP 插点法（引 J. Chem. Phys. 140, 214106 (2014)）
P171 线性插点 0.59 Å 与 IDPP 1.09 Å 的对比图
P172 ASE 与 pymatgen-diffusion 已实现 IDPP；许楠博士的 idpp.py
P173 idpp.py 的安装与使用方法
P174 分节封面：反应动力学分析
P175 基元反应与单分子基元反应速率
P176 双分子基元反应；三分子基元反应几乎不存在
P177 反应速率常数与 Arrhenius 方程；计算速率常数的方法
P178 过渡态理论 TST 公式；k.py 小脚本
P179 半衰期与 ΔGa 对照表
P180 谐振过渡态理论 HTST
P181 隧穿效应
P182 Wigner 方法计算透热系数
P183 Wigner 方法数值示例；虚频大小与隧穿的关系
P184 分节封面：催化反应机理
P185 表面催化基元步骤三类；三大类反应机理（LH/ER/MvK）
P186 Langmuir-Hinshelwood (LH) 机理
P187 最简单的 LH 机理与反应速率
P188 Eley-Rideal (ER) 机理
P189 最简单的 ER 机理与反应速率
P190 Mars-Van Krevelen (MvK) 机理
P191 最简单的 MvK 机理与反应速率
P192 经典 LH 实例：合成氨反应
P193 经典 ER 实例：Volmer-Heyrovsky HER
P194 经典 MvK 实例：CO 氧化反应
P195 催化循环：催化剂必须复原；催化剂不改变总反应能量变化
P196 声明/版权页
```

---

## §2 主题分段表

与 `seg_L3.tsv` 完全一致（见该文件）。分段按页边界切分，连续覆盖 L3.txt 第 1–2793 行，无重叠、无空档。

| 段 | 行范围 | 页范围 | 主题 | 要点 |
|---|---|---|---|---|
| 1 | 1–16 | P1–P2 | 声明与封面 | 版权声明；"表面热力学与动力学"分节封面、主讲人 |
| 2 | 17–230 | P3–P19 | 吸附基础 | 物理/化学/解离吸附；吸附能定义；吸附位点(top/bridge/hollow、HCP/FCC)；打破对称性 ISYM=0；覆盖度 |
| 3 | 231–356 | P20–P28 | 频率计算原理 | Hessian 与力常数矩阵；3N−6/3N−5；谐振子与 ZPE；有限位移法 NFREE=2/4；频率与优化须同级别 |
| 4 | 357–497 | P29–P36 | 频率计算实操 | vaspkit 403 固定原子；vaspkit/INCAR 设置；离子步数公式；grep cm 读虚频；IS/TS/FS 频率对比 |
| 5 | 498–514 | P37 | H2O 频率实例 | 3N 个频率中取 3N−6 个；虚频出现在低频段 |
| 6 | 515–650 | P38–P46 | 热力学量计算基础 | 配分函数 Q；热力学量关系式；热容；Q=q^N/N!；理想气体假设；玻尔兹曼常数 |
| 7 | 651–816 | P47–P55 | 振动热力学贡献 | 能量拆分与 qtot 乘积；吸附后转动平动转为振动；Uvib/Svib；ZPE；低频模式的处理（<50 cm⁻¹） |
| 8 | 817–890 | P56–P60 | 平动/转动/电子贡献 | qtrans 与压力；U/H/S 平动公式；qrot 线性/非线性；电子配分函数与简并 |
| 9 | 891–975 | P61–P66 | 0K 与有限温度热力学数据 | G(0)=εele+ZPE；vaspkit 501 流程；Is/Ts/Fs 的 298.15 K 与 800 K 表 |
| 10 | 976–1069 | P67–P73 | 气体分子自由能校正 | JANAF-NIST 查表法；Gaussian 法；vaspkit 502；O2 校正算例与实验值对比 |
| 11 | 1070–1104 | P74–P76 | 能量图与分节封面 | 解离吸附+迁移的 DFT/298.15K/800K 能量图；热力学分析封面 |
| 12 | 1105–1257 | P77–P87 | 化学平衡与 Langmuir 吸附 | 吸附平衡与等温式；熵/温度/压力/吸附能对覆盖度的影响；多组分竞争；CO 毒化 Pt |
| 13 | 1258–1293 | P88–P91 | 毒化实例与表面稳定性引言 | CO 电流电压曲线；Pt1/α-MoC；中毒案例；最稳定表面计算引言 |
| 14 | 1294–1471 | P92–P103 | 表面能与化学势 | γ(T,p) 公式与基准；RuO2(110) 算例；μO 上下限；温压影响；缺陷/掺杂表面 |
| 15 | 1472–1600 | P104–P112 | 多自变量相图与覆盖度 | CO 共存时的 γ(T,pO2,pCO)；Ag 表面覆盖度；Ostwald ripening；方法学总结 |
| 16 | 1601–1747 | P113–P125 | 过渡态概念与 NEB 原理 | 一阶鞍点；无过渡态的情形；方法分类；NEB/PEB/nudge/CI-NEB；dist.pl 检查 |
| 17 | 1748–1792 | P126–P128 | nebmake.pl 插点与可视化 | nebmake.pl 用法与插点数经验规则；生成 00/01/02；nebmovie.pl |
| 18 | 1793–1888 | P129–P133 | CINEB 输入与收敛 | INCAR 逐条设置（EDIFF/EDIFFG/IBRION/POTIM/IOPT/ICHAIN/LCLIMB/IMAGES/SPRING）；并行整除；nebef.pl；收敛判据 |
| 19 | 1889–1927 | P134–P136 | CINEB 后处理 | nebresults.pl 输出；mep.eps；vaspgr 收敛图；OUTCAR 打包 |
| 20 | 1928–2002 | P137–P141 | DIMER 原理与历史 | 二聚体/曲率最小化；旋转与平移；收敛判据；方法演进文献 |
| 21 | 2003–2070 | P142–P145 | DIMER 初猜与 MODECAR | 初猜结构准备与技巧；MODECAR 生成原理与内容；NEWMODECAR |
| 22 | 2071–2248 | P146–P153 | DIMER 输入与结果解读 | Dimer INCAR（ICHAIN=2/IOPT=2/DdR 等）；DIMCAR 逐列解读；CENTCAR/NEWMODECAR/dimmode.pl；收敛判断三条命令 |
| 23 | 2249–2295 | P154–P158 | 过渡态常见问题 | 五类失败模式与讲师处方（能量异常、受力爆炸、力不达标、虚频数目、原子顺序） |
| 24 | 2296–2416 | P159–P167 | 补充实例与 NEB+Dimer | 环己烷/Pt1-graphene 的 CINEB INCAR；nebresults 后处理链；NEB 粗搜 + Dimer 精修流程；neb2dim.pl |
| 25 | 2417–2487 | P168–P173 | 线性插点缺陷与 IDPP | nebmake.pl 的缺点；0.59 Å 实例；IDPP 原理与实现；idpp.py 安装使用 |
| 26 | 2488–2565 | P174–P178 | 反应动力学基础 | 基元反应与速率方程；Arrhenius；速率常数计算方法；TST 公式与 k.py |
| 27 | 2566–2650 | P179–P183 | 半衰期/HTST/隧穿 | 半衰期表；谐振过渡态理论；隧穿效应；Wigner 透热系数 |
| 28 | 2651–2772 | P184–P194 | 催化反应机理 | 三类基元步骤；LH/ER/MvK 机理与速率；合成氨、HER、CO 氧化三个经典实例 |
| 29 | 2773–2793 | P195–P196 | 催化循环与声明 | 催化剂复原闭环；催化剂不改变总反应能量变化；版权声明 |

---

## §3 知识条目

### 3.1 过渡态搜索：什么时候用哪种方法

**过渡态的定义（L3 P114, P115）**
- 过渡态（transition state）搜索的目标是**优化到一阶鞍点**，即 MEP（minimum energy path）上能量最高的点。
- 一阶鞍点的判据【讲义 P114】："仅在沿着反应路径上是能量极大点，而在（与）之正交的其他所有方向上都是能量极小点"。
- P114 的图把驻点分成：极大点（全局最大）、过渡态、极小点（全局最小）、极小点（局部极小）、极大点（局部极大）。

**没有过渡态的过程（L3 P116）【讲义原文列出】**
1. 离子键断裂成为阴阳离子（或阴阳离子结合）
2. 共价键断裂成为两个自由基（或自由基的复合反应），例：CH3CH3 → 2·CH3
3. 一些表面吸附/脱附的过程
4. 一些吸附/脱附过程静态计算不出过渡态，但模拟自由能势能面存在过渡态——这是熵效应的影响

**方法分类（L3 P117）【讲义原文】**
按所需初猜分四类：
1. 基于单个初猜结构的方法 —— **DIMER**
2. 基于反应物与产物结构的方法 —— **CI-NEB**
3. 基于反应物结构的方法
4. 势能面扫描

- VASP(VTST) 支持的最好用的两种是 **DIMER 与 CI-NEB**（L3 P117）。
- VTST 包是 VASP 的插件，**需要在编译 VASP 的时候导入**（L3 P117）。
- 讲义的进一步提示【P148】：提交脚本一定要选**编译了 VTST 的 VASP**，否则 `IBRION=3, POTIM=0` 关闭了 VASP 的结构优化模块，无法进行计算。

**选型（讲义给的判断）**
| 情形 | 讲师建议 | 页码 |
|---|---|---|
| 简单扩散、路径近似直线 | CI-NEB 效率高（本例 14 步收敛） | L3 P133、L3 P168 |
| 初猜结构好 | Dimer 效率很高 | L3 P164 |
| 初猜不好 | Dimer 经常失败 | L3 P164 |
| 复杂催化反应（两种方法单独都低效） | 先用 CINEB/NEB 粗搜 → 取能量最高的结构作为 Dimer 初猜 → 再用 Dimer 精修 | L3 P164、P165 |
| 只要一个初猜、可以不要 IS/FS | Dimer 可以不需要 IS/FS，但"这个早晚要算的"，先算 IS/FS 有助于初猜与理解反应 | L3 P142 |

---

### 3.2 CI-NEB：原理、代价、输入

**原理（L3 P118, P120, P122, P123, P124）**
- NEB 是 chain-of-states 搜索方法的一种，发展成现在的 CINEB（L3 P118）。
- 做法：在反应物到产物之间插入一系列结构，共插入 **P−1 个**，反应物编号 0、产物编号 P（L3 P118）。优化不是对每个点孤立优化，而是优化一个函数，每一步所有点一起运动（L3 P118）。
- 首末两点固定不动；其他点受两个力（L3 P120）：① 来自势能面的力；② chain 方向上的弹簧力。弹簧力避免相邻点距离过短或过长。
- 传统 PEB 的两个问题（L3 P121）：反应路径偏离 MEP；难以找到最高点，需要插入非常多的点，浪费计算资源。
- **nudge 过程**（L3 P122）——解决 MEP 偏离：
  - 弹簧力垂直于路径的分量被投影掉；平行于路径的分量完全保留；
  - 势能力在路径方向上的分量被投影掉；势能力垂直于路径的分量引导结构点正确移动。
  - 原文表述："(1) 每个点在平行于路径切线上的受力只等于弹簧力在这个方向分量，(2) 每个点在垂直于路径切线方向的受力只等于势能力在此方向上分量"。
- **CI-NEB 相对 NEB 的关键区别**（L3 P123）：能量最高的点**不受相邻点的弹簧力**，避免位置被拉离过渡态；并且把该点**平行于路径方向的势能力分量符号反转**，促使它沿能量升高方向爬到过渡态。
- CI-NEB 修正的两个 NEB 缺点（L3 P123）：(1) 要插足够多的点才能找到近似过渡态，计算资源消耗极大；(2) 珠子不可能到鞍点顶端，算出的过渡态能量总被低估，而 LDA/GGA 又常低估过渡态能量，误差叠加。

**代价与插点数目（L3 P124）—— 讲义明确反对"插点越多越好"**
- CI-NEB 只需要很少的点，"包含初、末态总共 5 个甚至 3 个点就能准确定位过渡态"。
- 原文强调："在网上看到一些说法 CI-NEB 插点越多越好，这是错误的结论！！由于能量最高的点可以自动爬坡，所以有的时候插一个点也可以精确地找到过渡态的位置，**大多数时候插 3 到 4 个点已经完全能应付正常的过渡态计算需要**。"
- L3 P126 又重复一次："（好多人被网上的有毒的教程误导，认为插一个点不对，这其实完全没有问题，这里只插一个点和插三个点的结果完全一样。）"
- L3 P126 给出插点数的经验规则：**插点数目 ≈ dist.pl 返回值 / 0.8**。
- **适用范围**：`IMAGES` 指"两个固定端点之间的像数"，总点数 = IMAGES + 2（L3 P131 把 IMAGES 注为"插点个数"；L3 P132 又说"核的个数必须整除插点的数量"）。

**CI-NEB 完整步骤（L3 P125–P136）**

| 步骤 | 内容 | 页码 |
|---|---|---|
| 一 | 优化初态（IS）和末态（FS）结构 | P125 |
| 二 | `dist.pl ini/CONTCAR fin/CONTCAR` 检查两结构相似程度；返回值 < 5 Å 一般可进行下一步（本例 1.73920306203566）；数值很大要检查初末态**原子顺序**是否一一对应 | P125 |
| 三 | `nebmake.pl ../is/CONTCAR ../fs/CONTCAR 1` 插点；成功提示 `OK, ALL SETUP HERE`，自动生成 `./00 ./01 ./02`；00 放 IS、02 放 FS、中间为插点，文件名统一为 POSCAR | P126 |
| 四 | `cp ../is/OUTCAR ./00/`、`cp ../fs/OUTCAR ./02/`（供后续分析） | P127 |
| 五 | `nebmovie.pl 0`（用 POSCAR 生成 xyz；参数 1 用 CONTCAR）检查插点合理性（可跳过） | P127、P128 |
| 六 | 准备 INCAR（见下表） | P129、P131 |
| 七 | POTCAR 与 KPOINTS 直接复制结构优化的 | P132 |
| 八 | 提交任务；核数必须整除插点数量 | P132 |
| 九 | `nebef.pl` 或 `nebefs.pl`（不带参数）跟踪收敛；后三列为 [最大原子受力]、[能量]、[相对初态的能量] | P132 |
| 十 | 收敛判据：**所有插点的最大原子受力都 < abs(EDIFFG)**；插多个点时所有点都要满足 | P133 |
| 十一 | 频率计算验证虚频 | P133（详见 L3 P153 / 频率章节） |
| 十二 | `nebresults.pl` 总结结果 | P134、P135 |

**CI-NEB 的 INCAR（L3 P129, P131）【讲义原文】**
```
#### Geo opt ####
EDIFFG = -0.03
IBRION = 3
POTIM  = 0
NSW    = 300
ISIF   = 2

#### VTST ####
ICHAIN = 0
LCLIMB = .TRUE.
IOPT   = 1
IMAGES = 1
SPRING = -5
```
逐条理由（讲义原文）：
1. `EDIFF = 1E-7` —— "这个参数非常关键！过渡态对力计算精度要求极高，更精准的电子步收敛会有更精准的力，可以加速收敛。**好多过渡态计算不收敛原因都是因为力的精度不够**。"（注：粗收敛可以适当放宽到 1E-5）（P129）
2. `EDIFFG = -0.03` —— "过渡态可以适当放宽结构优化的收敛精度到 −0.03，对于非常复杂难以收敛的体系可以放宽到 −0.05"（P129）
3. `IBRION = 3, POTIM = 0` —— "这是 VTST 识别并启动 VTST 优化算法的标致（标志）"（P129）
4. `IOPT = 1`；"IOPT 推荐 7，2，或 1。0 意味着启用 VASP 自带的优化算法（比如：IOPT=0，则 IBRION=1, POTIM=0.1）"（P129）
5. `ICHAIN = 0` 开启 NEB 方法（P131）
6. `LCLIMB = .TRUE.` 爬坡即 CI-NEB（P131）
7. `IMAGES = 1` 插点个数（P131）
8. `SPRING = -5` 弹簧力常数，"用 −5 默认值即可"（P131）

- IOPT 取值语义（L3 P130）：**IOPT = 1、2 适合精收敛；IOPT = 7 适合粗收敛**。
- 其他同批参数（P131 INCAR 全文）：`KPAR=4`、`NCORE=5`、`ENCUT=400`、`ISMEAR=1`、`SIGMA=0.2`、`NELMIN=5`、`NELM=300`、`GGA=PE`、`LREAL=Auto`、`LDIPOL=.TRUE.`、`IDIPOL=3`、`ISYM=0`、`ISTART=1`、`ICHARG=1`、`LWAVE/LCHARG=.TRUE.`、`LVTOT/LVHAR/LELF=.FALSE.`。

**后处理输出（L3 P134–P136）**
- `nebresults.pl` 依次做：`nebbarrier.pl`、`nebspline.pl`、`nebef.pl`、`nebmovie.pl`、`nebjmovie.pl`、`nebconverge.pl`，并把各文件夹 OUTCAR 打包压缩（P135）。
- 生成文件：`mep.eps`（以 dist.pl 距离为横坐标、能量为纵坐标的能垒图）、`vaspgr/` 下各插点收敛图（EPS/PS viewer 打开）、`movie.xyz`（Jmol 可看）（P135、P136）。
- `nebresults.pl` 输出示例（P134）：
  ```
  Forces and Energy:
  0 0.000000 -66.750800 0.000000
  1 0.007564 -66.256600 0.494200
  2 0.000000 -66.482400 0.268400
  Extremum 1 found at image 0.998685 with energy: 0.494221
  Extremum 2 found at image 1.998675 with energy: 0.268416
  ```
- 不想被压缩可用 `gunzip 0*/OUTCAR.gz`（P135）。
- `nebspline.pl` 输出 `spline.dat`、`exts.dat`、`mep.eps`；**拟合出来的极值点不一定是真实存在的，需要自己判断，并做频率计算验证**；"实际上一般我们只关注能量最高的 image 能量（用 nebef.pl 获取）"（L3 P162）。
- `exts.dat` 的极值点要区分三类（L3 P163）：可能存在的过渡态（需进一步验证）；我们要找的过渡态位置（进行频率验证）；重新优化此结构以确定极小值是否真实存在。

**CI-NEB 的代价（讲义口径）**
- L3 P123："要插入足够多的点才可能找到近似的过渡态，计算资源消耗极大"（这是 NEB 的缺点，CI-NEB 已缓解）。
- L3 P132：**核的个数必须整除插点的数量**（为保证最大并行效率，节点数最好等于插点的个数）——这是 CI-NEB 并行上的额外约束。
- L3 P133 算例：CI-NEB 耗时 875.054 s，最终能量 −66.26 eV。

---

### 3.3 DIMER：原理、代价、输入

**原理（L3 P137–P140）**
- Dimer 定义由两个点 R1、R2 组成的二聚体（哑铃），能量 E1/E2、受力 F1/F2，两点间距 **2ΔR**，ΔR 为定值；**通常 2ΔR ~ 0.01 Å**（L3 P137）。
- 因为间距非常小，Dimer 算过渡态**对力的精度要求非常高（EDIFF = 1E-7）**（L3 P137）。
- 中点 R 的受力 F(R) = (F1+F2)/2，总能量 E = (E1+E2)/2；每一步包括**平移 Dimer 和旋转 Dimer** 两步（L3 P138）。
- 旋转 Dimer：保持中点 R 不变作为轴，旋转直到总能量 E 最小；"能量 E 正比于曲率，即最小化 E 的过程就是最小化曲率的过程"，所以每一步的 Dimer 方向都是曲率最小方向；**R 收敛到过渡态位置时，Dimer 平行于虚频方向**，可跟踪 dimer 方向判断计算是否正常（L3 P138）。
- 平移 Dimer（L3 P139）：
  - 曲率 C > 0（极小点二次区域内）：F' 等于 F(R) 平行于 Dimer 方向分量的**负值**，没有垂直于 Dimer 方向的力，促使 Dimer 尽快离开这个区域；
  - 曲率 C < 0（过渡态或高阶鞍点的二次区域内）：F' 等于把 F(R) 平行于 Dimer 方向分量**符号反转**，并保持垂直于 Dimer 方向的受力。
- 收敛判据（L3 P140）：**力 F(R) < abs(EDIFFG)，且曲率 C < 0**，收敛结束计算；随后用频率计算验证只有一个虚频。

**历史（L3 P141）**
- G. Henkelman 提出并写入 VTST：J. Chem. Phys. 111, 7010 (1999)
- A. Heyden 等改进出 improved dimer：J. Chem. Phys. 123, 224101 (2005)
- J. Kästner 改进收敛性：J. Chem. Phys. 128, 014106 (2008)
- 这些改进都加入最新 VTST；**5.4.4 的 VASP 里也把改进的 Dimer 方法加入了**（L3 P141）
- 2014 年 G. Henkelman 又开发 solid-state dimer 研究相变：J. Chem. Phys. 140, 174104 (2014)

**DIMER 步骤（L3 P142–P153）**

| 步骤 | 内容 | 页码 |
|---|---|---|
| 一 | 优化 IS 与 FS。注：Dimer 可以不需要 IS/FS，但早晚要算，算 IS/FS 有助于初猜和理解反应 | P142 |
| 二 | 准备过渡态初猜结构 POSCAR：可从 MS 手动调整 IS/FS 得到；也可以 `nebmake.pl` 产生几个中间点，选一个作为 Dimer 初始结构 | P142 |
| 三 | 准备 MODECAR（见下） | P144、P145 |
| 四 | 准备 Dimer INCAR（见下） | P146、P147 |
| 五 | POTCAR 与 KPOINTS 同结构优化 | P148 |
| 六 | 提交任务（必须用编译了 VTST 的 VASP） | P148 |
| 七 | 跟踪收敛；发现严重不合理的结构偏离就杀掉任务重新调整初始构型 | P148 |

**初猜技巧（L3 P143）**
- "初猜是找过渡态最需要技巧的地方，初猜的好坏直接影响计算的成功率和计算时间。初猜要尽量接近过渡态。"
- **最基本的技巧：保证没有过短的键**，因为过短的键长会导致强排斥，让结构在前几个离子步崩掉从而远离过渡态。
- 例子：O 的 diffusion，如果 O 完全平着（z 不变）穿越能垒，bridge 位（过渡态）的 Au–O 键会比 hollow 位更短，所以**在过渡态位置 O 的 z 坐标会更高一点**。

**MODECAR（L3 P144、P145）**
- MODECAR 定义**初始的 dimer 方向**；如果没有这个文件，程序自己随机初猜一个方向（**强烈建议设置 MODECAR**）。
- 生成工具：VTST 库脚本 `modemake.pl`，原理是"用过渡态的初猜结构坐标减去初态，或者用末态结构坐标减去初态，再做归一化处理，相当于一个矢量"。
- 用法：
  ```
  modemake.pl ../is/CONTCAR ../fs/CONTCAR
  modemake.pl ../is/CONTCAR ./POSCAR
  ```
  第二种方法需要把 `is/CONTCAR` 后面的原子速度部分都删掉，以保持和 POSCAR 的行数一样（L3 P144）。
- 内容格式（L3 P145）：每个原子一行、每行 3 个数（对应 dx dy dz），逐原子排列；讲义示例中前若干行是 ~1E-14 ~ 1E-5 量级（几乎为零），**最后一行是主分量** `2.4199310346E-01 9.3308559935E-01 1.6190951779E-01`。
- "MODECAR 就是 dimer 的方向，也就是我们期待的虚频的振动的方向，开始 DIMER 计算以后每一 Dimer 旋转步都会更新 **NEWMODECAR** 为新的 dimer 方向"（L3 P145）。

**DIMER 的 INCAR（L3 P146、P147）【讲义原文】**
```
#### Geo opt ####
EDIFFG = -0.03
IBRION = 3
POTIM  = 0
NSW    = 300
ISIF   = 2

#### VTST ####
ICHAIN = 2
IOPT   = 2
# DdR = 5E-3
# DRotMax = 1
# DFNMin = 0.01
# DFNMax = 1.0
```
逐条理由：
1. `ICHAIN = 2` 开启 VTST 中 DIMER 的算法（P146）
2. `IBRION = 3, POTIM = 0` —— VTST 识别并启动 VTST 优化算法的标志（P146）
3. `IOPT = 2`；"为了保证过渡态计算稳定收敛，IOPT 推荐 7，2，1。0 意味着启用 VASP 自带的优化算法（比如：IOPT=0，则 IBRION=1, POTIM=0.1）"（P146）
4. `EDIFF = 1E-7` —— "由于 Dimer 的两个点间距很小，要求力计算精度极高"（P146）
5. `EDIFFG = -0.03` —— 同 CI-NEB 的放宽逻辑（P147）

- L3 P147 注释掉的四个 Dimer 专属参数（**讲义没有展开讲取值含义**，只在注释里给出数值）：`DdR = 5E-3`（dimer 间距）、`DRotMax = 1`（每个平移步最多旋转次数）、`DFNMin = 0.01`、`DFNMax = 1.0`。
- L3 P151 提到调参处方时又出现一次 **`DdR=0.01`**（"或者提高 DdR=0.01"）——与 P147 注释里的 `5E-3` 不是同一个数（见 §4 C-12）。

**DIMCAR 解读（L3 P149, P150, P151）**
列：`Step  Force  Torque  Energy  Curvature  Angle`
- **Step**：平移 Dimer 的步数；每一个平移 Dimer 中可以包含数个旋转 Dimer。
- **Force**：Dimer 在任意自由度上的最大受力；**这个 Force < abs(EDIFFG) 不是判断收敛的标准**；判断收敛的标准是**最大原子受力 F < abs(EDIFFG)**。
- **Torque**：Dimer 的扭矩，旋转 DIMER 总是向着使扭转力减小的方向转动；**当 Torque < 1 时，则进入平移 Dimer 步**。
- **Energy**：Dimer 中点的能量；**"这个能量不是电子熵外推到 0 的能量，故不能用作最终的过渡态能量，过渡态能量（取）OSZICAR 最后一个 E0"**。
- **Curvature**：Dimer 的曲率，旋转就是让 Dimer 转到曲率最小方向；在每个平移 Dimer 中 Curvature 应该逐渐下降；在过渡态位置，Dimer 的方向就是反应的方向。
- **Angle**：Dimer 旋转角度，每个平移 Dimer 中也应该逐渐下降。
- 最关键的是 Force、Torque、Curvature 三个量（P151）：旋转过程中 Torque 应不断下降，**否则要用更小的 EDIFF、PREC=Accurate 等方法提高力的计算精度，或者提高 DdR=0.01**；接近过渡态的标志是 **Force 逐渐变小，并且 Curvature 是负值**；Curvature 不是负的说明离过渡态还较远。

**CENTCAR / NEWMODECAR / dimmode.pl（L3 P152）**
- 每一平移 dimer 步都会更新 Dimer 中心的位置和最新的 dimer 方向，输出到 `CENTCAR`、`NEWMODECAR`。
- CENTCAR 格式同 POSCAR/CONTCAR；NEWMODECAR 格式同 MODECAR。
- `dimmode.pl CENTCAR NEWMODECAR 32 0.5` 生成 `dimmode.xyz`（以 CENTCAR 为中心、NEWMODECAR 为振动方向做动画），可用 Jmol、VMD 打开（Jmol 里 Tools–Animate–Loop）。
- **该脚本必须保证 CENTCAR 第一行是元素组成**。

**收敛确认三条命令（L3 P153）**
1. `grep converged OUTCAR` → 出现 `OPT: skip step - force has converged`
2. `grep RMS OUTCAR` → 看 `FORCES: max atom, RMS` 行，最后一个受力 < abs(EDIFFG) 即正常收敛
3. `tail -1 OSZICAR` → 取最后一个 **E0** 作为过渡态能量
   - 讲义示例：`F= -.66261570E+02 E0= -.66258695E+02  d E =-.705902E-05`
- 讲义算例：**207 个离子步，总用时 9620 秒**；且明确说明"我们设置的 EDIFFG=−0.01，发现 DIMCAR 里的 Force 没有到 0.01 就收敛了，**这是正常的**"（P153）。

**NEB + Dimer 组合流程（L3 P164–P167）【讲义给出的高效配方】**
1. 用 CINEB 或 NEB，**EDIFFG = −0.5，EDIFF = 1E-5 做粗收敛**，得到能量最高的结构作为 dimer 计算的初猜（此步参数无严格要求）（P165）
2. 运行 `nebresults.pl`，再运行 `neb2dim.pl (number of an image)`，自动产生一个 `dim` 文件夹，里面保存 dimer 计算所需的输入文件（P165）
3. VTST 提示：在 dim 的 INCAR 里使用 `ICHAIN = 0 / LCLIMB = .TRUE. / IOPT = 1 / IMAGES = 1 / SPRING = -5` 这些参数，**同时要把 CINEB 的参数删除掉**（P166）——【注：P166 这段是"VTST 提示我们"的原话，其意图与 Dimer 实际需要 ICHAIN=2 相冲突，见 §4 C-10】
4. `neb2dim.pl` 不指定 image 时，会自动根据 `exts.dat` 选取能量最高的点作为初始结构（P167）
5. **但讲义说"一般我们不需要用 neb2dim.pl 结构自动产生的 POSCAR 和 MODECAR"**，而是（P167）：
   (1) 手动复制能量最高的 image 的 CONTCAR 到 `dim/POSCAR`；
   (2) 用 `modemake.pl [初态] [dim/POSCAR]` 手动产生 MODECAR；
   (3) 修改准备 dimer 计算的 INCAR 文件。

---

### 3.4 插点方法：nebmake.pl（线性）vs IDPP

**nebmake.pl 线性插值的缺点（L3 P168）**
1. 初始结构远离真实反应路径；
2. 初始结构有非常不合理的键长、键角，甚至原子重叠。
- 适用范围【讲义 P168】：**对于近乎直线的原子扩散问题比较适用**；如果反应路径并非直线，线性插值的点可能距离真正的能量最小路径甚远，需要花更多时间优化。

**实例（L3 P169、P171）**
- 反应：`*C6H11 + *H → C6H10 + H2`
- 用 nebmake.pl 插点时，**(03) image 的 C–H 键距离只有 0.59 Å**，会使初始 CH 原子受力极大，一个离子步之后就偏离了正确的反应路径。
- IDPP 插点后同一位置为 **1.09 Å**（L3 P171）。

**IDPP（L3 P170–P173）**
- 文献：J. Chem. Phys. 140, 214106 (2014)（Image Dependent Pair Potential）
- 思路（L3 P170）：(1) 先线性插值；(2) 定义原子距离的插值；(3) 构造虚拟的势能面，对初始的线性插值结构做 NEB 简单优化；**主要思想是避免插值的 image 结构中某些原子相距太近**。
- 已有实现（L3 P172）：ASE（`https://wiki.fysik.dtu.dk/ase/tutorials/neb/idpp.html`）、pymatgen-diffusion。
- **许楠博士**基于 pymatgen-diffusion 和 pymatgen 两个库开发了 `idpp.py`，"实现了与 nebmake.pl 一样的插点用法"，熟悉 nebmake.pl 的用户可以很快上手（L3 P172）。
- 安装（L3 P173）：`pip install pymatgen pymatgen-diffusion` 或 `conda install pymatgen pymatgen-diffusion`；自测 `import pymatgen` / `import pymatgen_diffusion`。
- 用法（L3 P173）：`python3 ~/bin/idpp.py POSCARis POSCARfs 4` → 得到 `00 ~ 05` 共 6 个文件夹。
- 疑难体系用法（L3 P155）：`python3 ~/bin/idpp.py POSCARis POSCARfs 1`。

**仓库内真实脚本 `things to study\idpp.py`（31 行）** —— 与讲义说法一致的细节：
```python
from pymatgen.core import Structure
from pymatgen_diffusion.neb.pathfinder import IDPPSolver
import numpy as np, os, sys
...
obj = IDPPSolver.from_endpoints(endpoints=[init_struct, final_struct], nimages=int(sys.argv[3]),
                                sort_tol=1.0)
new_path = obj.run(maxiter=5000, tol=1e-5, gtol=1e-3, step_size=0.05,
                   max_disp=0.05, spring_const=5.0)
```
- 参数（讲义未提，脚本里写死）：`sort_tol=1.0`、`maxiter=5000`、`tol=1e-5`、`gtol=1e-3`、`step_size=0.05`、`max_disp=0.05`、`spring_const=5.0`。
- 参数个数检查：`if len(sys.argv) < 4: raise SystemError('Sytax Error! Run as python idpp.py ini/POSCAR fin/POSCAR 4')`。
- 脚本开头把 `sys.stdout` 重定向到 `os.devnull`，结尾再恢复并 `print("Improved interpolation of NEB initial guess has been generated. BYE.")`。
- 输出目录名格式 `'{0:02d}'.format(i)`，文件名固定为 `POSCAR`，用 pymatgen 的 `to(fmt="poscar")` 写出。
- **推论**：因为 IDPPSolver 的输入含两个端点，`nimages=4` 时输出 0..5 共 6 个文件夹（端点 + 4 个中间像），与讲义 P173 的"00~05 一个 6 个文件夹"一致；这与 `IMAGES = 4` 的 VASP 语义（4 个中间像 + 2 个端点 = 6 个文件夹）也一致。

---

### 3.5 频率计算与虚频

**为什么必须算频率（L3 P25）**
- "我们计算的结构优化和过渡态搜索任务只能保证得到的结构是驻点，即能量的一阶导数（原子受力）为零，还要进一步计算频率来确定虚频的个数。"
- 一般计算频率都用**谐振子模型**，只需要能量的二阶导数。

**频率与结构优化必须同级别（L3 P26）**
- "优化和振动分析必须在相同级别下进行"，因为级别（格点精度、溶剂模型、泛函、vdW 校正等）不同相当于振动分析不是在势能面的极小点位置进行，结果没有意义。
- **频率计算对 SCF 收敛/力精度要求更高**：
  - 结构优化：`EDIFF = 1E-5` 到 `1E-7` 皆可
  - **频率计算：`EDIFF = 1E-7`**（L3 P26，P30 重复）

**有限位移法（L3 P28）**
- 在 3N 个自由度上每个自由度做两次微调结构计算，求频率的数值解；**单独 VASP 只计算 Γ 点的振动频率，必须结合 phonopy 才能计算声子谱**。
- 每个自由度位移**两次（NFREE = 2）或四次（NFREE = 4）**。
- 表面吸附体系如果 slab 原子不参与化学反应，**可以把 slab 模型都固定住，只允许吸附原子振动**。
- 讲义明确："对于表面吸附分子，由于难以计算平动能和转动能，所以可以近似的认为分子平动转动的贡献耦合到了这 6 个振动中，故可以按照 3N 计算分子的振动能量"（L3 P24）。

**频率计算的 INCAR（L3 P30）【讲义原文】**
```
#### initial I/O ####
SYSTEM = Au
KPAR = 4
NCORE = 5
ISTART = 1
ICHARG = 1
LWAVE = .TRUE.
LCHARG = .TRUE.
LVTOT = .FALSE.
LVHAR = .FALSE.
LELF = .FALSE.
#### Electronic Relax ####
ENCUT = 400
ISMEAR = 1
SIGMA = 0.2
EDIFF = 1E-7
NELMIN = 5
NELM = 300
GGA = PE
LREAL = Auto
LDIPOL = .TRUE.
IDIPOL = 3
ISYM = 0
#### Geo opt ####
EDIFFG = -0.01
IBRION = 5
POTIM = 0.015
NSW = 300
ISIF = 2
NFREE = 2
```
讲义逐条：
1. `EDIFF = 1E-7`，"和过渡态计算一样频率计算也需要很高的力精度"
2. `IBRION = 5`，计算 Hessian 矩阵、能量对坐标的二阶导数和频率
3. `NFREE = 2`，"原子在每个方向上的位移次数，详见 INCAR 手册"
4. **"NSW 和 EDIFFG 都不用设置或取任意值。NSW 不能取 0"** —— 但同页列出的 INCAR 里**同时写了 `EDIFFG = -0.01` 和 `NSW = 300`**（见 §4 C-2）
5. `POTIM = 0.015`（"当 IBRION = 5 或 6 时的默认值"）—— **这是 L3 全文唯一一次提到 IBRION=6**

**前置处理：重新固定原子（L3 P29）**
```
vaspkit
403
1
0 0.48
cp POSCAR_fix POSCAR
```
- 做法：新建 `freq` 文件夹，复制过渡态计算的最终结构为 `POSCAR`；用 vaspkit 403 把 **O 原子以下**的原子都固定住；`0.48` 是分数坐标 z 的阈值。
- **推论**：与算例对照可确认这个阈值用法——`things to study\day3\ts\dim\POSCAR` 中 O 的分数 z = 0.48812，而 20 个 Au 的最大分数 z = 0.43488，用 0.48 作阈值刚好只放开 O。

**离子步数是固定的（L3 P31）**
- 【讲义原文】"频率计算的离子步数是固定的，= 6×[放开的原子数] + 1。比如我们的例子只放开了一个原子，那么 N = 6×1+1 = 7"。
- 检查输出的命令：`grep -3 Finite OUTCAR`，输出形如：
  ```
  Finite differences progress:
  Degree of freedom:   1/  3
  Displacement:        1/  2
  Total:               1/  6
  ```
- 【讲义原文】"Degree of freedom 是体系中的自由度 3N，Displacement 是 NFREE 的位移次数 2，Total = [Degree of freedom] × [Displacement] = 6"。
- **推论（与算例核对后判定讲义此处措辞不准）**：本例体系有 21 个原子，3N = 63，但输出是 `1/3`，所以这里的 "Degree of freedom" 其实是 **3 ×（放开的原子数）**，不是整个体系的 3N。依据：`4-thermo\7-4-Au-O-freq\ts\OUTCAR`（21 原子、只放开 1 个 O）显示 `3/3`；同目录 `o2\OUTCAR`（2 原子、全部放开）显示 `6/6`。两条都与 "3 × 放开原子数" 相符。
- 配套结论：**实际离子步数 = 3 × 放开原子数 × NFREE + 1**；`NFREE=2` 时即讲义 P31 的 "6×[放开的原子数]+1"。

**怎么读频率输出（L3 P32、P33、P37）**
- `OUTCAR` 最后一部分是**对角化力常数矩阵的本征值和本征矢，一共有 3N 个**（P32）。
- 每行格式（P32 原文示例）：
  ```
  1 f  =   12.609563 THz    79.228223 2PiTHz  420.609746 cm-1    52.148981 meV
  ```
  讲义说明："第一行是振动的能量不同的单位，一般我们用 cm-1，最后这个 52.148981 meV 是 hν 的值，**hν/2 是零点振动能 ZPE，求 zpe 可以直接读这个能量除以 2**"。
- 接着是原子坐标和对应振动方向（dx dy dz）；只放开一个 O 原子时只有该原子有值（P32）。
- 查虚频的命令：`grep cm OUTCAR`（P33）。
- 结果解读（P33 原文）："其中 f 是实频，**f/i 代表虚频**，这里说明我们计算的过渡态有**一个虚频，振动频率大约 132 cm-1**。**一般过渡态的虚频都 > ~100 cm-1，如果虚频太小，则过渡态可能找的不对，需要看振动方向检查一下**。"
- OUTCAR 可以用 Jmol 打开看振动模式（Tools – atom set chooser）（P33）。
- 气态分子（H2O）示例（P36、P37）："VASP 算出的分子的频率有 3N 个。实际上其中有 6 个是属于平动和转动在振动自由度上的投影，**这最小的 6 个频率中可能出现虚频，这些频率可以直接无视**"；"得到前 3N−6 个频率是我们关心的"。
- **推论（由讲义内三个实例的输出顺序归纳）**：VASP 5.4.4 打印频率的顺序是 **实频按由大到小、虚频（f/i）排在最后并按由小到大**。依据：P32/P33 的 Au–O 体系（12.609 → 12.052 → f/i 3.964）、P37 的 H2O（114.81, 111.39, 47.51, 1.910, 1.795, 0.244, 然后 f/i 0.182, 0.265, 1.836）、P71 的 O2（46.98, 1.953, 1.121, 然后 f/i 0.00698, 1.046, 1.294）。因此 P37 的"前 3N−6 个"这个说法**依赖输出顺序，不能当成通用规则**（见 §4 C-8）。

**几个虚频才算对**
- 极小点（IS/FS）：**没有虚频**（L3 P157 反面表述："如果没有虚频，那计算肯定是错的"是针对过渡态说的）。
- 过渡态：**恰好一个虚频**（L3 P33"有一个虚频"；L3 P140 流程图"频率计算验证一个虚频"；L3 P157 问题(4)"没有虚频或者有两个以上的虚频"都算失败）。
- 讲义给出的量化门槛：**过渡态虚频一般 > ~100 cm⁻¹**（L3 P33）。
- 振动方向的检查方法：OUTCAR 用 Jmol 看（P33）；Dimer 用 `dimmode.pl CENTCAR NEWMODECAR 32 0.5` 生成 `dimmode.xyz`（P152）。

**ZPE 与热力学量中的频率处理**
- ZPE = ½ Σᵢ hνᵢ（L3 P52）；"计算出的能量不是体系在 0K 下的能量，而是体系在 0K 下并且忽略 ZPE 的能量"（L3 P52）。
- 频率越大对 ZPE 贡献越大（H2 伸缩振动 4395 cm⁻¹，所以 H2 参与的反应 ZPE 校正非常大）（L3 P53）。
- 频率越小对 ZPE 贡献越小，但对 qvib 贡献越大，对升温造成的熵增贡献越大（L3 P54）。
- **低频振动处理**：做表面吸附分子自由能校正时，平动转动 6 自由度被限制转为振动，很可能出现小的振动频率使校正出的自由能异常低，"所以有的文献建议做表面吸附分子的自由能校正的时候，**把频率在 50 cm⁻¹ 以下的贡献都算成是 50 cm⁻¹**"（L3 P55）；L3 P64 又说"一般把做法是把频率过小的熵当作 **50 cm⁻¹ 或 60 cm⁻¹** 计算"。
- **P61 的 ZPE 读法**："ZPE 是计算频率 grep cm OUTCAR，取最后**一排** meV 的能量和，再除以 2000"。**推论**：机械地"把所有 meV 求和除以 2000"在分子/含虚频的体系会算错（见 §4 C-3）。

**关于 IBRION = 6 / 7 / 8 与 DYNMAT 的覆盖情况（重要，避免误引）**
- L3 全文检索结果（我已按行核对）：
  - `IBRION` 共出现 11 处，取值只有 **3**（过渡态）和 **5**（频率），另有一处文字提到 "IBRION = 5 或 6 时的默认值"（P30）。
  - **`IBRION = 6` 只在 P30 的这一句里被提到，没有任何用法说明；`IBRION = 7`、`IBRION = 8` 在 L3 全文中一次都没有出现。**
  - **`DYNMAT` 在 L3 全文中出现 0 次**；讲义也没有讲怎么读 DYNMAT 文件。
- 旁证（同一课程的其他算例，非 L3 正文）：`things to study\线上中级班-催化资料\4-thermo\7-5-IRspectrum\INCAR` 用的是 `IBRION = 7`、`NFREE = 2`、`POTIM = 0.015`、`NSW = 1`、`LEPSILON = .TRUE.`、`NWRITE = 3`，`SYSTEM = ethanol`，配套有 `spectra.dat`、`ir.sh`、`ir_6.sh`、`spectra.exe`，是红外光谱（IR）流程。
- 在 `things to study` 下全部 `INCAR` / `INCAR.bak` 中，`IBRION` 只出现 **2、3、5、7** 四个取值；**没有 6，也没有 8**。
- **因此：本讲义（L3）只覆盖 IBRION=5 的有限位移频率计算；IBRION=6/8、DYNMAT 的读法在本资料范围内无依据，标记 `[来源待核对]`，不得据 L3 写成断言。**

---

### 3.6 判据与阈值汇总（含适用范围）

| 量 | 讲义取值 | 页码 | 适用范围 / 备注 |
|---|---|---|---|
| 结构优化 `EDIFF` | 1E-5 ~ 1E-7 皆可 | L3 P26 | 一般几何优化 |
| 频率计算 `EDIFF` | **1E-7** | L3 P26、P30 | 振动分析；频率对力精度要求更高 |
| 过渡态 `EDIFF` | **1E-7**（关键）；粗收敛可放宽到 1E-5 | L3 P129、P146、P165 | CI-NEB 与 Dimer 都要求；理由是"力的精度不够"是 TS 不收敛主因 |
| 过渡态 `EDIFFG` | 模板写 **−0.03**；难收敛体系放宽到 **−0.05** | L3 P129、P147 | 讲义模板值 |
| 过渡态 `EDIFFG`（讲义自述算例实际值） | **−0.01** | L3 P153 | 与模板不一致，见 §4 C-1 |
| NEB+Dimer 组合的粗收敛 | `EDIFFG = −0.5`、`EDIFF = 1E-5` | L3 P165 | 仅用于"粗收敛拿初猜"，此步参数无严格要求 |
| 频率计算 `POTIM` | **0.015** | L3 P30 | IBRION=5 或 6 时的默认值 |
| 过渡态 `POTIM` | **0** | L3 P129、P131、P146、P147 | 与 `IBRION = 3` 搭配是 VTST 生效的标志 |
| `IBRION = 3` + `IOPT = 0` 的退路 | `IBRION = 1, POTIM = 0.1` | L3 P129、P146 | 讲义原话 |
| 频率 `NFREE` | 2 或 4；算例用 2 | L3 P28、P30 | 有限位移法位移次数 |
| 频率计算离子步数 | 6×放开原子数 + 1（NFREE=2 时） | L3 P31 | **推论**：通用式为 3×放开原子数×NFREE + 1 |
| 过渡态虚频 | 一般 **> ~100 cm⁻¹**；太小说明 TS 可能不对 | L3 P33 | 表面吸附体系经验值 |
| 过渡态虚频个数 | **恰好 1 个** | L3 P33、P140、P157 | 0 个或多于 1 个都算失败 |
| 低频截断 | **< 50 cm⁻¹ 按 50 cm⁻¹ 计**（P64 另说 50 或 60） | L3 P55、P64 | 只用于**表面吸附分子**的自由能校正 |
| `dist.pl` 判据 | 返回值 **< 5 Å** 可进行下一步 | L3 P125 | CI-NEB 前置检查；太大要检查原子顺序 |
| 插点数目 | **≈ dist.pl 返回值 / 0.8** | L3 P126 | 经验规则；同页又说本例只需 1 个点 |
| CI-NEB 插点总数建议 | 含初末态 **3 ~ 5 个点**足够；"越多越好"是错的 | L3 P124 | 讲师的明确态度 |
| 并行约束 | 核数必须整除插点数量 | L3 P132 | CI-NEB 专有 |
| `SPRING` | **−5**（默认） | L3 P131、P160 | CI-NEB 弹簧常数 |
| `IMAGES` | CI-NEB 用 1（Au 算例）/ 4（环己烷算例） | L3 P131、P160 | 两个算例对照 |
| `IOPT` | 1、2 精收敛；7 粗收敛 | L3 P130 | CI-NEB 用 1；Dimer 模板用 2；难体系用 7 |
| `DdR` | 注释值 5E-3；P151 处方里写 0.01 | L3 P147、P151 | Dimer 间距；两处数值不一致 |

---

### 3.7 常见失败模式与讲师处方（L3 P154–P158，共 5 条）

| # | 现象 | 讲师处方 | 页码 |
|---|---|---|---|
| 1 | CINEB 计算得到的**中间点能量比初态和末态都要低** | 两种可能：① IS 与 FS 之间还存在至少一个极小点；② **初态和末态本就不是极小点**，需要用更严格的精度重新继续计算初态和末态 | L3 P154 |
| 2 | CINEB 一开始就出现**极大的原子受力（比如 10 eV/Å 以上）** | 原因肯定是**初始结构不合理**：改用非线性插点（`idpp.py` 脚本），或者把不合理的 POSCAR 下载下来人工调整 | L3 P155 |
| 3 | **已接近收敛，但很久力不能达到收敛标准** | 两个原因：① 力的精度不够 → `PREC=Accurate`、`EDIFF=1E-7`；② 优化算法不合适 → 尝试 `IOPT=7`，或 `IOPT=0`（用 VASP 自带的 DIIS 优化）；也可能是**力的收敛标准过于严格** | L3 P156 |
| 4 | **过渡态收敛了，但算频率时没有虚频，或有两个以上虚频** | 没有虚频：计算肯定是错的，最可能还是力的精度不够。多个虚频：也可能是力精度不够 → `EDIFF = 1E-7` 严格化，**或换用 Dimer 方法** | L3 P157 |
| 5 | **nebmake.pl 插点结构非常混乱** | 检查初态和末态的**原子顺序是不是一一对应**；这是新手常见错误，**在计算初末态的时候就要注意不要打乱相应的原子顺序** | L3 P158 |

补充的收敛/稳定性处方散落在别处：
- Dimer 旋转中 Torque 不下降 → 用更小的 EDIFF、`PREC=Accurate`，或提高 `DdR=0.01`（L3 P151）
- Curvature 不是负值 → 说明离过渡态还较远，耐心等待（L3 P151）
- Dimer 计算中出现严重不合理的结构偏离 → 杀掉任务重新调整初始构型（L3 P148）
- 过渡态初猜：保证没有过短的键（L3 P143）
- 答疑稿补充：CI-NEB 结果里"**能量出现下降是不对的**"（D3-P34）；频率"**只算能量最高的点即可**"（D3-P34）

---

### 3.8 与真实算例的交叉核对

核对对象：
- `things to study\day3\`（Dimer / NEB / IDPP 算例）
- `things to study\线上中级班-催化资料\5-ts\`（O/Au(111) 与 环己烷/Pt1-graphene 的 TS 算例）
- `things to study\线上中级班-催化资料\4-thermo\`（频率与热力学算例）

#### 3.8.1 完全对得上的部分（讲义数据 = 算例数据）

| 内容 | 讲义 | 算例文件 | 结论 |
|---|---|---|---|
| Au–O 过渡态频率 | L3 P32 `1 f = 12.609563 THz 79.228223 2PiTHz 420.609746 cm-1 52.148981 meV`；P33 `3 f/i= 3.964289 THz … 132.234445 cm-1 16.394988 meV` | `4-thermo\7-4-Au-O-freq\ts\OUTCAR` 三行**逐字符相同** | 完全一致 |
| IS / FS 频率 | L3 P35：IS 363.75/361.16/358.64；FS 346.224065/335.310174/333.824346 cm⁻¹ | `7-4-Au-O-freq\is\OUTCAR`、`fs\OUTCAR` 完全相同 | 完全一致 |
| O2 的 6 个频率 | L3 P71 的 6 行 | `7-4-Au-O-freq\o2\OUTCAR` 6 行逐字符相同（1567.082879 cm⁻¹ / 194.293584 meV 等） | 完全一致 |
| Dimer 算例的离子步数与末行 | L3 P153 "经过 207 个离子步"；`F= -.66261570E+02 E0= -.66258695E+02  d E =-.705902E-05` | `5-ts\8-1-ex1-O-Au\ts-dimer\OSZICAR`：**207** 条 `F=` 行；末行**逐字符相同** | 完全一致 |
| Dimer INCAR（Au） | L3 P147 的 INCAR 全文 | `5-ts\8-1-ex1-O-Au\ts-dimer\INCAR`：`SYSTEM=Au`、`NCORE=16`、`ENCUT=400`、`ISMEAR=1`、`SIGMA=0.2`、`EDIFF=1E-7`、`NELMIN=5`、`NELM=300`、`GGA=PE`、`LREAL=Auto`、`LDIPOL/IDIPOL=3`、`ISYM=0`、`EDIFFG=-0.01`、`IBRION=3`、`POTIM=0`、`NSW=300`、`ISIF=2`、`IOPT=2`、`ICHAIN=2`，`DdR/DRotMax/DFNMin/DFNMax` 均被注释 | 标签集合完全一致；`EDIFFG` 与并行标签不同（见 3.8.2） |
| CI-NEB INCAR（Au） | L3 P131 的 INCAR | `5-ts\8-1-ex1-O-Au\ts-cineb\INCAR`：`ICHAIN=0`、`LCLIMB=.TRUE.`、`IOPT=1`、`IMAGES=1`、`SPRING=-5` | 完全一致（`EDIFFG` 见 3.8.2） |
| CI-NEB 生成 00/01/02 三个文件夹 | L3 P126 | `5-ts\8-1-ex1-O-Au\ts-cineb\` 下确有 `00/`、`01/`、`02/` | 完全一致 |
| 收敛判据"所有插点最大受力 < abs(EDIFFG)" | L3 P133 | `5-ts\8-1-ex2...\nebef.dat`：6 行最大受力 0.009926 / 0.019729 / 0.028569 / 0.018706 / 0.018991 / 0.009783，**全部 < 0.03 = abs(EDIFFG)** | 完全一致 |
| 环己烷算例的 CINEB INCAR | L3 P160：`ICHAIN=0`、`LCLIMB=.TRUE.`、`IOPT=7`、`IMAGES=4`、`SPRING=-5`、`IVDW=11`、`EDIFFG=-0.03`、`IBRION=3`、`POTIM=0`、`NSW=1000`、`ISIF=2`、`ENCUT=400`、`ISMEAR=0`、`SIGMA=0.05`、`EDIFF=1E-6`、`ISPIN=2` | `5-ts\8-1-ex2c6h12ptgraphene\c6h12ptgraphene\INCAR` 中上述**每一个标签的取值都相同** | 完全一致（`SYSTEM`/`NCORE` 例外，见 3.8.2） |
| **0.59 Å vs 1.09 Å**（讲义最强调的一个对比） | L3 P169：nebmake.pl 的 (03) image 的 C–H 只有 **0.59 Å**；L3 P171：IDPP 为 **1.09 Å** | 我逐像计算最短 C–H：`day3\idpp\c6h12-nebmake\03\POSCAR` = **0.5916 Å**；`day3\idpp\c6h12-idpp\03\POSCAR` = **1.0879 Å**（同样的对比在 01/02/04 上分别是 0.8011/0.5947/0.7942 vs 1.0908/1.0879/1.0883） | **算例精确复现了讲义的核心论断** |
| 反应式 `*C6H11 + *H → C6H10 + H2` | L3 P169 | `day3\idpp\*\05\POSCAR` 中最短 H–H = **0.7528 Å**（即生成了 H2），IS（00）中最短 H–H = 1.7685 Å | 一致，产物确实成 H2 |
| 固定的原子与 vaspkit 403 阈值 | L3 P29 用 `0 0.48` 固定 O 以下原子 | `day3\ts\dim\POSCAR` 有 `Selective dynamics`，20 个 Au 全 `F F F`（最大分数 z = 0.43488），O 为 `T T T`（分数 z = 0.48812） | 与 `0.48` 阈值精确吻合 |
| MODECAR 的行数与主分量 | L3 P145：逐原子一行、每行 3 个数、最后一行是主分量 | `day3\ts\dim\MODECAR` 共 **21 行** = 21 个原子；最后一行 `-1.5692019662E-02  -9.6340592504E-01  -2.6975265185E-02`（主分量在 z，对应 O 原子） | 格式与"末行为主分量"一致 |

#### 3.8.2 讲义 vs 算例：不一致清单（单列）

| # | 位置 | 讲义怎么说 | 算例里实际写的是什么 | 我的判断与依据 |
|---|---|---|---|---|
| X-1 | CI-NEB 模板 `EDIFFG` | L3 P129 与 P131 都写 `EDIFFG = -0.03`；P147 Dimer 模板也写 `-0.03` | `5-ts\8-1-ex1-O-Au\ts-cineb\INCAR` = `-0.01`；`ts-dimer\INCAR` = `-0.01`；`day3\ts\dim\INCAR` = `-0.01`；`8-1-ex2...\INCAR` = `-0.03` | **讲义模板与三个真实算例不一致**；而且 L3 P153 自述"我们设置的 EDIFFG=−0.01"，与模板自相矛盾。8-1-ex2 是唯一与讲义模板一致的算例。见 §4 C-1 |
| X-2 | 环己烷算例的 `SYSTEM` / `NCORE` | L3 P160：`SYSTEM = Pt`、`NCORE = 10` | `INCAR`：`SYSTEM = MoS2`、`NCORE = 8`；`INCAR.bak`：`SYSTEM = MoS2`、`NCORE = 10` | `NCORE=10` 来自 `INCAR.bak`；**`SYSTEM = Pt` 在两个文件里都不存在**（两处都是 `SYSTEM = MoS2`，明显是模板残留）。讲义里的 Pt 是人为改的/笔误 |
| X-3 | CI-NEB/Dimer 的并行标签 | L3 P30/P131 模板写 `KPAR = 4`、`NCORE = 5` | Au 的算例：`#KPAR = 4`（被注释）、`NCORE = 16`；Pt/graphene 算例：`# KPAR = 4`（被注释）、`NCORE = 8`（或 .bak 的 10） | 模板与实际算例在并行标签上系统性地不同；报告只记录 INCAR 里的取值差异，不涉及任何机器信息 |
| X-4 | CI-NEB 收敛步数 | L3 P133："此例算 **14 步**就收敛了" | `5-ts\8-1-ex1-O-Au\ts-cineb\01\OSZICAR` 中 `F=` 行数 = **13**；`neb.dat` 也只有 3 行（00/01/02） | 差 1 步。**不确定**是讲义把第 0 步也计入，还是另有版本。列为待核对（§5） |
| X-5 | `neb.dat` 的 image 1 能量 | L3 P134 的 nebresults.pl 输出：image 0/1/2 相对能量 = 0 / **0.494200** / 0.268400 | `5-ts\8-1-ex1-O-Au\ts-cineb\neb.dat`：0 / **0.498031** / 0.268417 | image 2 对得上（0.268400 vs 0.268417），image 1 差 **3.8 meV**。用同一算例的 OSZICAR E0 反算（−66.256661 − (−66.750879) = 0.494218）与讲义一致而与 neb.dat 不一致。**不确定** neb.dat 第 3 列到底取自哪个量。列为待核对（§5） |
| X-6 | `day3\ts\05` 与 `day3\ts-neb\00` 里的 OUTCAR | 讲义 P129–P153 描述的过渡态计算应该用 `IBRION=3, POTIM=0, EDIFF=1E-7, EDIFFG=-0.03/-0.01, ICHAIN=0/2` | 这两个 `OUTCAR.gz` 解压后回显的是 `IBRION = 2`、`POTIM = 0.2000`、`EDIFF = 0.1E-05`、`EDIFFG = -.1E-01`、`NFREE = 1`、`NSW = 300`、`ICH(A)IN = 0` —— 是**普通 CG 几何优化**，不是 Dimer/NEB 计算 | 这两份 OUTCAR **不能用来核对讲义的 TS 工作流**。要核对 TS 请用 `5-ts\8-1-ex1-O-Au\`（CINEB 与 Dimer 各一套） |
| X-7 | `day3\ts-neb\00\OUTCAR.gz` 与同目录 POSCAR 的对应关系 | 按 CINEB 流程（P127），00 里应放 IS 的 OUTCAR/CONTCAR | 该 OUTCAR 里唯一的"position of ions in fractional coordinates"块（即输入结构）中 O = (0.63251, 0.32403, 0.49211)，而同目录 `POSCAR` 的 O = (0.66372, 0.33233, 0.47798)，**分数坐标差约 0.03**（≈0.18 Å） | 该 OUTCAR 不是从这份 POSCAR 起算的。**推论**：OUTCAR 是"未弛豫初猜 → 弛豫"的那次计算，而 `00/POSCAR` 已是弛豫后的 `is/CONTCAR`。列为待核对 |
| X-8 | `day3\idpp\` 下的目录名与内容 | 讲义把 `nebmake.pl` 与 `idpp.py` 当作两种插点方法对比（P168–P173） | 我算了 MD5：`day3\idpp\nebmake\02,03,04,05\POSCAR` 与 `day3\idpp\c6h12-idpp\02,03,04,05\POSCAR` **逐字节相同**（同一 MD5）；而 `day3\idpp\c6h12-nebmake\02,03\POSCAR` 最短 C–H 是 0.5947/0.5916 Å（线性插值特征）。`nebmake\01` 最短 C–H = 1.0937 Å（IDPP 特征） | **目录名与内容不符**：名为 `nebmake` 的目录装的是 **IDPP 的结果**（00–05 全套），名为 `c6h12-nebmake` 的目录才是 **nebmake.pl 线性插值**的结果，`c6h12-idpp` 只是同一 IDPP 运行中 02–05 的副本。**推论**（依据是 MD5 相同 + 几何指标一致）。这一点如不澄清会误导使用者 |
| X-9 | `day3\idpp\c6h12-idpp\` 的完整性 | 讲义 P173：idpp.py 产出 `00~05` 共 6 个文件夹 | `c6h12-idpp\` 只有 `02,03,04,05`（缺 `00,01`）；`day3\idpp\nebmake\` 才有完整 00–05 | 与 X-8 同一件事的两面 |
| X-10 | `8-1-ex2c6h12ptgraphene` 里 `POSCARis` / `POSCARfs` 与 NEB 端点的对应 | 按 P126 流程，`POSCARis`/`POSCARfs` 应分别等于 `00/` 与 `05/` 里的结构 | 我做了逐原子比对：**顶层 `POSCARis` 与 `c6h12ptgraphene\POSCARfs` 逐原子完全相同（最大偏差 0.000000 Å）**；而顶层 `POSCARfs`（最短 H–H = 0.7528 Å，已生成 H2）与 `c6h12ptgraphene\05\POSCAR` **不同**（最大偏差 12.31 Å） | 归档文件的命名有歧义：真正被 NEB 使用的 FS 是 `c6h12ptgraphene\POSCARfs`（它等于顶层 `POSCARis`），而顶层 `POSCARfs` 是另一个含 H2 的结构。**推论**：直接照搬顶层文件名会配错端点。已列为待核对（§5） |
| X-11 | 该 NEB 结果的物理合理性 | 讲义 P154 问题(1)说"CINEB 计算得到的中间点能量比初态和末态都要低"；D3-P34 说"能量出现下降是不对的" | `8-1-ex2...\nebef.dat` 的能量剖面是 0 → 0.2105 → 0.1670 → 0.6399 → 0.6586 → **0.5078**（末态比初态高 **0.508 eV**）；`exts.dat` 拟合出 7 个极值点（1.12/0.2151、1.86/0.1610、2.99/0.6400、3.06/0.6393、3.78/0.6680） | 这是一个**强吸热**基元步且路径上有多个极值。**不能据此判定计算错误**（C–H 活化本身可以吸热）；但结合 X-10（端点可疑），这份结果使用前必须重新确认 IS/FS。讲义 P162 也提醒"拟合出来的极值点不一定是真实存在的" |
| X-12 | 该 NEB 的反应坐标距离 | 讲义 P126 说 nebmake.pl 是**线性**插值（各段距离应大致相等） | 由 POSCAR 算的逐段 sqrt(Σd²)：00→01 1.8598、01→02 1.8598、02→03 1.8598、03→04 1.8598、04→05 1.8599 Å（**完全等距 → 确认是线性插值**）；但 `neb.dat` 第 2 列给出 0 / 5.299 / 10.597 / 15.897 / 21.196 / **46.003** | 输入的确是线性插值；neb.dat 的 46.00 是**弛豫后**的量，末段 24.8 Å 远大于前四段的 ~5.30 Å。我实测 `04/CONTCAR → 05/POSCAR` 的 sqrt(Σd²) = **26.68 Å**（`02/CONTCAR → 03/CONTCAR` 也有 13.32 Å） | 说明弛豫过程中 image 04（及 03）跑得离路径很远。**结论**：neb.dat 的距离列反映的是弛豫后的实际构型，不是插值距离；解读时不能当成反应坐标的线性刻度。列为待核对 |
| X-13 | `8-1-ex1-O-Au\ts-dimer\` 的 DIMCAR | L3 P149/P150/P151 用大段篇幅讲 DIMCAR 的 Step/Force/Torque/Energy/Curvature/Angle | `ts-dimer\` 目录下**没有 DIMCAR 文件**（只有 CENTCAR、CONTCAR、INCAR、KPOINTS、MODECAR、NEWMODECAR、OSZICAR、POSCAR） | 讲义 P149 的 DIMCAR 表格**无法用这套归档算例核对**。列为待核对 |
| X-14 | Dimer 的 `MODECAR` 与 `NEWMODECAR` 是否只作用在被放开的原子上 | L3 P144/P145 没提这个限制 | `5-ts\8-1-ex1-O-Au\ts-dimer\MODECAR` 末行 `2.4199310346E-01 9.3308559935E-01 1.6190951779E-01`（主分量在 y），与 L3 P145 展示的示例完全相同 → **讲义 P145 的 MODECAR 片段确实来自这套算例** | 一致，可交叉引用 |
| X-15 | `day3\ts\dim\MODECAR` 与 `POSCAR` 的一致性 | 讲义 P29 的做法是"把 O 以下原子都固定住"，只放开吸附原子 | `day3\ts\dim\POSCAR` 中 20 个 Au 全是 `F F F`（固定），但 `MODECAR` 里 Au 对应的行**有可观数值**（如第 5 行 −1.7874036818E-01、第 20 行 +1.2108268966E-01） | **推论**：这份 MODECAR 是由未加 Selective dynamics 的 IS/FS 相减得到的（modemake.pl 对所有原子都算），与后来固定的 POSCAR 不完全匹配。VASP 会忽略固定原子上的力，所以不致命，但使用者应知道两者不是同一次约束下产生的。列为待核对 |
| X-16 | `day3\ts\dim\POSCAR` 的文件完整性 | 讲义没有相关说明 | 该 POSCAR 第 10–30 行是 21 个原子坐标，**第 32–52 行是 21 行 `NaN NaN NaN`** | 文件尾部多了 21 行 NaN（原子数那么多行，疑似速度/预测块被写成 NaN）。**推论**：转换工具产生的残留；VASP 读到额外行会有风险，入库前应清理。列为待核对 |
| X-17 | 频率计算的 `NSW` | L3 P30 写 `NSW = 300`，并说"NSW 和 EDIFFG 都不用设置或取任意值。NSW 不能取 0" | `7-4-Au-O-freq\ts\OUTCAR` 回显 `NSW = 289`（21 原子、放开 1 个）；`o2\OUTCAR` 回显 `NSW = 61`（2 原子全放开）；但两者 OSZICAR 的 `F=` 行数分别是 **7** 和 **13**（= 3×放开原子数×NFREE+1） | INCAR 写 300，OUTCAR 回显却是 289/61 —— 说明 VASP 在 IBRION=5 下**会改写 NSW**。**回显值的计算公式我不确定**（289 与 61 都不是 3×N_free×NFREE+1）。列为待核对（§5） |
| X-18 | `NFREE` 在 OUTCAR 里的标签 | L3 P30："NFREE = 2，原子在每个方向上的位移次数" | `7-4-Au-O-freq\*\OUTCAR` 里回显为 `NFREE  =      2    steps in history (QN), initial steepest desc. (CG)` | VASP 复用了同一个标签名，OUTCAR 的说明文字是给 IBRION=2 用的，**看 OUTCAR 回显会被误导**。这解释了为什么 `day3\ts\05\OUTCAR`（IBRION=2）回显 `NFREE = 1` |

#### 3.8.3 其他可用的真实算例（讲义未展开，但对决策库有价值）

- `things to study\线上中级班-催化资料\5-ts\8-1-ex1-O-Au\` 是**唯一一套同时含 CI-NEB 与 Dimer 的完整 Au(111) O 迁移算例**：
  - `is\`：IS 弛豫（`IBRION=2, POTIM=0.2, EDIFFG=-0.01, EDIFF=1E-6`），OSZICAR 末行 `F=-66.752468, E0=-66.750879`
  - `fs\`：FS 弛豫，33 离子步，`F=-66.486971, E0=-66.482462`
  - `ts-cineb\`：3 个文件夹（00/01/02）、`IMAGES=1`、`IOPT=1`，image 01 用 **13** 个离子步收敛，`E0=-66.256661`；产物含 `nebef.pl` 系列后处理产物（`neb.dat`、`mep.eps`、`movie.xyz`、`vaspout1.eps`）
  - `ts-dimer\`：207 离子步，`E0=-66.258695`
  - **推论**：两种方法给出的 TS 能量相差 −66.256661 vs −66.258695 = **2.0 meV**，彼此吻合得很好 —— 这是"两种方法可以互相验证"的一个直接证据。`[来源待核对]`（此比较是我算的，讲义没有做这个对比）
- `8-1-ex2c6h12ptgraphene\c6h12ptgraphene\` 提供 `neb.dat`、`nebef.dat`、`exts.dat`、`spline.dat`、`mep.eps`、`movie.vasp`、`movie.xyz`、`vaspgr\vaspout1..4.eps` —— **这是核对 `nebresults.pl` 全部产物清单（L3 P135）的最好样本**，且证实了四个 `vaspgr` 图（对应 4 个 image）。
- `KPOINTS` 对照：`day3\ts\dim\KPOINTS` 是 `Gamma / 5 5 1`；`5-ts\8-1-ex1-O-Au\ts-cineb\KPOINTS` 是 `G / 7 7 1`（5 行详版格式）。讲义正文没有给过渡态算例的 KPOINTS 取值。

---

## §4 冲突与错误日志

格式：`位置 | 原文怎么说 | 问题是什么 | 我的判断与依据`。
**本节只记录，不裁定；不确定的一律写明"不确定"。**

### 4.1 讲义内部前后不一致

**C-1｜`EDIFFG` 模板值与讲义自述的实际值打架**
- 位置：L3 P129、L3 P131、L3 P147 vs L3 P153
- 原文：P129 "（2）EDIFFG = -0.03，过渡态可以适当放宽结构优化的收敛精度到 -0.03，对于非常复杂难以收敛的体系可以放宽到 -0.05"；P131/P147 的 INCAR 全文也都写 `EDIFFG = -0.03`。但 P153 说"**注意：我们设置的 EDIFFG=-0.01**，发现 DIMCAR 里的 Force 没有到 0.01 就收敛了，这是正常的"。
- 问题：同一份讲义，模板给 −0.03，自述的实算给 −0.01，两个数在同一节里并存，没有解释哪个是推荐值。
- 我的判断与依据：**模板是 −0.03，实际算例是 −0.01**。依据是三个真实 INCAR（`day3\ts\dim`、`5-ts\...\ts-cineb`、`ts-dimer`）都写 −0.01，只有 `8-1-ex2...` 写 −0.03。两者都可用，但"该用哪个"讲义没有说清 —— 建议按体系难度选：−0.03 起步，简单体系可以收到 −0.01。

**C-2｜`NSW`/`EDIFFG` 在频率计算里"不用设置"，但同一页的 INCAR 又设了**
- 位置：L3 P30
- 原文："（4）NSW 和 EDIFFG 都不用设置或取任意值。NSW 不能取 0"，紧接着列出的 INCAR 里有 `EDIFFG = -0.01` 和 `NSW = 300`。
- 问题：文字与示例自相矛盾。
- 我的判断与依据：**文字说的是"这两个量不影响 IBRION=5 的结果"**（因为离子步数是固定的），**示例保留了上一个任务的残留值**。依据：`7-4-Au-O-freq\ts\OUTCAR` 回显 `NSW = 289`（不是 INCAR 里的 300），说明 VASP 在 IBRION=5 下确实改写了 NSW。所以"取任意值"这个说法方向是对的，但"OUTCAR 回显值 = INCAR 值"不成立。

**C-3｜ZPE 的算法：P61 的"全部 meV 求和除以 2000"与 P37/P71 的实际做法不一致**
- 位置：L3 P61 vs L3 P37、L3 P71、L3 P32
- 原文：
  - P61："ZPE 是计算频率 grep cm OUTCAR，**取最后一排 meV 的能量和，再除以 2000**"
  - P32："最后这个 52.148981 meV 是 hν 的值，hν/2 是零点振动能 ZPE，**求 zpe 可以直接读这个能量除以 2**"
  - P71："这里我们先算一下 O2 振动频率，得到 6 个值，由于双原子分子有 3N−5 个振动自由度，**所以只需要取第一个频率即可**。ZPE = 194.29/2000 = 0.097145 eV"
- 问题：三种说法互不等价。把 P71 的 6 行 meV 全加起来是 216.711，/2000 = 0.10836 eV，**不等于**讲义给的 0.097145 eV。而按 P32 的"每条 hν/2 再求和"（P32 表达式）也会得到 0.10836。
- 我的判断与依据：**P71 的做法（只统计真实的 3N−6 或 3N−5 个振动模式）在物理上是对的；P61 的"全部求和除以 2000"是简写，只对"所有列出的频率都是真实振动模式"的场合成立**。依据：O2 的 6 行里有 3 行标 `f/i`（虚频，是平动转动残余，见 P36 的说明），虚频不应计入 ZPE；讲义自己在 P71 也只取了第一个。另外"最后一**排**"疑似"最后一**列**"的笔误（meV 是每行最后一列）。**不确定** P61 是否只是排版简写。

**C-4｜P64 的 vaspkit 输出与 P65 的汇总表对不上**
- 位置：L3 P64 vs L3 P65
- 原文：P64 是 vaspkit 501 的输出：`Zero-point energy E_ZPE : 1.515 kcal/mol 0.065715 eV`、`Thermal correction to U(T): 2.189 kcal/mol 0.094915 eV`、`Thermal correction to H(T): 2.189 kcal/mol 0.094915 eV`、`Thermal correction to G(T): 1.158 kcal/mol 0.050237 eV`、`Entropy S : 14.459 J/(mol*K) 0.000150 eV`。P65 的 298.15 K 表里 Is 行是 `εele -66.7509, ZPE 0.0672, ΔH0→T 0.0285, T*S 0.0433, ΔG 0.0524`。
- 问题：ZPE（0.065715 vs 0.0672）、ΔH（0.094915 vs 0.0285）、ΔG（0.050237 vs 0.0524）三项都不相等。ΔH 差了 3 倍多。讲义没有标注 P64 对应的是 Is、Ts 还是 Fs。
- 我的判断与依据：**不确定这两页是否来自同一次计算**。旁证：由 P33/P35 的频率（IS 三个实频 363.75/361.16/358.64 cm⁻¹）手算 298 K 的 ΔU 约 3×kT×x/(e^x−1)，x = hν/kT ≈ 1.75，得 ≈0.0276 eV，**与 P65 的 0.0285 相符而与 P64 的 0.0949 不符**。所以 P65 的 Is 行是自洽的；P64 的输出**可能对应另一个体系/另一次运行**。**这是推论，不是讲义的说法**，列为待核对。
- 附注：P64 里 `Entropy S : 14.459 J/(mol*K) 0.000150 eV` 的第二个数其实是"每 K 的熵"（14.459/96485 = 1.499e-4 eV/K），**讲义没解释这一列**；同一个输出里 TS = ΔH − ΔG = 0.094915 − 0.050237 = 0.044678 eV，与 0.000150 不是一回事。

**C-5｜P98 的 vaspkit 输出与 P99 表中同一温度的值不一致**
- 位置：L3 P98 vs L3 P99
- 原文：P98 `echo -e "502\n100\n1\n3\n" | vaspkit | grep G\(T\):` → `Thermal correction to G(T): -1.207 kcal/mol -0.052318 eV`；P98 标注"参考 0K，1bar"、"1bar 100K"。P99 表里 0 K → μO = −4.8829，100 K → μO = **−4.95763**。
- 问题：−4.8829 + (−0.052318) = **−4.93522** ≠ −4.95763，差 **0.0224 eV**。
- 我的判断与依据：**不确定原因**。可能是 P98 的命令回显与 P99 的表不是同一次计算（例如压力/自旋多重度输入不同），也可能是 P99 表用了别的基准。P99 表自身的增量（0→100 为 −0.0747，100→200 为 −0.0956）在物理上更合理（温度升高自由能下降加速）。列为待核对。

**C-6｜"前 3N−6 个频率"这个说法依赖输出顺序**
- 位置：L3 P37 vs L3 P33、L3 P71
- 原文：P37 "得到**前 3N−6 个**频率是我们关心的"；但同页输出里虚频 `f/i` 排在最后三行，实频排在最前。P33 的过渡态例子里，唯一有意义的频率（虚频 132 cm⁻¹）恰恰排在**第 3 行（最后一行）**。
- 我的判断与依据：**"前 3N−6 个"在 P37 那个例子里碰巧对，但不能当通用规则。** 依据（我把讲义内三个例子放在一起看）：P32/P33 的 Au–O 是 12.609 → 12.052 → f/i 3.964；P37 的 H2O 是 114.81/111.39/47.51/1.910/1.795/0.244 然后 f/i 0.182/0.265/1.836；P71 的 O2 是 46.98/1.953/1.121 然后 f/i 0.00698/1.046/1.294。三例共同规律是"**实频由大到小在前，虚频由小到大在后**"。**推论**，不是讲义的原话。建议的稳妥做法是**逐行看 f/i 标记**，而不是数前几行。

**C-7｜`DdR` 的两个取值**
- 位置：L3 P147 vs L3 P151
- 原文：P147 的 INCAR 里 `# DdR = 5E-3  # The dimer separation`（注释掉）；P151 "否则要用更小的 EDIFF，PREC=Accurate 等方法以提高力的计算精度，**或者提高 DdR=0.01**"。
- 问题：同讲义里 DdR 出现 5E-3 与 0.01 两个值，一个是默认注释、一个是调参处方，没有说明两者的关系。
- 我的判断与依据：**两者都对，语境不同**——P147 是 VTST 的默认 dimer 间距，P151 是"力算不准时把间距调大"的处方。但讲义没写清默认值到底是哪个。真实算例（`day3\ts\dim\INCAR`、`ts-dimer\INCAR`）里 **`DdR` 都是注释状态**，没有给出实算取值。列为待核对。

**C-8｜P118 的"NEB 点编号"与 P120 的"P+1 点"表述**
- 位置：L3 P118 vs L3 P120
- 原文：P118 "共插入 P−1 个，反应物编号为 0，产（物）编号物为 P"；P120 "这 P+1 点保持第一和最后一个点不动"。
- 问题：两处一致（0..P 共 P+1 个点，其中 P−1 个是插点），但 P118 的句子"产编号物为 P"是明显的**词序错乱**（原文排版/笔误），"共插入 P-1 个"与"点"混用。
- 我的判断与依据：**语义可还原为"共 P+1 个点，两端固定，中间 P−1 个为插点"**，与 L3 P131 的 `IMAGES` 语义（插点个数）一致。属排版/笔误，不影响理解。原文排版如此。

**C-9｜P126 "插点数 ≈ dist/0.8" 与同页"这个例子插一个点就够了"**
- 位置：L3 P126
- 原文："插点的数目取决于前面 dist.pl 的返回值，一般插点数目可取（dist.pl 返回值/0.8）。**这个例子插一个点就够了**。"
- 问题：本例 dist.pl = 1.7392，1.7392/0.8 = **2.17**，按公式应插约 2 个点，但讲义插 1 个。
- 我的判断与依据：**这条规则只是量级经验，不是硬约束**；讲义紧接着用两句话为"只插一个点"辩护（"这里只插一个点和插三个点的结果完全一样"），并用 P133 的 14 步收敛做背书。**推论**：该公式的真正用途是判断"路径是否太长、需要更多点"，而不是精确决定插点数。

**C-10｜`neb2dim.pl` 段落里给的一组参数与 Dimer 的实际要求冲突**
- 位置：L3 P166 vs L3 P146/P147
- 原文：P166 "VTST 提示我们使用这些参数，同时**要把 CINEB 的参数删除掉**：`ICHAIN = 0 / LCLIMB = .TRUE. / IOPT = 1 / IMAGES = 1 / SPRING = -5`"。
- 问题：这段列的正是 **CINEB** 的参数（ICHAIN=0、LCLIMB、IMAGES、SPRING），而 Dimer 需要的是 `ICHAIN = 2`、`IOPT = 2`（P146），且 Dimer 不用 LCLIMB/IMAGES/SPRING。同页文字说"要把 CINEB 的参数删除掉"，却把 CINEB 参数原样列出。
- 我的判断与依据：**这段是排版/来源混入错误，应以 P146/P147 的 Dimer INCAR 为准**。依据：`5-ts\8-1-ex1-O-Au\ts-dimer\INCAR` 里 CINEB 段落整块被 `#` 注释掉，生效的是 `ICHAIN = 2` + `IOPT = 2`，且**没有** LCLIMB/IMAGES/SPRING。**不确定** P166 是不是"neb2dim.pl 输出的 dim/INCAR 模板仍然带着 CINEB 段"这一实际情况的描述 —— 若如此，则讲义的意思是"记得手改"，但它没写出来。

**C-11｜`day3\ts\dim\INCAR` 的段标题与内容错位（算例侧，非讲义）**
- 位置：`things to study\day3\ts\dim\INCAR`
- 原文：第 49–55 行是 `#### DIMER ####` 段（全部注释），第 57–62 行标题是 `#### CINEB ####`，但里面写的是 `ICHAIN = 2 # 0:CINEB, 2:DIMER` 和 `IOPT = 2`（即 Dimer 的设置）。
- 问题：生效的设置挂在 `#### CINEB ####` 标题下。
- 我的判断与依据：**明显是复制模板时没改段标题**。依据：`5-ts\8-1-ex1-O-Au\ts-dimer\INCAR` 的同一段标题写的是 `#### DIMER ####`，内容相同。对照即可确认。

### 4.2 讲义 vs 答疑稿不一致

**C-12｜"挖掉一个 O 空穴后体系带什么电"——讲师自己承认讲反了**
- 位置：D3-P5、D3-P6
- 原文：学员问"扣了一个氧原子，应该是不带走多余电子，怎么使得表面带正电的"；讲师答"**这里我上课时候应该是讲反了**，挖掉一个 O 空穴，体系带有负电，此时会使得负载团簇也带负电"，并让学员去看 J. Am. Chem. Soc. 2013, 135, 10673−10683。
- 问题：**L3 讲义正文（196 页）里没有这段"氧空穴带电"的讨论**，所以我无法在 L3 中定位被讲反的那一处。
- 我的判断与依据：这是**答疑稿明确推翻某处课堂口述**的记录。**L3 文本层里找不到对应段落**（我按"空穴/氧空位/带电"检索过正文，正文只在 P110 提到 Ostwald ripening 的化学势分析，与带电无关）。因此这条更正**无法绑定到具体页码**。列为待核对（§5）。

**C-13｜频率只算最高点 —— 答疑稿给了讲义正文没明说的操作规则**
- 位置：D3-P33、D3-P34
- 原文：学员问 CI-NEB 结果 0 / −0.4 / −0.9 / 0.1 / 0.8 / 0.4 收敛后"虚频处理是每个文件夹都需要吗"；讲师答"**频率只算能量最高的点即可**"、"能量出现下降是不对的"。
- 问题：L3 正文只说"步骤十一：频率计算验证虚频"（P133），**没有说只对哪一个 image 算频率**。
- 我的判断与依据：**答疑稿是正文的必要补充**。它与 L3 P162"一般我们只关注能量最高的 image 能量"（用 nebef.pl 获取）的口径一致。建议把"只对能量最高的 image 做频率验证"写进决策库。另外 D3-P34 说"能量出现下降是不对的"——与 L3 P154 问题(1)（中间点能量比初末态低）是同一类问题的两种表述。

**C-14｜气体分子热力学量：Gaussian 与 vaspkit 是否一致**
- 位置：D3-P35、D3-P36 vs L3 P67
- 原文：学员问"用高斯估计水分子的热力学量和 vaspkit 处理结果差的多吗"；讲师答"**一样的**"。L3 P67 说"用实验数据校正热力学量，和用高斯算出来数据的非常接近"，并把 Gaussian 列为方法二、vaspkit 502 列为方法三。
- 问题：不构成冲突，但 L3 P67 的小标题写"**有两种方法**"，正文却列了**三种**（JANAF-NIST、Gaussian、vaspkit 502）。
- 我的判断与依据：**"两种"是漏改的标题**，正文三法是实际内容。属讲义内部小笔误。

### 4.3 疑似笔误 / PDF 抽取排版错乱

**C-15｜公式与上下标被打散（通篇现象）**
- 位置：L3 P5、P10、P15、P22、P23、P42、P47、P51、P54、P56、P58、P61、P92、P95、P104、P105、P178、P180、P182 等
- 现象举例：
  - P21/P23 的 `𝜕2𝐸 / 𝜕𝑥𝑖𝜕𝑥𝑗`、`𝐌−1/2𝐇𝐌−1/2`（应为 M^(−1/2) H M^(−1/2)）
  - P23 的 `𝛩𝑖,𝑗 = 𝐻𝑖,𝑗 / 𝑀𝑖,𝑖𝑀𝑗,𝑗`（分母应为 √(M_ii·M_jj)，平方根在抽取中丢失）
  - P51 的 `𝑈vib(𝑇) = 𝑅 Σ ... (ℎ𝑣𝑖/𝑘)(1/2 + 𝑒^(−ℎ𝑣𝑖/𝑘𝑇)/(1 − 𝑒^(−ℎ𝑣𝑖/𝑘𝑇)))`
  - P58 的转动配分函数两式（线性分子 `8π²IkT/(σh²)`、非线性 `8π²/σh³ (2πkT)^{3/2} √(I_A I_B I_C)`）—— 根号被打散
  - P95/P106 的 `𝐺RuO2 bulk` 上标/下标被拆到下一行
  - P178 的 `𝑘 = (kB𝑇/ℎ) 𝑒^(−Δ𝐺a/kB𝑇)`、P180 的 HTST 连乘式、P182 的 `𝜅(𝑇) = 1 + 1/24 [1.44 × 𝑣≠/𝑇]²`
- 我的判断与依据：**这是 PDF 文本层抽取的固有限制，不是讲义内容错误**。我按化学/物理语义还原并在 §3 里注明。原文排版如此。**凡是被打散的公式，本报告都不把它们当作"逐字引用"。**

**C-16｜明显错字/词序错乱清单（原文排版如此）**
| 位置 | 原文 | 问题 | 我的判断 |
|---|---|---|---|
| L3 P3 | `Chemical, physical, dissociative adsdorptiono` | `adsdorptiono` 拼写错误 | 应为 `adsorption`；标题行笔误 |
| L3 P9 | `H原子在Cu(100)表面上就有三种吸附位点：Top site, Bridge site, Hollow site` | 同一页 P7 讲的是 Cu(111) 上的 H；P11 也是 Cu(111)；P14 又拿 "H在Cu(100)的Top，bridge位" 举例 | **不确定**是 (100) 还是 (111) 笔误。P14 的论点（top/bridge 非极小值）与 P10/P11 的 Cu(111) 结论一致。列为待核对 |
| L3 P31 | `Degree of freedom是体系中的自由度3N` | 与同页输出 `1/3` 和 21 原子体系矛盾 | 应为 **3 ×（放开的原子数）**；见 §3.5 与 3.8.2 的依据 |
| L3 P61 | `取最后一排meV的能量和` | "排"应为"列" | 笔误；且全量求和在含虚频时是错的（见 C-3） |
| L3 P114 | `而在于之正交的其他所有方向上` | "在于之"应为"在于与之" | 词序/漏字 |
| L3 P118 | `产编号物为P` | 词序错乱 | 应为"产物编号为 P" |
| L3 P151 | `过渡态能量去OSZICAR最后一个E0` | "去"应为"取" | 笔误 |
| L3 P151 | `这个能量不是电子熵外推到0的能量` | 表述含混 | **推论**：应指 DIMCAR 的 Energy 不是"电子熵（−TS）外推到 0 K"的那个能量（即 OSZICAR 的 E0）；OUTCAR 里就是 `free energy TOTEN` 与 `energy(sigma->0)` 的区别。**不确定**，列为待核对 |
| L3 P169 | `其中(03)image的C-H键距离只有0.59 A` | "A" 应为 "Å" | 单位符号降级；算例实测 0.5916 Å，数值对 |
| L3 P171 | `0.59 Å 1.09 Å` / `IDPP插点法线性插点法` | **数字与标签的阅读顺序相反** | 按化学语义还原为"**线性插点法 0.59 Å、IDPP 1.09 Å**"。依据：L3 P169 说 nebmake.pl（线性）给 0.59 Å、P170 起用 IDPP 作对比；算例文件实测 `c6h12-nebmake\03` = 0.5916 Å、`c6h12-idpp\03` = 1.0879 Å |
| L3 P172 | 页脚孤零零一行 `IDPPnebmake.pl` | 与上下文无法衔接 | **原文排版如此**，疑似把 "IDPP / nebmake.pl" 的比较标签打散 |
| L3 P81 | `NørsKov在其书中估算` | 人名拼写 | 通常写作 **Nørskov**。原文如此 |
| L3 P87 | `Pt时过电位最小的HER电极材料` | "Pt时"应为"Pt是" | 笔误 |
| L3 P3 / P29 | `adsdorptiono`、`Dist`… | — | 见上 |

**C-17｜DIMCAR 示例表格的排版错乱**
- 位置：L3 P149
- 原文：表格后紧跟 `。。。`，然后单独 5 行 `平移1 / 平移2 / 平移3 / 平移4 / 平移5`，再一行 `扭矩 曲率 旋转角度`。表格右侧还有讲义手加的 `旋转1..旋转4` 注解。
- 问题：`平移1..5` 与 `扭矩 曲率 旋转角度` 显然是**表格的列/行标签**，被抽取器甩到了表格外面；`旋转1` 等注解也与表格行错位。
- 我的判断与依据：**这是排版/抽取错乱，不是内容错误**。还原后的语义是：DIMCAR 每个 Step 下有多行"旋转 k"，列含义为 Step/Force/Torque/Energy/Curvature/Angle（与 P150/P151 的逐列解读一致）。原文排版如此。

**C-18｜P140 与 P150 的 Dimer 流程图重复且文字零散**
- 位置：L3 P140、L3 P150
- 原文：两页都出现 `平移Dimer / 判断力F(R) < |EDIFFG|, 且曲率C<0 / 旋转Dimer` 三个短语，位置分散。
- 问题：是流程图的三个方框，被抽取成散句。
- 我的判断与依据：**语义 = 循环：旋转 Dimer → 判断 F(R) < |EDIFFG| 且 C < 0 → 是则结束，否则平移 Dimer 后继续旋转**。原文排版如此。与 P139 的 C>0 / C<0 讨论一致。

### 4.4 与官方文档可能不符之处（只记录，不裁定）

**C-19｜`IOPT = 0` 到底是"VASP 自带的 DIIS 优化"还是"IBRION=1, POTIM=0.1"**
- 位置：L3 P129、L3 P146 vs L3 P156
- 原文：
  - P129/P146："0 意味着启用 VASP 自带的优化算法，（比如：IOPT=0，则 IBRION=1, POTIM=0.1）"
  - P156："尝试 IOPT=7，或者 **IOPT=0，用 vasp 自带的 DIIS 优化**"
- 问题：同一个 `IOPT=0` 被解释成两件事：一处是"退回 IBRION=1 + POTIM=0.1"，一处是"用 VASP 自带的 DIIS 优化"。而 INCAR 里同时写着 `IBRION = 3, POTIM = 0`，**讲义没有说明 VTST 会不会覆盖这两个值**。
- 我的判断与依据：**只记录，不裁定**。两条说法在 VASP 的历史版本里都能找到对应（IBRION=1 在旧手册里被描述为 RMM-DIIS 型离子弛豫），但**"设了 IBRION=3/POTIM=0 之后 IOPT=0 会怎么走"在 L3 里无依据**。列为待核对。

**C-20｜"虚频 > ~100 cm⁻¹"这个门槛没有出处**
- 位置：L3 P33
- 原文："一般过渡态的虚频都 **> ~100 cm-1**，如果虚频太小，则过渡态可能找的不对，需要看振动方向检查一下。"
- 问题：这是一个经验门槛，讲义没给出处，也没说适用范围（吸附物质量、力收敛标准是否影响）。
- 我的判断与依据：**只记录**。它是经验值。反例就在同一份资料里：`7-4-Au-O-freq\o2\OUTCAR` 的**分子**（非过渡态）虚频有 0.007/1.046/1.294 THz，量级很小；而讲义 P36 明确说分子最少的 6 个频率里出现虚频"可以直接无视"。所以这个门槛只对**表面过渡态**用。列为待核对。

**C-21｜`LREAL = Auto` 与 `NCORE/KPAR` 这类并行/精度标签，讲义给的是模板值**
- 位置：L3 P30、P131、P147
- 原文：模板统一写 `KPAR = 4`、`NCORE = 5`；`LREAL = Auto`；`PREC` 被注释掉。
- 问题：同一份讲义在 P156/P151 又建议"用 `PREC=Accurate`"提高力精度，但所有 INCAR 模板里 `PREC` 都是注释状态，两者没有对照说明。
- 我的判断与依据：**只记录**。真实算例（`ts-cineb\INCAR`、`ts-dimer\INCAR`）里 `PREC` 同样是注释状态（`# PREC = Normal` / `# PREC = Accurate`），说明"力不够时再打开"是实际做法。这一条对决策库有用：**默认不设 PREC，出问题再上 Accurate**。

---

## §5 待核对清单

以下条目只有单一来源，或是我自己推出的结论，**未获第二来源确认**。凡标 `[来源待核对]` 的都不应当作断言使用。

1. `[来源待核对]` **P61 的 ZPE 求和的正确形式**。我判定"应只对真实的 3N−6（或 3N−5）个实频求和、虚频不计入"，依据是 P71 的 O2 算例与 P36 的说明。但 L3 原文 P61 写的是"全部 meV 求和除以 2000"。需与 VASP 手册/vaspkit 文档核对。
2. `[来源待核对]` **P64 的 vaspkit 501 输出到底对应 Is / Ts / Fs 中的哪一个**。我用频率手算 ΔU ≈ 0.0276 eV 去反推，支持它是"另一个体系/另一次运行"，但这是我算的，不是资料的说法。
3. `[来源待核对]` **P98 与 P99 的 0.0224 eV 偏差来源**。无法用现有资料判定是命令输入不同、还是表中数据来自另一次计算。
4. `[来源待核对]` **IBRION = 6 / 7 / 8 与 DYNMAT 的用法**。L3 全文只覆盖 `IBRION = 5`（`IBRION=6` 仅作为"默认 POTIM"的附带提及），`DYNMAT` 出现 0 次。同课程 `4-thermo\7-5-IRspectrum\INCAR` 用的是 `IBRION = 7`，但那是红外谱流程，L3 正文没有讲。**不得据 L3 写 IBRION=6/7/8 的用法。**
5. `[来源待核对]` **Dimer 的 `DdR` 实算取值**。讲义的 INCAR 里恒为注释（5E-3），P151 又建议"提高到 0.01"；两份真实 Dimer INCAR 里 `DdR` 也都是注释状态，**没有任何实算证据**。
6. `[来源待核对]` **CI-NEB 的收敛步数到底是 13 还是 14**。讲义 P133 说 14 步，`ts-cineb\01\OSZICAR` 只有 13 条 `F=` 行。差 1 的原因不明。
7. `[来源待核对]` **`neb.dat` 第 2、3、4 列的确切语义**。我实测该文件的 image 1 相对能量（0.498031）与同算例 OSZICAR 的 E0 差（0.494218）、与讲义 P134 的 0.494200 都不一致，而 image 2 三处一致。列的物理含义需要查 VTST 脚本源码才能确定。
8. `[来源待核对]` **`8-1-ex2` 那套 NEB 的 IS/FS 配对是否正确**。我证实了"顶层 POSCARis ≡ inner POSCARfs"和"顶层 POSCARfs ≠ 05/POSCAR"，但**无法判断这是归档时的文件管理失误，还是这套算例本来就用了另一对端点**。
9. `[来源待核对]` **`02/CONTCAR → 03/CONTCAR` 的 13.32 Å 与 `04/CONTCAR → 05/POSCAR` 的 26.68 Å 漂移是否正常**。我只有一套样本，没有第二个同类 NEB 结果可对照。
10. `[来源待核对]` **`NSW = 289 / 61` 的回显公式**。我确认了 INCAR 写 300、OUTCAR 回显 289（21 原子）和 61（2 原子），也确认了实际离子步数是 7 和 13。但 289 与 61 这两个数怎么来的，**我没有依据**。
11. `[来源待核对]` **Dimer 在初猜差时与 CI-NEB 的定量代价对比**。讲义只说"Dimer 初猜好效率高、初猜不好经常失败"（P164），没有给数字；我用 `ts-cineb`（13 步）与 `ts-dimer`（207 步）作对比，**但这两个算例的 EDIFFG 相同、初猜来源不同，不能直接当作方法优劣的证据**。
12. `[来源待核对]` **"过渡态虚频 > ~100 cm⁻¹"的适用范围**。它是 L3 P33 的经验值，没有出处，也不知道是否依赖吸附物质量与力收敛标准。
13. `[来源待核对]` **`IOPT = 0` 的实际行为**（见 C-19）。L3 内部两种说法并存，需查 VTST 文档。
14. `[来源待核对]` **C-12 那条"上课讲反了"的更正对应 L3 的哪一页**。L3 正文里找不到氧空穴带电的段落，无法绑定页码。
15. `[来源待核对]` **`day3\ts\dim\MODECAR` 与 `POSCAR` 约束不一致**（X-15）以及 **`POSCAR` 尾部 21 行 NaN**（X-16）。我确认了现象，但**不确定**这是否会影响当时的计算（VASP 对 POSCAR 多余行的容忍度我没有验证）。
16. `[来源待核对]` **`day3\idpp\nebmake\` 目录名与内容不符**（X-8）。我用 MD5 相同 + 几何指标一致证明"该目录装的是 IDPP 结果"，但**这是推论，不是任何文件里写着的**。
17. `[来源待核对]` **讲义 P119、P34、P75 三页是纯图片页**（文本层只有页眉页脚）。它们承载的信息（NEB 示意、频率结果图、能量图）在文本层里丢失，我只知道主题，**内容无法核对**。
18. `[来源待核对]` **P128 提到的"把 nebmovie.pl 源码倒数 5-7 行注释掉可以生成 .xyz"**。这是对 VTST 脚本的改动说明，我手边没有 `nebmovie.pl` 源码可核对。
19. `[来源待核对]` **P7 "Threefold/hollow"、"H2/Cu(111) → 2H/Cu(111)" 等图内文字**与正文的对应关系。图内标签被抽取成独立行，我按上下文还原，未获独立确认。
20. `[来源待核对]` **P110 的 Ostwald ripening 判据方向**：原文写"ΔµSA(CO) > ΔµNP(CO) ，SAs aggregation"，即单原子化学势高于纳米颗粒时趋于聚集。逻辑自洽（化学势高 → 不稳定 → 聚集），但同一页没有给公式出处，只有 P111 的 Gibbs–Thomson 关系与 JACS 2017 引文。列为待核对。
