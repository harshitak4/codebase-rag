from app.vector_store import CodeVectorStore
from transformers import pipeline

INDEX_PATH = "data/code_index"

class RAGAnswerer:
    def __init__(self):
        self.store = CodeVectorStore()
        self.store.load(INDEX_PATH)

        # Lightweight CPU-safe model
        self.llm = pipeline(
            "text-generation",
            model="google/flan-t5-base",
            max_new_tokens=256
        )

    def answer(self, question: str, k: int = 5) -> str:
        results = self.store.search(question, k=k)

        context = "\n\n".join(
            f"File: {r['file']}\nCode:\n{r['code']}"
            for r in results
        )

        prompt = f"""
You are a senior software engineer.

Answer the question using ONLY the code below.

Question:
{question}

Code:
{context}

Answer clearly and concisely.
"""

        output = self.llm(prompt)[0]["generated_text"]
        return output