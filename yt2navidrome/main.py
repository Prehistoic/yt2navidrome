import logging
import os
import sys
import time
from pathlib import Path

import click
from click_option_group import optgroup

from yt2navidrome.downloader.playlist import PlaylistUtils
from yt2navidrome.downloader.video import Video, VideoUtils
from yt2navidrome.template import Template, TemplateReader
from yt2navidrome.utils.banner import display_banner
from yt2navidrome.utils.ffmpeg_installer import FFmpegInstaller
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
@optgroup.group("IO")
@optgroup.option(
    "--input",
    "-i",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Input directory containing yt2navidrome templates",
)
@optgroup.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    help="Output directory where music will be saved",
)
def main(verbose: bool, quiet: bool, input_dir: Path, output_dir: Path) -> None:
    """
    CLI tool to download YT videos and playlists with metadata required for Navidrome
    """
    try:
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

        # 1 - Read yt2navidrome templates from input dir
        logger.info(f"Reading yt2navidrome templates from {input_dir}...")
        templates = TemplateReader.read_directory(input_dir)
        logger.info(f"Found {len(templates)} yt2navidrome templates")

        # We repeat following actions for each template
        for template in templates:
            process_template(template, output_dir)

    except Exception:
        logger.exception("Unexpected error")
        sys.exit(1)


def process_template(template: Template, output_dir: Path) -> None:
    """
    Download videos from a template

    Args:
        template: Template to consider
        output_dir: Output directory where the video(s) will be downloaded
    """
    # Gather the list of videos based on the URLs in the given templates
    if template.playlist:
        playlist = PlaylistUtils.extract_info_from_url(template.url)
        if playlist:
            videos = playlist.videos
    else:
        video = VideoUtils.extract_info_from_url(template.url)
        if video:
            videos = [video]

    # Prepare the list of missing videos that we will need to download
    missing_videos: list[Video] = list(filter(lambda video: not VideoUtils.exists(video, output_dir), videos))

    # Download videos while adding metadata based on regexes given in templates
    os.makedirs(output_dir, exist_ok=True)
    for video in missing_videos:
        VideoUtils.download(video, output_dir, template.parsers)
        time.sleep(10)
