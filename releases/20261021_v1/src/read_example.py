from pathlib import Path
import argparse
from release_engine import read_jl
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--sample-id',default='CRD-20261021-v1-00001');a=p.parse_args()
r=next(x for x in read_jl(Path(a.repo)/'data/prompts.jsonl') if x['sample_id']==a.sample_id);print(r['prompt'])
