# vectorstore.py
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import pickle
from typing import List
from ingest import DocumentChunk

EMB_MODEL_NAME = os.getenv("EMB_MODEL_NAME", "all-MiniLM-L6-v2")
EMB_DIM = 384  # for all-MiniLM-L6-v2

class VectorStore:
    def __init__(self, model_name: str = EMB_MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.id_to_meta = {}
        self.emb_dim = self.model.get_sentence_embedding_dimension()

    def build(self, chunks: List[DocumentChunk]):
        texts = [c.text for c in chunks]
        ids = [c.id for c in chunks]
        metas = [{"source": c.source, "id": c.id} for c in chunks]

        emb = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        self.index = faiss.IndexFlatIP(self.emb_dim)
        # normalize vectors to use inner product as cosine
        faiss.normalize_L2(emb)
        self.index.add(emb)
        for i, mid in enumerate(ids):
            self.id_to_meta[mid] = metas[i]
        # store embeddings mapping for retrieval of the text if needed
        self._texts = texts
        self._ids = ids
        print(f"[vectorstore] Built index with {len(ids)} vectors.")

    def save(self, path: str = "faiss.index"):
        faiss.write_index(self.index, path)
        with open(path + ".meta.pkl", "wb") as f:
            pickle.dump({"id_to_meta": self.id_to_meta, "texts": self._texts, "ids": self._ids}, f)
        print(f"[vectorstore] saved to {path} (+meta)")

    def load(self, path: str = "faiss.index"):
        self.index = faiss.read_index(path)
        with open(path + ".meta.pkl", "rb") as f:
            d = pickle.load(f)
        self.id_to_meta = d["id_to_meta"]
        self._texts = d["texts"]
        self._ids = d["ids"]
        print("[vectorstore] loaded index and metadata")

    def query(self, q: str, top_k: int = 5):
        emb_q = self.model.encode([q], convert_to_numpy=True)
        faiss.normalize_L2(emb_q)
        D, I = self.index.search(emb_q, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0 or idx >= len(self._ids):
                continue
            doc_id = self._ids[idx]
            meta = self.id_to_meta.get(doc_id, {})
            results.append({"id": doc_id, "source": meta.get("source"), "text": self._texts[idx], "score": float(score)})
        return results