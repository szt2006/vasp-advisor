# G7 精读报告 —— 《Learn VASP The Hard Way》第二版 第 7 组（VASP 生态工具与脚本）

- **资料来源**：`references/raw/lvthw/A17.txt` … `A34.txt`（共 18 篇，2528 行）。
  行数逐篇核对过 `references/raw/lvthw/_MANIFEST.tsv`，一致。
- **本组主题**（`references/raw/lvthw/_GROUPS.tsv` 第 8 行）：`G7_生态工具` = A17 A18 A19 A20 A21 A22 A23 A24 A25 A26 A27 A28 A29 A30 A31 A32 A33 A34。
- **引用格式**：`A29:60` = `references/raw/lvthw/A29.txt` 的第 60 行（1 起）。行号都落在该文件的实际行数内。
  官方层引用格式：`references/official/pages/<页面>.md`。既有知识层引用格式：`decide.md:915` / `playbook.md:330` / `learn_L3.md:514` 等。
- **书写约定**：
  - 【原文】= 作者真的这么写（带 `A..:<行>`）
  - 推论：= 我根据原文/所附脚本/所附算例推出的，**不是**作者的断言
  - 证据标记沿用 `references/_WRITING_CONTRACT.md` §1：`[官方]` / `[算例]` / `[实测]` / `[经验]` / `[待核对]`
  - LVTHW 是**第三方二手教程**（按契约 §8 的权威序，低于官方与真实算例）。所以本组绝大多数条目**只能标 `[经验]` 或 `[待核对]`**，我逐条标了。
- **完成度声明**：A17–A34 共 18 篇、2528 行**逐行读完**（无跳读）。
  另外读了配套脚本实物 4 份：`things to study2/LVTHW-master/source/_posts/{A18/li_conductivity.py, A19/expand.py, A20/smiles_to_xyz.py, A24/test.py}`，
  以及算例文件 `A19/{CONTCAR,POSCAR}`、`A24/pda.vasp`。
  **未读取**任何 `POTCAR`；`A33` 正文里出现的那个真实 `api_key` **没有被复制到本报告**（见 §3.7）。

---

## §1 覆盖清单

格式：`POST_ID 行数 主题摘要`。18 篇连续，一篇不少；行数 = 该 `.txt` 全文行数（与 `_MANIFEST.tsv` 一致）。

```
A17  202  ASE 格式转换：mol/cif → xyz / POSCAR；ASE 写出的 POSCAR 默认是「无元素行」的 VASP4 形态
A18  251  Pymatgen 算离子电导率：AIMD → XDATCAR → MSD → 自扩散系数 → Nernst-Einstein 电导率；含 AIMD 降本四件套与算例 884.05 mS/cm@900K
A19  84   ASE 扩胞：expand.py CONTCAR 4 4 1 → POSCAR（4→64 个 Ru）；cell*(x,y,z) + direct=True + sort=True
A20  195  ASE + Openbabel 的 SMILES→3D：pybel.make3D(MMFF94) 生成构型，再用 ASE 套周期盒子并写 xyz/POSCAR
A21  79   Ubuntu20 装 p4vasp（Python2/GTK2 遗物）：从旧 archive 取 deb、先 gtk2 后 glade2
A22  231  VirtualBox 装 Ubuntu 虚拟机：资源分配、vdi、Guest Additions、共享文件夹权限
A23  184  Ubuntu 常用软件：apt 清单、Anaconda、**装完 Anaconda 后 p4vasp 报 SyntaxError 的诊断与修复**、VESTA 免安装 + PATH、备份
A24  112  离子迁移概率密度可视化：XDATCAR → DiffusionAnalyzer → ProbabilityDensityAnalysis → CHGCAR 体数据 → VESTA；含「怎么读这张图」的四条判据
A25  64   matminer 是什么（数据获取 + 特征化 + 建模 + Automatminer）与安装
A26  183  matminer 从 Materials Project 取数：criteria/properties 语义、$gt/$lt/$exists/$all 操作符、warnings 做数据质量过滤、性能坑
A27  118  从 Citrine 取数：Silicon 实验带隙 7 条、*OH 9 条 / *O 21 条吸附能；数据稀疏与库版本漂移
A28  122  ASE 取原子间距离：get_distance(mic=True/False)；Pt–Ti 3.8175 Å vs 7.4611 Å；ASE 下标从 0 开始
A29  178  ⚠️ ASE 消虚频小脚本：沿虚频方向位移坐标再重新优化；含 ASE 版与纯 python 版两份代码
A30  50   VASP 官方 Youtube 的 9 个视频清单（资源指引，无计算知识）
A31  163  VTST 编译进 VASP：vtstcode 目录 ↔ VASP 版本对应、main.F 与 .objects 两处修改、grep VTST 验证
A32  150  ⚠️ Improved Dimer Method（IBRION=44）脚本：从粗频率 OUTCAR 抽最大虚频方向，写成 Dimer Axis Block
A33  39   matminer/pymatgen 从 Materials Project 取结构并导出 CIF（正文里写死了一个真实 api_key）
A34  123  ⚠️ ASE 热力学模块 IdealGasThermo 算气体熵：四个必填输入、eV/K 量纲、G = E + ZPE − T·S
```

> 与任务单给的篇目行数有 ±1 的差异（任务单写 A17=201/A29=179 等）。
> 我以**实际文件行数**为准：`read` 报告的 total 与 `_MANIFEST.tsv` 第 17–34 行的第 7 列**逐篇一致**，
> 且 18 篇合计 **2528 行**（与任务单总数一致）。差异原因未查明 → `[待核对]`（见 §5）。

---

## §2 主题分段表

与 `references/raw/lvthw/seg_G7.tsv` **逐行一致**（该文件含表头 `post_id 起行 止行 主题 要点`，五列制表符分隔）。
每个 post 的行区间连续覆盖该 `.txt` 全文，无重叠、无空档。

| post | 起行 | 止行 | 主题 |
|---|---|---|---|
| A17 | 1 | 11 | front-matter 与标题 |
| A17 | 12 | 19 | 引言：本文要做什么 |
| A17 | 20 | 27 | 例子1 mol→xyz 的输入 |
| A17 | 28 | 75 | 实操 ase gui 转 mol→xyz |
| A17 | 76 | 96 | 滤纸与例子2 CIF→XYZ/POSCAR |
| A17 | 97 | 155 | 实操 CIF→xyz 与 CIF→POSCAR 逐行输出 |
| A17 | 156 | 190 | ASE 写 POSCAR 的 VASP4 格式问题 |
| A17 | 191 | 202 | 结语 |
| A18 | 1 | 33 | front-matter；Pymatgen 是什么 |
| A18 | 34 | 48 | 离子电导率的理论框架与 AIMD 降本配方 |
| A18 | 49 | 74 | 后处理三个公式 |
| A18 | 75 | 110 | 算例 INCAR 与 XDATCAR 合并 |
| A18 | 111 | 133 | 安装 pymatgen |
| A18 | 134 | 167 | DiffusionAnalyzer 类与 from_structures |
| A18 | 168 | 226 | li_conductivity.py 与运行结果 |
| A18 | 227 | 251 | 下载、思考题与打赏 |
| A19 | 1 | 16 | front-matter 与引言 |
| A19 | 17 | 45 | 例子：1x1 Ru(0001) → 4x4 |
| A19 | 46 | 77 | expand.py 脚本与参数 |
| A19 | 78 | 84 | 打赏与联系方式 |
| A20 | 1 | 20 | front-matter；引子与装环境 |
| A20 | 21 | 47 | SMILES 是什么 |
| A20 | 48 | 101 | smiles_to_xyz.py 全文 |
| A20 | 102 | 127 | 运行命令与产物 |
| A20 | 128 | 179 | 脚本逐段详解 |
| A20 | 180 | 195 | 小结：结构合理性必须自查 |
| A21 | 1 | 12 | front-matter；p4vasp 的前景判断 |
| A21 | 13 | 34 | 下载解压与基础编译依赖 |
| A21 | 35 | 57 | 旧运行库依赖与 install.sh |
| A21 | 58 | 73 | 注意与反馈 |
| A21 | 74 | 79 | 打赏 |
| A22 | 1 | 16 | front-matter；虚拟机的选型 |
| A22 | 17 | 30 | 准备工作 |
| A22 | 31 | 88 | 创建虚拟机 |
| A22 | 89 | 140 | 安装 Ubuntu 系统 |
| A22 | 141 | 169 | 增强扩展包（Guest Additions） |
| A22 | 170 | 199 | 网络、剪贴板共享、共享文件夹 |
| A22 | 200 | 231 | 共享文件夹权限的解决办法与打赏 |
| A23 | 1 | 26 | front-matter；建 ~/bin |
| A23 | 27 | 84 | apt 软件清单与用途 |
| A23 | 85 | 111 | 安装 Anaconda |
| A23 | 112 | 140 | Anaconda 后 p4vasp 失效的诊断与修复 |
| A23 | 141 | 169 | VESTA 免安装与 PATH 设置 |
| A23 | 170 | 184 | 备份策略与打赏 |
| A24 | 1 | 12 | front-matter |
| A24 | 13 | 33 | 引言：这篇要画的图 |
| A24 | 34 | 60 | 安装 pymatgen-diffusion |
| A24 | 61 | 91 | 官方 notebook 用法 |
| A24 | 92 | 112 | 从 XDATCAR 起飞：test.py |
| A25 | 1 | 15 | front-matter 与引言 |
| A25 | 16 | 26 | matminer 能做什么 |
| A25 | 27 | 62 | 安装与自测 |
| A25 | 63 | 64 | 结尾 |
| A26 | 1 | 18 | front-matter；入口 |
| A26 | 19 | 38 | 示例1：单元素材料的密度 |
| A26 | 39 | 59 | criteria/properties 语义与 DataFrame |
| A26 | 60 | 91 | 示例2：带隙大于 4.0 eV |
| A26 | 92 | 121 | 示例3：VRH 弹性模量与数据质量过滤 |
| A26 | 122 | 162 | 复杂示例：成分 + 热力学稳定性 + 出图 |
| A26 | 163 | 183 | 结尾 |
| A27 | 1 | 21 | front-matter；Citrine 与依赖 |
| A27 | 22 | 60 | 示例1：Si 的实验带隙 |
| A27 | 61 | 111 | 示例2：*OH 与 *O 的吸附能 |
| A27 | 112 | 118 | 结尾 |
| A28 | 1 | 16 | front-matter 与引言 |
| A28 | 17 | 40 | 例子：Pt/TiO2(101) 的两种距离 |
| A28 | 41 | 79 | get_dis_AB.py 与 mic 参数 |
| A28 | 80 | 114 | 输出、格式改进与放进 ~/bin |
| A28 | 115 | 122 | 结尾与联系方式 |
| A29 | 1 | 16 | front-matter；虚频的烦恼与方法概述 |
| A29 | 17 | 28 | 原理四步与校正因子举例 |
| A29 | 29 | 62 | OUTCAR 虚频段原文 |
| A29 | 63 | 111 | vib_correct.py（ASE 版） |
| A29 | 112 | 121 | 使用说明 5 条 |
| A29 | 122 | 174 | 纯 python 版（不用 ASE） |
| A29 | 175 | 178 | 二维码 |
| A30 | 1 | 15 | front-matter 与频道截图 |
| A30 | 16 | 40 | 9 个视频清单与作者评价 |
| A30 | 41 | 50 | 关注建议与下载方式 |
| A31 | 1 | 26 | front-matter；编译的两个前提 |
| A31 | 27 | 42 | 下载解压与版本对应 |
| A31 | 43 | 58 | 编译前准备 |
| A31 | 59 | 79 | main.F 的替换内容与版次差异 |
| A31 | 80 | 112 | src/.objects 的修改与顺序要求 |
| A31 | 113 | 124 | 完整编译命令 |
| A31 | 125 | 148 | 验证：grep VTST 看版本横幅 |
| A31 | 149 | 163 | 四条总结与结尾 |
| A32 | 1 | 13 | front-matter；IDM/Dimer/NEB 的关系 |
| A32 | 14 | 18 | IDM 已内置，只需 IBRION=44 |
| A32 | 19 | 51 | IDM 五步流程 |
| A32 | 52 | 58 | 脚本下载地址 |
| A32 | 59 | 130 | get_dimer.py 全文 |
| A32 | 131 | 145 | 五条注意事项 |
| A32 | 146 | 150 | 结尾 |
| A33 | 1 | 12 | front-matter |
| A33 | 13 | 23 | matminer 从 MP 取 Cu |
| A33 | 24 | 37 | pymatgen 取结构并导出 CIF |
| A33 | 38 | 39 | 二维码 |
| A34 | 1 | 12 | front-matter |
| A34 | 13 | 27 | IdealGasThermo 的四个必填输入 |
| A34 | 28 | 81 | get_gas_entropy.py 全文 |
| A34 | 82 | 105 | 运行输出：熵分解、G 与 S |
| A34 | 106 | 116 | 四点说明 |
| A34 | 117 | 123 | 下载与二维码 |

