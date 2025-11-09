# project libs
from env_handler import load_paths
from state_machine import KBState, detect_kb_state
from streamlit_app import *


def main():
    # initialize environment and data
    datasets_dir, chroma_dir, metadata_path = load_paths()

    # define KB state
    kb_state, kb_info = detect_kb_state(datasets_dir, metadata_path)
    print(f"Knowledge Base State: {kb_state.name}")

    # setup common GUI elements
    init_user_interface()

    # act according to state
    if kb_info["total_pdfs"] > 0:
        processed = kb_info["processed"]
        total = kb_info["total_pdfs"]
        
        # display global KB status indicator
        kb_status_indicator(processed, total)

    if kb_state in (KBState.NO_DATA, KBState.EMPTY):
        show_quick_start(datasets_dir)

    elif kb_state in (KBState.UP_TO_DATE, KBState.OUTDATED):
        show_main_tabs(datasets_dir, kb_info)    

if __name__ == '__main__':
    main()

