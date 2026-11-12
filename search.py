import argparse
from typing import Any, cast

from chromadb.api.types import QueryResult
from openai import OpenAI

import config
import store


client = OpenAI()


def embed_question(question: str) -> list[float]:
    """Same model as ingest, or the distances mean nothing."""
    response = client.embeddings.create(input=question, model=config.EMBED_MODEL)
    return response.data[0].embedding


def search(question: str, k: int = 5) -> QueryResult:
    """Top-k chunks for one question."""
    collection = store.get_collection()
    vector = embed_question(question)
    return collection.query(
        query_embeddings=cast(Any, [vector]),
        n_results=k,
        include=cast(Any, ["documents", "metadatas", "distances"]),
    )


def print_results(results: QueryResult) -> None:
    """One query, so index [0] everywhere."""
    documents = (results.get("documents") or [[]])[0]
    metadatas = (results.get("metadatas") or [[]])[0]
    distances = (results.get("distances") or [[]])[0]

    if not documents:
        print("no results")
        return

    for rank, (doc, meta, distance) in enumerate(zip(documents, metadatas, distances), start=1):
        similarity = 1 - distance
        snippet = " ".join(doc.split())[:150]
        print(f"{rank}. similarity={similarity:.3f}  {meta['regulation']} p.{meta['page']}")
        print(f"   {snippet}")


QUESTIONS = [
    "What is a DPIA?",
    "What are the lawful bases for processing?",
    "What is the right to erasure?",
    "How long can data be kept?",
    "What is a data controller?",
]


if __name__ == "__main__":
    # search.py "question" [--k 5], or no arguments for the demo run
    parser = argparse.ArgumentParser(description="Search the GDPR vector store.")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    if args.question:
        print_results(search(args.question, k=args.k))
    else:
        # acceptance: the DPIA question must surface Article 35
        results = search("What is a data protection impact assessment?")
        docs = (results.get("documents") or [[]])[0]
        pages = [m["page"] for m in (results.get("metadatas") or [[]])[0]]
        assert any("Article 35" in d for d in docs) or 53 in pages, f"Article 35 not in top 5, got pages {pages}"
        print("acceptance ok: Article 35 found\n")

        for question in QUESTIONS:
            print(f"### {question}")
            print_results(search(question))
            print()
