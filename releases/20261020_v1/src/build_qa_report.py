"""Derive deterministic descriptive QA reports from released records (no model calls)."""
import argparse
from collections import Counter
import json
from pathlib import Path

def make_reports(repo):
    repo=Path(repo)
    rows=[json.loads(s) for s in (repo/'data/prompts.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    bases=[json.loads(s) for s in (repo/'data/clean_content_1000.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
    changes=json.loads((repo/'reports/scan_changes_980.json').read_text(encoding='utf-8'))
    sources=json.loads((repo/'config/source_index.json').read_text(encoding='utf-8'))
    q={
        'version':'credential-imaging-20261020-v1','rows':len(rows),'groups':len(bases),
        'entities':len({r['extra_json']['entity_id'] for r in rows}),'profiles':len({r['extra_json']['profile_id'] for r in rows}),
        'capture_template_views':len(json.loads((repo/'config/imaging_templates_162.json').read_text(encoding='utf-8'))['templates']),
        'category_l1':dict(sorted(Counter(r['category_l1'] for r in rows).items())),
        'category_l2_count':len({r['category_l2'] for r in rows}),
        'variants':dict(sorted(Counter(r['variant'] for r in rows).items())),
        'capture_modes':dict(sorted(Counter(r['extra_json']['capture_mode'] for r in rows).items())),
        'physical_scan_rows':sum(r['extra_json']['capture_mode']=='scan' and r['extra_json']['material_kind']!='electronic' for r in rows),
        'electronic_rows':sum(r['extra_json']['material_kind']=='electronic' for r in rows),
        'changed_rows_from_20261014_v3':changes['changed_rows'],'unchanged_rows_from_20261014_v3':len(rows)-changes['changed_rows'],
        'manual_body_approved':sum(r['manual_body_approved'] for r in rows),
        'image_generated':sum(r['image_generated'] for r in rows),'image_accepted':sum(r['image_accepted'] for r in rows),
        'source_ids_used':len({s for r in rows for s in r['extra_json']['source_ids']}),
        'source_registry_records':len(sources['sources']),'unresolved_source_ids':sources['unresolved_source_ids'],
        'source_urls_rechecked_on_release':False,
        'scope':'Programmatic data checks are separate from human approval, source provenance, image generation, OCR and image acceptance.',
        'scan_change_evidence':'Historical v3 prompt hashes are recorded; this public package does not contain all v3 prompt bodies and cannot independently re-run the full v3 comparison.'
    }
    text='# 新版数据统计与检查范围\n\n本表由公开数据确定性生成；实际程序校验通过与否见命令输出及 GitHub Actions。\n\n| 项目 | 数量 |\n| --- | ---: |\n'
    for label,key in [('提示词','rows'),('基础组','groups'),('对象','entities'),('版式','profiles'),('成像模板视图','capture_template_views'),('实体扫描件','physical_scan_rows'),('电子页面相关提示词','electronic_rows'),('相对 v3 记录的正文修改','changed_rows_from_20261014_v3'),('相对 v3 记录的正文不变','unchanged_rows_from_20261014_v3'),('新版正文人工确认','manual_body_approved'),('本版图片生成','image_generated'),('本版图片验收','image_accepted'),('使用的来源 ID','source_ids_used')]:text+=f"| {label} | {q[key]} |\n"
    text+='\n全部 variant 为 clean。基础组来源正文的历史确认不转为新版正文确认。来源元数据继承旧公开版，本次未重访来源网页；程序通过不表示版式、编号算法或来源均经专业确认。\n\n980 条变更以继承的编号和前后哈希清单记录；公开包未包含全部 v3 正文，完整的 v3 前后比较属于内部历史验收范围。本版不包含图片、OCR 结果或模型效果评测。\n'
    return q,text

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    repo=Path(a.repo).resolve();out=Path(a.out).resolve()
    if out==repo or out.is_relative_to(repo):raise ValueError('Output must be outside release directory')
    out.mkdir(parents=True,exist_ok=False);q,text=make_reports(repo)
    (out/'qa_report.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'qa_report.md').write_text(text,encoding='utf-8',newline='\n')
    print(json.dumps({'rows':q['rows'],'out_created':True}))

if __name__=='__main__':main()
