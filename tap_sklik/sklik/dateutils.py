from datetime import datetime, time


def as_start_of_day(dt: datetime) -> datetime:
    """
    Get a datetime object that with same date but hours=0, minutes=0, seconds=0, ... in
    same timezone.
    """
    return datetime.combine(dt, time.min, dt.tzinfo)


def as_end_of_day(dt: datetime) -> datetime:
    """
    Get a datetime object that with same date but hours=23, minutes=59, seconds=59, ...
    in same timezone.
    """
    return datetime.combine(dt, time.max, dt.tzinfo)
