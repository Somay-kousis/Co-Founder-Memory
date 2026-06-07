import re

# Normalize common typos and word variations for delete-memory requests.
def normalize_memory_query(text: str) -> str:
    normalized = text.lower()
    replacements = [
        (r"\bdelet\b", "delete"),
        (r"\bdeletee\b", "delete"),
        (r"\bmemroies\b", "memories"),
        (r"\bmemroes\b", "memories"),
        (r"\bmemroy\b", "memory"),
        (r"\bmemry\b", "memory"),
        (r"\bmemo ries\b", "memories"),
        (r"\bforget all the memories\b", "forget all memories"),
        (r"\bclear all the memories\b", "clear all memories")
    ]
    for pattern, replace in replacements:
        normalized = re.sub(pattern, replace, normalized)
    return normalized

_memory_delete_patterns = [
    re.compile(r"\b(delete|forget|remove|clear)\b.*\b(memories|memory)\b"),
    re.compile(r"\b(memories|memory)\b.*\b(delete|forget|remove|clear)\b"),
    re.compile(r"\b(delete|forget|remove|clear)\b.*\b(all|any|these|those|the|this|that)\b.*\b(memories|memory)\b"),
    re.compile(r"\b(delete|forget|remove|clear)\b.*\b(of|about|related to|any)\b.*\b(memories|memory)\b"),
]


def is_memory_delete_query(text: str) -> bool:
    normalized = normalize_memory_query(text)
    return any(pattern.search(normalized) for pattern in _memory_delete_patterns)
