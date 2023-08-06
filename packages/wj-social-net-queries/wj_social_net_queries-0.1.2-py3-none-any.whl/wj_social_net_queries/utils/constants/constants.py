import os

from dotenv import load_dotenv

load_dotenv()

# Env variables
META_API_SECRET_KEY = os.getenv("META_API_SECRET_KEY", "")
META_APP_ID = os.getenv("META_APP_ID", "")
TOKEN = os.getenv("LONG_LIVE_TOKEN", "")

# API Operations
GET = "get"
POST = "post"
PATCH = "patch"
DELETE = "delete"

# OTHERS
DATA = "data"
ID = "id"
MEDIA_DIR = "downloaded_media"

# File types
JSON = "json"
CSV = "csv"
