import json
import os

import chromadb

import config

chunk_path = os.path.join(config.PROCESSED_DIR, "gdpr_chunks.json")

client = chromadb.PersistentClient(path=config.CHROMA_DIR)


def get_collection():
    return client.get_or_create_collection(name="regulations")


if __name__ == "__main__":
    collection = get_collection()

    with open(chunk_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    ids, documents, metadatas = [], [], []
    for chunk in chunks[:10]:
        ids.append(f"{chunk['regulation']}-p{chunk['page']}-c{chunk['chunk_index']}")
        documents.append(chunk["text"])
        metadatas.append({"regulation": chunk["regulation"], "page": chunk["page"]})

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    print(collection.count())

