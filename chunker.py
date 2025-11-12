from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[Dict]:
    tokens = text.split()
    if len(tokens) <= chunk_size:
        return [{"chunk_text": text, "chunk_id": "0"}]
    chunks = []
    start = 0
    i = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = " ".join(chunk_tokens)
        chunks.append({"chunk_text": chunk_text, "chunk_id": str(i)})
        i += 1
        if end == len(tokens):
            break
        start = end - overlap
    return chunks
