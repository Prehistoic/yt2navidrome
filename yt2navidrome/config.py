from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Misc
PROJECT_NAME = "yt2navidrome"
PROJECT_ROOT = Path(__file__).parent
