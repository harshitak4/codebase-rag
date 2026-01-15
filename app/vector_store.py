import faiss
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer


class CodeVectorStore:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []

    def build(self, chunks):
        texts = [
            f"{c['name']}\n{c['docstring']}\n{c['code']}"
            for c in chunks
        ]

        embeddings = self.model.encode(texts, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        self.metadata = chunks

    def save(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(path / "index.faiss"))

        with open(path / "meta.json", "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def load(self, path):
        path = Path(path)

        self.index = faiss.read_index(str(path / "index.faiss"))

        with open(path / "meta.json", "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(self, query, k=5):
        query_embedding = self.model.encode([query]).astype("float32")
        distances, indices = self.index.search(query_embedding, k)

        results = []
        for i in indices[0]:
            results.append(self.metadata[i])

        return results