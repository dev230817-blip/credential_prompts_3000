#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read-only structural and content validator for the credential_prompts_3000 release.

This validator is deliberately independent of the packaging scripts. It checks
identity, not only counts: confirmation objects, group-level bindings, template
bindings and object hashes, full-field CSV reconciliation, source publication
rules and URL leakage.

Checks
------
Counting / identity
  V01-V09   row counts, variant distribution, group membership, unique ids
  V30-V31   registry of duplicate ids, record count vs unique id count
Referential integrity
  V10-V13   profile/spec resolution (with registered exceptions), source ids
Hash binding
  V14-V22   prompt and visible-field hashes, confirmation counts, clean and
            template group counts, image state
Content-level consistency
  V32       confirmation identity and group-level bindings
  V33       template binding signature and published object hash
  V24-V27   full-field CSV reconciliation for all four exports
Publication boundary
  V34       published sources satisfy every documented condition
  V35       no URL outside the published allowlist anywhere in the package
  V36       unpublished source records contain no URL string
  V37       publication split is reported
  V41       exact dangling-reference registry and deduplicated impacts
  V38       sources.csv leaks no URL for unpublished sources
  V39       the shipped ZIP leaks no URL outside the allowlist
Hygiene
  V23       no internal paths or secrets in published text
  V28-V29   release_version present, exception registry present

Nothing is written inside the repository. The report goes to --report-dir
(outside the repo) or to stdout.

