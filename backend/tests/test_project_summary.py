from project_summary import scan_project, format_project_summary


def test_scan_project_counts_files_and_extensions(tmp_path):
    repo = tmp_path

    (repo / "README.md").write_text("# Test Project", encoding="utf-8")
    (repo / "main.py").write_text("print('hello')", encoding="utf-8")
    (repo / "requirements.txt").write_text("openai", encoding="utf-8")

    src = repo / "src"
    src.mkdir()
    (src / "app.js").write_text("console.log('hello')", encoding="utf-8")

    summary = scan_project(str(repo))

    assert summary["total_files"] == 4
    assert summary["extensions"][".py"] == 1
    assert summary["extensions"][".md"] == 1
    assert summary["extensions"][".txt"] == 1
    assert summary["extensions"][".js"] == 1
    assert "README.md" in summary["important_files"]
    assert "main.py" in summary["important_files"]
    assert "requirements.txt" in summary["important_files"]


def test_scan_project_ignores_venv(tmp_path):
    repo = tmp_path

    (repo / "main.py").write_text("print('hello')", encoding="utf-8")

    venv = repo / "venv"
    venv.mkdir()
    (venv / "ignored.py").write_text("print('ignore')", encoding="utf-8")

    summary = scan_project(str(repo))

    assert summary["total_files"] == 1


def test_format_project_summary_outputs_sections(tmp_path):
    repo = tmp_path

    (repo / "README.md").write_text("# Test Project", encoding="utf-8")
    summary = scan_project(str(repo))

    output = format_project_summary(summary)

    assert "Project Summary" in output
    assert "Supported files scanned" in output
    assert "File types" in output
    assert "Important files" in output