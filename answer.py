import sys
from pathlib import Path

from chromadb.api.types import QueryResult
from openai import OpenAI

import config
import search


PROMPT_PATH = Path("prompts/answer.txt")

client = OpenAI()


def retrieve(question: str, k: int = 5) -> QueryResult:
    """Top-k chunks for one question, reusing search.py."""
    return search.search(question, k=k)


def build_context(results: QueryResult) -> str:
    """Number the passages as '[n] (regulation, p. page) text', one per line."""
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]

    lines = []
    for n, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        text = " ".join(doc.split())
        lines.append(f"[{n}] ({meta['regulation']}, p. {meta['page']}) {text}")
    return "\n".join(lines)


def answer(question: str, k: int = 5) -> str:
    """Answer one question from the retrieved passages only."""
    context = build_context(retrieve(question, k))
    template = PROMPT_PATH.read_text()
    prompt = template.replace("{context}", context).replace("{question}", question)
    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content or ""


QUESTIONS = [
    "What is a DPIA?",
    "What is the right to erasure?",
    "What are the lawful bases for processing?",
    "What does Chinese law say about DPIAs?",  # out of scope, should be refused
]


if __name__ == "__main__":
    # answer.py "question", or no arguments for the demo run
    questions = sys.argv[1:2] or QUESTIONS
    for question in questions:
        print(f"### {question}")
        print(answer(question))
        print()