---

## §3 知识条目

### 3.1 ⚠️ A29 —— 消虚频的具体方法（本组最值钱的一篇）

#### 3.1.1 方法：**沿虚频的振动方向，把原子的坐标平移一小段，然后重新优化**

【原文】作者的原理陈述是 5 句话（A29:17-27）：

1. `OUTCAR` 里带 `f/i` 的行说明有虚频（A29:19）；
2. 该行下面的 `X, Y, Z` 是体系中原子的坐标，也就是 `POSCAR` 里的内容（A29:21）；
3. `dx, dy, dz` 是**虚频对应的原子振动方向上的位移**（A29:23）；
4. 把 `(dx, dy, dz)` 乘一个 **0–1 之间的校正因子**，加到 `POSCAR` 的坐标上（A29:25）；
5. 例子：z 方向校正因子取 `0.1`，新 z 坐标 = `10.709980 + (−0.676634) × 0.1`（A29:27）。

**所以答案是：不是随机位移、不是换算法，而是"沿虚频本征矢方向把原子推出去"**——物理上就是
"从鞍点/过渡态附近沿着负曲率方向滑向极小点"。这一点与方法论文献里"displace along the imaginary mode and reoptimize"完全同构。

#### 3.1.2 脚本到底做了什么（ASE 版，A29:67-111）

| 步骤 | 代码行为 | 行 |
|---|---|---|
| 1 | 逐行扫 `OUTCAR`，遇到含 `f/i` 的行就取 `split()[6]`（**第 7 列 = `cm-1` 列**），只保留**数值最大**的那个，并记下 `l_position = 行号 + 2` | A29:80-88 |
| 2 | `l_position = f/i 行号 + 2` ⇒ 正好跳过 `X Y Z dx dy dz` 表头，落到**第一行原子** | A29:88（对照 A29:31-33） |
| 3 | ASE 读 `POSCAR`，取坐标与原子数 | A29:90-92 |
| 4 | 取 `OUTCAR` 中 `[l_position : l_position+num_atoms]` 共 `num_atoms` 行，每行取**第 4–6 列**（即 `dx, dy, dz`） | A29:96-103 |
| 5 | `new_positions = model_positions + vib_dis * 0.4`（**脚本里用的校正因子是 0.4**） | A29:106 |
| 6 | `write('POSCAR_new', model, vasp5=True)` | A29:110 |
| 7 | 用法：新建目录 → 把 `POSCAR_new` 复制进去改名 `POSCAR` → 重新优化 | A29:120 |

#### 3.1.3 ⚠️ `dx, dy, dz` 的量纲 —— 我复算出来了（这一条决定"校正因子"怎么理解）

【原文】作者只说"位移 × 校正因子"（A29:25），**没有说 dx,dy,dz 是 Å、还是无量纲**。

推论（`[实测]`，用 A29 自己贴出的数据复算）：A29:59 是该虚频块里**唯一非零**的一行
（原子坐标 `0.099192 11.590822 10.709980`，位移 `−0.736317 0.002031 −0.676634`）。
我算它的模长：

```
sqrt(0.736317² + 0.002031² + 0.676634²)
  = sqrt(0.5421627 + 0.0000041 + 0.4578336)
  = sqrt(1.0000004) = 1.00000
```

⇒ **`dx,dy,dz` 是单位方向矢量的分量（无量纲），不是 Å 位移。**
⇒ **校正因子 × 1 ≈ 该原子的位移量（Å）**，于是：

| 校正因子 | 该原子的 |dx| | 该原子的 |dz| | 位移矢量长度 |
|---|---|---|---|
| 0.1（A29:27 的举例） | 0.0736 Å | 0.0677 Å | 0.10 Å |
| 0.4（A29:106 脚本默认） | 0.2945 Å | 0.2707 Å | 0.40 Å |

**⚠️ 重要限定（推论）**：这个"因子 = 位移 Å"的换算**只在虚频模局域在少数原子上时成立**。
本算例里 27 个原子只有最后 1 个有非零分量 ⇒ 局域模。如果虚频是**离域**软模，
每个原子的分量都很小（本征矢要按 3N 归一），即使因子取 1，位移也可能远小于 1 Å。
⇒ 这就是作者说"具体多大自己根据经验调"（A29:106）的真正原因。**别把 0.4 当成"0.4 Å 的统一位移"。**

#### 3.1.4 ⚠️ 同一篇文章里两个不同的校正因子 —— 不可当作推荐值

| 出处 | 值 |
|---|---|
| 正文举例（A29:27） | **0.1** |
| ASE 版脚本默认（A29:106） | **0.4** |
| 纯 python 版脚本默认（A29:165） | **0.4** |

**两个值都出现过，作者没有解释为什么不同** ⇒ 本 skill **不得写成"推荐 0.4"**。
只能登记"0.1 与 0.4 都在文中出现过；作者明说自行调整"，并给出上面那张"因子↔位移"的换算表让用户自己判断量级。`[待核对]`

#### 3.1.5 适用范围与**不适用**范围（作者自己写了）

- **适用**：普通结构优化时出现的虚频（A29:121 第 4 条）。
- **明确不适用**：**过渡态计算出现好几个虚频时不要用这个脚本** —— 因为脚本默认只用**最大**虚频对应的位移（A29:121）。
  ⇒ 对过渡态，你想要的往往是"沿反应坐标那一个"，而不是"数值最大的那一个"。
- 顺带一句原文（A29:15）："再不幸一些，除了过渡态对应的虚频外，还出现了一个伴生的姐弟虚频" —— 这是作者对这个失败模式的描述。

#### 3.1.6 ⚠️ 两个会**静默改坏输入**的坑（我读代码发现的，作者没提）

1. **纯 python 版会把所有原子写成固定**：
   A29:172 硬编码 `f_out.write(... + '  F  F  F\n')` —— 输出的 `POSCAR_new` **每个原子都是 `F F F`**。
   如果你原来是"只放开吸附物"的频率/优化设置，跑完这个脚本再拿去优化，**结构一个原子都不会动，而程序不会报任何错**。
   → **处方**：打开 `POSCAR_new`，检查 `Selective dynamics` 那一行之后每一行的 `T/F` 是否与你原来的一致。
2. **纯 python 版读原子数的方式只对 VASP5 格式成立**：
   A29:151 用 `num_atoms = sum(int(i) for i in lines_pos[6]...)` —— 硬编码读**第 7 行**。
   VASP5 的 POSCAR（有元素行）第 7 行才是计数行 ✅；
   VASP4 的 POSCAR（**没有元素行**——正是 A17 里 ASE 默认写出的那种！）第 7 行是 `Direct`/`Selective dynamics`，`int()` 会直接抛异常。推论，`[待核对]`
   → 这正好和 §3.9 的 A17 坑是**同一个根源**：谁都不该对"第几行是计数行"做硬编码。

（ASE 版由 ASE 负责读写，不踩这两个坑；但 A29:74-75 需要 `numpy` + `ase`。）

#### 3.1.7 与既有知识层的关系：这是**缺口**，不是冲突

`decide.md:915-933`（§13.3）只讲**怎么判**虚频（数量、数值、方向、用 `IBRION=7` 复核）；
`playbook.md:330-340`（S12）的处方是"更严的优化再收一次 / 加 `POTIM` / 用 `IBRION=7` 复核"，
**四条处方里没有"沿虚频方向位移"这一步**。
⇒ 建议把 A29 的方法补成 S12 的处方之一，但**必须带 A29:121 的限制**（过渡态多虚频不适用）
与 §3.1.4 的"因子无定值"声明。详见 §4 的 C2。

---

### 3.2 ⚠️ A34 —— 用 ASE 热力学模块算气体熵（完整方法）

#### 3.2.1 用什么函数

【原文】`from ase.thermochemistry import IdealGasThermo`（A34:43），配合 `ase.io.read/write`（A34:42）与 `scipy.constants`（A34:44）。

#### 3.2.2 四个**必须人工给对**的物理输入（A34:15-25）

| 输入 | 含义 | 本文取值 | 给错了会怎样 |
|---|---|---|---|
| 对称数 σ | `symmetrynumber` | NH₃ = **3**（A34:47, 71） | 推论：S_rot 差 `R ln σ`；NH₃ 若误填 1，S_rot 多 `R ln3` ≈ 9.13 J/(mol·K) `[待核对]` |
| 几何 | `geometry` = `'linear'` / `'nonlinear'` | NH₃ = **`'nonlinear'`**（A34:70） | 转动配分函数公式不同（3 个 vs 2 个转动自由度） |
| 自旋 | `spin` | NH₃ = **0**（A34:48） | 影响电子熵项 S_elec（本文输出里它是 0） |
| 温度 + 压强 | `temperature` / `pressure` | 298.15 K / **101325**（A34:49, 74） | 见 §3.2.5，**这一项最容易出错** |

【原文】作者说明前三项："网站上都有相应的说明，自己根据分子的特性改下即可"，
对称数不会算就查 Cramer《Essentials of Computational Chemistry》2nd Ed. 的 **Table 10.1 与 Appendix B**（A34:25, 37）。
`spin` 的取值规则抄在脚本 docstring 里：全配对 = 0、单电子自由基 = 0.5、两个未成对电子的三重态（如 O₂）= 1.0（A34:38）。

#### 3.2.3 频率、能量、结构分别怎么进（这一段是全部细节所在）

| 进什么 | 怎么取 | 行 |
|---|---|---|
| **振动频率** | 打开 **`./freq/OUTCAR`**，逐行找含 `cm-1` 的行，取 **倒数第二列**（`split()[-2]`）——这是 **meV** 列，再 `/1000` 换成 **eV** | A34:56-64 |
| 同上 | 然后 **丢掉最后 6 个**：`vib_energies[:-6]`；理由是"对分子来说，VASP 频率结果中的后面 6 个对应的是平动和转动部分，不能作为振动算熵" | A34:64, 113 |
| **电子能** | `potentialenergy = read('./OUTCAR', format='vasp-out').get_potential_energy()`（**取优化目录的** OUTCAR） | A34:50-51 |
| **结构** | `atoms = read('./freq/POSCAR')`（**取频率目录的** POSCAR） | A34:46, 53 |

⚠️ 注意这里有个隐含约定：**熵的振动部分来自 `freq/`，电子能来自上一级目录的 `OUTCAR`**（A34:111-113 有说明）。
所以"分子优化"与"分子频率"是两个目录，一个 `test_nh3/` 装优化、一个 `test_nh3/freq/` 装频率（A34:88-90, 111-113）。

#### 3.2.4 算出来是什么量纲

```python
zpe     = thermo.get_ZPE_correction()                                  # eV
entropy = thermo.get_entropy(temperature=298.15, pressure=101325)      # eV/K  ← 行末注释原文 "# Unit eV/K"
TS      = tem * entropy                                                # eV
G       = potentialenergy + zpe - TS                                   # eV
print('S', con.Avogadro * con.electron_volt * entropy, 'J/K/mol')      # 转成 J/(K·mol)
```

（A34:73-79）

- `get_ZPE_correction()` → **eV**；
- `get_entropy(...)` → **eV/K**（作者在 A34:74 行末明确注了 `# Unit eV/K`）；
- 转成化工惯用的 `J/(K·mol)`：乘 `N_A × e`（A34:79）。

**我核算过这条换算（`[实测]`）**：用同一段输出里的两个数
`S = 0.0019964 eV/K`（A34:101）与 `S = 192.6230402411749 J/K/mol`（A34:104），
二者之比 = 192.6230 / 0.0019964 = **96486 ≈ N_A·e = 96485.33 J·mol⁻¹/eV** ✅。
⇒ 量纲链是自洽的：**1 eV/K = 96485.33 J/(K·mol)**。

#### 3.2.5 ⚠️ 怎么接到 `ΔG = ΔE + ΔZPE − TΔS` 上 —— 以及一个**会静默引入 0.086 eV 的坑**

对接关系（`[官方]` 无对应页；此处是 `decide.md:1066` 的公式 + A34 的实现）：

```
ΔG = ΔE(DFT) + ΔZPE − TΔS
                  ↑        ↑
     thermo.get_ZPE_correction()      T × thermo.get_entropy(T, P)
     （A34:73）                        （A34:74-75）
```

