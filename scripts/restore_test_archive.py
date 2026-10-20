"""Verify or explicitly restore the exact historical test fixture.

No archive is extracted. The original manifest digest is the acceptance gate.
"""
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import urllib.error
import argparse

ROOT=Path(__file__).resolve().parents[1]
NAME="docs/archive/Agentic_Crystallization_1.9_VERIFIED.zip"
RELEASE_API="https://api.github.com/repos/jacksonjp0311-gif/agentic-crystallization/releases/418588443/assets"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def restore(root=ROOT, *, source=None, url=None, draft=False):
    expected=json.loads((root/"docs/provenance/ORIGINAL_PACKAGE_SHA256SUMS.json").read_text())["files"][NAME]
    target=root/NAME
    if target.exists():
        if target.stat().st_size > 20_000_000 or hashlib.sha256(target.read_bytes()).hexdigest()!=expected:
            raise ValueError("Existing historical archive differs; refusing overwrite")
        print("Historical fixture SHA256 verified")
        return
    if source is not None:
        source=Path(source)
        if not source.is_file() or source.stat().st_size > 20_000_000:
            raise ValueError("Fixture source unavailable or oversized; use the exact original v1.9 ZIP.")
        data=source.read_bytes()
    elif url is not None:
        if not url.startswith("https://"):
            raise ValueError("Fixture URL must use HTTPS.")
        # Public recovery path intentionally sends no credentials.
        try:
            with urllib.request.urlopen(url,timeout=30) as response:
                data=response.read(20_000_001)
        except OSError as exc:
            raise ValueError("Fixture download unavailable. Use --source with the original ZIP or the complete research bundle.") from exc
    elif draft:
        data=_draft_download()
    else:
        raise ValueError("Historical fixture missing. Use the complete research bundle, or run scripts/restore_test_archive.py --source PATH_TO_ORIGINAL_ZIP. Public asset availability is not yet verified.")
    if len(data)>20_000_000 or hashlib.sha256(data).hexdigest()!=expected:
        raise ValueError("Historical archive hash/size mismatch; original fixture required.")
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("xb") as f:
        f.write(data)
    print("Historical fixture restored and SHA256 verified")


def _draft_download():
    token=os.environ.get("GH_TOKEN")
    if not token:
        raise RuntimeError("Historical fixture missing. Supply GH_TOKEN with draft-release access or restore the original ZIP manually.")
    headers={"Authorization":"Bearer "+token,"User-Agent":"agentic-crystallization-research","Accept":"application/vnd.github+json"}
    with urllib.request.urlopen(urllib.request.Request(RELEASE_API,headers=headers),timeout=30) as response:
        assets=json.load(response)
    match=[a for a in assets if a["name"]==Path(NAME).name]
    if len(match)!=1:
        raise ValueError("Required historical release asset missing or ambiguous")
    url=match[0]["url"]
    if not url.startswith("https://api.github.com/repos/jacksonjp0311-gif/agentic-crystallization/releases/assets/"):
        raise ValueError("Unexpected asset endpoint")
    headers["Accept"]="application/octet-stream"
    req=urllib.request.Request(url,headers=headers)
    try:
        response=urllib.request.build_opener(NoRedirect).open(req,timeout=60)
    except urllib.error.HTTPError as exc:
        if exc.code!=302:
            raise
        destination=exc.headers["Location"]
        if not destination.startswith("https://"):
            raise ValueError("Insecure asset redirect")
        # Do not send repository credentials to the signed download host.
        response=urllib.request.urlopen(destination,timeout=60)
    with response:
        data=response.read(20_000_001)
    return data


def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group()
    group.add_argument("--source",type=Path)
    group.add_argument("--url")
    group.add_argument("--draft",action="store_true",help="Private CI preparation only; requires draft access")
    args=parser.parse_args()
    try:
        restore(source=args.source,url=args.url,draft=args.draft)
    except (ValueError,RuntimeError,OSError) as exc:
        parser.exit(1,str(exc)+"\n")


if __name__=="__main__":
    main()
