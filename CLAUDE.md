# CLAUDE.md

> ⚠️ **本文件只是一个极简指针，不重复内容。**
> 唯一真源是 **`AGENTS.md`** —— 请先读它。

**这是什么**：一套 **VASP 计算顾问** skill（知识库 + 零依赖 CLI 工具链）。
**它不替用户跑计算**，只做：推荐参数 / 生成输入 / 校验 / 解析 / 诊断 / 后处理。

**先跑这个**：

```bash
python scripts/doctor.py
```

**按需求取用**：

| 需求 | 命令 |
|---|---|
| 环境行不行 | `python scripts/doctor.py` |
| 生成输入 | `python scripts/wizard.py` |
| 校验输入 | `python scripts/validate.py <目录> --potcar <POTCAR>` |
| 看数值 | `python scripts/parse_output.py <目录>` |
| 判自洽 | `python scripts/compare.py <目录>` |
| 查症状 | `python scripts/diagnose.py <目录>` |
| 选参数 | `python scripts/recommend.py --goal <目标> --elements "<元素>"` |

**三条硬约束**：

1. **不生成、不复制 `POTCAR`**（受 VASP 许可保护，只能只读头部数字用于校验）。
2. **站点信息不进仓库**（集群地址/队列/核数/账号/路径）→ 出口是 `SITE.md`。
3. **不声称验证过但实际没验证的事**；查不到就写"来源待核对"。

**改完必须跑**：

```bash
python _validate_all_suites.py     # 串行跑全部护栏，不要并行
```

**红了先弄明白再改，不要为了让灯变绿而放宽判据。**

更多：`USAGE.md`（面向人）· `README.md`（结构）· `CONTRIBUTING.md`（改动规范）·
`references/MAINTENANCE.md`（知识库维护）· `CHANGELOG.md`（含 23 条更正记录）
