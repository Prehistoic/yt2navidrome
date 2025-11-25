from typing import cast

from yt_dlp import YoutubeDL

from yt2navidrome.config import DENO_INSTALL_DIR
from yt2navidrome.downloader import Video
from yt2navidrome.utils.logging import get_logger


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
                "js_runtimes": {"deno": {"path": DENO_INSTALL_DIR}},
                "format": "bestaudio/best",
                "no_playlist": True,
                "force_generic_extractor": True,
                "skip_download": True,
                "embed_metatadata": True,
            }

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

        except Exception as e:
            cls.logger.error(f"An error occurred during initial video processing: {e}", exc_info=True)
            return None
