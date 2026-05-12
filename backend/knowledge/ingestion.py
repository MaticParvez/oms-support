"""
Document ingestion pipeline: load → chunk → embed → store.
Supports markdown files, plain text, and URLs.
"""
import re
import uuid
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from knowledge.vector_store import add_documents


CHUNK_SIZE = 500       # words per chunk
CHUNK_OVERLAP = 50     # word overlap between chunks


def _chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - overlap
    return chunks


def _clean_markdown(text: str) -> str:
    # Remove HTML tags if any, strip code blocks minimally
    text = re.sub(r"```[\s\S]*?```", "[code block]", text)
    text = re.sub(r"`[^`]+`", lambda m: m.group(0)[1:-1], text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)  # links → text
    text = re.sub(r"#{1,6}\s+", "", text)  # headings
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)  # bold/italic
    return text.strip()


def ingest_text(
    text: str,
    source: str,
    title: str,
    category: str = "general",
    tags: Optional[list[str]] = None,
) -> list[str]:
    cleaned = _clean_markdown(text)
    chunks = _chunk_text(cleaned)
    if not chunks:
        return []

    metadatas = [
        {
            "source": source,
            "title": title,
            "category": category,
            "tags": ",".join(tags or []),
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]
    ids = [f"{source}::{i}::{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    return add_documents(chunks, metadatas, ids)


def ingest_file(path: str, category: str = "general", tags: Optional[list[str]] = None) -> list[str]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = p.read_text(encoding="utf-8")
    return ingest_text(
        text=text,
        source=p.name,
        title=p.stem.replace("_", " ").replace("-", " ").title(),
        category=category,
        tags=tags,
    )


def ingest_url(url: str, category: str = "general", tags: Optional[list[str]] = None) -> list[str]:
    resp = requests.get(url, timeout=15, headers={"User-Agent": "OMS-Support-Bot/1.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    title = soup.title.string if soup.title else url
    text = soup.get_text(separator=" ", strip=True)

    return ingest_text(text=text, source=url, title=title, category=category, tags=tags)


def ingest_directory(dir_path: str, category: str = "docs", glob: str = "**/*.md") -> dict:
    results = {"ingested": 0, "chunks": 0, "errors": []}
    for path in Path(dir_path).glob(glob):
        try:
            ids = ingest_file(str(path), category=category)
            results["ingested"] += 1
            results["chunks"] += len(ids)
        except Exception as e:
            results["errors"].append({"file": str(path), "error": str(e)})
    return results
