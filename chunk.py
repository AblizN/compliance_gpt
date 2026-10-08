import json
import os
import statistics

import config


def chunk_text(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    """Sliding windows in characters, not tokens. Stops at the end of text; no duplicate tail."""
    assert size > 0, "size must be greater than 0"
    assert overlap >= 0, "overlap cannot be negative"
    assert overlap < size, "overlap must be less than size"

    chunks = []
    step = size - overlap

    for start in range(0, len(text), step):
        chunks.append(text[start : start + size])
        if start + size >= len(text):
            break

    return chunks


def chunk_pages(pages: list[dict]) -> list[dict]:
    """Chunk per page; chunk_index restarts at 0 and each chunk keeps regulation and page."""
    chunk_list = []
    for page in pages:
        for index, chunk in enumerate(chunk_text(page["text"])):
            chunk_list.append(
                {
                    "regulation": page["regulation"],
                    "page": page["page"],
                    "chunk_index": index,
                    "text": chunk,
                }
            )
    return chunk_list


if __name__ == "__main__":
    in_path = os.path.join(config.PROCESSED_DIR, "gdpr.json")
    out_path = os.path.join(config.PROCESSED_DIR, "gdpr_chunks.json")

    with open(in_path, "r", encoding="utf-8") as file:
        pages = json.load(file)

    chunks = chunk_pages(pages)

    with open(out_path, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=2)

    lengths = [len(chunk["text"]) for chunk in chunks]
    print(f"chunks: {len(chunks)}")
    print(
        f"length mean: {statistics.mean(lengths):.1f}, min: {min(lengths)}, max: {max(lengths)}"
    )

