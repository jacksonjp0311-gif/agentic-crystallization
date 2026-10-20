"""Bounded review aid: inspect tracked source/data and PDF text for sensitive patterns."""
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
    "credential":re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)"),
    "personal_path":re.compile(r"(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+|/home/[^/\s]+|/Users/[^/\s]+)"),
    "email":re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
}


def main():
    names=subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0")
    findings=[];unscanned=[];allowlisted=[]
    for n in filter(None,names):
        p=ROOT/n
        if p.suffix==".pdf":
            try:
                from pypdf import PdfReader
                text="\n".join(page.extract_text() or "" for page in PdfReader(p).pages)
            except Exception:
                unscanned.append(n);continue
        elif p.suffix in (".png",".jpg",".jpeg"):
            continue
        else:
            try:text=p.read_text(encoding="utf-8")
            except UnicodeError:
                unscanned.append(n);continue
        for category,pattern in PATTERNS.items():
            if pattern.search(text):
                if n=="scripts/scan_repository.py" and category=="personal_path":
                    allowlisted.append({"path":n,"category":category,"reason":"Scanner regex literals, not an actual personal path"})
                    continue
                findings.append({"path":n,"category":category})
    result={"findings":findings,"unscanned":unscanned,"allowlisted":allowlisted,
            "limitations":"Pattern scan only; images and nested historical ZIP contents require separate review before public release."}
    print(json.dumps(result,indent=2))
    return int(bool(findings or unscanned))


if __name__=="__main__":
    raise SystemExit(main())
