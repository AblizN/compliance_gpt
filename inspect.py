import json
import os
import random

import config

chunk_path = os.path.join(config.PROCESSED_DIR, "gdpr_chunks.json")

with open(chunk_path, "r", encoding="utf-8") as file:
    chunks = json.load(file)


for _ in range(5):
    chunk = random.choice(chunks)
    print(f"regulation: {chunk['regulation']}")
    print(f"chunk_index: {chunk['chunk_index']}")
    print(f"page: {chunk['page']}")
