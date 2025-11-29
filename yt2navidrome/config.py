import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Misc
PROJECT_NAME = "yt2navidrome"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_NAME, "data")

# YT-DLP Options
COOKIE_FILE_PATH = os.path.join(DATA_DIR, "cookies.txt")
CONSECUTIVE_DOWNLOADS_SLEEP_TIME = 10

# FFMpeg Options
FFMPEG_URL_WINDOWS = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
ALLOWED_METADATA_INPUTS = ["title", "uploader"]

# Default Song Metadata Values
DEFAULT_TITLE = "Untitled"
DEFAULT_ARTIST = "Unknown Artist"
DEFAULT_ALBUM = "Unknown Album"
DEFAULT_TRACK_NUMBER = "0"