**⚠️ 坑：压力（标准态）必须与你的参考态一致。**
脚本传的是 `pressure=101325`（Pa）= 1 atm ≈ 1.013 bar；所以输出里那一项
`S (1 bar -> P) = −0.0000011 eV/K`（A34:99）几乎为零 —— **这正是"标准态取 1 bar"的标志**。
我用理想气体熵的压力依赖 `ΔS = −R ln(P₂/P₁)` 复核了它：
`−R ln(101325/100000) = −0.1094 J/(mol·K) = −1.134×10⁻⁶ eV/K`，与打印的 −1.1×10⁻⁶ **吻合**（`[实测]`）。
⇒ 由此可确信：**ASE 这一项就是从 1 bar 换到你给的压力**。

而课程里的液态水参考态是**饱和蒸气压 ≈ 0.035 bar**（`decide.md:1051-1052`，`[讲义]` L4 P9）。
如果把 A34 的 1 bar 熵直接拿去接 CHE 图：

```
ΔS(1 bar → 0.035 bar) = −R ln(3500/100000) = +27.88 J/(mol·K) = +2.889×10⁻⁴ eV/K
TΔS @298.15 K          = +0.0861 eV
```

⇒ **每个水分子会带来约 0.086 eV 的偏差**（推论，`[待核对]`；量级与常见吸附能 0.1–0.5 eV 同阶，**足以改变结论**）。
**处方**：用 ASE 算熵时，`pressure` 要写成**与你参考态一致**的值（水 → `3500` Pa；1 bar 参考态 → `100000` Pa），
并把这个选择写进论文的方法部分。→ 已在 §4 的 C5 登记。

#### 3.2.6 算例输出（NH₃，298.15 K，1 atm）——可直接当量级参考

【原文】A34:92-104：

| 项 | S (eV/K) | T·S (eV) |
|---|---|---|
| S_trans (1 bar) | 0.0014947 | 0.446 |
| S_rot | 0.0004981 | 0.149 |
| S_elec | 0.0000000 | 0.000 |
| S_vib | 0.0000047 | 0.001 |
| S (1 bar → P) | −0.0000011 | −0.000 |
| **合计 S** | **0.0019964** | **0.595** |

`G = −19.220631915628093`（eV）、`S = 192.6230402411749 J/K/mol`（A34:103-104）。
读法提示（推论）：常温下**熵几乎全来自平动（75%）+ 转动（25%）**，振动项 `S_vib` 只占 0.24%
—— 所以"分子熵算得准不准"几乎等于"平动/转动算得准不准"，而这两项只依赖 T、P、分子质量、转动惯量与对称数。
作者自己也在目录里放了 **NIST-JANAF（`H-083.txt`）**用来对比（A34:36, 109），但**没有贴出对比结果**。

#### 3.2.7 限制与待核对

1. **`[:-6]` 依赖输出顺序**（A34:64, 113）：它假设"最后 6 行就是平动/转动投影"。
   若分子频率里有**虚频**（VASP 把虚频排在最后），`[:-6]` 会切错。
   `playbook.md:1340` 已经提醒过这个陷阱：**"稳妥做法是逐行看 `f/i` 标记，不要数前几行"**。→ §4 的 C4。
2. **电子能的口径没交代**（A34:51）：`ase.io.read('./OUTCAR', format='vasp-out').get_potential_energy()`
   取的是 `free energy TOTEN` 还是 `energy(sigma->0)`，文中没说 ⇒ `[待核对]`。
   按 `decide.md:948-962`（§14.1），报数应该用 **`energy(sigma->0)`**。
3. **只对孤立分子成立**：表面吸附物种要改用另一个模块（作者写作 **"Harmonic limit"**，A34:115）。
   ASE 里对应的类名与用法，本 skill **未核实** ⇒ `[待核对]`（`[待核对]` 也包括"作者这个叫法是否准确"）。
   物理前提与 `playbook.md:1292` 记的同一条一致：吸附后平动转动被削弱、可当作振动处理。
4. **环境依赖**：`ase` + `scipy`（A34:42-44）。→ 与"零依赖"的关系见 §4 的分界清单。

---

### 3.3 A32 —— Improved Dimer Method（IDM）脚本

#### 3.3.1 IDM 与标准 Dimer 的区别（作者口径 + 官方佐证）

【原文】
- IDM 与传统 Dimer、NEB 一样都用于优化过渡态；VTST 已经带了很多 Dimer 相关脚本，不必重造（A32:13）。
- **"IDM 已经编译在 VASP 里面了，不需要额外编译"**（A32:15）。
- **"IDM 跟平时的优化计算差不多，主要修改 `IBRION = 44` 即可"**（A32:17）。
- "NEB 结合 IDM 优化过渡态也很高效，成功率非常高"（A32:13）；文末又说"IDM 结合 NEB 的成功率很高，非常推荐"（A32:148）。

`[官方]` 佐证（**这是本组少数能拿到官方明文的条目**）：
`references/official/pages/IBRION.md` 第 1 行的取值表里含 `44`；第 24 行写 `IBRION 44 improved dimer method`；
第 66 行写"用 improved dimer method（`IBRION=44`），可以从相空间里**任意一个结构**出发搜索过渡态"。

⇒ **IDM 是 VASP 原生功能（`IBRION=44`），与 VTST 的 `ICHAIN` 家族是两套东西。** 这一条与既有 `decide.md:786` 的记法有冲突，见 §4 的 C1。

#### 3.3.2 作者的五步流程（A32:19-51）

| 步 | 做什么 | 关键细节 |
|---|---|---|
| 3.1 | **造初始过渡态结构**，三条路 | ①手搭 → 存 `POSCAR`；②用 VTST 的 `nebmake.pl` 插点，挑一个接近 TS 的 `POSCAR`；③**先跑 NEB 约 30 步**，把能量最高的结构检查后存成 `POSCAR`（A32:21-27） |
| 3.2 | **对初始结构做一次"便宜"的频率计算** | **`NWRITE = 3` 必须**（A32:33）；精度不用高：slab 原子**全固定**、分子大就只放开断键/成键的那几个原子、**Gamma 点**（A32:35-41） |
| 3.2 | **有几个小虚频不用消** | "过渡态结构本来就是粗糙的，这里消虚频也没必要；不过**一定要有过渡态对应的虚频**，如果没有，重新搭一个过渡态结构，继续算频率"（A32:43） |
| 3.3 | **用脚本把虚频方向写成 IDM 的 POSCAR** | 本篇的主题，见下 |
| 3.4 | 准备 `INCAR`/`KPOINTS`/`POTCAR` 提交 | — |
| 3.5 | **再用精度高一点的频率计算复验** IDM 出来的 TS | A32:49 |

#### 3.3.3 脚本做什么（`get_dimer.py`，代码抄在 A32:60-130）

1. 读 **`POSCAR_relax`**：作者强调这是"**没有固定那些原子的**"结构（A32:87, 136）；
   用 ASE 读进来再 `write('POSCAR_dimer', vasp5=True)` —— 目的是"保证 POSCAR 里面的结构干净，避免出错"（A32:136）。
2. 扫 `OUTCAR`，用 **`'Eigenvectors after division by SQRT(mass)'`** 这一行定位频率块起点（A32:98）；
   **找不到就直接退出**并打印 `Check Frequency results and then rerun this script. **Remember**: NWRITE must be 3. BYEBYE!`（A32:101-103）。
   ⇒ 这就是把"忘记 `NWRITE=3`"变成一个**显式报错**的设计，值得学。
3. 在块内找 `f/i` 行，取 `split()[6]`（`cm-1` 列）**最大**的虚频，记 `l_position = 行号 + 2`（A32:108-113）。
4. 取其后 `len(model)` 行，每行取**第 4–6 列**（`dx, dy, dz`），**原样追加**到 `POSCAR_dimer` 末尾；
   追加前先写一行 **`  ! Dimer Axis Block`**（A32:115-121）。
5. 输出 `POSCAR_dimer`；**用的时候改名 `POSCAR`**（A32:127, 140）；**在频率计算目录里直接运行**（A32:144）。

#### 3.3.4 什么时候该用 IDM

【原文】+ 推论：

- **只知道初态 + 一个粗糙方向/一个粗糙的 TS 结构**时（正是 `decide.md:785-786` 对 Dimer 家族的定位）。
- **已经用 NEB 跑过一段、想省事**时：作者推荐的路线是"NEB 跑约 30 步 → 取能量最高的像 → 频率确认有 TS 虚频 → IDM 精修"（A32:27, 148）。
  推论：这比"从头搭一个 TS"可靠得多，因为能量最高的像已经是个不错的初猜。
- **想消虚频**时：作者说"计算出的结果极少出现多个虚频的情况。**因此，这个方法也可以用来消虚频**"（A32:148）。
  ⚠️ 这与 A29 是**两条不同的消虚频路线**：A29 = 直接位移坐标；A32 = 让 IDM 自己爬到鞍点。选哪条取决于你到底想要"极小点"还是"鞍点"（见 §4 的 C2）。

#### 3.3.5 INCAR 模板（写在脚本 docstring 里，A32:66-79）

```
频率步：IBRION = 5    POTIM = 0.015    NFREE = 2    NWRITE = 3  ### Must be 3
IDM 步 ：NSW = 100    PREC = Normal    IBRION = 44  !  use the dimer method as optimization engine
         EDIFFG = -0.05    POTIM = 0.05
```

#### 3.3.6 限制 / 待核对

1. **`EDIFFG = -0.05` 比本 skill 的推荐松 5 倍**：`decide.md:847`（§12.3）推荐 `-0.01`，并强调"真正不能动的是 `EDIFF = 1E-7`"。
   A32 的模板**没有提 `EDIFF`**，也没给任何算例结果 ⇒ `[待核对]`。见 §4 的 C9。
2. **只取最大虚频**（A32:111）⇒ 与 A29 同一个限制：如果初始结构有 2 个虚频，脚本只给你其中一个，IDM 仍可能爬错 saddle。
3. **原子数/顺序必须与 `POSCAR_relax` 一致**（用 `len(model)` 截取，A32:118）。
   若两者原子数或顺序不同，位移会**错位贴到别的原子上，而且不报错** ⇒ 静默失效。
4. **块起点取的是"最后一次"出现的 `Eigenvectors after division by SQRT(mass)`**（A32:97-99 的循环不 `break`）。
   如果目录里做过多次频率（续算），要确认拿到的就是你想要的那一次。
5. `POTIM = 0.05`（IDM 步）也是作者个人取值，无出处 ⇒ `[待核对]`。

---

### 3.4 A31 —— 把 VTST 编进 VASP

#### 3.4.1 为什么编、前提是什么

【原文】VASP 自带的过渡态搜索"不强大，没法解决我们的实际计算问题"（A31:20）。编译的两个关键前提（A31:13-17）：

1. **VASP 本身能顺利编译** —— "如果这一步你还没搞定，就打算直接编译 VTST，会导致你不知道问题从哪里来"（A31:22, 151）；
2. **严格按官网说明一步步来**（A31:17, 24）；VTST 的编译命令跟 VASP 一样是 `make`（A31:22）。

#### 3.4.2 ⚠️ 版本/接口要求（本组最容易踩的一条）

【原文】A31:30-40：解压后**三套文件对应三类 VASP**：

| vtstcode 位置 | 对应 VASP 版本 |
|---|---|
| `vtstcode5/` | VASP **5**（子版本尽量用最新的 5.4.4） |
| `vtstcode6.1/` | VASP **6.1 与 6.2** |
| 上面**两个文件夹之外**的文件 | VASP **6.3** |

作者的取舍建议：VASP5 升 VASP6 要额外花钱 ⇒ 有 VASP5 版权就用 `vtstcode5`；
6.1/6.2 升 6.3 不花钱且 6.3 支持机器学习 ⇒ 直接用 6.3，"vtst6.1 这个文件夹，直接删掉就 OK"（A31:38-40）。

**接口级要求（改 `main.F`）**：

- **VTST v2.04 及以后**必须改 `src/main.F`：把
  `CALL CHAIN_FORCE(T_INFO%NIONS,DYN%POSION,TOTEN,TIFOR, & LATT_CUR%A,LATT_CUR%B,IO%IU6)`
  改成
  `CALL CHAIN_FORCE(T_INFO%NIONS,DYN%POSION,TOTEN,TIFOR, & TSIF,LATT_CUR%A,LATT_CUR%B,IO%IU6)`
  （即多传一个 `TSIF` 实参）（A31:60-69）。
