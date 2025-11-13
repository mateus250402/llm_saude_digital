from langchain_huggingface import HuggingFaceEmbeddings
from config.config_ai import configure_ai
from utils.indexUpdate import build_or_update_index
from utils.aiConfig import criar_qa_chain_from_retriever
from utils.aiTalk import interactive_loop
from utils.inspect import inspect_docs

def main():
    configure_ai()

    pdf_list = [
        "pdf/teste_grande.pdf",
        # adicionar outros PDFs aqui
    ]

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    db, all_docs = build_or_update_index(
        pdf_list,
        embeddings,
        index_dir="faiss_index",
        processed_file="processed.json",
        docs_cache="docs_cache.json",
        chunk=1000,
        overlap=200,
    )
    
    inspect_docs(all_docs)

    retriever = db.as_retriever(search_kwargs={"k": 200})
    qa_chain, stuff_chain = criar_qa_chain_from_retriever(retriever, model_name="gemini-2.5-flash")

    interactive_loop(qa_chain, stuff_chain, all_docs, max_results=2000)

if __name__ == "__main__":
    main()