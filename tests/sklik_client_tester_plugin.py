"""
Provide a tested Sklik Client to tests

Tested in tests/test_sklik_client_tester_plugin.py
"""

import pytest
from tap_sklik.sklik.client import Client

from .settings import SKLIK_TEST_TOKEN


@pytest.fixture
def client():
    yield Client(SKLIK_TEST_TOKEN)
