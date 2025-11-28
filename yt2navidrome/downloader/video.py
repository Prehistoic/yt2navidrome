from pathlib import Path
from typing import cast

import ffmpeg_downloader as ffdl
from yt_dlp import YoutubeDL

from yt2navidrome.config import COOKIE_FILE_PATH
from yt2navidrome.downloader.models import Video
from yt2navidrome.utils.logging import get_logger


def clean_path_ascii(s: str) -> str:
    """Return a string with only safe ASCII characters for file paths, spaces to underscores, no trailing spaces."""
    # Remove non-ASCII characters
    s = s.encode("ascii", "ignore").decode("ascii")
    # Strip the string as we may have removed characters after the last space
    s = s.strip()
    return s


class VideoUtils:
    logger = get_logger(__name__)

    @classmethod
    def extract_info_from_url(cls, video_url: str) -> Video | None:
        """
        Extracts relevant info from a Youtube video URL.

        Args:
            video_url: The URL of the YouTube video.

        Returns:
            A Video instance.
        """
        try:
            cls.logger.debug(f"Starting video scan for {video_url}...")

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

            # 1. Extract the video information
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
    def exists(cls, video: Video, output_dir: Path) -> bool:
        """Check if a file exists at output_dir/video.uploader/video.title with any extension."""
        expected_dir = output_dir / clean_path_ascii(video.uploader)
        expected_name = clean_path_ascii(video.title)

        cls.logger.debug(f"Checking if {expected_dir}/{expected_name} exists")

        if not expected_dir.is_dir():
            cls.logger.debug(f"Output dir {expected_dir} does not exist yet")
            return False

        for file in expected_dir.iterdir():
            if file.is_file() and file.stem == expected_name:
                cls.logger.debug(f"{file} exists")
                return True

        cls.logger.debug(f"{expected_dir}/{expected_name} missing")
        return False

    @classmethod
    def download(cls, video: Video, output_dir: Path, custom_parsers: list[str]) -> None:
        """
        Download a Youtube video URL while embedding relevant metadata.

        Args:
            video: The YouTube video to download.
            output_dir: Directory where the video will be saved
            custom_parsers: A list of strings indicating yt-dlp how to parse metadata

        Returns:
            The path of the downloaded video (or None if download failed)
        """
        cls.logger.info(f"Starting download for {video.url}")
        cls.logger.debug(f"Parsers used: {' | '.join(custom_parsers)}")

        if not output_dir.is_dir():
            cls.logger.error(f"Output directory {output_dir} not found")
            return None

        download_dir = output_dir / clean_path_ascii(video.uploader)
        download_dir.mkdir(exist_ok=True)
        cls.logger.debug(f"Download dir: {download_dir}")

        ydl_opts = {
            # General Options
            "format": "bestaudio[ext=m4a]",
            "outtmpl": str(download_dir / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "writethumbnail": True,
            # Parse metadata with given parsers
            "parse_metadata": custom_parsers,
            # FFmpeg
            "ffmpeg_location": ffdl.ffmpeg_path,
            # Postprocessor: Audio Extraction and Conversion
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ],
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

            cls.logger.info(f"Successfully downloaded {video.url} to {download_dir}")

        except Exception:
            cls.logger.exception(f"Failed to download {video.url}")
            return None
