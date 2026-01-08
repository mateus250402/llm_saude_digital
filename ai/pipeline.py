from langchain_huggingface import HuggingFaceEmbeddings
from config.config_ai import configure_ai
from ai.indexUpdate import build_or_update_index
from ai.aiConfig import criar_qa_chain_from_retriever
from utils.inspect import inspect_docs
from utils.loadDocs import reset_index

def run_pipeline(pdf_list):
    configure_ai()

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    reset_index()
    db, all_docs = build_or_update_index(
        pdf_list, 
        embeddings,
        index_dir="faiss_index",
        processed_file="json/processed.json",
        docs_cache="json/docs_cache.json",
        chunk=1000, overlap=200,
    )

    inspect_docs(all_docs)

    retriever = db.as_retriever(search_kwargs={"k": 200})
    qa_chain, stuff_chain = criar_qa_chain_from_retriever(
        retriever, model_name="gemini-flash-lite-latest"
    )

    return qa_chain, stuff_chain, all_docs