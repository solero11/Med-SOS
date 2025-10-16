"""
Test harness for Protocol Ingestion Module
"""
import os
import unittest
import tempfile
from src.protocols.ingest import ProtocolIngestor

class TestProtocolIngestor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.library_dir = os.path.join(self.temp_dir.name, "library")
        self.index_path = os.path.join(self.temp_dir.name, "index.yaml")
        self.ingestor = ProtocolIngestor(self.library_dir, self.index_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_get_protocol(self):
        protocol_name = "test_protocol"
        protocol_data = {"title": "Test Protocol", "steps": ["Step 1", "Step 2"]}
        self.ingestor.save_protocol(protocol_name, protocol_data)
        loaded = self.ingestor.get_protocol(protocol_name)
        self.assertEqual(loaded["title"], "Test Protocol")
        self.assertEqual(loaded["steps"], ["Step 1", "Step 2"])

    def test_missing_protocol(self):
        with self.assertRaises(FileNotFoundError):
            self.ingestor.get_protocol("nonexistent_protocol")

if __name__ == "__main__":
    unittest.main()
