"""Regression probes must reject corrupted data even after hashes are resealed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/'src'))
from validate_release import validate
from export_data import export
from verify_hashes import verify,files,sha
from build_qa_report import make_reports

def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def reseal(repo):
    actual=files(repo)
    entries=[{'path':r,'bytes':p.stat().st_size,'sha256':sha(p)} for r,p in sorted(actual.items()) if r not in {'release_manifest.json','SHA256SUMS.txt'}]
    write(repo/'release_manifest.json',{'payload_files':entries,'payload_file_count':len(entries),'payload_bytes_total':sum(e['bytes'] for e in entries)})
    actual=files(repo)
    (repo/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+r+'\n' for r,p in sorted(actual.items()) if r!='SHA256SUMS.txt'),encoding='utf-8')

class ReleaseChecks(unittest.TestCase):
    def probe(self,mutate,check):
        with tempfile.TemporaryDirectory(prefix='imaging_regression_') as temp:
            repo=Path(temp)/'repo';shutil.copytree(REPO,repo,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            mutate(repo);reseal(repo);self.assertTrue(verify(repo)['passed'])
            report=validate(repo)
            self.assertFalse(report['passed']);self.assertIn(check,[r['id'] for r in report['results'] if not r['passed']])
    def row_change(self,fn):
        def mutate(repo):
            p=repo/'data/prompts.jsonl';rows=[json.loads(s) for s in p.read_text(encoding='utf-8').splitlines()]
            fn(rows[0]);p.write_text(''.join(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n' for r in rows),encoding='utf-8')
        return mutate
    def test_body_modified_with_recomputed_hash(self):
        def alter(r):r['prompt']=r['prompt'].replace('彩色平板扫描仪','手机相机',1);r['prompt_sha256']=hashlib.sha256(r['prompt'].encode()).hexdigest()
        self.probe(self.row_change(alter),'V10')
    def test_approval_cannot_be_inherited(self):
        self.probe(self.row_change(lambda r:r.update(manual_body_approved=True)),'V15')
    def test_missing_review_row(self):
        def mutate(repo):
            p=repo/'reports/review_status.jsonl';p.write_text('\n'.join(p.read_text(encoding='utf-8').splitlines()[1:])+'\n',encoding='utf-8')
        self.probe(mutate,'V15')
    def test_wrong_visible_value(self):
        self.probe(self.row_change(lambda r:r['expected_visible_text'].update({'签发机关':'Changed value'})),'V08')
    def test_image_acceptance_not_invented(self):
        self.probe(self.row_change(lambda r:r.update(image_accepted=True)),'V16')
    def test_unresolved_source(self):
        self.probe(self.row_change(lambda r:r['extra_json']['source_ids'].append('UNKNOWN')),'V17')
    def test_qa_counts_not_trusted(self):
        def mutate(repo):
            p=repo/'reports/qa_report.json';q=json.loads(p.read_text(encoding='utf-8'));q['rows']=999;write(p,q)
        self.probe(mutate,'V19')
    def test_private_path_rejected(self):
        def mutate(repo):
            p=repo/'config/source_index.json';q=json.loads(p.read_text(encoding='utf-8'));q['note']='C:/Users/private/example';write(p,q)
        self.probe(mutate,'V20')
    def test_exports_refuse_overwrite_and_inside_release(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileExistsError):export(REPO,Path(temp))
        with self.assertRaises(ValueError):export(REPO,REPO/'new-export')
    def test_qa_reproducible(self):
        self.assertEqual(make_reports(REPO),make_reports(REPO))
    def test_hashes_detect_extra_file(self):
        with tempfile.TemporaryDirectory() as temp:
            repo=Path(temp)/'repo';shutil.copytree(REPO,repo,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            (repo/'extra.txt').write_text('unexpected',encoding='utf-8');self.assertFalse(verify(repo)['passed'])

if __name__=='__main__':unittest.main()
