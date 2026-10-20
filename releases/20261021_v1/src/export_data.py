from pathlib import Path
import argparse
from release_engine import export,read_jl
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args();r=Path(a.repo)
export(r,read_jl(r/'data/prompts.jsonl'))
