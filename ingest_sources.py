import feedparser
import requests
from newspaper import Article
import pdfplumber
from bs4 import BeautifulSoup
from kb_updater.utils import doc_id_from_url, text_fingerprint
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

def fetch_rss(url):
    feed = feedparser.parse(url)
    items = []
    for e in feed.entries:
        title = e.get("title", "")
        link = e.get("link", "")
        summary = e.get("summary", "")
        content = title + "\n\n" + summary
        items.append({"url": link, "title": title, "text": content})
    return items

def fetch_webpage(url):
    try:
        a = Article(url)
        a.download()
        a.parse()
        title = a.title or ""
        text = a.text or ""
        return {"url": url, "title": title, "text": text}
    except Exception as e:
        logger.exception("webpage fetch failed")
        # fallback: requests + BeautifulSoup
        r = requests.get(url, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(separator="\n")
        title = soup.title.string if soup.title else ""
        return {"url": url, "title": title, "text": text}

def fetch_pdf(url):
    r = requests.get(url, stream=True, timeout=30)
    r.raise_for_status()
    tmp = "/tmp/tmp_doc.pdf"
    with open(tmp, "wb") as f:
        f.write(r.content)
    text = ""
    with pdfplumber.open(tmp) as pdf:
        for p in pdf.pages:
            page_text = p.extract_text()
            if page_text:
                text += page_text + "\n"
    return {"url": url, "title": url.split("/")[-1], "text": text}

def fetch_sources(sources_config):
    docs = []
    for s in sources_config:
        t = s.get("type")
        url = s.get("url")
        try:
            if t == "rss":
                docs.extend(fetch_rss(url))
            elif t == "webpage":
                docs.append(fetch_webpage(url))
            elif t == "pdf":
                docs.append(fetch_pdf(url))
            else:
                logger.warning("Unknown source type %s", t)
        except Exception as e:
            logger.exception("Failed to fetch %s", url)
    # add doc_id and fingerprint
    for d in docs:
        d["doc_id"] = doc_id_from_url(d.get("url", ""))
        d["fingerprint"] = text_fingerprint(d.get("text", ""))
    return docs
