"""Restore the original historical test fixture from a private release asset.

No archive is extracted. The original manifest digest is the acceptance gate.
"""
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parents[1]
NAME="docs/archive/Agentic_Crystallization_1.9_VERIFIED.zip"
RELEASE_API="https://api.github.com/repos/jacksonjp0311-gif/agentic-crystallization/releases/418588443/assets"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def main():
    expected=json.loads((ROOT/"docs/provenance/ORIGINAL_PACKAGE_SHA256SUMS.json").read_text())["files"][NAME]
    target=ROOT/NAME
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest()!=expected:
            raise ValueError("Existing historical archive differs; refusing overwrite")
        print("Historical fixture SHA256 verified")
        return
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
    if len(data)>20_000_000 or hashlib.sha256(data).hexdigest()!=expected:
        raise ValueError("Historical archive hash/size mismatch")
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("xb") as f:
        f.write(data)
    print("Historical fixture restored and SHA256 verified")


if __name__=="__main__":
    main()
