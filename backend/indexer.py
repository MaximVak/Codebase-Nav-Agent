from pathlib import Path

ALLOWED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".cpp", ".c", ".h", ".cs",
    ".html", ".css", ".md", ".json"
}

IGNORED_DIRS = {
    ".git", "node_modules", "dist", "build", "__pycache__",
    ".next", "venv", ".venv", "chroma_db"
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def read_code_files(repo_path: str):
    repo = Path(repo_path)
    files = []

    for path in repo.rglob("*"):
        if path.is_file() and not should_ignore(path):
            if path.suffix in ALLOWED_EXTENSIONS:
                try:
                    text = path.read_text(encoding="utf-8")
                    files.append({
                        "path": path.relative_to(repo).as_posix(),
                        "content": text
})
                except UnicodeDecodeError:
                    continue

    return files


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
    files = read_code_files(repo_path)
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

    return all_chunks