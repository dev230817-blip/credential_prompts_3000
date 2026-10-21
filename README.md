# credential_prompts_3000

[English](README_EN.md) | 中文

用于AI生成富文字图像来源检测研究的证件类提示词库。仓库保留历史名称，当前交付版为[20261021_seal_v1](deliveries/20261021_seal_v1/README.md)，以20261021_v2为基线补充分类印章要求：**1430类、4290条，全clean，5一级、40二级**。

本次印章修订：546类明确要求有章、578类不强制加章、306类按所选样式判断。直接使用[修订CSV](deliveries/20261021_seal_v1/证件类提示词_4290条.csv)及[含8张既有配图的说明](deliveries/20261021_seal_v1/证件类_分类与生图说明.md)。未运行新生图，旧配图不是本次印章修改的验收结果。下表保留的v2多格式文件不含此修订。

本版沿用使用者选择的A口径：每类三条提供相同核心取值，允许模型采用不同版式、固定印刷文案和装饰。它们是同一信息组，不是同一份证面的严格三视图。实体1418类×扫描/正拍/斜拍＝4254条；电子12类×原生页面/屏幕正拍/屏幕斜拍＝36条。

| 文件 | 用途 |
| --- | --- |
| [团队CSV](releases/20261021_v2/data/credential_prompts_4290_unified.csv) | 固定12列，UTF-8 BOM |
| [完整TXT](releases/20261021_v2/data/prompts.txt) | 阅读和复制 |
| [Excel筛选](releases/20261021_v2/data/prompts_filter.xlsx) | 分类、国家、载体和成像方式 |
| [JSONL主数据](releases/20261021_v2/data/prompts.jsonl) | 核心值、正文、哈希与追溯 |
| [四类12条样例](releases/20261021_v2/docs/examples_12.md) | 学位证、户口页、香港商业登记证、CFP数字证书 |

target_texts只覆盖给定核心取值，不是整页OCR转录；extra_json.content_group_id关联核心值组，group_id仍保留团队文字篡改组的原意并留空。标准aspect_ratio仅限定输出画布，文档本体比例交由模型。旧固定骨架、统一印章与合成授予句已从新版提示词移除。

| 版本 | 内容与口径 |
| --- | --- |
| [20261021_seal_v1](deliveries/20261021_seal_v1/README.md) | 当前交付：4290条，仅补充分类印章要求；原核心值和成像不变 |
| [20261021_v2](releases/20261021_v2/README.md) | 保留完整基线：1430类/4290条，同组核心值固定，版式与固定文案可变化 |
| [20261021_v1](releases/20261021_v1/README.md) | 历史：1430类/4290条，锁定输入完整文字和合成骨架 |
| [20261020_v1](releases/20261020_v1/README.md) | 历史：1000组/3000条，全clean三成像 |
| [20261011_v4](releases/20261011_v4/README.md) | 历史：2986条，clean/subtle/strong三档 |

分类及地理覆盖不变，不新增类别或补中外比例。本轮未重新检索或核查类别，未生图。用户此前小样支持改写方向，仍观察到补造信息、提示词说明入图和裁切，新指令尚未做新一轮图片验证。新4290条未逐条人工确认，对应图像生成/验收0。未附真实证件或内部个人资料；交付修订目录附8张既有合成示例图。历史目录和Git历史保留。

详见[字段说明](releases/20261021_v2/docs/data_fields.md)、[小样反馈](releases/20261021_v2/docs/pilot_feedback.md)、[复现范围](releases/20261021_v2/docs/reproduction_scope.md)和[版本记录](CHANGELOG.md)。许可证未定，未新增LICENSE。
