    import yaml
    from kb_updater.ingest_sources import fetch_sources
    from kb_updater.chunker import chunk_text
    from kb_updater.embedder import Embedder
    from kb_updater.vector_store import FaissStore
    import os
    from tqdm import tqdm

    def load_config(path="config.yaml"):
        with open(path, "r") as f:
            return yaml.safe_load(f)

def run_once(config_path="config.yaml"):
    cfg = load_config(config_path)
    sources = cfg.get("data", {}).get("sources", [])
    ingest_cfg = cfg.get("ingest", {})
    embed_cfg = cfg.get("embedder", {})
    vs_cfg = cfg.get("vector_db", {})

    docs = fetch_sources(sources)
    embedder = Embedder(model_name=embed_cfg.get("model_name", "sentence-transformers/all-MiniLM-L6-v2"))
    # estimate embedding dim from model
    sample_emb = embedder.embed_texts(["hello"])
    dim = sample_emb.shape[1]
    store = FaissStore(index_path=vs_cfg.get("path", "./data/faiss_index"), dim=dim, metadata_db=vs_cfg.get("metadata_db", "./data/metadata.sqlite"))

    to_embed_texts = []
    metadatas = []
    for d in docs:
        chunks = chunk_text(d.get("text", ""), chunk_size=ingest_cfg.get("chunk_size", 800), overlap=ingest_cfg.get("chunk_overlap", 100))
        for ch in chunks:
            chunk_text_str = ch.get("chunk_text", "")
            if len(chunk_text_str) < ingest_cfg.get("min_chunk_length", 50):
                continue
            to_embed_texts.append(chunk_text_str)
            metadatas.append({
                "doc_id": d.get("doc_id"),
                "chunk_id": ch.get("chunk_id"),
                "text": chunk_text_str,
                "fingerprint": d.get("fingerprint"),
                "url": d.get("url"),
                "metadata": {"title": d.get("title")}
            })
    if to_embed_texts:
        import numpy as np
        embs = embedder.embed_texts(to_embed_texts, batch_size=embed_cfg.get("batch_size", 64))
        store.upsert(embs, metadatas)
    else:
        print("No new chunks to embed.")
