import logging
import sys

import click

from yt2navidrome.commands import download, edit
from yt2navidrome.utils.banner import display_banner
from yt2navidrome.utils.ffmpeg import FFmpegInstaller
from yt2navidrome.utils.logging import disable_all_logging, get_logger, set_global_logging_level

logger = get_logger(__name__)


@click.group()
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
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """CLI tool to download and format YT videos and playlists with metadata required for Navidrome"""
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet

    # Finish setting up logging with args
    if verbose:
        set_global_logging_level(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    if quiet:
        disable_all_logging()

    # Display banner
    if not quiet:
        display_banner()

    # Ensure FFmpeg is installed
    if not FFmpegInstaller.ensure_ffmpeg_installed():
        logger.error("Failure in downloading FFmpeg. Exiting...")
        sys.exit(1)


# Register subcommands
cli.add_command(download)
cli.add_command(edit)
