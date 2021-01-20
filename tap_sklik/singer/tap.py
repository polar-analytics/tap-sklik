import json
import logging
import os
from datetime import datetime
from typing import List
from tap_sklik.sklik.constants import SKLIK_API_DATETIME_FMT

import singer
from singer import Catalog, CatalogEntry, Schema
from singer.metadata import get_standard_metadata

from ..sklik.client import Client
from ..sklik.extract import extract_ad_campaigns


def load_schema(schema_name):
    """ Load schema from schemas folder """
    schema_abs_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "schemas"
    )
    filename = f"{schema_name}.json"
    path = os.path.join(schema_abs_path, filename)
    with open(path) as file:
        schema = Schema.from_dict(json.load(file))
    return schema


def get_metadata(*args, **kwargs):
    metadatas = get_standard_metadata(*args, **kwargs)
    # all fields to automatic and selected
    for metadata_node in metadatas:
        metadata_node["metadata"].update({"inclusion": "automatic", "selected": True})
    return metadatas


def load_catalog_entries(stat_granularity: str = None) -> List[CatalogEntry]:
    # ad_campaigns metadata fields
    ad_campaigns_stream_name = "ad_campaigns"
    ad_campaigns_schema = load_schema("ad_campaigns")

    ad_campaigns_key_properties = ["id"]
    if stat_granularity is not None and stat_granularity != "total":
        ad_campaigns_key_properties.append("date")

    ad_campaigns_catalog_entry = CatalogEntry(
        tap_stream_id="ad_campaigns",
        stream=ad_campaigns_stream_name,
        schema=ad_campaigns_schema,
        key_properties=ad_campaigns_key_properties,
        metadata=get_metadata(
            schema=ad_campaigns_schema.to_dict(),
            schema_name=ad_campaigns_stream_name,
            key_properties=ad_campaigns_key_properties,
        ),
        replication_key=ad_campaigns_key_properties,
        is_view=None,
        database=None,
        table=None,
        row_count=None,
        stream_alias=None,
        replication_method=None,
    )

    # return all catalog entries
    return [ad_campaigns_catalog_entry]


def discover(stat_granularity: str = None):
    catalog_entries = load_catalog_entries(stat_granularity=stat_granularity)
    return Catalog(catalog_entries)


def extract(
    client: Client,
    schema_id: str,
    start_date: datetime,
    end_date: datetime,
    stat_granularity=None,
    include_current_day_stats=None,
):
    if schema_id == "ad_campaigns":
        # pass optional kwargs if defined
        optionalKwargs = {}
        if stat_granularity is not None:
            optionalKwargs["stat_granularity"] = stat_granularity
        if include_current_day_stats is not None:
            optionalKwargs["include_current_day_stats"] = include_current_day_stats
        # do API call
        return extract_ad_campaigns(client, start_date, end_date, **optionalKwargs)
    else:
        raise NotImplementedError()


def sync(config, state, catalog: Catalog):
    """ Sync data from tap source """
    # get required config
    token = config["token"]
    start_date = datetime.strptime(config["start_date"], SKLIK_API_DATETIME_FMT)
    end_date = datetime.strptime(config["end_date"], SKLIK_API_DATETIME_FMT)

    # get optional config
    stat_granularity = config.get("stat_granularity", None)
    include_current_day_stats = config.get("include_current_day_stats", None)

    client = Client(token)

    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        logging.info(f"Syncing stream {stream.tap_stream_id}")

        # Extract data
        extracted_data = extract(
            client,
            stream.tap_stream_id,
            start_date,
            end_date,
            stat_granularity=stat_granularity,
            include_current_day_stats=include_current_day_stats,
        )

        # Push to singer
        singer.write_schema(
            stream.tap_stream_id, stream.schema.to_dict(), stream.key_properties
        )
        bookmark_column = stream.replication_key
        is_sorted = True  # TODO is it ?
        # max_bookmark = None
        for row in extracted_data:
            # TODO: place type conversions or transformations here

            # write one or more rows to the stream:
            singer.write_records(stream.tap_stream_id, [row])
            if bookmark_column:
                if is_sorted:
                    # update bookmark to latest value
                    singer.write_state(
                        {stream.tap_stream_id: [row[key] for key in bookmark_column]}
                    )
                else:
                    # if data unsorted, save max value until end of writes
                    raise NotImplementedError(
                        "Unsorted data source is not yet supported"
                    )
        if bookmark_column and not is_sorted:
            # singer.write_state({stream.tap_stream_id: max_bookmark})
            raise NotImplementedError("Unsorted data source is not yet supported")
