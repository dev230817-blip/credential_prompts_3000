#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only example reader for the credential_prompts_3000 release.

Standard library only. Does not call any model or network service.

Usage
-----
    python read_example.py --data <repo_dir>
    python read_example.py --data <repo_dir> --prompt-id <prompt_id>
    python read_example.py --data <repo_dir> --group-id <group_id>

Exit codes
----------
0  success
1  data files missing or unreadable
2  argument error, or the requested object does not exist
"""
import argparse
import json
import os
import sys

MAX_PROMPT_PREVIEW = 400


def die(code, message):
    sys.stderr.write(message + "\n")
    return code


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError("%s line %d: %s" % (path, lineno, exc))
    return rows


def shorten(value, limit):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    if len(text) <= limit:
        return text
    return text[:limit] + " …(+%d chars)" % (len(text) - limit)


def show_prompt(rec, full=False):
    print("prompt_id   : %s" % rec.get("prompt_id"))
    print("group_id    : %s" % rec.get("group_id"))
    print("profile_id  : %s" % rec.get("profile_id"))
    print("variant     : %s" % rec.get("variant"))
    print("entity/quota: %s / %s" % (rec.get("entity_id"), rec.get("quota_id")))
    print("country/lang: %s / %s" % (rec.get("country"), rec.get("visible_language")))
    print("source_ids  : %s" % json.dumps(rec.get("source_ids", []), ensure_ascii=False))
    print("anomaly     : category=%s count=%s changed=%s" % (
        rec.get("anomaly_category"), rec.get("anomaly_count"),
        rec.get("changed_field_count")))
    print("review      : body_approved=%s variant=%s" % (
        rec.get("body_approved"), rec.get("variant_review_status")))
    print("image       : ready_for_generation=%s image_generated=%s" % (
        rec.get("ready_for_generation"), rec.get("image_generated")))
    print("visible text:")
    evt = rec.get("expected_visible_text") or {}
    for k, v in evt.items():
        print("  %-24s %s" % (k, v))
    print("prompt:")
    print(shorten(rec.get("prompt", ""), 100000 if full else MAX_PROMPT_PREVIEW))
    print()


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Read-only viewer for credential_prompts_3000")
    ap.add_argument("--data", required=True,
                    help="path to the release repository directory")
    ap.add_argument("--prompt-id", default=None,
                    help="show only this prompt_id")
    ap.add_argument("--group-id", default=None,
                    help="show the prompts of this group_id")
    ap.add_argument("--limit", type=int, default=3,
                    help="max rows to show when no id is given (default 3)")
    ap.add_argument("--full", action="store_true",
                    help="print the whole prompt body instead of a preview")
    args = ap.parse_args(argv)

    if args.prompt_id and args.group_id:
        return die(2, "give either --prompt-id or --group-id, not both")
    if args.limit < 1:
        return die(2, "--limit must be >= 1")

    data = os.path.abspath(args.data)
    prompts_path = os.path.join(data, "final", "prompts.jsonl")
    if not os.path.exists(prompts_path):
        return die(1, "data file not found: %s" % prompts_path)

    try:
        rows = load_jsonl(prompts_path)
    except (OSError, ValueError) as exc:
        return die(1, "cannot read %s: %s" % (prompts_path, exc))

    print("release data : %s" % prompts_path)
    print("record count : %d" % len(rows))
    print()

    if args.prompt_id:
        picked = [r for r in rows if r.get("prompt_id") == args.prompt_id]
        if not picked:
            return die(2, "prompt_id not found: %s" % args.prompt_id)
    elif args.group_id:
        picked = [r for r in rows if r.get("group_id") == args.group_id]
        if not picked:
            return die(2, "group_id not found: %s" % args.group_id)
        order = {"clean": 0, "subtle": 1, "strong": 2}
        picked.sort(key=lambda r: order.get(r.get("variant"), 9))
    else:
        picked = rows[:args.limit]

    for rec in picked:
        show_prompt(rec, full=args.full)
    return 0


if __name__ == "__main__":
    sys.exit(main())
