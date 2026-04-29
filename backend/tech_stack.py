import json
from pathlib import Path


TECH_FILE_NAMES = {
    "requirements.txt",
    "package.json",
    "pyproject.toml",
    "Pipfile",
    "poetry.lock",
    "Dockerfile",
    "docker-compose.yml",
    "compose.yml",
    ".env.example",
    "README.md"
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


def should_ignore(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def find_tech_files(repo_path: str):
    repo = Path(repo_path)
    found_files = []

    for path in repo.rglob("*"):
        if path.is_file() and not should_ignore(path):
            if path.name in TECH_FILE_NAMES:
                found_files.append(path)

    return found_files


def read_file(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def detect_from_package_json(content: str):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    technologies = []

    dependencies = data.get("dependencies", {})
    dev_dependencies = data.get("devDependencies", {})

    all_dependencies = {
        **dependencies,
        **dev_dependencies
    }

    for package_name in all_dependencies:
        technologies.append(package_name)

    return technologies


def detect_from_requirements(content: str):
    technologies = []

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        package_name = (
            line.split("==")[0]
            .split(">=")[0]
            .split("<=")[0]
            .split("~=")[0]
            .split(">")[0]
            .split("<")[0]
            .strip()
        )

        if package_name:
            technologies.append(package_name)

    return technologies


def detect_tech_stack(repo_path: str):
    repo = Path(repo_path)
    results = []

    for path in find_tech_files(repo_path):
        content = read_file(path)

        if content is None:
            continue

        detected = []

        if path.name == "package.json":
            detected = detect_from_package_json(content)

        elif path.name == "requirements.txt":
            detected = detect_from_requirements(content)

        elif path.name == "Dockerfile":
            detected = ["Docker"]

        elif path.name in {"docker-compose.yml", "compose.yml"}:
            detected = ["Docker Compose"]

        elif path.name == ".env.example":
            detected = ["Environment variables"]

        elif path.name == "pyproject.toml":
            detected = ["Python project configuration"]

        elif path.name == "README.md":
            detected = ["Project documentation"]

        results.append({
            "file": str(path.relative_to(repo)),
            "technologies": detected
        })

    return results


def format_tech_stack(results):
    if not results:
        return "No common dependency or configuration files were found."

    output = ["Detected technology/configuration files:"]

    for item in results:
        output.append(f"\n- {item['file']}")

        if item["technologies"]:
            for tech in item["technologies"]:
                output.append(f"  - {tech}")
        else:
            output.append("  - Found, but no technologies were automatically detected.")

    return "\n".join(output)