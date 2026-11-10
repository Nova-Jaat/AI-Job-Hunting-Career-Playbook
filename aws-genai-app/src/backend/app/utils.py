import re
from typing import List, Dict, Any

def recursive_chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: List[str] = None
) -> List[str]:
    """
    Splits text into chunks preserving semantic paragraph and sentence boundaries.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]

    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Look for the best separator within the overlap window
        split_pos = -1
        for sep in separators:
            pos = text.rfind(sep, start + chunk_size - chunk_overlap, end)
            if pos != -1:
                split_pos = pos + len(sep)
                break

        if split_pos == -1:
            split_pos = end

        chunk = text[start:split_pos].strip()
        if chunk:
            chunks.append(chunk)

        start = max(start + 1, split_pos - chunk_overlap)

    return chunks
