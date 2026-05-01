import shutil
from pathlib import Path


UPLOAD_DIR = Path("uploads")
EXTRACTED_REPOS_DIR = Path("extracted_repos")


def ensure_upload_dirs():
    UPLOAD_DIR.mkdir(exist_ok=True)
    EXTRACTED_REPOS_DIR.mkdir(exist_ok=True)


def cleanup_uploads():
    removed = {
        "uploads_removed": False,
        "extracted_repos_removed": False
    }

    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
        removed["uploads_removed"] = True

    if EXTRACTED_REPOS_DIR.exists():
        shutil.rmtree(EXTRACTED_REPOS_DIR)
        removed["extracted_repos_removed"] = True

    ensure_upload_dirs()

    return removed