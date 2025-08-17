from typing import List

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> List[str]:
    text = text.replace("\r\n", "\n")
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in parts:
        if len(current) + len(p) + 2 <= max_chars:
            current = (current + "\n\n" + p).strip() if current else p
        else:
            if current:
                chunks.append(current)
            if len(p) <= max_chars:
                current = p
            else:
                start = 0
                while start < len(p):
                    end = min(start + max_chars, len(p))
                    chunk = p[start:end]
                    chunks.append(chunk)
                    start = max(end - overlap, end)
                current = ""
    if current:
        chunks.append(current)
    merged = []
    for c in chunks:
        if merged and len(merged[-1]) + len(c) + 1 < max_chars:
            merged[-1] = merged[-1] + "\n" + c
        else:
            merged.append(c)
    return merged
