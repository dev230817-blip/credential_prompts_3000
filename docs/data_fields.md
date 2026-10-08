# data_fields.md — 字段、导出规则与哈希口径

主数据文件：`final/prompts.jsonl`（2,986 条）、`final/groups.jsonl`（1,000 条）、
`final/review_status.jsonl`（2,986 条）、`config/*.json`。CSV／TXT 是同版导出。

## 1. 标识与归属

| 字段 | 说明 |
| --- | --- |
| `prompt_id` | 提示词唯一 ID，形如 `G1007-<entity>-<hash>-<variant>` |
| `group_id` | 基础组唯一 ID，形如 `G1007-<entity>-<hash>` |
| `variant` | `clean` / `subtle` / `strong` |
| `profile_id` | 版式与规则定义 ID |
| `spec_id`、`parent_spec_id` | 规格 ID 与父规格 ID |
| `entity_id`、`quota_id` | 实体与配额单元 |
| `candidate_id` | 早期候选编号，保留原值 |
| `source_ids` | 该条引用的来源 ID 列表，可解析到 `config/sources.json` |
| `release_version` | 本次发布标识，当前为 `codex-20261007-v3`；文档与工具的后续修订另由 Git 提交记录区分 |

## 2. 内容字段

| 字段 | 说明 |
| --- | --- |
| `prompt` | 提示词正文。本次发布逐字保留，未改写、未翻译、未润色 |
| `expected_visible_text` | 图中应逐字显示的虚构值字典（键为字段名，值为可见文字） |
| `shared_prompt_sections` | 共用段落：`object`、`carrier`、`layout`、`rendering` |
| `context` | 版次参考日与可选机读区标记 |
| `pending_checks` | 仍待核的事项，按原样保留 |
| `fictional_adaptations` | 虚构化说明 |
| `surface` | 证面，例如国徽面、人像面、资料页 |
| `country`、`visible_language`、`instruction_language` | 国家与语言 |
| `prompt_characters`、`description_characters`、`visible_text_characters` | 长度统计 |
| `template_version`、`prompt_version` | 模板与提示词版本标签 |
| `source_input_version` | 输入的阶段标签；内部项目目录前缀已在本发布中清理 |

## 3. 异常字段

| 字段 | 说明 |
| --- | --- |
| `anomaly_category`、`anomaly_count` | 异常类别与数量 |
| `changes` | 逐项改动（字段、旧值、新值） |
| `changed_fields`、`changed_field_count` | 实际改动字段 |
| `target_rule_ids`、`expected_failure_rules`、`rule_failure_count` | 目标规则与预期失败 |
| `anomaly_basis`、`evidence_basis` | 异常与证据依据 |
| `collateral_failure_rules`、`unexpected_rule_failures` | 连带失败与意外失败 |
| `count_policy` | 计数口径说明 |
| `difficulty_status`、`single_image_detectable` | 设计层声明；`single_image_detectable` 可为 `null` |

## 4. 审核状态字段

`final/prompts.jsonl` 把当前审核状态写成固定枚举，原阶段性文字保留在
`historical_review_status` 中。`final/groups.jsonl` 保留原状态文字，没有该历史对象字段。
当前确认范围以 `review_status.jsonl` 的实际 ID／哈希绑定为准，不能只按组文件的旧状态判断。

| 字段 | 取值 | 含义 |
| --- | --- | --- |
| `body_approved` | `true` / `false` | 该条正文是否被有效正文绑定覆盖 |
| `variant_review_status` | `body_confirmed` / `body_unconfirmed` | 当前正文确认状态 |
| `manual_review_status` | `clean_fields_confirmed` / `clean_fields_unconfirmed` / `clean_fields_legacy_inherited` | 本组 clean 取值状态；`legacy_inherited` 表示仅按原 ID／哈希继承的历史确认 |
| `template_review_status` | `template_confirmed` / `template_unconfirmed` | 经绑定核查的模板状态 |
| `historical_review_status` | 对象 | 上述四个字段在内部 v10 中的原始文字 |
| `ready_for_generation`、`image_generated` | `true` / `false` | 全量为 `false` |
| `generation_status` | 文本 | 生成阶段说明；属历史属性 |
| `validation` | 对象 | 程序检查结果：`errors`、`checks`、`pending_checks` |

历史文字的参考含义如下；实际当前状态还取决于有效确认绑定，不是逐字替换：

| 原值 | 当前值 |
| --- | --- |
| `待人工审核`、`新增模板待使用者确认`、`新增/修订模板待使用者确认`、`返修模板哈希已变，待审`、`正文待人工审核`、`返修正文待人工抽查` | 未确认类枚举 |
| `使用者已审核通过文字取值`、`沿用已审字段` | 未被当前绑定覆盖时为 `clean_fields_legacy_inherited`；被覆盖时为 `clean_fields_confirmed` |

**clean 取值确认只表达本组 clean 取值已确认，不扩展到 subtle 与 strong 的取值确认。**

