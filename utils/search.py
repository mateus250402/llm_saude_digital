from typing import List, Optional
from langchain.schema import Document
from typing import List, Optional
from langchain.schema import Document

def keyword_search(docs: List[Document], query: str, keywords: Optional[List[str]] = None, source_filter: Optional[str] = None, max_results: Optional[int] = None) -> List[Document]:
    q_lower = query.lower()
    tokens = [t for t in q_lower.split() if len(t) > 2]
    if keywords is None:
        keywords = []
    matches = []
    for doc in docs:
        if source_filter and source_filter not in str(doc.metadata.get("source", "")).lower():
            continue
        text = (doc.page_content or "").lower()
        if any(kw.lower() in text for kw in keywords) or any(tok in text for tok in tokens):
            matches.append(doc)
    # ordenar por source e página (se existir) para ter páginas em ordem
    def _key(d):
        src = d.metadata.get("source", "")
        try:
            p = int(d.metadata.get("page", 10**9))
        except Exception:
            p = 10**9
        return (src, p)
    matches.sort(key=_key)
    if max_results is None:
        return matches
    return matches[:max_results]

def extract_answer(resp):
    if isinstance(resp, dict):
        return resp.get("answer") or resp.get("result") or resp.get("output") or str(resp)
    return str(resp)