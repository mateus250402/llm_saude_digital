from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

def criar_qa_chain_from_retriever(retriever, model_name: str):
    prompt_template = """
Responda à pergunta apenas com base no conteúdo fornecido do documento. Dê respostas completas.
Você é um assistente da área da saúde.
Se a informação aparecer em forma de lista no documento, copie todos os itens.
Se não houver resposta no documento, diga: "Não sei com base no documento."
Sempre exibir o nome do documento e a(s) pagina(s) do PDF de onde a informação foi retirada.
Formatar a resposta em markdown com título e a pergunta feita pelo usuário.

Contexto (trecho do documento): {context}

Pergunta: {input}
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "input"])

    llm = ChatGoogleGenerativeAI(model=model_name)

    stuff_chain = create_stuff_documents_chain(llm=llm, prompt=prompt, document_variable_name="context")

    qa_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=stuff_chain)

    return qa_chain, stuff_chain