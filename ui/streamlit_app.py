import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from app.rag_answer import RAGAnswerer

# Page config
st.set_page_config(
    page_title="Codebase RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .code-chunk {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🤖 Codebase RAG Assistant</p>', unsafe_allow_html=True)
st.caption("Ask questions about your codebase using AI-powered semantic search")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This tool uses **Retrieval-Augmented Generation (RAG)** to answer questions about your codebase.
    
    **How it works:**
    1. Semantic search finds relevant code
    2. AI analyzes the code (if available)
    3. Generates contextual answers
    
    **Requirements:**
    - Index built from your repo
    - Ollama running locally (optional)
    """)
    
    st.divider()
    
    st.header("⚙️ Settings")
    k_results = st.slider("Number of code chunks to retrieve", 1, 10, 5)
    show_distances = st.checkbox("Show similarity scores", value=False)
    
    st.divider()
    
    st.header("📊 Stats")
    if Path("data/code_index/meta.json").exists():
        import json
        with open("data/code_index/meta.json") as f:
            metadata = json.load(f)
        st.metric("Indexed Code Chunks", len(metadata))
        st.metric("Functions", sum(1 for m in metadata if "Function" in m["type"]))
        st.metric("Classes", sum(1 for m in metadata if "Class" in m["type"]))
    else:
        st.warning("No index found. Run `python -m app.build_index` first.")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Load RAG system
@st.cache_resource
def load_rag():
    """Load RAG system with caching"""
    try:
        return RAGAnswerer()
    except FileNotFoundError as e:
        st.sidebar.error(f"❌ Index not found: {str(e)}")
        st.error("Please build an index first:")
        st.code("python -m app.build_index --github https://github.com/user/repo")
        st.stop()
    except Exception as e:
        st.error(f"❌ Failed to load RAG system: {str(e)}")
        st.stop()

try:
    rag = load_rag()
    
except Exception as e:
    st.error(f"❌ Failed to initialize: {str(e)}")
    st.info("Make sure you've built an index first:")
    st.code("python -m app.build_index --github https://github.com/user/repo")
    st.stop()

# Main interface
st.divider()

# Question input
question = st.text_area(
    "💬 Ask a question about the codebase",
    placeholder="Examples:\n- How does authentication work?\n- Explain the database connection logic\n- What does the UserService class do?",
    height=100,
    key="question_input"
)

col1, col2, col3 = st.columns([1, 1, 4])

with col1:
    ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)

with col2:
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# Process question
if ask_button:
    if not question.strip():
        st.warning("⚠️ Please enter a question")
    else:
        with st.spinner("🔍 Searching codebase..."):
            try:
                answer, contexts = rag.answer(question, k=k_results)
                
                # Add to history
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer,
                    "contexts": contexts
                })
                
                # Clear input and rerun
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.divider()
    st.subheader("💬 Chat History")
    
    for i, chat in enumerate(reversed(st.session_state.chat_history)):
        idx = len(st.session_state.chat_history) - i
        
        with st.container():
            # Question
            st.markdown(f"### 🙋 Question {idx}")
            st.info(chat["question"])
            
            # Answer
            st.markdown("### 🤖 Answer")
            st.success(chat["answer"])
            
            # Retrieved contexts
            with st.expander(f"📂 View {len(chat['contexts'])} Retrieved Code Snippets"):
                for j, ctx in enumerate(chat["contexts"], 1):
                    st.markdown(f"**Snippet {j}**")
                    
                    col_a, col_b, col_c = st.columns(3)
                    col_a.markdown(f"📄 **File:** `{ctx['file']}`")
                    col_b.markdown(f"🏷️ **Type:** `{ctx['type']}`")
                    col_c.markdown(f"✨ **Name:** `{ctx['name']}`")
                    
                    if show_distances and 'distance' in ctx:
                        st.caption(f"Similarity score: {ctx['distance']:.4f}")
                    
                    # Show docstring if available
                    if ctx.get('docstring'):
                        st.markdown(f"**Description:** {ctx['docstring'][:200]}...")
                    
                    st.code(ctx["code"], language="python")
                    st.divider()
            
            st.markdown("---")

else:
    st.info("👋 Ask a question to get started!")

# Footer
st.divider()
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.caption("• 100% Local • No cloud calls")
with col_b:
    st.caption("• No cloud calls")
with col_c:
    st.caption("• Your code stays on your machine")
