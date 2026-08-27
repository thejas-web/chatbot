from pathlib import Path
import os
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(Path(__file__).resolve().parent / ".env")

# Resolve the project root (one level up from this file's directory)
BASE_DIR = Path(__file__).resolve().parent.parent

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 800

CHUNK_OVERLAP = 100

TOP_K = 5


SITE_ROOT = "https://www.webenza.com"
SITEMAP_URL = "https://www.webenza.com/sitemap.xml"
ROBOTS_URL = "https://www.webenza.com/robots.txt"

OUTPUT_DIR = BASE_DIR / "scraped_pages"
ALL_PAGES_JSON = OUTPUT_DIR / "_all_pages.json"

VECTOR_STORE_DIR = str(BASE_DIR / "data" / "vector_store")

groq_api_key = os.getenv("GROQ_API_KEY")

SIMLI_API_KEY = os.getenv('SIMLI_API_KEY')
SIMLI_FACE_ID = os.getenv('SIMLI_FACE_ID')
