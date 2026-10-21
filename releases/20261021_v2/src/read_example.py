from pathlib import Path
import argparse
from release_engine import read_jl
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--sample-id',default='CRD-20261021-v2-03010');a=p.parse_args();print(next(r['prompt'] for r in read_jl(Path(a.repo)/'data/prompts.jsonl') if r['sample_id']==a.sample_id))
