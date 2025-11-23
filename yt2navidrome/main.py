import logging

import click

from yt2navidrome.utils.banner import display_banner
from yt2navidrome.utils.logging import disable_all_logging, get_logger, set_global_logging_level

logger = get_logger(__name__)


@click.command
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose logging",
)
@click.option(
    "--quiet",
    is_flag=True,
    default=False,
    help="Disable all logs",
)
# Lorem Ipsum Options
# @optgroup.group("Lorem Ipsum", help="lorem ipsum")
# @optgroup.option(
#     [...]
# )
def main(
    verbose: bool,
    quiet: bool,
) -> None:
    """
    CLI entrypoint
    """
    # Finish setting up logging with args
    if verbose:
        set_global_logging_level(logging.DEBUG)

    if quiet:
        disable_all_logging()

    # Display banner
    if not quiet:
        display_banner()

    # Main logic
    pass
