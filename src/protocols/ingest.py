"""
Protocol Ingestion Module

Handles ingestion of clinical protocols from PDFs, web pages, or LLM prompts and stores them as structured YAML files. Also updates the protocol index for fast lookup.
"""

import os
import yaml
from typing import Dict, Any

class ProtocolIngestor:
    def __init__(self, library_dir: str, index_path: str):
        self.library_dir = library_dir
        self.index_path = index_path
        if not os.path.exists(library_dir):
            os.makedirs(library_dir)
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                yaml.dump({}, f)

    def save_protocol(self, protocol_name: str, protocol_data: Dict[str, Any]):
        yaml_path = os.path.join(self.library_dir, f"{protocol_name}.yaml")
        with open(yaml_path, 'w') as f:
            yaml.dump(protocol_data, f)
        self._update_index(protocol_name, yaml_path)

    def _update_index(self, protocol_name: str, yaml_path: str):
        with open(self.index_path, 'r') as f:
            index = yaml.safe_load(f) or {}
        index[protocol_name] = yaml_path
        with open(self.index_path, 'w') as f:
            yaml.dump(index, f)

    def get_protocol(self, protocol_name: str) -> Dict[str, Any]:
        with open(self.index_path, 'r') as f:
            index = yaml.safe_load(f) or {}
        yaml_path = index.get(protocol_name)
        if not yaml_path or not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Protocol '{protocol_name}' not found.")
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
