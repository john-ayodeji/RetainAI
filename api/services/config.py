import os
from pathlib import Path

# load .env early so environment-backed config values are available at import-time
BASE_DIR = Path(__file__).resolve().parents[2]
try:
	# optional dependency, only used to load a .env file during local/dev runs
	from dotenv import load_dotenv

	env_path = BASE_DIR / ".env"
	if env_path.exists():
		load_dotenv(env_path)
except Exception:
	# python-dotenv not installed or load failed; fall back to process env
	pass


def get_env(key: str, default=None):
	return os.getenv(key, default)


def model_artifact_path():
	return os.path.join(BASE_DIR, "ml", "artifacts", "model.pkl")


def feature_names_path():
	return os.path.join(BASE_DIR, "ml", "artifacts", "feature_names.json")

# OPENAI_API_KEY = get_env("OPENAI_API_KEY")
# OPENAI_API_KEY = get_env("OPENAI_API_KEY")
# GEMINI_API_KEY = get_env("GEMINI_API_KEY")
# GEMINI_MODEL = "gemini-2.0-flash"

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL   = os.getenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it:free")
OPENROUTER_REFERER = os.getenv("OPENROUTER_REFERER", "http://localhost") 