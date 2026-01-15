import requests
from typing import Tuple, List, Dict
from app.vector_store import CodeVectorStore

INDEX_PATH = "data/code_index"
OLLAMA_URL = "http://localhost:11434/api/generate"

class RAGAnswerer:
    """
    RAG system for answering questions about codebases using Ollama.
    """
    
    def __init__(self, index_path: str = INDEX_PATH, model: str = "codellama:7b"):
        """
        Initialize RAG answerer.
        
        Args:
            index_path: Path to vector index
            model: Ollama model name
        """
        self.model = model
        self.store = CodeVectorStore()
        
        try:
            self.store.load(index_path)
            print(f"✅ Loaded index from {index_path}")
        except FileNotFoundError:
            print(f"❌ Index not found at {index_path}")
            print("Run 'python -m app.build_index' first to create an index")
            raise
        
    
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                print(f"✅ Ollama connected (model: {model})")
            else:
                print("⚠️  Ollama is running but returned unexpected status")
        except requests.exceptions.RequestException:
            print("❌ Ollama not running!")
            print("Start Ollama with: ollama serve")
            print(f"Then pull model: ollama pull {model}")
            raise ConnectionError("Ollama is not running")
    
    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama API for text generation.
        
        Args:
            prompt: Prompt to send to model
            
        Returns:
            Generated text
        """
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 512
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return f"Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out. The model might be too slow for this query."
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def answer(self, question: str, k: int = 5) -> Tuple[str, List[Dict]]:
        """
        Answer a question using RAG.
        
        Args:
            question: User's question
            k: Number of code chunks to retrieve
            
        Returns:
            Tuple of (answer, retrieved_contexts)
        """
    
        results = self.store.search(question, k=k)
        
        if not results:
            return "No relevant code found in the index.", []
        
    
        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Code Snippet {i}]\n"
                f"File: {r['file']}\n"
                f"Type: {r['type']}\n"
                f"Name: {r['name']}\n"
                f"```python\n{r['code']}\n```\n"
            )
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are a senior software engineer analyzing a codebase. Answer the user's question based ONLY on the code snippets provided below. Be specific and reference the actual code.

Question: {question}

Code Context:
{context}

Answer (be concise and technical):"""
        
        answer = self._call_ollama(prompt)
        
        return answer, results

class RAGAnswererFallback:
    """
    Fallback RAG answerer that works without Ollama (returns context only).
    """
    
    def __init__(self, index_path: str = INDEX_PATH):
        self.store = CodeVectorStore()
        self.store.load(index_path)
        print("⚠️  Running in fallback mode (no Ollama)")
    
    def answer(self, question: str, k: int = 5) -> Tuple[str, List[Dict]]:
        results = self.store.search(question, k=k)
        
        if not results:
            return "No relevant code found.", []
        
        answer = "**Relevant code found:**\n\n"
        for i, r in enumerate(results, 1):
            answer += f"{i}. `{r['file']}` - {r['type']} `{r['name']}`\n"
        
        answer += "\n💡 *Install Ollama for AI-generated answers*"
        
        return answer, results
