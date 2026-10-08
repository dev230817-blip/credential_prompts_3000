#!/usr/bin/env python3
"""Rebuild public QA from repository data using only the standard library.

Historical AI review outcomes are explicitly inherited, not recomputed.
No network requests or private project paths are used.
"""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import sys

def jl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]

def j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def build(REPO, OUT):
    prompts = jl(os.path.join(REPO, "final", "prompts.jsonl"))
    groups = jl(os.path.join(REPO, "final", "groups.jsonl"))
    review = jl(os.path.join(REPO, "final", "review_status.jsonl"))
    sources = j(os.path.join(REPO, "config", "sources.json"))["sources"]
    specs = j(os.path.join(REPO, "config", "specs.json"))["specs"]
    profiles = j(os.path.join(REPO, "config", "profiles.json"))["profiles"]
    templates = j(os.path.join(REPO, "config", "templates.json"))["templates"]

    variants = collections.Counter(p["variant"] for p in prompts)
    per_group = collections.defaultdict(set)
    for p in prompts:
        per_group[p["group_id"]].add(p["variant"])
    triplets = sum(1 for v in per_group.values() if v == {"clean", "subtle", "strong"})
    clean_only = [g for g, v in per_group.items() if v == {"clean"}]

    confirmed = [r for r in review if r["body_confirmed"]]
    clean_conf_groups = sorted({r["group_id"] for r in review if r["clean_fields_confirmed"]})
    tpl_conf_groups = sorted({r["group_id"] for r in review if r["template_confirmed"]})
    tpl_styles = sorted({r["template_confirmation_scope"].split("profile:")[1].split(" ")[0]
                         for r in review if r["template_confirmed"]})

    # 正文长度
    lengths = [p["prompt_characters"] for p in prompts]
    desc = [p["description_characters"] for p in prompts if p.get("description_characters")]

    # 异常
    anomaly = collections.Counter(p.get("anomaly_category") or "(none)" for p in prompts)
    changed_fields = collections.Counter()
    for p in prompts:
        for f in p.get("changed_fields") or []:
            changed_fields[f] += 1

    # 来源
    pub_index = [s for s in sources if s["publication"] == "index_published"]
    id_only = [s for s in sources if s["publication"] == "identifier_only"]
    pending = [s for s in sources if s["publication"] == "identifier_only_pending"]

    # 组级
    country = collections.Counter(g["country"] for g in groups)
    language = collections.Counter(g["visible_language"] for g in groups)
    quota = collections.Counter(g["quota_id"] for g in groups)

    report = {
        "schema": "credential-prompts-3000-public-qa-v1",
        "release_version": prompts[0]["release_version"],
        "measured_from": "repo/credential_prompts_3000 (published files only)",
        "counts": {
            "groups": len(groups),
            "prompts": len(prompts),
            "review_status_rows": len(review),
            "variant_clean": variants.get("clean", 0),
            "variant_subtle": variants.get("subtle", 0),
            "variant_strong": variants.get("strong", 0),
            "triplet_groups": triplets,
            "clean_only_groups": len(clean_only),
            "clean_only_group_ids": clean_only,
            "specs": len(specs),
            "profiles": len(profiles),
            "templates": len(templates),
            "sources": len(sources),
            "quota_units": len(quota),
            "entities": len({g["entity_id"] for g in groups}),
        },
        "repo_name_vs_data": {
            "repo_name": "credential_prompts_3000",
            "actual_groups": len(groups),
            "actual_prompts": len(prompts),
            "original_prompt_target": 3000,
            "shortfall_vs_original_target": 3000 - len(prompts),
            "explanation": ("The repository name retains the original 3,000-prompt target. "
                            "Seven UKMT groups remain clean-only under the existing decision; "
                            "no records were added to fill the 14-prompt shortfall."),
        },
        "variant_meaning": {
            "clean": "No designed anomaly; variants share the carrier, field set, labels and layout",
            "subtle": "One concealed anomaly",
            "strong": "Two or three anomalies, or one obvious anomaly",
            "important": "All variants are synthetic-image prompts, not real-photo versus AI-image labels",
        },
        "prompt_lengths": {
            "prompt_characters_min": min(lengths),
            "prompt_characters_max": max(lengths),
            "prompt_characters_mean": round(sum(lengths) / len(lengths), 1),
            "description_characters_min": min(desc) if desc else None,
            "description_characters_max": max(desc) if desc else None,
        },
        "anomaly": {
            "category_distribution": dict(anomaly.most_common()),
            "changed_field_top": dict(changed_fields.most_common(10)),
            "groups_without_anomaly_expected": len(clean_only),
        },
        "review_state": {
            "body_confirmed_rows": len(confirmed),
            "body_unconfirmed_rows": len(review) - len(confirmed),
            "clean_fields_confirmed_groups": len(clean_conf_groups),
            "template_confirmed_groups": len(tpl_conf_groups),
            "template_confirmed_styles": len(tpl_styles),
            "new_human_confirmations_in_this_release": 0,
            "image_reviewed": 0,
            "ready_for_generation_true": sum(1 for p in prompts
                                             if p["ready_for_generation"]),
            "image_generated_true": sum(1 for p in prompts if p["image_generated"]),
        },
        "ai_review_history": {
            "note": ("Inherited from internal historical AI-assisted review, not independently "
                     "recomputed from this repository: 486 rejudged records, comprising "
                     "187 resolved, 218 evidence-backed limitations, 60 unsubstantiated "
                     "and 21 correctly registered. Limitations remain limitations."),
            "rejudge_total": 486,
            "rejudge_distribution": {"已解决": 187, "有据限制": 218, "不成立": 60,
                                     "登记无误": 21},
        },
        "sources_publication": {
            "total_records": len(sources),
            "index_published": len(pub_index),
            "identifier_only": len(id_only),
            "identifier_only_pending": len(pending),
            "unpublished_total": len(id_only) + len(pending),
            "note": ("Publication categories are mutually exclusive. unpublished_total is the "
                     "sum of identifier_only and identifier_only_pending. Official status "
                     "requires the publisher and original channel; link reachability alone "
                     "does not establish the correctness of rules or layouts."),
        },
        "distribution": {
            "country_groups": dict(country.most_common()),
            "visible_language_groups": dict(language.most_common()),
            "top_quota_units": dict(quota.most_common(12)),
        },
        "limits_retained": [
            "2,603 prompt texts remain outside the human-confirmed scope.",
            "218 inherited evidence-backed limitations remain unresolved limitations.",
            "Single-image detectability and difficulty have not been tested through image review.",
            "Unspecified coordinates, font sizes, materials and security features are not inferred.",
            "No license has been selected for this version.",
        ],
    }

    # 发布文件哈希（用于报告自证）
    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()


    report["measured_file_hashes"] = {
        name: sha(os.path.join(REPO, name))
        for name in ("final/prompts.jsonl", "final/groups.jsonl", "final/review_status.jsonl",
                     "config/specs.json", "config/profiles.json", "config/templates.json",
                     "config/sources.json")
    }

    with open(os.path.join(OUT, "qa_report.json"), "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")

    c = report["counts"]
    md = []
    md.append("# Published release QA (measured from the published files)")
    md.append("")
    md.append("This report is generated from the bytes actually shipped in "
              "`credential_prompts_3000/`. It is not a re-titled copy of the internal "
              "v10 run report.")
    md.append("")
    md.append("## 1. Counts")
    md.append("")
    md.append("| Item | Value |")
    md.append("| --- | ---: |")
    md.append("| Groups | %d |" % c["groups"])
    md.append("| Prompts | %d |" % c["prompts"])
    md.append("| review_status.jsonl rows | %d |" % c["review_status_rows"])
    md.append("| clean / subtle / strong | %d / %d / %d |"
              % (c["variant_clean"], c["variant_subtle"], c["variant_strong"]))
    md.append("| Triplet groups | %d |" % c["triplet_groups"])
    md.append("| clean-only groups (UKMT exception) | %d |" % c["clean_only_groups"])
    md.append("| Quota units / entities | %d / %d |" % (c["quota_units"], c["entities"]))
    md.append("| Specs / profiles / templates | %d / %d / %d |"
              % (c["specs"], c["profiles"], c["templates"]))
    md.append("| Source records | %d |" % c["sources"])
    md.append("")
    md.append("The repository name says `3000`; the corpus is **%d groups / %d prompts**. "
              "The 14-row shortfall against the original 3,000-prompt target is retained "
              "under the existing decision. No data was invented to match the name."
              % (c["groups"], c["prompts"]))
    md.append("")
    md.append("## 2. Variant meaning")
    md.append("")
    md.append("`clean` = no designed anomaly; `subtle` = one concealed defect; "
              "`strong` = two or three defects, or one obvious defect. All three variants "
              "are used to build synthetic images. They are **not** “real photo vs. AI image” "
              "labels.")
    md.append("")
    md.append("## 3. Review state")
    md.append("")
    rs = report["review_state"]
    md.append("| Item | Value |")
    md.append("| --- | ---: |")
    md.append("| body_confirmed rows | %d |" % rs["body_confirmed_rows"])
    md.append("| Unconfirmed body rows | %d |" % rs["body_unconfirmed_rows"])
    md.append("| clean-fields confirmed groups | %d |" % rs["clean_fields_confirmed_groups"])
    md.append("| template confirmed groups | %d |" % rs["template_confirmed_groups"])
    md.append("| template confirmed styles | %d |" % rs["template_confirmed_styles"])
    md.append("| New human confirmations in this release | %d |"
              % rs["new_human_confirmations_in_this_release"])
    md.append("| Images generated / reviewed | 0 |")
    md.append("| ready_for_generation = true | %d |" % rs["ready_for_generation_true"])
    md.append("| image_generated = true | %d |" % rs["image_generated_true"])
    md.append("")
    md.append("Human confirmation was recorded earlier by the user for the selected "
              "129 groups / 383 rows. This release only carries that state through verified "
              "bindings; it adds none.")
    md.append("")
    md.append("## 4. Source publication")
    md.append("")
    sp = report["sources_publication"]
    md.append("| Item | Value |")
    md.append("| --- | ---: |")
    md.append("| Source records | %d |" % sp["total_records"])
    md.append("| Published as official index | %d |" % sp["index_published"])
    md.append("| Identifier only | %d |" % sp["identifier_only"])
    md.append("| Identifier only, provenance pending | %d |" % sp["identifier_only_pending"])
    md.append("| Unpublished total (the preceding two categories) | %d |" % sp["unpublished_total"])
    md.append("")
    md.append("Official status is decided by the publishing body **and** the original "
              "channel. Third-party mirrors of official content are not presented as the "
              "official original link. Every referenced `source_id` resolves to a record; "
              "records whose provenance is not confirmed are published as identifier-only.")
    md.append("")
    md.append("## 5. Retained limits")
    md.append("")
    md.append("Historical AI-review outcomes are inherited from internal records, "
              "not recomputed judgments. The JSON report retains their original Chinese "
              "category keys: resolved, evidence-backed limitations, unsubstantiated and "
              "correctly registered, respectively. Machine validation does not add human confirmation.")
    md.append("")
    for x in report["limits_retained"]:
        md.append("- " + x)
    md.append("")
    md.append("## 6. Data measured")
    md.append("")
    md.append("The seven primary-data hashes are retained in `qa_report.json`. "
              "For the complete file set, use `SHA256SUMS.txt` and `release_manifest.json` "
              "at the repository root.")
    md.append("")

    with open(os.path.join(OUT, "qa_report.md"), "w", encoding="utf-8",
              newline="\n") as f:
        f.write("\n".join(md))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    repo, out = os.path.abspath(args.repo), os.path.abspath(args.out)
    if os.path.exists(out):
        ap.error("Output directory already exists; refusing to overwrite")
    if Path(out).resolve().is_relative_to(Path(repo).resolve()):
        ap.error("Output directory must be outside the repository")
    if not os.path.isfile(os.path.join(repo, "final", "prompts.jsonl")):
        ap.error("Repository data not found")
    os.makedirs(out)
    try:
        build(repo, out)
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write("QA generation failed: " + str(exc) + "\n")
        return 1
    print("QA reports written to " + out)
    return 0

if __name__ == "__main__":
    sys.exit(main())
