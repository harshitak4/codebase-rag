# 🤖 Codebase RAG Assistant

Ask questions about any codebase using AI-powered semantic search. This tool uses **Retrieval-Augmented Generation (RAG)** to provide accurate, context-aware answers about your code.

## ✨ Features

- 🔍 **Semantic Code Search** - Find relevant code using natural language
- 🤖 **AI-Powered Answers** - Get explanations using CodeLlama
- 📦 **100% Local** - No cloud calls, your code stays private
- 🚀 **Fast Indexing** - FAISS vector search for instant retrieval
- 💻 **Clean UI** - Beautiful Streamlit interface
- 🔌 **GitHub Integration** - Index any public repository

## 🎯 Use Cases

- "How does authentication work in this codebase?"
- "Explain the database connection logic"
- "What does the UserService class do?"
- "Show me all API endpoints"
- "Where is error handling implemented?"

## 🛠️ Installation

### Prerequisites

1. **Python 3.8+**
2. **Ollama** - [Download here](https://ollama.com/download)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/harshitak4/codebase-rag.git
cd codebase-rag
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install and start Ollama:**
```bash
# Download Ollama from https://ollama.com/download
# Then pull the CodeLlama model:
ollama pull codellama:7b
```

4. **Start Ollama server:**
```bash
ollama serve
```

## 🚀 Quick Start

### Option 1: Index a GitHub Repository

```bash
python -m app.build_index --github https://github.com/pallets/flask
```

### Option 2: Index a Local Repository

```bash
python -m app.build_index --local /path/to/your/repo
```

### Launch the UI

```bash
streamlit run ui/streamlit_app.py
```

Open http://localhost:8501 in your browser.

## 📖 Usage Examples

### Building an Index

**From GitHub:**
```bash
python -m app.build_index --github https://github.com/tiangolo/fastapi
```

**From Local Path:**
```bash
python -m app.build_index --local ./my-project
```

### Using the CLI

```bash
python test_rag.py
```

### Using the Web UI

1. Start Streamlit: `streamlit run ui/streamlit_app.py`
2. Enter your question
3. Click "Ask"
4. View AI-generated answer and source code

## 🏗️ Architecture

```
┌─────────────┐
│   GitHub    │
│  Repository │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Code Ingestion  │
│  (AST Parser)   │
└──────┬──────────┘
       │
       ▼
┌──────────────────┐
│ Code Chunks      │
│ (Functions/      │
│  Classes)        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Embeddings       │
│ (SentenceTrans-  │
│  former)         │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ FAISS Index      │
│ (Vector Store)   │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐      ┌─────────────┐
│ User Question    │─────▶│   Search    │
└──────────────────┘      └──────┬──────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │  Retrieved   │
                          │    Code      │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │   Ollama     │
                          │ (CodeLlama)  │
                          └──────┬───────┘
                                 │
                                 ▼
                          ┌──────────────┐
                          │    Answer    │
                          └──────────────┘
```

## 📁 Project Structure

```
codebase-rag/
├── app/
│   ├── __init__.py
│   ├── vector_store.py       # FAISS vector store
│   ├── ingest_code.py         # Code extraction (AST)
│   ├── ingest_github_repo.py  # GitHub cloning
│   ├── build_index.py         # Index building pipeline
│   └── rag_answer.py          # RAG system with Ollama
├── ui/
│   └── streamlit_app.py       # Web interface
├── data/
│   ├── repos/                 # Cloned repositories
│   └── code_index/            # FAISS index + metadata
├── test_rag.py                # CLI test script
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Change the LLM Model

Edit `app/rag_answer.py`:
```python
# Default: codellama:7b
# Other options: codellama:13b, deepseek-coder, starcoder
rag = RAGAnswerer(model="deepseek-coder")
```

### Adjust Retrieval Count

In the Streamlit UI sidebar, use the slider to change the number of code chunks retrieved (default: 5).

### File Size Limits

Edit `app/ingest_code.py`:
```python
MAX_FILE_SIZE_KB = 500        # Skip files larger than this
MAX_CHARS_PER_FILE = 100000   # Character limit per file
```

## 🧪 Testing

Run the test script:
```bash
python test_rag.py
```

This will:
1. Load the index
2. Ask 3 test questions
3. Show answers and retrieved code

## 🐛 Troubleshooting

### "Index not found"
**Solution:** Build an index first using `python -m app.build_index`

### "Ollama not running"
**Solution:** Start Ollama with `ollama serve`, then pull the model with `ollama pull codellama:7b`

### "No code chunks found"
**Solution:** The repository might not have any Python files, or they're all being filtered out. Check the ignore lists in `app/ingest_code.py`

### Slow performance
**Solution:** 
- Use a smaller model: `codellama:7b` instead of `codellama:13b`
- Reduce retrieval count (k parameter)
- Index fewer files

## 🎓 How It Works

1. **Code Ingestion**: Python files are parsed using AST to extract functions and classes
2. **Embedding Generation**: Each code chunk is converted to a 384-dim vector using sentence-transformers
3. **Vector Indexing**: Vectors are stored in a FAISS index for fast similarity search
4. **Query Processing**: User questions are embedded and searched against the index
5. **Context Retrieval**: Top-k most similar code chunks are retrieved
6. **Answer Generation**: Retrieved code + question are sent to Ollama (CodeLlama)
7. **Response**: AI generates a contextual answer based on actual code

## 📊 Performance

- **Indexing Speed**: ~100 files/minute (depends on file size)
- **Search Latency**: <100ms for retrieval
- **Answer Generation**: 5-15 seconds (depends on model and hardware)
- **Memory Usage**: ~2GB RAM for small repos, ~5GB for large repos

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Support for more languages (JavaScript, Java, etc.)
- Better code chunking strategies
- Web-based index building UI
- Multi-repo indexing
- Code similarity visualization

## 📝 License

MIT License - feel free to use this for any purpose.

##  Acknowledgments

- **FAISS** by Meta AI
- **sentence-transformers** by UKPLab
- **Ollama** for easy local LLM deployment
- **Streamlit** for the awesome UI framework

## 📧 Contact

Questions? Open an issue on GitHub!

---

**Built with ❤️ for developers who want to understand codebases faster**
