import faiss
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class CodeVectorStore:
    """Vector store for code embeddings using FAISS and sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector store with a sentence transformer model.
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []
    
    def build(self, chunks: List[Dict]) -> None:
        """
        Build FAISS index from code chunks.
        
        Args:
            chunks: List of code chunk dictionaries with keys: name, docstring, code, file, type
        """
        if not chunks:
            raise ValueError("Cannot build index from empty chunks list")
        
        print(f"Building embeddings for {len(chunks)} code chunks...")
        
        texts = []
        for c in chunks:
            text = f"{c['name']}\n{c['docstring']}\n{c['code']}"
            texts.append(text)
        
        embeddings = self.model.encode(
            texts, 
            show_progress_bar=True,
            batch_size=32
        )
        embeddings = np.array(embeddings).astype("float32")
        
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        
        self.metadata = chunks
        print(f"✅ Index built with {self.index.ntotal} vectors (dimension: {dim})")
    
    def save(self, path: str) -> None:
        """
        Save index and metadata to disk.
        
        Args:
            path: Directory path to save index files
        """
        if self.index is None:
            raise ValueError("No index to save. Build an index first.")
        
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        index_path = path / "index.faiss"
        faiss.write_index(self.index, str(index_path))
        
        meta_path = path / "meta.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)
        
        print(f"✅ Index saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load index and metadata from disk.
        
        Args:
            path: Directory path containing index files
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Index directory not found: {path}")
        
        index_path = path / "index.faiss"
        meta_path = path / "meta.json"
        
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        if not meta_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {meta_path}")
        
        self.index = faiss.read_index(str(index_path))
        
        with open(meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)
        
        print(f"✅ Index loaded: {self.index.ntotal} vectors")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar code chunks.
        
        Args:
            query: Search query string
            k: Number of results to return
            
        Returns:
            List of metadata dictionaries for top-k results
        """
        if self.index is None:
            raise ValueError("No index loaded. Load or build an index first.")
        
        query_embedding = self.model.encode([query]).astype("float32")
        
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            result = self.metadata[idx].copy()
            result['distance'] = float(dist)
            results.append(result)
        
        return results
