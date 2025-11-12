import hashlib
import logging
from typing import Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def doc_id_from_url(url: str) -> str:
    """Deterministic id for a document (used for upserts)."""
    return hashlib.sha1(url.encode("utf-8")).hexdigest()

def text_fingerprint(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()

def ensure_dirs(path):
    import os
    os.makedirs(path, exist_ok=True)
