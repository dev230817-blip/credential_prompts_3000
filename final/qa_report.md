# Published release QA (measured from the published files)

This report is generated from the bytes actually shipped in `credential_prompts_3000/`. It is not a re-titled copy of the internal v10 run report.

## 1. Counts

| Item | Value |
| --- | ---: |
| Groups | 1000 |
| Prompts | 2986 |
| review_status.jsonl rows | 2986 |
| clean / subtle / strong | 1000 / 993 / 993 |
| Triplet groups | 993 |
| clean-only groups (UKMT exception) | 7 |
| Quota units / entities | 29 / 50 |
| Specs / profiles / templates | 105 / 51 / 56 |
| Source records | 222 |

The repository name says `3000`; the corpus is **1000 groups / 2986 prompts**. The 14-row shortfall against the original 3,000-prompt target is retained under the existing decision. No data was invented to match the name.

## 2. Variant meaning

`clean` = no designed anomaly; `subtle` = one concealed defect; `strong` = two or three defects, or one obvious defect. All three variants are used to build synthetic images. They are **not** “real photo vs. AI image” labels.

## 3. Review state

| Item | Value |
| --- | ---: |
| body_confirmed rows | 383 |
| Unconfirmed body rows | 2603 |
| clean-fields confirmed groups | 129 |
| template confirmed groups | 129 |
| template confirmed styles | 54 |
| New human confirmations in this release | 0 |
| Images generated / reviewed | 0 |
| ready_for_generation = true | 0 |
| image_generated = true | 0 |

Human confirmation was recorded earlier by the user for the selected 129 groups / 383 rows. This release only carries that state through verified bindings; it adds none.

## 4. Source publication

| Item | Value |
| --- | ---: |
| Source records | 222 |
| Published as official index | 120 |
| Identifier only | 102 |
| Identifier only, provenance pending | 6 |

Official status is decided by the publishing body **and** the original channel. Third-party mirrors of official content are not presented as the official original link. Every referenced `source_id` resolves to a record; records whose provenance is not confirmed are published as identifier-only.

## 5. Retained limits

- 2,603 条正文未在人工确认范围内，仍是未确认。
- 有据限制 218 条仍为限制，未在本次转为事实通过。
- 单图可判性与实际难度未由图片复核验证。
- 未明示的坐标、字号、材质与防伪不推断。
- 首版未添加许可证。

## 6. Data measured

| File | SHA-256 |
| --- | --- |
| `final/prompts.jsonl` | `d717aa843d91102617a9354a7af5449774201c152ad4c8ce2bf8152d84fc2370` |
| `final/groups.jsonl` | `3dad25003251974f22dccbbd43dbe18056bddbb894c6774dfeb77896d44e84c4` |
| `final/review_status.jsonl` | `9bc1e7382a52fa4d2100f16a51ce98672a4a1143efb49952c581227bd4ea8968` |
| `config/specs.json` | `3da29311f66e1a0c5ea2ad0eb0039bbb6839e87b2ef84a657d1984df5eca1c40` |
| `config/profiles.json` | `f44f8dd91488d1d3f62f36bb9cf4e8f7c451b537fa9184a7c6504e7634bb262b` |
| `config/templates.json` | `d8c7324647344eec82393025efc7b8a4dc0bf7019939e6ce2a9092175d145cdb` |
| `config/sources.json` | `eb9216c79d1ecc1beef1eba3bf08e1cb0e6d5ab4475457f8fd4e1428b3d31d9f` |
