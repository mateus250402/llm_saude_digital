import os
import shutil
import json
import hashlib
from typing import List
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def reset_index(
    index_dir: str = "faiss_index",
    processed_file: str = "json/processed.json",
    docs_cache: str = "json/docs_cache.json"
):
    """Remove o índice FAISS e arquivos auxiliares, garantindo uma sessão limpa."""
    if os.path.exists(index_dir):
        shutil.rmtree(index_dir)

    if os.path.exists(processed_file):
        os.remove(processed_file)

    if os.path.exists(docs_cache):
        os.remove(docs_cache)

    print("🔄 Índice FAISS resetado com sucesso!\n")

def preparar_documentos(pdf_path: str, chunk: int = 1000, overlap: int = 200) -> List[Document]:
    # Gerencia verificação de cache
    processed_file = "json/processed.json"
    current_hash = _file_hash(pdf_path)
    processed_data = _load_processed(processed_file)

    # Se o arquivo já foi processado e não mudou, retorna vazio
    if processed_data.get(pdf_path) == current_hash:
        print(f"⏭️  Documento já indexado (ignorando): {Path(pdf_path).name}")
        return []

    print(f"📄 Processando novo documento: {Path(pdf_path).name}")

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

    # Atualiza o arquivo de controle com o novo hash
    processed_data[pdf_path] = current_hash
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)
    _save_processed(processed_file, processed_data)

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
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
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