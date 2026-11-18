import re
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


def build_sources(results: QueryResult) -> list[dict]:
    """Same order as the context, so [n] in the answer is sources[n-1]."""
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]

    sources = []
    for n, (doc, meta) in enumerate(zip(documents, metadatas), start=1):
        text = " ".join(doc.split())
        sources.append({
            "n": n,
            "regulation": meta["regulation"],
            "page": meta["page"],
            "snippet": text[:200],
        })
    return sources


def answer(question: str, k: int = 5) -> dict:
    """Answer one question from the retrieved passages, with its sources."""
    results = retrieve(question, k)
    template = PROMPT_PATH.read_text()
    prompt = template.replace("{context}", build_context(results)).replace("{question}", question)
    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return {
        "answer": response.choices[0].message.content or "",
        "sources": build_sources(results),
        "model": config.CHAT_MODEL,
        "k": k,
    }


def print_result(result: dict) -> None:
    """The answer, then the numbered source list."""
    print(result["answer"])
    print()
    for source in result["sources"]:
        print(f"[{source['n']}] {source['regulation']} p.{source['page']}  {source['snippet']}")


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
        result = answer(question)
        print_result(result)

        # every [n] in the answer needs a source
        cited = [int(n) for n in re.findall(r"\[(\d+)\]", result["answer"])]
        assert all(1 <= n <= len(result["sources"]) for n in cited), f"bad citation in {cited}"
        print()
