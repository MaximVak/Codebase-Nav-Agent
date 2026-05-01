import { useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [repoPath, setRepoPath] = useState("../sample_repo");
  const [question, setQuestion] = useState("Where is authentication handled?");
  const [fresh, setFresh] = useState(true);
  const [output, setOutput] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  async function callApi(endpoint, body) {
    setLoading(true);
    setOutput("");
    setSources([]);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong.");
      }

      return data;
    } catch (error) {
      setOutput(`Error: ${error.message}`);
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event) {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    if (!file.name.endsWith(".zip")) {
      setUploadMessage("Please upload a .zip file.");
      return;
    }

    setLoading(true);
    setOutput("");
    setSources([]);
    setUploadMessage("Uploading and extracting ZIP...");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setRepoPath(data.repo_path);
      setUploadMessage(`Upload complete. Repo path set to: ${data.repo_path}`);
      setOutput("ZIP uploaded successfully. You can now run Summary, Tech Stack, or Ask Codebase.");
    } catch (error) {
      setUploadMessage("");
      setOutput(`Error: ${error.message}`);
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  }

  async function handleSummary() {
    const data = await callApi("/summary", {
      repo_path: repoPath
    });

    if (data) {
      setOutput(data.result);
    }
  }

  async function handleTechStack() {
    const data = await callApi("/tech-stack", {
      repo_path: repoPath
    });

    if (data) {
      setOutput(data.result);
    }
  }

  async function handleAsk() {
    const data = await callApi("/ask", {
      repo_path: repoPath,
      question,
      fresh
    });

    if (data) {
      setOutput(data.answer);
      setSources(data.retrieved_sources || []);
    }
  }

  return (
    <main className="app">
      <section className="hero">
        <p className="eyebrow">LLM Developer Tool</p>
        <h1>Codebase Nav Agent</h1>
        <p className="subtitle">
          Ask natural-language questions about a local codebase and get grounded answers with source references.
        </p>
      </section>

      <section className="panel">
        <label>
          Upload a zipped codebase
          <input
            type="file"
            accept=".zip"
            onChange={handleUpload}
            disabled={loading}
          />
        </label>

        {uploadMessage && <p className="upload-message">{uploadMessage}</p>}

        <label>
          Repository path
          <input
            value={repoPath}
            onChange={(event) => setRepoPath(event.target.value)}
            placeholder="../sample_repo"
          />
        </label>

        <div className="button-row">
          <button onClick={handleSummary} disabled={loading}>
            Project Summary
          </button>

          <button onClick={handleTechStack} disabled={loading}>
            Tech Stack
          </button>
        </div>
      </section>

      <section className="panel">
        <label>
          Question
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Where is authentication handled?"
            rows={4}
          />
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={fresh}
            onChange={(event) => setFresh(event.target.checked)}
          />
          Re-index before asking
        </label>

        <button onClick={handleAsk} disabled={loading || !question.trim()}>
          Ask Codebase
        </button>
      </section>

      <section className="panel output-panel">
        <h2>Output</h2>

        {loading ? (
          <p className="muted">Loading...</p>
        ) : (
          <pre>{output || "Run a command to see output here."}</pre>
        )}

        {sources.length > 0 && (
          <div className="sources">
            <h3>Retrieved Sources</h3>
            <ul>
              {sources.map((source) => (
                <li key={source}>{source}</li>
              ))}
            </ul>
          </div>
        )}
      </section>
    </main>
  );
}

export default App;