from pathlib import Path
import collections,csv,hashlib,json,re

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_csv(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

manifest=json.loads((HERE/'file_manifest.json').read_text(encoding='utf-8'))
for name,expected in manifest['files_sha256'].items():
    assert digest(HERE/name)==expected, 'file hash: '+name
rules=json.loads((HERE/'seal_rules.json').read_text(encoding='utf-8'))
policies=read_csv(HERE/'seal_policy_1430.csv');bycat={r['category_entry_id']:r for r in policies}
rows=read_csv(HERE/'证件类提示词_4290条.csv')
base=read_csv(REPO/'releases/20261021_v2/data/credential_prompts_4290_unified.csv')
original={r['sample_id']:r for r in base}
assert len(rows)==4290 and len(rows[0])==12 and len({r['sample_id'] for r in rows})==4290
assert len(policies)==len(bycat)==1430
assert dict(collections.Counter(r['seal_policy'] for r in policies))==rules['category_counts']
counts=collections.Counter();groups=collections.defaultdict(list)
allowed_extra={'category_l2','category_l2_path','csv_category_l2_format','local_delivery_revision','upstream_release_version'}
for row in rows:
    source=original[row['sample_id']];meta=json.loads(row['extra_json']);old_meta=json.loads(source['extra_json'])
    cid=meta['category_entry_id'];code=bycat[cid]['seal_policy'];p=row['prompt'];counts[code]+=1
    block='\n\n【印章要求】\n'+rules['paragraphs'][code]
    assert p.count(block)==1 and p.count('【印章要求】')==1
    restored=p.replace(block,'').replace(rules['new_style_sentence'],rules['old_style_sentence'])
    assert restored==source['prompt'], 'non-seal prompt change: '+row['sample_id']
    assert hashlib.sha256(p.encode('utf-8')).hexdigest()==meta['prompt_sha256']
    for key in row:
        if key not in {'prompt','category_l2','extra_json'}:assert row[key]==source[key],(row['sample_id'],key)
    for key,val in old_meta.items():
        if key!='prompt_sha256':assert meta[key]==val,(row['sample_id'],key)
    assert set(meta)-set(old_meta)==allowed_extra
    assert meta['category_l2']==source['category_l2']
    assert row['category_l2']==meta['category_l2_path']==source['category_l2']+' / '+meta['category_name']+' / '+meta['capture_label']
    assert row['aspect_ratio']==meta['canvas_aspect_ratio']
    assert row['sample_id'] in bycat[cid]['sample_ids'].split('|')
    groups[cid].append(meta['capture_mode'])
assert dict(counts)==rules['row_counts']
assert len(groups)==1430 and all(len(m)==len(set(m))==3 for m in groups.values())
assert collections.Counter(r['aspect_ratio'] for r in rows)=={'3:2':2637,'2:3':1653}
md=(HERE/'证件类_分类与生图说明.md').read_text(encoding='utf-8')
images=re.findall(r'!\[[^\]]*\]\((images/[^)]+)\)',md)
assert len(images)==8 and all((HERE/name).is_file() for name in images)
print(json.dumps({'status':'pass','rows':4290,'categories':1430,'policy_rows':dict(counts),'images_referenced':8,'non_seal_prompt_changes':0,'image_generation_performed':False},ensure_ascii=False))
