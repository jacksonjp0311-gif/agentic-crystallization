"""Final code/experiment integrity and independent-replay regression gates."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_stage_l import verify

class StageLSealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.final=ROOT/'experiments/stage_l_holdout'
        cls.replay=ROOT/'experiments/stage_l_independent_replay'

    def test_final_seed_contract_and_source_sha(self):
        prereg=json.loads((ROOT/'docs/PREREGISTRATION_STAGE_L.json').read_text())
        protocol=json.loads((self.final/'protocol.json').read_text())
        self.assertEqual(protocol['seed_first'],80000)
        self.assertEqual(protocol['seed_count'],40)
        self.assertEqual(protocol['code_sha256'],prereg['code_sha256'])
        self.assertTrue(verify(self.final,ROOT)['verified'])

    def test_byte_exact_independent_reproduction(self):
        self.assertTrue(verify(self.replay,ROOT)['verified'])
        for name in ['runs.csv','summary.json','protocol.json','SHA256SUMS.json']:
            self.assertEqual((self.final/name).read_bytes(),(self.replay/name).read_bytes(),name)

    def test_modified_data_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            copy=Path(temp)/'cohort';shutil.copytree(self.final,copy)
            src=copy/'runs.csv';data=src.read_bytes();src.write_bytes(data+b'altered\n')
            with self.assertRaises(ValueError):verify(copy,ROOT)

    def test_negative_controls_present_and_not_omitted(self):
        s=json.loads((self.final/'summary.json').read_text())
        bad=s['false_shift']['crystal']
        self.assertEqual(bad['false_certifications'],bad['certified'])
        self.assertGreater(bad['certified'],400)
        self.assertEqual(s['unknown_shift']['crystal']['certified'],0)
        self.assertEqual(s['unknown_shift']['crystal']['total_queries'],0)
        self.assertEqual(s['noise']['crystal']['false_certifications'],0)

    def test_historical_verified_zip_exists(self):
        f=ROOT/'docs/archive/Agentic_Crystallization_1.9_VERIFIED.zip'
        self.assertTrue(f.is_file())
        self.assertGreater(f.stat().st_size,1000000)

if __name__=='__main__':unittest.main()
