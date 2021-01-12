from typing import Any, Dict, List
from copy import deepcopy

from .client import Client

PAGINATED_CALL_LIMIT = 100


def _extract_paginated(
    client: Client,
    method: str,
    arguments: Dict[str, Any],
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
        campaigns = data.get("campaigns", [])

        # stop if empty data
        if len(campaigns) == 0:
            non_empty_response = False
            continue

        # store result
        accumulated_campaigns.extend(campaigns)

        # increment offset
        offset += limit

    return accumulated_campaigns


def extract_ad_campaigns(client: Client):
    # get ad campaigns
    return _extract_paginated(
        client,
        "campaigns.list",
        [
            # restrictionFilter
            {},
            # displayOptions
            {
                "displayColumns": [
                    "id",
                    "name",
                    "status",
                    "type",
                    "createDate",
                    "endDate",
                    "defaultBudgetId",
                    "exhaustedTotalBudget",
                    "totalBudgetFrom",
                    "totalBudget",
                ]
            },
        ],
    )
