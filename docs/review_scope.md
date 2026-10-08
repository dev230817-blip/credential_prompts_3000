# review_scope.md — 确认范围与未确认范围

本文件区分四层状态：程序检查、AI 辅助审读、人工确认、图片状态。四层彼此独立，
不能互相替代，也不能相加。

## 1. 人工确认范围

使用者本人在 2026-10-07 答复「已全部确认」，并选定「逐批已看过内容，按『按内容确认』登记」。
确认范围就是人工待审包的全部内容：

| 层级 | 覆盖 | 说明 |
| --- | ---: | --- |
| 模板 | 54 个样式 | 129 个被确认组落到 54 个 `profile_id` |
| clean 取值 | 129 组 | 只表达本组 clean 取值已确认 |
| 正文 | 129 组 / 383 条 | 逐条正文确认 |
| 图片 | 0 | 本轮未执行生图与图片复核 |

129 组覆盖 29 个配额单元、54 个活跃样式、50 个实体。

**范围外 2,603 条正文仍未确认。** 2,986 减 383 等于 2,603。

clean 取值确认不得扩展为 subtle 与 strong 的取值确认；模板确认按实际模板、哈希与适用范围
逐项核查，不凭相同 `profile_id` 无条件扩展。

## 2. 确认与哈希绑定的关系

三项确认各自绑定到实际对象哈希：

- 单条正文绑定：`sha256(prompt)`；
- 一组正文绑定：`canonical_hash({variant: sha256(prompt)})`，只含实际存在的档位；
- clean 取值绑定：`canonical_hash(expected_visible_text)`；
- 模板绑定：模板签名哈希 `template_binding_sha256` 与完整模板对象哈希 `template_object_sha256`
  同时核对。

哈希口径见 `data_fields.md` 第 7 节。`final/review_status.jsonl` 逐条给出上述绑定结果。

**绑定是组级记录，不能把「129 个组级正文绑定」当成「129 条正文」。** 129 个组级绑定覆盖
383 条正文。

本次发布只做绑定同步：对象哈希已重新复算并匹配，原确认时间、原确认依据和失效历史保持
不变。发布转换改变了整行哈希，但正文哈希、取值哈希和模板哈希各自独立，未混用。

## 3. AI 辅助审读（历史）

全量 2,986 条做过一轮 AI 辅助审读：

| 原判 | 条数 |
| --- | ---: |
| 通过 | 2,500 |
| 需返修 | 302 |
| 待核 | 184 |

后两类共 486 条做过最终重判：

| 结论 | 条数 |
| --- | ---: |
| 已解决 | 187 |
| 有据限制 | 218 |
| 不成立 | 60 |
| 登记无误 | 21 |

按原状态拆分：需返修的 302 条中，已解决 187、有据限制 49、不成立 45、登记无误 21；
待核的 184 条中，有据限制 169、不成立 15。

**有据限制 218 条仍然是限制。** 它们表示依据不足以支持结论，不因为本次发布包通过检查就变成
「事实全部通过」。AI 辅助审读结论不等于人工确认，也不计入人工确认数量。

## 4. 图片状态

- `ready_for_generation`：全量 `false`
- `image_generated`：全量 `false`
- `image_review_status`：全量 `not_reviewed`
- 当前版本生成及验收图片：0

生图与图片复核已取消。`difficulty_status` 与 `single_image_detectable` 是设计层声明，
不表示实际图片难度已经验证。本包不包含任何图片验收结论。

## 5. 本次发布新增的确认

**0。** 发布副本没有新增任何人工确认，没有把程序检查或 AI 审读登记成人工确认，也没有
因为重建 CSV 而改变确认范围。

内部早期记录另有 24 组 clean 取值确认、0 条历史正文确认和 18 张历史图片。
它们属于各自的历史 ID／哈希范围，不与本包 129 组／383 条或当前图片 0 相加，
也不能从本包的一个状态枚举反推出这 24 组历史范围。

本包组文件中有 12 组保留“使用者已审核通过文字取值”或“沿用已审字段”的原状态。
其中 3 组已被当前确认绑定覆盖；其余 9 组对应 27 条正文记录，当前取值状态为
`clean_fields_legacy_inherited`。旧标签与当前绑定分别统计，不修改原组记录。

## 6. 使用者裁定

配额调整沿用既有裁定：`C19-house` 与 `E10-brn` 划除配额并保留原因，`C13-main`、
`C17-school`、`C16-legal`、`E06-us` 增加配额。原 3,000 条目标与实际 2,986 条之间的 14 条
差额按已有裁定保留，本次不补。

## 当前包可复算摘要

此表只统计当前公开记录；校验器从实际数据独立复算。历史 24 组与 18 图不在此表中。

| 指标 | 当前值 |
| --- | --- |
| `release_version` | `codex-20261007-v3` |
| `groups` | `1000` |
| `prompts` | `2986` |
| `body_confirmed_rows` | `383` |
| `body_unconfirmed_rows` | `2603` |
| `clean_fields_confirmed_groups` | `129` |
| `template_confirmed_styles` | `54` |
| `index_published` | `120` |
| `identifier_only` | `96` |
| `identifier_only_pending` | `6` |
| `unpublished_total` | `102` |
| `configured_unique_profiles` | `50` |
| `referenced_profiles` | `54` |
| `unreferenced_configured_profiles` | `0` |
| `historical_status_groups` | `12` |
| `historical_status_now_confirmed_groups` | `3` |
| `legacy_inherited_groups` | `9` |
| `legacy_inherited_rows` | `27` |
