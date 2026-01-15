from app.vector_store import CodeVectorStore
from app.search_code import search_code
from app.rag_answer import RAGAnswerer

# 1. Load vector store
store = CodeVectorStore()
store.load("data/code_index")

print("✅ Vector store loaded")

# 2. Ask a test question
question = "What does CodeVectorStore do?"

# 3. Retrieve relevant code
results = search_code(store, question)

print(f"🔎 Retrieved {len(results)} code chunks")

# 4. Generate answer using Ollama
rag = RAGAnswerer()
answer = rag.answer(question)

print("\n💡 ANSWER:\n")
print(answer)