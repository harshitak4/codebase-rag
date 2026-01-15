import sys
from pathlib import Path
from app.ingest_github_repo import ingest_github_repo
from app.ingest_code import load_repository
from app.vector_store import CodeVectorStore

INDEX_PATH = "data/code_index"

def build_index_from_github(repo_url: str, index_path: str = INDEX_PATH) -> None:
    """
    Complete pipeline: Clone GitHub repo → Extract code → Build index.
    
    Args:
        repo_url: GitHub repository URL
        index_path: Where to save the index
    """
    print("=" * 60)
    print("🚀 Building Code Index from GitHub Repository")
    print("=" * 60)
    
    print("\n📥 STEP 1: Cloning and ingesting repository...")
    chunks = ingest_github_repo(repo_url)
    
    if not chunks:
        print("❌ No code chunks found. Exiting.")
        return
    
    print(f"✅ Extracted {len(chunks)} code chunks")
    
    print("\n🔨 STEP 2: Building vector index...")
    store = CodeVectorStore()
    store.build(chunks)
    
    print("\n💾 STEP 3: Saving index...")
    store.save(index_path)
    
    print("\n" + "=" * 60)
    print("✅ Index built successfully!")
    print(f"📁 Location: {index_path}")
    print(f"📊 Total vectors: {len(chunks)}")
    print("=" * 60)

def build_index_from_local(repo_path: str, index_path: str = INDEX_PATH) -> None:
    """
    Build index from a local repository.
    
    Args:
        repo_path: Path to local repository
        index_path: Where to save the index
    """
    print("=" * 60)
    print("🚀 Building Code Index from Local Repository")
    print("=" * 60)
    
    repo_path = Path(repo_path)
    
    if not repo_path.exists():
        print(f"❌ Repository not found: {repo_path}")
        return

    print("\n📂 STEP 1: Loading repository...")
    chunks = load_repository(repo_path)
    
    if not chunks:
        print("❌ No code chunks found. Exiting.")
        return
    
    print(f"✅ Extracted {len(chunks)} code chunks")
    
    print("\n🔨 STEP 2: Building vector index...")
    store = CodeVectorStore()
    store.build(chunks)
    
    print("\n💾 STEP 3: Saving index...")
    store.save(index_path)
    
    print("\n" + "=" * 60)
    print("✅ Index built successfully!")
    print(f"📁 Location: {index_path}")
    print(f"📊 Total vectors: {len(chunks)}")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  From GitHub:  python -m app.build_index --github <repo_url>")
        print("  From local:   python -m app.build_index --local <path>")
        print("\nExamples:")
        print("  python -m app.build_index --github https://github.com/pallets/flask")
        print("  python -m app.build_index --local ./my-project")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "--github" and len(sys.argv) >= 3:
        repo_url = sys.argv[2]
        build_index_from_github(repo_url)
    
    elif mode == "--local" and len(sys.argv) >= 3:
        repo_path = sys.argv[2]
        build_index_from_local(repo_path)
    
    else:
        print("❌ Invalid arguments. Use --github <url> or --local <path>")
        sys.exit(1)
