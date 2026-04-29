import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


def get_collection(api_key: str):
    client = chromadb.PersistentClient(path="./chroma_db")

    embedding_function = OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )

    collection = client.get_or_create_collection(
        name="code_chunks",
        embedding_function=embedding_function
    )

    return collection


def index_chunks(collection, chunks):
    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk-{i}")
        documents.append(chunk["content"])
        metadatas.append({
            "file_path": chunk["file_path"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"]
        })

    if ids:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )


def is_documentation_file(file_path: str) -> bool:
    normalized_path = file_path.replace("\\", "/").lower()

    return (
        normalized_path.endswith(".md")
        or "readme" in normalized_path
        or normalized_path.endswith(".txt")
    )


def search_code(collection, question: str, n_results: int = 8):
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )

    matched_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        file_path = metadata["file_path"]

        matched_chunks.append({
            "content": doc,
            "file_path": file_path,
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"],
            "distance": distance,
            "is_documentation": is_documentation_file(file_path)
        })

    overview_keywords = [
        "what does this project do",
        "what is this project",
        "summarize",
        "overview",
        "purpose",
        "readme"
    ]

    is_overview_question = any(
        keyword in question.lower()
        for keyword in overview_keywords
    )

    if not is_overview_question:
        matched_chunks.sort(
            key=lambda chunk: (
                chunk["is_documentation"],
                chunk["distance"]
            )
        )
    else:
        matched_chunks.sort(
            key=lambda chunk: chunk["distance"]
        )

    return matched_chunks