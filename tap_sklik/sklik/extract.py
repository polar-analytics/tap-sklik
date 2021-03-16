from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List

from tap_sklik.sklik.constants import SKLIK_API_DATETIME_FMT
from tap_sklik.sklik.dateutils import as_end_of_day, as_start_of_day

from .client import Client

PAGINATED_CALL_LIMIT = 100

AD_CAMPAIGN_REPORT_COLUMNS = [
    "actualClicks",
    "adSelection",
    "automaticLocation",
    "avgCpc",
    "avgPos",
    "clickMoney",
    "clicks",
    "context",
    "contextNetwork",
    "conversionValue",
    "conversions",
    "createDate",
    "ctr",
    "defaultBudgetId",
    "deleteDate",
    "deleted",
    # Deprecated fields, now removed
    # "deviceDesktop",
    # "deviceMobile",
    # "deviceOther",
    # "deviceTablet",
    "devicesPriceRatio",
    "endDate",
    "excludedSearchServices",
    "excludedUrls",
    "exhaustedBudget",
    "exhaustedBudgetShare",
    "exhaustedTotalBudget",
    "fulltext",
    "id",
    "impressionMoney",
    "impressions",
    "ish",
    "ishContext",
    "ishSum",
    "missImpressions",
    "name",
    "paymentMethod",
    "pno",
    "schedule",
    "scheduleEnabled",
    "startDate",
    "status",
    "stoppedBySchedule",
    "totalBudget",
    "totalBudgetFrom",
    "totalClicks",
    "totalClicksFrom",
    "totalMoney",
    "transactions",
    "type",
    "underForestThreshold",
    "underLowerThreshold",
    "videoFormat",
]


def _extract_paginated(
    client: Client,
    method: str,
    arguments: Dict[str, Any],
    response_data_list_key: str,
    limit: int = PAGINATED_CALL_LIMIT,
) -> List[Dict[str, Any]]:
    # set to False when the API calls gets 0 results (because out of pagination bounds)
    non_empty_response = True
    # pagination offset (+= limit at every successful call)
    offset = 0

    # returned value
    # extend this list at each successful API call
    accumulated_records = []

    # iterate while there are results in the pagination
    while non_empty_response:
        # build
        pagination_display_options = {
            "limit": limit,
            "offset": offset,
        }
        # immutable data is good
        arguments_with_pagination = deepcopy(arguments)
        arguments_with_pagination[1].update(pagination_display_options)

        # get data
        data = client.call(method, arguments_with_pagination)
        records = data.get(response_data_list_key, [])
        # stop if empty data
        if len(records) == 0:
            non_empty_response = False
            continue
        # store result
        accumulated_records.extend(records)
        # increment offset
        offset += limit

    return accumulated_records


def extract_ad_campaigns(
    client: Client,
    start_date: datetime,
    end_date: datetime,
    stat_granularity: str,
    include_current_day_stats: bool,
):
    """
    Creates an ad campaigns report, then fetches that report

    `stat_granularity` is one of `['total', 'daily', 'monthly', 'quarterly', 'yearly']`
    """
    start_date_start_of_day = as_start_of_day(start_date)
    end_date_end_of_day = as_end_of_day(end_date)

    if include_current_day_stats and stat_granularity not in ["total", "daily"]:
        raise ValueError(
            "include_current_day_stats can be set to True only when stat_granularity "
            + "is either 'total' or 'daily'"
        )

    formatted_start_date = start_date_start_of_day.strftime(SKLIK_API_DATETIME_FMT)
    formatted_end_date = end_date_end_of_day.strftime(SKLIK_API_DATETIME_FMT)

    create_report_display_options = {"statGranularity": stat_granularity}
    if include_current_day_stats is not None:
        create_report_display_options[
            "includeCurrentDayStats"
        ] = include_current_day_stats

    create_report_data = client.call(
        "campaigns.createReport",
        [
            # restrictionFilter
            {"dateFrom": formatted_start_date, "dateTo": formatted_end_date},
            # displayOptions
            create_report_display_options,
        ],
    )

    if "reportId" not in create_report_data:
        raise ValueError("Could not create a new report")
    report_id = create_report_data["reportId"]

    # fetch report
    campaigns = _extract_paginated(
        client,
        "campaigns.readReport",
        [
            # reportId
            report_id,
            # displayOptions
            {"displayColumns": AD_CAMPAIGN_REPORT_COLUMNS},
        ],
        response_data_list_key="report",
    )

    # campaigns.stats is an array, flatten by duplication
    campaigns = [
        # merge
        dict(**record, **recordStat)
        for record in campaigns
        for recordStat in record.get("stats", [])
    ]

    for record in campaigns:
        # remove nested .stats
        del record["stats"]
        # convert ".date" to string if present
        if "date" in record:
            record["date"] = str(record["date"])

    return campaigns
