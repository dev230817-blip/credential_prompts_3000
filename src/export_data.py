#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate the CSV/TXT convenience exports from the release main data.

Main data (JSONL/JSON) is authoritative. This script never edits it.

Usage
-----
    python export_data.py --repo <repo_dir> --out <new_dir>

`--out` must not exist yet; the script refuses to overwrite anything.

Export rules (same as the shipped exports)
------------------------------------------
* booleans      -> ``true`` / ``false`` (lower case)
* null          -> empty cell
* dict / list   -> compact JSON, ``ensure_ascii=False, separators=(",", ":")``
* text          -> verbatim; embedded newlines are CSV-quoted
* encoding      -> UTF-8 without BOM, CRLF line endings for CSV

Exit codes
----------
0  success
1  source data unreadable/inconsistent
2  argument error, or the output directory already exists
"""
import argparse
import csv
import json
import os
import sys


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


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return str(v)


def ordered_fields(rows, first):
    names = list(first)
    for r in rows:
        for k in r:
            if k not in names:
                names.append(k)
    return names


def write_csv(path, rows, fieldnames):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\r\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: cell(r.get(k)) for k in fieldnames})


def main(argv=None):
    ap = argparse.ArgumentParser(description="Export release CSV/TXT convenience files")
    ap.add_argument("--repo", required=True, help="release repository directory")
    ap.add_argument("--out", required=True, help="new output directory (must not exist)")
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.repo)
    out = os.path.abspath(args.out)
    if os.path.exists(out):
        return die(2, "output directory already exists: %s" % out)
    if not os.path.isdir(repo):
        return die(2, "repository directory not found: %s" % repo)

    src = {
        "prompts": os.path.join(repo, "final", "prompts.jsonl"),
        "groups": os.path.join(repo, "final", "groups.jsonl"),
        "specs": os.path.join(repo, "config", "specs.json"),
        "sources": os.path.join(repo, "config", "sources.json"),
    }
    for name, path in src.items():
        if not os.path.exists(path):
            return die(1, "source data missing for %s: %s" % (name, path))

    try:
        prompts = load_jsonl(src["prompts"])
        groups = load_jsonl(src["groups"])
        specs = load_json(src["specs"])["specs"]
        sources = load_json(src["sources"])["sources"]
    except (OSError, ValueError, KeyError) as exc:
        return die(1, "cannot read source data: %s" % exc)

    if not prompts or not groups or not specs or not sources:
        return die(1, "source data is empty (prompts=%d groups=%d specs=%d sources=%d)"
                   % (len(prompts), len(groups), len(specs), len(sources)))

    os.makedirs(out)
    write_csv(os.path.join(out, "prompts.csv"), prompts,
              ordered_fields(prompts, prompts[0].keys()))
    write_csv(os.path.join(out, "groups.csv"), groups,
              ordered_fields(groups, groups[0].keys()))
    write_csv(os.path.join(out, "specs.csv"), specs,
              ordered_fields(specs, ["spec_id"]))
    write_csv(os.path.join(out, "sources.csv"), sources,
              ordered_fields(sources, ["source_id", "publication"]))

    with open(os.path.join(out, "prompts.txt"), "w", encoding="utf-8", newline="\n") as f:
        for r in prompts:
            f.write("=" * 78 + "\n")
            f.write("prompt_id: %s\n" % r.get("prompt_id"))
            f.write("group_id: %s\n" % r.get("group_id"))
            f.write("variant: %s\n" % r.get("variant"))
            f.write("profile_id: %s\n" % r.get("profile_id"))
            f.write("source_ids: %s\n" % json.dumps(r.get("source_ids", []),
                                                    ensure_ascii=False))
            f.write("-" * 78 + "\n")
            f.write(str(r.get("prompt", "")) + "\n\n")

    print("exported to %s" % out)
    for name in ("prompts.csv", "groups.csv", "specs.csv", "sources.csv", "prompts.txt"):
        p = os.path.join(out, name)
        print("  %-14s %10d bytes" % (name, os.path.getsize(p)))
    print("  rows: prompts=%d groups=%d specs=%d sources=%d"
          % (len(prompts), len(groups), len(specs), len(sources)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
