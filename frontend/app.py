# frontend/app.py
import streamlit as st
import requests
import os
from llm.generator import generate_answer
from vectorstore.store import get_collection, get_collection_stats

BACKEND_URL = os.environ.get("GYANSETU_API_URL", "http://localhost:8000")

# ── URLs for auto-ingestion on cold start ─────────────────────
URLS = [
    "https://en.wikipedia.org/wiki/Chevening_Scholarship",
    "https://en.wikipedia.org/wiki/Commonwealth_Scholarship",
    "https://en.wikipedia.org/wiki/DAAD",
    "https://en.wikipedia.org/wiki/Fulbright_Program",
    "https://en.wikipedia.org/wiki/Erasmus_Programme",
    "https://en.wikipedia.org/wiki/University_of_Toronto",
    "https://en.wikipedia.org/wiki/University_of_British_Columbia",
    "https://en.wikipedia.org/wiki/National_University_of_Singapore",
    "https://en.wikipedia.org/wiki/University_of_Melbourne",
    "https://en.wikipedia.org/wiki/Google_Scholar",
    "https://en.wikipedia.org/wiki/ArXiv",
    "https://en.wikipedia.org/wiki/Semantic_Scholar",
    "https://en.wikipedia.org/wiki/Student_visa",
    "https://en.wikipedia.org/wiki/International_student",
]


@st.cache_resource
def load_or_build_database():
    """
    Runs once when the app starts.
    If ChromaDB is empty, ingests all documents automatically.
    This handles cold starts on Hugging Face Spaces.
    """
    from ingestion.ingest_pipeline import ingest_urls

    collection = get_collection()
    stats = get_collection_stats(collection)

    if stats["total_chunks"] == 0:
        ingest_urls(URLS)
        stats = get_collection_stats(collection)

    return stats


# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="GyanSetu — জ্ঞানের সেতু",
    page_icon="🎓",
    layout="wide"
)
# Run on every cold start — cached so only runs once
load_or_build_database()
# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/emoji/96/graduation-cap-emoji.png", width=60)
    st.title("GyanSetu")
    st.caption("জ্ঞানের সেতু — Bridge to Knowledge")
    st.divider()

    # Corpus stats
    st.markdown("### 📊 Knowledge Base")
    try:
        collection = get_collection()
        stats = get_collection_stats(collection)
        st.metric("Total Chunks", stats["total_chunks"])
        st.metric("Documents Indexed", "14")
    except:
        st.caption("Knowledge base loading...")

    st.divider()
    st.markdown("### 📚 Topics Covered")
    st.markdown("""
- 🏆 Scholarships
- 🎓 University Admissions
- 🔬 Research Databases
- ✈️ Student Visa & Living Costs
- 🌍 Studying Abroad
    """)

    st.divider()
    st.markdown("### 🌐 Supported Languages")
    st.markdown("🇬🇧 English  |  🇧🇩 বাংলা")

    st.divider()
    st.markdown("### 🌍 Ingest a URL")
    ingest_url = st.text_input(
        "Paste any URL to add its content to the knowledge base",
        placeholder="https://example.com/article",
        label_visibility="collapsed",
    )
    if st.button("📥 Ingest URL", type="primary", use_container_width=True):
        if not ingest_url:
            st.error("Please enter a URL first.")
        else:
            with st.spinner("Scraping, chunking, and embedding..."):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/ingest-url",
                        json={"url": ingest_url},
                        timeout=120,
                    )
                    data = resp.json()
                    if resp.status_code == 200:
                        if data["chunks_added"]:
                            st.success(
                                f"✅ Added {data['chunks_added']} chunks "
                                f"from your URL to the knowledge base."
                            )
                        else:
                            st.info(f"ℹ️ {data['message']}")
                    else:
                        st.error(f"❌ {data['detail']}")
                except requests.ConnectionError:
                    st.error("❌ Could not reach the API server. Is it running?")
                except Exception as e:
                    st.error(f"❌ Something went wrong: {str(e)}")

    st.divider()
    st.markdown("### 📄 Upload a PDF")
    uploaded_file = st.file_uploader(
        "Upload a PDF to add to the knowledge base",
        type="pdf",
        label_visibility="collapsed",
    )
    if st.button("📄 Ingest PDF", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.error("Please select a PDF file first.")
        else:
            with st.spinner("Extracting, chunking, and embedding..."):
                try:
                    file_bytes = uploaded_file.read()
                    resp = requests.post(
                        f"{BACKEND_URL}/ingest-pdf",
                        files={"file": (uploaded_file.name,
                                        file_bytes, "application/pdf")},
                        timeout=120,
                    )
                    data = resp.json()
                    if resp.status_code == 200:
                        if data["chunks_added"]:
                            st.success(
                                f"✅ Added {data['chunks_added']} chunks "
                                f"from your PDF to the knowledge base."
                            )
                        else:
                            st.info(f"ℹ️ {data['message']}")
                    else:
                        st.error(f"❌ {data['detail']}")
                except requests.ConnectionError:
                    st.error("❌ Could not reach the API server. Is it running?")
                except Exception as e:
                    st.error(f"❌ Something went wrong: {str(e)}")

    st.divider()
    st.caption(
        "Built with LangChain · ChromaDB · "
        "HuggingFace · Groq · Streamlit"
    )

# ── Main area ─────────────────────────────────────────────────
st.title("🎓 GyanSetu — জ্ঞানের সেতু")
st.markdown("**RAG Powered Research Assistant for Bangladeshi Students**")
st.divider()

# ── Example questions ─────────────────────────────────────────
with st.expander("💡 Example questions — click to expand"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🇬🇧 English**")
        st.markdown("""
- What is the Chevening scholarship?
- How does the Fulbright scholarship work?
- What is the acceptance rate at UBC?
- How does Google Scholar help researchers?
- What is a student visa?
        """)
    with col2:
        st.markdown("**🇧🇩 বাংলা**")
        st.markdown("""
- ফুলব্রাইট বৃত্তি কি?
- শেভেনিং বৃত্তির যোগ্যতার শর্ত কি?
- গুগল স্কলার কিভাবে কাজ করে?
- কানাডায় পড়াশোনার জন্য কি লাগে?
- ইরাসমাস প্রোগ্রাম কি?
        """)

# ── Chat history ──────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Query input ───────────────────────────────────────────────
query = st.chat_input(
    "Ask your question in English or Bangla..."
)

# ── Process query ─────────────────────────────────────────────
if query and query.strip():
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": query
    })

    with st.spinner("Searching knowledge base..."):
        try:
            result = generate_answer(query)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
                "language": result["language"],
                "chunks": len(result["chunks"])
            })
        except Exception as e:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Something went wrong: {str(e)}",
                "sources": [],
                "language": "en",
                "chunks": 0
            })

# ── Render chat history ───────────────────────────────────────
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="🎓"):
            # Language and chunks info
            lang = "🇧🇩 Bangla" if message["language"] == "bn" else "🇬🇧 English"
            st.caption(f"{lang} · {message['chunks']} chunks retrieved")

            # Answer
            st.markdown(message["content"])

            # Sources
            if message["sources"]:
                with st.expander("📚 Sources"):
                    for source in message["sources"]:
                        st.markdown(f"- [{source}]({source})")

# ── Empty state ───────────────────────────────────────────────
if not st.session_state.chat_history:
    st.info(
        "👋 Welcome to GyanSetu! Type your question below "
        "in English or Bangla to get started."
    )

# ── Footer ────────────────────────────────────────────────────
st.divider()
st.caption(
    "⚠️ GyanSetu answers are grounded in indexed documents. "
    "Always verify scholarship and visa information from official sources."
)
