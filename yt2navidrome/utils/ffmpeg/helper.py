import json
import subprocess as sp
import tempfile
from pathlib import Path
from typing import Any, cast

import ffmpeg_downloader as ffdl

from yt2navidrome.utils.logging import get_logger


class FFmpegHelper:
    logger = get_logger(__name__)

    @classmethod
    def get_metadata(cls, filepath: Path) -> dict[str, Any]:
        """
        Return metadata as a dict using ffprobe, or None on error.

        Args:
            filepath: Path to video file

        Returns:
            A dict containing the extracted metadata
        """
        cls.logger.debug(f"Extracting metadata from {filepath}")

        video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v"}
        if not filepath.is_file():
            cls.logger.error(f"Failed to extract metadata: {filepath} does not exist")
            return {}

        if filepath.suffix.lower() not in video_exts:
            cls.logger.error(f"Failed to extract metadata: {filepath} is not a video file")
            return {}

        try:
            command = [ffdl.ffprobe_path, "-v", "error", "-show_entries", "format:stream", "-of", "json", str(filepath)]

            cls.logger.debug(f"Running: {' '.join(command)}")
            result = sp.run(command, capture_output=True, encoding="utf-8", check=True)  # noqa: S603
            return cast(dict[str, Any], json.loads(result.stdout))

        except FileNotFoundError:
            cls.logger.exception(f"Failed to extract metadata: ffprobe command not found at {ffdl.ffprobe_path}")
            return {}

        except sp.CalledProcessError:
            cls.logger.exception("Failed to extract metadata: ffprobe command error")
            return {}

    @classmethod
    def get_tags(cls, filepath: Path) -> dict[str, str]:
        """
        Return tags as a dict using ffprobe, or None on error.

        Args:
            filepath: Path to video file

        Returns:
            A dict containing the extracted tags
        """
        cls.logger.debug(f"Extracting tags from {filepath}")

        metadata = cls.get_metadata(filepath)

        format: dict[str, Any] = metadata.get("format", {})  # noqa: A001
        tags: dict[str, str] = format.get("tags", {})
        return tags

    @classmethod
    def add_metadata(cls, filepath: Path, entries: dict[str, str]) -> None:
        """
        Add metadata to a video file with ffmpeg

        Args:
            filepath: Path to video file
            entries: Metadata entries to add
        """
        cls.logger.info(f"Adding metadata to {filepath}")

        video_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v"}
        if not filepath.is_file():
            cls.logger.error(f"Failed to add metadata: {filepath} does not exist")
            return None

        if filepath.suffix.lower() not in video_exts:
            cls.logger.error(f"Failed to add metadata: {filepath} is not a video file")
            return None

        original_filepath = filepath

        # 1. Create a temporary output file path
        # Use a temp directory in the same parent directory as the file for same-disk operation
        temp_dir = filepath.parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=filepath.suffix) as tmp:
            temp_filepath = Path(tmp.name)

            cls.logger.debug(f"Using temp file: {temp_filepath}")

            # 2. Preparing the ffmpeg command
            command = [
                ffdl.ffmpeg_path,
                "-v",
                "error",
                "-y",  # Overwrite output files without asking
                "-i",
                str(filepath),
            ]

            # Add all metadata options
            for key, value in entries.items():
                cls.logger.debug(f"Adding metadata: {key} = {value}")
                metadata_options = ["-metadata", f"{key}={value}"]
                command.extend(metadata_options)

            # Add copy codec and the temporary output file path
            # -c copy avoids re-encoding, making the process fast
            command.extend(["-c", "copy", str(temp_filepath)])

            # 3. Executing the ffmpeg command
            try:
                cls.logger.debug(f"Running FFmpeg: {' '.join(command)}")
                sp.run(command, check=True)  # noqa: S603

                # 4. If successful, replace the original file with the temporary file
                cls.logger.debug(f"FFmpeg successful. Overwriting {original_filepath} with {temp_filepath}")
                temp_filepath.replace(original_filepath)

            except FileNotFoundError:
                cls.logger.exception(f"Failed to add metadata: ffmpeg command not found at {ffdl.ffmpeg_path}")

            except sp.CalledProcessError:
                cls.logger.exception("Failed to add metadata: ffmpeg command error")

            except OSError:
                cls.logger.exception(
                    f"Failed to rename/replace the file: Could not move {temp_filepath} to {original_filepath}"
                )

            finally:
                # 5. Ensure the temporary file is deleted if it still exists (e.g., if os.replace failed)
                if temp_filepath.exists():
                    cls.logger.debug(f"Cleaning up un-renamed temp file: {temp_filepath}")
                    temp_filepath.unlink()

                # 6. Remove tempdir
                if temp_dir.is_dir():
                    temp_dir.rmdir()
