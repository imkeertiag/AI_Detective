from __future__ import annotations

import re
import unicodedata
from typing import Iterable

from rapidfuzz import fuzz


def normalize_name(name: str | None) -> str:
    if not name:
        return ""
    name = unicodedata.normalize("NFKC", str(name)).upper()
    name = re.sub(r"[^A-Z0-9 ]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def soundex_code(name: str) -> str:
    name = normalize_name(name)
    if not name:
        return ""
    first = name[0]
    codes = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6",
    }
    digits = []
    prev = None
    for ch in name[1:]:
        code = codes.get(ch, "0")
        if code != "0" and code != prev:
            digits.append(code)
        prev = code
    encoded = first + "".join(digits)
    return (encoded[:4] + "0000")[:4]


def name_similarity_score(left_name: str | None, right_name: str | None) -> float:
    left = normalize_name(left_name)
    right = normalize_name(right_name)
    if not left or not right:
        return 0.0
    token_ratio = fuzz.token_sort_ratio(left, right) / 100.0
    phonetic_score = 1.0 if soundex_code(left) == soundex_code(right) else 0.0
    return round(min(1.0, max(token_ratio, phonetic_score)), 4)


def find_best_name_match(target_name: str, candidates: Iterable[str]) -> tuple[str, float] | None:
    best_name = None
    best_score = -1.0
    for candidate in candidates:
        score = name_similarity_score(target_name, candidate)
        if score > best_score:
            best_score = score
            best_name = candidate
    if best_name is None:
        return None
    return best_name, best_score
