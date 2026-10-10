# credential_prompts_3000

[English](README_EN.md) | **中文**

面向 **AI 生成的富文字图像来源检测研究** 的证件类提示词库，属于上海交通大学大创项目「面向主流文生图模型的生成图片检测算法研究」。数据涵盖中国、美国和英国的证件与证书，共 **1,000 个基础组、2,986 条提示词**。

每条 `prompt` 包含证件载体、版面布局、字段标签和需要呈现的完整文字，可以读取后用于文生图实验。图中个人姓名、证件号码等取值使用虚构内容，不留待填占位符。仓库提供提示词、规格、来源索引和检查工具；当前发布版本尚未生成图片。构造取值未与真实登记系统比对，
用于研究实验，不用于实际证件办理或身份认证。

## 数据构成

同一 `group_id` 下的提示词共用载体、字段集合、标签和构图，通过字段取值变化形成三个档位：

| 档位 | 内容 | 条数 |
| --- | --- | ---: |
| `clean` | 基础版本，没有设计异常 | 1,000 |
| `subtle` | 在基础版本上设置一处隐蔽问题 | 993 |
| `strong` | 设置两三处问题，或一处明显问题 | 993 |
| **合计** | **1,000 个基础组** | **2,986** |

其中 993 组包含三个档位，7 组 UKMT 数学竞赛证书仅保留 `clean`。该证书不印分数与编号，按既定设计范围不设置异常，因此比最初 3,000 条目标少 14 条，仓库名沿用原目标。

三个档位都是生图提示词，`clean` 不表示真实拍摄样本；异常的隐蔽程度也尚未通过生成图片验证。

## 分类与覆盖

数据按 29 个配额单元、50 个实体组织。配额单元对应一类证件或业务，实体进一步区分证面或细分对象；`profile_id` 记录采用的版式样式。

| 维度 | 基础组分布 |
| --- | --- |
| 国家 | 中国 604，美国 205，英国 191 |
| 图中可见文字的语言 | 中文 604，英文 396 |
| 分类编号 | `C` 前缀为中国证件，`E` 前缀为境外证件 |

各分类的组数、实体清单和样式口径见 [分类表](docs/taxonomy.md)。

## 文件说明

```text
.
├── README.md / README_EN.md
├── CHANGELOG.md                         # 版本变更记录
├── SHA256SUMS.txt / release_manifest.json
├── final/
│   ├── prompts.jsonl                    # 主文件：2,986 条完整提示词
│   ├── prompts.csv / prompts.txt        # 同一版本的便捷导出
│   ├── groups.jsonl / groups.csv        # 1,000 个基础组及组级字段
│   ├── review_status.jsonl              # 每条提示词的审核状态
│   └── qa_report.json / qa_report.md    # 数据统计与程序检查结果
├── config/
│   ├── specs.json / specs.csv           # 证件规格与规则
│   ├── profiles.json / templates.json   # 版式样式与提示词模板
│   ├── sources.json / sources.csv       # 来源索引及支持范围
│   └── known_reference_exceptions.json  # 已登记的关联例外
├── docs/                               # 分类、字段、审核与来源说明
├── tests/                              # 回归测试
├── .github/workflows/                  # 自动检查
└── src/                                # 读取、导出和校验工具
```

`final/` 与 `config/` 中的 JSONL／JSON 为主数据。CSV 中的数组和对象以 JSON 字符串保存，提示词正文与 JSONL 一致，无需另行拼接。

## 主要字段

| 字段 | 说明 |
| --- | --- |
| `prompt_id` / `group_id` / `variant` | 提示词编号、所属基础组与档位 |
| `quota_id` / `entity_id` | 配额单元与细分实体 |
| `country` / `visible_language` | 国家与图中可见文字的语言 |
| `profile_id` / `spec_id` / `source_ids` | 版式样式、规格及来源关联 |
| `expected_visible_text` | 图中要求呈现的字段标签与完整取值 |
| `changes` / `changed_fields` / `target_rule_ids` | 相对基础版本的变化及目标规则 |
| `prompt` | 完整生图指令 |
| `body_approved` / `variant_review_status` | 正文人工确认与档位审核状态 |
| `ready_for_generation` / `image_generated` | 生图准备与图片生成状态，当前均为 `false` |

主要字段及哈希口径见 [数据字段说明](docs/data_fields.md)。

## 使用方法

以下示例在仓库根目录运行，只使用 Python 标准库；自动检查使用 Python 3.14。

读取第一个基础组的提示词：

```python
import json

with open("final/prompts.jsonl", encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

group_id = rows[0]["group_id"]
for row in rows:
    if row["group_id"] == group_id:
        print(row["prompt_id"], row["variant"])
        prompt = row["prompt"]  # 完整提示词正文
        print(prompt[:200])     # 只显示前 200 个字符
```

也可以用命令行查看示例、导出数据和检查文件：

```bash
# 查看前三条提示词；加 --full 可显示完整正文
python src/read_example.py --data . --limit 3

# 重新导出 CSV / TXT；输出目录须不存在
python src/export_data.py --repo . --out ./my_export

# 检查数据及关联关系；报告写入仓库外
python src/validate_release.py --repo . --report-dir ../validation_out

# 重建公开 QA 报告；输出目录须不存在且位于仓库外
python src/build_qa_report.py --repo . --out ../qa_rebuilt

# 核对文件集合及 SHA-256 校验值
python src/verify_hashes.py --repo .
```

这些工具不联网、不调用图像模型。仓库支持读取、导出和校验现有数据，历史生成流程的复现范围见 [复现说明](docs/reproduction_scope.md)。

## 质量检查与已知边界

程序校验的数量与逐项结果见实际运行输出，覆盖组与档位数量、ID 和关联关系、正文及可见值哈希、人工确认绑定、CSV 一致性和来源公开条件。程序检查通过与人工确认、图片验收分别记录。

使用者于2026-10-11明确确认最新版全部 **2,986 条提示词正文**，未确认正文 **0 条**。独立 clean 取值确认仍为 **129 组**；内容未变且绑定有效的独立模板确认覆盖 **31 个样式**，历史54样式确认另存。正文确认不替代来源核实或图片验收。具体状态见 [审核范围](docs/review_scope.md) 和 [检查报告](final/qa_report.md)。

来源表共 222 条记录：**120 条**公开来源索引，**102 条**仅保留 ID、支持范围与限制，其中 6 条标为出处待核。七个悬空引用影响 129 条提示词、43 个基础组，三组重复 ID 也已登记；使用配置时需保留这些例外。详细依据见 [来源与限制](docs/sources_and_limits.md) 和 [关联例外清单](config/known_reference_exceptions.json)。

当前发布版本尚未调用图像模型，因此没有图片可读性、OCR 准确率、视觉真实感或检测难度的实测结果。

许可证待项目组确定，当前未附 `LICENSE`。发布文件的哈希与 Git 换行设置见 [文件完整性说明](docs/release_integrity.md)。

## 10月11日反馈修订

本版接入签名、公章、机构标志与关键图形的明确描述。相对旧发布版累计修改1,150条正文，涉及388组、23个样式；原可见取值与异常设计不变。当前共用描述见 `config/active_templates.json`，旧模板和规格作为基线保留，冻结生成器未逐字节重建当前正文。

内部参考覆盖为5已取得、22部分覆盖、21仅样张、2未取得。C02户主卡有四川与河北的编辑版独立参考，列为部分覆盖；C18与NMC仍未取得。本轮停止继续检索与核实，错版、旁证和签章依据限制保留。项目外原图及私有观察不发布，图片生成和验收仍为0。
