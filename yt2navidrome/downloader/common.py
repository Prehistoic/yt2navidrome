import glob
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def check_if_already_downloaded(base_directory: Path, video_id: str) -> bool:
    """
    Checks if any directory whose name is the video_id exists recursively
    under the base_directory.

    Args:
        base_directory: The root directory to start the search from.
        video_id: The ID string to search for (e.g., '12345').

    Returns:
        True if at least one matching directory is found, False otherwise.
    """
    pattern = str(base_directory / "**" / video_id)
    first_match = next((m for m in glob.iglob(pattern, recursive=True) if Path(m).is_dir()), None)
    return first_match is not None


def extract_video_id_from_url(video_url: str) -> str | None:
    """Extract YouTube video ID from URL."""
    parsed_url = urlparse(video_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("v", [None])[0]
