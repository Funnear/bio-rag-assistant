import time
import re
from urllib.parse import quote

import streamlit as st

# project libs
from generate_answer import generate_answer_chain
from preprocess import init_ingest, ingest_new_data, restore_from_cache

def add_reference_links(answer: str) -> str:
    """Convert italic references in the References section into Scholar links."""

    # Split into main body and references section
    marker = "**References:**"
    if marker not in answer:
        # No references section -> return unchanged
        return answer

    body, refs_block = answer.split(marker, maxsplit=1)

    # Process references block line by line
    lines = refs_block.splitlines()
    new_lines = []

    # Pattern: italic text with a year, but only within a single line
    pattern = re.compile(r"\*([^*\n]+?\d{4}[^*\n]*)\*")

    for line in lines:
        match = pattern.search(line)
        if not match:
            new_lines.append(line)
            continue

        ref_text = match.group(1).strip()
        url = f"https://scholar.google.com/scholar?q={quote(ref_text)}"

        # Replace only this specific italic reference in this line
        old = f"*{ref_text}*"
        new = f"*[{ref_text}]({url})*"
        new_lines.append(line.replace(old, new, 1))

    refs_block_new = "\n".join(new_lines)

    # Reassemble full answer
    return body + marker + refs_block_new

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

def kb_status_indicator(processed, total):
    if total <= 0:
        raise ValueError("Parameter 'total' must be a positive integer greater than 0.")

    with st.container():
        coverage_ratio = processed / total
        coverage_percent = int(coverage_ratio * 100)

        st.markdown("**Knowledge base status**")
        st.progress(coverage_ratio)  # value between 0.0 and 1.0
        st.caption(f"{coverage_percent}%  ({processed}/{total} documents processed)")

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
        start = time.time()
        with st.spinner("Generating response..."):
            answer = generate_answer_chain(retriever, question)
        elapsed = time.time() - start

        st.subheader("Answer to your question:")

        answer = add_reference_links(answer)
        st.markdown(answer, unsafe_allow_html=True)

        st.caption(f"✅ Response generated in {elapsed:.2f} seconds")

def show_kb_tab(datasets_dir, kb_info):
    st.caption("Knowledge Base control")

    total = kb_info["total_pdfs"]
    processed = kb_info["processed"]
    new_files = kb_info.get("new_files", [])
    changed_files = kb_info.get("changed_files", [])

    st.write(f"Dataset folder: `{datasets_dir}`")
    st.write(f"Total PDFs: {total}")
    st.write(f"Processed: {processed}")

    # --- Determine if KB needs update and store in session state ---
    needs_update = bool(new_files or changed_files)
    st.session_state["kb_needs_update"] = needs_update

    # --- New files list (collapsible if more than 1, hidden if none) ---
    if new_files:
        if len(new_files) > 1:
            with st.expander("🆕 New files detected", expanded=True):
                st.markdown("\n".join(f"- {name}" for name in new_files))
        else:
            st.markdown("**🆕 New file detected:**")
            st.markdown(f"- {new_files[0]}")

    # --- Changed files list (collapsible if more than 1, hidden if none) ---
    if changed_files:
        if len(changed_files) > 1:
            with st.expander("🔁 Changed files", expanded=True):
                st.markdown("\n".join(f"- {name}" for name in changed_files))
        else:
            st.markdown("**🔁 Changed file:**")
            st.markdown(f"- {changed_files[0]}")

    # --- Init session flags if missing ---
    if "kb_updating" not in st.session_state:
        st.session_state["kb_updating"] = False
    if "retriever" not in st.session_state:
        st.session_state["retriever"] = None

    # --- Update button (disabled if nothing to update) ---
    btn_label = "Update knowledge base"
    if needs_update:
        btn_help = "Process new/changed PDFs and update the index."
    else:
        btn_help = "Knowledge base is already up to date."

    if st.button(btn_label, disabled=not needs_update, help=btn_help):
        st.session_state["kb_updating"] = True
        with st.spinner("Detecting and processing new items..."):
            new_retriever = ingest_new_data()
        st.session_state["retriever"] = new_retriever
        st.session_state["kb_updating"] = False
        st.success(
            "Knowledge base updated successfully! "
            "You can now ask questions in the Assistant tab."
        )
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
