from pathlib import Path
import argparse,json
from release_engine import validate
p=argparse.ArgumentParser();p.add_argument('--repo',default=str(Path(__file__).resolve().parents[1]));p.add_argument('--report-dir');p.add_argument('--rebuild',action='store_true');a=p.parse_args();print(json.dumps(validate(Path(a.repo),a.report_dir,a.rebuild),ensure_ascii=False))
