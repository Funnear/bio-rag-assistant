import streamlit as st
import asyncio
from preprocess import *
from generate_answer import *

def user_interface(retriever):
    st.title("Biology topic study assistant")
    st.write("Gene expression activation via micro RNA.")

    question = st.text_input("Ask a question:")

    if question:
        with st.spinner("Generating response..."):
            answer = generate_answer_chain(retriever, question)

        st.subheader("Answer to your question:")
        st.write(f"{answer}")  

def main():
    # initialize environment and data
    setup_environment()
    retriever = retrieve_data()

    # get questions
    user_interface(retriever)

if __name__ == '__main__':
    main()

