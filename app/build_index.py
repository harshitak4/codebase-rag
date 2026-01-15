from pathlib import Path
from app.ingest_code import load_repository
from app.vector_store import CodeVectorStore

REPO_PATH = Path("data/repos/fastapi")
INDEX_PATH = "data/code_index"

def main():
    print("Loading repository...")
    chunks = load_repository(REPO_PATH)
    print(f"Loaded {len(chunks)} code chunks")

    print("Building vector index...")
    store = CodeVectorStore()
    store.build(chunks)

    print("Saving index...")
    store.save(INDEX_PATH)

    print("Vector index built successfully!")

if __name__ == "__main__":
    main()