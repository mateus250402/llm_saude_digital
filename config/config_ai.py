import os
from dotenv import load_dotenv

def configure_ai():
    load_dotenv()

    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError("Defina a variável de ambiente GOOGLE_API_KEY no arquivo .env.")

    os.environ["GOOGLE_API_KEY"] = api_key
    print("✅ Chave da API carregada com sucesso!")
