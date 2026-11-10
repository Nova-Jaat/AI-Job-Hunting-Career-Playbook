import pytest
from app.utils import recursive_chunk_text

def test_recursive_chunking():
    sample_text = (
        "Amazon Bedrock offers high performance LLMs. " * 30
    )
    chunks = recursive_chunk_text(sample_text, chunk_size=200, chunk_overlap=40)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 250 # allow boundary grace
