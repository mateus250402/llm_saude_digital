from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain

def criar_qa_chain_from_retriever(retriever, model_name: str):
    prompt_template = """
    Você é um assistente especializado em protocolos de Saúde Digital e Atenção Primária.
    Sua função é ler os documentos fornecidos no contexto e responder à pergunta do usuário com precisão clínica e administrativa.

    ---
    
    ### REGRAS OBRIGATÓRIAS:
    1. **Fidelidade Estrita ao Contexto:** Responda APENAS com base nos trechos fornecidos abaixo em "Contexto". Não use conhecimento externo prévio.
    2. **Sem Alucinações:** Se a resposta não estiver explícita no contexto, diga: "Não encontrei essa informação nos documentos fornecidos."
    3. **Detalhamento e Siglas (CRÍTICO):** 
       - Ao explicar siglas (ex: FICA, HOPE, SOFA), você DEVE explicar CADA LETRA da sigla individualmente. **Nunca** pule letras ou deixe incompleto.
       - Use listas ou tópicos para garantir que todos os passos/itens sejam mostrados.
    4. **Citações:** 
       - Ao final da resposta, liste as fontes consultadas.
       - Formato: `[Fonte: Nome_do_Arquivo | Página: X]`
       - Remova o prefixo "pdf/" dos nomes dos arquivos na exibição.

    ---

    Contexto (Documentos recuperados):
    {context}

    ---

    Pergunta do Usuário: {input}

    Resposta (Seja completo, explique todas as letras de siglas se houver):
    """


    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "input"])
    llm = ChatGoogleGenerativeAI(model=model_name, max_output_tokens=4000)
    stuff_chain = create_stuff_documents_chain(llm=llm, prompt=prompt, document_variable_name="context")
    qa_chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=stuff_chain)

    return qa_chain, stuff_chain