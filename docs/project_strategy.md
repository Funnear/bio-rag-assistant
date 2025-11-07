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
- Add Back-End layer (Flask or FastAPI):
  - a reusable REST API (e.g., other apps/tools call your RAG),
  - multi-user access with auth/rate-limits,
  - background jobs/queues (long ingests, scheduled crawls),
  - separate frontends (web/mobile) or remote deployment.

# Future perspectives

- Support data inputs and responses in multiple languages. For instance: Russian speaking researcher learns from articles published in German.