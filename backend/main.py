import argparse
import os
import shutil
from dotenv import load_dotenv


from indexer import create_chunks
from retriever import get_collection, index_chunks, search_code
from llm import answer_question
from tech_stack import detect_tech_stack, format_tech_stack


def reset_chroma_db():
    if os.path.exists("./chroma_db"):
        shutil.rmtree("./chroma_db")


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY. Create a .env file inside backend/.")

    parser = argparse.ArgumentParser(
        description="Codebase Nav Agent: ask questions about a local codebase."
    )

    parser.add_argument(
        "--repo",
        required=True,
        help="Path to the codebase folder you want to analyze."
    )

    parser.add_argument(
        "--question",
        required=False,
        help="Question to ask about the codebase."
    )

    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Re-index the repo from scratch."
    )

    parser.add_argument(
        "--tech-stack",
        action="store_true",
        help="Detect common technologies and configuration files in the repo."
    )

    args = parser.parse_args()

    if args.tech_stack:
        results = detect_tech_stack(args.repo)
        print(format_tech_stack(results))
        return

    if not args.question:
        parser.error("Please provide --question, or use --tech-stack.")

    if args.fresh:
        reset_chroma_db()

    print("Reading and chunking files...")
    chunks = create_chunks(args.repo)
    print(f"Created {len(chunks)} chunks.")

    collection = get_collection(api_key)

    if args.fresh:
        print("Indexing chunks...")
        index_chunks(collection, chunks)

    print("Searching relevant code...")
    matched_chunks = search_code(collection, args.question)

    print("\nRetrieved sources:")
    seen_files = set()
    max_sources = 5

    for chunk in matched_chunks:
        file_path = chunk["file_path"]

        if file_path not in seen_files:
            seen_files.add(file_path)
            print(f"- {file_path}, lines {chunk['start_line']}-{chunk['end_line']}")

        if len(seen_files) >= max_sources:
            break

    print("\nAsking LLM...")
    answer = answer_question(api_key, args.question, matched_chunks)

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()