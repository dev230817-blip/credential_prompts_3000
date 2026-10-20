from pathlib import Path
import argparse
from release_engine import read_jl,write_reports
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args();r=Path(a.repo)
write_reports(r,read_jl(r/'data/base_content_1430.jsonl'),read_jl(r/'data/prompts.jsonl'))
