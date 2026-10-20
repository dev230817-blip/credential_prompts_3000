"""Regression checks for public report/document corruption, after valid resealing."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]

def run_tool(repo, name, *args):
    return subprocess.run([sys.executable, '-B', '-X', 'utf8', str(repo / 'src' / name),
                           '--repo', str(repo), *map(str, args)], capture_output=True, timeout=60)

def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

def reseal(repo):
    """Recompute the manifest so content checks, rather than stale hashes, must fail."""
    names = sorted(p.relative_to(repo).as_posix() for p in repo.rglob('*')
                   if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts)
    manifest = json.loads((repo / 'release_manifest.json').read_text(encoding='utf-8'))
    entries = [{'path': name, 'bytes': (repo / name).stat().st_size,
                'sha256': hashlib.sha256((repo / name).read_bytes()).hexdigest()}
               for name in names if name not in ('SHA256SUMS.txt', 'release_manifest.json')]
    manifest.update(payload_files=entries, payload_file_count=len(entries),
                    payload_bytes_total=sum(e['bytes'] for e in entries))
    write_json(repo / 'release_manifest.json', manifest)
    (repo / 'SHA256SUMS.txt').write_text(''.join(
        hashlib.sha256((repo / name).read_bytes()).hexdigest() + '  ' + name + '\n'
        for name in names if name != 'SHA256SUMS.txt'), encoding='utf-8', newline='\n')

class ReleaseConsistency(unittest.TestCase):
    def assert_mutation(self, mutate, target):
        with tempfile.TemporaryDirectory(prefix='credential_regression_') as temp:
            repo = Path(temp) / 'repo'
            shutil.copytree(REPO, repo, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
            mutate(repo)
            reseal(repo)
            hashes = run_tool(repo, 'verify_hashes.py')
            self.assertEqual(hashes.returncode, 0, hashes.stderr.decode('utf-8', errors='replace'))
            result = run_tool(repo, 'validate_release.py')
            self.assertEqual(result.returncode, 1, result.stderr.decode('utf-8', errors='replace'))
            report = json.loads(result.stdout)
            self.assertIn(target, [r['id'] for r in report['results'] if not r['passed']])

    def alter_qa(self, field, value):
        def mutate(repo):
            path = repo / 'final/qa_report.json'
            report = json.loads(path.read_text(encoding='utf-8'))
            report['sources_publication'][field] = value
            write_json(path, report)
        return mutate

    def test_exclusive_source_categories(self):
        self.assert_mutation(self.alter_qa('identifier_only', 102), 'V42')

    def test_unpublished_total(self):
        self.assert_mutation(self.alter_qa('unpublished_total', 101), 'V42')

    def test_qa_data_hash(self):
        def mutate(repo):
            path = repo / 'final/qa_report.json'
            report = json.loads(path.read_text(encoding='utf-8'))
            report['measured_file_hashes']['final/prompts.jsonl'] = '0' * 64
            write_json(path, report)
        self.assert_mutation(mutate, 'V43')

    def test_current_version_documentation(self):
        def mutate(repo):
            path = repo / 'docs/data_fields.md'
            path.write_text(path.read_text(encoding='utf-8').replace(
                '当前为 `codex-20261011-feedback-v4`', '当前为 `wrong-version`'), encoding='utf-8', newline='\n')
        self.assert_mutation(mutate, 'V44')

    def test_current_review_scope(self):
        def mutate(repo):
            path = repo / 'docs/review_scope.md'
            path.write_text(path.read_text(encoding='utf-8').replace(
                '| `legacy_inherited_rows` | `27` |', '| `legacy_inherited_rows` | `72` |'), encoding='utf-8', newline='\n')
        self.assert_mutation(mutate, 'V44')

    def test_qa_markdown_corruption(self):
        def mutate(repo):
            path = repo / 'final/qa_report.md'
            path.write_bytes(path.read_bytes().replace(b'| Source records | 222 |', b'| Source records | 223 |'))
        self.assert_mutation(mutate, 'V45')

    def test_generator_determinism_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='credential_qa_rebuild_') as temp:
            first, second = Path(temp) / 'one', Path(temp) / 'two'
            for output in (first, second):
                result = run_tool(REPO, 'build_qa_report.py', '--out', output)
                self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
            for name in ('qa_report.json', 'qa_report.md'):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
                self.assertEqual((first / name).read_bytes(), (REPO / 'final' / name).read_bytes())
            before = {p.name: p.read_bytes() for p in first.iterdir()}
            result = run_tool(REPO, 'build_qa_report.py', '--out', first)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(before, {p.name: p.read_bytes() for p in first.iterdir()})

    def test_normal_release_and_historical_scopes(self):
        result = run_tool(REPO, 'validate_release.py')
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', errors='replace'))
        self.assertEqual(json.loads(result.stdout)['failed'], 0)

    def test_changed_body_invalidates_confirmation(self):
        def mutate(repo):
            path = repo / 'final/prompts.jsonl'
            rows = [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]
            rows[0]['prompt'] += ' altered body'
            path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows), encoding='utf-8')
        self.assert_mutation(mutate, 'V14')

    def test_missing_confirmation_record(self):
        def mutate(repo):
            path = repo / 'final/review_status.jsonl'
            rows = path.read_text(encoding='utf-8').splitlines()
            path.write_text('\n'.join(rows[1:]) + '\n', encoding='utf-8')
        self.assert_mutation(mutate, 'V03')

    def test_csv_body_disagreement(self):
        def mutate(repo):
            import csv
            path = repo / 'final/prompts.csv'
            with path.open(encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f); fields = reader.fieldnames; rows = list(reader)
            rows[0]['prompt'] += ' altered export'
            with path.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
        self.assert_mutation(mutate, 'V24')

    def test_active_template_disagreement(self):
        def mutate(repo):
            path = repo / 'config/active_templates.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            data['templates'][0]['shared_prompt_sections']['layout'] += ' changed layout'
            write_json(path, data)
        self.assert_mutation(mutate, 'V46')

    def test_coverage_counts(self):
        def mutate(repo):
            path = repo / 'config/reference_coverage.json'
            data = json.loads(path.read_text(encoding='utf-8')); data['counts']['partial'] = 23
            write_json(path, data)
        self.assert_mutation(mutate, 'V48')

    def test_private_metadata_path(self):
        def mutate(repo):
            path = repo / 'config/reference_coverage.json'
            data = json.loads(path.read_text(encoding='utf-8')); data['note'] = 'C:/Users/private/original.png'
            write_json(path, data)
        self.assert_mutation(mutate, 'V49')

    def test_wrong_confirmation_basis(self):
        def mutate(repo):
            path = repo / 'final/review_status.jsonl'
            rows = [json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()]
            rows[0]['confirmation_basis'] = 'machine_check_only'
            path.write_text(''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows), encoding='utf-8')
        self.assert_mutation(mutate, 'V47')

if __name__ == '__main__':
    unittest.main()
