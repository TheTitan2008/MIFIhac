from __future__ import annotations

import hashlib
import math
import re


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("ё", "е")).strip()


def hashed_char_vector(text: str, dimensions: int = 384) -> dict[int, float]:
    value = f"  {normalize(text)}  "
    counts: dict[int, float] = {}
    for size in (3, 4, 5):
        for pos in range(max(0, len(value) - size + 1)):
            gram = value[pos : pos + size].encode("utf-8")
            index = int.from_bytes(hashlib.sha256(gram).digest()[:4], "big") % dimensions
            counts[index] = counts.get(index, 0.0) + 1.0
    norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
    return {k: v / norm for k, v in counts.items()}


def cosine(left: dict[int, float], right: dict[int, float]) -> float:
    if len(left) > len(right):
        left, right = right, left
    return sum(value * right.get(index, 0.0) for index, value in left.items())


def similarity(left: str, right: str) -> float:
    return cosine(hashed_char_vector(left), hashed_char_vector(right))
