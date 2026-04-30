from pathlib import Path

from indexer import create_chunks, read_code_files, chunk_text


def test_chunk_text_splits_lines():
    text = "\n".join([f"line {i}" for i in range(1, 101)])

    chunks = chunk_text(text, max_lines=40)

    assert len(chunks) == 3
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 40
    assert chunks[1]["start_line"] == 41
    assert chunks[1]["end_line"] == 80
    assert chunks[2]["start_line"] == 81
    assert chunks[2]["end_line"] == 100


def test_read_code_files_ignores_unwanted_dirs(tmp_path):
    repo = tmp_path

    good_file = repo / "app.py"
    good_file.write_text("print('hello')", encoding="utf-8")

    ignored_dir = repo / "node_modules"
    ignored_dir.mkdir()
    ignored_file = ignored_dir / "ignored.js"
    ignored_file.write_text("console.log('ignore')", encoding="utf-8")

    files, skipped = read_code_files(str(repo))

    file_paths = [file["path"] for file in files]

    assert "app.py" in file_paths
    assert "node_modules/ignored.js" not in file_paths
    assert skipped["ignored_dirs"] >= 1


def test_create_chunks_includes_file_metadata(tmp_path):
    repo = tmp_path

    code_file = repo / "main.py"
    code_file.write_text("def hello():\n    return 'world'\n", encoding="utf-8")

    chunks, skipped = create_chunks(str(repo))

    assert len(chunks) == 1
    assert chunks[0]["file_path"] == "main.py"
    assert chunks[0]["start_line"] == 1
    assert chunks[0]["end_line"] == 2
    assert "def hello" in chunks[0]["content"]
    assert skipped["secret_files"] == 0

def test_read_code_files_ignores_secret_files(tmp_path):
    repo = tmp_path

    secret_file = repo / ".env"
    secret_file.write_text("OPENAI_API_KEY=secret", encoding="utf-8")

    good_file = repo / "main.py"
    good_file.write_text("print('safe')", encoding="utf-8")

    files, skipped = read_code_files(str(repo))
    file_paths = [file["path"] for file in files]

    assert "main.py" in file_paths
    assert ".env" not in file_paths
    assert skipped["secret_files"] == 1