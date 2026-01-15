"""
Test script for RAG system
"""
from app.rag_answer import RAGAnswerer

def main():
    print("=" * 60)
    print("🧪 Testing RAG System")
    print("=" * 60)

    try:
        print("\n1️⃣ Loading RAG system...")
        rag = RAGAnswerer()
        print("✅ RAG system loaded\n")
    except Exception as e:
        print(f"❌ Failed to load RAG: {e}")
        print("\nMake sure you:")
        print("  1. Built an index: python -m app.build_index --github <repo_url>")
        print("  2. Started Ollama: ollama serve")
        print("  3. Pulled model: ollama pull codellama:7b")
        return
    
    test_questions = [
        "What does the CodeVectorStore class do?",
        "How is the FAISS index built?",
        "Explain the search functionality"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'=' * 60}")
        print(f"Question {i}: {question}")
        print('=' * 60)
        
        try:
            answer, contexts = rag.answer(question, k=3)
            
            print(f"\n🤖 ANSWER:\n")
            print(answer)
            
            print(f"\n📂 Retrieved {len(contexts)} code chunks:")
            for j, ctx in enumerate(contexts, 1):
                print(f"  {j}. {ctx['file']} - {ctx['type']} '{ctx['name']}'")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
