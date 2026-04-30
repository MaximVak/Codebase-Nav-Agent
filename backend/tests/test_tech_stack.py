from tech_stack import detect_tech_stack, format_tech_stack


def test_detect_tech_stack_from_requirements(tmp_path):
    repo = tmp_path

    requirements = repo / "requirements.txt"
    requirements.write_text(
        "openai\nchromadb==0.5.0\npython-dotenv>=1.0.0\n",
        encoding="utf-8"
    )

    results = detect_tech_stack(str(repo))

    assert len(results) == 1
    assert results[0]["file"] == "requirements.txt"
    assert "openai" in results[0]["technologies"]
    assert "chromadb" in results[0]["technologies"]
    assert "python-dotenv" in results[0]["technologies"]


def test_detect_tech_stack_from_package_json(tmp_path):
    repo = tmp_path

    package_json = repo / "package.json"
    package_json.write_text(
        """
        {
          "dependencies": {
            "react": "^18.2.0",
            "express": "^4.18.2"
          },
          "devDependencies": {
            "vite": "^5.0.0"
          }
        }
        """,
        encoding="utf-8"
    )

    results = detect_tech_stack(str(repo))

    technologies = results[0]["technologies"]

    assert "react" in technologies
    assert "express" in technologies
    assert "vite" in technologies


def test_format_tech_stack_handles_empty_results():
    output = format_tech_stack([])

    assert "No common dependency or configuration files were found." in output