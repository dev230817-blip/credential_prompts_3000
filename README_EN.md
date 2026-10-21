# credential_prompts_3000

English | [中文](README.md)

Credential prompts for research on AI-generated text-rich images. The repository retains its historical name. The current delivery is [20261021_seal_v1](deliveries/20261021_seal_v1/README.md), a seal-requirement patch of the preserved 20261021_v2 release: **1,430 categories / 4,290 clean prompts**, with 5 first-level and 40 second-level categories.

Use the [patched CSV](deliveries/20261021_seal_v1/证件类提示词_4290条.csv) and [illustrated explanation](deliveries/20261021_seal_v1/证件类_分类与生图说明.md). Seals are required for 546 categories, not forced for 578, and conditional on the selected style for 306. Only seal instructions and derived prompt hashes changed from the current delivery CSV. Its existing category display paths and corrected canvas ratios are preserved. No new images were generated; the eight existing illustrations are not validation of this patch. The v2 exports linked below remain an unchanged baseline and do not include this patch.

The user selected policy A: three prompts in each group supply identical core values while layout, fixed prose and decoration may vary. These are information groups, not controlled views of one identical document. The 1,418 physical categories have scan/front/oblique modes (4,254 rows); the 12 electronic categories have native-page/front-screen/oblique-screen modes (36 rows).

Use the [12-column CSV](releases/20261021_v2/data/credential_prompts_4290_unified.csv), [TXT](releases/20261021_v2/data/prompts.txt), [Excel](releases/20261021_v2/data/prompts_filter.xlsx), [JSONL](releases/20261021_v2/data/prompts.jsonl), or [12 examples](releases/20261021_v2/docs/examples_12.md).

target_texts contains supplied core values only, not the complete page transcription or the final reading order. content_group_id links these values; group_id retains the team text-tampering meaning and stays empty. The output canvas ratio does not fix document shape. The previous generic layout skeleton, forced seal style and synthetic boilerplate are removed.

All three archived releases remain unchanged: [20261021_v1](releases/20261021_v1/README.md), 4,290 prompts with frozen full input text and synthetic layouts; [20261020_v1](releases/20261020_v1/README.md), 3,000 clean prompts; and [20261011_v4](releases/20261011_v4/README.md), 2,986 clean/subtle/strong prompts. Git history is preserved.

No category or source research was repeated. Previous user-provided pilot images supported the direction but also showed invented details, instruction leakage and cropping. The revised controls have not been image-tested. No images were generated or accepted for this new release, and new prompts have not been individually approved. Supplied names and records are fictional. Real credentials and internal files are not included. The delivery patch includes eight existing synthetic illustrations. See [field semantics](releases/20261021_v2/docs/data_fields.md), [pilot scope](releases/20261021_v2/docs/pilot_feedback.md), [offline reproduction](releases/20261021_v2/docs/reproduction_scope.md), and [limits](releases/20261021_v2/docs/review_and_limits.md). Licensing remains undecided; no new LICENSE is added.
