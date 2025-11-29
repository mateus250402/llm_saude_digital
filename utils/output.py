import datetime
import json
from pathlib import Path
from typing import List, Dict, Any
from langchain.schema import Document

def save_answer_json(answer: str, question: str, docs: List[Document], output_dir: str = "output") -> Dict[str, Any]:
    """
    Salva a resposta em JSON e RETORNA o objeto de dados.
    Use o retorno desta função para exibir na sua tela.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_path / f"answer_{timestamp}.json"
    
    # Prepara os dados estruturados
    data = {
        "data_hora": timestamp,
        "pergunta": question,
        "resposta": answer,
    }
    
    # Salva no arquivo
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Retorna os dados para você usar no seu programa
    return data