- **VASP 6.2 还要再换一行**：`IF (LCHAIN) CALL chain_init( T_INFO, IO)` → `CALL chain_init( T_INFO, IO)`（A31:70-75）。
- **vasp.6.2.1 需要 vtstcode 4.1 (revision 182)**（A31:76）。

【原文】⚠️ 作者对 6.3 的态度是**不确定的**，值得原样保留这种不确定性：
"至于 6.3 是不是跟 6.2 一样？可以编译 2 个版本，一个替换，一个不替换，然后对比下。
**本人测试的结果是，如果不替换，编译会失败。**"（A31:79）⇒ 标 `[经验]`，且只对作者当时的 vtstcode 快照成立。

**接口级要求（改 `src/.objects`）**：

【原文】官网说的 `variable SOURCE`，"指的就是 `src` 目录里面的 `.objects` 文件，这个文件前面带 `.`，是隐藏的"（A31:94-96）。两条硬顺序（A31:100-102）：

1. `dynmat.o, neb.o, dimer.o, lanczos.o, instanton.o` 必须在 **`chain.o` 之前**；
2. `sd.o, cg.o, qm.o, lbfgs.o, bfgs.o, fire.o` 必须在 **优化器驱动 `opt.o` 之前**。

作者给的粘贴位置是 `chain.o` 之前、紧接 `tetweight.o`/`hamil_rot.o`（A31:105-110），并提醒"**不要随便改顺序**"（A31:112）。

#### 3.4.3 完整流程（A31:113-124）

```
cp <你的 VASP 源码目录> <同目录>_vtst     # 整份备份：原生版与 VTST 版并存
cd <...>_vtst
cp <解压出的 vtstcode>/vtstcode<版本>/*  src/
vi src/main.F                          # 按 §3.4.2 替换
vi src/.objects                        # 按 §3.4.2 插入并保证顺序
make
```

⚠️ 作者原文里的 `cp 5.4.4  5.4.4_vtst` 是他自己的**目录名**，消费层只能写 `<你的 VASP 源码目录>`（红线 §7.1）。

#### 3.4.4 验证（一条命令）+ 常见失败

**判据**：`grep VTST -A 10 <某个小算例>/OUTCAR`（A31:128），正常会打印（A31:134-144）：

```
VTST: version 3.2, (02/03/18)

 CHAIN: initializing optimizer
 OPT: Using Conjugate-Gradient optimizer
 OPT: CG, Init
 OPT: CG, FDSTEP      0.005000
 OPT: CG, MAXMOVE      0.200000
 CHAIN: Read ICHAIN            0
 CHAIN: Running the NEB
```

⇒ 看到 `VTST: version ...` 横幅 = VTST 真的被编进去了。
（`playbook.md:1403` 记的另一种判据是 `grep RMS OUTCAR`；两条**不冲突、可同时用**，见 §4 的 C8。）

**常见失败（我按 A31 归纳的五条）**：

| # | 症状 | 原因 | 出处 |
|---|---|---|---|
| 1 | 编译报错，但分不清是谁的错 | VASP 本身没编过 | A31:22, 151 |
| 2 | 编译失败 | VASP 6.2/6.3 少替换 `chain_init` 那一行 | A31:79（作者实测） |
| 3 | 链接/符号相关报错 | `.objects` 里对象顺序放错（`chain.o` / `opt.o` 的相对位置） | A31:100-112 |
| 4 | 编出来的不是你要的东西 | vtstcode 目录与 VASP 版本没配对 | A31:30-40 |
| 5 | 跑起来没有 VTST 行为 | 用的是没编 VTST 的那个可执行文件（作者建议整份复制目录以防混淆） | A31:49 |

⚠️ A31:159 是作者对"下载地址/运行案例/提交命令/编译失败怎么办"这类问题的**拒答**（且带联系方式）。本 skill 应把"编译失败怎么排查"按上表补齐，而不是照抄拒答。

---

### 3.5 A24 —— 离子迁移概率密度可视化

#### 3.5.1 要什么输入

- **必须有的输入**：**`XDATCAR`**（来自一次 AIMD 计算）（A24:102；脚本实物 `A24/test.py`）。
- **必须有的软件**：`pymatgen` + **`pymatgen-diffusion` 插件**（A24:30, 34-48）。
- **辅助输入**：AIMD 的温度与 `POTIM`（要传给 `DiffusionAnalyzer`）；算例传的是 `900` 与 `2`（A24:103）。

#### 3.5.2 怎么算（四步，A24:97-105）

```python
traj = Trajectory.from_file('XDATCAR')                                   # 1 读轨迹
diff = DiffusionAnalyzer.from_structures(traj, 'Li', 900, 2, 1)          # 2 扩散分析（离子/温度/POTIM/step_skip）
pda  = ProbabilityDensityAnalysis.from_diffusion_analyzer(               # 3 投影成三维概率密度
           diff, interval=0.5, species=("Li"))
pda.to_chgcar(filename="pda.vasp")                                       # 4 写成 CHGCAR 格式
```

参数语义（对照 `A18:189-193` 的同名调用）：`'Li'` = 研究哪种离子；`900` = 温度（K）；
`2` = `POTIM`（fs）；`1` = `step_skip`（间隔步数）。`interval=0.5` 文中**没写单位** ⇒ `[待核对]`。
文中还给了另一条入口：从官方 notebook 的 **json** 反序列化 `DiffusionAnalyzer` 再投影（A24:74-88）。

#### 3.5.3 输出长什么样（`[算例]` 我打开了实物文件）

`things to study2/LVTHW-master/source/_posts/A24/pda.vasp`：

- 第 1–8 行是 **POSCAR 头**：注释行 `Li60 Sn16 S64`、缩放 `1.00`、3 行晶格、元素行 `Li S Sn`、计数 `60 64 16`、`direct`（`A24/pda.vasp:1-8`）；
  ⚠️ **注释行写的是 `Li60 Sn16 S64`，元素行却是排序后的 `Li S Sn`** —— 在 VESTA 里看到的原子叠放顺序与注释行不一致，别被注释行误导（推论）。
- 随后 140 行原子坐标（60+64+16），空行后是**网格与体数据**：`26 32 29`（`A24/pda.vasp:150`）。
- 体数据的数值量级在 0 ~ 1.3×10²（`A24/pda.vasp:151`）⇒ **不是归一化到 0–1 的概率**，
  具体归一化口径文中没写 ⇒ `[待核对]`。**只把它当相对分布看，别读绝对值。**

#### 3.5.4 结果怎么读（作者引文献给出的四条判据，A24:22-26）

| 图上的形态 | 物理结论 |
|---|---|
| 概率密度沿某个方向连成**通道**，且通道连通性好 | 迁移势垒低（文中例子 **0.22 ~ 0.25 eV**） |
| 概率密度铺成**三维网格**，且分布更均匀 | 势垒更低（例子 **0.18 ~ 0.19 eV**） |
| 概率密度**只在特定位点附近成团** | 离子**不能**有效移动 |
| 概率密度呈现**局域化**行为 | 同样不行 |

文献原话（作者引用）："扩散网络里所有位点应当能量上彼此接近，并且要用大通道把它们连起来"（A24:26）。
出处：Wang et al., *Nature Materials* **2015**, *14*, 1026–1031（A24:18）。

#### 3.5.5 限制

1. **成本在 AIMD 而不在后处理**：后处理"大概耗时 8 分钟，因机器而异"（A24:108），但前面必须有一段足够长的 AIMD。
2. **温度与 `POTIM` 必须与 AIMD 实际设置一致**（A24:103 的 `900`/`2` 就是 `TEBEG`/`POTIM`；对照 A18:92-94 的 INCAR）。
3. **作者的安装方式是土办法**：把解压出的 `pymatgen_diffusion` 目录**手工丢进 Anaconda 的 `site-packages`**（A24:44-46）
   ⇒ 绕过 pip，容易与 pymatgen 版本打架；正规做法应走 pip/conda。
4. **作者的 import 路径是否还在**：`pymatgen.analysis.diffusion_analyzer`、`pymatgen.core.trajectory`
   （A24:74, 98-100）在新版 pymatgen 上是否仍存在，本 skill **未核实** ⇒ `[待核对]`。
   同理 A18:180 的 `from pymatgen import Structure`（顶层导入）是**很老的写法**。
5. **网格分辨率由 `interval` 定**：本例 26×32×29（`A24/pda.vasp:150`）；`interval` 越小越贵、体数据越大（推论）。

---

### 3.6 A28 / A19 / A20 / A18 —— 四个"取数/造结构"工具

#### 3.6.1 A28 通过 ASE 取原子间距离

| 项 | 内容 | 出处 |
|---|---|---|
| **用途** | 量两个原子的距离，**并且正确处理周期性边界** | A28:15 |
| **输入** | `POSCAR`（可改成 `CONTCAR` 或其他带坐标的文件）+ 两个原子序号 | A28:60, 75 |
| **核心调用** | `model.get_distance(a, b, mic=True)` / `mic=False` | A28:62-63 |
| **输出** | 两个数：考虑最小镜像的距离、直接量的距离 | A28:65, 84 |
| **算例** | 同一对原子：`mic=True` → **3.8175 Å**；`mic=False` → **7.4611 Å** | A28:84 |
| **⚠️ 序号基准** | **ASE 下标从 0 开始**；p4vasp 显示的是从 1 开始的序号（Pt 109→108、Ti 23→22） | A28:33, 57, 74 |
| **等价实现** | `mic=False` 等价于自己用 numpy 算 `norm(coord_A − coord_B)` | A28:68-71, 77 |

**限制**：
- `mic=True` 只做**最小镜像**（找一个最短的周期像），它**不判断这个短距离在物理上是否有意义**
  （推论：薄 slab/大分子的真空层若小于另一方向的重复距离，可能给出"穿过真空"的假短距离）⇒ `[待核对]`。
- 作者的建议仍以**建模阶段**为先："最理想的情况就是模型搭建的时候将这一情况考虑进来，尽可能把分子放在 slab 的中间部分"（A28:27）。
- 脚本用 `sys.argv[1:3]` 强制要两个参数，**没做参数校验**；缺参会直接抛 `IndexError`（推论）。

#### 3.6.2 A19 ASE 扩胞

| 项 | 内容 | 出处 |
|---|---|---|
| **用途** | 把优化好的小胞扩成大胞（作者的理由：直接优化刚切好的大胞更费时间，先优化 1×1 再扩到 4×4 再优化"相对来说快一些"） | A19:22 |
| **用法** | `expand.py CONTCAR 4 4 1`（沿 x/y/z 三个方向的**整数**倍数） | A19:31, 64, 76 |
| **核心调用** | `read_vasp("CONTCAR")` → `cell*(x,y,z)` → `write_vasp("POSCAR", direct=True, sort=True)` | A19:66-67 |
| **输入/输出** | 输入 `CONTCAR`（4 个 Ru）→ 输出 `POSCAR`（64 个 Ru），z 方向与真空不变 | `[算例]` `A19/CONTCAR` vs `A19/POSCAR` |

**限制（我读脚本实物发现的三条硬限制 + 两条推论）**：

1. ⚠️ **`sys.argv[1]` 被读进来但根本没用**：脚本第 11 行 `file_read = sys.argv[1]`，
   第 14 行却硬编码 `read_vasp("CONTCAR")`（`A19/expand.py:11, 14`；正文同 `A19:63-66`）。
   ⇒ 你写 `expand.py POSCAR 4 4 1` 它**照样读 CONTCAR**，而且**不报错**（静默失效）。
2. **只能是整数倍**：倍数用 `int()` 解析（A19:64），做不到 1.5× 这类非整数扩胞。
3. **只支持对角超胞**（`cell*(x,y,z)`），不支持任意超胞矩阵（如 √3×√3、含切变的超胞）。
4. 推论：`sort=True` 会**按元素重排原子**。若你原结构带 `Selective dynamics` 的 `T/F`、
   或后续要用 `LDAUL`/`LDAUU`/`MAGMOM` 这类**按 POSCAR 元素顺序对位**的标签，
   重排后必须重新核对（对照算例：`CONTCAR` 里前三行是 `F F F / F F F / T T T`，
   扩完的 `POSCAR` 前两行变成 `F F F / T T T`，顺序确实变了）。⇒ `[待核对]`
5. 推论：扩胞**不打破对称性**。若 1×1 优化落在一个高对称解上，4×4 的优化很可能停在同一个高对称解；
   要允许重构/低对称吸附构型，扩胞后需要人为扰动或降低对称性。⇒ `[待核对]`

#### 3.6.3 A20 SMILES → XYZ/POSCAR

