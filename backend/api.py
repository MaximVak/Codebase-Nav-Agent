import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from indexer import create_chunks
from retriever import get_collection, index_chunks, search_code, reset_collection
from llm import answer_question
from tech_stack import detect_tech_stack, format_tech_stack
from project_summary import scan_project, format_project_summary


load_dotenv()

app = FastAPI(
    title="Codebase Nav Agent API",
    description="API for asking natural-language questions about local codebases.",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    repo_path: str
    question: str
    fresh: bool = False


class UtilityRequest(BaseModel):
    repo_path: str


class AskResponse(BaseModel):
    answer: str
    retrieved_sources: list[str]
    chunks_created: int
    skipped: dict


class UtilityResponse(BaseModel):
    result: str


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Codebase Nav Agent API"
    }


@app.get("/")
def root():
    return {
        "message": "Codebase Nav Agent API is running.",
        "docs": "/docs"
    }


@app.post("/summary", response_model=UtilityResponse)
def get_summary(request: UtilityRequest):
    summary = scan_project(request.repo_path)

    return {
        "result": format_project_summary(summary)
    }


@app.post("/tech-stack", response_model=UtilityResponse)
def get_tech_stack(request: UtilityRequest):
    results = detect_tech_stack(request.repo_path)

    return {
        "result": format_tech_stack(results)
    }


@app.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing OPENAI_API_KEY. Create a .env file inside backend/."
        )

    chunks, skipped = create_chunks(request.repo_path)

    if request.fresh:
        collection = reset_collection(api_key, request.repo_path)
        index_chunks(collection, chunks)
    else:
        collection = get_collection(api_key, request.repo_path)

    matched_chunks = search_code(collection, request.question)

    retrieved_sources = []

    seen_files = set()
    max_sources = 5

    for chunk in matched_chunks:
        file_path = chunk["file_path"]

        if file_path not in seen_files:
            seen_files.add(file_path)
            retrieved_sources.append(
                f"{file_path}, lines {chunk['start_line']}-{chunk['end_line']}"
            )

        if len(seen_files) >= max_sources:
            break

    answer = answer_question(api_key, request.question, matched_chunks)

    return {
        "answer": answer,
        "retrieved_sources": retrieved_sources,
        "chunks_created": len(chunks),
        "skipped": skipped
    }