from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def generate_answer_chain(retriever, question):
    # LLM
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0.2)

    # Prompt (concise + citations)
    prompt = ChatPromptTemplate.from_template(
        """
        You are a concise scientific research assistant with expertise in {topic}.
        Your goal is to provide **a concise, factual, and well-structured scientific summary** formatted for Markdown display.

        **Question:** {question}

        **Context from peer-reviewed sources:**
        {context}

        ---

        Write your answer as a structured scientific summary following these rules:

        - Begin with **Short Answer:** — a short bullet list containing only the names of the main proteins, molecules, or entities that directly answer the question.
        - Continue with **Overview:** (on a new line) — 1–3 sentences summarizing the mechanism or concept.
        - Then include **Relevant processes and protein components:** — bullet points describing key mechanisms, molecules, or interactions.
        - Then include **Limitations:** — 1–2 sentences describing study limitations or missing information.
        - Finish with  **References:** — each reference should appear as a bullet, formatted in *italic Harvard style* (e.g., *Vasudevan et al. 2007, Science, 318:1931–1934*).
        - Use Markdown formatting:
        - Bold headers followed by a colon (**Header:**)
        - Bullet lists using “- ”
        - Italic text for references
        - Maintain an academic, factual tone — no speculation or general knowledge outside the context.
        - If evidence is insufficient, explicitly state that data in the provided context is limited.
        - Do NOT fabricate or infer references beyond the context.

        Now produce the answer:
        """
    )

    topic = "Gene expression activation via microRNA"

    docs = retriever.invoke(question)

    def format_docs(docs):
        return "\n\n".join(
            f"[{i+1}] {d.page_content}\nMETA: {d.metadata}"
            for i, d in enumerate(docs)
        )

    inputs = {
        "context": retriever | format_docs,       # Retrieves and formats source docs
        "question": RunnablePassthrough(),        # Passes user query directly
        "topic": RunnablePassthrough(lambda _: topic),  # Optional thematic context
    }

    chain = inputs | prompt | llm | StrOutputParser()

    answer = chain.invoke(input=question)

    return answer

