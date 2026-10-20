# Reproducing the v2.4 research with rc2 tooling

## Two distributions
The wheel and source distribution are a lightweight installable library. They do not contain
the frozen research corpus or historical fixtures. The complete reproduction bundle
`Agentic_Crystallization_2.4_REPRODUCTION_rc2.zip` contains current source, tests, research
documents/data and the exact v1.9 ZIP required by the unchanged protected historical test.
Other historical version ZIPs remain separate release assets; they are not needed for this suite.
Every bundle member is bound by RESEARCH_SHA256SUMS.json.

Extract the complete bundle, then:
```
python -m pip install .
python scripts/verify_bundle.py
python scripts/restore_test_archive.py
python -m unittest discover -s tests -v
python scripts/research_verify.py
python scripts/reproduce.py
```
No Git credentials or Git checkout are needed for these checks.

## Git clone fixture setup
For a lightweight Git clone, obtain the original v1.9 ZIP from a complete bundle or your
original package, then run:
```
python scripts/restore_test_archive.py --source PATH_TO_ORIGINAL_ZIP
```
Windows root workflow: `./run.ps1 -Action setup -Fixture PATH_TO_ORIGINAL_ZIP`;
or `./run.ps1 -Action fixtures -Fixture PATH_TO_ORIGINAL_ZIP` after library setup.
`test` verifies the fixture before running tests. Corruption refuses overwrite; missing or
unavailable inputs explain recovery. SHA256 is checked before installing bytes.
An explicitly supplied HTTPS `--url` can fetch a published asset without credentials.
No default anonymous download is promised: this repository and release remain private.
Public asset availability is a publication gate still to execute after authorization.
`--draft` is an explicit private-CI preparation path, not required by ordinary bundle users.

## Verification and builds
`./run.ps1 -Action verify` verifies preserved research hashes and both Stage P cohorts.
`reproduce` regenerates complete holdout/replication without overwriting frozen data;
`python scripts/reproduce.py --resume` verifies existing generated output and fills only
missing cohorts. Raw CSVs must be byte-identical; JSON contents must match, allowing Windows
CRLF serialization. Generated manifests must verify their own files.
`package` builds wheel/source and the complete bundle (requires Git and the fixture).
`python scripts/check_distribution.py` installs the wheel in a fresh environment outside the
checkout with source overrides removed, extracts the bundle without credentials, verifies
its manifest and fixture, and runs the complete tests and research-integrity checks.
Original source/data identity remains in docs/provenance/ORIGINAL_PACKAGE_SHA256SUMS.json.
