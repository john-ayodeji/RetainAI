import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]


def get_env(key: str, default=None):
	return os.getenv(key, default)


def model_artifact_path():
	return os.path.join(BASE_DIR, "ml", "artifacts", "model.pkl")


def feature_names_path():
	return os.path.join(BASE_DIR, "ml", "artifacts", "feature_names.json")


OPENAI_API_KEY = get_env("OPENAI_API_KEY")
GEMINI_API_KEY = get_env("GEMINI_API_KEY")
# The expected model resource name for the Generative Language API. Examples:
# models/gemini-1.5-mini or models/text-bison-001
GEMINI_MODEL = get_env("GEMINI_MODEL", "models/gemini-1.5-mini")
