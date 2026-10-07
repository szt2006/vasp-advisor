# VERSIONS —— VASP 版本意识（**这个 skill 的一条硬约束**）

> **一句话**：本 skill 的知识来自**不同世代的 VASP**，
> 而 VASP 对"不认识的标签"**常常只是静默忽略**。
> 所以「这个参数该填多少」必须配上「**你的版本支持它吗**」。

---

## 1. 为什么需要这一页（**这是一个实测出来的真实风险**）

本项目把三个来源的版本**量了一遍**：

| 来源 | 实测版本 | 怎么测的 |
|---|---|---|
| **官方 wiki 语料**（`references/official/`，630 页） | **VASP 6.6 时代** | 91 处 `{{Available}}` 门槛中 **61×`6.5.0`、25×`6.6.0`**；`Changelog` 页最新条目是 `6.6.1` |
| **`things to study/` 的 98 个真实算例** | **全部 `vasp.5.4.4`** | 56 份 `OUTCAR` 第一行**无一例外**是 `vasp.5.4.4.18Apr17-6-g9f103f2a35` |
| **《Learn VASP The Hard Way》** | 以 `vasp.5` / `VASP5` 为主 | 132 篇里 `vasp.5` 22 处、`VASP5` 16 处 |
| **课程讲义** | 提到 `VASP5.4.4` | 1 处 |

⇒ **我们一直在用 6.6 时代的官方文档，去支撑 5.4.4 上的行为断言。**

**这为什么会伤人**：VASP 对 `INCAR` 里**不认识的标签**，
往往是**忽略掉继续算**（或报一个与真实原因无关的错）。于是：

> 你照着一个 6.5.0 才有的参数写了 `INCAR`，
> 跑完了，出结果了，**没有任何报错** ——
> 而那个参数**根本没生效**。

这正是本 skill 最想消灭的那一类问题：「**程序不报错，但结果不对**」。

---

## 2. 三层机制（各管什么）

### 2.1 `references/official/_versions.tsv` —— **版本门控表**

从官方层**逐行提取**（`_extract_versions.py`），**每条都带原文行号**。
**不手写** —— 手写的版本表必然腐烂，且会与官方层互相冲突。

| 提取的类型 | 官方模板 | 是不是"门槛" |
|---|---|---|
| `available` | `{{Available\|6.5.0}}` | ✅ **是** |
| `available_upto` | `{{Available\|6.2.0\|6.4.0}}` | ✅ **是**（区间） |
| `deprecated` | `{{NB\|deprecated\|…}}` | ✅ **是**（能跑但不推荐） |
| `cond_default` | `{{DEF\|TAG\|cond\|val}}` | ❌ 是默认值规则，不是门槛 |
| `min_version_text` | 正文散文 `in VASP.6.4` | ❌ **只是线索**（见下） |

### 2.2 ⚠️ **为什么"散文里的版本"不能当门槛**（本项目实测的反例）

如果把 `min_version_text` 也当门槛，对一个 **5.4.4** 用户会报出：

| 标签 | 会被判"需 6.4.3+" | 在多少个真实算例里出现 |
|---|---|---|
| `GGA` | 需 6.4.3 | **94** |
| `ISIF` | 需 6.4.1 | **94** |
| `ISPIN` | 需 6.5.0 | **49** |

而这三个标签**显然在 5.4.4 里就有**。

**根因**：那句话讲的是**某个新增取值**的版本
（例如官方 `ISIF` 页说 `ISIF=8` 自 VASP.6.4.1 起），
**不是**"整个标签自那时才有"。

⇒ **门槛必须由官方结构化标注（`{{Available}}`）兜底**；
散文版本只作线索，用来查证。

### 2.3 `references/official/_known_issues.tsv` —— **官方缺陷登记簿**

官方 `Known issues` 页是一份**结构化**的缺陷库（110 条），每条带
`reported_in_version`（**从哪版开始有这个问题**）与 `resolved_in_version`。
**这正是「不报错但结果错」那类问题的官方清单。**

