"""
Test harness for SBAR Builder Utility
"""
import unittest
from src.utils.sbar_builder import SBAR

class TestSBAR(unittest.TestCase):
    def test_empty_sbar(self):
        sbar = SBAR()
        self.assertFalse(sbar.is_complete())
        self.assertEqual(set(sbar.missing_fields()), {"situation", "background", "assessment", "recommendation"})

    def test_partial_sbar(self):
        sbar = SBAR(situation="Low O2", background="Recent surgery")
        self.assertFalse(sbar.is_complete())
        self.assertIn("assessment", sbar.missing_fields())
        self.assertIn("recommendation", sbar.missing_fields())

    def test_complete_sbar(self):
        sbar = SBAR(
            situation="Hypotension after central line",
            background="45M, appendectomy, no lung disease",
            assessment="Possible tension pneumothorax",
            recommendation="Needle decompression, chest tube"
        )
        self.assertTrue(sbar.is_complete())
        self.assertEqual(sbar.missing_fields(), [])
        self.assertEqual(sbar.to_dict()["situation"], "Hypotension after central line")

if __name__ == "__main__":
    unittest.main()
