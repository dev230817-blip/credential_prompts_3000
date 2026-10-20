# 证件提示词 20261020_v1

[仓库首页](../../README.md) · [版本变更](CHANGELOG.md)

本版包含 1,000 组基础内容、3,000 条提示词，全部 variant 为 clean。每组使用相同的完整虚构取值，枚举三种成像；图中文字保持原来的中文或英文。覆盖 50 个对象、54 套版式、162 个成像模板视图。

| 范围 | 条数 | 成像 |
| --- | ---: | --- |
| 980 组实体 | 2,940 | 扫描件、正面自然拍摄、轻度斜拍，各 980 条 |
| 20 组电子页面 | 60 | 电子平面呈现、屏幕正拍、屏幕斜拍，各 20 条 |

相对内部 20261014_v3，本版只加强 980 条实体平扫的扫描件描述，其他 2,020 条正文不变；可见值、版式和画布比例不因这次成像修订变化。3 组父母字段共 6 处的已批准修正继续保留。

## 直接使用

- [团队 CSV](data/credential_prompts_3000_unified.csv)：12 列，UTF-8 BOM，CRD-0001—CRD-3000。
- [TXT](data/prompts.txt)：按编号阅读和复制。
- [Excel](data/prompts_filter.xlsx)：提示词、对象分类、成像模板三张表。
- [JSONL 主数据](data/prompts.jsonl)：用于程序读取。

以下命令在本版本目录运行，使用 Python 3.11 或以上版本；Excel 导出和校验需要安装 requirements.txt 中的依赖。

```bash
python -m pip install -r requirements.txt
python -B src/read_example.py --repo . --limit 3
python -B src/validate_release.py --repo .
python -B src/verify_hashes.py --repo .
python -B src/export_data.py --repo . --out ../my_export
python -B src/build_qa_report.py --repo . --out ../my_qa
python -B -m unittest discover -s tests -v
```

导出及 QA 输出目录必须位于本版本目录外且尚不存在。脚本不调用图像模型。当前统计及证据范围见[QA 报告](reports/qa_report.md)，程序实际通过结果见命令输出和 GitHub Actions。

## 状态与文件角色

新版正文人工确认 0，图片生成 0，图片验收 0。旧基础正文的确认、单份纪念页的用户试验反馈、程序校验均不替代本版逐条正文或图片验收。

[clean_content_1000.jsonl](data/clean_content_1000.jsonl)保存基础内容和历史 source_prompt，用于追溯；它不是本版最终生图正文。正式读取最新版时使用 data/prompts.jsonl 或同版 CSV/TXT。来源索引继承旧公开版，当前没有重新检查来源网页。

详见[字段说明](docs/data_fields.md)、[分类](docs/taxonomy.md)、[成像规则](docs/imaging_rules.md)、[审核与限制](docs/review_and_limits.md)、[复现范围](docs/reproduction_scope.md)。包内 JSON/JSONL 为主数据；便捷导出由公开工具生成。文件字节见 SHA256SUMS.txt 和 release_manifest.json。
