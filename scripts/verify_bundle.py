"""Check an extracted release's own manifest without requiring Git or credentials."""
import hashlib
import json
from pathlib import Path


def verify(root):
    root=Path(root).resolve()
    manifest=json.loads((root/"RESEARCH_SHA256SUMS.json").read_text(encoding="utf-8"))
    for name, expected in manifest.items():
        path=(root/name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Missing or unsafe release entry")
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise ValueError("Release entry hash mismatch: "+name)
    return {"verified":True,"files":len(manifest)}


if __name__=="__main__":
    print(json.dumps(verify(Path(__file__).resolve().parents[1])))
