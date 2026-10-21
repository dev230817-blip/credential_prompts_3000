# 20261021_v2：1430类、4290条知识引导提示词

本版采用使用者选择的A口径：同一类的三条提示词提供相同核心取值，允许模型组织不同版式、固定印刷文案和装饰。它们是同一信息组，不是同一份文书的严格三视图。五一级、40二级及1430类范围不变；实体1418类各扫描、正拍、斜拍，电子12类各原生页面、屏幕正拍、屏幕斜拍，共4290条。

使用[团队CSV](data/credential_prompts_4290_unified.csv)、[完整TXT](data/prompts.txt)、[Excel](data/prompts_filter.xlsx)、[JSONL](data/prompts.jsonl)，或先看[四类12条样例](docs/examples_12.md)。旧20261021_v1及其他历史版保留。

新版移除固定文书骨架、统一印章规则和文档本体比例。标准aspect_ratio只控制输出画布。字段名用于说明取值，不要求逐项打印。target_texts只覆盖给定核心值，不是整页文字转录；content_group_id关联核心取值组，不能作为像素配对或完整正文相同的依据。group_id保留团队文字篡改分组原意并留空。

从父版抽取的核心字段组1428类不变；香港商业登记证、CFP数字认证证书两类采用对话试验取值，差异见reports/parent_value_comparison.json。旧标题、国家等上下文不再强制印入，合成授予句和印章文字不作为锁定版式。

安装requirements.txt后，可在本版本目录运行：`python -B -X utf8 src/build_release.py --repo .`；检查：`python -B -X utf8 src/validate_release.py --repo . --rebuild`；哈希：`python -B -X utf8 src/verify_hashes.py --repo .`。构建只用本目录的基础取值和配置，不访问模型、网络或父项目；重新导出不自动改写发行清单。

本轮未检索或复核类别，未运行生图。用户此前小样支持这一写法方向，同时显示补造信息、说明文字入图、裁切及版式变化等限制，见[小样反馈](docs/pilot_feedback.md)。新4290条正文未逐条人工确认，对应图片生成与验收均为0；已有试图不计入本版本正式图片数。
