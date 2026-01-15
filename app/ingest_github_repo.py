from pathlib import Path
import shutil
from git import Repo

from app.ingest_code import load_repository


REPOS_DIR = Path("data/repos")


def clone_github_repo(repo_url: str) -> Path:
    """
    Clone a GitHub repo into data/repos and return local path
    """
    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    repo_name = repo_url.rstrip("/").split("/")[-1]
    repo_path = REPOS_DIR / repo_name

    if repo_path.exists():
        shutil.rmtree(repo_path)

    print(f"Cloning {repo_url} into {repo_path}")
    Repo.clone_from(repo_url, repo_path)

    return repo_path


def ingest_github_repo(repo_url: str):
    """
    Clone repo and extract python code chunks
    """
    repo_path = clone_github_repo(repo_url)

    chunks = load_repository(repo_path)

    return chunks


if __name__ == "__main__":
    repo_url = "https://github.com/pallets/flask"
    chunks = ingest_github_repo(repo_url)

    print(f"Extracted {len(chunks)} chunks")
    print(chunks[0])