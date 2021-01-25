import logging
from tap_sklik.sklik.dateutils import as_end_of_day, as_start_of_day
from tap_sklik.sklik.constants import SKLIK_API_DATETIME_FMT
from datetime import datetime
from collections import namedtuple

ParsedConfig = namedtuple(
    "ParsedConfig",
    ("start_date", "end_date", "stat_granularity", "include_current_day_stats"),
)


def get_parsed_configs(config) -> ParsedConfig:
    start_date = datetime.strptime(config["start_date"], SKLIK_API_DATETIME_FMT)
    end_date = datetime.strptime(config["end_date"], SKLIK_API_DATETIME_FMT)

    stat_granularity = config.get("stat_granularity", "daily")
    include_current_day_stats = config.get("include_current_day_stats", None)

    if include_current_day_stats is None:
        today = datetime.now()
        start_date_start_of_day = as_start_of_day(start_date)
        end_date_end_of_day = as_end_of_day(end_date)

        if (
            # granularity is daily
            stat_granularity == "daily"
            # and today's date is in queried range
            and (start_date_start_of_day <= today <= end_date_end_of_day)
        ):
            include_current_day_stats = True
            logging.info("Automatically set include_current_day_stats to True")

    return ParsedConfig(
        start_date=start_date,
        end_date=end_date,
        stat_granularity=stat_granularity,
        include_current_day_stats=include_current_day_stats,
    )
