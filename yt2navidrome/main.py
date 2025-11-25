import logging
import sys

import click
from click_option_group import optgroup

from yt2navidrome.downloader import PlaylistUtils, Video, VideoUtils
from yt2navidrome.template import TemplateReader
from yt2navidrome.utils.banner import display_banner
from yt2navidrome.utils.deno_installer import DenoInstaller
from yt2navidrome.utils.logging import disable_all_logging, get_logger, set_global_logging_level
from yt2navidrome.utils.output_helper import OutputHelper

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
@optgroup.group("IO")
@optgroup.option(
    "--input",
    "-i",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Input directory containing yt2navidrome templates",
)
@optgroup.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True),
    required=True,
    help="Output directory where music will be saved",
)
def main(verbose: bool, quiet: bool, input_dir: str, output_dir: str) -> None:
    """
    CLI tool to download YT videos and playlists with metadata required for Navidrome
    """
    # Finish setting up logging with args
    if verbose:
        set_global_logging_level(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    if quiet:
        disable_all_logging()

    # Display banner
    if not quiet:
        display_banner()

    # Ensure deno is installed (yt-dlp now requires a JS runtime for Youtube extraction)
    if not DenoInstaller.ensure_deno_installed():
        logger.error("Failure in downloading deno (JS runtime required for yt-dlp). Exiting...")
        sys.exit(1)

    # 1 - Read yt2navidrome templates from input dir
    logger.info(f"Reading yt2navidrome templates from {input_dir}...")
    templates = TemplateReader.read_directory(input_dir)
    logger.info(f"Found {len(templates)} yt2navidrome templates")

    # 2 - Gather the list of videos based on the URLs in the given templates
    videos: list[Video] = []
    for template in templates:
        if template.playlist:
            playlist = PlaylistUtils.extract_info_from_url(template.url)
            if playlist:
                videos.extend(playlist.videos)
        else:
            video = VideoUtils.extract_info_from_url(template.url)
            if video:
                videos.append(video)

    # 3 - Prepare the list of missing videos that we will need to download
    missing_videos: list[Video] = list(filter(lambda video: not OutputHelper.exists(output_dir, video), videos))

    # 4 - Download videos while adding metadata based on regexes given in templates
    print(missing_videos)
