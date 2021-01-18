from tap_sklik.sklik.constants import SKLIK_API_DATETIME_FMT
from typing import Any, Dict, List
from copy import deepcopy
from datetime import datetime

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
    "deviceDesktop",
    "deviceMobil",
    "deviceOther",
    "deviceTablet",
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
    accumulated_campaigns = []

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
        campaigns = data.get(response_data_list_key, [])
        # stop if empty data
        if len(campaigns) == 0:
            non_empty_response = False
            continue
        # store result
        accumulated_campaigns.extend(campaigns)
        # increment offset
        offset += limit

    return accumulated_campaigns


def extract_ad_campaigns(client: Client, start_date: datetime, end_date: datetime):
    """
    Creates an ad campaigns report, then fetches that report
    """
    formatted_start_date = start_date.strftime(SKLIK_API_DATETIME_FMT)
    formatted_end_date = end_date.strftime(SKLIK_API_DATETIME_FMT)
    create_report_data = client.call(
        "campaigns.createReport",
        [{"dateFrom": formatted_start_date, "dateTo": formatted_end_date}],
    )

    if "reportId" not in create_report_data:
        raise ValueError("Could not create a new report")
    report_id = create_report_data["reportId"]

    # fetch report
    return _extract_paginated(
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
