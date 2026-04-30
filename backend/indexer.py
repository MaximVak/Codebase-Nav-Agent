from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".cpp", ".c", ".h", ".cs",
    ".html", ".css", ".md", ".json", ".txt", ".toml", ".yml", ".yaml"
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".next",
    "venv",
    ".venv",
    "chroma_db",
    "tests",
    ".pytest_cache"
}

IGNORED_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
    "secrets.json",
    "credentials.json",
    "id_rsa",
    "id_rsa.pub"
}

MAX_FILE_SIZE_BYTES = 200_000
MAX_FILES_TO_INDEX = 500


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def is_secret_file(path: Path) -> bool:
    return path.name in IGNORED_FILE_NAMES


def is_allowed_file(path: Path) -> bool:
    return path.suffix in ALLOWED_EXTENSIONS


def read_code_files(repo_path: str):
    repo = Path(repo_path)
    files = []
    skipped = {
        "ignored_dirs": 0,
        "unsupported_extensions": 0,
        "secret_files": 0,
        "too_large": 0,
        "decode_errors": 0,
        "file_limit_reached": 0
    }

    for path in repo.rglob("*"):
        if len(files) >= MAX_FILES_TO_INDEX:
            skipped["file_limit_reached"] += 1
            break

        if not path.is_file():
            continue

        if should_ignore(path):
            skipped["ignored_dirs"] += 1
            continue

        if is_secret_file(path):
            skipped["secret_files"] += 1
            continue

        if not is_allowed_file(path):
            skipped["unsupported_extensions"] += 1
            continue

        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            skipped["too_large"] += 1
            continue

        try:
            text = path.read_text(encoding="utf-8")
            files.append({
                "path": path.relative_to(repo).as_posix(),
                "content": text
            })
        except UnicodeDecodeError:
            skipped["decode_errors"] += 1

    return files, skipped


def chunk_text(text: str, max_lines: int = 80):
    lines = text.splitlines()
    chunks = []

    for i in range(0, len(lines), max_lines):
        chunk_lines = lines[i:i + max_lines]

        chunks.append({
            "content": "\n".join(chunk_lines),
            "start_line": i + 1,
            "end_line": i + len(chunk_lines)
        })

    return chunks


def create_chunks(repo_path: str):
    files, skipped = read_code_files(repo_path)
    all_chunks = []

    for file in files:
        chunks = chunk_text(file["content"])

        for chunk in chunks:
            if chunk["content"].strip():
                all_chunks.append({
                    "file_path": file["path"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "content": chunk["content"]
                })

    return all_chunks, skipped