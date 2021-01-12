"""
Test Sklik Client

The `client: Client` mock is provided by the custom tests/sklik_client_tester_plugin.py
The Client initialization is tested in tests/test_sklik_client_tester_plugin.py
"""


from tap_sklik.client import Client


def test_client_call(client: Client):
    data = client.call("client.get", [])
    assert data["status"] == 200
