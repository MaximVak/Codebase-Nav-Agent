import { useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [repoPath, setRepoPath] = useState("../sample_repo");
  const [question, setQuestion] = useState("Where is authentication handled?");
  const [fresh, setFresh] = useState(true);

  const [summaryOutput, setSummaryOutput] = useState("");
  const [techStackOutput, setTechStackOutput] = useState("");
  const [answerOutput, setAnswerOutput] = useState("");
  const [sources, setSources] = useState([]);

  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [loadingAction, setLoadingAction] = useState("");

  const isLoading = Boolean(loadingAction);

  function resetMessages() {
    setStatusMessage("");
    setErrorMessage("");
  }

  function getFriendlyError(error) {
    if (error.message === "Failed to fetch") {
      return "Could not connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000.";
    }

    return error.message;
  }

  async function callApi(endpoint, body, actionName) {
    setLoadingAction(actionName);
    resetMessages();

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
      setErrorMessage(getFriendlyError(error));
      return null;
    } finally {
      setLoadingAction("");
    }
  }

  async function handleUpload(event) {
    const file = event.target.files[0];

    if (!file) {
      return;
    }

    resetMessages();

    if (!file.name.endsWith(".zip")) {
      setErrorMessage("Please upload a .zip file.");
      return;
    }

    setLoadingAction("upload");
    setSources([]);
    setAnswerOutput("");

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
      setStatusMessage(`Upload complete. Repository path set to: ${data.repo_path}`);
    } catch (error) {
      setErrorMessage(getFriendlyError(error));
    } finally {
      setLoadingAction("");
      event.target.value = "";
    }
  }

  async function handleSummary() {
    const data = await callApi(
      "/summary",
      { repo_path: repoPath },
      "summary"
    );

    if (data) {
      setSummaryOutput(data.result);
      setStatusMessage("Project summary generated.");
    }
  }

  async function handleTechStack() {
    const data = await callApi(
      "/tech-stack",
      { repo_path: repoPath },
      "tech-stack"
    );

    if (data) {
      setTechStackOutput(data.result);
      setStatusMessage("Tech stack detected.");
    }
  }

  async function handleAsk() {
    const data = await callApi(
      "/ask",
      {
        repo_path: repoPath,
        question,
        fresh
      },
      "ask"
    );

    if (data) {
      setAnswerOutput(data.answer);
      setSources(data.retrieved_sources || []);
      setStatusMessage(`Answer generated from ${data.chunks_created} indexed chunks.`);
    }
  }

  function getButtonText(action, label) {
    return loadingAction === action ? "Loading..." : label;
  }

  return (
    <main className="app">
      <section className="hero">
        <p className="eyebrow">LLM Developer Tool</p>
        <h1>Codebase Nav Agent</h1>
        <p className="subtitle">
          Upload a zipped codebase or enter a local repo path, then ask questions
          and get grounded answers with source references.
        </p>
      </section>

      <section className="panel">
        <div className="section-heading">
          <h2>Repository</h2>
          <p>Use the included sample repo, enter a local path, or upload a ZIP file.</p>
        </div>

        <label>
          Upload zipped codebase
          <input
            type="file"
            accept=".zip"
            onChange={handleUpload}
            disabled={isLoading}
          />
        </label>

        <label>
          Repository path
          <input
            value={repoPath}
            onChange={(event) => setRepoPath(event.target.value)}
            placeholder="../sample_repo"
            disabled={isLoading}
          />
        </label>

        <div className="button-row">
          <button onClick={handleSummary} disabled={isLoading || !repoPath.trim()}>
            {getButtonText("summary", "Project Summary")}
          </button>

          <button onClick={handleTechStack} disabled={isLoading || !repoPath.trim()}>
            {getButtonText("tech-stack", "Tech Stack")}
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <h2>Ask a Question</h2>
          <p>The answer is generated from retrieved source-code chunks.</p>
        </div>

        <label>
          Question
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Where is authentication handled?"
            rows={4}
            disabled={isLoading}
          />
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={fresh}
            onChange={(event) => setFresh(event.target.checked)}
            disabled={isLoading}
          />
          Re-index before asking
        </label>

        <button onClick={handleAsk} disabled={isLoading || !repoPath.trim() || !question.trim()}>
          {getButtonText("ask", "Ask Codebase")}
        </button>
      </section>

      {(statusMessage || errorMessage || isLoading) && (
        <section className={`notice ${errorMessage ? "error" : "success"}`}>
          {isLoading && <p>Running {loadingAction}...</p>}
          {statusMessage && !isLoading && <p>{statusMessage}</p>}
          {errorMessage && <p>{errorMessage}</p>}
        </section>
      )}

      <section className="results-grid">
        <article className="panel output-card">
          <h2>Project Summary</h2>
          <pre>{summaryOutput || "Run Project Summary to see an overview here."}</pre>
        </article>

        <article className="panel output-card">
          <h2>Tech Stack</h2>
          <pre>{techStackOutput || "Run Tech Stack to see detected technologies here."}</pre>
        </article>

        <article className="panel output-card full-width">
          <h2>Answer</h2>
          <pre>{answerOutput || "Ask a codebase question to see the answer here."}</pre>

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
        </article>
      </section>
    </main>
  );
}

export default App;