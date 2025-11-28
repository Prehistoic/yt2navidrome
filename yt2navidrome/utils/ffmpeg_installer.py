import subprocess

import ffmpeg_downloader as ffdl

from yt2navidrome.utils.logging import get_logger

# --- Configuration ---

# For Windows: Direct download link for a reliable FFmpeg build
FFMPEG_URL_WINDOWS = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# --- Core Functionality ---


class FFmpegInstaller:
    logger = get_logger(__name__)

    @classmethod
    def ensure_ffmpeg_installed(cls) -> bool:
        """Determines the OS and ensures FFmpeg is installed."""
        cls.logger.debug("Checking if FFmpeg is installed")

        if ffdl.installed():
            cls.logger.debug(f"FFmpeg already installed at {ffdl.ffmpeg_path}")
            return True

        # FFmpeg is not installed, proceed with OS-specific installation
        cls.logger.debug("Installing FFmpeg")

        try:
            subprocess.run(["ffdl", "install", "-y"])  # noqa: S607,S603
        except Exception:
            cls.logger.exception("ffdl failed to install FFmpeg")
            return False

        cls.logger.debug(f"FFmpeg is now installed at {ffdl.ffmpeg_path}")
        return True
