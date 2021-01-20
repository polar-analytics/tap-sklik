import singer
from singer import utils
from .tap import discover, sync

REQUIRED_CONFIG_KEYS = ["token", "start_date", "end_date"]
LOGGER = singer.get_logger()


@utils.handle_top_exception(LOGGER)
def cli():
    # Parse command line arguments
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    # If discover flag was passed, run discovery mode and dump output to stdout
    if args.discover:
        catalog = discover(args.config)
        catalog.dump()
    # Otherwise run in sync mode
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = discover(args.config)
        sync(args.config, args.state, catalog)