```bash
python references/official/_extract_known_issues.py --for-version 5.4.4
```

---

## 3. 怎么用（三条路径）

### 3.1 先弄清你的版本

```bash
# 最可靠：OUTCAR 第一行
head -1 OUTCAR        # → vasp.5.4.4.18Apr17-6-g9f103f2a35 (build …) complex
```

`validate.py` **会自动读它**（`parse_version_number` 把它变成 `(5, 4, 4)`）。
没有 `OUTCAR` 时用 `--vasp-version` 显式给：

```bash
python scripts/validate.py <目录> --vasp-version 5.4.4
```

**两个都没有时，版本检查不执行** —— 工具会**如实说"未检查"**，不会猜。

### 3.2 查一个标签的门槛

```bash
python references/official/_extract_versions.py --gate EFERMI
python references/official/_extract_versions.py --list      # 按版本汇总
```

⚠️ 输出里若写「**没有找到任何版本标注**」，它的意思是
「**官方未标注版本门槛**」—— **不等于**「所有版本都支持」。
官方只对**新加的**标签标 `{{Available}}`，绝大多数标签根本没标。

### 3.3 查你那个版本有哪些已知缺陷

```bash
python references/official/_extract_known_issues.py --for-version 5.4.4
```

---

## 4. 实测：**5.4.4 用户最该知道的 5 条**

> 以下全部来自官方 `Known issues` 页（`pages/Known_issues.md`），
> 提取件在 `_known_issues.tsv`。**每条都能回原文核对。**

| # | 官方标题 | 首现 | 修于 | 为什么危险 |
|---|---|---|---|---|
| **#51** | **Bug in default NBANDS for negative magnetic moments** | 5.4.4 | 6.6.0 | 默认 `NBANDS` 用了 `MAGMOM` 的**带符号值**而不是绝对值 ⇒ **能带数常常太少**，还可能崩在**误导性的报错**上。**只影响自动定 `NBANDS`**（`ISPIN=2` / `LNONCOLLINEAR`）。⇒ **处方：显式写 `NBANDS`。** |
| **#50** | **EFIELD tag and symmetries** | 5.4.4 | 6.6.0 | 加 `EFIELD` 时，`IDIPOL` 方向上的**反演对称性没被去掉**，偶极形不成 ⇒ **结果就是错的**。官方建议**手动 `ISYM=0`**。 |
| **#83** | **Ionic contributions to macroscopic polarization (atoms at periodic boundary)** | 5.4.4 | 6.3.2 | 周期性边界上的原子对 `p[ion]` 的贡献被重复计入 ⇒ **`OUTCAR` 里报的 `Ionic dipole moment: p[ion]` 与别的版本不一样**（数值不同，物理上仍等价）。⚠️ **跨版本比这个数会得出错误结论。** |
| **#22** | **Uninitialized variable IFLAG in ELMIN for ICHARG=5** | 5.4.0 | 6.5.0 | `ICHARG=5` 时 `IFLAG` 未初始化，**每个 MPI rank 一个随机值** ⇒ 取决于编译器，可能**无限等待**、也可能**结果不一致**。 |
| **#92** | **Acoustic sum rule incorrectly applied to Born effective charges in charged cells** | `<6` | **未修** | VASP 把 Born 有效电荷之和硬掰到 0，**这只对中性胞成立**。用 `LEPSILON`（DFPT）时**不管 `ISYM` 都会发生**。⚠️ **带电体系算 Born 电荷要小心。** |

**另外两条与版本无关、但常被误用的**：

- **#101**（首现 5.4.4，**未修**）：TDDFT（`ALGO=TIMEEV`）在 **Gamma 版**里
  把复数系数**静默截断成实部** ⇒ 虚部直接丢掉。**只影响 Gamma 版 + TIMEEV。**
- **#25**：`resolved_in_version = PBE.64` —— ⚠️ 这是 **POTCAR 数据发布版**，
  **不是 VASP 程序版本**（别去找一个叫 "VASP PBE.64" 的版本号）。
  内容：某版 Nd 的 `POTCAR` 第一行日期打错（`25May2002` 应为 `25May2022`）。

