# 审核范围

2026-10-11，使用者明确选择“全部2,986条最新版正文”，确认指向本版完整提示词。每条正文与实际ID、SHA-256绑定，组级绑定只包含该组实际存在的档位。此记录依据使用者声明，不声称独立见证逐条阅读。

当前正文确认2,986条、未确认0条，覆盖1,000组。本次建立2,986条确认事件，其中历史已确认383个ID内，290条正文曾因累计修订改变，93条未变；历史范围外新增覆盖2,603个ID。原确认时间、依据与失效历史保存在每条审核记录的 `historical_confirmation` 中。

独立clean取值确认仍为129组，不扩大为全量取值确认。历史54样式模板确认另存；只有当前共用段落与旧独立确认对象一致的绑定继续有效，当前保留31组／31样式。全量正文确认不自动扩大独立模板确认。

程序QA、历史AI审读、使用者正文确认、来源核实与图片验收分别统计。历史AI重判486条的187已解决／218有据限制／60不成立／21登记无误仍保留；停止继续核源不等于来源事实全部通过。

当前 `ready_for_generation=false`、`image_generated=false`、`image_review_status=not_reviewed`，当前版本图片生成与验收0。历史18图属于旧版，不计入本版。

## 当前包可复算摘要

| 指标 | 当前值 |
| --- | --- |
| `release_version` | `codex-20261011-feedback-v4` |
| `groups` | `1000` |
| `prompts` | `2986` |
| `body_confirmed_rows` | `2986` |
| `body_unconfirmed_rows` | `0` |
| `clean_fields_confirmed_groups` | `129` |
| `template_confirmed_styles` | `31` |
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
