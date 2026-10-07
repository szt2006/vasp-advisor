# GEMINI.md

> ⚠️ **本文件只是一个极简指针，不重复内容。**
> 唯一真源是 **`AGENTS.md`** —— 请先读它。

**这是什么**：一套 **VASP 计算顾问** skill（分层可溯源知识库 + 零依赖 CLI 工具链）。
它**不替用户跑计算**，只做：推荐参数 / 生成输入 / 校验 / 解析 / 诊断 / 后处理。

**先跑**：`python scripts/doctor.py`

**常用命令**：

```bash
python scripts/wizard.py                  # 一问一答生成一套自洽输入
python scripts/validate.py  <目录> --potcar <POTCAR>   # 校验输入
python scripts/compare.py   <目录>        # 判自洽 + 力平衡
python scripts/diagnose.py  <目录>        # 症状 → 处方
python scripts/recommend.py --goal <目标> --elements "<元素>"
python _validate_all_suites.py            # 改完必跑（串行）
```

**三条硬约束**：

1. **不生成、不复制 `POTCAR`** —— 受 VASP 许可保护，不得再分发；
   只能只读头部几个数字（`TITEL`/`ENMAX`/`ZVAL`）用于校验。
2. **站点信息不进仓库**（集群地址 / 队列名 / 核数 / 账号 / 机器路径 /
   `module load` 的具体模块）—— 出口是 `SITE.md`（永不入库）。
3. **不声称验证过但实际没验证的事** —— 查不到就写"来源待核对"。

**一条最容易被误解的事**：`validate.py` / `compare.py` / `diagnose.py` 的
`OK` 都只表示"**检查过的那些项**没发现问题"。
每个工具都会打印「本次未检查的项」—— **那不是"通过了"，是"没查"**。

更多：`USAGE.md` · `README.md` · `CONTRIBUTING.md` ·
`references/MAINTENANCE.md` · `CHANGELOG.md`