---

## 4b. ⚠️ **一个必须知道的例外：补丁版（VTST 等）**

官方 `{{Available|…}}` 标的是「**官方原生**从哪个版本起有」。
**补丁版可以在老版本上提供新标签** —— 最典型的是 **VTST**：

| 标签 | 官方原生 | 但 VTST 补丁版 |
|---|---|---|
| `IMAGES` | 自 **6.2.0** | **5.4.4 一直能用** |
| `ICHAIN` / `IOPT` / `LCLIMB` / `SPRING` | 官方分类表里**没有独立页** | 同上，VTST 提供 |

⇒ 所以 `validate.py` 报 `VER.too_old` 时的准确含义是：

> 「**官方原生**从 X 版本起才有这个标签」
> **不等于**「在你的环境里一定不可用」。

**本项目实测到过这个假阴性**：`things to study/` 的 NEB 算例（5.4.4）
用了 `IMAGES`，而按官方门槛它"不该有" —— 实际是 VTST 提供的。

**怎么判断自己是不是补丁版**：看 `OUTCAR` 里有没有 `VTST` 相关字样，
或问集群管理员。**本 skill 不检查这个**（`OUTCAR` 里的标识因补丁而异）。

---

## 5. ⚠️ 这一层**做不到**什么（诚实边界）

1. **官方自己说这份 known issues 是 `incomplete`。**
   ⇒ **没列出来的不代表没问题。** 它只是"第一道网"。

2. **绝大多数标签没有版本标注。**
   ⇒ 工具只能报"**官方明文标了**"的那些。对没标的，它**不说话**
   （不是"都支持"，是"官方没写、我们不知道"）。

3. **没有用户版本时判断不了**（`OUTCAR` 与 `--vasp-version` 都没有）。
   此时工具**如实说"未检查"**，不猜。

4. **`Changelog` 页只回溯到 `6.4.3`。**
   官方那份 Release notes 的版本小节实测只有
   `6.6.1 / 6.6.0 / 6.5.1 / 6.5.0 / 6.4.3` —— **5.x 与 6.0–6.4.2 的改动不在里面**。
   ⇒ 想查"5.4.4 → 6.x 到底变了什么"，**这份 Changelog 帮不上忙**。

5. **本 skill 没有在真机上验证过任何版本门控。**
   全部来自**官方文档的自述**。要落实，需要**两次真机运行**（两个版本）
   —— 见 `conformance/README.md` 的"你可以怎么帮忙"。

---

## 6. 给 AI 助手的硬性要求

当用户问"某个参数该怎么填"时：

1. **先问（或先读）他的 VASP 版本。** 有 `OUTCAR` 就读第一行；
   没有就问 —— **不要假定他在用最新版**。
2. 推荐一个标签前，**查一下它的版本门槛**。
3. 用户版本低于门槛时，**明说"这个标签在你的版本上可能不存在，
   而且程序可能静默忽略它"**，并给出替代做法。
4. **不要把"官方没标版本"说成"所有版本都支持"。**
   正确措辞：「官方未标注版本门槛」。
5. 提到"某个 bug 已修"时，**必须同时给出"首现版本"与"修于版本"**
   —— 只说"已修"会让还在老版本上的人以为没事。

> ⚠️ 这条要求与 `AGENTS.md` §8「诚实的能力边界」是同一条：
> **不声称验证过但实际没验证的事**，以及
> **不把"我没查到"说成"它不存在"**（见 `CHANGELOG.md` CR-026 的教训）。

---

## 7. 重建这些文件

```bash
# 版本门控表（从官方层逐行提取）
python references/official/_extract_versions.py

# 官方缺陷登记簿
python references/official/_extract_known_issues.py

# 需要先抓官方页（若 pages/ 里没有）
python references/official/_fetch_named.py --title "Changelog" \
       --title "Known issues" --title "Installing VASP.6.X.X"
```

两个脚本都**只用标准库**，且**可反复跑**（幂等）。
