import os

from dotenv import load_dotenv

load_dotenv()  # reads .env into os.environ (does nothing if .env is missing)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")              # original PDFs go here
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")  # cleaned text / chunks
CHROMA_DIR = os.path.join(DATA_DIR, "chroma")        # vector store (Day 6+)

EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"