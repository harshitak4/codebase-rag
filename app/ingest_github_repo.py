import os
import stat
import shutil
from pathlib import Path
from git import Repo
from app.ingest_code import load_repository
from typing import List, Dict

REPOS_DIR = Path("data/repos")

def _on_rm_error(func, path, exc_info):
    """
    Error handler for Windows file permission issues during directory removal.
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"⚠️  Could not remove {path}: {e}")

def clone_github_repo(repo_url: str) -> Path:
    """
    Clone a GitHub repository to local storage.
    
    Args:
        repo_url: GitHub repository URL (e.g., https://github.com/user/repo)
        
    Returns:
        Path to cloned repository
        
    Raises:
        ValueError: If URL is invalid
        GitCommandError: If cloning fails
    """
    if not repo_url.startswith(("https://github.com/", "git@github.com:")):
        raise ValueError(f"Invalid GitHub URL: {repo_url}")
    
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    
    repo_name = repo_url.rstrip("/").split("/")[-1]
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    
    repo_path = REPOS_DIR / repo_name
    
    if repo_path.exists():
        print(f"🗑️  Removing existing repo: {repo_path}")
        shutil.rmtree(repo_path, onerror=_on_rm_error)
    
    print(f"📥 Cloning {repo_url}...")
    try:
        Repo.clone_from(repo_url, repo_path, depth=1)  
        print(f"✅ Cloned to {repo_path}")
    except Exception as e:
        print(f"❌ Failed to clone: {e}")
        raise
    
    return repo_path

def ingest_github_repo(repo_url: str) -> List[Dict]:
    """
    Clone a GitHub repo and extract all Python code chunks.
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        List of code chunks
    """
    repo_path = clone_github_repo(repo_url)
    chunks = load_repository(repo_path)
    return chunks

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m app.ingest_github_repo <github_url>")
        print("Example: python -m app.ingest_github_repo https://github.com/pallets/flask")
        sys.exit(1)
    
    repo_url = sys.argv[1]
    chunks = ingest_github_repo(repo_url)
    
    print(f"\n📊 Summary:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Functions: {sum(1 for c in chunks if 'Function' in c['type'])}")
    print(f"  Classes: {sum(1 for c in chunks if 'Class' in c['type'])}")
    
    if chunks:
        print(f"\n📄 Sample chunk:")
        print(f"  File: {chunks[0]['file']}")
        print(f"  Type: {chunks[0]['type']}")
        print(f"  Name: {chunks[0]['name']}")
        print(f"  Code length: {len(chunks[0]['code'])} chars")