Exit codes
----------
0  all checks passed
1  one or more checks failed
2  argument error / repository layout missing
"""
import argparse
import collections
import csv as _csv
import hashlib
import json
import os
import re
import sys
import zipfile

EXPECTED_GROUPS = 1000
EXPECTED_PROMPTS = 2986
EXPECTED_VARIANTS = {"clean": 1000, "subtle": 993, "strong": 993}
EXPECTED_TRIPLETS = 993
EXPECTED_CLEAN_ONLY = 7
EXPECTED_BODY_CONFIRMED = 383
EXPECTED_UNCONFIRMED = 2603
EXPECTED_CLEAN_GROUPS = 129
EXPECTED_TEMPLATE_GROUPS = 129
EXPECTED_TEMPLATE_STYLES = 54

INTERNAL_PATH_PATTERNS = [
    re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"),
    re.compile(r"implementation_1007|followup_124_20261007_v1|research_1007|"
               r"maintenance_20261007_v10_records|codex_closeout|replay_A|replay_B"),
    re.compile(r"(?<![\w:])/(?:home|Users|mnt|opt|var|tmp|srv)/"),
]
SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token)\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]
URL_PATTERN = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+")
PROVENANCE_BLOCK_MARKERS = ("第三方线索", "待官方源核实", "待核实", "出处未核",
                            "已失效", "本地接收", "不升级")
OFFICIAL_HOST_SUFFIX = (".gov.cn", ".gov", ".gov.uk", ".edu.cn", ".edu", ".ac.uk",
                        ".edu.au", ".gov.au", "publishing.service.gov.uk")
OFFICIAL_HOST_EXTRA = {
    "legislation.gov.uk", "www.legislation.gov.uk", "ukmt.org.uk",
    "www.cms.org.cn", "cms.org.cn", "www.nmc.org.uk", "www.gmc-uk.org",
    "www.hcpc-uk.org", "www.cods.org.cn", "www.icao.int",
    "www.consilium.europa.eu", "www.ox.ac.uk", "account.chsi.com.cn",
    "www.nidirect.gov.uk", "design.homeoffice.gov.uk",
    "companieshouse.blog.gov.uk",
}
NON_OFFICIAL_HOSTS = {"www.linkedin.com", "www.independent.co.uk", "www.bzchaxun.com",
                      "zw.china.com.cn", "114.255.111.180"}


def hs(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hc(o):
    return hs(json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


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


def official_host(host):
    if not host:
        return False
    if host in NON_OFFICIAL_HOSTS:
        return False
    if host in OFFICIAL_HOST_EXTRA:
        return True
    return any(host.endswith(suf) for suf in OFFICIAL_HOST_SUFFIX)


def host_of(url):
    m = re.match(r"https?://([^/]+)", url or "")
    return m.group(1).lower().split(":")[0] if m else ""


def walk_strings(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_strings(v, path + "/" + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_strings(v, path + "[%d]" % i)
    elif isinstance(obj, str):
        yield path, obj


def collect_source_ids(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "source_ids" and isinstance(v, list):
                acc.update(x for x in v if isinstance(x, str))
            else:
                collect_source_ids(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_source_ids(v, acc)


def export_cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return str(v)


def template_signature(t):
    """模板结构签名：共用段落 + 槽位字段顺序 + 槽位类型串。"""
    fields = json.dumps([x["field"] for x in t["visible_chunks"] if "field" in x],
                        ensure_ascii=False)
    tags = "".join("F" if "field" in x else "L" for x in t["visible_chunks"])
    return hs("|".join([hc(t["shared_prompt_sections"]), fields, tags]))


def body_access_failure(record):
    # A missing downloadable standard is not itself a failure to read the index.
    # Explicit reports of failure to retrieve/read the body are blocking.
    text = str(record.get("不能据此确认的内容", record.get("limitations", "")))
    return bool(re.search(r"(?:未(?:能)?(?:取得|取到|获取|读取|读到|取回)|无法|不能).{0,16}(?:正文|全文|附表)", text))


def template_binding_checks(review, templates):
    by_spec = collections.defaultdict(list)
    for t in templates:
        by_spec[t.get("spec_id")].append(t)
    errors = []
    for r in review:
        if not r.get("template_confirmed"):
            continue
        scope = r.get("template_confirmation_scope", "")
        spec = scope.split("spec:")[-1] if "spec:" in scope else ""
        group = by_spec.get(spec, [])
        if not group:
            errors.append("%s: template spec %r not found" % (r.get("prompt_id"), spec))
            continue
        sigs = {template_signature(t) for t in group}
        if len(sigs) != 1 or r.get("template_binding_sha256") not in sigs:
            errors.append("%s: template signature mismatch or ambiguity" % r.get("prompt_id"))
        obj_hashes = {hc(t) for t in group}
        internal_hashes = {hc({k: v for k, v in t.items() if k != "release_version"})
                           for t in group}
        if len(obj_hashes) != 1 or len(internal_hashes) != 1:
            errors.append("%s: ambiguous template objects" % r.get("prompt_id"))
            continue
        if r.get("template_object_sha256") != next(iter(obj_hashes)):
            errors.append("%s: template object hash mismatch" % r.get("prompt_id"))
        if r.get("template_internal_object_sha256") != next(iter(internal_hashes)):
            errors.append("%s: internal template object hash mismatch" % r.get("prompt_id"))
        expected_resolution = "unique" if len(group) == 1 else "duplicate_identical:%d" % len(group)
        if r.get("template_object_resolution") != expected_resolution:
            errors.append("%s: template resolution mismatch" % r.get("prompt_id"))
    return errors


def reconcile_csv(csv_path, rows, key):
    if not os.path.exists(csv_path):
        return False, "missing file %s" % csv_path
    with open(csv_path, encoding="utf-8", newline="") as f:
        got = list(_csv.DictReader(f))
    if len(got) != len(rows):
        return False, "row count %d != %d" % (len(got), len(rows))
    mismatches = []
    for a, b in zip(rows, got):
        for k, v in a.items():
            if (b.get(k) or "") != export_cell(v):
                mismatches.append({"object": a.get(key), "field": k,
                                   "csv": (b.get(k) or "")[:60],
                                   "json": export_cell(v)[:60]})
                break
        if len(mismatches) >= 5:
            break
    if mismatches:
        return False, json.dumps(mismatches, ensure_ascii=False)
    return True, "ok"


class Report(object):
    def __init__(self):
        self.results = []

    def check(self, code, title, ok, actual="", detail=""):
        self.results.append({"id": code, "check": title, "passed": bool(ok),
                             "actual": actual if isinstance(actual, str) else
                             json.dumps(actual, ensure_ascii=False)[:600],
                             "detail": detail})

    @property
    def failed(self):
        return [r for r in self.results if not r["passed"]]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate the release package (read-only)")
    ap.add_argument("--repo", required=True, help="release repository directory")
    ap.add_argument("--report-dir", default=None,
                    help="directory outside the repo for the JSON/MD report")
    args = ap.parse_args(argv)

    repo = os.path.abspath(args.repo)
    final = os.path.join(repo, "final")
    config = os.path.join(repo, "config")
    if not os.path.isdir(final) or not os.path.isdir(config):
        sys.stderr.write("release layout not found under %s (expected final/ and config/)\n"
                         % repo)
        return 2
    if args.report_dir:
        rd = os.path.abspath(args.report_dir)
        if rd == repo or rd.startswith(repo + os.sep):
            sys.stderr.write("--report-dir must be outside the repository: %s\n" % rd)
            return 2

    rep = Report()
    try:
        prompts = load_jsonl(os.path.join(final, "prompts.jsonl"))
        groups = load_jsonl(os.path.join(final, "groups.jsonl"))
        review = load_jsonl(os.path.join(final, "review_status.jsonl"))
        specs = load_json(os.path.join(config, "specs.json"))["specs"]
        profiles = load_json(os.path.join(config, "profiles.json"))["profiles"]
        templates = load_json(os.path.join(config, "templates.json"))["templates"]
        sources = load_json(os.path.join(config, "sources.json"))["sources"]
        exceptions = load_json(os.path.join(config, "known_reference_exceptions.json"))
    except (OSError, ValueError, KeyError) as exc:
        sys.stderr.write("cannot read release data: %s\n" % exc)
        return 1

    # ---------------- counting ----------------
    rep.check("V01", "group count == 1000", len(groups) == EXPECTED_GROUPS, len(groups))
    rep.check("V02", "prompt count == 2986", len(prompts) == EXPECTED_PROMPTS, len(prompts))
    rep.check("V03", "review_status rows == prompt rows",
              len(review) == len(prompts), "%d vs %d" % (len(review), len(prompts)))
    variants = collections.Counter(p.get("variant") for p in prompts)
    rep.check("V04", "variant distribution = 1000/993/993",
              dict(variants) == EXPECTED_VARIANTS, dict(variants))

    per_group = collections.defaultdict(set)
    for p in prompts:
        per_group[p.get("group_id")].add(p.get("variant"))
    triplets = sum(1 for v in per_group.values() if v == {"clean", "subtle", "strong"})
    clean_only = sum(1 for v in per_group.values() if v == {"clean"})
    other = {g: sorted(v) for g, v in per_group.items()
             if v not in ({"clean", "subtle", "strong"}, {"clean"})}
    rep.check("V05", "triplet groups == 993", triplets == EXPECTED_TRIPLETS, triplets)
    rep.check("V06", "clean-only groups == 7", clean_only == EXPECTED_CLEAN_ONLY, clean_only)
    rep.check("V07", "no other group variant set", not other, json.dumps(other)[:200])

    pids = [p.get("prompt_id") for p in prompts]
    gids = [g.get("group_id") for g in groups]
    rep.check("V08", "prompt_id unique", len(set(pids)) == len(pids),
              len(pids) - len(set(pids)))
    rep.check("V09", "group_id unique", len(set(gids)) == len(gids),
              len(gids) - len(set(gids)))

    dup_report = {
        "specs": {"records": len(specs), "unique_ids": len({s.get("spec_id") for s in specs})},
        "profiles": {"records": len(profiles),
                     "unique_ids": len({p.get("profile_id") for p in profiles})},
        "templates": {"records": len(templates),
                      "unique_ids": len({t.get("spec_id") for t in templates})},
    }
    registered = exceptions.get("duplicate_ids", {})
    reg_dupes = {(d["object_type"], d["id"]) for d in registered.get("duplicates", [])}
    found_dupes = set()
    for kind, rows, key in (("spec", specs, "spec_id"), ("profile", profiles, "profile_id"),
                            ("template", templates, "spec_id")):
        cnt = collections.Counter(r.get(key) for r in rows)
        found_dupes |= {(kind, k) for k, n in cnt.items() if n > 1}
    rep.check("V30", "duplicate ids in config are exactly the registered ones",
              found_dupes == reg_dupes and bool(found_dupes),
              {"found": sorted(found_dupes), "registered": sorted(reg_dupes)})
    rep.check("V31", "record count and unique id count are both reported",
              all(v["records"] != v["unique_ids"] for v in dup_report.values()),
              dup_report)

    # ---------------- references ----------------
    profile_ids = {p.get("profile_id") for p in profiles}
    spec_ids = {s.get("spec_id") for s in specs}
    allow_profile = set(exceptions.get("dangling_profile_ids", {}))
    allow_spec = set(exceptions.get("dangling_spec_ids", {}))
    bad_profile = sorted({p.get("profile_id") for p in prompts} - profile_ids)
    bad_spec = sorted({p.get("spec_id") for p in prompts} - spec_ids)
    rep.check("V10", "profile_id resolves or is a registered exception",
              set(bad_profile) <= allow_profile, bad_profile)
    rep.check("V11", "spec_id resolves or is a registered exception",
              set(bad_spec) <= allow_spec, bad_spec)

    impact_errors = []
    impact_by_type = {}
    affected_prompt_ids, affected_group_ids = set(), set()
    for kind, key, known, registry in (
        ("profile", "profile_id", profile_ids, exceptions.get("dangling_profile_ids", {})),
        ("spec", "spec_id", spec_ids, exceptions.get("dangling_spec_ids", {}))):
        missing = [p for p in prompts if p.get(key) not in known]
        expected_registry = {}
        for rid in sorted({p.get(key) for p in missing}):
            matches = [p for p in missing if p.get(key) == rid]
            expected_registry[rid] = {"prompt_rows": len(matches),
                                     "group_rows": len({p.get("group_id") for p in matches})}
        if registry != expected_registry:
            impact_errors.append(kind + ": id set or per-id impact mismatch")
        impact_by_type[kind] = {"prompt_rows": len(missing),
                               "group_rows": len({p.get("group_id") for p in missing})}
        affected_prompt_ids.update(p.get("prompt_id") for p in missing)
        affected_group_ids.update(p.get("group_id") for p in missing)
    if exceptions.get("affected_prompt_rows") != len(affected_prompt_ids):
        impact_errors.append("affected prompt union mismatch")
    if exceptions.get("affected_group_rows") != len(affected_group_ids):
        impact_errors.append("affected group union mismatch")
    if exceptions.get("affected_by_reference_type") != impact_by_type:
        impact_errors.append("reference-type impact mismatch")
    rep.check("V41", "dangling reference registry and deduplicated impact match data",
              not impact_errors, impact_errors or impact_by_type)

    source_ids = {s.get("source_id") for s in sources}
    referenced = set()
    for obj in prompts + groups + specs + profiles + templates:
        collect_source_ids(obj, referenced)
    missing_sources = sorted(referenced - source_ids)
    rep.check("V12", "all referenced source_ids exist",
              not missing_sources, missing_sources[:8])

    review_by_id = {r.get("prompt_id"): r for r in review}
    rep.check("V13", "review_status id set == prompt id set",
              set(review_by_id) == set(pids), len(set(review_by_id) ^ set(pids)))

    # ---------------- hashes ----------------
    bad_body, bad_visible = [], []
    for p in prompts:
        r = review_by_id.get(p.get("prompt_id"))
        if r is None:
            continue
        if r.get("prompt_sha256") != hs(p.get("prompt", "")):
            bad_body.append(p.get("prompt_id"))
        if r.get("visible_fields_sha256") != hc(p.get("expected_visible_text", {})):
            bad_visible.append(p.get("prompt_id"))
    rep.check("V14", "review prompt_sha256 matches recomputed hash",
              not bad_body, bad_body[:5])
    rep.check("V15", "review visible_fields_sha256 matches recomputed hash",
              not bad_visible, bad_visible[:5])

    # ---------------- confirmation identity ----------------
    prompt_by_id = {p.get("prompt_id"): p for p in prompts}
    prompts_by_group = collections.defaultdict(list)
    review_by_group = collections.defaultdict(list)
    identity_errors = []
    for p in prompts:
        prompts_by_group[p.get("group_id")].append(p)
    for r in review:
        p = prompt_by_id.get(r.get("prompt_id"))
        if p is None:
            continue
        if r.get("group_id") != p.get("group_id") or r.get("variant") != p.get("variant"):
            identity_errors.append("%s: review group/variant mismatch" % r.get("prompt_id"))
        if bool(r.get("body_confirmed")) != bool(p.get("body_approved")):
            identity_errors.append("%s: review body status != prompt status" % r.get("prompt_id"))
        review_by_group[p.get("group_id")].append(r)
    for gid, actual in prompts_by_group.items():
        rows = review_by_group.get(gid, [])
        if len(rows) != len(actual):
            identity_errors.append("%s: review group membership mismatch" % gid)
            continue
        if len({p.get("variant") for p in actual}) != len(actual):
            identity_errors.append("%s: repeated variant" % gid)
        body_hash = hc({p.get("variant"): hs(p.get("prompt", "")) for p in actual})
        clean = [p for p in actual if p.get("variant") == "clean"]
        clean_hash = hc(clean[0].get("expected_visible_text", {})) if len(clean) == 1 else None
        for flag in ("body_confirmed", "clean_fields_confirmed", "template_confirmed"):
            if len({bool(r.get(flag)) for r in rows}) != 1:
                identity_errors.append("%s: %s not uniform" % (gid, flag))
        for r in rows:
            confirmed_body = bool(r.get("body_confirmed"))
            expected_body = body_hash if confirmed_body else ""
            expected_clean = clean_hash if r.get("clean_fields_confirmed") else ""
            if r.get("body_group_binding_sha256", "") != expected_body:
                identity_errors.append("%s: body group hash mismatch" % r.get("prompt_id"))
            if r.get("clean_fields_binding_sha256", "") != expected_clean:
                identity_errors.append("%s: clean group hash mismatch" % r.get("prompt_id"))
            if r.get("clean_fields_confirmed") and clean_hash is None:
                identity_errors.append("%s: clean object not unique" % gid)
            if not confirmed_body:
                if r.get("confirmation_basis") != "not_in_review_scope":
                    identity_errors.append("%s: unconfirmed basis mismatch" % gid)
                if any(r.get(k) for k in ("clean_fields_confirmed", "template_confirmed",
                    "template_binding_sha256", "template_object_sha256",
                    "template_internal_object_sha256", "confirmed_at", "reconfirmed_at")):
                    identity_errors.append("%s: unconfirmed group carries confirmation" % gid)
    rep.check("V32", "confirmation identity and recomputed group hashes consistent",
              not identity_errors, identity_errors[:6])

    confirmed = [r for r in review if r.get("body_confirmed")]
    rep.check("V16", "confirmed body rows == 383",
              len(confirmed) == EXPECTED_BODY_CONFIRMED, len(confirmed))
    rep.check("V17", "unconfirmed body rows == 2603",
              len(review) - len(confirmed) == EXPECTED_UNCONFIRMED,
              len(review) - len(confirmed))
    clean_groups = {r.get("group_id") for r in review if r.get("clean_fields_confirmed")}
    rep.check("V18", "clean_fields confirmed groups == 129",
              len(clean_groups) == EXPECTED_CLEAN_GROUPS, len(clean_groups))
    tpl_groups = {r.get("group_id") for r in review if r.get("template_confirmed")}
    rep.check("V19", "template confirmed groups == 129",
              len(tpl_groups) == EXPECTED_TEMPLATE_GROUPS, len(tpl_groups))
    scopes = {r.get("template_confirmation_scope") for r in review
              if r.get("template_confirmed")}
    styles = {s.split("profile:")[1].split(" ")[0] for s in scopes if "profile:" in s}
    rep.check("V20", "template confirmation covers 54 profiles",
              len(styles) == EXPECTED_TEMPLATE_STYLES, len(styles))

    tpl_errors = template_binding_checks(review, templates)
    rep.check("V33", "template binding signature and published object hash consistent",
              not tpl_errors, tpl_errors[:6])

    # ---------------- image ----------------
    img_true = sum(1 for p in prompts if p.get("image_generated"))
    ready_true = sum(1 for p in prompts if p.get("ready_for_generation"))
    rep.check("V21", "no image_generated / ready_for_generation set",
              img_true == 0 and ready_true == 0, "image=%d ready=%d" % (img_true, ready_true))
    rep.check("V22", "all image_review_status == not_reviewed",
              all(r.get("image_review_status") == "not_reviewed" for r in review),
              collections.Counter(r.get("image_review_status")
                                  for r in review).most_common(3))

    # ---------------- hygiene ----------------
    hits = []
    for obj, label in ((prompts, "prompts"), (groups, "groups"), (specs, "specs"),
                       (profiles, "profiles"), (templates, "templates"),
                       (sources, "sources"), (exceptions, "exceptions")):
        for path, text in walk_strings(obj):
            for pat in INTERNAL_PATH_PATTERNS + SECRET_PATTERNS:
                if pat.search(text):
                    hits.append("%s%s" % (label, path))
                    break
    rep.check("V23", "no internal paths or secrets in published text",
              not hits, hits[:5])

    # ---------------- CSV reconciliation ----------------
    ok_p, msg_p = reconcile_csv(os.path.join(final, "prompts.csv"), prompts, "prompt_id")
    ok_g, msg_g = reconcile_csv(os.path.join(final, "groups.csv"), groups, "group_id")
    ok_s, msg_s = reconcile_csv(os.path.join(config, "specs.csv"), specs, "spec_id")
    ok_o, msg_o = reconcile_csv(os.path.join(config, "sources.csv"), sources, "source_id")
    rep.check("V24", "prompts.csv reconciles field by field with prompts.jsonl",
              ok_p, msg_p)
    rep.check("V25", "groups.csv reconciles field by field with groups.jsonl",
              ok_g, msg_g)
    rep.check("V26", "specs.csv reconciles field by field with specs.json", ok_s, msg_s)
    rep.check("V27", "sources.csv reconciles field by field with sources.json", ok_o, msg_o)

    rep.check("V28", "release_version present on groups and prompts",
              all(g.get("release_version") for g in groups)
              and all(p.get("release_version") for p in prompts), "")
    rep.check("V29", "known_reference_exceptions.json present with both sections",
              bool(allow_profile) and bool(allow_spec)
              and bool(registered.get("duplicates")),
              "profile=%d spec=%d duplicates=%d" % (len(allow_profile), len(allow_spec),
                                                    len(registered.get("duplicates", []))))

    # ---------------- publication boundary ----------------
    published = [s for s in sources if s.get("publication") == "index_published"]
    unpublished = [s for s in sources if s.get("publication") != "index_published"]

    rule_errors = []
    for s in published:
        urls = s.get("url") or []
        if not urls:
            rule_errors.append("%s: published without url" % s.get("source_id"))
        if not s.get("发布机构"):
            rule_errors.append("%s: published without publisher" % s.get("source_id"))
        for u in urls:
            if not official_host(host_of(u)):
                rule_errors.append("%s: non-official host %s" % (s.get("source_id"), u))
        status = s.get("核查状态", "")
        for m in PROVENANCE_BLOCK_MARKERS:
            if m in status:
                rule_errors.append("%s: status contains %r" % (s.get("source_id"), m))
        if body_access_failure(s):
            rule_errors.append("%s: recorded body retrieval failure" % s.get("source_id"))
        basis = s.get("publication_basis")
        if not isinstance(basis, str) or not all(label in basis for label in (
            "发布主体为官方机构：", "URL 主机属官方渠道：",
            "核查状态不含出处未定标记：", "原记录未载明链接无法取得正文")):
            rule_errors.append("%s: four publication conditions not recorded" % s.get("source_id"))
        if "check_status" not in s:
            rule_errors.append("%s: published without check_status" % s.get("source_id"))
    rep.check("V34", "published sources satisfy every documented condition",
              not rule_errors, rule_errors[:6])

    allowed_urls = set()
    for s in published:
        allowed_urls.update(s.get("url") or [])
    documented = exceptions.get("documented_urls", {})
    doc_urls = {d["url"] for d in documented.get("urls", [])}
    allowed_urls |= doc_urls

    # 说明性官方网址必须确有官方主机
    bad_doc = [u for u in doc_urls if not official_host(host_of(u))]
    rep.check("V40", "documented reference URLs are all on official hosts",
              not bad_doc and not documented.get("unregistered_non_official"),
              {"non_official_documented": bad_doc[:5],
               "unregistered": documented.get("unregistered_non_official", [])[:5]})

    scan_targets = []
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
        for fn in filenames:
            if fn.endswith((".py", ".pyc", ".pyo")) or fn == "SHA256SUMS.txt":
                continue
            full = os.path.join(dirpath, fn)
            scan_targets.append(os.path.relpath(full, repo).replace(os.sep, "/"))
    leaks = []
    for rel in scan_targets:
        full = os.path.join(repo, rel.replace("/", os.sep))
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for u in URL_PATTERN.findall(text):
            if u not in allowed_urls:
                leaks.append({"file": rel, "url": u})
    rep.check("V35", "no URL outside the published allowlist anywhere in the package",
              not leaks, leaks[:6])

    bad_unpub = []
    for s in unpublished:
        for path, text in walk_strings(s):
            if URL_PATTERN.search(text):
                bad_unpub.append("%s%s" % (s.get("source_id"), path))
                break
    rep.check("V36", "unpublished source records contain no URL string",
              not bad_unpub, bad_unpub[:6])

    rep.check("V37", "publication split reported",
              len(published) > 0 and len(unpublished) > 0,
              "published=%d unpublished=%d total=%d"
              % (len(published), len(unpublished), len(sources)))

    with open(os.path.join(config, "sources.csv"), encoding="utf-8", newline="") as f:
        src_csv = list(_csv.DictReader(f))
    csv_leaks = [r.get("source_id") for r in src_csv
                 if r.get("publication") != "index_published"
                 and URL_PATTERN.search(json.dumps(r, ensure_ascii=False))]
    rep.check("V38", "sources.csv leaks no URL for unpublished sources",
              not csv_leaks, csv_leaks[:6])

    art_dir = os.path.join(os.path.dirname(os.path.dirname(repo)), "artifacts")
    zip_leaks = []
    if os.path.isdir(art_dir):
        for name in sorted(os.listdir(art_dir)):
            if not name.endswith(".zip"):
                continue
            zpath = os.path.join(art_dir, name)
            try:
                with zipfile.ZipFile(zpath) as zf:
                    for entry in zf.namelist():
                        if entry.endswith((".py", "/")):
                            continue
                        data = zf.read(entry).decode("utf-8", errors="replace")
                        for u in URL_PATTERN.findall(data):
                            if u not in allowed_urls:
                                zip_leaks.append({"zip": name, "entry": entry, "url": u})
            except (OSError, zipfile.BadZipFile) as exc:
                zip_leaks.append({"zip": name, "error": str(exc)})
    rep.check("V39", "shipped ZIP leaks no URL outside the published allowlist",
              not zip_leaks, zip_leaks[:5])

    result = {
        "schema": "credential-release-validation-v3",
        "repo": repo,
        "passed": sum(1 for r in rep.results if r["passed"]),
        "failed": len(rep.failed),
        "duplicate_id_report": dup_report,
        "source_publication": {"published": len(published),
                               "unpublished": len(unpublished),
                               "total": len(sources)},
        "results": rep.results,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report_dir:
        os.makedirs(args.report_dir, exist_ok=True)
        with open(os.path.join(args.report_dir, "validation_report.json"), "w",
                  encoding="utf-8") as f:
            f.write(text)
        with open(os.path.join(args.report_dir, "validation_report.md"), "w",
                  encoding="utf-8") as f:
            f.write("# Release validation\n\n")
            f.write("%d passed / %d failed\n\n" % (result["passed"], result["failed"]))
            for r in rep.results:
                f.write("- [%s] %s %s: %s%s\n" % (
                    "PASS" if r["passed"] else "FAIL", r["id"], r["check"], r["actual"],
                    (" -> " + r["detail"]) if r["detail"] else ""))
        print("%d passed / %d failed (report written to %s)"
              % (result["passed"], result["failed"], os.path.abspath(args.report_dir)))
    else:
        sys.stdout.write(text)
    for r in rep.failed:
        sys.stderr.write("FAIL %s %s (actual=%s)\n" % (r["id"], r["check"], r["actual"]))
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
