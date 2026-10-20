#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify SHA256SUMS.txt and release_manifest.json against the actual files.

Checks
------
* every path listed in SHA256SUMS.txt exists and hashes as recorded
* every payload path in release_manifest.json exists, has the recorded size
  and hash
* no unlisted extra files inside the repository (SHA256SUMS.txt itself is
  excluded by design)
* no duplicate or malformed entries

Nothing is written.

Usage
-----
    python verify_hashes.py --repo <repo_dir>

Exit codes
----------
0  hashes and file set consistent
1  hash mismatch, missing file, extra file, or malformed checksum list
2  argument error / checksum files not found
"""
import argparse
import hashlib
import json
import os
import sys

EXCLUDED_FROM_SUMS = {"SHA256SUMS.txt"}
EXCLUDED_FROM_MANIFEST = {"SHA256SUMS.txt", "release_manifest.json"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_sums(path):
    entries = []
    problems = []
    with open(path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if len(line) < 67 or line[64:66] != "  ":
                problems.append("line %d: malformed entry %r" % (lineno, line[:80]))
                continue
            digest, rel = line[:64], line[66:]
            if not all(c in "0123456789abcdef" for c in digest):
                problems.append("line %d: not a hex digest" % lineno)
                continue
            entries.append((rel, digest))
    return entries, problems


def main(argv=None):
    ap = argparse.ArgumentParser(description="Verify release checksums and file set")
    ap.add_argument("--repo", required=True, help="release repository directory")
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(repo):
        sys.stderr.write("repository directory not found: %s\n" % repo)
        return 2
    sums_path = os.path.join(repo, "SHA256SUMS.txt")
    manifest_path = os.path.join(repo, "release_manifest.json")
    if not os.path.exists(sums_path):
        sys.stderr.write("checksum file not found: %s\n" % sums_path)
        return 2

    entries, problems = parse_sums(sums_path)
    listed = [rel for rel, _ in entries]
    dupes = sorted({r for r in listed if listed.count(r) > 1})

    missing = []
    mismatched = []
    for rel, digest in entries:
        full = os.path.join(repo, rel.replace("/", os.sep))
        if not os.path.exists(full):
            missing.append(rel)
            continue
        actual = sha256_file(full)
        if actual != digest:
            mismatched.append({"path": rel, "expected": digest, "actual": actual})

    manifest_problems = []
    manifest_size_errors = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, ValueError) as exc:
            manifest_problems.append("cannot read release_manifest.json: %s" % exc)
            manifest = None
        if manifest is not None:
            for item in manifest.get("payload_files", []):
                rel = item.get("path")
                full = os.path.join(repo, str(rel).replace("/", os.sep))
                if not os.path.exists(full):
                    manifest_problems.append("manifest path missing: %s" % rel)
                    continue
                if os.path.getsize(full) != item.get("bytes"):
                    manifest_size_errors.append(
                        {"path": rel, "expected": item.get("bytes"),
                         "actual": os.path.getsize(full)})
                if sha256_file(full) != item.get("sha256"):
                    manifest_problems.append("manifest hash mismatch: %s" % rel)
    else:
        manifest_problems.append("release_manifest.json not found")

    actual_files = set()
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for fn in filenames:
            if fn.endswith((".pyc", ".pyo")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), repo).replace(os.sep, "/")
            actual_files.add(rel)

    extra = sorted(actual_files - set(listed) - EXCLUDED_FROM_SUMS)
    listed_set = set(listed)
    if manifest_path and os.path.exists(manifest_path):
        pass

    failed = bool(problems or dupes or missing or mismatched or manifest_problems
                  or manifest_size_errors or extra)
    report = {
        "schema": "deepseek-release-hash-verification-v1",
        "repo": repo,
        "sha256sums_entries": len(entries),
        "manifest_payload_files": len(json.load(open(manifest_path, encoding="utf-8"))
                                      .get("payload_files", []))
        if os.path.exists(manifest_path) else 0,
        "actual_files": len(actual_files),
        "malformed_entries": problems,
        "duplicate_entries": dupes,
        "missing_files": missing,
        "hash_mismatches": mismatched,
        "manifest_problems": manifest_problems,
        "manifest_size_errors": manifest_size_errors,
        "extra_files_not_listed": extra,
        "passed": not failed,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
