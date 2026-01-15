import os
import shutil
import stat
from pathlib import Path
import git

def _on_rm_error(func, path, exc_info):
    # Windows permission fix
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_github_repo(repo_url: str) -> str:
    repo_name = repo_url.rstrip("/").split("/")[-1]
    base_path = Path("data/repos")
    base_path.mkdir(parents=True, exist_ok=True)

    repo_path = base_path / repo_name

    if repo_path.exists():
        shutil.rmtree(repo_path, onerror=_on_rm_error)

    git.Repo.clone_from(repo_url, repo_path)
    return str(repo_path)