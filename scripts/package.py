"""Package tracked research files with byte hashes; nested history is a separate asset."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    names=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    names=[n for n in names if n and not n.endswith(".zip")]
    if not names:
        raise ValueError("Stage reviewed repository files before packaging")
    out=ROOT/"dist"
    out.mkdir(exist_ok=True)
    destination=out/"Agentic_Crystallization_2.4_RESEARCH_PREVIEW.zip"
    hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as z:
        for n in names:
            info=zipfile.ZipInfo(n,date_time=(2026,10,20,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(ROOT/n).read_bytes())
        z.writestr("RESEARCH_SHA256SUMS.json",json.dumps(hashes,sort_keys=True,indent=2))
    print(destination.name,hashlib.sha256(destination.read_bytes()).hexdigest())


if __name__=="__main__":
    main()
