from app.vector_store import CodeVectorStore

INDEX_PATH = "data/code_index"

def search(query: str, k: int = 5):
    store = CodeVectorStore()
    store.load(INDEX_PATH)

    results = store.search(query, k=k)
    return results


if __name__ == "__main__":
    query = input("🔎 Ask a question about the codebase: ")
    results = search(query)

    print("\n📄 Top matching code snippets:\n")
    for i, r in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print(f"File: {r['file']}")
        print(f"Name: {r['name']}")
        print(r["code"])
        print()