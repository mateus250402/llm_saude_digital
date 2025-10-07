from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
import os
import warnings

warnings.filterwarnings("ignore")

os.environ["GOOGLE_API_KEY"] = "AIzaSyCNEiMNGmgfh_cL8Xr89xnc7PsMfeIvsEc"

# Carregar PDF
loader = PyPDFLoader("teste_grande.pdf")
docs = loader.load() 

# Dividir em chunks menores para melhorar a busca
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = splitter.split_documents(docs)
if not docs:
    raise ValueError("Nenhum documento foi carregado ou o PDF está vazio.")

# Criar embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Banco vetorial
db = FAISS.from_documents(docs, embeddings)

# Retriever que pega mais trechos relevantes
retriever = db.as_retriever(search_kwargs={"k": 1000})

# Prompt flexível para qualquer pergunta
prompt_template = """
Responda à pergunta apenas com base no conteúdo fornecido do documento.
Você é um assistente da área da saúde.
Se a informação aparecer em forma de lista no documento, copie todos os itens.
Se não houver resposta no documento, diga: "Não sei com base no documento."
Sempre exibir o nome do documento e a(s) pagina(s) do PDF de onde a informação foi retirada, essa página é a do leitor de PDF, desconsidere a paginação do documento.
Formatar a resposta em markdown com título e a pergunta feita pelo usuário."

Contexto (trecho do documento): {context}

Pergunta: {input}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "input"],
)

# Conectar LLM Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Cadeia moderna de QA
stuff_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=prompt,
    document_variable_name="context"
)

qa_chain = create_retrieval_chain(
    retriever=retriever,
    combine_docs_chain=stuff_chain
)

# Histórico
historico = []

# Loop
while True:
    query = input("👤 Digite sua pergunta: ")

    if query.lower() in ["sair", "exit", "quit"]:
        print("Encerrando...")
        break

    resposta = qa_chain.invoke({"input": query})

    print("\n🤖 Agente de IA:")
    print(resposta['answer'], "\n")

    historico.append({"pergunta": query, "resposta": resposta['answer']})