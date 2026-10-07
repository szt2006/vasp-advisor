# NOTICE —— **许可分层与第三方归属**

> ⚠️ **本仓库的许可不是一个，是分层的。**
> 根 `LICENSE` 的 MIT **只覆盖原创部分**；下面几层各有各的许可与权利人。
> **把整个仓库当成 MIT 使用是错的。**
>
> **本文件不是法律意见。** 它记录的是"各层内容的来源与官方声明的许可"，
> 以及本项目的合规做法。**使用者与再分发者请自行核对原始许可条款。**

---

## 一、逐层清单

| 路径 | 内容 | 来源 / 权利人 | 许可 | 可否自由再分发 |
|---|---|---|---|---|
| `scripts/`、`references/*.md`（原创部分）、`_*.py`、`examples/`、`vasp-calc/`、`conformance/` | **原创代码与原创知识库**（含全部更正记录、护栏、索引层） | 本仓库作者 | **MIT**（见 `LICENSE`） | ✅ 是 |
| `references/official/pages/`（637 页）、`references/official/raw/`（637 个 `.wiki`） | VASP Wiki 正文的采录 | [VASP Wiki](https://www.vasp.at/wiki/)，© VASP Software GmbH | **GNU Free Documentation License 1.2** | ⚠️ **可再分发，但须遵守 FDL 1.2**（保留署名、许可声明，衍生作品同样以 FDL 分发） |
| `references/raw/L1–L4.txt`、`D1–D4.txt`、`learn_L*.md`、`seg_L*.tsv` | 课程讲义与答疑的**文本抽取物** | **课程主办机构**（版权归原机构） | **未获再分发授权** | ⚠️ **见 §二，请自行判断** |
| `references/raw/lvthw/<ID>.txt` | 《Learn VASP The Hard Way》第二版——**行数骨架**（每行 `(content withheld)`，**不含正文**） | 作者 **BigBro(a)s（大师兄科研网）** | 该站**未声明许可** | ✅ 骨架仅含**行数**，不含表达性内容 |
| `references/raw/lvthw/*.md`、`seg_G*.tsv`、`_MANIFEST.tsv` 等 | 本项目**自己写的**精读报告、分段表、清单 | 本仓库作者 | **MIT** | ✅ 是 |
| `references/official/_versions.tsv`、`_known_issues.tsv`、`_keywords.tsv`、`_sources.tsv` | 从 VASP Wiki **抽取的结构化事实**（版本号、缺陷登记、标签归属） | 事实来自 VASP Wiki | 与上层同源（FDL 1.2） | ⚠️ 同上 |
| `references/cases/` | 真实算例的**登记与观察**（**不含 `POTCAR`**，不含原始文件副本） | 本项目 | **MIT** | ✅ 是 |

---

## 二、⚠️ 需要再分发者自行判断的一层：课程讲义与答疑

`references/raw/L1–L4.txt` / `D1–D4.txt` / `learn_L*.md` / `seg_L*.tsv`
是**课程讲义的逐页文本抽取**与**答疑记录**。

- **已知**：讲义**自带版权声明**（`references/raw/README.md` §6 记了这一点，
  这也是原始 PDF 与算例目录**没进仓库**的原因）。
- **本项目的立场**：这些内容**只用于内部溯源** ——
  即"知识库里的每条结论能追回原文"。仓库里保留的是**抽取后的文本**，
  不是原始 PDF。
- **本项目对此的立场**：这是一个**学习者的个人学习项目** —— **非商业**、
  目的是**个人学习与溯源**，且**原始 PDF 从未入库**（只保留抽取后的文本）。
  **这不是"已获公开再分发授权"的声明**，本文件也**不替原机构表态**。
- **⇒ 如果你要商业使用、大规模镜像，或主张对这部分的权利，
  请就这一层自行取得授权，或把它从你的副本中移除。**
  （移除很便宜：删 `references/raw/` 下的 `L*.txt` / `D*.txt` /
  `learn_L*.md` / `seg_L*.tsv` 即可，其余层不受影响。）

> 这一层是**本仓库唯一一处"来源与授权不明确"的地方**，如实写在这里，
> 而不是模糊过去。**把它写明，比假装不存在更负责。**

---

## 三、明确**不在**本仓库里的东西（以及为什么）

| 内容 | 为什么不在 |
|---|---|
| **`POTCAR` 及其任何片段** | 受 VASP 许可保护，**不得再分发**（其自带版权声明）。本仓库**只校验**你已有的那个，不生成、不复制、不缓存。`.gitignore` + `_doc_consistency.py --scan-leaks` 双重把关。 |
| 原始讲义 PDF、原始算例文件、`WAVECAR`/`CHGCAR` 等 | 版权 + 体积（最大单个 190 MB） |
| LVTHW 站点的**逐字正文** | ⚠️ **该站含 673 条站点信息**（集群名/账号/IP/密钥路径，见其 `SITEINFO.tsv`）。**发布版只保留行数骨架**，正文与站点信息均不入库。做法见 `references/MAINTENANCE.md` §12 与 `_publish_prep.py`。 |
| 任何**站点信息**（集群地址 / 队列名 / 核数 / 账号 / 路径） | 本项目红线（`AGENTS.md` 第 6/8 条）。 |

---

## 四、署名与致谢

- **VASP Wiki** —— 官方权威层的全部来源。© VASP Software GmbH，
  以 **GNU FDL 1.2** 发布。逐页来源 URL、抓取日期与 `sha256` 登记在
  `references/official/_sources.tsv`（659 行）。
- **《Learn VASP The Hard Way》第二版** —— 作者 **BigBro(a)s（大师兄科研网）**。
  本仓库的 E′ 层是它的精读与交叉核对结果。
- **课程讲义与答疑** —— 版权归**原机构**所有；本仓库仅作内部溯源保留抽取文本。
- **本 skill 的结构**参照了同一作者的 `cp2k-aimd` skill。

---

## 五、如果你是来"用"这个仓库的

- ✅ **可以**自由使用、修改、再分发**原创部分**（MIT）。
- ⚠️ **`references/official/` 是 VASP Wiki 的衍生** —— 再分发时请遵守 FDL 1.2。
  最省事的做法：**直接引用 [VASP Wiki](https://www.vasp.at/wiki/) 的原始页面链接**
  （每个页面的来源 URL 都能在 `_sources.tsv` 里查到），而不是转贴正文。
- ⚠️ **`references/raw/` 的讲义层** —— 见 §二，请自行判断。

---

_本文件随仓库一起维护。改动请同步 `README.md` 的 §引用与致谢 与
`references/MAINTENANCE.md`。_