| 项 | 内容 | 出处 |
|---|---|---|
| **用途** | 只知道一个分子的 SMILES 字符串，就想得到 3D 结构（xyz 与 POSCAR） | A20:35, 47 |
| **输入** | `smiles_to_xyz.py '<SMILES>' <输出前缀>`；四个示例：`[CH3]`、`CCO`、`C`、`c1ccccc1` | A20:108-111 |
| **输出** | `<前缀>_ase.xyz` 与 `<前缀>_POSCAR` 两个文件 | A20:98-99, 113 |
| **核心两步** | ① Openbabel：`pybel.readstring("smi", smiles)` + `make3D(forcefield='mmff94', steps=100)`；② ASE：建 16×17×18 Å 的周期盒子、把原子逐个塞进去、`center()`、写文件 | A20:78-99, 140, 169 |
| **依赖** | `openbabel` + `ase`(+`numpy`)；作者给的是 conda 装法 | A20:20-28 |

**限制（逐条按代码读出来的）**：

1. **3D 构型来自力场，不是 DFT**：`make3D` 用 **MMFF94** 力场优化 **100 步**（A20:79, 140）。
   ⇒ 几何质量 = 力场质量；`steps=100` 是否收敛，文中没验证 ⇒ `[待核对]`。
   ⇒ 只能当**初始结构**，必须自己做 DFT 优化（对照 A20:187 作者的提醒）。
2. **盒子尺寸硬编码 16×17×18 Å**（A20:85, 169）。分子一大，周期像之间就会重叠 ⇒ 必须自己检查/改大。
3. **周期边界直接设 True**（A20:86）⇒ 产物天生是**周期体系**；要算孤立分子得自己改成非周期。
4. **`FixAtoms` 用不存在的元素 `'XX'` 来"固定零个原子"**（A20:95, 177）：
   `indices=[atom.index for atom in geo if atom.symbol == 'XX']` 恒为空表 ⇒ 效果是"全部放开"。
   推论：这是个**技巧**不是**保证** —— 依赖"ASE 里确实没有 XX 元素"这一事实。`[待核对]`
5. **含过渡金属的 SMILES 未必能跑**：MMFF94 的参数覆盖面有限，作者没给金属体系的例子 ⇒ `[待核对]`。
6. **必须人工检查结构合理性**（作者原话，A20:187）："不要搭建完结构就立刻提交任务，先认真检查一遍。"
   ⇒ 这条其实是本篇最该进知识层的一句（与 `playbook.md` 的"症状→处方"精神一致）。

#### 3.6.4 A18 Pymatgen 算离子电导率

| 项 | 内容 | 出处 |
|---|---|---|
| **用途** | 从 AIMD 轨迹算固态电解质的离子电导率 σ | A18:32, 38 |
| **输入** | `XDATCAR`（一次或多次续算拼起来的）+ 温度 + `POTIM` + `step_skip` + 研究哪种离子 | A18:103-109, 186-193 |
| **方法链** | AIMD → 平均 MSD → 自扩散系数 → Nernst-Einstein 电导率 | A18:38, 51-73 |
| **公式** | `averageMSD = ⟨[r(t)]²⟩`（对 N 个离子与 t₀ 平均）；`Ds = averageMSD/(2dt)`；`σ = n e² Z² Ds / (k_B T)` | A18:53-73 |
| **输出** | `diff.conductivity`，单位 **mS/cm**；写进 `result.dat`（温度 + 电导率） | A18:199-205 |
| **算例结果** | 900 K 时 **884.05 mS/cm** | A18:223, 226 |
| **AIMD 降本四件套** | 截断能：**氧化物 400 eV / 硫化物 280 eV / 硒化物 270 eV**；**Gamma 点 + gam 版 VASP**；**单胞**（原子多时）；**步长 2 fs（`POTIM = 2`）** | A18:42-48 |

**AIMD 的 INCAR（算例原文，A18:86-101）**：
`ISTART=0 / ICHARG=2 / IBRION=0 / ISIF=2 / NPAR=8 / NSW=30000 / TEBEG=900 / PREC=N / POTIM=2 / SMASS=0.0 / NELMIN=4 / LWAVE=F / LCHARG=F / IALGO=48 / LREAL=A`

**限制 / 坑**：

1. ⚠️ **"NVT" 与 `SMASS = 0.0` 自相矛盾**：正文说"用 NVT 系综第一性原理分子动力学"（A18:38），
   但同一篇贴出的 INCAR 里是 `SMASS = 0.0`（A18:95）。
   按本 skill 的理解 `SMASS = 0` 是 **NVE**（微正则，`TEBEG` 只给初温）⇒ 温度会漂移；
   而 A18:193 又把 `900` 当成**真实温度**喂给 Nernst-Einstein 公式 ⇒ σ 可能偏。
   **本 skill 未核实到官方明文** ⇒ `[待核对]`（自查动作见 §4 的 C6）。**不得**据此断言作者算错。
2. **续算拼 `XDATCAR` 要手工删重复的晶格行**（A18:109）：多次续算的 `XDATCAR` 直接 `cat` 之后，
   中间会混入重复的晶格信息行，必须手工删掉 —— 否则轨迹解析会错。
3. **σ 公式是 Nernst-Einstein 形式**，推论：它不含 Haven 比/关联因子（离子间关联运动），
   也不含电子电导贡献 ⇒ 对"离子-离子强关联"的体系会偏 ⇒ `[待核对]`。
4. **要 300 K 的电导率必须外推**：作者把"如何得出 300 K 下的电导率"直接列成思考题（A18:239）
   ⇒ 常用做法是 Arrhenius 外推，但**本文没给**。
5. **【经验】降本四件套没有收敛测试支撑**：那三个截断能是作者给的数值（A18:44），
   没说做过收敛测试、也没说适用的泛函/赝势 ⇒ 只能当"起始值"，标 `[待核对]`。

---

### 3.7 A25 / A26 / A27 / A33 —— 材料数据库与机器学习工具

#### 3.7.1 A25 matminer 是什么

【原文】matminer 是"用于材料数据挖掘的基于 Python 的开源软件"（A25:19），能做四件事：
① 从各种数据库获取材料属性数据；② 把复杂材料属性（成分、晶体结构、能带结构）表征为与物理相关的**特征量**；
③ 训练机器学习模型；④ 分析数据挖掘结果（A25:19）。
它"使用 pandas 数据格式"，另有一个自动化版本 **Automatminer**（A25:21）；
可访问 **Citrine / Materials Project / MDF** 等库（A25:23）；由 Pymatgen 开发者开发（A25:15）。

**安装与坑**（A25:29, 33-50）：`pip install matminer` 即可，但作者**特意建了 `python=3.6` 的虚拟环境**
（`conda create -n py36 python=3.6`）再 `conda install -c conda-forge pymatgen` + `pip install matminer`
⇒ 推论：matminer 有**较严的 Python/pymatgen 版本要求**，不建议装进主环境。`[待核对]`

#### 3.7.2 A26 matminer 从 MP 取数（本组最像"方法论"的一篇）

**怎么取**（A26:17-25, 31-37）：

```python
from matminer.data_retrieval.retrieve_MP import MPDataRetrieval
mpdr = MPDataRetrieval(api_key='<你自己的 key>')
df = mpdr.get_dataframe(criteria={...}, properties=[...])   # 返回 pandas DataFrame
```

- `criteria` = 搜索条件的字典，可以有多个键值对；`properties` = 想要的性质列表；
  **`criteria` 其实也是材料的性质**（A26:39）。
- **操作符**（A26:65-67, 99, 127-128）：
  `{"$gt": 4.0}` 大于、`{"$lt": 1e-6}` 小于、`{"$exists": True}` 存在、
  `{"$in": [...]}` 属于、`{"$all": [...]}` 全都含。
  作者的提示很实用："带隙大于 4.0，greater than 缩写成 gt，在 matminer 中要写成 `$gt`"（A26:65）。
- **可用的性质名**要去 pymatgen 的 `matproj.py` 里查（A26:39）。

**三个示例的实际产出**（可当量级参考）：

| 示例 | criteria | 结果 |
|---|---|---|
| 1 | `{"nelements": 1}`，要 `density` + `pretty_formula` | **716 条**单元素材料（A26:50） |
| 2 | `{"band_gap": {"$gt": 4.0}}`，要 `pretty_formula` + `band_gap` | 结果用 `df.to_csv('materials_bg_gt_4.csv')` 存档（A26:67, 89） |
| 3 | `{"elasticity": {"$exists": True}, "elasticity.warnings": []}`，要 `K_VRH` + `G_VRH` | 只保留**没有警告**的弹性数据；用 `df.describe()` 统计（A26:101-104, 114) |
| 4 | 再加 `{"elements": {"$all": ["Pb","Te"]}, "e_above_hull": {"$lt": 1e-6}}`，还要 `bandstructure` + `dos` | **只有 3 条**（A26:130-143） |

**坑（都很实用）**：

1. **数据质量过滤要用 `elasticity.warnings: []`**（A26:99, 101）。
   ⇒ 推论：MP 里的弹性数据**带警告标记**，不滤掉就会把不可靠的数据算进统计。
   这是一条能推广到其它属性的做法：**先滤质量标记，再谈物理**。
2. **性能坑：要 `bandstructure` / `dos` 这种大对象会非常慢**。
   作者原话："`e_above_hull < 1e-6` … `# to limit the number of hits for the sake of time`"（A26:133）
   ⇒ **先用便宜的 criteria 把条数压下来，再取重属性**。
3. **`df['density'].count()` 计的是非空值个数**（A26:35），不是行数 ⇒ 有缺失值时两者不等（推论）`[待核对]`。
4. 作者对 pymatgen 作图有意见："Pymatgen 做的能带和 DOS 图不够美观"（A26:170）
   ⇒ 出图仍建议走自己的流程（本 skill 的 `postprocess.py` 同理）。

#### 3.7.3 A27 从 Citrine 取数

- **要先装客户端**：`pip install citrination_client`，"否则会报错"（A27:17）。
- **要 api_key**（A27:13, 27）。
- 示例 1：`cdr.get_dataframe(criteria={'formula':'Si','data_type':'EXPERIMENTAL'}, properties=['Band gap'], secondary_fields=True)`
  → **命中 7 条**实验带隙；返回字段带 `references`/`units`/`conditions`/`methods`/`dataType`（A27:33-49, 60）。
- 示例 2：`criteria={}` 只给 `properties` 就能返回全部 → *OH 吸附能 **9 条**、*O 吸附能 **21 条**（A27:70-71, 88）。
- ⚠️ **数据稀疏是主要限制**：作者直接说"这些数据库里面的数据还不够丰富"（A27:111）⇒ 不适合当高覆盖率的训练集。
- ⚠️ **库版本漂移**：输出里带 `pandas.io.json.json_normalize is deprecated` 的 FutureWarning（A27:39-41, 74-76）
  ⇒ 说明示例代码锁在一个老版本组合上；照抄会持续吃 deprecation 警告，未来可能直接失效。
- ⚠️ **字段名脆弱**：查询用小写 `'adsorption energy of OH'`（A27:70），
  但返回的字段是首字母大写的 `'Adsorption energy of OH'`（A27:82）⇒ 依赖 API 的大小写不敏感行为，脆弱（推论）。

#### 3.7.4 A33 matminer + pymatgen 取 MP 结构

- 两条路：`MPDataRetrieval.get_dataframe(..., properties=['pretty_formula','cif'])`（A33:19-21）；
  或 `MPRester(api_key=...).get_structure_by_material_id('mp-1009018')` + `CifWriter(...).write_file('Cu.cif')`（A33:26-37）。
- ⛔ **本篇正文第 16 行直接写死了一个真实 `api_key`**（`MPDataRetrieval(api_key='...')`）。
  这违反本站红线 §7.1/§7.2 的精神（密钥不进仓库）—— **本报告不复制该字符串**。
  作者自己在第 17 行又写"自行查阅自己的 api_key"，第 29 行给了 `"XXX"` 占位 ⇒ **前后自相矛盾**，
  正确写法只有一种：**从环境变量/本地配置文件读，绝不进代码、绝不进 git**。
- ⚠️ **示例文案与 criteria 不一致**：`print` 里写 `"There are {} entries on MP with 2 element"`（A33:22），
  但 criteria 是 `{"nelements": 1, ...}`（A33:19）⇒ **别信示例里的文案，只信 criteria 与返回值**（推论）。
- ⚠️ 本篇的代码**没有用代码块围起来**（A33:13-37 是裸 markdown）⇒ 直接复制粘贴容易混入说明文字。
- ⚠️ MP 的旧 REST API（`MPRester(api_key=...)`）与新 API 的差异、配额/限速，文中完全没提
  ⇒ 本 skill **未核实**其当前可用性，标 `[待核对]`。

