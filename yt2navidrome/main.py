import logging
import sys
import time
from pathlib import Path

import click
from click_option_group import optgroup

from yt2navidrome.config import (
    CONSECUTIVE_DOWNLOADS_SLEEP_TIME,
    DEFAULT_ALBUM,
    DEFAULT_ARTIST,
    DEFAULT_TITLE,
    DEFAULT_TRACK_NUMBER,
)
from yt2navidrome.downloader.playlist import PlaylistUtils
from yt2navidrome.downloader.video import VideoUtils
from yt2navidrome.template import Template, TemplateReader
from yt2navidrome.utils.banner import display_banner
from yt2navidrome.utils.ffmpeg import FFmpegHelper, FFmpegInstaller
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
        playlist = PlaylistUtils.process_playlist_url(template.url, output_dir)
        if playlist:
            missing_videos = playlist.videos
    else:
        video = VideoUtils.process_video_url(template.url, output_dir)
        if video:
            missing_videos = [video]

    if missing_videos:
        logger.info(f"Missing videos to download: {len(missing_videos)}")
    else:
        logger.info("No missing videos. Exiting...")
        sys.exit(0)

    # Download videos then add metadata based on provided parsers from the template
    for idx, video in enumerate(missing_videos):
        logger.info(f"Processing missing video {idx + 1}/{len(missing_videos)}")

        download_path = VideoUtils.download(video, output_dir)

        if download_path:
            # Generate metadata entries from template parsers
            metadata_entries = VideoUtils.parse_metadata_from_info(video, template.parsers)

            # Ensure required metadata keys have default values
            metadata_entries.setdefault("title", DEFAULT_TITLE)
            metadata_entries.setdefault("artist", DEFAULT_ARTIST)
            metadata_entries.setdefault("album", DEFAULT_ALBUM)
            metadata_entries.setdefault("track", DEFAULT_TRACK_NUMBER)
            metadata_entries["album_artist"] = metadata_entries["artist"]

            # Then add metadata to the downloaded file
            FFmpegHelper.add_metadata(download_path, metadata_entries)

            # Finally We read tags from the downloaded file
            if download_path:
                tags = FFmpegHelper.get_tags(download_path)
                artist: str = tags.get("artist", "ERROR")
                title: str = tags.get("title", "ERROR")
                album: str = tags.get("album", "ERROR")
                track: int = tags.get("track", -1)
                logger.info(f"{download_path.name} => Artist: {artist}")
                logger.info(f"{download_path.name} => Title: {title}")
                logger.info(f"{download_path.name} => Album: {album}")
                logger.info(f"{download_path.name} => Track n°: {track}")

        # Then we sleep for a bit to avoid YT rate limits
        if idx != len(missing_videos) - 1:
            time.sleep(CONSECUTIVE_DOWNLOADS_SLEEP_TIME)
