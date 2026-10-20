"""Unprivileged complete-bundle validation and clean installed-wheel smoke."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    wheels=list((ROOT/"dist").glob("*2.4.0rc2*.whl"))
    if len(wheels)!=1:
        raise ValueError("Build the exact rc2 wheel first")
    bundle=ROOT/"dist/Agentic_Crystallization_2.4_REPRODUCTION_rc2.zip"
    env=dict(os.environ)
    for key in ("PYTHONPATH","PYTHONHOME","GH_TOKEN","GITHUB_TOKEN"):
        env.pop(key,None)
    with tempfile.TemporaryDirectory() as td:
        scratch=Path(td)
        subprocess.run([sys.executable,"-m","venv",str(scratch/"venv")],check=True,env=env)
        python=scratch/"venv"/("Scripts/python.exe" if os.name=="nt" else "bin/python")
        def run(*args,cwd=scratch):
            subprocess.run([str(python),*args],cwd=cwd,env=env,check=True,timeout=180)
        run("-m","pip","install",str(wheels[0]))
        run("-I",str(ROOT/"scripts/installed_smoke.py"))
        extracted=scratch/"research";extracted.mkdir()
        with zipfile.ZipFile(bundle) as z:
            for item in z.infolist():
                dest=(extracted/item.filename).resolve()
                if not dest.is_relative_to(extracted.resolve()):
                    raise ValueError("Unsafe bundle path")
            z.extractall(extracted)
        run("scripts/verify_bundle.py",cwd=extracted)
        run("scripts/restore_test_archive.py",cwd=extracted)
        run("-m","unittest","discover","-s","tests","-q",cwd=extracted)
        run("scripts/research_verify.py",cwd=extracted)
    print("Clean installed wheel and unprivileged complete research bundle PASS")


if __name__=="__main__":
    main()
