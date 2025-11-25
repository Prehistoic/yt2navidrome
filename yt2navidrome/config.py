import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Misc
PROJECT_NAME = "yt2navidrome"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# YT-DLP Options
DENO_INSTALL_DIR = os.path.join(os.path.expanduser("~"), ".deno")
