"""Print a few current imaging-release records without generating images."""
import argparse
import json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--limit',type=int,default=3);ap.add_argument('--full',action='store_true');a=ap.parse_args()
    if a.limit<1:ap.error('--limit must be positive')
    with (Path(a.repo)/'data/prompts.jsonl').open(encoding='utf-8') as f:
        for i,line in enumerate(f):
            if i>=a.limit:break
            r=json.loads(line);m=r['extra_json']
            print(r['sample_id'],r['category_l2'],m['capture_label'])
            print(r['prompt'] if a.full else r['prompt'][:200])

if __name__=='__main__':main()
