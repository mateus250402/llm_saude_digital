import datetime
import json
from pathlib import Path
from typing import Dict, Any

def save_answer_json(answer: str, question: str, output_dir: str = "output") -> Dict[str, Any]:
    """
    Salva a resposta dentro do arquivo history.json (em formato de lista)
    e RETORNA o objeto de dados.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    history_file = output_path / "history.json"

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Novo registro
    data = {
        "data_hora": timestamp,
        "pergunta": question,
        "resposta": answer,
    }

    # Se o arquivo já existe, carrega o conteúdo
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    # Adiciona o novo registro
    history.append(data)

    # Salva de volta no history.json
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    return data