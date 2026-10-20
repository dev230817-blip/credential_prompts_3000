# credential_prompts_3000

[English](README_EN.md) | 中文

用于AI生成富文字图像来源检测研究的证件类提示词库。仓库名称保留历史命名；**最新版本为[20261021_v1](releases/20261021_v1/README.md)，1430类、1430份基础内容、4290条提示词**，覆盖5个一级、40个二级分类。

实体1418类各有扫描、正拍、斜拍，共4254条；电子12类各有原生页面、屏幕正拍、屏幕斜拍，共36条。每组三条的完整文字相同，仅呈现方式变化。国内1524条、国外国家2490条、国际体系276条；全部clean，不含文字异常对照。

| 文件 | 用途 |
| --- | --- |
| [团队CSV](releases/20261021_v1/data/credential_prompts_4290_unified.csv) | 固定12列，UTF-8 BOM |
| [完整TXT](releases/20261021_v1/data/prompts.txt) | 阅读和复制 |
| [Excel筛选](releases/20261021_v1/data/prompts_filter.xlsx) | 分类、国家、载体与成像方式 |
| [JSONL主数据](releases/20261021_v1/data/prompts.jsonl) | 完整字段、正文哈希与追溯 |
| [18条样例](releases/20261021_v1/docs/examples_18.md) | 六种文书各三成像 |

| 版本 | 内容 | 状态 |
| --- | --- | --- |
| [20261021_v1](releases/20261021_v1/README.md) | 1430类，4290条；实体与电子分别三成像 | 当前版本；新正文逐条人工确认0，图片生成0、验收0 |
| [20261020_v1](releases/20261020_v1/README.md) | 1000组，3000条，全clean三成像 | 历史公开版，完整保留 |
| [20261011_v4](releases/20261011_v4/README.md) | 2986条，clean/subtle/strong三档 | 历史公开版，完整保留 |

本版采用已确定的1430类范围，不新增类别、不为中外比例补数。三成像通过extra_json.content_group_id关联；group_id不改作成像组。输出画布与文档本体比例分开保存。类别数不等于已核实的独立视觉模板数。

每个发布目录包含自己的数据、配置、说明、离线构建和检查工具。旧目录与旧Git历史不改。[复现说明](releases/20261021_v1/docs/reproduction_scope.md)、[审核边界](releases/20261021_v1/docs/review_and_limits.md)、[版本沿革](CHANGELOG.md)。没有图片随包发布；许可证仍待项目组确定，未新增LICENSE。