---

### 3.8 A21 / A22 / A23 —— 软件安装类（**如实判定：大部分是那台机器的操作记录**）

> 任务要求"不要为了凑数硬写"。下面逐篇给结论，**写不出普适知识就直说**。

#### 3.8.1 A21 Ubuntu20 装 p4vasp —— **绝大部分是操作记录**

**能提炼的只有两条**：

1. **【可迁移方法】当软件依赖已被发行版移除的旧运行库时，去发行版的 archive pool 手动取旧 `.deb`，并按依赖顺序安装。**
   【原文】p4vasp 要 `python-gtk2` 与 `python-glade2`，现代 Ubuntu 仓库里没有，
   作者从 `archive.ubuntu.com/.../pygtk/` 下 deb；并强调"**先安装 gtk2，再安装 glade2**"（A21:40-44）。
2. **【可迁移的教训】"某一步报错可以忽略"这句话必须自己验证。**
   【原文】`bash install/install-ubuntu-dependencies.sh` 最后可能出 `python-epydoc` 报错，"可以忽略"（A21:61）。
   推论：这类"可以忽略"如果不自己确认它没影响后续步骤，就会变成静默失败。⇒ `[经验]`

**本篇给出的一条结论性判断（有决策价值）**：
【原文】"P4vasp 是一款基于 Python2 的…软件。由于 Python2 已经被时代所淘汰，p4vasp 官网也不见任何的针对 python3 的更新改进，**这个软件估计要凉**"（A21:12）。
⇒ **新项目不要依赖 p4vasp**。本组 A17/A28 里 p4vasp 只用来"看原子序号"，可视化的现代替代是 VESTA / ASE gui。

**其余全部是那台机器的操作记录**：`apt-get install gcc make / python2-dev / libxft-dev / libglfw3-dev / libgl1-mesa-dev / libglu1-mesa-dev`、`bash install.sh`（A21:31-56）。
⇒ **不提炼。** 本 skill 也不该教用户去装一个官方已放弃的 Python2 可视化软件。

#### 3.8.2 A22 Ubuntu 虚拟机安装 —— **主体是逐屏点击记录，只有"思路"可迁移**

**可迁移的 5 条（都是思路/经验，不是 VASP 知识）**：

| # | 可迁移的方法 | 原文出处 |
|---|---|---|
| 1 | **用虚拟机做隔离环境**：老版本/有风险的可视化软件装在 guest 里，不污染主机 | 全文立意；A22:15 |
| 2 | **整个系统就存在一个 vdi 文件里** ⇒ 换机器直接导入 vdi，不用重装；备份 = 拷 vdi | A22:55 |
| 3 | 资源共享三件套：Guest Additions（分辨率自适应、剪贴板双向）＋ 共享文件夹 | A22:145-165, 177, 187 |
| 4 | **共享文件夹挂载点没权限的解决办法**：`sudo adduser $USER vboxsf` 然后**重启**；若重启失败且报 USB 相关错误，就取消 USB 选项再启 | A22:210-217 |
| 5 | 【经验】资源分配：内存与 CPU 各给 host 的一半（太小 guest 卡死，太大 host 卡死） | A22:41, 67 |

**不可迁移（纯操作记录）**：VirtualBox 的每一个向导页面、每个对话框选什么（A22:31-140）。
⇒ **不提炼。** 并应明确：这些与 VASP 计算本身无关，**不属于本 skill 的知识范围**，
最多作为"如果你必须在本地跑老式可视化软件"的一条附注。

#### 3.8.3 A23 Ubuntu 常用软件 —— **有 1 条四要素齐全的"静默失效"，值得进 playbook**

**⭐ 值得进决策库的一条（完整四要素）**：

> **症状**：装完 Anaconda 之后，原本能用的 `p4v` 命令报
> `File ".../p4v.py", line 9 ... print """You need to get version 2.0 (or later) of PyGTK ...""" ^ SyntaxError: invalid syntax`（A23:121-126）。
> **诊断**：`p4v` / `p4v.py` 是 **Python2 脚本**，里面写死了 `python`；
> 而 Anaconda 把 `python` 变成了 PATH 里的 Python3 ⇒ 用 Python3 去解释 Python2 的 `print "..."` 语句，必然 SyntaxError（A23:112, 116-118）。
> **处方**：把 `p4v` 脚本里的 `python` **全部**改成 `python2`，并把 `p4v.py` 第一行的解释器也改成 `python2`（A23:114-118）。
> **判据**：`grep python "$(which p4v)"` 应显示 `exec python2 ...`；`grep python "$(which p4v.py)"` 应显示 `#!/usr/bin/env python2`（原文写的是 p4v 所在的系统目录，A23:132-136）。
> **为什么这条值钱**：这是典型的**"装了别的软件把原来能跑的东西弄坏了、而且看起来像是软件本身坏了"**。
> 迁移到任何"Python2 遗留工具 + 现代 conda/venv"场景都成立（例如老的 vaspkit 版本、老的 VASPsol 脚本）。
> **代价 / 例外**：改系统目录下的脚本属于"打补丁"，升级/重装软件会被覆盖；更稳的做法是给自己留一份 wrapper
> （推论，`[待核对]`）。**证据**：`[经验]` `A23:112-140`。

**其余可迁移的 4 条（都是"工具用法"，不是 VASP 知识）**：

1. `~/bin` 用来放自写脚本与可执行小程序，勤备份、不占空间（A23:17-23）。（与 A28:102-114、A29:119 的做法一致。）
2. `sshfs` 把服务器目录挂到本地，方便传数据（A23:61）。
3. `xclip` 把命令输出丢进剪贴板；`rename` 批量改名；`tree` 看目录树（A23:63-73）—— 都是效率工具。
4. **免安装（绿色）软件挂 PATH 的通用做法**：解压后在 `~/.bashrc` 里
   `export VESTA='<你的 VESTA 目录>'` + `export PATH=$PATH:$VESTA`，`source ~/.bashrc` 后直接敲 `VESTA`（A23:149-166）。
   【原文】作者特意提醒"上面 VESTA 的路径记得换成你自己电脑里面的"（A23:168）。
   **备份策略**：虚拟机路线备份 vdi；裸机路线备份 `~/bin` + `~/.bashrc`（A23:172-174）。

**不可迁移**：那一长串 `sudo apt-get install ...` 的具体包名清单（A23:31-53）。
它们在 Ubuntu 版本之间会变，且和 VASP 无关 ⇒ **只在需要时按需安装，不要照抄。**

---

### 3.9 A17 —— ASE 格式转换（含一条**会让 POTCAR 顺序核对失效**的坑）

**可迁移方法**：

- `ase gui <输入文件> -o <输出文件>` **一条命令做格式转换**：mol→xyz（A17:46）、cif→xyz（A17:109）、cif→POSCAR（A17:129）。
- 官方更规范的写法是 `ase convert -i mol -o xyz <in> <out>`（A17:66-70）—— `ase gui -o` 每次都会打一行
  `UserWarning: You should be using "ase convert ..." instead!`（A17:47, 71）。
- `ase gui <单个文件>` 直接可视化（A17:74）。
- 【原文】把输入文件"用文本编辑器打开、认真分析下它们的数据结构"是作者反复强调的前置动作（A17:80）。

**⚠️ 最有价值的一条坑（会静默改变下游校验）**：
【原文】ASE 写出的 POSCAR **默认没有元素行**（只有一行注释），作者把它称作"类似于 VASP4 的 POSCAR 格式"（A17:156）。
实证：第一次输出（A17:132-139）的第 1 行是 ` C  O `（注释），第 5 行是计数 `4  8`，第 6 行直接是 `Cartesian`；
打完补丁后（A17:183-189）第 6 行才出现真正的元素行 `   C   O`。
**为什么重要**：没有元素行，就无法核对"**POSCAR 的元素顺序 ↔ POTCAR 的拼接顺序**"——
而本 skill 的 `validate.py` 正是拿元素行做这项跨文件硬约束核对（`AGENTS.md` §7）。
⇒ **处方**：写文件时显式给 `vasp5=True`（A20:99 与 A29:110 就是这么写的）；
**不要**照抄作者"去改 ASE 源码里的 `vasp5 = False`"（A17:162-166）—— 改第三方库源码会在升级时失效（推论）。

**⚠️ 顺带纠一处**：A17:156 说"ASE 输出的 POSCAR 总是把元素行放在第一行的位置，类似于 VASP4 的 POSCAR 格式"
—— **这句把 VASP4/VASP5 说反了**：VASP5 才在注释行之后多一行元素行。
以输出实证（A17:133-139 无元素行 vs A17:183-189 有）与 `[官方]` POSCAR 页的口径为准。→ §4 的 C7。

---

### 3.10 A30 VASP 官方视频 —— **无计算知识**

【原文】VASP 官方在 Youtube 开了频道，当时有 9 个视频、下载后约 1G、关注人数 300 多（A30:16）。清单（A30:20-36）：

```
1 Advanced_methods_of_molecular_dynamics_VASP_Lecture
2 Basics_of_machine_learning_force_fields_VASP_Lecture
3 Electronic_Convergence_VASP_Lecture
4 Hybrid_functionals_VASP_Lecture
5 Introduction_to_ab_initio_simulation_in_VASP_VASP_Lecture
6 Introduction_to_molecular_dynamics_VASP_Lecture
7 py4vasp_04_release
8 Symmetry_and_sampling_in_reciprocal_space_VASP_Lecture
9 VASP_6.3_release
```

作者的判断：除 7（`py4vasp`）和 9（VASP 6.3 发布）之外，其余 7 个都是 1 小时以上的干货（A30:38）。

**本篇可迁移的只有"资源地图"这一件事**，没有任何计算判据。⚠️ 而且它是 **2022-04 的快照**，
视频数量/标题/时长都会变 ⇒ `[待核对]`。下载方式依赖公众号（A30:46），**不进消费层**。

---

## §4 与现有知识层的差异 / 冲突，以及"零依赖"分界

### 4.0 先给结论：本组对既有知识层主要是**补缺口**，不是推翻

18 篇里只有 4 篇（A29/A32/A31/A34）与既有决策库/手册**直接重叠**，
其余 14 篇（A17–A28、A30、A33）在 `decide.md` / `playbook.md` / `learn_L*.md` 里**基本没有对应条目**
—— 也就是说本组**新开了"VASP 生态工具与脚本"这一整块**。

### 4.1 冲突与差异（每条按「LVTHW 怎么说 | 现有知识层怎么说 | 我建议怎么裁定 + 理由」）

#### C1 「Improved Dimer 到底用什么标签」

- **LVTHW 怎么说**：IDM 已经编译在 VASP 里、不需要额外编译，只要 `IBRION = 44`（A32:15, 17）。
- **现有知识层怎么说**：`decide.md:786` 的表格里，"**Improved Dimer**" 一行的关键标签写的是 `ICHAIN = 3`, `IBRION = 3`。
- **我建议怎么裁定**：**拆成两行**。
  理由：`[官方]` `references/official/pages/IBRION.md` 第 1 行的取值表里含 `44`，第 24 行写 `IBRION 44 improved dimer method`，
  第 66 行写"用 improved dimer method 可以从相空间里任意一个结构出发搜索过渡态"。
  ⇒ **VASP 原生的 IDM = `IBRION = 44`（不需要 VTST）**；而 `ICHAIN` 家族是 **VTST 的路线**。
  现有表格把两者混成一行，会让读者以为"想用 Improved Dimer 就必须编 VTST"。
  建议改成：
  | 方法 | 关键标签 | 依赖 | 出处 |
  |---|---|---|---|
  | Improved Dimer（VASP 原生） | `IBRION = 44` | **不需要 VTST** | `[官方]` `IBRION.md:24, 66`；`[经验]` A32:15-17 |
  | Dimer（VTST 路线） | `IBRION = 3`, `POTIM = 0`, `ICHAIN = 2`, `IOPT = 2` + `MODECAR` | 需要编了 VTST 的 VASP | `[算例]` `decide.md:795-796` |
  ⚠️ **`ICHAIN = 3` 究竟对应哪个算法，本 skill 未核实**（`ICHAIN` 在 wiki 上没有独立页面，见 `decide.md:789-792`）⇒ `[待核对]`。
  **不要**据本报告把 `ICHAIN=3` 改成别的值。

#### C2 「虚频确认为真之后，到底怎么消」

- **LVTHW 怎么说**：**沿虚频方向把坐标平移一小段（校正因子 0.1 或 0.4），然后新建目录重新优化**（A29:15, 25, 106, 120）。
  另有一条不同路线：让 IDM 自己爬到鞍点，"这个方法也可以用来消虚频"（A32:148）。
