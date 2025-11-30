from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

def criar_qa_chain_from_retriever(retriever, model_name: str):
    prompt_template = """
    Você é um assistente da área da saúde.
    Use apenas informações encontradas no documento.
    Se não souber, responda: "Não sei com base no documento".
    Absolutamente sempre informe a fonte da informação no formato (nome_do_documento, número_das_páginas) ao final, ou (número_da_página) no corpo do texto se julgar necessário, se em nome_do_documento estiver "pdf/..." pode omitir "pdf/".

    Contexto:
    {context}

    Pergunta: {input}
    """

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "input"])

    llm = ChatGoogleGenerativeAI(model=model_name)

    stuff_chain = create_stuff_documents_chain(llm=llm, prompt=prompt, document_variable_name="context")

    qa_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=stuff_chain)

    return qa_chain, stuff_chain