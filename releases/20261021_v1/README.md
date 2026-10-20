# 20261021_v1：1430类、4290条证件提示词

本版以1430份完整基础内容各派生三条成像提示词。实体1418类使用扫描、正拍、斜拍，共4254条；电子12类使用原生页面、屏幕正拍、屏幕斜拍，共36条。五个一级、40个二级分类保持不变。类别数不是已核视觉模板数，图片不随包发布。

使用[团队CSV](data/credential_prompts_4290_unified.csv)、[完整TXT](data/prompts.txt)、[Excel筛选](data/prompts_filter.xlsx)或[JSONL主数据](data/prompts.jsonl)。[18条样例](docs/examples_18.md)展示六种文书的三个成像版本。

每组三条的完整文字、字段、日期、人像与签章设定相同，仅成像段和输出取景变化。variant全为clean；group_id保留为空，extra_json.content_group_id关联三成像。文档本体比例与标准输出画布分开，不拉伸文档来适配画布。

分类基线为20261020_v3，基础内容来自1430条提示词20261020_v2。622候补不加入，67条移出项不恢复，不为中外对半补数。沿用既有知识和来源层级，本轮没有重新检索证件、核查类别、补原图或运行生图。

运行：`python -B -X utf8 src/build_release.py --repo .`；检查：`python -B -X utf8 src/validate_release.py --repo . --rebuild`；哈希：`python -B -X utf8 src/verify_hashes.py --repo .`。先安装requirements.txt中的依赖。脚本仅使用本版本内的基础内容和配置，构建会重导出data/reports，不重写已封装的SHA256清单。

本版新正文逐条人工确认0，图片生成0、验收0。既有六图反馈只支持规则调整方向，不扩大为4290条图片验收。字段、版式及母语版本仍按[审核边界](docs/review_and_limits.md)记录。项目许可证尚未确定，本版不新增LICENSE。
