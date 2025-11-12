from kb_updater.embedder import Embedder
from kb_updater.vector_store import FaissStore
import yaml

def answer_query(query, k=5, config_path="config.yaml"):
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    ed = Embedder(model_name=cfg.get("embedder", {}).get("model_name", "sentence-transformers/all-MiniLM-L6-v2"))
    sample = ed.embed_texts([query])
    store = FaissStore(index_path=cfg.get("vector_db", {}).get("path", "./data/faiss_index"), metadata_db=cfg.get("vector_db", {}).get("metadata_db", "./data/metadata.sqlite"))
    results = store.search(sample, k=k)
    context_texts = [r["text"] for r in results]
    return {"query": query, "context": context_texts, "sources": [r.get("url") for r in results]}
