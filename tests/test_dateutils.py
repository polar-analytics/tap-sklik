from datetime import datetime
from tap_sklik.sklik.dateutils import as_end_of_day, as_start_of_day
import pytz


def test_as_start_of_day():
    # test that time is at min (0, 0, 0)
    assert as_start_of_day(datetime(2020, 1, 1, 12, 13, 14)) == datetime(
        2020, 1, 1, 0, 0, 0
    )
    # test not changing if time is already at min
    assert as_start_of_day(datetime(2020, 1, 1, 0, 0, 0)) == datetime(
        2020, 1, 1, 0, 0, 0
    )
    # test not changing timezone
    assert (
        as_start_of_day(
            datetime(2020, 1, 1, tzinfo=pytz.timezone("Australia/Sydney"))
        ).tzinfo.zone
        == "Australia/Sydney"
    )


def test_as_end_of_day():
    # test that time is at min (0, 0, 0)
    assert as_end_of_day(datetime(2020, 1, 1, 12, 13, 14)) == datetime(
        2020, 1, 1, 23, 59, 59, 999999
    )
    # test not changing if time is already at max
    assert as_end_of_day(datetime(2020, 1, 1, 23, 59, 59, 999999)) == datetime(
        2020, 1, 1, 23, 59, 59, 999999
    )
    # test not changing timezone
    assert (
        as_end_of_day(
            datetime(2020, 1, 1, tzinfo=pytz.timezone("Australia/Sydney"))
        ).tzinfo.zone
        == "Australia/Sydney"
    )
