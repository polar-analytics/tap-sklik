from datetime import datetime
from tap_sklik.singer.tap import discover, sync
from .settings import SKLIK_TEST_TOKEN


def test_discover():
    discover()


def test_sync():
    some_date = datetime(2018, 1, 1).strftime("%Y%m%d")
    sync(
        {"token": SKLIK_TEST_TOKEN, "start_date": some_date, "end_date": some_date},
        {},
        discover(),
    )


def test_sync_today():
    today = datetime.now().strftime("%Y%m%d")
    sync(
        {"token": SKLIK_TEST_TOKEN, "start_date": today, "end_date": today},
        {},
        discover(),
    )
