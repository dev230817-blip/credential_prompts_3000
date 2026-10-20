from pathlib import Path
import argparse,json
from release_engine import verify_hashes
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));a=p.parse_args()
print(json.dumps(verify_hashes(Path(a.repo)),ensure_ascii=False))
