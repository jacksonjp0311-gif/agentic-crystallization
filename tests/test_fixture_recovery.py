from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest
from unittest.mock import patch
from scripts.restore_test_archive import restore, ROOT, NAME


class FixtureRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        p=self.root/"docs/provenance";p.mkdir(parents=True)
        shutil.copyfile(ROOT/"docs/provenance/ORIGINAL_PACKAGE_SHA256SUMS.json",p/"ORIGINAL_PACKAGE_SHA256SUMS.json")

    def test_missing_has_actionable_error_and_no_network(self):
        with patch("urllib.request.urlopen",side_effect=AssertionError("network")):
            with self.assertRaisesRegex(ValueError,"--source"):
                restore(self.root)

    def test_local_unprivileged_recovery(self):
        with patch.dict("os.environ",{},clear=True), patch("urllib.request.urlopen",side_effect=AssertionError("network")):
            restore(self.root,source=ROOT/NAME)
            restore(self.root)
        self.assertEqual((self.root/NAME).read_bytes(),(ROOT/NAME).read_bytes())

    def test_corrupted_refused_without_overwrite(self):
        p=self.root/NAME;p.parent.mkdir(parents=True);p.write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError,"refusing overwrite"):
            restore(self.root,source=ROOT/NAME)
        self.assertEqual(p.read_bytes(),b"corrupt")

    def test_bad_source_not_installed(self):
        p=self.root/"bad.zip";p.write_bytes(b"bad")
        with self.assertRaisesRegex(ValueError,"hash/size"):
            restore(self.root,source=p)
        self.assertFalse((self.root/NAME).exists())

    def test_unavailable_public_asset_actionable(self):
        with patch("urllib.request.urlopen",side_effect=OSError("unavailable")):
            with self.assertRaisesRegex(ValueError,"download unavailable"):
                restore(self.root,url="https://example.invalid/fixture.zip")
