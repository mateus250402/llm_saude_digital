import os
import warnings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

warnings.filterwarnings("ignore")

def configure_ai():
    os.environ["GOOGLE_API_KEY"] = "AIzaSyCNEiMNGmgfh_cL8Xr89xnc7PsMfeIvsEc"

def preparar_documentos(pdf_path, chunk, overlap):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk, chunk_overlap=overlap)
    docs = splitter.split_documents(docs)
    if not docs:
        raise ValueError("Nenhum documento foi carregado ou o PDF está vazio.")
    # Adiciona nome do documento e página do leitor ao início do conteúdo de cada chunk
    for doc in docs:
        page = doc.metadata.get("page", None)
        source = doc.metadata.get("source", pdf_path)
        doc.page_content = f"Fonte: {source} | Página do leitor: {page}\n{doc.page_content}"
    return docs

def criar_qa_chain(docs, model_name, k):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embeddings)
    retriever = db.as_retriever(search_kwargs={"k": k})

    prompt_template = """
        Responda à pergunta apenas com base no conteúdo fornecido do documento.
        Você é um assistente da área da saúde.
        Se a informação aparecer em forma de lista no documento, copie todos os itens.
        Se não houver resposta no documento, diga: "Não sei com base no documento."
        Sempre exibir o nome do documento e a(s) pagina(s) do PDF de onde a informação foi retirada, essa página é a do leitor de PDF, desconsidere a paginação do documento.
        Formatar a resposta em markdown com título e a pergunta feita pelo usuário.

        Contexto (trecho do documento): {context}

        Pergunta: {input}
    """
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "input"],
    )

    llm = ChatGoogleGenerativeAI(model=model_name)
    
    stuff_chain = create_stuff_documents_chain(
        llm=llm,
        prompt=prompt,
        document_variable_name="context"
    )
    
    qa_chain = create_retrieval_chain(
        retriever=retriever,
        combine_docs_chain=stuff_chain
    )
    
    return qa_chain

def main():
    configure_ai()
    pdf_path = "teste_grande.pdf"
    docs = preparar_documentos(pdf_path, chunk=1000, overlap=200)
    qa_chain = criar_qa_chain(docs, model_name="gemini-2.5-flash", k=100)
    historico = []

    while True:
        query = input("👤 Digite sua pergunta: ")
        if query.lower() in ["sair", "exit", "quit"]:
            print("Encerrando...")
            break
        resposta = qa_chain.invoke({"input": query})
        print("\n🤖 Agente de IA:")
        print(resposta['answer'], "\n")
        historico.append({"pergunta": query, "resposta": resposta['answer']})

if __name__ == "__main__":
    main()