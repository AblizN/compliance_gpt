import json
import os
import time
from typing import Any, cast

import config
import store

from openai import OpenAI


if __name__ == "__main__":
    t0 = time.perf_counter()

    client = OpenAI()
    collection = store.get_collection()

    with open(os.path.join(config.PROCESSED_DIR, "gdpr_chunks.json"), "r", encoding="utf-8") as file:
        chunks = json.load(file)

    ids, docs, metas = [], [], []

    for chunk in chunks:
        ids.append(f"{chunk['regulation']}-p{chunk['page']}-c{chunk['chunk_index']}")
        docs.append(chunk["text"])
        metas.append(
            {
                "regulation": chunk["regulation"],
                "page": chunk["page"],
                "chunk_index": chunk["chunk_index"],
            }
        )
    assert len(set(ids)) == len(ids)

    BATCH = 100
    batches = 0

    for i in range(0, len(ids), BATCH):
        batch_ids = ids[i: i + BATCH]
        batch_metas = metas[i: i + BATCH]
        batch_docs = docs[i: i + BATCH]
        resp = client.embeddings.create(
            model=config.EMBED_MODEL, input=batch_docs)
        vectors = [item.embedding for item in resp.data]
        collection.upsert(
            ids=batch_ids,
            embeddings=cast(Any, vectors),
            documents=batch_docs,
            metadatas=batch_metas,
        )
        batches += 1

    print("ids", len(ids))
    print("batches", batches)
    print("time consumed", f"{time.perf_counter() - t0:.2f}s")
    print("collection count", collection.count())