## 5. review_status.jsonl

固定 2,986 条，一条对应一个 `prompt_id`。

| 字段 | 说明 |
| --- | --- |
| `prompt_id`、`group_id`、`profile_id`、`variant` | 关联键 |
| `prompt_sha256` | `sha256(prompt)`，见第 7 节 |
| `visible_fields_sha256` | `expected_visible_text` 的规范 JSON 哈希 |
| `template_confirmed` | 该组模板是否经绑定核查确认 |
| `template_binding_sha256` | 模板绑定签名哈希（只由共用段落与槽位结构决定，发布转换不改变它） |
| `template_object_sha256` | **实际发布模板对象**的完整对象哈希 |
| `template_object_resolution` | 该 `spec_id` 在发布模板中的解析结果：`unique`、`duplicate_identical:N`，歧义时为 `ambiguous:N` 且对象哈希留空 |
| `template_internal_object_sha256` | 内部 v10 旧模板对象的哈希，另列以便对照；不用于发布对象绑定 |
| `template_confirmation_scope` | 形如 `profile:<profile_id> spec:<spec_id>` |
| `clean_fields_confirmed` | 本组 clean 取值是否确认 |
| `clean_fields_binding_sha256` | clean 取值绑定哈希 |
| `body_confirmed` | 该条正文是否确认 |
| `body_group_binding_sha256` | 所属组的正文绑定哈希 |
| `confirmed_at`、`reconfirmed_at` | 原确认时间与重确认时间；未确认时为空字符串 |
| `confirmation_basis` | 来源类型：`existing_user_content_confirmation`、`clean_fields_only_no_body_confirmation`、`not_in_review_scope` |
| `ready_for_generation`、`image_generated` | 原样带出 |
| `image_review_status` | 固定 `not_reviewed` |
| `release_version` | 发布标识 |

未确认条目一律使用明确的未确认取值和空绑定字符串，不填写任何时间。`confirmation_basis`
只写来源类型，不复制对话、内部文件路径或个人信息。
`clean_fields_only_no_body_confirmation` 是保留枚举，本包未使用；不是新增确认。

`template_object_sha256` 绑定的是**发布副本中的模板对象**。发布副本给模板新增了
`release_version`，因此该哈希与内部旧对象哈希不同；去掉 `release_version` 后的对象哈希等于
内部旧哈希，这一等价关系逐条记录在 `template_internal_object_sha256` 与内部映射文件中。
两套哈希分开命名，不混用。

同一 `spec_id` 在发布模板中对应多条记录时（原数据存在重复 ID），解析结果记
`duplicate_identical:N`；若多条内容不同则为 `ambiguous:N`，此时**不填写对象哈希**，改为显式
报告歧义，不默认取第一条或最后一条。

## 6. config/sources.json

| 字段 | 说明 |
| --- | --- |
| `source_id` | 来源 ID，全部被引用 ID 均可解析 |
| `publication` | `index_published`／`identifier_only`／`identifier_only_pending` |
| `url` | 官方自有渠道发布时的公开链接数组；**未公开来源没有该字段** |
| `quota_ids`、`scope`、`发布机构`、`页面名称`、`来源类型` | 已公开来源的索引字段 |
| `目前可支持的判断`、`不能据此确认的内容` | 支持范围与限制 |
| `publication_basis` | 逐条列出四项公开条件的判断依据 |
| `repost_channel_note` | 文本由其他官方渠道转载／转述时的说明 |
| `release_link_checked_at`、`check_status` | 本次链接检查日期与**不含链接**的状态汇总 |
| `evidence_type`、`support_scope`、`limitations`、`not_published_reason` | 仅保留 ID 的来源所公开的内容 |
| `internal_origin_file_count` | 被清理的内部文件数量，仅保留计数 |
| `original_checked_at` | 原来源记录的访问日期，区别于发布整理时的链接检查日期 |
| `withheld_non_official_url_count` | 仅已公开来源带有此字段，统计从该记录隐藏的非官方 URL；不代表全部内部记录的隐藏数量 |
| `发布日期或更新日期`、`本次访问日期` | 原页面日期与原核查访问日期，保留文字形式 |
| `可见页面或面`、`已核字段与位置` | 原记录可支持的页面、证面、字段与位置 |
| `核查状态` | 原证据核查状态，不等于发布链接可达性 |
| `适用证件与范围`、`适用证件版本` | 原证据适用对象、范围与版次 |
| `release_version` | 发布标识 |

非公开来源不出现 URL 与发布机构详情，也不出现任何含链接的检查结果。含 URL 的完整访问记录
只保存在 `internal/source_publication_audit.csv` 的 `check_result` 字段。

## 7. 哈希口径

明文编码统一为 UTF-8。各类哈希分别用于不同对象，不能混用：

```python
import hashlib, json

def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def canonical_hash(obj) -> str:
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return text_hash(text)
```

