import upload_manager


def test_cleanup_uploads_removes_and_recreates_dirs(tmp_path, monkeypatch):
    uploads_dir = tmp_path / "uploads"
    extracted_dir = tmp_path / "extracted_repos"

    uploads_dir.mkdir()
    extracted_dir.mkdir()

    (uploads_dir / "test.zip").write_text("fake zip", encoding="utf-8")
    (extracted_dir / "file.py").write_text("print('hello')", encoding="utf-8")

    monkeypatch.setattr(upload_manager, "UPLOAD_DIR", uploads_dir)
    monkeypatch.setattr(upload_manager, "EXTRACTED_REPOS_DIR", extracted_dir)

    result = upload_manager.cleanup_uploads()

    assert result["uploads_removed"] is True
    assert result["extracted_repos_removed"] is True

    assert uploads_dir.exists()
    assert extracted_dir.exists()

    assert list(uploads_dir.iterdir()) == []
    assert list(extracted_dir.iterdir()) == []