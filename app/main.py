from app.rag_answer import CodeRAG

if __name__ == "__main__":
    rag = CodeRAG()

    while True:
        q = input("\nAsk about the repo (or 'exit'): ")
        if q.lower() == "exit":
            break

        answer = rag.answer(q)
        print("\nANSWER:\n", answer)