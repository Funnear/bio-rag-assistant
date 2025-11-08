from pathlib import Path
import json
import hashlib
from enum import Enum

class KBState(str, Enum):
    NO_DATA = "no_data"       # no PDFs at all
    EMPTY = "empty"           # PDFs exist, none processed
    UP_TO_DATE = "up_to_date" # all PDFs processed
    OUTDATED = "outdated"     # some PDFs new/changed

def compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Return hex SHA256 hash of file contents."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

def load_metadata(metadata_path: Path) -> dict[str, str]:
    """Return mapping {relative_filename: hash}."""
    if not metadata_path.exists():
        return {}
    try:
        with metadata_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("files", {})
    except Exception:
        # Corrupt/empty file → treat as no metadata
        return {}

def save_metadata(metadata_path: Path, files_map: dict[str, str]) -> None:
    metadata = {"files": files_map}
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

def detect_kb_state(datasets_dir: Path, metadata_path: Path):
    """
    Inspect PDFs in datasets_dir and metadata file.
    Return (state, info_dict) where info_dict contains counts and file lists.
    """
    # 1) Filesystem: find all PDFs
    pdf_paths = sorted(datasets_dir.glob("*.pdf"))
    total_pdfs = len(pdf_paths)

    # 2) Metadata: known {name -> hash}
    meta_map = load_metadata(metadata_path)

    if total_pdfs == 0 and not meta_map:
        return KBState.NO_DATA, {
            "total_pdfs": 0,
            "processed": 0,
            "new_files": [],
            "changed_files": [],
        }

    # Build current hashes
    current_map: dict[str, str] = {}
    for pdf in pdf_paths:
        rel_name = pdf.name  # simple: just filename
        current_map[rel_name] = compute_file_hash(pdf)

    # Determine categories
    processed = []
    new_files = []
    changed_files = []

    for name, cur_hash in current_map.items():
        old_hash = meta_map.get(name)
        if old_hash is None:
            new_files.append(name)
        elif old_hash != cur_hash:
            changed_files.append(name)
        else:
            processed.append(name)

    if total_pdfs == 0:
        # Has metadata but no files → weird, treat as empty
        state = KBState.EMPTY
    elif not processed and (new_files or changed_files):
        # PDFs exist, none processed
        state = KBState.EMPTY
    elif not (new_files or changed_files):
        state = KBState.UP_TO_DATE
    else:
        state = KBState.OUTDATED

    info = {
        "total_pdfs": total_pdfs,
        "processed": len(processed),
        "processed_files": processed,
        "new_files": new_files,
        "changed_files": changed_files,
    }
    return state, info

