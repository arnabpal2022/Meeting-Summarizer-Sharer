# app/services/rag.py
import os
import json
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.config import settings

class RAGIndex:
    def __init__(self, transcript_id: int):
        self.transcript_id = transcript_id
        self.index_dir = Path(settings.storage_dir) / "indexes" / f"{transcript_id}"
        self.index_path = self.index_dir / "index.faiss"
        self.meta_path = self.index_dir / "chunks.json"
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._model = None
        self._index = None
        self._chunks: List[str] = []

    def _ensure_model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)

    def build(self, chunks: List[str]):
        self._ensure_model()
        self.index_dir.mkdir(parents=True, exist_ok=True)
        embeddings = self._model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings.astype(np.float32))
        self._index = index
        self._chunks = chunks
        faiss.write_index(index, str(self.index_path))
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump({"chunks": chunks}, f, ensure_ascii=False)

    def load(self):
        if not self.index_path.exists() or not self.meta_path.exists():
            raise FileNotFoundError("RAG index not found for transcript")
        self._index = faiss.read_index(str(self.index_path))
        with open(self.meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self._chunks = data["chunks"]
        self._ensure_model()

    def query(self, query: str, k: int = 6) -> List[Tuple[int, float, str]]:
        if self._index is None or not self._chunks:
            self.load()
        q = self._model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
        scores, idx = self._index.search(q, min(k, len(self._chunks)))
        results = []
        for i, score in zip(idx[0], scores[0]):
            if i == -1:
                continue
            results.append((int(i), float(score), self._chunks[int(i)]))
        return results
