from pathlib import Path
import argparse
from release_engine import reports,read_jl
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args();r=Path(a.repo);reports(r,read_jl(r/'data/base_values_1430.jsonl'),read_jl(r/'data/prompts.jsonl'))
