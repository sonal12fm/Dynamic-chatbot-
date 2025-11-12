import faiss
import numpy as np
import os
import sqlite3
import json
from kb_updater.utils import ensure_dirs
from typing import List, Dict

class FaissStore:
    def __init__(self, index_path="./data/faiss_index", dim=384, metadata_db="./data/metadata.sqlite"):
        ensure_dirs(os.path.dirname(index_path) or ".")
        self.index_path = index_path
        self.metadata_db = metadata_db
        self.dim = dim
        if os.path.exists(index_path):
            try:
                self.index = faiss.read_index(index_path)
            except Exception:
                # fallback: recreate
                self.index = faiss.IndexFlatL2(dim)
        else:
            self.index = faiss.IndexFlatL2(dim)
        # metadata sqlite
        self.conn = sqlite3.connect(metadata_db)
        self._init_db()

        self.next_id = self._get_next_id()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            doc_id TEXT,
            chunk_id TEXT,
            text TEXT,
            fingerprint TEXT,
            url TEXT,
            metadata TEXT
        )
        """)
        self.conn.commit()

    def _get_next_id(self):
        c = self.conn.cursor()
        c.execute("SELECT MAX(id) FROM chunks")
        row = c.fetchone()
        if row and row[0] is not None:
            return row[0] + 1
        return 0

    def upsert(self, embeddings: np.ndarray, metadatas: List[Dict]):
        n, d = embeddings.shape
        ids = None
        # FAISS IndexFlatL2 doesn't support ids, so we simply add embeddings.
        # For ID'd indexes, use IndexIDMap or IndexHNSWFlat and pass ids.
        if isinstance(self.index, faiss.IndexFlatL2):
            self.index.add(embeddings)
        else:
            # this path assumes index supports add_with_ids
            ids = np.arange(self.next_id, self.next_id + n).astype(np.int64)
            self.index.add_with_ids(embeddings, ids)
        # store metadata rows
        c = self.conn.cursor()
        for i, md in enumerate(metadatas):
            metadata_json = json.dumps(md.get("metadata", {}))
            c.execute("INSERT INTO chunks (id, doc_id, chunk_id, text, fingerprint, url, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (int(self.next_id + i), md.get("doc_id"), md.get("chunk_id"), md.get("text"), md.get("fingerprint"), md.get("url"), metadata_json))
        self.conn.commit()
        self.next_id += n
        # save index
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception:
            pass

    def search(self, query_emb: np.ndarray, k=5):
        D, I = self.index.search(query_emb, k)
        results = []
        c = self.conn.cursor()
        for dist_row, idx_row in zip(D[0], I[0]):
            if idx_row == -1:
                continue
            c.execute("SELECT doc_id, chunk_id, text, fingerprint, url, metadata FROM chunks WHERE id=?", (int(idx_row),))
            row = c.fetchone()
            if row:
                results.append({
                    "id": int(idx_row),
                    "doc_id": row[0],
                    "chunk_id": row[1],
                    "text": row[2],
                    "fingerprint": row[3],
                    "url": row[4],
                    "metadata": json.loads(row[5]) if row[5] else {}
                })
        return results
