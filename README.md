# Dynamic Knowledge Base Updater (for GEN---AI-course)

## Project goal
Implement a system to **periodically** ingest documents (RSS, webpages, PDFs), chunk them, compute embeddings, and upsert them into a vector database so a chatbot can use up-to-date information automatically.

## How it works (high level)
- `ingest_sources.py` — fetch sources (rss, webpage, pdf)
- `chunker.py` — split into overlapping chunks
- `embedder.py` — generate embeddings (sentence-transformers)
- `vector_store.py` — store vectors in FAISS + metadata in SQLite
- `pipeline.py` — glue; runs an ingestion pass
- `scheduler.py` — optional long-running scheduler (APScheduler)
- `chatbot.py` — retrieve relevant contexts for queries

## Getting started
1. Create a virtualenv and install requirements:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Update `config.yaml` with your sources.
3. Run once:
   ```bash
   python -c "from kb_updater.pipeline import run_once; run_once('config.yaml')"
   ```
4. Start scheduler (optional):
   ```bash
   python -m kb_updater.scheduler
   ```

## Notebook
See `notebooks/dynamic_kb_demo.ipynb` for a demo with metrics and plots.

## Reproducibility
- Config is in `config.yaml`.
- Documents use SHA1 doc ids and fingerprints.
- Use the embedder/model specified in `config.yaml` for consistent embeddings.

## Notes
- This repo uses FAISS for local experiments. For production, consider Pinecone/Weaviate/Chroma with proper id-based upserts and vector indexing.
- If you want to use OpenAI embeddings instead, set `embedder` to `openai` in config and use `openai.Embedding.create(...)` (store your OPENAI_API_KEY in `.env`).
