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
| body_confirmed rows | 2986 |
| Unconfirmed body rows | 0 |
| clean-fields confirmed groups | 129 |
| template confirmed groups | 31 |
| template confirmed styles | 31 |
| New human confirmations in this release | 2986 |
| Images generated / reviewed | 0 |
| ready_for_generation = true | 0 |
| image_generated = true | 0 |

On 2026-10-11 the user explicitly confirmed all 2,986 latest prompt bodies. The 2,986 confirmation events include reconfirmation; 2,603 IDs were outside the historical 383-body scope. Independent clean-field and template approvals retain their own bindings.

## 4. Source publication

| Item | Value |
| --- | ---: |
| Source records | 222 |
| Published as official index | 120 |
| Identifier only | 96 |
| Identifier only, provenance pending | 6 |
| Unpublished total (the preceding two categories) | 102 |

Official status is decided by the publishing body **and** the original channel. Third-party mirrors of official content are not presented as the official original link. Every referenced `source_id` resolves to a record; records whose provenance is not confirmed are published as identifier-only.

## 5. Retained limits

Historical AI-review outcomes are inherited from internal records, not recomputed judgments. The JSON report retains their original Chinese category keys: resolved, evidence-backed limitations, unsubstantiated and correctly registered, respectively. Machine validation does not add human confirmation.

- All 2,986 current bodies were explicitly confirmed by the user; independent field/template and source statuses remain separate.
- 218 inherited evidence-backed limitations remain unresolved limitations.
- Single-image detectability and difficulty have not been tested through image review.
- Unspecified coordinates, font sizes, materials and security features are not inferred.
- No license has been selected for this version.

## 6. Data measured

The primary-data hashes are retained in `qa_report.json`. For the complete file set, use `SHA256SUMS.txt` and `release_manifest.json` at the repository root.
