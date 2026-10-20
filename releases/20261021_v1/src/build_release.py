from pathlib import Path
import argparse,json
from release_engine import build
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args()
print(json.dumps(build(Path(a.repo)),ensure_ascii=False))
