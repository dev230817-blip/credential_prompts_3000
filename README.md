# credential_prompts_3000

[English](README_EN.md) | 中文

用于 AI 生成的富文字图像来源检测研究的证件类提示词库，属于上海交通大学大创项目「面向主流文生图模型的生成图片检测算法研究」。

**最新版本：[20261020_v1](releases/20261020_v1/README.md)**。包含 1,000 组基础内容、3,000 条提示词，覆盖 5 个一级类别、29 个二级类型、50 个对象、54 套版式。图中姓名、号码等字段使用构造的虚构值；没有图片随包发布。

| 文件 | 用途 |
| --- | --- |
| [团队 CSV](releases/20261020_v1/data/credential_prompts_3000_unified.csv) | 12 列统一格式，UTF-8 BOM |
| [完整 TXT](releases/20261020_v1/data/prompts.txt) | 阅读和复制提示词 |
| [Excel 筛选表](releases/20261020_v1/data/prompts_filter.xlsx) | 筛选提示词、对象和成像模板 |
| [JSONL 主数据](releases/20261020_v1/data/prompts.jsonl) | 完整字段、正文哈希和追溯信息 |
| [数据检查报告](releases/20261020_v1/reports/qa_report.md) | 数据统计及证据范围；实际校验结果见 Actions |

## 版本怎么选

| 版本 | 内容 | 状态 |
| --- | --- | --- |
| [20261020_v1](releases/20261020_v1/README.md) | 3,000 条，全部 clean，每组三种成像；980 条实体平扫加强为扫描件描述 | 当前研究版本；正文人工确认 0，图片生成 0，图片验收 0 |
| [20261011_v4](releases/20261011_v4/README.md) | 2,986 条，clean/subtle/strong 三档 | 历史公开版；原数据、说明、工具和哈希清单完整保留 |

新版的三种成像改变呈现方式；旧版三档改变内容中的异常设计。新版并非在旧 2,986 条上补 14 条，而是从 1,000 组基础 clean 内容派生。旧版的正文确认不自动成为新版确认。

各版本的数据、配置、说明和校验工具均放在自己的版本目录。原根目录的 final/config/docs/src/tests 已归入 releases/20261011_v4；原提交仍保留在 Git 历史中。各发布包的清单只校验该包内部文件。

运行示例、导出和检查命令见[最新版说明](releases/20261020_v1/README.md)。[版本沿革](CHANGELOG.md)记录本次迁移。使用边界、来源继承和图片状态见[审核与限制](releases/20261020_v1/docs/review_and_limits.md)。许可证仍待项目组确定，当前未添加 LICENSE。
