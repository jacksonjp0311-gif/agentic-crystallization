import tempfile
import unittest
from pathlib import Path
from scripts.verify_experiment import verify
from agentic_crystallization.stage_j import run

class StageJIntegrityTests(unittest.TestCase):
    def test_verified_frozen_run(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'trial';run(out,seeds=range(8300,8302),stage='development')
            self.assertEqual(verify(out)['condition_rows'],36)

    def test_tampered_raw_output_refused(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'trial';run(out,seeds=range(8300,8302),stage='development')
            with (out/'runs.csv').open('a') as f:f.write('forged row\n')
            with self.assertRaises(ValueError):verify(out)

    def test_no_duplicate_seed_row_contract(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'trial';run(out,seeds=range(8300,8302),stage='development')
            self.assertTrue((out/'protocol.json').is_file())
            self.assertEqual(verify(out)['world_parameters'],2)

if __name__=='__main__':unittest.main()
