import ast
from pathlib import Path

# ---------- DEFENCE 1 CONFIG ----------

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".idea",
    ".vscode",
    ".pytest_cache"
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg",
    ".pdf", ".zip", ".tar", ".gz",
    ".mp4", ".mp3", ".exe", ".dll"
}

MAX_FILE_SIZE_KB = 200        # skip files larger than 200 KB
MAX_CHARS_PER_FILE = 8000     # hard limit per file (RAM safety)

def should_skip_file(file_path: Path) -> bool:
    # Skip hidden / ignored directories
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return True

    # Skip ignored extensions
    if file_path.suffix.lower() in IGNORE_EXTENSIONS:
        return True

    # Skip large files
    try:
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            return True
    except Exception:
        return True

    return False

def extract_python_chunks(file_path: Path):
    if should_skip_file(file_path):
        print(f"⏭ Skipping {file_path}")
        return []

    if should_skip_file(file_path):
        return []

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source = f.read(MAX_CHARS_PER_FILE)

    tree = ast.parse(source)
    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            code = ast.get_source_segment(source, node)
            chunks.append({
                "type": node.__class__.__name__,
                "name": node.name,
                "docstring": ast.get_docstring(node) or "",
                "code": code,
                "file": str(file_path)
            })

    return chunks


def load_repository(repo_path: Path):
    all_chunks = []

    for py_file in repo_path.rglob("*.py"):
        try:
            all_chunks.extend(extract_python_chunks(py_file))
        except Exception as e:
            print(f"Skipping {py_file}: {e}")

    return all_chunks


if __name__ == "__main__":
    repo_path = Path("data/repos/fastapi")
    chunks = load_repository(repo_path)

    print(f"Extracted {len(chunks)} code chunks")
    print(chunks[0])

from app.github_loader import clone_github_repo

from pathlib import Path

def ingest_github_repo(repo_url: str):
    repo_path = clone_github_repo(repo_url)
    return load_repository(Path(repo_path))