import argparse
import os
from dotenv import load_dotenv

from indexer import create_chunks
from retriever import get_collection, index_chunks, search_code, reset_collection
from llm import answer_question
from tech_stack import detect_tech_stack, format_tech_stack
from project_summary import scan_project, format_project_summary
from upload_manager import cleanup_uploads

def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

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

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show a quick non-LLM project summary."
    )

    parser.add_argument(
        "--cleanup-uploads",
        action="store_true",
        help="Delete uploaded ZIPs and extracted repositories."
    )

    args = parser.parse_args()

    if args.cleanup_uploads:
        removed = cleanup_uploads()
        print("Uploaded ZIPs and extracted repositories cleaned up.")
        print(f"Uploads removed: {removed['uploads_removed']}")
        print(f"Extracted repos removed: {removed['extracted_repos_removed']}")
        return

    if args.tech_stack:
        results = detect_tech_stack(args.repo)
        print(format_tech_stack(results))
        return

    if args.summary:
        summary = scan_project(args.repo)
        print(format_project_summary(summary))
        return

    if not args.question:
        parser.error("Please provide --question, --tech-stack, --summary, or --cleanup-uploads.")

    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY. Create a .env file inside backend/.")

    print("Reading and chunking files...")
    chunks, skipped = create_chunks(args.repo)
    print(f"Created {len(chunks)} chunks.")

    skipped_items = {
        reason: count
        for reason, count in skipped.items()
        if count > 0
    }

    if skipped_items:
        print("\nIndexing safety summary:")
        for reason, count in skipped_items.items():
            print(f"- {reason}: {count}")

    if args.fresh:
        collection = reset_collection(api_key, args.repo)
        print("Indexing chunks...")
        index_chunks(collection, chunks)
    else:
        collection = get_collection(api_key, args.repo)

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