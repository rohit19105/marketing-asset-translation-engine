import os

from dotenv import load_dotenv

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUTS_DIR = os.path.join(DATA_DIR, "outputs")
TRANSLATION_JOBS_DIR = os.path.join(DATA_DIR, "translation_jobs")
ASSETS_DIR = os.path.join(DATA_DIR, "assets")
GLOSSARY_DIR = os.path.join(DATA_DIR, "glossary")
TRANSLATION_MEMORY_DIR = os.path.join(DATA_DIR, "translation_memory")

GLOSSARY_PATH = os.path.join(GLOSSARY_DIR, "glossary.xlsx")
TM_PATH = os.path.join(TRANSLATION_MEMORY_DIR, "tm.json")

ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(ENV_PATH, override=True)


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
