"""Record or verify source/method hashes before descriptive comparisons."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];target=ROOT/"PLAN_FREEZE.json"
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def run(write=False):
    if write:
        assert not target.exists(),"freeze already exists"
        methods=["analyze.py","guard.py","exercise.py","check_source.py","check_analysis.py","freeze.py","replay.py"]
        paths=[ROOT/"src"/s for s in methods]+list((ROOT/"data").glob("*.json"))+list((ROOT/"tests").glob("*.py"))
        paths+=[ROOT/n for n in ["PROTOCOL.md","CODEBOOK.md","DATA_RIGHTS.md","requirements.txt"]]
        items={str(f.relative_to(ROOT)).replace("\\","/"):digest(f) for f in sorted(paths)}
        value=dict(source_checkpoint=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                   qualification="Source-informed; dates already visible during source review. Committed before first comparison command, not blinded.",
                   dependencies=items)
        target.write_bytes((json.dumps(value,indent=2,sort_keys=True)+"\n").encode())
    value=json.loads(target.read_bytes())
    for name,sha in value["dependencies"].items():assert digest(ROOT/name)==sha,("changed frozen dependency",name)
    print(json.dumps(dict(status="PASS",dependencies=len(value["dependencies"]),freeze_sha256=digest(target),source_checkpoint=value["source_checkpoint"])))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--write",action="store_true");run(p.parse_args().write)
