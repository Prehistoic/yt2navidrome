import logging

import click
from click_option_group import optgroup

from yt2navidrome.utils.banner import display_banner
from yt2navidrome.utils.logging import disable_all_logging, get_logger, set_global_logging_level

logger = get_logger(__name__)


@click.command
@optgroup.group("Misc")
@optgroup.option(
    "--verbose",
    "-v",
    is_flag=True,
    default=False,
    help="Enable verbose logging",
)
@optgroup.option(
    "--quiet",
    is_flag=True,
    default=False,
    help="Disable all logs",
)
def main(
    verbose: bool,
    quiet: bool,
) -> None:
    """
    CLI tool to download YT videos and playlists with metadata required for Navidrome
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
