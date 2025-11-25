import os

from yt2navidrome.downloader import Video
from yt2navidrome.utils.logging import get_logger


class OutputHelper:
    logger = get_logger(__name__)

    @staticmethod
    def clean_path_ascii(s: str) -> str:
        """Return a string with only safe ASCII characters for file paths, spaces to underscores, no trailing spaces."""
        # Remove non-ASCII characters
        s = s.encode("ascii", "ignore").decode("ascii")
        # Strip the string as we may have removed characters after the last space
        s = s.strip()
        return s

    @classmethod
    def get_video_path(cls, output_dir: str, video: Video) -> str:
        """Generate the expected outputh path for a video"""
        safe_uploader = cls.clean_path_ascii(video.uploader)
        safe_title = cls.clean_path_ascii(video.title)
        return os.path.join(output_dir, safe_uploader, safe_title)

    @classmethod
    def exists(cls, output_dir: str, video: Video) -> bool:
        """Check if a file exists at output_dir/video.uploader/video.title with any extension."""
        expected_path = cls.get_video_path(output_dir, video)

        cls.logger.debug(f"Checking if {expected_path} exists")

        dir_path = os.path.dirname(expected_path)
        if not os.path.isdir(dir_path):
            cls.logger.debug(f"Output dir {dir_path} does not exist yet")
            return False

        for fname in os.listdir(dir_path):
            name, _ = os.path.splitext(fname)
            if name == os.path.basename(expected_path):
                cls.logger.debug(f"{expected_path} exists")
                return True

        cls.logger.debug(f"{expected_path} missing")
        return False
