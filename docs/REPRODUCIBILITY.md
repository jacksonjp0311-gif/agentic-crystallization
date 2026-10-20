# Reproducibility

Use Python 3.10+ with NumPy. `run.ps1 -Action setup` creates `.venv`.
`test` runs every historical and API regression. `verify` checks preserved source/data hashes
and reconciles both Stage P cohorts. `reproduce` regenerates both complete cohorts into
`work/reproduction` and compares raw CSV bytes and parsed JSON summaries/protocols, refusing overwrite.
Windows JSON newline encoding differs from the historical LF serialization; generated
hash manifests are verified against generated files. `python scripts/reproduce.py --resume`
verifies existing output and generates missing cohorts without overwriting.
`demo` writes a separate single-seed synthetic trial. `package` builds a wheel and source
distribution and a repository ZIP with a checksum manifest. `status` shows Git state.

For portable operation: `python -m pip install .`, `python -m unittest discover -s tests -v`,
`python scripts/research_verify.py`, `python scripts/reproduce.py`.
Use `python -m agentic_crystallization.stage_p --out work/demo --count 1 --max-age 4 --no-cue`
for a standalone demo. Never rerun into frozen experiment directories.

Original package inventory is `docs/provenance/ORIGINAL_PACKAGE_SHA256SUMS.json`.
Original README and entry point are preserved there too. Git omits nested ZIP archives;
their digests stay in the provenance manifest and their bytes remain in the recovery package.
The exact original package verifier remains available for extracted original archives.
