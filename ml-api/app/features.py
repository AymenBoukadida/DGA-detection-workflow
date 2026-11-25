from __future__ import annotations

import math
from collections import Counter

import numpy as np

NUMERIC_FEATURE_NAMES = (
    "length",
    "digit_ratio",
    "vowel_ratio",
    "unique_char_ratio",
    "max_consonant_run",
    "entropy",
    "hyphen_count",
    "dot_count",
    "longest_label_length",
)

VOWELS = frozenset("aeiou")


def _max_consonant_run(domain: str) -> int:
    longest = 0
    current = 0
    for char in domain:
        if char.isalpha() and char not in VOWELS:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _entropy(domain: str) -> float:
    counts = Counter(domain)
    total = len(domain)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def domain_features(domain: str) -> list[float]:
    length = len(domain)
    digits = sum(char.isdigit() for char in domain)
    vowels = sum(char in VOWELS for char in domain)
    return [
        float(length),
        digits / length,
        vowels / length,
        len(set(domain)) / length,
        float(_max_consonant_run(domain)),
        _entropy(domain),
        float(domain.count("-")),
        float(domain.count(".")),
        float(max(len(label) for label in domain.split("."))),
    ]


def numeric_features(domains) -> np.ndarray:
    return np.asarray([domain_features(str(domain)) for domain in domains], dtype=np.float64)
