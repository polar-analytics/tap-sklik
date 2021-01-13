import json
import logging
import os
from datetime import datetime
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


def load_catalog_entries():
    ad_campaigns_stream_name = "ad_campaigns"
    ad_campaigns_schema = load_schema("ad_campaigns")
    ad_campaigns_key_properties = ["id"]

    return [
        CatalogEntry(
            tap_stream_id="ad_campaigns",
            stream=ad_campaigns_stream_name,
            schema=ad_campaigns_schema,
            key_properties=ad_campaigns_key_properties,
            metadata=get_metadata(
                schema=ad_campaigns_schema.to_dict(),
                schema_name=ad_campaigns_stream_name,
                key_properties=ad_campaigns_key_properties,
            ),
            replication_key=None,
            is_view=None,
            database=None,
            table=None,
            row_count=None,
            stream_alias=None,
            replication_method=None,
        )
    ]


def discover():
    return Catalog(load_catalog_entries())


def extract(client: Client, schema_id: str, start_date: datetime, end_date: datetime):
    if schema_id == "ad_campaigns":
        return extract_ad_campaigns(client, start_date, end_date)
    else:
        raise NotImplementedError()


def sync(config, state, catalog: Catalog):
    """ Sync data from tap source """
    # get Client
    token = config["token"]
    start_date = datetime.strptime(config["start_date"], SKLIK_API_DATETIME_FMT)
    end_date = datetime.strptime(config["end_date"], SKLIK_API_DATETIME_FMT)

    client = Client(token)

    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        logging.info(f"Syncing stream {stream.tap_stream_id}")

        # Extract data
        extracted_data = extract(client, stream.tap_stream_id, start_date, end_date)

        # Push to singer
        singer.write_schema(
            stream.tap_stream_id, stream.schema.to_dict(), stream.key_properties
        )
        bookmark_column = stream.replication_key
        is_sorted = True  # TODO is it ?
        max_bookmark = None
        for row in extracted_data:
            # TODO: place type conversions or transformations here

            # write one or more rows to the stream:
            singer.write_records(stream.tap_stream_id, [row])
            if bookmark_column:
                if is_sorted:
                    # update bookmark to latest value
                    singer.write_state({stream.tap_stream_id: row[bookmark_column]})
                else:
                    # if data unsorted, save max value until end of writes
                    max_bookmark = max(max_bookmark, row[bookmark_column])
        if bookmark_column and not is_sorted:
            singer.write_state({stream.tap_stream_id: max_bookmark})