| 对象 | 口径 |
| --- | --- |
| 单条正文 | `text_hash(prompt)` |
| clean 取值 | `canonical_hash(expected_visible_text)` |
| 一组正文 | `canonical_hash({variant: text_hash(prompt)})`，只含实际存在的档位 |
| 模板签名 | `sha256("|".join([canonical_hash(shared_prompt_sections), json.dumps([槽位 field 列表], ensure_ascii=False), 槽位类型串]))`，槽位类型串按 `visible_chunks` 顺序把含 `field` 的记 `F`、其余记 `L` |
| 发布模板对象 | `canonical_hash(发布副本中的整个模板对象)` |
| 内部模板对象 | `canonical_hash(内部 v10 的整个模板对象)` |
| 文件 | 文件字节的 SHA-256，见 `SHA256SUMS.txt` 与 `release_manifest.json` |

**正文哈希、取值哈希、模板哈希和整行哈希必须分开记录。** 发布转换改变整行哈希时，不代表
正文哈希或取值哈希发生变化。发布副本中 2,986 条正文哈希与可见值哈希与内部 v10 全量一致；
383 条模板已确认记录的发布对象哈希全部可复算。

## 8. 导出规则

CSV／TXT 由主数据重新生成，规则固定：

| 类型 | 导出形式 |
| --- | --- |
| 布尔 | `true` / `false`（小写） |
| 空值 `null` | 空单元格 |
| 字典、列表 | 紧凑 JSON：`ensure_ascii=False`，分隔符 `(",", ":")`（嵌套字典和列表不转成自然语言） |
| 文本 | 原样字符串；含换行时按 CSV 引号规则转义 |
| 编码 | CSV: UTF-8 无 BOM，行结束符 CRLF；JSONL／JSON／TXT: UTF-8 无 BOM，行结束符 LF |

`final/prompts.txt` 按 `prompts.jsonl` 的行序输出，每条前有分隔线与 `prompt_id` 等头部，
正文完整保留。

`config/specs.json` 中的 `generation_contract.source_binding` 是内部补证包的文件哈希绑定；
本发布把它替换为 `{"publication": "withheld", "internal_file_count": N, "note": ...}`，只保留数量，
不公开内部文件路径。`config/profiles.json` 中原有的 `source_files`（内部材料卡路径）已整体移除。
`config/sources.json` 中原有的 `origin_files` 已移除，改为 `internal_origin_file_count` 计数。

## 9. 记录条数与唯一 ID 数

公开配置里存在**原数据自身**的重复 ID，因此“记录条数”与“唯一 ID 数”不同：

| 文件 | 记录条数 | 唯一 ID 数 | 重复 ID |
| --- | ---: | ---: | --- |
| `config/specs.json` | 105 | 104 | `EXEC-V7-E07-uk` |
| `config/profiles.json` | 51 | 50 | `P1007-V6-E07-uk` |
| `config/templates.json` | 56 | 55 | `EXEC-V6-E07-uk` |

重复 ID 的两条对象哈希、差异字段与影响范围逐条登记在
`config/known_reference_exceptions.json` 的 `duplicate_ids` 字段。同一 ID 下的两条模板记录内容相同；
两条重复规格与两条重复画像内容不同。

**读取这些文件时必须按行处理。** 按 ID 建字典会静默丢掉一条记录；遇到同名 ID 时应报告歧义，
不得默认取第一条或最后一条。`src/validate_release.py` 的 V30／V31 会分别核对重复 ID 是否与
登记一致，并报出上述两个数字。

## v3 校验补充

V32 按实际组成员复算正文与clean取值绑定，并核对review与prompt的组别、档位和正文确认标记。V33 同时核对发布模板、去掉release_version后的内部模板及解析状态。V41 从实际引用复算七个悬空ID的逐项影响与去重并集：profile为72条／24组，spec为57条／19组，总计129条／43组。

## 10. 组级阶段字段

以下字段保留运行阶段的信息，不构成人工确认。字段可能只在部分记录出现。

| 字段 | 说明 |
| --- | --- |
| `generation_family` | 生成阶段或保留基线的来源系列标签 |
| `source_status`、`layout_status` | 来源与版式的阶段状态，保留原文字 |
| `revision_version` | 部分修订组记录的修订标签 |
| `baseline_prompt_id` | 部分继承组对应的基线提示词 ID |
| `evidence_level`、`execution_status` | 部分阶段记录的证据层级与执行状态 |
| `text_review` | 部分记录保留的历史文字审阅说明 |

## 11. QA 汇总字段

`sources_publication` 的三个分类互不重叠。`identifier_only` 只统计该枚举，
不再把待核项包含在内；`unpublished_total` 是 `identifier_only` 与
`identifier_only_pending` 之和。`measured_file_hashes` 保留七个主数据文件的字节哈希。
历史 AI 审读数字标为继承记录，公开工具不能重做当时的原始判定。
