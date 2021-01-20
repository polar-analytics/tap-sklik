from datetime import datetime, timedelta
from tap_sklik.singer.tap import discover, sync
from .settings import SKLIK_TEST_TOKEN


def test_discover():
    discover({"start_date": "20200101", "end_date": "20200101"})


def test_discover_with_granularity():
    discover(
        {"start_date": "20200101", "end_date": "20200101", "stat_granularity": "weekly"}
    )


def test_sync():
    some_date_str = datetime(2018, 1, 1).strftime("%Y%m%d")
    config = {
        "token": SKLIK_TEST_TOKEN,
        "start_date": some_date_str,
        "end_date": some_date_str,
    }
    sync(
        config,
        {},
        discover(config),
    )


def test_sync_today():
    today_str = datetime.now().strftime("%Y%m%d")
    config = {"token": SKLIK_TEST_TOKEN, "start_date": today_str, "end_date": today_str}
    sync(
        config,
        {},
        discover(config),
    )


def test_sync_weekly():
    some_date = datetime(2018, 1, 1)
    some_later_date = some_date + timedelta(days=15)
    config = {
        "token": SKLIK_TEST_TOKEN,
        "start_date": some_date.strftime("%Y%m%d"),
        "end_date": some_later_date.strftime("%Y%m%d"),
        "stat_granularity": "weekly",
    }
    sync(
        config,
        {},
        discover(config),
    )
