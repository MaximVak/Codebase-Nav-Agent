from openai import OpenAI


def answer_question(api_key: str, question: str, chunks):
    client = OpenAI(api_key=api_key)

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"""
SOURCE FILE: {chunk["file_path"]}
SOURCE LINES: {chunk["start_line"]}-{chunk["end_line"]}

CODE:
{chunk["content"]}
"""
        )

    context = "\n---\n".join(context_parts)

    prompt = f"""
You are an AI codebase navigation assistant.

Your job is to help developers understand a codebase using ONLY the provided source code context.

Important rules:
- Only answer using the provided context.
- Do not guess or invent files, functions, frameworks, or behavior.
- If the provided context is not enough, say what information is missing.
- Cite file paths and line numbers when making claims.
- If mentioning a function, make sure it actually appears in the cited source context.
- Keep the answer concise, accurate, and useful.

Format your answer like this:

[Clear explanation]

Sources:
- file_path, lines start-end: short reason this source was used
- file_path, lines start-end: short reason this source was used

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
                "content": "You are a careful codebase assistant. You only answer from provided source code context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    return response.choices[0].message.content