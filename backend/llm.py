from openai import OpenAI


def answer_question(api_key: str, question: str, chunks):
    client = OpenAI(api_key=api_key)

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"""
File: {chunk["file_path"]}
Lines: {chunk["start_line"]}-{chunk["end_line"]}
Code:
{chunk["content"]}
"""
        )

    context = "\n---\n".join(context_parts)

    prompt = f"""
You are an AI codebase navigation assistant.

Answer the user's question using only the provided code context.

Rules:
- Cite file paths and line numbers.
- Be specific and concise.
- If the context is not enough, say what information is missing.
- Do not invent files, frameworks, or behavior.
- Explain the code in a way that helps a developer understand the project.

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You help developers understand unfamiliar codebases."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content