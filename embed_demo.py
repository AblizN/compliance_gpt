import math

from openai import OpenAI

import config

client = OpenAI()


def embed(text: str) -> list[float]:
    response = client.embeddings.create(input=text, model=config.EMBED_MODEL)
    return response.data[0].embedding


def find_magnitude(vec: list[float]) -> float:
    magnitude = 0
    for dimension in vec:
        magnitude = magnitude + dimension**2
    return math.sqrt(magnitude)


def find_dot_prod(vec1: list[float], vec2: list[float]) -> float:
    dot_prod = 0
    matrix = [list(item) for item in zip(vec1, vec2)]
    for item in matrix:
        dot_prod += item[0] * item[1]
    return dot_prod


def find_cosine_similarity(dot_prod: float, magnitude1: float, magnitude2: float) -> float:
    return dot_prod / (magnitude1 * magnitude2)


if __name__ == "__main__":

    text1 = "A DPIA is required for high-risk processing"
    text2 = "Impact assessments are mandatory before risky data use"
    text3 = "The pizza in Naples is excellent"

    vec1 = embed(text1)
    vec2 = embed(text2)
    vec3 = embed(text3)

    print("vector 1 length", len(vec1))
    print("vector 2 length", len(vec2))
    print("vector 3 length", len(vec3))

    magnitude1 = find_magnitude(vec1)
    magnitude2 = find_magnitude(vec2)
    magnitude3 = find_magnitude(vec3)

    dot_prod12 = find_dot_prod(vec1, vec2)
    print(
        "cosine similarity between 1 & 2",
        find_cosine_similarity(dot_prod12, magnitude1, magnitude2),
    )

    dot_prod13 = find_dot_prod(vec1, vec3)
    print(
        "cosine similarity between 1 & 3",
        find_cosine_similarity(dot_prod13, magnitude1, magnitude3),
    )

    dot_prod23 = find_dot_prod(vec2, vec3)
    print(
        "cosine similarity between 2 & 3",
        find_cosine_similarity(dot_prod23, magnitude2, magnitude3),
    )