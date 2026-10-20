"""Verify a self-contained release's exact file set, sizes and SHA-256 values."""
import argparse
import hashlib
import json
from pathlib import Path

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def files(repo):
    return {p.relative_to(repo).as_posix(): p for p in Path(repo).rglob('*')
            if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts
            and p.suffix != '.pyc'}

def verify(repo):
    repo=Path(repo).resolve(); actual=files(repo); problems=[]
    manifest=json.loads((repo/'release_manifest.json').read_text(encoding='utf-8'))
    entries=manifest['payload_files']; names=[e['path'] for e in entries]
    if len(names)!=len(set(names)):problems.append('Duplicate manifest path')
    expected=set(actual)-{'release_manifest.json','SHA256SUMS.txt'}
    if set(names)!=expected:problems.append('Manifest file set mismatch')
    if manifest['payload_file_count']!=len(entries):problems.append('Manifest count mismatch')
    if manifest['payload_bytes_total']!=sum(e['bytes'] for e in entries):problems.append('Manifest byte total mismatch')
    for e in entries:
        p=repo/e['path']
        if not p.resolve().is_relative_to(repo) or not p.is_file():
            problems.append('Invalid/missing path: '+e['path']);continue
        if sha(p)!=e['sha256'] or p.stat().st_size!=e['bytes']:problems.append('Manifest hash/size mismatch: '+e['path'])
    sums=[]
    for line in (repo/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        digest,rel=line.split('  ',1);sums.append(rel)
        p=repo/rel
        if not p.resolve().is_relative_to(repo) or not p.is_file() or sha(p)!=digest:problems.append('Checksum mismatch: '+rel)
    if len(sums)!=len(set(sums)) or set(sums)!=set(actual)-{'SHA256SUMS.txt'}:problems.append('Checksum file set mismatch')
    return {'passed':not problems,'payload_file_count':len(entries),'checked_file_count':len(sums),'problems':problems}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);args=ap.parse_args()
    try:report=verify(args.repo)
    except (ValueError,KeyError,OSError) as exc:report={'passed':False,'problems':[str(exc)]}
    print(json.dumps(report,ensure_ascii=False,indent=2));return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
