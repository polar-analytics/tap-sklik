from tap_sklik.singer.tap import discover, sync
from .settings import SKLIK_TEST_TOKEN


def test_discover():
    discover()


def test_sync():
    sync(
        {"token": SKLIK_TEST_TOKEN, "start_date": "20210112", "end_date": "20210112"},
        {},
        discover(),
    )