- **现有知识层怎么说**：`decide.md:915-933`（§13.3）只给"怎么判"（数量 / 数值 / 方向 / `IBRION=7` 复核）；
  `playbook.md:330-340`（S12）的处方是"更严的优化再收一次 / 检查 `POTIM` / `IBRION=7` 复核"，
  **没有任何一条说"沿虚频方向位移"**。
- **我建议怎么裁定**：**这是缺口，补进 `playbook.md` S12 作为新处方**，并且必须带三个限定：
  ① 只适用于**极小点**优化的虚频，**过渡态多虚频时不要用**（A29:121）；
  ② **校正因子无定值**（文中 0.1 与 0.4 都出现过），只能给"因子 × 1 ≈ 位移 Å"的换算让用户自己衡量（见 §3.1.3）；
  ③ 用完**必须检查 `POSCAR_new` 的 `Selective dynamics` 标志**，别让"全 `F F F`"把结构固定死（§3.1.6 的坑 1）。
  理由：现有 S12 的处方全是"在同一个结构上再收一次"，**对真虚频（该往势阱另一边滑）无效**；
  而"沿负曲率方向位移"是唯一能在**不换算法**的前提下把鞍点/近鞍点推回极小点的做法。

#### C3 「校正因子取多少」

- **LVTHW 怎么说**：正文举例 **0.1**（A29:27）；ASE 版脚本 **0.4**（A29:106）；纯 python 版 **0.4**（A29:165）。
  作者只说"具体多大自己根据经验调"（A29:106）。
- **现有知识层怎么说**：**无**（`decide.md` / `playbook.md` 里没有"虚频位移校正因子"这个概念）。
- **我建议怎么裁定**：**明确写成"文中出现过两个值、无定论"**，不写推荐值；同时给出量纲换算（§3.1.3 的表格）
  与"模局域 ⇒ 因子≈位移 Å；模离域 ⇒ 位移远小于因子"这条限定。标 `[待核对]`。
  理由：契约 §5 要求"任何阈值都要写出处、适用体系、反例"；这里三者都缺，只能如实标注。

#### C4 「频率数组怎么切出振动模」

- **LVTHW 怎么说**：分子算熵时**丢掉最后 6 个**：`vib_energies[:-6]`（A34:64, 113）。
- **现有知识层怎么说**：`playbook.md:1340` 明确警告——VASP 的打印顺序（实频在前、虚频在后）
  只是**归纳出来的**、标了 `[待核对]`，**"稳妥做法是逐行看 `f/i` 标记，不要数前几行"**；
  `playbook.md:361-367`（S15）也要求"**虚频不计入** ZPE，逐行看 `f/i` 标记"。
- **我建议怎么裁定**：**以 playbook 的做法为准**，A34 的 `[:-6]` 只在**分子已优化到无虚频**时安全。
  建议把 A34 的写法在本 skill 里改写成三步：①逐行按 `f/i` 与实频分类；②从实频里按数值找出 6 个近零模（平动/转动投影）；
  ③剩下的才是振动模。
  理由：`[:-6]` 是一个**位置假设**，一旦分子带虚频（虚频排在末尾）就会同时切错虚频与近零实频，
  而且**不会报错**——正是契约 §4 里最值钱的那类"程序不报错但结果不对"。

#### C5 「气体熵的参考压力」

- **LVTHW 怎么说**：`get_entropy(temperature=298.15, pressure=101325)`（A34:74），
  即 **1 atm ≈ 1.013 bar**；输出里 `S (1 bar -> P) = −0.0000011 eV/K` 几乎为零（A34:99）。
- **现有知识层怎么说**：`decide.md:1051-1056`（§16.2）——液态水取**饱和蒸气压（≈0.035 bar）**下的水蒸气能量代替，
  用 `vaspkit-502-298.15-0.035-1` 计算；`[讲义]` L4 P9。
- **我建议怎么裁定**：**必须在 §17 里显式声明"用第三方热力学模块算熵时，压力要设成与你的参考态一致"**。
  理由：我复算过这条压力项的量级——`ΔS(1 bar → 0.035 bar) = −R ln(3500/100000) = +27.88 J/(mol·K) = +2.889×10⁻⁴ eV/K`，
  在 298.15 K 对应 **TΔS ≈ +0.086 eV**（`[实测]`/推论，标 `[待核对]`）。
  这与常见吸附能（0.1–0.5 eV）、OER 过电势的关注量级同阶 ⇒ **足以改变结论，且不会有任何报错**。
  ⇒ 建议同时在 `playbook.md` 的"自由能校正"工作流里加一条自查：**报 ΔG 之前，把"每个气相分子的参考压力"写下来核对一遍**。

#### C6 「AIMD 到底跑的是哪个系综」

- **LVTHW 怎么说**：正文说"用 **NVT** 系综第一性原理分子动力学"（A18:38）；
  但同一篇的 INCAR 里是 `SMASS = 0.0`（A18:95），并且第 3 步把 `900`（=`TEBEG`）当成真实温度传给 `DiffusionAnalyzer`（A18:193）。
- **现有知识层怎么说**：`decide.md` / `playbook.md` / `learn_L*.md` 里**没有** AIMD 系综与 `SMASS` 的条目
  （本组之前的资料没覆盖 AIMD 的电导率应用）。
- **我建议怎么裁定**：**登记为冲突，不裁定谁对**。
  按本 skill 的理解 `SMASS = 0` 对应 **NVE**（`TEBEG` 只定初温），此时温度会漂移，
  而 σ 公式里的 T 应当是**实际温度**；但**本 skill 未核实到官方明文** ⇒ 标 `[待核对]`。
  **自查动作**（建议写进 playbook）：跑完 AIMD 先看 OUTCAR/OSZICAR 里的**温度时间序列**是否漂移——
  用 `grep "T=" OSZICAR`（或 `TEMP`）取一列画出来；若漂移明显，σ 里的 T 取**时间平均温度**而不是 `TEBEG`。
  ⚠️ 我**没有**验证过 `SMASS=0` 就是 NVE（`references/official/pages/` 下本次未检索到 `SMASS` 页）⇒ 不要当结论用。

#### C7 「ASE 写出的 POSCAR 属于 VASP4 还是 VASP5」

- **LVTHW 怎么说**：A17:156 说 ASE"总是把元素行放在第一行的位置，**类似于 VASP4 的 POSCAR 格式**"。
- **现有知识层怎么说**：`AGENTS.md` §7 把"元素顺序 ↔ POTCAR 拼接顺序"列为要守的跨文件硬约束；
  `scripts/vasp_common.py:363-365` 用 `symbols` / `species_line_is_symbols` 区分"有没有元素行"。
- **我建议怎么裁定**：**认定 A17:156 的表述是错的**（把 VASP4/VASP5 说反了）。
  理由：实证就在同一篇里——无元素行的那次输出第 6 行直接是 `Cartesian`（A17:133-139），
  打上 `vasp5=True` 之后第 6 行才出现元素行 `   C   O`（A17:183-189）；
  按 `[官方]` POSCAR 页的口径，"有元素行"才是 VASP5 格式。
  ⇒ 消费层只写事实："**ASE 默认写出的 POSCAR 没有元素行**；写入时给 `vasp5=True` 才有。"

#### C8 「怎么确认 VTST 真的编进去了」

- **LVTHW 怎么说**：`grep VTST -A 10 <OUTCAR>`，期望看到 `VTST: version 3.2, (02/03/18)` 与 `CHAIN:`/`OPT:` 横幅（A31:128-144）。
- **现有知识层怎么说**：`playbook.md:1403`（`[答疑]` D4-P59/D4-P60）——"用 `grep RMS OUTCAR` 看有没有信息。"
- **我建议怎么裁定**：**两条都留，合并成一条双命令判据**。
  理由：两者查的是不同证据（一条查**版本横幅**、一条查 **RMS 输出**），互不冲突且互补；
  `playbook.md:1402` 已强调"`IBRION=3` + `POTIM=0` 是 VTST 生效的标志；必须用编译了 VTST 的 VASP"，
  多一个可自查的动作只会更好。**注意**：两条判据都需要**先跑一个 NEB/Dimer 小算例**才看得到输出。

#### C9 「IDM 的 `EDIFFG`」

- **LVTHW 怎么说**：脚本 docstring 的 INCAR 模板里 `EDIFFG = -0.05`（A32:77）。
- **现有知识层怎么说**：`decide.md:847`（§12.3）推荐 `-0.01`，并指出"真正不能动的是 `EDIFF = 1E-7`"。
- **我建议怎么裁定**：**按权威序，`-0.01` 优先**（`[算例]` 真实收敛算例 > 本组的个人模板）。
  理由：A32 的模板**没有给 `EDIFF`**、也**没有给任何算例结果** ⇒ 只能当"粗搜起手式"。
  建议表述：「IDM 起步可以用 `EDIFFG = -0.05` 先粗搜（`[经验]` A32:77），
  但**最终报数的那个 TS 必须收到 `EDIFFG = -0.01` + `EDIFF = 1E-7`**（`[算例]` `decide.md:847`）。」

### 4.2 ⚠️ 专门回答：**"零依赖工具链" 与 "只能作方法参考" 的分界线**

本 skill 承诺核心工具**只用 Python 标准库**（`AGENTS.md` §2），而本组大量依赖 ASE/pymatgen/matminer。
我逐条把本组的方法按"输入形态 + 计算内核"过了一遍，结论如下。

#### 分界原则（我建议用这三条判定，而不是"用不用 ASE"）

1. **输入是不是本地文本文件？**（`OUTCAR`/`POSCAR`/`XDATCAR`/`CONTCAR` → 是）
2. **计算内核是不是纯算术？**（加减乘、取 min、直方图计数、解析式 → 是；力场/DFT/网络请求/大规模线性代数 → 否）
3. **结论能不能被本地数据自查？**（能不能给出一个"改了之后红灯变绿灯"的判据）

三条都"是" ⇒ **可以进零依赖工具链**；只要有一条"否" ⇒ **只能作方法参考**。

#### 清单

