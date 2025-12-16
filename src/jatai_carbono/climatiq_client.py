import requests
from typing import List, Dict

from jatai_carbono.config import CLIMATIQ_API_KEY

CLIMATIQ_SEARCH_URL = "https://api.climatiq.io/data/v1/search"


def buscar_fatores_climatiq(
    query_en: str,
    limit: int = 10
) -> List[Dict]:
    """
    Busca fatores de emissão na API da Climatiq a partir de um termo em inglês.
    Usa GET conforme comportamento observado da API.
    Retorna lista vazia em caso de erro 4xx controlado.
    """

    if not CLIMATIQ_API_KEY:
        raise ValueError("CLIMATIQ_API_KEY não configurada.")

    headers = {
        "Authorization": f"Bearer {CLIMATIQ_API_KEY}"
    }

    params = {
        "query": query_en,
        "data_version": "^3",
    }

    response = requests.get(
        CLIMATIQ_SEARCH_URL,
        headers=headers,
        params=params
    )

    # ---- Tratamento controlado de erro ----
    if response.status_code == 400:
        # Query inválida ou não reconhecida pela Climatiq
        return []

    response.raise_for_status()

    results = response.json().get("results", [])

    fatores = []
    for r in results:
        fatores.append({
            "activity_id": r.get("activity_id"),
            "name": r.get("name"),
            "category": r.get("category"),
            "region": r.get("region"),
            "year": r.get("year"),
            "unit": r.get("unit"),
            "factor": r.get("factor"),
            "source": r.get("source"),
            "data_version": r.get("data_version")
        })

    return fatores
