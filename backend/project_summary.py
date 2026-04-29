from collections import Counter
from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".cpp", ".c", ".h", ".cs",
    ".html", ".css", ".md", ".json", ".txt", ".toml", ".yml", ".yaml", ".example"
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
    "chroma_db"
}

IMPORTANT_FILE_NAMES = {
    "README.md",
    "requirements.txt",
    "package.json",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    "compose.yml",
    ".env.example",
    "main.py",
    "app.py",
    "server.js",
    "index.js",
    "index.ts"
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def scan_project(repo_path: str):
    repo = Path(repo_path)
    files = []
    directories = Counter()
    extensions = Counter()
    important_files = []

    for path in repo.rglob("*"):
        if should_ignore(path):
            continue

        if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS:
            relative_path = path.relative_to(repo)
            files.append(relative_path)

            if path.suffix:
                extensions[path.suffix] += 1

            if path.name in IMPORTANT_FILE_NAMES:
                important_files.append(relative_path)

            parts = relative_path.parts
            if len(parts) > 1:
                directories[parts[0]] += 1

    return {
        "total_files": len(files),
        "extensions": extensions,
        "important_files": important_files,
        "directories": directories
    }


def format_project_summary(summary):
    output = ["Project Summary"]

    output.append(f"\nSupported files scanned: {summary['total_files']}")

    output.append("\nFile types:")
    if summary["extensions"]:
        for extension, count in summary["extensions"].most_common():
            output.append(f"- {extension}: {count}")
    else:
        output.append("- No supported source files found.")

    output.append("\nMain directories:")
    if summary["directories"]:
        for directory, count in summary["directories"].most_common(10):
            output.append(f"- {directory}/: {count} supported files")
    else:
        output.append("- No major subdirectories found.")

    output.append("\nImportant files:")
    if summary["important_files"]:
        for file_path in summary["important_files"][:15]:
            output.append(f"- {file_path}")
    else:
        output.append("- No common important files found.")

    return "\n".join(output)