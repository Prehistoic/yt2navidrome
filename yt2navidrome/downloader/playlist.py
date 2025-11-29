from pathlib import Path
from typing import Any, cast

from yt_dlp import YoutubeDL

from yt2navidrome.config import COOKIE_FILE_PATH
from yt2navidrome.downloader.common import check_if_already_downloaded, extract_video_id_from_url
from yt2navidrome.downloader.models import Playlist
from yt2navidrome.downloader.video import Video, VideoUtils
from yt2navidrome.utils.logging import get_logger


class PlaylistUtils:
    logger = get_logger(__name__)

    @classmethod
    def extract_video_if_needed(cls, entry: dict[str, Any], output_dir: Path) -> Video | None:
        """Extract video info if not already downloaded."""
        video_url = cast(str, entry.get("url"))
        if not video_url:
            cls.logger.error(f"Failed to process video. Invalid URL: {video_url}")
            return None

        video_id = extract_video_id_from_url(video_url)
        if not video_id:
            cls.logger.error("Failed to process video. No YT ID found")
            return None

        if check_if_already_downloaded(output_dir, video_id):
            cls.logger.debug(f"Video with ID {video_id} already exists. Skipping...")
            return None

        # Can skip check since already done above
        video = VideoUtils.process_video_url(video_url, output_dir, check_if_exists=False)
        return video

    @classmethod
    def process_playlist_url(cls, playlist_url: str, output_dir: Path) -> Playlist | None:
        """
        Extracts info for videos in a YouTube playlist. Skips videos already downloaded.

        Args:
            playlist_url: The URL of the YouTube playlist.
            output_dir: Path where the missing videos would be downloaded.

        Returns:
            A Playlist instance (or None).
        """
        try:
            cls.logger.info(f"Processing playlist {playlist_url}")

            ydl_opts: dict[str, Any] = {
                "quiet": True,  # Suppress status messages
                "extract_flat": "in_playlist",  # Only extract titles and URLs from the playlist, not all video info yet
                "force_generic_extractor": True,  # Ensure it processes the playlist URL as a playlist
                "skip_download": True,  # Do not download anything
            }

            if Path(COOKIE_FILE_PATH).exists():
                ydl_opts.update({"cookiefile": COOKIE_FILE_PATH})

            # Extract the playlist information
            with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                playlist_info = ydl.extract_info(playlist_url, download=False)

            if not playlist_info or playlist_info.get("_type") != "playlist":
                cls.logger.error(f"URL {playlist_url} did not return a valid playlist.")
                return None

            playlist_title = cast(str, playlist_info.get("title", "Unknown Playlist"))
            entries = cast(list[dict[str, Any]], playlist_info.get("entries", []))

            cls.logger.info(f"Playlist found: **{playlist_title}**")
            cls.logger.info(f"Total videos to process: {len(entries)}")

            # Extract videos, filtering out None and skipped ones
            playlist_videos = [
                v for entry in entries if entry for v in [cls.extract_video_if_needed(entry, output_dir)] if v
            ]

            # Create and return Playlist instance
            return Playlist(title=playlist_title, videos=playlist_videos)

        except Exception as e:
            cls.logger.error(f"An error occurred during initial playlist processing: {e}", exc_info=True)
            return None
