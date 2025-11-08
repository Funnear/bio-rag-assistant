import streamlit as st

# project libs
from generate_answer import generate_answer_chain
from preprocess import init_ingest, ingest_new_data, restore_from_cache

def init_user_interface():
    # page config
    st.set_page_config(
        page_title="🧬 Bio RAG Assistant",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get help": "https://github.com/Funnear/bio-rag-assistant/tree/main/docs",
            "Report a bug": "https://github.com/Funnear/bio-rag-assistant/issues",
            "About": """
Bio RAG Assistant 🧬
A Streamlit app to assist biology topic study using Retrieval-Augmented Generation (RAG) techniques.

For more information, see the project [presentation (PDF)](https://github.com/Funnear/bio-rag-assistant/blob/main/presentation/Presentation.pdf) in the GitHub repository:

Author: [Faniia Prazdnikova](https://www.linkedin.com/in/faniia-prazdnikova-607a6a3b/)
            """,
        }
    )
    # subtitle / smaller text in UI
    st.title("🧬 Biology topic study assistant")
    st.subheader("Gene expression activation via microRNA")

def kb_status_indicator(coverage, processed, total):
    st.info(f"Knowledge base status: {coverage}% ({processed}/{total} documents processed)")

def show_quick_start(datasets_dir):
    st.caption("Quick start")

    st.write(
        "Before you can ask biology questions, the assistant needs to read your PDF materials "
        "about gene expression activation via microRNA."
    )

    st.markdown("**Current dataset folder:**")
    st.code(str(datasets_dir))

    st.write("Add one or more PDF files to this folder, then click the button below.")

    if st.button("Scan and build knowledge base"):
        with st.spinner("Initializing ingestion..."):
            retriever = init_ingest()
        st.success("Knowledge base built successfully! You can now ask questions in the Assistant tab.")
        show_qa_tab(retriever)

def show_qa_tab():
    st.caption("Assistant")

    if st.session_state.get("kb_updating", False):
        st.info("Knowledge base is being updated. Please wait until the update is finished.")
        return

    retriever = st.session_state.get("retriever")
    if retriever is None:
        st.warning("Knowledge base is not ready yet. Go to the Knowledge Base tab to initialize it.")
        return

    question = st.text_input("Ask a question:")
    if question:
        with st.spinner("Generating response..."):
            answer = generate_answer_chain(retriever, question)
        st.subheader("Answer to your question:")
        st.write(answer)

def show_kb_tab(datasets_dir, kb_info):
    st.caption("Knowledge Base control")
    st.write(f"Dataset folder: `{datasets_dir}`")
    st.write(f"Total PDFs: {kb_info['total_pdfs']}")
    st.write(f"Processed: {kb_info['processed']}")
    st.write(f"New files: {kb_info['new_files']}")
    st.write(f"Changed files: {kb_info['changed_files']}")

    if "kb_updating" not in st.session_state:
        st.session_state["kb_updating"] = False
    if "retriever" not in st.session_state:
        st.session_state["retriever"] = None

    if st.button("Update knowledge base"):
        st.session_state["kb_updating"] = True
        with st.spinner("Detecting and processing new items..."):
            new_retriever = ingest_new_data()
        st.session_state["retriever"] = new_retriever
        st.session_state["kb_updating"] = False
        st.success("Knowledge base updated successfully! You can now ask questions in the Assistant tab.")
        st.rerun()

def show_main_tabs(datasets_dir, kb_info):
    # restore retriever from cache
    if "retriever" not in st.session_state:
        st.session_state["retriever"] = restore_from_cache()

    # define tabs
    global tab_qa, tab_kb
    tab_qa, tab_kb = st.tabs(["👩‍🔬 Assistant", "📚 Knowledge Base"])

    with tab_qa:
        show_qa_tab()

    with tab_kb:
        show_kb_tab(datasets_dir, kb_info)
