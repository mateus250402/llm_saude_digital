import os
import json
import hashlib
from typing import List
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def preparar_documentos(pdf_path: str, chunk: int = 1000, overlap: int = 200) -> List[Document]:
    loader = PyPDFLoader(pdf_path)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk, chunk_overlap=overlap)
    try:
        docs = loader.load_and_split(text_splitter=splitter)
    except TypeError:
        docs = loader.load_and_split(splitter)
    if not docs:
        return []

    def _page_key(d):
        p = d.metadata.get("page", None)
        try:
            return int(p)
        except Exception:
            return 10**9

    docs.sort(key=_page_key)

    for doc in docs:
        page = doc.metadata.get("page", None)
        source = doc.metadata.get("source", Path(pdf_path).name)
        doc.page_content = f"Fonte: {source} | Página do leitor: {page}\n\n{doc.page_content}"

    return docs

def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def _load_processed(path: str):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _save_processed(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _save_docs_cache(path: str, docs: List[Document]):
    serial = [{"page_content": d.page_content, "metadata": d.metadata} for d in docs]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serial, f, ensure_ascii=False, indent=2)

def _load_docs_cache(path: str) -> List[Document]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Document(page_content=item["page_content"], metadata=item.get("metadata", {})) for item in raw]