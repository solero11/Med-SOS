"""
Smoke test for the emergency registry validator.
"""
from src.utils import registry_loader


def test_registry_validates_all_topics():
    assert registry_loader.validate_all() == 0
