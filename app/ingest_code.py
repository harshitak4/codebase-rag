import ast
from pathlib import Path
from typing import List, Dict

IGNORE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", "node_modules",
    "dist", "build", ".idea", ".vscode", ".pytest_cache",
    "tests", "test", "docs", "examples", ".mypy_cache",
    "htmlcov", ".tox", ".eggs", "*.egg-info"
}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".pdf", ".zip", ".tar", ".gz", ".bz2",
    ".mp4", ".mp3", ".wav", ".exe", ".dll", ".so",
    ".pyc", ".pyo", ".pyd"
}

MAX_FILE_SIZE_KB = 500
MAX_CHARS_PER_FILE = 100000

def should_skip_file(file_path: Path) -> bool:
    """
    Determine if a file should be skipped during ingestion.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file should be skipped, False otherwise
    """
 
    if any(part.startswith('.') and part != '..' for part in file_path.parts):
        if file_path.name not in {'.gitignore', '.env.example'}:
            return True
    
    for part in file_path.parts:
        if part in IGNORE_DIRS:
            return True
    
    if file_path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    
    try:
        size_kb = file_path.stat().st_size / 1024
        if size_kb > MAX_FILE_SIZE_KB:
            print(f"⏭ Skipping large file ({size_kb:.1f}KB): {file_path}")
            return True
    except Exception:
        return True
    
    return False

def extract_python_chunks(file_path: Path) -> List[Dict]:
    """
    Extract functions and classes from a Python file using AST.
    
    Args:
        file_path: Path to Python file
        
    Returns:
        List of code chunk dictionaries
    """
    if should_skip_file(file_path):
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read(MAX_CHARS_PER_FILE)
        
        tree = ast.parse(source)
        
    except SyntaxError as e:
        print(f"⚠️  Syntax error in {file_path}: {e}")
        return []
    except Exception as e:
        print(f"⚠️  Error parsing {file_path}: {e}")
        return []
    
    chunks = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            try:
                code = ast.get_source_segment(source, node)
                
                if code and len(code.strip()) > 10:  
                    chunk = {
                        "type": node.__class__.__name__.replace("Def", "").replace("Async", "Async"),
                        "name": node.name,
                        "docstring": ast.get_docstring(node) or "",
                        "code": code,
                        "file": str(file_path.relative_to(file_path.parent.parent))
                    }
                    chunks.append(chunk)
            except Exception as e:
                print(f"⚠️  Error extracting from {file_path}: {e}")
                continue
    
    return chunks

def load_repository(repo_path: Path) -> List[Dict]:
    """
    Load all Python code chunks from a repository.
    
    Args:
        repo_path: Path to repository root
        
    Returns:
        List of all code chunks found
    """
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository not found: {repo_path}")
    
    if not repo_path.is_dir():
        raise ValueError(f"Not a directory: {repo_path}")
    
    print(f"📂 Scanning repository: {repo_path}")
    
    all_chunks = []
    python_files = list(repo_path.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files")
    
    for py_file in python_files:
        try:
            chunks = extract_python_chunks(py_file)
            all_chunks.extend(chunks)
            
            if chunks:
                print(f"✅ {py_file.name}: {len(chunks)} chunks")
                
        except Exception as e:
            print(f"❌ Error processing {py_file}: {e}")
    
    print(f"\n📊 Total chunks extracted: {len(all_chunks)}")
    return all_chunks
