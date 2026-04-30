# Codebase Nav Agent

Codebase Nav Agent is an LLM-powered developer tool that helps users understand unfamiliar codebases. It scans a local repository, indexes source files with embeddings, retrieves relevant code chunks, and answers natural-language questions with file-level citations.

## What It Does

Instead of manually searching through a project folder, users can ask questions like:

- What does this project do?
- What technologies does this project use?
- Where is authentication handled?
- Which files handle indexing and retrieval?
- How does the app use OpenAI?
- What files would I change to add a new feature?

The agent searches the codebase, finds relevant files, and generates an answer grounded in the actual source code.

## Example

Command:

    python main.py --repo .. --question "What technologies does this project use?"

Example answer:

    This project uses Python, the OpenAI API, ChromaDB, and python-dotenv.

    The OpenAI API is used to generate answers from retrieved code context.
    ChromaDB is used as the vector database for storing and searching embedded code chunks.
    python-dotenv is used to load the OpenAI API key from environment variables.

    Sources:
    - backend/llm.py
    - backend/retriever.py
    - backend/main.py
    - backend/requirements.txt

## Features

- Scans local code repositories
- Reads common source file types such as Python, JavaScript, TypeScript, HTML, CSS, Markdown, and JSON
- Ignores unnecessary folders like `.git`, `node_modules`, `venv`, and build folders
- Splits source files into smaller chunks with line ranges
- Stores code chunks in a local ChromaDB vector database
- Uses OpenAI embeddings to search relevant code
- Uses an OpenAI chat model to answer questions based on retrieved code
- Provides file references and line numbers in responses
- Shows retrieved sources before generating an answer
- Includes a no-cost tech stack detection command
- Includes a no-cost project summary command
- Includes a sample repository for testing

## Tech Stack

- Python
- OpenAI API
- ChromaDB
- python-dotenv
- Retrieval-Augmented Generation

## Project Structure

        Codebase-Nav-Agent/
            backend/
                main.py
                indexer.py
                retriever.py
                llm.py
                tech_stack.py
                project_summary.py
                requirements.txt
                .env.example
            sample_repo/
                README.md
                package.json
                src/
                App.jsx
                server/
                db.js
                routes/
                    auth.js
                middleware/
                    authMiddleware.js
            README.md
            .gitignore

## How It Works

1. The user provides a local repository path and a question.
2. The agent scans the repository for supported source files.
3. Source files are split into smaller chunks.
4. Each chunk is embedded using OpenAI embeddings.
5. Chunks are stored in a local ChromaDB vector database.
6. The user's question is used to retrieve the most relevant chunks.
7. The retrieved chunks are sent to an OpenAI chat model.
8. The model answers the question using only the retrieved code context.

## Setup

### 1. Clone the repository

    git clone https://github.com/MaximVak/Codebase-Nav-Agent.git
    cd Codebase-Nav-Agent/backend

### 2. Create a virtual environment

On Windows PowerShell:

    python -m venv venv
    venv\Scripts\Activate.ps1

On macOS/Linux:

    python -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Add your OpenAI API key

Create a `.env` file inside the `backend` folder:

    OPENAI_API_KEY=your_api_key_here

Do not commit your `.env` file to GitHub.

### 5. Run the agent

From inside the `backend` folder:

    python main.py --repo .. --question "What does this project do?" --fresh

The `--fresh` flag rebuilds the vector database from scratch.

After indexing once, you can ask more questions without `--fresh`:

    python main.py --repo .. --question "What technologies does this project use?"

    python main.py --repo .. --question "Which files handle indexing and retrieval?"

## Command Format

    python main.py --repo PATH_TO_REPO --question "Your question here" --fresh

Arguments:

- `--repo`: Path to the local codebase you want to analyze
- `--question`: Natural-language question about the codebase
- `--fresh`: Optional flag to rebuild the vector index

## Commands

### Ask a question about a codebase

    python main.py --repo PATH_TO_REPO --question "Your question here" --fresh

Use `--fresh` when indexing a repo for the first time or after files change.

Example:

    python main.py --repo ../sample_repo --question "Where is authentication handled?" --fresh

### Ask another question without re-indexing

    python main.py --repo ../sample_repo --question "What technologies does this project use?"

### Detect the tech stack without calling the LLM

    python main.py --repo ../sample_repo --tech-stack

Example output:

    Detected technology/configuration files:

    - package.json
      - bcrypt
      - express
      - jsonwebtoken
      - pg
      - react
      - vite

    - README.md
      - Project documentation

### Generate a project summary without calling the LLM

    python main.py --repo ../sample_repo --summary

Example output:

    Project Summary

    Supported files scanned: 6

    File types:
    - .js: 3
    - .jsx: 1
    - .json: 1
    - .md: 1

    Main directories:
    - server/: 3 supported files
    - src/: 1 supported files

    Important files:
    - README.md
    - package.json

## Example Questions

- What does this project do?
- What technologies does this project use?
- Where is authentication handled?
- How does the backend connect to the frontend?
- Which files would I modify to add a new feature?
- Explain the project architecture.

## Sample Repository

This project includes a small sample repository in `sample_repo/` so users can test the agent immediately.

The sample repo is a small task tracker app with:

- React frontend
- Express-style backend
- JWT authentication route
- JWT authentication middleware
- Simple user lookup database file

Example questions:

    python main.py --repo ../sample_repo --question "What does this sample project do?" --fresh

    python main.py --repo ../sample_repo --question "Where is authentication handled?"

    python main.py --repo ../sample_repo --tech-stack

## Current Limitations

- Runs as a command-line tool only
- Requires the user to provide their own OpenAI API key for LLM-powered questions
- Works best on small to medium-sized repositories
- Does not yet support uploaded ZIP files
- Does not yet include a web interface
- Does not yet separate indexes for multiple projects
- Retrieval quality depends on the files indexed and the wording of the question

## Roadmap

- Add unit tests for file scanning, chunking, tech stack detection, and project summary
- Add a license file
- Add better project-specific index storage
- Add FastAPI backend
- Add React frontend
- Support ZIP uploads
- Add safety limits for repo size, file size, and ignored sensitive files
- Add Docker support
- Deploy a hosted demo version

## Resume Description

Built an LLM-powered codebase navigation agent that indexes local software repositories, retrieves relevant source code using vector search, and answers natural-language questions with file-level citations using OpenAI and ChromaDB.

## License

MIT