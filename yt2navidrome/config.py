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
