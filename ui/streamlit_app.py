import sys
import os

# Allow imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from app.rag_answer import RAGAnswerer

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Codebase RAG",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Codebase RAG Assistant")
st.caption("Ask questions about your codebase ")

# ---------------- SESSION STATE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

@st.cache_resource
def load_rag():
    return RAGAnswerer()

rag = load_rag()

# ---------------- INPUT ----------------
question = st.text_area(
    "💬 Ask a question",
    placeholder="e.g. How does FAISS work in this project?",
    height=90
)

if st.button("🚀 Ask"):
    if question.strip():
        with st.spinner("Thinking..."):
            answer, contexts = rag.answer(question)

        st.session_state.chat_history.append(
            {
                "question": question,
                "answer": answer,
                "contexts": contexts
            }
        )
    else:
        st.warning("Please enter a question.")

# ---------------- CHAT HISTORY ----------------
st.divider()
st.subheader("🧵 Chat History")

for i, chat in enumerate(reversed(st.session_state.chat_history), 1):
    with st.container():
        st.markdown(f"###  Question {i}")
        st.markdown(chat["question"])

        st.markdown("### 🤖 Answer")
        st.markdown(chat["answer"])

        with st.expander("📂 Retrieved Code Context"):
            for j, c in enumerate(chat["contexts"], 1):
                st.markdown(
                    f"""
**{j}. File:** `{c['file']}`  
**Type:** `{c['type']}`  
**Name:** `{c['name']}`
"""
                )
                st.code(c["code"], language="python")

        st.divider()

st.divider() 
st.caption("Built locally • No cloud calls • Your code stays on your machine")