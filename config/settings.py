import os
from pathlib import Path
from dotenv import load_dotenv


def load_env() -> None:
	"""Load environment variables from a .env file if present."""
	# Load from repo root .env
	repo_root = Path(__file__).resolve().parents[1]
	env_path = repo_root / ".env"
	# Load only once; subsequent calls are cheap and safe
	load_dotenv(dotenv_path=env_path, override=False)


# Load at import time so tests/scripts see env immediately
load_env()

# API keys (read once at import)
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

# Storage and app settings
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "storage/chroma")
DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Paris")


def require_env(value: str | None, name: str) -> str:
	"""Return value or raise a helpful error if missing."""
	if not value:
		raise ValueError(f"Missing env var: {name}. Check your .env and settings.")
	return value
