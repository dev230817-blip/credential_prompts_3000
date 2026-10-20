# 字段说明

JSONL 每行一条完整记录。团队 CSV 固定 12 列：

| 字段 | 含义 |
| --- | --- |
| sample_id | CRD-0001 至 CRD-3000，本版唯一编号 |
| direction | credential |
| category_l1 / category_l2 | 用途一级与二级分类 |
| variant | 全部 clean，表示没有设计内容异常，不表示真实照片 |
| aspect_ratio | 输出画布约定，不是实物尺寸测量 |
| prompt | 直接用于本版文生图实验的完整指令 |
| group_id | 按团队导出约定留空；基础组关联见 extra_json.source_group_id |
| target_texts | 预期可见字段值，以竖线连接；需要无歧义结构时读取 JSONL 的 expected_visible_text |
| tamper_types / tamper_details | 留空 |
| extra_json | CSV 中编码为 JSON 字符串；JSONL 中为对象 |

extra_json 保存对象、版式、来源 ID、国家、页别、指令语言、可见文字语言、载体、成像方式、待核项及历史追溯。capture_mode 使用 scan/front_photo/oblique_photo；电子页面的 scan 表示电子平面呈现，不能解释为实体扫描。capture_label 给出人类可读的当前名称。

JSONL 另外保存 expected_visible_text、prompt_sha256、version、manual_body_approved、image_generated、image_accepted 和领域审核限制。prompt_sha256 对 prompt 的 UTF-8 字节计算 SHA-256，不含额外换行。源提示词、当前正文、历史 v3 正文的哈希分别记录，不互换。

source_body_approved 只描述历史 source_prompt。manual_body_approved 才是本版正文确认状态。reports/review_status.jsonl 按 sample_id 和当前正文哈希绑定。

provenance/approved_parent_overrides.json 记录 3 组、6 字段的限定修正。基础文件同时保存 source_expected_visible_text 和当前 expected_visible_text，校验器逐字段核对该变换。
