from typing import List
from langchain.schema import Document
from utils.search import keyword_search, extract_answer
from utils.output import save_answer_md

def interactive_loop(qa_chain, stuff_chain, all_docs: List[Document], max_results: int = 20, expand_threshold: int = 10):
    while True:
        query = input("👤 Digite sua pergunta: ")
        if query.lower() in ["sair", "exit", "quit"]:
            break

        matched_docs = keyword_search(all_docs, query, keywords=None, source_filter=None, max_results=max_results)
        print(f"[debug] keyword matches: {len(matched_docs)}")

        if matched_docs:
            # se poucos matches, inclua todos os chunks dos mesmos arquivos para ampliar cobertura
            if len(matched_docs) < expand_threshold:
                sources = {d.metadata.get("source") for d in matched_docs}
                expanded = [d for d in all_docs if d.metadata.get("source") in sources]
                # ordenar por source e página
                def _key(d):
                    src = d.metadata.get("source", "")
                    try:
                        p = int(d.metadata.get("page", 10**9))
                    except Exception:
                        p = 10**9
                    return (src, p)
                expanded.sort(key=_key)
                docs_for_chain = expanded
                print(f"[debug] expanded docs to {len(docs_for_chain)} chunks from sources: {sources}")
            else:
                docs_for_chain = matched_docs

            resp = stuff_chain.invoke({"input": query, "context": docs_for_chain})
            docs_for_sources = docs_for_chain
        else:
            resp = qa_chain.invoke({"input": query})
            docs_for_sources = resp.get("context") if isinstance(resp, dict) else []

        answer = extract_answer(resp)
        print("\n🤖 Agente de IA:")
        print(answer, "\n")

        try:
            md_file = save_answer_md(answer, query, docs_for_sources, output_dir="output")
            print(f"✅ Salvo em: {md_file}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar MD: {e}")