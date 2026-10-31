"""Reproduce saved-data outputs in a separate folder and verify frozen inputs."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def call(script,*args):
    subprocess.run([sys.executable,str(ROOT/"src"/script),*map(str,args)],cwd=ROOT,check=True)
def run(out,analysis_only=False):
    out=out.resolve();assert out!=ROOT/"results" and not out.exists(),"use a new separate output directory"
    call("freeze.py");call("check_source.py")
    before={str(f.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/"data").glob("*.json")}
    call("analyze.py","--out",out)
    # The exercise reads committed case classifications; those are independently checked below.
    call("exercise.py","--out",out)
    names=["cases.json","planned_references.json","summary.json","exercise.json"]
    for name in names:assert (out/name).read_bytes()==(ROOT/"results"/name).read_bytes(),("replay mismatch",name)
    call("check_analysis.py")
    subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,check=True)
    if not analysis_only:
        call("check_figures.py");call("check_paper.py")
    after={str(f.relative_to(ROOT)).replace("\\","/"):hashlib.sha256(f.read_bytes()).hexdigest() for f in (ROOT/"data").glob("*.json")}
    assert before==after,"source projections changed"
    (out/"REPLAY_RECEIPT.json").write_bytes((json.dumps(dict(status="PASS",python=sys.version.split()[0],
          reproduced_files=names,unchanged_source_files=len(before),native_redownload=False,
          scope="Saved factual projection replay; native sources and semantic adjudication were checked separately."),indent=2)+"\n").encode())
    print("PASS SAVED_DATA_REPLAY",sys.version.split()[0],len(names),len(before))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);p.add_argument("--analysis-only",action="store_true");a=p.parse_args();run(a.out,a.analysis_only)
