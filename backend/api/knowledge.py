"""
Knowledge base management API: ingest documents, search, delete, list stats.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import tempfile, os

from knowledge.ingestion import ingest_text, ingest_url, ingest_directory
from knowledge.vector_store import search, delete_document, count_documents

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class TextIngestRequest(BaseModel):
    text: str
    source: str
    title: str
    category: str = "general"
    tags: Optional[list[str]] = None


class UrlIngestRequest(BaseModel):
    url: str
    category: str = "docs"
    tags: Optional[list[str]] = None


class SearchRequest(BaseModel):
    query: str
    n_results: int = 5
    where: Optional[dict] = None


@router.post("/ingest/text")
def ingest_text_endpoint(req: TextIngestRequest):
    ids = ingest_text(req.text, req.source, req.title, req.category, req.tags)
    return {"chunks_stored": len(ids), "ids": ids}


@router.post("/ingest/url")
def ingest_url_endpoint(req: UrlIngestRequest):
    try:
        ids = ingest_url(req.url, req.category, req.tags)
        return {"chunks_stored": len(ids), "ids": ids}
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch URL: {str(e)}")


@router.post("/ingest/file")
async def ingest_file_endpoint(
    file: UploadFile = File(...),
    category: str = Form("docs"),
    tags: str = Form(""),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    suffix = os.path.splitext(file.filename or "upload.txt")[1] or ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        from knowledge.ingestion import ingest_file
        ids = ingest_file(tmp_path, category=category, tags=tag_list)
        return {"filename": file.filename, "chunks_stored": len(ids)}
    finally:
        os.unlink(tmp_path)


@router.post("/ingest/directory")
def ingest_directory_endpoint(
    dir_path: str,
    category: str = "docs",
    glob: str = "**/*.md",
):
    result = ingest_directory(dir_path, category=category, glob=glob)
    return result


@router.post("/search")
def search_knowledge(req: SearchRequest):
    results = search(req.query, n_results=req.n_results, where=req.where)
    return {"query": req.query, "results": results}


@router.delete("/document/{doc_id}")
def delete_doc(doc_id: str):
    delete_document(doc_id)
    return {"deleted": doc_id}


@router.get("/stats")
def kb_stats():
    return {"total_chunks": count_documents()}
