import requests
from typing import Tuple, List, Dict
from app.vector_store import CodeVectorStore

INDEX_PATH = "data/code_index"

class RAGAnswerer:
    """
    Simplified RAG answerer with better error handling
    """
    
    def __init__(self, index_path: str = INDEX_PATH):
        self.store = CodeVectorStore()
        
        try:
            self.store.load(index_path)
            print(f"✅ Loaded index from {index_path}")
        except FileNotFoundError:
            print(f"❌ Index not found at {index_path}")
            raise
        
        # Check if Ollama is available
        self.ollama_available = self._check_ollama()
        
        if self.ollama_available:
            print("✅ Ollama is available")
        else:
            print("⚠️  Ollama not available - will provide code snippets only")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama with shorter timeout and simpler prompt"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5-coder:1.5b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 150,  # Shorter response
                        "top_p": 0.9
                    }
                },
                timeout=20  # Shorter timeout
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return None
                    
        except Exception as e:
            return None
    
    def answer(self, question: str, k: int = 5) -> Tuple[str, List[Dict]]:
        """
        Answer a question using RAG
        """
        # Retrieve relevant code
        results = self.store.search(question, k=k)
        
        if not results:
            return "No relevant code found in the index.", []
        
        # Build simple answer first (fallback)
        fallback_answer = f"**Found {len(results)} relevant code snippets:**\n\n"
        for i, r in enumerate(results[:5], 1):
            fallback_answer += f"{i}. `{r['file']}` - {r['type']} `{r['name']}`\n"
            if r.get('docstring'):
                fallback_answer += f"   {r['docstring'][:100]}...\n"
        
        # If Ollama not available, return simple summary
        if not self.ollama_available:
            fallback_answer += "\n💡 *Start Ollama for AI-generated explanations*"
            return fallback_answer, results
        
        # Build SHORT context (only top 2 results, truncated)
        context_parts = []
        for i, r in enumerate(results[:2], 1):
            code_snippet = r['code'][:300] + "..." if len(r['code']) > 300 else r['code']
            context_parts.append(
                f"[{i}] {r['name']} from {r['file']}\n{code_snippet}"
            )
        
        context = "\n\n".join(context_parts)
        
        # VERY short, direct prompt
        prompt = f"""Q: {question}

Code:
{context}

A (1-2 sentences):"""
        
        # Try to get AI answer
        ai_answer = self._call_ollama(prompt)
        
        if ai_answer:
            return ai_answer.strip(), results
        else:
            # Use fallback
            fallback_answer += "\n⚠️ *AI timeout - showing code snippets only*"
            return fallback_answer, results