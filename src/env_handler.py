from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]  # project root

def load_paths():
    """Load dataset/chroma/metadata paths from .env, with sensible defaults."""
    # Ensure .env is loaded (if present)
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        # Load environment variables from .env file
        # LangChain gets OPENAI_API_KEY from here
        load_dotenv(env_path)
    # TODO: catch file does not exist and pass to the GUI later

    # Defaults inside project root
    default_datasets = BASE_DIR / "datasets"
    default_chroma = BASE_DIR / ".chroma_db"
    default_metadata = BASE_DIR / "kb_metadata.json"

    datasets_dir = Path(os.getenv("DATASETS_DIR") or default_datasets).expanduser()
    chroma_dir = Path(os.getenv("CHROMA_DB_DIR") or default_chroma).expanduser()
    metadata_path = Path(os.getenv("KB_METADATA_PATH") or default_metadata).expanduser()

    # Ensure datasets folder exists; do NOT touch Chroma folder yet
    datasets_dir.mkdir(parents=True, exist_ok=True)

    return datasets_dir, chroma_dir, metadata_path

