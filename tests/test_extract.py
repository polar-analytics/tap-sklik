from sklik_el.client import Client
from sklik_el.extract import extract


def test_extract(client: Client):
    extract(client)
