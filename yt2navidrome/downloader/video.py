import re
from pathlib import Path
from typing import cast

import ffmpeg_downloader as ffdl
from yt_dlp import YoutubeDL

from yt2navidrome.config import COOKIE_FILE_PATH
from yt2navidrome.downloader.common import check_if_already_downloaded, extract_video_id_from_url
from yt2navidrome.downloader.models import Video
from yt2navidrome.template import MetadataParser
from yt2navidrome.utils.logging import get_logger


def clean_path_ascii(s: str) -> str:
    """Return a string with only safe ASCII characters for file paths"""
    # Remove non-ASCII characters
    s = s.encode("ascii", "ignore").decode("ascii")
    # Remove forbidden characters in filenames
    s = re.sub(r'[<>:"/\\|?*]', "-", s)
    # Remove leading/trailing - and spaces
    s = s.strip("- ")
    return s


class VideoUtils:
    logger = get_logger(__name__)

    @classmethod
    def process_video_url(cls, video_url: str, output_dir: Path, check_if_exists: bool = True) -> Video | None:
        """
        Extracts relevant info from a Youtube video URL.

        Args:
            video_url: The URL of the YouTube video.
            output_dir: Path where the missing videos would be downloaded.
            check_if_exists: Whether or not to check if the video was already downloaded.

        Returns:
            A Video instance (or None).
        """
        try:
            cls.logger.debug(f"Starting video scan for {video_url}...")

            if check_if_exists:
                video_id = extract_video_id_from_url(video_url)
                if not video_id:
                    cls.logger.error("Failed to process video. No YT ID found")
                    return None

                if check_if_already_downloaded(output_dir, video_id):
                    cls.logger.debug(f"Video with ID {video_id} already exists. Skipping...")
                    return None

            # 1. Extract the video information
            ydl_opts = {
                "quiet": True,
                "format": "bestaudio/best",
                "no_playlist": True,
                "force_generic_extractor": True,
                "skip_download": True,
                "embed_metatadata": True,
            }

            if Path(COOKIE_FILE_PATH).exists():
                ydl_opts.update({"cookiefile": COOKIE_FILE_PATH})

            with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                video_info = ydl.extract_info(video_url, download=False)

            if not video_info:
                cls.logger.error(f"URL {video_url} did not return a valid video.")
                return None

            # 2. Parse the information to retrieve relevant fields
            video_title = cast(str, video_info.get("title", "Untitled Video"))
            video_uploader = cast(str, video_info.get("uploader", "Unknown Uploader"))

            # 3. Create and return the Video instance
            return Video(url=video_url, title=video_title, uploader=video_uploader)

        except Exception:
            cls.logger.exception("An error occurred during initial video processing")
            return None

    @classmethod
    def download(cls, video: Video, output_dir: Path) -> Path | None:
        """
        Download a Youtube video URL.

        Args:
            video: The YouTube video to download.
            output_dir: Directory where the video will be saved

        Returns:
            The path of the downloaded video (or None if download failed)
        """
        cls.logger.info(f"Starting download for {video.url}")

        video_id = extract_video_id_from_url(video.url)
        if not video_id:
            cls.logger.error("Failed to process video. No YT ID found")
            return None

        download_filename_no_ext = clean_path_ascii(video.title)
        download_dir = output_dir / clean_path_ascii(video.uploader) / video_id
        download_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts = {
            # General Options
            "format": "bestaudio[ext=m4a]",
            "outtmpl": str(download_dir / download_filename_no_ext) + ".%(ext)s",
            "noplaylist": True,
            "writethumbnail": True,
            # FFmpeg
            "ffmpeg_location": ffdl.ffmpeg_path,
            # Postprocessors
            "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}, {"key": "EmbedThumbnail"}],
            # Verbosity
            "quiet": True,
            "noprogress": True,
            "simulate": False,
        }

        if Path(COOKIE_FILE_PATH).exists():
            ydl_opts.update({"cookiefile": COOKIE_FILE_PATH})

        try:
            with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                ydl.download(video.url)

            # Verifies the file was indeed downloaded and return its path
            expected_path = download_dir / (download_filename_no_ext + ".mp4")
            if expected_path.exists():
                cls.logger.info(f"Successfully downloaded {video.url} to {expected_path}")
                return expected_path
            else:
                cls.logger.warning(f"Download finished but no file found at {expected_path}")
                return None

        except Exception:
            cls.logger.exception(f"Failed to download {video.url}")
            return None

    @classmethod
    def parse_metadata_from_info(cls, video: Video, parsers: list[MetadataParser]) -> dict[str, str]:
        """
        Parse video info to generate metadata entries.

        Args:
            video: The video to extract info from
            parsers: A list of parsers to use to define the metadata entries values

        Returns:
            A dict with metadata entries (key: value)
        """
        cls.logger.info(f"Parsing metadata from video {video.title}")

        metadata_entries = {}

        for parser in parsers:
            cls.logger.debug(parser.summary())

            try:
                source = getattr(video, parser.input)
            except Exception:
                cls.logger.exception(f"Failed to get attribute {parser.input} from Video instance")
                return {}

            compiled_pattern = re.compile(parser.regex)
            match = compiled_pattern.search(source)

            if match:
                cls.logger.debug(f"Found matching values: {match.groupdict()}")
                metadata_entries.update(match.groupdict())

        return metadata_entries
