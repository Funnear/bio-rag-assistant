from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def generate_answer_chain(retriever, question):
    # LLM
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0.25)

    # Prompt (concise + citations)
    prompt = ChatPromptTemplate.from_template(
        """You are a concise scientific assistant. Use ONLY the context.
    If unsure, say: "The provided context does not contain this information."
    Answer in ≤120 words, with Harvard-style citation(s) at the end.

    Question: {question}

    Context:
    {context}

    Format:
    - Short answer
    - Harvard citation(s): (Author Year, Journal, pages/DOI)
    """
    )

    # Chain: retrieve -> stuff -> generate
    docs = retriever.invoke(question)

    def format_docs(docs):
        return "\n\n".join(
            f"[{i+1}] {d.page_content}\nMETA: {d.metadata}"
            for i, d in enumerate(docs)
        )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(input=question)

    return answer

