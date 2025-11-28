from pathlib import Path
from typing import Any, cast

from yt_dlp import YoutubeDL

from yt2navidrome.config import COOKIE_FILE_PATH
from yt2navidrome.downloader.models import Playlist
from yt2navidrome.downloader.video import VideoUtils
from yt2navidrome.utils.logging import get_logger


class PlaylistUtils:
    logger = get_logger(__name__)

    @classmethod
    def extract_info_from_url(cls, playlist_url: str) -> Playlist | None:
        """
        Extracts URL and title for each video in a YouTube playlist

        Args:
            playlist_url: The URL of the YouTube playlist.

        Returns:
            A Playlist instance.
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

            # 1. Extract the playlist information
            # This step gets the list of entries (videos) in the playlist
            with YoutubeDL(ydl_opts) as ydl:  # type: ignore[arg-type]
                playlist_info = ydl.extract_info(playlist_url, download=False)

            if not playlist_info or playlist_info.get("_type") != "playlist":
                cls.logger.error(f"URL {playlist_url} did not return a valid playlist.")
                return None

            playlist_title = cast(str, playlist_info.get("title", "Unknown Playlist"))
            entries = cast(list[dict[str, Any]], playlist_info.get("entries", []))

            cls.logger.info(f"Playlist found: **{playlist_title}**")
            cls.logger.info(f"Total videos to process: {len(entries)}")

            # 2. Iterate over the entries in the playlist
            playlist_videos = []
            for idx, entry in enumerate(entries):
                if not entry:
                    continue

                cls.logger.info(f"Processing video #{idx + 1}")

                video_url = cast(str, entry.get("url"))
                if not video_url:
                    cls.logger.error(f"Failed to process video. Invalid URL: {video_url}")
                    continue

                video = VideoUtils.extract_info_from_url(video_url)

                if video:
                    playlist_videos.append(video)

            # 3. Create and return Playlist instance
            return Playlist(title=playlist_title, videos=playlist_videos)

        except Exception as e:
            cls.logger.error(f"An error occurred during initial playlist processing: {e}", exc_info=True)
            return None
