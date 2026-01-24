import os
from pathlib import Path
from typing import List
from langchain_community.vectorstores import FAISS

from utils.loadDocs import (
    preparar_documentos,
    _file_hash,
    _load_processed,
    _save_processed,
    _save_docs_cache,
    _load_docs_cache,
)

def build_or_update_index(
    pdf_paths: List[str],
    embeddings,
    index_dir: str = "faiss_index",
    processed_file: str = "json/processed.json",
    docs_cache: str = "json/docs_cache.json",
    chunk: int = 3000,
    overlap: int = 500,
):
    processed = _load_processed(processed_file)
    cached_docs = _load_docs_cache(docs_cache)
    new_docs = []

    for pdf in pdf_paths:
        pdf_path = os.path.normpath(pdf)
        if not os.path.exists(pdf_path):
            continue

        # MODO RÁPIDO: Checa apenas se o caminho do arquivo já existe na lista de processados
        # Se quiser voltar ao modo seguro, use: h = file_hash(pdf_path)
        if pdf_path in processed:
            print(f"✅ Mantido do cache (via nome): {Path(pdf_path).name}")
            continue
        
        # Se não existe, aí sim processamos
        print(f"⚙️ Processando novo arquivo: {Path(pdf_path).name}")
        
        # Precisamos calcular o hash APENAS para salvar no registro (opcional, mas bom pra futuro)
        # Ou podemos salvar apenas "ok" ou data de modificação se não quiser ler o arquivo
        h = _file_hash(pdf_path) 
        
        docs = preparar_documentos(pdf_path, chunk, overlap)
        new_docs.extend(docs)
        processed[pdf_path] = h

    all_docs = cached_docs + new_docs

    db = None
    idx_path = Path(index_dir)
    if idx_path.exists():
        try:
            db = FAISS.load_local(index_dir, embeddings)
        except Exception:
            db = None

    if db is None:
        if not all_docs:
            raise ValueError("Índice inexistente e nenhum documento novo para criar.")
        db = FAISS.from_documents(all_docs, embeddings)
    else:
        if new_docs:
            db.add_documents(new_docs)

    db.save_local(index_dir)
    _save_processed(processed_file, processed)
    _save_docs_cache(docs_cache, all_docs)
    return db, all_docs