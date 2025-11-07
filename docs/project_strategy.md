# Business goal

# Thematical scope

Gene expression activation via micro RNA.

# POC

# MVP

- Use web-scraping or ChatGPT-5 for finding new articles on the specified subject. 
- Resources to consider: PubMed, ResearchGate, SpringerLink, Nature, ScienceDirect, Google Scholar.
- Multimodal extension later: use separate embedding models for text and image embeddings. Store both in the vector DB with a shared dimensionality.
- Introduce reranker for better answer precision: 
  - Query → Embedding → Vector DB → Top-k chunks → **Reranker** → Top-n (best) chunks → LLM

# Future perspectives

- Support data inputs and responses in multiple languages. For instance: Russian speaking researcher learns from articles published in German.