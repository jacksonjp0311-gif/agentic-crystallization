"""Ensure both final and historical archived Stage K snapshots are auditable."""
from pathlib import Path
import shutil
import tempfile
import unittest
from scripts.verify_stage_k import verify

ROOT=Path(__file__).resolve().parents[1]


class StageKVerifierTests(unittest.TestCase):
    def test_final_frozen_holdout(self):
        result=verify(ROOT/'experiments/stage_k_holdout',ROOT,expect_worlds=400)
        self.assertTrue(result['verified'])
        self.assertEqual(result['rows'],2800)
        self.assertEqual(result['source_snapshot'],'final')

    def test_archived_preseal_cohort(self):
        result=verify(ROOT/'experiments/stage_k_exploratory_observed',ROOT,
                      expect_worlds=400,preseal=True)
        self.assertEqual(result['source_snapshot'],'preseal')

    def test_detect_corrupted_output_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            src=ROOT/'experiments/stage_k_holdout'
            dst=Path(d)/'corrupt'
            dst.mkdir()
            for f in src.iterdir():
                if f.is_file():shutil.copyfile(f,dst/f.name)
            with (dst/'runs.csv').open('a',encoding='utf-8') as f:
                f.write('\ncorrupted')
            with self.assertRaises(ValueError):verify(dst,ROOT)


if __name__=='__main__':unittest.main()