| # | 本组方法 | 输入 | 计算内核 | 能否零依赖 | 裁定与理由 |
|---|---|---|---|---|---|
| 1 | **A29 消虚频位移** | `OUTCAR` + `POSCAR`（本地文本） | 字符串定位 + 逐行取列 + 坐标加减 | ✅ **可以** | ⭐ **最该进的一件**。作者自己就给了不用 ASE 的版本（A29:122-174），只需去掉 numpy。**附加条件**：必须把"只取最大虚频 ⇒ 过渡态不适用"（A29:121）与"纯 python 版会把原子全写成 `F F F`"（A29:172）这两条限制一起实现/提示，否则做成工具反而危险。 |
| 2 | **A32 生成 IDM 的 Dimer Axis Block** | 频率 `OUTCAR` + `POSCAR_relax`（本地文本） | 定位 `Eigenvectors after division by SQRT(mass)` + 截 `N` 行 + 追加 3 列 | ✅ **可以** | ⭐ 与 #1 共用同一个"虚频块解析器"。**当前 `scripts/` 里没有解析 `f/i` 的代码** —— 检索式与范围：`grep -E "f/i|imaginary|cm-1" scripts/`（`scripts/` 下 9 个 `.py`），**零命中**；含 `freq` 的命中只有 `wizard.py:138-139`（一个 goal 名）、`compare.py:75,445-457`（`freq_dof` 自由度核对）、`vasp_common.py:230`（发现 `DYNMAT` 文件），都不是虚频解析。而 `decide.md:915-933` 与 `playbook.md` S12/S13/S15 全靠人工 `grep cm OUTCAR` 读数（如 `playbook.md:1339-1341`）⇒ **加这个解析器是把现有条目从"人工"变成"可核对"**。零依赖且收益最大。 |
| 3 | **A28 原子间距离（含最小镜像）** | `POSCAR`/`CONTCAR`（本地文本） | 分数→笛卡尔 + 27 个周期像取 min | ✅ **可以** | 基础设施已经具备：`scripts/vasp_common.py` 的 `read_poscar()` 已给 `PoscarData.cartesian()`（`vasp_common.py:383-392`）与 `Cell.v`。零依赖只是补 20 行算术。**价值**：这是**判据级**的能力（键长/吸附原子高度/是否穿真空），而且 mic=True/False 两个数一起给最有诊断价值。 |
| 4 | **A19 扩胞** | `CONTCAR`（本地文本） | 晶格乘倍数 + 原子按 n₁×n₂×n₃ 复制平移 + 写 POSCAR | ✅ **可以** | 纯文本读写 + 循环。**必须吸收作者脚本的两个教训**：①不要像 `A19/expand.py:11,14` 那样读 `argv[1]` 却硬编码 `CONTCAR`；②`sort=True` 会重排原子 ⇒ 要么不排序、要么在输出里提示"原子顺序已改变，请重新核对 `MAGMOM`/`LDAUU`/`Selective dynamics`"。 |
| 5 | **A24 迁移概率密度的"统计"部分** | `XDATCAR`（本地文本） | 三维直方图计数 | ⚠️ **理论可行，建议先不做** | 解析 `XDATCAR` + 直方图 + 写文本都是标准库能力，但真正的工作量在**归一化口径、插值/展宽、以及产出给 VESTA 看的体数据格式**（对照 `A24/pda.vasp:150-151` 的 `26 32 29` 网格）。**且口径不明**（§3.5.3，标 `[待核对]`）⇒ 现在实现等于把一个未核实的口径固化进工具。**建议**：只登记方法，等第 5 条做完（距离/扩胞/虚频）有余力再评估。 |
| 6 | **A18 离子电导率** | `XDATCAR`（本地文本） | MSD 平均 + 线性拟合 + Nernst-Einstein | ⚠️ **公式可零依赖，实现不建议** | 公式是解析式（A18:53-73），但 MSD 需要处理**未折叠坐标/周期性**、多 t₀ 平均、`step_skip` 语义，且 `SMASS` 系综问题（C6）尚未裁定 ⇒ **现在做容易做出一个"数看着对、物理不对"的工具**。建议只把**公式 + 单位（mS/cm）+ 必须核对实际温度**登记进知识层。 |
| 7 | **A34 气体熵** | `freq/OUTCAR` + `POSCAR` | 平动（Sackur-Tetrode）/转动（刚性转子）/振动配分函数的解析式 + 转动惯量 | ⚠️ **数学上可零依赖，工程上不建议** | 公式全是解析式，转动惯量从 POSCAR 坐标就能算，物理常数可以硬编码 CODATA ⇒ **理论上零依赖可行**。**但**：①对称数 σ 是**物理输入**，算不出来，只能让用户给（A34:25）；②自制实现与 ASE 结果对不上时，用户**无法察觉**（没有第二来源）；③本 skill 的红线是"不声称验证过实际没验证的事"（契约 §7.3）。**折中裁定**：**只登记"用哪个量、什么量纲、怎么接进 ΔG、参考压力必须对齐（C5）"**，不提供实现；若将来要提供，**必须先对着 NIST-JANAF 表（A34:36, 109 提到的 H-083）验证过**再上。 |
| 8 | **A20 SMILES→3D** | SMILES 字符串 | **生成化学上合理的 3D 构型**（力场优化） | ❌ **不行** | `make3D` 是 OpenBabel 的力场构象生成（A20:79）—— 这是**算法能力**，不是算术，标准库无从实现。⇒ **只能作方法参考**（"用它生成初猜，再自己 DFT 优化"）。 |
| 9 | **A17 格式转换（mol/cif→xyz/POSCAR）** | mol / cif / xyz | cif 的**对称性展开**是硬骨头 | ⚠️ **部分可行，不建议进工具链** | `xyz`/`mol` 是简单文本；但真正的 `cif` 带对称操作与空间群，要正确展开成 P1 的原子列表很容易错（且错了不报错）。⇒ **只作方法参考**（提示用户用 ASE/`ase convert`）。**例外**：如果只是"ASE 写出的 POSCAR 没有元素行"这一条，那是**校验问题**，本 skill 已有能力（元素行核对）。 |
| 10 | **A31 VTST 编译** | 与 Python 无关 | 编译流程 + 验证命令 | ✅ **可以（作为文档/检查清单）** | 不需要代码能力：把它写成"版本配对表 + 两处必改点 + `.objects` 顺序 + 两条验证命令"的自查清单即可。**注意红线**：不得写作者的目录名（`5.4.4` 等），写 `<你的 VASP 源码目录>`。 |
| 11 | **A25 / A26 / A27 / A33 数据库与 ML** | 外部网络 + api_key | 网络请求 + pandas + ML | ❌ **不行（且不该做）** | 违反零依赖（`pandas`/`matminer`/`pymatgen`），还要**发网络请求**、要 **api_key**（A33:16 就是反面教材）。⇒ **只能作方法参考**：登记"能取什么、怎么取、有什么坑（质量标记、性能、稀疏、版本漂移）"。 |
| 12 | **A21 / A22 / A23 安装类** | — | — | ➖ **不适用** | 与 Python 依赖无关，属系统操作。**按 §3.8 的判定**：只有 A23 的"Python2 遗留工具被 Python3 抢走解释器 → SyntaxError"这条**能进 playbook 的症状→处方**，其余不提炼。 |

#### 一句话总结这条分界

> **分界不是"用不用 ASE"，而是"输入是不是本地文本 + 计算是不是纯算术"。**
> 本组里**值得进零依赖工具链**的是 **A29（消虚频位移）、A32（Dimer Axis Block）、A28（含最小镜像的原子距离）、A19（扩胞）** 四件
> ——它们共用同一个"**解析 `OUTCAR` 虚频块 + 读写 POSCAR**"的基础设施，
> 而这正是当前 `scripts/` 里**完全缺失**的一块。
> **必须依赖第三方、只能作方法参考**的是 **A20（力场生成 3D）、A25–A27/A33（数据库/ML）、A18/A24（pymatgen 扩散分析）**，
> 以及 **A34（ASE 热力学）**——A34 虽然数学上可以零依赖，但**对称数要人给、结果没有第二来源可比对**，
> 所以本 skill 的定位是**讲清楚它、不实现它**。

---

## §5 待核对清单

> 凡标 `[待核对]` 的条目**不得当断言使用**。本组是**第三方教程**，绝大多数条目天然只有单一来源。

### 5.1 影响"能不能照做"的（优先级最高）

1. `[待核对]` **A29 的校正因子**：正文 0.1（A29:27）vs 脚本 0.4（A29:106, 165）。
   两个值都无出处、无收敛性依据。**必须实测**：拿一个已知有虚频的算例，分别用 0.1/0.2/0.4 跑一遍，看哪个能回极小点。
2. `[待核对]` **A29 的"因子 × 1 = 位移 Å"换算是否普适**：我是用 A29:59 **唯一一个非零行**（模长 = 1.00000）复算出来的。
   对**离域软模**是否成立、以及 VASP 是否**总是**把每个虚频块按 3N 归一，**未核实**。
3. `[待核对]` **A29/A32 依赖的 OUTCAR 格式**：`f/i` 行的第 7 列 = `cm-1`、块起点 = `f/i 行号 + 2`、每行后三列 = `dx,dy,dz`
   —— 这些都只在**作者贴出的那一段输出**上验证过（A29:30-59）。跨 VASP 版本、跨 `NWRITE` 设置是否稳定，**未核实**。
   建议：实现时不要只看列号，**先断言表头行含 `X Y Z dx dy dz`**。
4. `[待核对]` **A18 的 AIMD 系综**：正文说 NVT（A18:38）vs INCAR 的 `SMASS = 0.0`（A18:95）。
   我推断 `SMASS=0` 是 NVE，但**没找到官方明文**（本次未检索到 `SMASS` 官方页）。**自查动作**：看 OUTCAR/OSZICAR 的温度时间序列是否漂移。
5. `[待核对]` **A34 的 `potentialenergy` 口径**：`ase.io.read('./OUTCAR', format='vasp-out').get_potential_energy()`（A34:51）
   取的是 `free energy TOTEN` 还是 `energy(sigma->0)`，文中未说明。按 `decide.md:948-962` 应当用后者。
6. `[待核对]` **A34 的参考压力偏差量级**：我算得 `ΔS(1 bar→0.035 bar) = +2.889×10⁻⁴ eV/K`、`TΔS@298.15 K = +0.086 eV`。
   公式 `ΔS = −R ln(P₂/P₁)` 是理想气体标准结果，但**我没有在 ASE 的实现里逐步核对过**（只用它自己的 `S (1 bar -> P)` 那一行反推验证过 1 atm 的情形）。
7. `[待核对]` **A33 / A26 / A27 的 API 现状**：MP 的旧 REST API（`MPRester(api_key=...)`）与 Citrine 的服务是否仍按 2021–2022 年的方式可用、配额与限速如何，**全部未核实**。

### 5.2 方法性/物理性的

8. `[待核对]` **A19 的 `sort=True` 之后 `Selective dynamics` 是否语义不变**：算例里 `CONTCAR` 前三行是 `F F F / F F F / T T T`，
   扩完的 `POSCAR` 前两行是 `F F F / T T T` ⇒ 顺序确实变了。**变了之后 T/F 对应的是不是同一批物理原子，未核实。**
9. `[待核对]` **A19 的"先优化小胞再扩胞"是否真的更快/更对**：作者自己的表述是软的（A19:22 承认直接优化大胞也行）。
   推论我认为它**不会打破对称性**、可能停在同一个高对称解，**未核实**。
10. `[待核对]` **A28 `mic=True` 在薄 slab/大真空下的假短距离**：推论，未找到算例验证。
11. `[待核对]` **A24 的 `interval=0.5` 单位**（推测 Å）与 **`pda.vasp` 体数据的归一化口径**（`A24/pda.vasp:151` 的量级是 0~1.3×10²）。
12. `[待核对]` **A24/A18 的 pymatgen import 路径在新版上是否还在**：
    `pymatgen.analysis.diffusion_analyzer`、`pymatgen.core.trajectory`、`from pymatgen import Structure`（A18:180、A24:74, 98-100）。
13. `[待核对]` **A34 的"表面吸附物种用 Harmonic limit"**：作者写作 `Harmonic limit`（A34:115），
    ASE 里对应的类名/用法**未核实**；物理前提（吸附后平动转动冻结成振动）与 `playbook.md:1292` 一致。
14. `[待核对]` **A18 的 σ 是否含 Haven 比/关联因子**：我按 Nernst-Einstein 形式判断它不含，**未核实**。
15. `[待核对]` **A18 的三个 AIMD 截断能（400/280/270 eV）**（A18:44）：无收敛测试、无泛函/赝势说明。
16. `[待核对]` **A32 的 `EDIFFG = -0.05` 与 `POTIM = 0.05`**（A32:77-78）：无出处、无算例。
17. `[待核对]` **A31 对 VASP 6.3 的判断**（少替换 `chain_init` 那一行会编译失败，A31:79）：作者自己的单次实测，且他自己也不确定 6.3 是否与 6.2 相同。
18. `[待核对]` **A32 与 A29 的消虚频路线该选哪条**：A29 = 直接位移坐标（推向极小点）；A32 = IDM 爬到鞍点（推向鞍点）。
    **目标不同、不可互换**；我把它写成"取决于你要极小点还是鞍点"是**推论**，作者没有对比过这两条。

### 5.3 格式/流程性的

19. `[待核对]` **任务单给的篇目行数与实际文件行数差 ±1**：任务单写 A17=201、A19=83、A20=194、A29=179、A33=40 等；
    实际（`read` 的 total 与 `_MANIFEST.tsv` 第 17–34 行第 7 列，**两者逐篇一致**）是
    A17=202、A18=251、A19=84、A20=195、A21=79、A22=231、A23=184、A24=112、A25=64、A26=183、
    A27=118、A28=122、**A29=178**、A30=50、A31=163、A32=150、**A33=39**、A34=123，合计 **2528**（与任务单总数一致）。
    **本报告的 `seg_G7.tsv` 用实际行数**。差异原因未查明。
20. `[待核对]` **A30 的视频清单是 2022-04 的快照**（9 个视频、约 1G、300 多人关注），现在必然不同。
21. `[待核对]` **A21 的"p4vasp 要凉"** 是 2020 年的判断；该软件是否已完全不可用，**未核实**。

### 5.4 本次**没有做**的事（诚实边界）

- 没有跑过任何一个脚本（A19/A20/A24/A29/A32/A34 的代码都只是**读**，没有执行）⇒ 所有写法上的坑都是**读代码推出来的**，不是实测的。
- 没有读过本组对应的 `.md` 源文件（只读了 `.txt`），也没有读过 `A19/CONTCAR`/`POSCAR` 之外的算例数据。
- 没有访问网络核实 ASE/pymatgen/matminer/Citrine/VTST/Materials Project 的任何官方文档
  ⇒ **凡是"某函数参数是什么含义、某 API 还在不在"的问题，一律标 `[待核对]`。**
- 没有读过任何 `POTCAR`。
