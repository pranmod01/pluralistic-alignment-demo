import os

# Read OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Local SQLite DB path
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.environ.get("PLURALITY_DB_PATH") or os.path.join(BASE_DIR, "data.sqlite")

# GPT model to use (may be adjusted)
GPT_MODEL = os.environ.get("GPT_MODEL") or "gpt-3.5-turbo"
