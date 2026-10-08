# reproduction_scope.md — 可复现范围

## 1. 本版能复现什么

本版支持**使用、导出、QA 汇总与校验**，这些能力只依赖仓库内的文件与 Python 标准库：

| 能力 | 命令 | 结果 |
| --- | --- | --- |
| 读取任意提示词与组级元数据 | `python src/read_example.py --data . --prompt-id <id>` | 只读输出，不联网、不调用模型 |
| 从主数据重新导出 CSV／TXT | `python src/export_data.py --repo . --out <new_dir>` | 输出目录必须不存在，脚本拒绝覆盖 |
| 校验包结构与数据一致性 | `python src/validate_release.py --repo . --report-dir <dir>` | 检查数量与逐项结果见实际运行输出，报告写到包外 |
| 重建公开 QA 报告 | `python src/build_qa_report.py --repo . --out <new_dir>` | 从公开数据生成 JSON／Markdown，拒绝覆盖 |
| 复核哈希与文件集合 | `python src/verify_hashes.py --repo .` | 对照 `SHA256SUMS.txt` 与 `release_manifest.json` |

上述工具都按参数解析路径，脚本内没有原项目的绝对路径，也不读取仓库以外的输入。Python 解释器
与标准库本身的路径不计为项目依赖。

## 2. 本版不能复现什么

本版**没有**包含完整的生成过程重建：

- 没有生成器脚本（`v6`～`v10` 各阶段运行脚本）；
- 没有冻结的 v9 基线包；
- 没有 A／B 重放产物目录；
- 没有历史运行目录与备份；
- 没有原内部审阅包、私人计划、联系人或真实原图。

因此**不能**从本仓库重新生成这 2,986 条提示词，也不能从历史生成流程逐字节重建当前交付。仓库文件本身可通过 Git 检出与哈希验证复原。

## 3. 关于“冻结重放”的准确说法

内部做过的工作只作为背景说明，避免把局部结论说成整体结论：

- 两次冻结基线重放 A／B 的运行文件 **24/24 一致**。
- 与当前订正版比较：运行文件 **15 项相同、9 项有据不同**；输入文件 **13 项相同、5 项有据不同**。
- 逐字段明确变换后，未解释差异为 0。
- **当前完整订正版没有由冻结生成器逐字节重建**；当前输入基线也已从 v9 阶段同步到 v10，
  重放使用的是归档内的冻结基线。

这组数字说明“差异可解释”，**不说明“全链完全复现”**。

## 4. 与当前订正版的关系

发布副本来自内部 v10 保存后订正的主数据。发布侧对正文、可见值、异常与确认范围的改动只限于
`CHANGELOG.md` 列出的五类允许转换。要用本仓库复核正文与可见值保持，做法是：

1. 用 `read_example.py` 导出目标 `prompt_id` 的 `prompt` 与 `expected_visible_text`；
2. 用 `data_fields.md` 第 7 节的哈希口径复算；
3. 与内部记录的对应哈希比较。

包内不含内部哈希清单，因此第 3 步需要内部材料；包内可以独立完成的是第 1、2 步，以及
`final/review_status.jsonl` 与 `final/prompts.jsonl` 之间的内部一致性核对。

## 5. 已知限制对复现的影响

- `config/known_reference_exceptions.json` 中的 7 个 `profile_id`／`spec_id` 指向更早阶段对象，
  本仓库不含这些对象，因此无法从本仓库复原它们的规则定义。
- 同文件登记的三组重复 ID（specs `EXEC-V7-E07-uk`、profiles `P1007-V6-E07-uk`、
  templates `EXEC-V6-E07-uk`）在原数据中即存在。本仓库按行保留全部记录，不合并；因此按 ID
  建索引会丢记录，读取时必须以行为单位。
- 102 条来源未公开详情，其中 96 条为 `identifier_only`，6 条为
  `identifier_only_pending`；无法据此复核隐藏的详细依据。
- 原项目保护文件与访问异常的复核证据留在内部材料中，不属于公开仓库可独立重建的范围。
- 仓库的字节保真依赖 `.gitattributes` 的 `* -text`。若入库环境改写换行，磁盘哈希与 ZIP 一致
  也不代表提交后一致；相关验证见 `release_integrity.md`。
