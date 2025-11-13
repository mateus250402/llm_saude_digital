import datetime
from pathlib import Path
from typing import List
from langchain.schema import Document

def _format_sources(docs: List[Document]):
    if not docs:
        return ""
    seen = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", None)
        key = f"{src} | Página: {page}"
        if key not in seen:
            seen.append(key)
    return "\n".join(f"- {s}" for s in seen)

def save_answer_md(answer: str, question: str, docs: List[Document], output_dir: str = "output") -> str:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_path / f"answer_{timestamp}.md"
    sources_md = _format_sources(docs)
    md = f"# Resposta gerada\n\n**Pergunta:** {question}\n\n**Resposta:**\n\n{answer}\n\n"
    if sources_md:
        md += f"**Fontes:**\n\n{sources_md}\n"
    filename.write_text(md, encoding="utf-8")
    return str(filename)